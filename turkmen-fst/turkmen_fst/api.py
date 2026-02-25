# -*- coding: utf-8 -*-
"""
TurkmenFST — FastAPI REST API (api.py)

Endpoints:
    GET  /              — API kullanım kılavuzu (HTML)
    POST /generate/noun — İsim çekimi
    POST /generate/verb — Fiil çekimi
    POST /generate      — Birleşik üretim (isim veya fiil)
    POST /analyze       — Morfolojik analiz
    GET  /lexicon/{word} — Sözlük sorgusu
    GET  /health        — Sağlık kontrolü

Swagger UI: http://localhost:8000/docs
"""

from __future__ import annotations
import os
import re
from functools import lru_cache
from typing import Optional, Literal

try:
    from fastapi import FastAPI, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import HTMLResponse
    from pydantic import BaseModel, Field
    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False

from turkmen_fst.phonology import PhonologyRules
from turkmen_fst.lexicon import Lexicon, POS_DISPLAY
from turkmen_fst.morphotactics import VerbMorphotactics
from turkmen_fst.generator import MorphologicalGenerator
from turkmen_fst.analyzer import MorphologicalAnalyzer


# ==============================================================================
#  TOKENIZER & SPELLCHECK YARDIMCILARI
# ==============================================================================

_WORD_RE = re.compile(r"[a-zA-ZçÇäÄöÖüÜňŇýÝşŞžŽîÎ'-]+", re.UNICODE)


def tokenize(text: str) -> list[dict]:
    """
    Metni kelimelere ayırır. Her kelime için konum bilgisi de döndürür.

    Returns:
        [{"word": "kitabym", "start": 0, "end": 7}, ...]
    """
    tokens = []
    for m in _WORD_RE.finditer(text):
        tokens.append({"word": m.group(), "start": m.start(), "end": m.end()})
    return tokens


def _edit_distance(a: str, b: str) -> int:
    """İki string arasındaki Levenshtein edit distance."""
    if len(a) < len(b):
        return _edit_distance(b, a)
    if len(b) == 0:
        return len(a)
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a):
        curr = [i + 1]
        for j, cb in enumerate(b):
            cost = 0 if ca == cb else 1
            curr.append(min(curr[j] + 1, prev[j + 1] + 1, prev[j] + cost))
        prev = curr
    return prev[-1]


def _find_similar_roots(word: str, lexicon: Lexicon,
                        max_distance: int = 2, max_results: int = 10) -> list[str]:
    """
    Sözlükte edit distance ≤ max_distance olan kelimeleri bulur.
    Performans için kelime uzunluğuna göre filtreleme yapar.
    """
    w = word.lower()
    wlen = len(w)
    candidates = []

    for key in lexicon._entries:
        # Uzunluk farkı edit distance'dan büyükse atla
        if abs(len(key) - wlen) > max_distance:
            continue
        dist = _edit_distance(w, key)
        if 0 < dist <= max_distance:
            candidates.append((dist, key))

    candidates.sort(key=lambda x: (x[0], x[1]))
    return [c[1] for c in candidates[:max_results]]


def generate_suggestions(wrong_word: str, analyzer: MorphologicalAnalyzer,
                         lexicon: Lexicon, max_suggestions: int = 5) -> list[str]:
    """
    Yanlış yazılmış kelime için öneri üretir.

    Strateji:
    1. Edit distance ≤ 2 olan sözlük köklerini bul
    2. Her köke orijinal kelimeye en yakın çekim formlarını üret
    3. En yakın formları sırala ve döndür
    """
    similar_roots = _find_similar_roots(wrong_word, lexicon, max_distance=2, max_results=15)

    suggestions = set()
    for root in similar_roots:
        # Kökün kendisi bir öneri olabilir
        suggestions.add(root)

        # Kökün çekim formlarını üretip orijinal kelimeye yakınlığa göre sırala
        # Ama tüm paradigmayı üretmek pahalı, sadece kökü öneriyoruz
        # İleride buraya tam paradigma eklenebilir

    # Orijinal kelimeye en yakın olanları sırala
    ranked = sorted(suggestions, key=lambda s: _edit_distance(s.lower(), wrong_word.lower()))
    return ranked[:max_suggestions]


# ==============================================================================
#  SÖZLÜK YÜKLEME
# ==============================================================================

def _find_lexicon_path() -> str:
    candidates = [
        os.path.join(os.path.dirname(__file__), "..", "data", "turkmence_sozluk.txt"),
        os.path.join(os.path.dirname(__file__), "..", "..", "turkmence_sozluk.txt"),
    ]
    for path in candidates:
        real = os.path.realpath(path)
        if os.path.exists(real):
            return real
    return ""


# Global instances
_lexicon = Lexicon()
_path = _find_lexicon_path()
if _path:
    _lexicon.load(_path)

_generator = MorphologicalGenerator(_lexicon)
_analyzer = MorphologicalAnalyzer(_lexicon)


# ==============================================================================
#  İYELİK GÖRÜNTÜLEME EŞLEMESİ
# ==============================================================================

IYELIK_DISPLAY = {
    "A1": "D₁b", "A2": "D₂b", "A3": "D₃b",
    "B1": "D₁k", "B2": "D₂k", "B3": "D₃k"
}

MORPHEME_DISPLAY = {
    "PLURAL": "Çokluk (San)",
    "POSSESSIVE": "Degişlilik (İyelik)",
    "CASE": "Düşüm (Hal)",
    "TENSE": "Zaman",
    "PERSON": "Şahıs",
    "NEGATION": "Olumsuzluk",
}


def _format_morphemes(morphemes: list, possessive: Optional[str] = None) -> list:
    """Morpheme listesini kullanıcı dostu formata çevirir."""
    result = []
    for category, suffix in morphemes:
        entry = {
            "category": category,
            "display": MORPHEME_DISPLAY.get(category, category),
            "suffix": suffix,
        }
        if category == "POSSESSIVE" and possessive:
            entry["code"] = IYELIK_DISPLAY.get(possessive, possessive)
        result.append(entry)
    return result


# ==============================================================================
#  FASTAPI UYGULAMA
# ==============================================================================

if HAS_FASTAPI:

    API_DESCRIPTION = """
## Türkmen Türkçesi Morfolojik Analiz ve Sentez API'si

### Hızlı Başlangıç

**İsim çekimi** — `POST /generate/noun` ile sadece `stem` gönderin:
```json
{"stem": "kitap"}
```
Sonuç: `kitap` (yalın hal). Ek parametreler ekleyerek çekim yapabilirsiniz.

### Parametre Kodları

#### İyelik (Possessive) Kodları
| Kod | Görüntüleme | Açıklama | Örnek (kitap) |
|-----|-------------|----------|---------------|
| `A1` | D₁b | 1. tekil (meniň) | kitab**ym** |
| `A2` | D₂b | 2. tekil (seniň) | kitab**yň** |
| `A3` | D₃b | 3. tekil (onuň) | kitab**y** |

#### Hal (Case) Kodları
| Kod | Hal Adı | Soru | Örnek (kitap) |
|-----|---------|------|---------------|
| _(boş)_ | Baş (Yalın) | kim? näme? | kitap |
| `A2` | Eýelik (İlgi) | kimiň? nämäniň? | kitab**yň** |
| `A3` | Barlag (Yönelme) | kime? nämä? | kitab**a** |
| `A4` | Tabyn (Belirtme) | kimi? nämäni? | kitab**y** |
| `A5` | Ýerlik (Bulunma) | kimde? nämede? | kitap**da** |
| `A6` | Çykyş (Çıkma) | kimden? nämeden? | kitap**dan** |

#### Fiil Zaman Kodları
| Kod | Zaman | Örnek (gel-) |
|-----|-------|-------------|
| `1` | Anyk Öten (belirli geçmiş) | gel**di**m |
| `2` | Daş Öten (belirsiz geçmiş) | gel**ipdi**m |
| `3` | Dowamly Öten (sürekli geçmiş) | gel**ýärdi**m |
| `4` | Umumy Häzirki (geniş şimdiki) | gel**ýär**in |
| `5` | Anyk Häzirki (kesin şimdiki) | _(yardımcı fiil)_ |
| `6` | Mälim Geljek (belirli gelecek) | men gel**jek** |
| `7` | Nämälim Geljek (belirsiz gelecek) | gel**er**in |

#### Şahıs Kodları
| Kod | Zamiri | Açıklama |
|-----|--------|----------|
| `A1` | Men | 1. tekil |
| `A2` | Sen | 2. tekil |
| `A3` | Ol | 3. tekil |
| `B1` | Biz | 1. çoğul |
| `B2` | Siz | 2. çoğul |
| `B3` | Olar | 3. çoğul |
"""

    app = FastAPI(
        title="TurkmenFST API",
        description=API_DESCRIPTION,
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc"
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ---- Request / Response modelleri ----

    class NounGenerateRequest(BaseModel):
        """İsim çekimi isteği. Sadece `stem` zorunludur, diğerleri opsiyoneldir."""
        stem: str = Field(
            ...,
            description="Kök kelime (ör. kitap, adam, burun)",
            json_schema_extra={"example": "kitap"}
        )
        plural: bool = Field(
            False,
            description="Çoğul eki eklensin mi? (true → kitaplar)"
        )
        possessive: Optional[str] = Field(
            None,
            description="İyelik kodu: A1 (meniň), A2 (seniň), A3 (onuň). Boş bırakılabilir."
        )
        poss_type: str = Field(
            "tek",
            description="İyelik tipi: 'tek' (tekil) veya 'cog' (çoğul)"
        )
        case: Optional[str] = Field(
            None,
            description="Hal kodu: A2 (ilgi), A3 (yönelme), A4 (belirtme), A5 (bulunma), A6 (çıkma). Boş bırakılabilir."
        )

        model_config = {
            "json_schema_extra": {
                "examples": [
                    {
                        "summary": "Yalın hal (en basit)",
                        "description": "Sadece kök kelime — ek yok",
                        "value": {"stem": "kitap"}
                    },
                    {
                        "summary": "İyelik çekimi",
                        "description": "kitap + A1 iyelik → kitabym",
                        "value": {"stem": "kitap", "possessive": "A1"}
                    },
                    {
                        "summary": "Tam çekim",
                        "description": "kitap + çoğul + A3 iyelik + A2 hal → kitaplarynyň",
                        "value": {"stem": "kitap", "plural": True, "possessive": "A3", "case": "A2"}
                    }
                ]
            }
        }

    class VerbGenerateRequest(BaseModel):
        """Fiil çekimi isteği. stem, tense ve person zorunludur."""
        stem: str = Field(
            ...,
            description="Fiil kökü (ör. gel, oka, bar)",
            json_schema_extra={"example": "gel"}
        )
        tense: str = Field(
            ...,
            description="Zaman kodu: 1 (Anyk Öten), 2 (Daş Öten), 3 (Dowamly Öten), 4 (Umumy Häzirki), 5 (Anyk Häzirki), 6 (Mälim Geljek), 7 (Nämälim Geljek)",
            json_schema_extra={"example": "1"}
        )
        person: str = Field(
            ...,
            description="Şahıs kodu: A1 (Men), A2 (Sen), A3 (Ol), B1 (Biz), B2 (Siz), B3 (Olar)",
            json_schema_extra={"example": "A1"}
        )
        negative: bool = Field(
            False,
            description="Olumsuz mu? (true → gelmedi)"
        )

        model_config = {
            "json_schema_extra": {
                "examples": [
                    {
                        "summary": "Geçmiş zaman",
                        "description": "gel + geçmiş + 1. tekil → geldim",
                        "value": {"stem": "gel", "tense": "1", "person": "A1"}
                    },
                    {
                        "summary": "Olumsuz şimdiki",
                        "description": "gel + şimdiki + 3. tekil + olumsuz → gelmeýär",
                        "value": {"stem": "gel", "tense": "4", "person": "A3", "negative": True}
                    }
                ]
            }
        }

    class UnifiedGenerateRequest(BaseModel):
        """Birleşik üretim isteği. type='noun' veya type='verb' seçerek kullanın."""
        type: str = Field(
            "noun",
            description="Kelime türü: 'noun' (isim) veya 'verb' (fiil)"
        )
        stem: str = Field(
            ...,
            description="Kök kelime",
            json_schema_extra={"example": "kitap"}
        )
        # İsim parametreleri
        plural: bool = Field(False, description="[İsim] Çoğul eki")
        possessive: Optional[str] = Field(None, description="[İsim] İyelik: A1, A2, A3 (boş bırakılabilir)")
        poss_type: str = Field("tek", description="[İsim] İyelik tipi: tek/cog")
        case: Optional[str] = Field(None, description="[İsim] Hal: A2-A6 (boş bırakılabilir)")
        # Fiil parametreleri
        tense: Optional[str] = Field(None, description="[Fiil] Zaman kodu: 1-7 (fiil için zorunlu)")
        person: Optional[str] = Field(None, description="[Fiil] Şahıs kodu: A1-B3 (fiil için zorunlu)")
        negative: bool = Field(False, description="[Fiil] Olumsuz mu")

        model_config = {
            "json_schema_extra": {
                "examples": [
                    {
                        "summary": "İsim çekimi",
                        "description": "kitap + iyelik A1 → kitabym",
                        "value": {"type": "noun", "stem": "kitap", "possessive": "A1"}
                    },
                    {
                        "summary": "Fiil çekimi",
                        "description": "gel + geçmiş + 1. tekil → geldim",
                        "value": {"type": "verb", "stem": "gel", "tense": "1", "person": "A1"}
                    }
                ]
            }
        }

    class GenerateResponse(BaseModel):
        """Üretim sonucu."""
        result: str = Field(..., description="Çekimlenmiş kelime (ör. kitabym)")
        breakdown: str = Field(..., description="Ek ayrımı (ör. kitap + ym)")
        stem: str = Field(..., description="Orijinal kök kelime")
        morphemes: list = Field(..., description="Uygulanan ekler: [{category, display, suffix, code}]")
        valid: bool = Field(..., description="Geçerli bir çekim mi")

    class AnalyzeRequest(BaseModel):
        """Morfolojik analiz isteği."""
        word: str = Field(
            ...,
            description="Analiz edilecek çekimli kelime (ör. kitabym, kitaplar, geldim)",
            json_schema_extra={"example": "kitabym"}
        )

        model_config = {
            "json_schema_extra": {
                "examples": [
                    {
                        "summary": "İsim analizi",
                        "value": {"word": "kitabym"}
                    },
                    {
                        "summary": "Çoğul isim",
                        "value": {"word": "kitaplar"}
                    },
                    {
                        "summary": "Fiil analizi",
                        "value": {"word": "geldi"}
                    }
                ]
            }
        }

    class AnalyzeSingleResult(BaseModel):
        """Tek bir çözümleme sonucu."""
        stem: str = Field(..., description="Bulunan kök")
        word_type: str = Field(..., description="Kelime türü: noun/verb/unknown")
        breakdown: str = Field(..., description="Analiz formülü (ör. Kitap (Kök) + ym (D₁b))")
        suffixes: list = Field(..., description="Ek listesi")
        meaning: str = Field("", description="Anlam (eş sesli kelimeler için)")

    class AnalyzeResponse(BaseModel):
        """Çoklu analiz sonucu."""
        word: str = Field(..., description="Orijinal kelime")
        success: bool = Field(..., description="En az bir çözümleme bulundu mu")
        count: int = Field(..., description="Bulunan çözümleme sayısı")
        results: list[AnalyzeSingleResult] = Field(..., description="Çözümleme sonuçları listesi")

    class LexiconResponse(BaseModel):
        word: str
        found: bool
        entries: list
        pos_display: Optional[str] = None

    class HealthResponse(BaseModel):
        status: str
        version: str
        lexicon_loaded: bool
        lexicon_words: int

    # ---- Spellcheck Modelleri ----

    class SpellcheckRequest(BaseModel):
        """Yazım denetimi isteği."""
        text: str = Field(
            ...,
            description="Kontrol edilecek metin (bir veya birden fazla kelime)",
            json_schema_extra={"example": "men kitabym okadym"}
        )

        model_config = {
            "json_schema_extra": {
                "examples": [
                    {
                        "summary": "Basit cümle",
                        "value": {"text": "men kitabym okadym"}
                    },
                    {
                        "summary": "Hatalı kelimeler",
                        "value": {"text": "kitaplarymzdan mugalym geldy"}
                    }
                ]
            }
        }

    class SpellcheckWordResult(BaseModel):
        """Tek kelime yazım kontrolü sonucu."""
        word: str = Field(..., description="Kontrol edilen kelime")
        correct: bool = Field(..., description="Doğru mu?")
        start: int = Field(..., description="Kelime başlangıç pozisyonu")
        end: int = Field(..., description="Kelime bitiş pozisyonu")
        suggestions: list[str] = Field(default_factory=list,
                                       description="Yanlışsa öneri listesi")
        analysis: Optional[str] = Field(None,
                                         description="Doğruysa morfolojik analiz")

    class SpellcheckResponse(BaseModel):
        """Yazım denetimi sonucu."""
        text: str = Field(..., description="Orijinal metin")
        word_count: int = Field(..., description="Kontrol edilen kelime sayısı")
        error_count: int = Field(..., description="Hatalı kelime sayısı")
        results: list[SpellcheckWordResult] = Field(...,
                                                      description="Kelime bazlı sonuçlar")

    class SpellcheckBatchRequest(BaseModel):
        """Toplu yazım denetimi — kelime listesi."""
        words: list[str] = Field(
            ...,
            description="Kontrol edilecek kelimeler listesi",
            json_schema_extra={"example": ["kitabym", "okadym", "mugalym"]}
        )

    # ---- Endpoints ----

    @app.get("/", response_class=HTMLResponse, tags=["Guide"],
             summary="API Kullanım Kılavuzu")
    async def api_guide():
        """Ana sayfa — API kullanım kılavuzu (HTML)."""
        return HTMLResponse(content="""
<!DOCTYPE html>
<html lang="tk">
<head>
    <meta charset="utf-8">
    <title>TurkmenFST API</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
               max-width: 800px; margin: 40px auto; padding: 0 20px; color: #333;
               line-height: 1.6; }
        h1 { color: #1a5f2a; border-bottom: 2px solid #1a5f2a; padding-bottom: 8px; }
        h2 { color: #2d7a3e; margin-top: 32px; }
        code { background: #f4f4f4; padding: 2px 6px; border-radius: 3px; font-size: 0.9em; }
        pre { background: #f8f8f8; border: 1px solid #ddd; border-radius: 6px;
              padding: 16px; overflow-x: auto; }
        table { border-collapse: collapse; width: 100%; margin: 16px 0; }
        th, td { border: 1px solid #ddd; padding: 8px 12px; text-align: left; }
        th { background: #f0f7f0; }
        a { color: #1a5f2a; }
        .example { background: #f0f7f0; border-left: 4px solid #1a5f2a;
                   padding: 12px 16px; margin: 16px 0; border-radius: 0 4px 4px 0; }
        .endpoint { background: #e8f5e9; padding: 4px 8px; border-radius: 4px;
                    font-weight: bold; }
    </style>
</head>
<body>
    <h1>🇹🇲 TurkmenFST API v1.0</h1>
    <p>Türkmen Türkçesi Morfolojik Analiz ve Sentez API'si</p>
    <p>📖 <a href="/docs">Swagger UI (İnteraktif API Belgesi)</a> |
       📋 <a href="/redoc">ReDoc</a></p>

    <h2>Hızlı Başlangıç</h2>

    <h3>1. İsim Çekimi</h3>
    <p class="endpoint">POST /generate/noun</p>
    <div class="example">
        <strong>En basit kullanım — sadece kök kelime gönderin:</strong>
        <pre>curl -X POST http://localhost:8000/generate/noun \\
  -H "Content-Type: application/json" \\
  -d '{"stem": "kitap"}'</pre>
        <strong>İyelik ekli:</strong>
        <pre>{"stem": "kitap", "possessive": "A1"}  → kitabym</pre>
        <strong>Çoğul + hal:</strong>
        <pre>{"stem": "kitap", "plural": true, "case": "A5"}  → kitaplarda</pre>
    </div>

    <h3>2. Fiil Çekimi</h3>
    <p class="endpoint">POST /generate/verb</p>
    <div class="example">
        <strong>stem + tense + person zorunludur:</strong>
        <pre>{"stem": "gel", "tense": "1", "person": "A1"}  → geldim</pre>
        <strong>Olumsuz:</strong>
        <pre>{"stem": "gel", "tense": "4", "person": "A3", "negative": true}  → gelmeýär</pre>
    </div>

    <h3>3. Kelime Analizi</h3>
    <p class="endpoint">POST /analyze</p>
    <div class="example">
        <pre>{"word": "kitabym"}  → kök: kitap, ek: ym (D₁b)</pre>
    </div>

    <h3>4. Sözlük Sorgusu</h3>
    <p class="endpoint">GET /lexicon/kitap</p>

    <h3>5. Yazım Denetimi (TÄZE!)</h3>
    <p class="endpoint">POST /spellcheck</p>
    <div class="example">
        <strong>Metin kontrolü:</strong>
        <pre>{"text": "men kitabym okadym"}</pre>
        <strong>Toplu kontrol:</strong>
        <pre>POST /spellcheck/batch
{"words": ["kitabym", "okadym", "mugalym"]}</pre>
    </div>

    <h3>6. Paradigma Tablosu (TÄZE!)</h3>
    <p class="endpoint">POST /paradigm</p>
    <div class="example">
        <strong>İsim paradigması:</strong>
        <pre>{"stem": "kitap", "type": "noun"}</pre>
        <strong>Fiil paradigması:</strong>
        <pre>{"stem": "gel", "type": "verb"}</pre>
    </div>

    <h2>Parametre Kodları</h2>

    <h3>İyelik (Degişlilik)</h3>
    <table>
        <tr><th>Kod</th><th>Gösterim</th><th>Açıklama</th><th>Örnek</th></tr>
        <tr><td>A1</td><td>D₁b</td><td>1. tekil (meniň)</td><td>kitab<b>ym</b></td></tr>
        <tr><td>A2</td><td>D₂b</td><td>2. tekil (seniň)</td><td>kitab<b>yň</b></td></tr>
        <tr><td>A3</td><td>D₃b</td><td>3. tekil (onuň)</td><td>kitab<b>y</b></td></tr>
    </table>

    <h3>Hal (Düşüm)</h3>
    <table>
        <tr><th>Kod</th><th>Hal</th><th>Soru</th><th>Örnek</th></tr>
        <tr><td><em>boş</em></td><td>Baş (Yalın)</td><td>kim? näme?</td><td>kitap</td></tr>
        <tr><td>A2</td><td>Eýelik (İlgi)</td><td>kimiň?</td><td>kitab<b>yň</b></td></tr>
        <tr><td>A3</td><td>Barlag (Yönelme)</td><td>kime?</td><td>kitab<b>a</b></td></tr>
        <tr><td>A4</td><td>Tabyn (Belirtme)</td><td>kimi?</td><td>kitab<b>y</b></td></tr>
        <tr><td>A5</td><td>Ýerlik (Bulunma)</td><td>kimde?</td><td>kitap<b>da</b></td></tr>
        <tr><td>A6</td><td>Çykyş (Çıkma)</td><td>kimden?</td><td>kitap<b>dan</b></td></tr>
    </table>

    <h3>Fiil Zamanları</h3>
    <table>
        <tr><th>Kod</th><th>Zaman</th><th>Örnek (gel-)</tr>
        <tr><td>1</td><td>Anyk Öten</td><td>gel<b>di</b>m</td></tr>
        <tr><td>2</td><td>Daş Öten</td><td>gel<b>ipdi</b>m</td></tr>
        <tr><td>3</td><td>Dowamly Öten</td><td>gel<b>ýärdi</b>m</td></tr>
        <tr><td>4</td><td>Umumy Häzirki</td><td>gel<b>ýär</b>in</td></tr>
        <tr><td>5</td><td>Anyk Häzirki</td><td><em>yardımcı fiil</em></td></tr>
        <tr><td>6</td><td>Mälim Geljek</td><td>men gel<b>jek</b></td></tr>
        <tr><td>7</td><td>Nämälim Geljek</td><td>gel<b>er</b>in</td></tr>
    </table>

    <h3>Şahıs Kodları</h3>
    <table>
        <tr><th>Kod</th><th>Zamir</th></tr>
        <tr><td>A1</td><td>Men (Ben)</td></tr>
        <tr><td>A2</td><td>Sen</td></tr>
        <tr><td>A3</td><td>Ol (O)</td></tr>
        <tr><td>B1</td><td>Biz</td></tr>
        <tr><td>B2</td><td>Siz</td></tr>
        <tr><td>B3</td><td>Olar (Onlar)</td></tr>
    </table>
</body>
</html>
""")

    @app.get("/health", response_model=HealthResponse, tags=["System"],
             summary="Sistem sağlık kontrolü")
    async def health():
        """Sistemin çalışıp çalışmadığını ve sözlük durumunu kontrol eder."""
        return HealthResponse(
            status="ok",
            version="1.0.0",
            lexicon_loaded=_lexicon.is_loaded,
            lexicon_words=_lexicon.word_count
        )

    @app.post("/generate/noun", response_model=GenerateResponse, tags=["Generation"],
              summary="İsim çekimi (üretim)")
    async def generate_noun(req: NounGenerateRequest):
        """
        İsim çekimi yapar.

        **En basit kullanım** — sadece `stem` gönderin, diğer alanları boş bırakın:
        ```json
        {"stem": "kitap"}
        ```

        **İyelik eklemek için** `possessive` alanını kullanın:
        ```json
        {"stem": "kitap", "possessive": "A1"}
        ```
        Sonuç: `kitabym` (kitap + ym = D₁b)

        **Çoğul + hal** eklemek için:
        ```json
        {"stem": "kitap", "plural": true, "case": "A5"}
        ```
        Sonuç: `kitaplarda` (kitap + lar + da)
        """
        result = _generator.generate_noun(
            req.stem, req.plural, req.possessive, req.poss_type, req.case
        )
        if not result.is_valid:
            raise HTTPException(status_code=400, detail=result.error)
        return GenerateResponse(
            result=result.word,
            breakdown=result.breakdown,
            stem=result.stem,
            morphemes=_format_morphemes(result.morphemes, req.possessive),
            valid=result.is_valid
        )

    @app.post("/generate/verb", response_model=GenerateResponse, tags=["Generation"],
              summary="Fiil çekimi (üretim)")
    async def generate_verb(req: VerbGenerateRequest):
        """
        Fiil çekimi yapar.

        **Zorunlu alanlar**: `stem`, `tense`, `person`

        ```json
        {"stem": "gel", "tense": "1", "person": "A1"}
        ```
        Sonuç: `geldim` (gel + di + m)

        **Olumsuz**:
        ```json
        {"stem": "gel", "tense": "1", "person": "A1", "negative": true}
        ```
        Sonuç: `gelmedim`
        """
        result = _generator.generate_verb(
            req.stem, req.tense, req.person, req.negative
        )
        if not result.is_valid:
            raise HTTPException(status_code=400, detail=result.error)
        return GenerateResponse(
            result=result.word,
            breakdown=result.breakdown,
            stem=result.stem,
            morphemes=_format_morphemes(result.morphemes),
            valid=result.is_valid
        )

    @app.post("/generate", response_model=GenerateResponse, tags=["Generation"],
              summary="Birleşik üretim (isim veya fiil)")
    async def generate(req: UnifiedGenerateRequest):
        """
        İsim veya fiil çekimini tek endpoint'ten yapar.

        **İsim çekimi** (`type: "noun"`):
        ```json
        {"type": "noun", "stem": "kitap", "possessive": "A1"}
        ```

        **Fiil çekimi** (`type: "verb"` — tense ve person zorunlu):
        ```json
        {"type": "verb", "stem": "gel", "tense": "1", "person": "A1"}
        ```
        """
        if req.type == "noun":
            result = _generator.generate_noun(req.stem, req.plural, req.possessive, req.poss_type, req.case)
            morphemes = _format_morphemes(result.morphemes, req.possessive)
        elif req.type == "verb":
            if not req.tense or not req.person:
                raise HTTPException(
                    status_code=400,
                    detail="Fiil çekimi için 'tense' (zaman: 1-7) ve 'person' (şahıs: A1-B3) alanları zorunludur. "
                           "Örnek: {\"type\": \"verb\", \"stem\": \"gel\", \"tense\": \"1\", \"person\": \"A1\"}"
                )
            result = _generator.generate_verb(req.stem, req.tense, req.person, req.negative)
            morphemes = _format_morphemes(result.morphemes)
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Geçersiz tür: '{req.type}'. 'noun' (isim) veya 'verb' (fiil) kullanın."
            )

        if not result.is_valid:
            raise HTTPException(status_code=400, detail=result.error)

        return GenerateResponse(
            result=result.word,
            breakdown=result.breakdown,
            stem=result.stem,
            morphemes=morphemes,
            valid=result.is_valid
        )

    @app.post("/analyze", response_model=AnalyzeResponse, tags=["Analysis"],
              summary="Morfolojik analiz (kelime çözümleme)")
    async def analyze(req: AnalyzeRequest):
        """
        Çekimli bir kelimeyi köküne ve eklerine ayırır.

        ```json
        {"word": "kitabym"}
        ```
        Sonuç: kök = `Kitap`, ekler = `ym (D₁b)`

        Hem isim hem fiil çekimlerini otomatik algılar.
        """
        multi = _analyzer.parse(req.word)
        results_list = []
        for r in multi.results:
            results_list.append(AnalyzeSingleResult(
                stem=r.stem,
                word_type=r.word_type,
                breakdown=r.breakdown,
                suffixes=r.suffixes,
                meaning=r.meaning
            ))
        return AnalyzeResponse(
            word=multi.original,
            success=multi.success,
            count=multi.count,
            results=results_list
        )

    @app.get("/lexicon/{word}", response_model=LexiconResponse, tags=["Lexicon"],
             summary="Sözlük sorgusu")
    async def lexicon_lookup(word: str):
        """
        Sözlükte kelime arar.

        Örnek: `GET /lexicon/kitap` → kelime türü, morfolojik özellikler
        """
        entries = _lexicon.lookup(word)
        found = len(entries) > 0

        entry_list = []
        pos_display = None
        for entry in entries:
            entry_list.append({
                "word": entry.word,
                "pos": entry.pos,
                "features": entry.features
            })
            if pos_display is None:
                pos_display = POS_DISPLAY.get(entry.pos)

        return LexiconResponse(
            word=word,
            found=found,
            entries=entry_list,
            pos_display=pos_display
        )

    # ---- Spellcheck Endpoints ----

    @app.post("/spellcheck", response_model=SpellcheckResponse,
              tags=["Spellcheck"], summary="Yazım denetimi")
    async def spellcheck(req: SpellcheckRequest):
        """
        Metin içindeki kelimelerin yazımını kontrol eder.

        Her kelime analyzer ile çözümlenir:
        - Çözümleme başarılıysa → **doğru**
        - Çözümleme bulunamazsa → **yanlış** + öneri listesi

        ```json
        {"text": "men kitabym okadym"}
        ```

        Sonuç: `kitabym` ✅ doğru, `okadym` ❌ yanlış → öneriler: [`okadym`...]
        """
        tokens = tokenize(req.text)
        results = []
        error_count = 0

        for tok in tokens:
            w = tok["word"]
            multi = _analyzer.parse(w)

            # Kelime doğru mu? (en az 1 bilinen kökle çözümlenebiliyorsa)
            is_correct = False
            analysis_str = None

            if multi.success and multi.results:
                for r in multi.results:
                    if r.word_type != "unknown":
                        is_correct = True
                        analysis_str = r.breakdown
                        break

            suggestions = []
            if not is_correct:
                error_count += 1
                suggestions = generate_suggestions(w, _analyzer, _lexicon, max_suggestions=5)

            results.append(SpellcheckWordResult(
                word=w,
                correct=is_correct,
                start=tok["start"],
                end=tok["end"],
                suggestions=suggestions,
                analysis=analysis_str
            ))

        return SpellcheckResponse(
            text=req.text,
            word_count=len(tokens),
            error_count=error_count,
            results=results
        )

    @app.post("/spellcheck/batch", response_model=SpellcheckResponse,
              tags=["Spellcheck"], summary="Toplu yazım denetimi")
    async def spellcheck_batch(req: SpellcheckBatchRequest):
        """
        Kelime listesi üzerinde yazım denetimi yapar.

        ```json
        {"words": ["kitabym", "okadym", "mugalym"]}
        ```
        """
        results = []
        error_count = 0
        offset = 0

        for w in req.words:
            multi = _analyzer.parse(w)

            is_correct = False
            analysis_str = None

            if multi.success and multi.results:
                for r in multi.results:
                    if r.word_type != "unknown":
                        is_correct = True
                        analysis_str = r.breakdown
                        break

            suggestions = []
            if not is_correct:
                error_count += 1
                suggestions = generate_suggestions(w, _analyzer, _lexicon, max_suggestions=5)

            results.append(SpellcheckWordResult(
                word=w,
                correct=is_correct,
                start=offset,
                end=offset + len(w),
                suggestions=suggestions,
                analysis=analysis_str
            ))
            offset += len(w) + 1

        return SpellcheckResponse(
            text=" ".join(req.words),
            word_count=len(req.words),
            error_count=error_count,
            results=results
        )

    # ---- Paradigma Endpoints ----

    class ParadigmaRequest(BaseModel):
        """Paradigma tablosu isteği."""
        stem: str = Field(
            ...,
            description="İsim veya fiil kökü (ör. kitap, gel)",
            json_schema_extra={"example": "kitap"}
        )
        type: str = Field(
            "noun",
            description="Kelime türü: 'noun' (isim) veya 'verb' (fiil)"
        )

        model_config = {
            "json_schema_extra": {
                "examples": [
                    {"summary": "İsim paradigması", "value": {"stem": "kitap", "type": "noun"}},
                    {"summary": "Fiil paradigması", "value": {"stem": "gel", "type": "verb"}}
                ]
            }
        }

    class ParadigmaNounRow(BaseModel):
        """İsim paradigma tablosu satırı."""
        case_code: str = Field(..., description="Hal kodu")
        case_name: str = Field(..., description="Hal adı")
        base: str = Field(..., description="Yalın form")
        possA1: str = Field("", description="D₁b (meniň)")
        possA2: str = Field("", description="D₂b (seniň)")
        possA3: str = Field("", description="D₃b (onuň)")

    class ParadigmaNounResponse(BaseModel):
        """İsim paradigma tablosu."""
        stem: str
        type: str = "noun"
        singular: list[ParadigmaNounRow] = Field(..., description="Tekil paradigma")
        plural: list[ParadigmaNounRow] = Field(..., description="Çoğul paradigma")

    class ParadigmaVerbRow(BaseModel):
        """Fiil paradigma tablosu satırı."""
        person_code: str
        person_name: str
        positive: str = ""
        negative: str = ""

    class ParadigmaVerbTense(BaseModel):
        """Bir zaman için paradigma."""
        tense_code: str
        tense_name: str
        rows: list[ParadigmaVerbRow]

    class ParadigmaVerbResponse(BaseModel):
        """Fiil paradigma tablosu."""
        stem: str
        type: str = "verb"
        tenses: list[ParadigmaVerbTense]

    CASE_NAMES = {
        None: ("—", "Baş düşüm (Yalın)"),
        "A2": ("A₂", "Eýelik düşüm (İlgi)"),
        "A3": ("A₃", "Barlag düşüm (Yönelme)"),
        "A4": ("A₄", "Tabyn düşüm (Belirtme)"),
        "A5": ("A₅", "Ýerlik düşüm (Bulunma)"),
        "A6": ("A₆", "Çykyş düşüm (Çıkma)"),
    }

    TENSE_NAMES = {
        "1": "Anyk öten zaman",
        "2": "Daş öten zaman",
        "3": "Dowamly öten zaman",
        "4": "Umumy häzirki zaman",
        "5": "Anyk häzirki zaman",
        "6": "Mälim geljek zaman",
        "7": "Nämälim geljek zaman",
    }

    PERSON_NAMES = {
        "A1": "Men", "A2": "Sen", "A3": "Ol",
        "B1": "Biz", "B2": "Siz", "B3": "Olar",
    }

    @app.post("/paradigm", tags=["Paradigm"],
              summary="Paradigma tablosu oluştur")
    async def paradigm(req: ParadigmaRequest):
        """
        Bir kelimenin tam çekim paradigmasını döndürür.

        **İsim:**  6 hal × 4 iyelik (yalın, A1, A2, A3) × tekil/çoğul = 48 form
        **Fiil:**   7 zaman × 6 şahıs × olumlu/olumsuz = 84 form

        ```json
        {"stem": "kitap", "type": "noun"}
        ```
        """
        if req.type == "noun":
            return _generate_noun_paradigm(req.stem)
        elif req.type == "verb":
            return _generate_verb_paradigm(req.stem)
        else:
            raise HTTPException(status_code=400,
                                detail=f"Geçersiz tür: '{req.type}'")

    def _generate_noun_paradigm(stem: str) -> ParadigmaNounResponse:
        """İsim paradigma tablosu oluşturur."""
        cases = [None, "A2", "A3", "A4", "A5", "A6"]
        poss_codes = [None, "A1", "A2", "A3"]

        singular_rows = []
        plural_rows = []

        for case in cases:
            code, name = CASE_NAMES[case]

            # Tekil
            s_row = {"case_code": code, "case_name": name}
            for poss in poss_codes:
                r = _generator.generate_noun(stem, plural=False,
                                              possessive=poss, case=case)
                key = "base" if poss is None else f"poss{poss}"
                s_row[key] = r.word if r.is_valid else "—"
            singular_rows.append(ParadigmaNounRow(**s_row))

            # Çoğul
            p_row = {"case_code": code, "case_name": name}
            for poss in poss_codes:
                r = _generator.generate_noun(stem, plural=True,
                                              possessive=poss, case=case)
                key = "base" if poss is None else f"poss{poss}"
                p_row[key] = r.word if r.is_valid else "—"
            plural_rows.append(ParadigmaNounRow(**p_row))

        return ParadigmaNounResponse(stem=stem,
                                      singular=singular_rows,
                                      plural=plural_rows)

    def _generate_verb_paradigm(stem: str) -> ParadigmaVerbResponse:
        """Fiil paradigma tablosu oluşturur."""
        tenses = []
        persons = ["A1", "A2", "A3", "B1", "B2", "B3"]

        for t_code in ["1", "2", "3", "4", "5", "6", "7"]:
            rows = []
            for p_code in persons:
                pos_r = _generator.generate_verb(stem, t_code, p_code, negative=False)
                neg_r = _generator.generate_verb(stem, t_code, p_code, negative=True)
                rows.append(ParadigmaVerbRow(
                    person_code=p_code,
                    person_name=PERSON_NAMES[p_code],
                    positive=pos_r.word if pos_r.is_valid else "—",
                    negative=neg_r.word if neg_r.is_valid else "—",
                ))
            tenses.append(ParadigmaVerbTense(
                tense_code=t_code,
                tense_name=TENSE_NAMES[t_code],
                rows=rows,
            ))

        return ParadigmaVerbResponse(stem=stem, tenses=tenses)

else:
    # FastAPI yoksa dummy app
    app = None
    print("UYARI: FastAPI kurulu değil. API kullanabilmek için: pip install fastapi uvicorn")
