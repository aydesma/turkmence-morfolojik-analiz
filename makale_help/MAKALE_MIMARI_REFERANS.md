# TurkmenFST — Sistem Mimarisi ve Morfolojik Kurallar: Makale Referans Dokümanı

> **Amaç:** MAKALE_TURKLANG.md'nin **§4 Sistem Mimarisi** ve **morfolojik kural** bölümlerini yazarken kullanılmak üzere, `turkmen-fst/turkmen_fst/` modüler paketinden derlenen teknik bilgiler.
>
> **Not:** Canlı web sitesi (`app.py`) monolitik `morphology.py` dosyasını kullanır; ancak bu doküman ve makaledeki anlatım, asıl modüler motoru (`turkmen-fst/turkmen_fst/`) temel alır. Her iki motor aynı kuralları uygular ve aynı çıktıyı üretir.

---

## 1. Genel Mimari

TurkmenFST, beş bağımsız Python modülünden oluşan modüler bir pakettir. Her modül tek bir sorumluluk taşır:

```
turkmen-fst/turkmen_fst/
├── phonology.py        # Fonoloji: ses kuralları (ünlü uyumu, yumuşama, düşme, yuvarlaklaşma)
├── lexicon.py          # Sözlük: 32.015 girdi yükleme, özellik sorgulama
├── morphotactics.py    # Morfotaktik: FST durum makinesi (ek sırası doğrulama)
├── generator.py        # Sentez: kök + parametreler → çekimli yüzey formu
├── analyzer.py         # Analiz: çekimli yüzey formu → kök + ek çözümleme
├── api.py              # REST API endpoint'leri
├── cli.py              # Komut satırı arayüzü
└── __init__.py         # Paket girişi
```

**Veri akışı (pipeline):**

```
                  ┌─────────────┐
                  │ phonology   │ ← Ses kuralları (stateless, pure functions)
                  │  .py        │
                  └──────┬──────┘
                         │ çağırılır
  ┌──────────┐    ┌──────┴───────┐    ┌──────────────────┐
  │ lexicon  │───→│ generator    │←───│ morphotactics    │
  │  .py     │    │  .py         │    │  .py             │
  │          │    │              │    │                  │
  │ 32.015   │    │ NounGen +   │    │ NounMorphotactics│
  │ kök+POS+ │    │ VerbGen +   │    │ VerbMorphotactics│
  │ özellik  │    │ MorphGen    │    │ State + Trans.   │
  └──────────┘    └──────┬───────┘    └──────────────────┘
                         │ üretim sonuçları
                  ┌──────┴──────┐
                  │ analyzer    │ ← Ters çözümleme (generator doğrulamalı)
                  │  .py        │
                  └─────────────┘
```

**Tasarım ilkeleri:**
- Her modül bağımsız olarak test edilebilir.
- Fonoloji modülü durum tutmaz (stateless); saf fonksiyonlar olarak çalışır.
- Morfotaktik durum makinesi, sentez motorundan ayrıdır; doğrulama ve üretim birbirinden bağımsızdır.
- Analiz motoru, sentez motorunu dolaylı olarak kullanır (ters üretim stratejisi).

---

## 2. Fonoloji Modülü (`phonology.py`)

### 2.1 Ünlü Sistemi — `VowelSystem` sınıfı

Türkmen Türkçesinin ünlü envanteri `frozenset` veri yapılarıyla tanımlanır:

| Kategori | Ünlüler | Python sabiti |
|----------|---------|---------------|
| Kalın (yogyn / back) | a, o, u, y | `YOGYN = frozenset("aouy")` |
| İnce (front) | e, ä, ö, i, ü | `INCE = frozenset("eäöiü")` |
| Yuvarlak (rounded / dodak) | o, ö, u, ü | `DODAK = frozenset("oöuü")` |
| Tümü | a, o, u, y, e, ä, ö, i, ü | `ALL = YOGYN \| INCE` |

### 2.2 Fonolojik Kurallar — `PhonologyRules` sınıfı

Tüm kurallar `@staticmethod` olarak tanımlanır; durum tutmaz ve herhangi bir modül tarafından doğrudan çağrılabilir.

#### 2.2.1 Ünlü Niteliği Belirleme
```python
PhonologyRules.get_vowel_quality(word) → "yogyn" | "ince"
```
Son ünlüye göre kelimenin kalın/ince niteliğini belirler. Tüm ek seçimleri bu niteliğe dayanır.

#### 2.2.2 Ünsüz Yumuşaması (Consonant Softening)
```python
SOFTENING_TABLE = {'p': 'b', 'ç': 'j', 't': 'd', 'k': 'g'}
PhonologyRules.apply_consonant_softening(stem) → str
```
Kök son harfi sert ünsüz ise ve ünlüyle başlayan ek geliyorsa yumuşatma uygulanır. Sözlükteki `softening` etiketi (7.001 kelime) bu kuralın uygulanıp uygulanmayacağını belirler.

**Mimari fark (Apertium ile):** TurkmenFST sözlükte yüzey formunu saklar (`kitap`), ek geldiğinde yumuşatır (`kitab+ym`). Apertium ise underlying formu saklar (`kitab`), sözcük sonunda sertleştirir (`kitap`). TurkmenFST yaklaşımı enedilim.com ile aynıdır.

#### 2.2.3 Ünlü Düşmesi (Vowel Elision)
```python
PhonologyRules.apply_vowel_drop(stem, suffix) → str
```
İki alt kategoride işler:

| Tür | Veri yapısı | Örnek | Sayı |
|-----|------------|-------|------|
| Düzenli düşme | `VOWEL_DROP_CANDIDATES` (frozenset) | burun→burn, ogul→ogl, agyz→agz | 20 kelime |
| Düzensiz düşme | `VOWEL_DROP_EXCEPTIONS` (dict) | asyl→asl, mähir→mähr, ylym→ylm | 5 kelime |

Kural: Ek ünlüyle başlıyorsa, kökün son hecesindeki ünlü düşer. 5.654 yanlış pozitifi önlemek için kural tabanlı değil, **liste tabanlı** yaklaşım benimsenmiştir.

#### 2.2.4 Yuvarlaklaşma (Rounding Harmony)

İki düzeyde çalışır:

1. **Genel:** Kök yuvarlak ünlü içeriyor ve son harf y/i ise → u/ü dönüşümü (çoğul eki ve 3. iyelik öncesinde)
   ```python
   PhonologyRules.apply_rounding_harmony(stem, quality) → str
   ```

2. **Berdi Hoca Özel Kuralı:** `YUVARLAKLASMA_LISTESI` — 3 kelimelik istisna listesi:
   ```python
   YUVARLAKLASMA_LISTESI = {"guzy": "guzu", "süri": "sürü", "guýy": "guýu"}
   ```
   Bu kelimeler çoğul ve 3.iyelik eklerinden önce kökün kendisi değişir. enedilim.com öğretim materyalinden (Berdi Hoca) tespit edilmiştir.

   **Apertium karşılaştırması:** Apertium'da bu kural tanımlı değildir → `guzy → guzylar` (yanlış). TurkmenFST: `guzy → guzular` (doğru, enedilim uyumlu).

#### 2.2.5 Ön-Ek Pipeline'ı
```python
PhonologyRules.apply_pre_suffix_rules(stem, suffix, apply_drop, apply_softening) → str
```
Ek eklenmeden önce sırasıyla: (1) ünlü düşmesi, (2) ünsüz yumuşaması uygular.

---

## 3. Sözlük Modülü (`lexicon.py`)

### 3.1 Veri Yapısı — `LexiconEntry` dataclass

Her giriş üç bileşen taşır:
```
kelime<TAB>%<POS%>[<TAB>özellikler]
```

```python
@dataclass
class LexiconEntry:
    word: str           # "kitap"
    pos: str            # "n", "v", "adj", "np", ...
    features: dict      # {"softening": True, "vowel_drop": True, ...}
```

Özellik etiketleri:

| Etiket | Açıklama | Sayı |
|--------|----------|------|
| `softening` | Ünsüz yumuşaması izni | 7.001 kelime |
| `vowel_drop` | Ünlü düşmesi adayı | 20 kelime |
| `exception_drop` | Düzensiz ünlü düşmesi (asl, mähr gibi) | 5 kelime |
| `homonym` | Eş sesli kelime bilgisi | 6 kelime |
| `rounding` | Yuvarlaklaşma | 3 kelime |

### 3.2 Eş Sesli Kelimeler — `HOMONYMS` dict

```python
HOMONYMS = {
    "at":   {"1": ("A:T (Ad, isim)", True),  "2": ("AT (At, beygir)", False)},
    "but":  {"1": ("BU:T (Vücut)", True),    "2": ("BUT (Temel taşı)", False)},
    ...  # toplam 6 eş sesli kök
}
```

Her anlam için farklı yumuşama izni tanımlanır. Paradigma üretiminde eş sesli kelimeler çift tablo olarak gösterilir.

### 3.3 Sözlük İstatistikleri

| POS | Sayı | Oran |
|-----|------|------|
| İsim (n) | 21.798 | %68,1 |
| Fiil (v) | 6.471 | %20,2 |
| Sıfat (adj) | 3.094 | %9,7 |
| Özel isim (np) | 548 | %1,7 |
| Diğer | 104 | %0,3 |
| **Toplam** | **32.015** | **%100** |

5 kaynak: Wiktionary (1.649), Hunspell tk_TM (16.238), Orfoepik (5.362), enedilim.com (8.802), PDF OCR (dolaylı).

---

## 4. Morfotaktik Durum Makinesi (`morphotactics.py`)

### 4.1 Genel Yapı

Beesley & Karttunen (2003) sonlu durum morfolojisi modelinden ilham alınarak tasarlanmıştır. Üç temel veri yapısı:

```python
class StateType(Enum):       # Durum türü (NOUN_STEM, PLURAL, POSSESSIVE, ...)
class State:                  # name, state_type, is_final
class Transition:             # source, target, category, description
```

### 4.2 İsim FST — `NounMorphotactics`

**Durum diyagramı:**
```
STEM ──→ [PLURAL] ──→ [POSSESSIVE] ──→ [CASE]
  │                        ↑               ↑
  │────────────────────────┘               │
  │────────────────────────────────────────┘
```

| Durum | is_final | Açıklama |
|-------|----------|----------|
| STEM | ✅ | Yalın hal — ek almadan durulabilir |
| PLURAL | ✅ | Çoğul ekinden sonra |
| POSSESSIVE | ✅ | İyelik ekinden sonra |
| CASE | ✅ | Hal ekinden sonra |

**Geçersiz diziler (reject):**
- CASE → PLURAL ❌
- CASE → POSSESSIVE ❌
- POSSESSIVE → PLURAL ❌

**Geçerli geçiş sayısı:** 27 Transition (STEM→5 hedef × multiple categories)

```python
NounMorphotactics.validate_noun_params(plural, possessive, case) → (bool, str)
NounMorphotactics.is_valid_sequence(categories) → bool
```

### 4.3 Fiil FST — `VerbMorphotactics`

**Durum diyagramı:**
```
V_STEM ──→ [NEGATION] ──→ TENSE ──→ [PERSON]
  │                          ↑          ↑
  │──────────────────────────┘          │
  └─────────────────────────────────────┘
```

| Durum | is_final | Açıklama |
|-------|----------|----------|
| V_STEM | ❌ | Fiil kökü — tek başına geçerli çekim değil |
| NEGATION | ❌ | Olumsuzluk — tek başına geçerli değil |
| TENSE | ✅ | 3. tekil şahıs boyutunda final |
| PERSON | ✅ | Şahıs eki sonrası final |

### 4.4 Zaman Kodu Envanteri — 18 Kod

`VerbMorphotactics.TENSE_CODE_MAP` ve `TENSE_DISPLAY`:

| Grup | Kod | Motor | Türkmence Adı | Ek kalıbı |
|------|-----|-------|---------------|-----------|
| **Öten Zaman** | Ö1 | 1 | Anyk Öten | `-dy/-di/-du/-dü` + şahıs |
| | Ö2 | 2 | Daş Öten | `-ypdy/-ipdi` + şahıs |
| | Ö3 | 3 | Dowamly Öten | `-ýardy/-ýärdi` + şahıs |
| **Häzirki Zaman** | H1 | 4 | Umumy Häzirki | `-ýar/-ýär` + genişletilmiş şahıs |
| | H2 | 5 | Anyk Häzirki | otyr/dur/ýatyr/ýör + özel ek |
| **Geljek Zaman** | G1 | 6 | Mälim Geljek | `-jak/-jek` + kopula(`dir/dyr`) + genişl. şahıs |
| | G2 | 7 | Nämälim Geljek | `-ar/-er/-r` + genişl. şahıs |
| **Yeni Kipler** | Ş1 | 8 | Şert formasy | `-sa/-se` + standart şahıs |
| | B1K | 9 | Buýruk formasy | Şahıs bazlı özel kalıplar |
| | HK | 10 | Hökmanlyk | `-maly/-meli` [+ `däl`] |
| | NÖ | 11 | Nätanyş Öten | `-ypdyr/-ipdir` + genişl. şahıs |
| | AÖ | 12 | Arzuw-Ökünç | `-sa/-se` + `-dy/-di` + standart şahıs |
| **Fiilimsi** | FH | 13 | Hal işlik | `-yp/-ip/-up/-üp/-p` |
| | FÖ | 14 | Öten ortak | `-an/-en` |
| | FÄ | 15 | Häzirki ortak | `-ýan/-ýän` |
| | FG | 16 | Geljek ortak | `-jak/-jek` |
| **İşlik Derejesi** | ETT | 17 | Ettirgen | `-dyr/-dir/-dur/-dür` / `-t` |
| | EDL | 18 | Edilgen | `-yl/-il/-ul/-ül` / `-yn/-in/-un/-ün` |

---

## 5. Sentez Motoru (`generator.py`)

### 5.1 Sınıf Hiyerarşisi

```python
class NounGenerator:          # İsim çekimi
class VerbGenerator:          # Fiil çekimi
class MorphologicalGenerator: # Birleşik arayüz (NounGen + VerbGen)
```

`MorphologicalGenerator` her iki motoru sararak tek API sunar:
```python
gen = MorphologicalGenerator(lexicon)
gen.generate_noun("kitap", plural=True, possessive="A1")
gen.generate_verb("gel", tense="1", person="A1")
gen.analyze_noun(root, s_code, i_code, h_code)  # Flask uyumlu
gen.analyze_verb(root, tense_code, person_code, negative)  # Flask uyumlu
```

### 5.2 İsim Sentez Pipeline'ı — `NounGenerator.generate()`

```
1. State machine doğrulama (NounMorphotactics.validate_noun_params)
2. Yuvarlaklaşma kontrolü (Berdi Hoca kuralı: guzy→guzu)
3. Çoğul eki ekleme (-lar/-ler, ünlü uyumu + yuvarlaklaşma)
4. İyelik eki ekleme (ünlü düşmesi + ünsüz yumuşaması + 4-yönlü uyum)
5. Hal eki ekleme (n-kaynaştırma + ilgi hali yuvarlak kuralı)
6. GenerationResult döndürme (word, breakdown, morphemes)
```

**İlgi hali yuvarlak kuralı (TurkmenFST'nin önemli avantajı):**
```python
if len(stem) <= 4 and kok_yuvarlak:
    ek = "uň" if nit == "yogyn" else "üň"   # göz → gözüň
else:
    ek = "yň" if nit == "yogyn" else "iň"     # kitap → kitabyň
```
Apertium'da bu kural tanımlı değildir → kısa yuvarlak köklerde (`göz, suw, gol`) sistematik hata üretir.

### 5.3 Fiil Sentez Pipeline'ı — `VerbGenerator.generate()`

```
1. Ünlü niteliği belirleme (get_vowel_quality)
2. Ünlü sonu kontrolü (ends_with_vowel)
3. Zamana göre dallanma (18 zaman kodu)
4. Olumsuzluk stratejisi (zamana bağlı: sentetik veya analitik)
5. Şahıs eki seçimi (standart veya genişletilmiş)
6. GenerationResult döndürme
```

### 5.4 Şahıs Eki Tabloları

**Standart tablo** (Ö1, Ö2, Ö3, Ş1, AÖ zamanları):

| Kişi | Kalın (yogyn) | İnce |
|------|---------------|------|
| A1 | -m | -m |
| A2 | -ň | -ň |
| A3 | ∅ | ∅ |
| B1 | -k | -k |
| B2 | -ňyz | -ňiz |
| B3 | -lar | -ler |

**Genişletilmiş tablo** (H1, G2, NÖ zamanları):

| Kişi | Kalın (yogyn) | İnce |
|------|---------------|------|
| A1 | -yn | -in |
| A2 | -syň | -siň |
| A3 | ∅ | ∅ |
| B1 | -ys | -is |
| B2 | -syňyz | -siňiz |
| B3 | -lar | -ler |

### 5.5 Olumsuzluk Stratejileri

| Zaman | Strateji | Kalıp |
|-------|----------|-------|
| Ö1 | Sentetik | `kök + ma/me + dy/di + şahıs` |
| Ö2 | Birleşik | `kök + män/man + di/dy + şahıs` (enedilim düzeltmesi) |
| Ö3 | **Analitik** | `kök + ýan/ýän + däldi + şahıs` (perifrastik) |
| H1 | Sentetik | `kök + me/ma + ýar/ýär + şahıs` |
| G1 | Analitik | `kök + jak/jek + däl` (şahıs eki yok) |
| G2 | Özel | A1/A2/B1/B2: `-mar/-mer`; A3/B3: `-maz/-mez` |
| Ş1 | Sentetik | `kök + ma/me + sa/se + şahıs` |
| B1K | Sentetik | `kök + ma/me + şahıs bazlı` |
| HK | Analitik | `kök + maly/meli + däl` |
| NÖ | Birleşik | `kök + mandyr/mändir + şahıs` |
| AÖ | Sentetik | `kök + ma/me + sa/se + dy/di + şahıs` |

### 5.6 Yeni Kipler — Detaylı Kurallar

#### Ş1 — Şert Formasy (Şart Kipi)
- Kalıp: `kök + [ma/me] + sa/se + standart_şahıs`
- Örnekler: gel → gelsem, gelse, gelmesem

#### B1K — Buýruk Formasy (Emir Kipi)
Şahıs bazlı özel kal:

| Şahıs | Olumlu kalıp | Örnek (gel) | Olumsuz kalıp | Örnek |
|--------|-------------|-------------|---------------|-------|
| A1 | -aýyn/-eýin (ünsüz); -ýyn/-ýin (ünlü) | geleýin | -ma/-me + ýyn/ýin | gelmeýin |
| A2 | çıplak kök | gel | -ma/-me | gelme |
| A3 | -syn/-sin (std); -sun/-sün (dodak) | gelsin, dursun | -ma/-me + syn/sin | gelmesin |
| B1 | -aly/-eli; ünlü: -ly/-li | geleli | -ma/-me + ly/li | gelmeli |
| B2 | -yň/-iň (std); -uň/-üň (dodak); ünlü: -ň | geliň, görüň | -ma/-me + ň | gelmeň |
| B3 | -synlar/-sinler; -sunlar/-sünler (dodak) | gelsinler | -ma/-me + synlar/sinler | gelmesinler |

**Dodak uyumu notu:** Olumlu formda tek heceli yuvarlak kökler A3 ve B3'te -sun/-sün alır. Olumsuzda `-ma/-me` eklendikten sonra dodak uyumu iptal olur.

#### HK — Hökmanlyk Formasy (Gereklilik)
- Olumlu: `kök + maly/meli`
- Olumsuz: `kök + maly/meli + däl` (analitik)
- Şahıs eki yoktur.
- Örnekler: gelmeli, almaly, gelmeli däl

#### NÖ — Nätanyş Öten (Kanıtsal / Evidential)
- Olumlu: `kök + ypdyr/ipdir + genişletilmiş_şahıs`
- Olumsuz: `kök + mandyr/mändir + genişletilmiş_şahıs`
- Dodak fiillerde: -updyr/-üpdir (dur → durupdyr)
- Örnekler: gelipdir, gelipdirin, gelmändir

#### AÖ — Arzuw-Ökünç (Dileksi / Optative)
- Kalıp: `kök + [ma/me] + sa/se + dy/di + standart_şahıs`
- Yapısal olarak Şert (sa/se) + Anyk Öten (dy/di) birleşimi
- Örnekler: gelsedim, gelsedi, gelmesedim

### 5.7 Fiilimsi Formları — Şahıs Eki Almaz

| Form | Olumlu | Olumsuz | Örnekler |
|------|--------|---------|----------|
| FH — Hal işlik | `-yp/-ip/-up/-üp/-p` | `-man/-män` | gelip, alyp, durup; gelmän |
| FÖ — Öten ortak | `-an/-en` (ünlü sonu: `-n`) | `-madyk/-medik` | gelen, alan, okan; gelmedik |
| FÄ — Häzirki ortak | `-ýan/-ýän` | `-maýan/-meýän` | gelýän, alýan; gelmeýän |
| FG — Geljek ortak | `-jak/-jek` | `-majak/-mejek` | geljek, aljak; gelmejek |

**Dodak uyumu (FH):** Tek heceli yuvarlak kökler: -up/-üp (dur → durup, gör → görüp).

### 5.8 İşlik Derejeleri (Fiil Çatısı) — Şahıs Eki Almaz

#### ETT — Ettirgen (Causative)
| Kök tipi | Ek | Örnek |
|----------|-----|-------|
| Ünlüyle biten | `-t` | oka → okat |
| Tek heceli dodak | `-dur/-dür` | dur → durdur, gör → gördür |
| Diğer | `-dyr/-dir` | gel → geldir, al → aldyr, bar → bardyr |

#### EDL — Edilgen (Passive)
| Kök tipi | Ek | Örnek |
|----------|-----|-------|
| Ünlüyle biten (önceki harf l) | `-n` | söýle → söýlen |
| Ünlüyle biten (diğer) | `-l` | oka → okal |
| l ile biten + dodak | `-un/-ün` | gül → gülün |
| l ile biten + diğer | `-yn/-in` | gel → gelin, al → alyn |
| Diğer + dodak | `-ul/-ül` | gör → görül, dur → durul |
| Diğer | `-yl/-il` | ber → beril, bar → baryl |

---

## 6. Analiz Motoru (`analyzer.py`)

### 6.1 Strateji: Üretici Doğrulamalı Ters Çözümleme

```
Girdi: Çekimli yüzey formu (ör. "kitabymyň")
  1. Sözlükten olası kök adaylarını belirle
  2. Her kök adayı için tüm ek kombinasyonlarını generator ile üret
  3. Üretilen yüzey formunu giriş kelimesiyle karşılaştır
  4. Eşleşme → başarılı analiz
Çıktı: AnalysisResult(stem="kitap", suffixes=[...], breakdown="...")
```

**Avantaj:** Fonolojik kurallar analiz modülünde tekrar kodlanmaz — sentez motorunun kuralları dolaylı olarak çalışır. Bu, sentez-analiz arasında **%100 tutarlılık** garantisi sağlar.

### 6.2 Veri Yapıları

```python
@dataclass
class AnalysisResult:
    success: bool
    original: str        # Giriş kelimesi
    stem: str            # Bulunan kök
    suffixes: list       # Ek listesi [{suffix, type, code}, ...]
    breakdown: str       # "Kitap (Kök) + lar (S2) + ym (D₁b)"
    word_type: str       # "noun" / "verb"
    meaning: str         # Eş sesli kelimeler için anlam

@dataclass
class MultiAnalysisResult:
    original: str
    results: list[AnalysisResult]
```

### 6.3 Çapraz Tekilleştirme (Cross-Deduplication)

Eş sesli kelimeler için birden fazla çözümleme üretilebilir. `breakdown_key` mekanizması, farklı anlamlardan gelen ama aynı ek dizisine sahip sonuçları eleyerek tekrarsız çıktı verir.

---

## 7. İsim Çekimi Paradigması

### 7.1 Tam Envanter

**Çekim şeması:** `KÖK + [çoğul -lar/-ler] + [iyelik] + [hal]`

**6 hal:**
| Hal | Kod | Ünsüz sonu | Ünlü sonu | İyelik sonrası (A3) |
|-----|-----|-----------|-----------|---------------------|
| Yalın | A1 | ∅ | ∅ | ∅ |
| İlgi | A2 | -yň/-iň (std); -uň/-üň (≤4 harf+yuvarlak) | -nyň/-niň | -nyň |
| Yönelme | A3 | -a/-e | son ünlü → a/ä | -na/-ne |
| Belirtme | A4 | -y/-i (yumuşama uygulanır) | -ny/-ni | -ny/-ni |
| Bulunma | A5 | -da/-de | -da/-de | -nda |
| Çıkma | A6 | -dan/-den | -dan/-den | -ndan |

**3 iyelik (tekil) + 2 iyelik (çoğul):**
| Kişi | Kod | Ünsüz sonu | Ünlü sonu |
|------|-----|-----------|-----------|
| 1.tekil | A1 | -ym/-im/-um/-üm | -m |
| 2.tekil | A2 | -yň/-iň/-uň/-üň | -ň |
| 3.tekil | A3 | -y/-i | -sy/-si (yuvarlak: -su/-sü) |
| 1.çoğul | B1 | A1 eki + -yz/-iz | - |
| 2.çoğul | B2 | A2 eki + -yz/-iz | - |

**Toplam kombinasyon:** 6 hal × (1+5 iyelik) × 2 (tekil/çoğul) = 72 olası form/kök

---

## 8. Fiil Çekimi Paradigması

### 8.1 Temel 7 Zaman × 6 Şahıs × 2 (Olumlu/Olumsuz)

Toplam: 7 × 6 × 2 = **84** temel fiil çekim formu / kök

### 8.2 Yeni 5 Kip

Toplam: 5 × 6 × 2 = **60** kip formu

### 8.3 Fiilimsi (4 form) + İşlik Derejesi (2 form)

Fiilimsi: 4 × 2 (olumlu/olumsuz) = **8** form
İşlik derejesi: 2 form (şahıs/olumsuzluk eki almaz)

### 8.4 Genel Toplam

84 + 60 + 8 + 2 = **154** potansiyel form başına kök fiil × 6.471 fiil kökü = ~995.000+ üretilebilir fiil formu (teorik).

---

## 9. enedilim.com Doğrulaması ve Berdi Hoca Kuralları

### 9.1 enedilim.com Senkronizasyonu

Türkmenistan devlet dili resmi portalı olan enedilim.com, sistemin **birincil doğrulama kaynağıdır**. Yapılan çalışmalar:

1. **Sözlük doğrulama:** 20.120 başlık kelimesinin tamamı sözlükte mevcuttur (%100 kapsama).
2. **POS doğrulama:** enedilim API'sinden alınan POS bilgileriyle çapraz kontrol yapılmıştır.
3. **Fiil çekim doğrulama:** 7 temel zamanda paradigma tabloları enedilim.com ile birebir karşılaştırılmış, 4 uyumsuzluk tespit edilip düzeltilmiştir:
   - Ö2 olumsuz: `-me+ipdi` → `-män+di`
   - Ö3 olumsuz: `-me+ýärdi` → `-ýän däldi` (analitik)
   - G1 olumlu: kopula kişi ekleri eklendi (`-jakdyryn/-jekdirin`)
   - G2 olumsuz: `-mar/-mer` vs `-maz/-mez` kişi ayrımı

### 9.2 Berdi Hoca Özel Kuralları

enedilim.com'daki öğretim materyallerinden (Berdi Hoca derslerinden) tespit edilen ek kurallar:

1. **Yuvarlaklaşma listesi:** guzy→guzu, süri→sürü, guýy→guýu (3 kelime)
2. **İlgi hali yuvarlak kuralı:** ≤4 harf + yuvarlak ünlü → -uň/-üň (göz→gözüň, suw→suwuň)

Bu kurallar ne Apertium'da ne de diğer kaynaklarda belgelenmiştir; enedilim.com'a özgü ve dolaylı dilbilimsel bilgi olarak sisteme entegre edilmiştir.

---

## 10. Apertium Karşılaştırması — Makale Özeti

### 10.1 İsim Karnesi

| Kriter | TurkmenFST | Apertium-tuk |
|--------|:---------:|:-----------:|
| 6 temel hal | ✅ | ✅ |
| İlgi hali yuvarlak kural | ✅ | ❌ |
| Yuvarlaklaşma | ✅ | ❌ |
| Ünlü düşmesi | ✅ | ✅ |
| İyelik (6 kişi) | ✅ | ✅ |
| Ünsüz yumuşaması | ✅ | ✅ |
| -daky bulunma sıfatı | ❌ | ✅ |
| -syz yokluk eki | ❌ | ✅ |
| Sözlük boyutu | **32K** | ~2K |
| **Puan** | **6/8** | **6/8** |

### 10.2 Fiil Karnesi

| Kriter | TurkmenFST | Apertium-tuk |
|--------|:---------:|:-----------:|
| 7 temel zaman | ✅ | ✅ |
| 5 ek kip (Şert/Buýruk/HK/NÖ/AÖ) | ✅ | ✅ |
| 4 fiilimsi | ✅ | ✅ |
| Ettirgen/Edilgen | ✅ | ✅ |
| 6 kişi çekimi | ✅ | ✅ |
| Olumlu/olumsuz | ✅ | ✅ |
| G2 olumsuz -mar/-mer ayrımı | ✅ | ❌ |
| Ö2 olumsuz -män kalıbı | ✅ | ❌ |
| Ö3 olumsuz analitik yapı | ✅ | ❌ |
| G1 kopula kişi ekleri | ✅ | ❌ |
| enedilim.com doğrulaması | ✅ | ❌ (20+ FIXME) |

### 10.3 Mimari Farklılıklar

| Boyut | TurkmenFST | Apertium-tuk |
|-------|-----------|--------------|
| **Uygulama** | Python prosedürel + FST-inspired state machine | HFST: lexc + twol deklaratif |
| **Sözlük formatı** | Yüzey form (kitap) | Underlying form (kitab) |
| **Yumuşama yönü** | Sert→yumuşak (ek öncesi) | Yumuşak→sert (sözcük sonu) |
| **Fonoloji** | `PhonologyRules` static methods | twol iki düzeyli kurallar |
| **Test** | 105 pytest + 124 yeni + 4.788 ref + 1.192 RT | Temel test dosyaları |
| **Sözlük** | 32.015 kök (5 kaynak) | ~2.000 leksikon girişi |
| **FIXME** | 0 | 20+ |

---

## 11. Test Verileri

| Test Seti | Sayı | Durum |
|-----------|------|-------|
| Birim testleri (pytest) | 105 | ✅ %100 |
| Yeni fiil form testleri (test_new_verb_forms.py) | 124 | ✅ %100 |
| v26 referans eşleşme | 4.788 | ✅ %100 |
| Round-trip (tur-dönüş) | 1.192 | ✅ %100 |
| API endpoint testleri | 18 | ✅ %100 |
| **Toplam** | **6.227** | ✅ |

---

## 12. Web Arayüzü ve API

- **Flask** tabanlı web uygulaması
- **Vercel** üzerinde canlı: `turkmence-morfolojik-analiz.vercel.app`
- 4 sekmeli web arayüzü: İsim Çekimi, Fiil Çekimi, Morfolojik Analiz (Derňew), Paradigma
- 7 RESTful endpoint (JSON)
- Fiil çekimi dropdown: 4 optgroup (İşlik Formalary, Fiilimsi, İşlik Derejeleri)
- Eş sesli kelimeler için çift paradigma tablosu
- GitHub: `aydesma/turkmence-morfolojik-analiz` (MIT lisansı)

---

## 13. Makalede Güncellenecek Bölümler

MAKALE_TURKLANG.md'de aşağıdaki bölümler yeni eklenen formları yansıtacak şekilde güncellenmelidir:

1. **Öz / Abstract:** "7 zaman × 6 şahıs" → "18 zaman/kip/form kodu (7 temel zaman + 5 kip + 4 fiilimsi + 2 çatı)"
2. **§1 Giriş, madde 3:** İsim ve fiil çekimi açıklaması genişletilmeli
3. **§3.3 Fiil Çekimi tablosu:** 7'den 18'e genişletilmeli
4. **§4.3 Morfotaktik:** Fiil FST diyagramı 18 kodu yansıtmalı
5. **§4.4 Sentez Motoru:** VerbGenerator açıklaması yeni formları kapsamalı
6. **§7 Değerlendirme tablosu:** Test sayıları güncellenmeli (105+124+4788+1192+18)
7. **§8 Tartışma, Sınırlılıklar:** "-daky ve -syz henüz eksik" kalmalı; "5 ek kip, fiilimsi, çatı eklendi" notu eklenmeli
8. **§8 Gelecek Çalışmalar:** Kısa vadede türetim ekleri öncelikli; fiil kiplerini "tamamlandı" olarak işaretle
9. **§9 Sonuç:** Rakamları güncelle
10. **Tablo 5:** Yeni test satırı ekle (124 yeni fiil form testi)
11. **Tablo 6 Karşılaştırma:** Fiil kip/form kapsamı sütunu eklenebilir
