# TurkmenFST — Türkmen Türkçesi Morfolojik Analiz Motoru

Finite-State Automaton (FST) mimarisinden ilham alan, modüler ve genişletilebilir bir
Türkmence morfolojik analiz ve sentez (üretim) sistemi.

## Özellikler

| Özellik | Açıklama |
|---------|----------|
| **İsim çekimi** | 6 hal × 3 iyelik × 2 çoğul — tam paradigma üretimi |
| **Fiil çekimi** | 7 zaman × 6 şahıs × olumlu/olumsuz = 84 çekim formu |
| **Morfolojik analiz** | Çekimli kelime → kök + morfem ayrıştırması |
| **Fonoloji kuralları** | Ünlü uyumu, ünsüz yumuşaması, ünlü düşmesi, yuvarlaklaşma |
| **State machine** | FST-ilhamlı morfotaktik doğrulama (ek sırası kontrolü) |
| **Zenginleştirilmiş sözlük** | 30 000+ kelime, morfolojik özellik etiketleri |
| **REST API** | FastAPI tabanlı JSON API |
| **Web arayüzü** | Flask tabanlı interaktif çekim arayüzü |
| **CLI** | Komut satırı araçları (üretim, analiz, interaktif) |

---

## Kurulum

```bash
# Temel kurulum
pip install -e .

# API desteğiyle
pip install -e ".[api]"

# Web arayüzüyle
pip install -e ".[web]"

# Geliştirme (tüm bağımlılıklar)
pip install -e ".[dev]"
```

---

## Hızlı Başlangıç

### Python API

```python
from turkmen_fst import MorphologicalGenerator, MorphologicalAnalyzer, Lexicon

# Sözlük yükle
lexicon = Lexicon()
lexicon.load("data/turkmence_sozluk.txt")

# Sentez (Üretim)
gen = MorphologicalGenerator(lexicon)

# İsim çekimi: kitap + çoğul + 1. tekil iyelik
result = gen.generate_noun("kitap", plural=True, possessive="A1")
print(result.word)       # kitaplarymy
print(result.breakdown)  # kitap + lar + ym

# Fiil çekimi: gel + geçmiş zaman + 1. tekil
result = gen.generate_verb("gel", tense="1", person="A1")
print(result.word)       # geldim

# Analiz (Ayrıştırma)
analyzer = MorphologicalAnalyzer(lexicon)
result = analyzer.parse_noun("kitabym")
print(result.stem)       # Kitap
print(result.suffixes)   # [{'suffix': 'ym', 'type': 'Degişlilik', 'code': 'A1'}]
```

### Komut Satırı (CLI)

```bash
# İsim çekimi
python -m turkmen_fst generate --stem kitap --type noun --plural --poss A1

# Fiil çekimi
python -m turkmen_fst generate --stem gel --type verb --tense 1 --person A1

# Kelime analizi
python -m turkmen_fst analyze kitabym geldi

# İnteraktif mod
python -m turkmen_fst interactive

# API sunucusu başlat
python -m turkmen_fst serve --port 8000
```

### REST API

```bash
# Sunucuyu başlat
python -m turkmen_fst serve

# İsim çekimi
curl -X POST http://localhost:8000/generate/noun \
  -H "Content-Type: application/json" \
  -d '{"stem": "kitap", "plural": true, "possessive": "A1"}'

# Kelime analizi
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"word": "kitabym"}'

# Swagger belgeleri
open http://localhost:8000/docs
```

### Web Arayüzü

```bash
cd web
python app.py
# → http://localhost:5001
```

---

## Mimari

```
turkmen_fst/
├── phonology.py       # Fonoloji kuralları (ünlü uyumu, yumuşama, düşme)
├── lexicon.py         # Sözlük yönetimi (kelime yükleme, özellik etiketleri)
├── morphotactics.py   # FST state machine (ek sırası doğrulama)
├── generator.py       # Sentez motoru (kök + ekler → çekimli kelime)
├── analyzer.py        # Analiz motoru (çekimli kelime → kök + ekler)
├── cli.py             # Komut satırı arayüzü
├── api.py             # FastAPI REST API
└── __main__.py        # python -m turkmen_fst giriş noktası

data/
└── turkmence_sozluk.txt  # 30 000+ kelimelik zenginleştirilmiş sözlük

web/
├── app.py             # Flask web arayüzü
└── templates/
    └── index.html     # Web UI şablonu

tests/
├── test_phonology.py      # Fonoloji birim testleri (36 test)
├── test_morphotactics.py  # State machine testleri (33 test)
├── test_generator.py      # v26 referans doğrulama (4788 vaka + 15 test)
├── test_analyzer.py       # Analiz testleri (21 test)
└── v26_reference.json     # v26.0 referans sonuçları
```

---

## Modüller

### `phonology.py` — Fonoloji Kuralları

| Kural | Açıklama | Örnek |
|-------|----------|-------|
| Ünlü niteliği | yogyn (kalın) / ince | bar → yogyn, gel → ince |
| Ünsüz yumuşaması | p→b, t→d, ç→j, k→g | kitap → kitab+ym |
| Ünlü düşmesi | Son hecedeki ünlü düşer | burun → burn+y |
| Yuvarlaklaşma | y/i → u/ü (yuvarlak kök) | göl → göl+ler |
| İstisna düşmesi | Özel kökler (asyl → asl) | asyl → asl+y |

### `morphotactics.py` — State Machine

İsim: `STEM → [PLURAL] → [POSSESSIVE] → [CASE]`  
Fiil: `V_STEM → [NEGATION] → TENSE → [PERSON]`

### `lexicon.py` — Sözlük Formatı

```
kelime<TAB>pos<TAB>özellikler
kitap	%<n%>	softening
burun	%<n%>	vowel_drop
asyl	%<n%>	exception_drop:asl
at	%<n%>	softening;homonym:1=A:T_(Ad,_isim)|yes;2=AT_(At,_beygir)|no
```

**Özellik etiketleri:**
- `softening` — ünsüz yumuşaması uygulanan kelimeler
- `vowel_drop` — ünlü düşmesi adayları
- `exception_drop:X` — istisna ünlü düşmesi (X = düşmüş hali)
- `homonym:...` — eş sesli kelime bilgisi

---

## Test

```bash
# Tüm testleri çalıştır
python -m pytest tests/ -v

# Sadece v26 referans doğrulama
python -m pytest tests/test_generator.py -v

# Kapsamlı rapor
python -m pytest tests/ -v --tb=long
```

**Test sonuçları:**
- ✅ 105/105 test başarılı
- ✅ 4788/4788 v26 referans çekim eşleşmesi (%100)

---

## İsim Çekim Kodları

| Parametre | Kod | Açıklama |
|-----------|-----|----------|
| Çoğul | `plural=True` | -lar / -ler |
| 1. tekil iyelik | `A1` | -(y)m / -(i)m |
| 2. tekil iyelik | `A2` | -(y)ň / -(i)ň |
| 3. tekil iyelik | `A3` | -(s)y / -(s)i |
| İlgi hali | `A2` | -(n)yň |
| Yönelme hali | `A3` | -(n)a / -(n)e |
| Belirtme hali | `A4` | -(n)y / -(n)i |
| Bulunma hali | `A5` | -(n)da |
| Çıkma hali | `A6` | -(n)dan |

## Fiil Zaman Kodları

| Kod | Zaman | Örnek (gel-) |
|-----|-------|-------------|
| `1` (Ö1) | Anyk Öten (belirli geçmiş) | geldim |
| `2` (Ö2) | Daş Öten (belirsiz geçmiş) | gelipdim |
| `3` (Ö3) | Dowamly Öten (sürekli geçmiş) | gelýärdim |
| `4` (H1) | Umumy Häzirki (geniş şimdiki) | gelýärin |
| `5` (H2) | Anyk Häzirki (kesin şimdiki) | (yardımcı fiil gerektirir) |
| `6` (G1) | Mälim Geljek (belirli gelecek) | men geljek |
| `7` (G2) | Nämälim Geljek (belirsiz gelecek) | gelerin |

---

## Kullanım Alanları

### Şu An Aktif Olan Yetenekler

| Alan | Açıklama | Durum |
|------|----------|-------|
| **Morfolojik Üretim (Generation)** | Kök + ek parametreleri → Çekimli kelime (`kitap + ym → kitabym`) | ✅ Aktif |
| **Morfolojik Analiz (Analysis)** | Çekimli kelime → Kök + ek çözümlemesi (`kitabym → kitap + ym`) | ✅ Aktif |
| **REST API** | Dış uygulamalar için JSON API (FastAPI + Swagger) | ✅ Aktif |
| **Web Arayüzü** | Tarayıcı üzerinden interaktif çekim ekranı | ✅ Aktif |
| **CLI** | Terminal üzerinden toplu/tekli üretim ve analiz | ✅ Aktif |

### Doğrudan Uygulanabilir Kullanımlar

#### 1. Yazım Denetimi (Spell Checker)

Sözlük + morfoloji kuralları birlikte kullanılarak doğru yazım kontrolü yapılabilir.
Motor, yazılan kelimenin:
- Sözlükteki bir köke ait olup olmadığını,
- Eklerin doğru sırada ve doğru formda olup olmadığını,
- Fonoloji kurallarına (ünlü uyumu, ünsüz yumuşaması) uyup uymadığını kontrol eder.

```python
from turkmen_fst import MorphologicalAnalyzer, Lexicon

lexicon = Lexicon()
lexicon.load("data/turkmence_sozluk.txt")
analyzer = MorphologicalAnalyzer(lexicon)

# Doğru yazım → kök bulunur
result = analyzer.parse("kitabym")    # ✅ kitap + ym
print(result.success)                 # True

# Yanlış yazım → kök bulunamaz
result = analyzer.parse("kitapbym")   # ❌ geçersiz
print(result.success)                 # stem bulunamaz veya eşleşmez
```

#### 2. Eğitim Yazılımları

Türkmence öğrenenler için interaktif çekim araçları:
- **Paradigma tabloları**: Bir kelimenin tüm çekim formlarını otomatik oluşturma
- **Alıştırma üreteci**: Rastgele çekim soruları ve doğru cevap kontrolü
- **Ek analizi**: Öğrencinin yazdığı kelimeyi parçalara ayırarak açıklama

```python
# Bir kelimenin tam paradigmasını oluştur
gen = MorphologicalGenerator(lexicon)
cases = [None, "A2", "A3", "A4", "A5", "A6"]
for case in cases:
    r = gen.generate_noun("kitap", case=case)
    print(f"{case or 'Yalın':5s} → {r.word}")
```

#### 3. Makine Çevirisi (MT)

Çeviri sistemlerinde Türkmence morfolojik ön/son işleme:
- **Ön işleme**: Çekimli kelimeleri köke indirgeyerek çeviri kalitesini artırma
- **Son işleme**: Çevrilmiş kökler + hedef dil ekleri → doğru çekimli kelime üretme
- **Subword tokenization**: BPE/SentencePiece yerine dilbilgisel birim bazlı tokenizasyon

#### 4. Metin Madenciliği / NLP

- **Kök ayırma (Stemming)**: Metin sınıflandırma, arama motorları için kelimeleri köke indirgeme
- **Lemmatization**: Kelimenin sözlük formunu (lemma) bulma
- **Özellik çıkarımı**: Metindeki morfolojik yapıları (çoğul, iyelik, zaman) algılama
- **Arama motoru**: `kitabym`, `kitabyň`, `kitapda` → hepsi "kitap" aramasında bulunsun

#### 5. Dil Belgeleme

Türkmen dilinin morfolojik kurallarının formal tanımı:
- State machine ile ek sırası kuralları (hangi ek hangi ekten sonra gelebilir)
- Fonoloji kurallarının programatik ifadesi
- 4788 doğrulanmış test vakasıyla kural kapsamı belgeleme

### Entegrasyon Olanakları

#### LibreOffice Eklentisi (Yazım Denetimi)

TurkmenFST, LibreOffice için yazım denetimi eklentisi olarak kullanılabilir.
LibreOffice, Hunspell tabanlı `.dic` / `.aff` dosyaları veya Python-UNO makrolarıyla
özel yazım denetçileri destekler.

**Yöntem 1 — Hunspell Sözlük Üretimi:**

Motor kullanılarak tüm kelimelerin çekim formları üretilebilir ve standart
Hunspell formatına dönüştürülebilir:

```python
# Tüm sözlükteki isimlerin çekim formlarını üret → .dic dosyasına yaz
import turkmen_fst

lexicon = turkmen_fst.Lexicon()
lexicon.load("data/turkmence_sozluk.txt")
gen = turkmen_fst.MorphologicalGenerator(lexicon)

with open("tk_TM.dic", "w", encoding="utf-8") as f:
    for entry in lexicon.get_nouns():
        forms = set()
        forms.add(entry.word)
        for case in [None, "A2", "A3", "A4", "A5", "A6"]:
            for poss in [None, "A1", "A2", "A3"]:
                for plural in [False, True]:
                    r = gen.generate_noun(entry.word, plural=plural,
                                         possessive=poss, case=case)
                    forms.add(r.word)
        for form in sorted(forms):
            f.write(form + "\n")
```

**Yöntem 2 — Python-UNO Makrosu (Gerçek Zamanlı):**

LibreOffice'in Python-UNO arayüzüyle doğrudan motor çağrılabilir.
Bu yöntem, sadece önceden üretilmiş kelime listelerine değil,
gerçek zamanlı morfolojik analize dayanır.

**Yöntem 3 — LanguageTool Entegrasyonu:**

Açık kaynaklı [LanguageTool](https://languagetool.org/) projesine Türkmence
kuralları eklemek mümkündür. TurkmenFST'nin morfoloji kuralları Java'ya
taşınarak veya API olarak çağrılarak gramer kontrolü sağlanabilir.

#### Microsoft Office Eklentisi

Office 365 eklentileri JavaScript/TypeScript ile yazılır. TurkmenFST'nin
REST API'si kullanılarak Word eklentisi geliştirilebilir:

```
Word Eklentisi (JS) ←→ TurkmenFST API (localhost:8000) ←→ Morfoloji Motoru
```

- **Office Add-in SDK** ile taskpane eklentisi oluşturulur
- Kullanıcı belge yazdıkça arka planda API'ye sorgu gönderilir
- Hatalı çekimler kırmızı çizgiyle işaretlenir
- Doğru öneri listesi morfolojik üretimle sağlanır

#### Tarayıcı Eklentisi (Chrome/Firefox)

REST API üzerinden tarayıcı eklentisi ile her web sayfasında yazım kontrolü:

```
Tarayıcı Eklentisi ←→ POST /analyze ←→ TurkmenFST API
```

#### Telegram / WhatsApp Bot

Chatbot olarak morfolojik sorgulama:
- Kullanıcı: `çekim kitap çoğul A1`
- Bot: `kitaplarym (kitap + lar + ym)`

#### VS Code Eklentisi

Türkmence metin dosyalarında yazım denetimi sağlayan Language Server Protocol
(LSP) tabanlı VS Code eklentisi:
- `.tkm` veya `.txt` dosyalarında gerçek zamanlı yazım kontrolü
- Quick fix önerileri (morfolojik üretimle doğru formlar)

---

## Lisans

MIT

---

## Katkıda Bulunma

1. Fork edin
2. Feature branch oluşturun (`git checkout -b feature/yeni-ozellik`)
3. Testleri çalıştırın (`python -m pytest tests/ -v`)
4. PR gönderin

> v26 referans uyumluluğunu koruyan değişiklikler kabul edilir.
> `test_generator.py::test_all_noun_inflections` %100 geçmek zorundadır.
