# TurkmenFST — Yapılan Değişikliklerin Ayrıntılı Dokümantasyonu

> Son güncelleme: 25 Şubat 2026

---

## Genel Bakış

Bu belge, TurkmenFST projesinde yapılan tüm değişiklikleri dosya bazında ayrıntılı olarak belgelemektedir.

---

## 1. Sözlük Dosyası — `turkmen-fst/data/turkmence_sozluk.txt`

### Mevcut Durum
- **Toplam kelime:** 54.783+
- **Format:** `kelime<TAB>%<pos%><TAB>özellikler`

### Yapılan Değişiklikler

#### 1.1 Hunspell İthalatı (Önceki Oturum)
- **Ne yapıldı:** Hunspell `.dic` dosyasından (FLAG num, AF alias bayrakları) kelimeler ithal edildi
- **Sonuç:** 1.733 → 38.480 kelime (36.747 yeni kelime)
- **Detaylar:**
  - Hunspell grup /21 (fiiller), /26 (fiiller), /1-/20 (isimler, sıfatlar, vb.)
  - 109 fiil kökü düzeltildi: `-mak`/`-mek` son eki silindi (örn. `almak` → `al`)
  - POS etiketleri Hunspell gruplarına göre otomatik atandı

#### 1.2 tum.txt İthalatı (Bu Oturum)
- **Ne yapıldı:** `turkmence_sozluk_tum.txt`'den 16.308 kelime ithal edildi
- **Kaynak:** 111.147 satırlık Türkmen orfoepik sözlüğü
- **İthal edilen:**
  - **335 fiil kökü** (`%<v%>` etiketi) — tire ile biten girişlerden (`kelime-`)
  - **14.857 saf kelime** (`%<n?%>` etiketi) — düz metin girişlerinden
  - **1.116 açıklamalı kelime** (`%<n?%>` etiketi) — parantezli açıklamalı girişlerden
- **Filtrelenen:** 71.158 türetilmiş form (mastarlar, sıfat-fiiller, soyut isimler, sıfatlar) ithal **edilmedi**
- **Sözlükteki bölümler:**
  ```
  # === tum.txt'den eklenen Fiil Kökleri (335 adet) ===
  # === tum.txt'den eklenen Saf Kelimeler (14857 adet) - POS belirsiz ===
  # === tum.txt'den eklenen Açıklamalı Kelimeler (1116 adet) - POS belirsiz ===
  ```

### POS Dağılımı

| POS | Sayı | Yüzde |
|-----|------|-------|
| `v` (fiil) | 21.054 | %38.4 |
| `n?` (muhtemel isim) | 15.973 | %29.2 |
| `n` (isim) | 15.089 | %27.5 |
| `adj` (sıfat) | 1.998 | %3.6 |
| `np` (özel isim) | 548 | %1.0 |
| `unk` (bilinmeyen) | 33 | %0.1 |
| `adv` (zarf) | 33 | %0.1 |
| `num` (sayı) | 26 | %0.0 |
| `pro` (zamir) | 14 | %0.0 |

---

## 2. Lexicon Modülü — `turkmen-fst/turkmen_fst/lexicon.py`

### Mevcut Durum
- **Satır sayısı:** ~345
- **Temel fonksiyonlar:** Sözlük yükleme, kelime arama, morfolojik özellik hesaplama

### Yapılan Değişiklikler

#### 2.1 POS_TAG_MAP Güncellemesi
```python
# Eklenen satır:
"%<n?%>": "n?",
```
- `%<n?%>` etiketli kelimelerin dahili `"n?"` kodu ile tanınmasını sağlar

#### 2.2 POS_DISPLAY Güncellemesi
```python
# Eklenen satır:
"n?": "At? (Muhtemel isim)",
```
- API ve web arayüzünde kullanıcıya gösterilen POS açıklaması

#### 2.3 get_nouns() Güncellemesi
```python
# Eski:
if entry.pos == "n":
# Yeni:
if entry.pos in ("n", "n?"):
```
- `n?` etiketli kelimeler de isim paradigması üretimi ve analizinde kullanılıyor

#### 2.4 _compute_features() Güncellemesi
```python
# Eski:
if pos in ("n", "np"):
# Yeni:
if pos in ("n", "np", "n?"):
```
- `n?` etiketli kelimelerde ünsüz yumuşaması algılama aktif

#### 2.5 LexiconEntry Docstring Güncellemesi
- `pos` alanının alabileceği değerlere `"n?"` eklendi

---

## 3. Parser Modülü — `parser.py` (Ana dizin)

### Eski Durum
- **Yöntem:** Kalıp tabanlı (pattern-based), sözlüksüz
- **Satır sayısı:** 442
- **Sorunlar:**
  - Sözlük doğrulaması yok — her kelimeyi "başarılı" olarak çözüyor
  - Ünsüz yumuşaması sadece basit tablo ile yapılıyor
  - Ünlü düşmesi sadece 9 kelime için tanımlı
  - Fiil çekiminde sadece string matching kullanılıyor

### Yeni Durum
- **Yöntem:** Generator-doğrulamalı morfolojik analiz (sözlük destekli)
- **Satır sayısı:** ~250
- **Motor:** `turkmen-fst/turkmen_fst/analyzer.py` kullanıyor
- **Sözlük:** `turkmen-fst/data/turkmence_sozluk.txt` (54.783 kelime)

### Ana Fonksiyonlar

| Fonksiyon | Açıklama |
|-----------|----------|
| `parse_kelime(kelime)` | Tek sonuç döndüren ana çözümleme fonksiyonu |
| `parse_kelime_multi(kelime)` | Çoklu sonuç döndüren çözümleme (belirsiz kelimeler için) |
| `parse_isim(kelime)` | Sadece isim olarak çözümleme |
| `parse_fiil(kelime)` | Sadece fiil olarak çözümleme |

### Mimari

```
parser.py
  └── turkmen-fst/turkmen_fst/analyzer.py (MorphologicalAnalyzer)
        ├── turkmen-fst/turkmen_fst/lexicon.py (Lexicon — sözlük)
        ├── turkmen-fst/turkmen_fst/generator.py (NounGenerator + VerbGenerator)
        └── turkmen-fst/turkmen_fst/phonology.py (Fonoloji kuralları)
```

### Çıktı Formatı (template uyumlu)
```python
{
    "basarili": True,
    "orijinal": "kitabym",
    "kok": "Kitap",
    "ekler": [{"ek": "ym", "tip": "Degişlilik", "kod": "D₁b"}],
    "analiz": "Kitap (Kök) + ym (D₁b)",
    "tur": "isim",
    "anlam": ""  # eş sesli kelimeler için
}
```

---

## 4. Flask Web Uygulaması — `app.py`

### Yapılan Değişiklikler

#### 4.1 Import Güncellemesi
```python
# Eski:
from parser import parse_kelime
# Yeni:
from parser import parse_kelime, parse_kelime_multi
```

#### 4.2 Çoklu Sonuç Desteği
- `parse_results_all` değişkeni eklendi
- Parse işleminde `parse_kelime_multi()` kullanılıyor
- Birden fazla çözümleme varsa tümü template'e gönderiliyor

#### 4.3 Template'e Yeni Değişken
```python
parse_results_all=parse_results_all,  # Tüm çözümleme sonuçları
```

---

## 5. Web Template — `templates/index.html`

### Yapılan Değişiklikler

#### 5.1 Çoklu Çözümleme Gösterimi
- Birden fazla sonuç varsa "X olasy çözümleme tapyldy" mesajı gösteriliyor
- Her çözümleme "Çözümleme 1", "Çözümleme 2"... başlıklarıyla gösteriliyor
- Çözümlemeler arasında ayırıcı çizgi var

#### 5.2 POS Badge Güncellemesi
- İsim: "At (İsim)" — mavi badge
- Fiil: "Işlık (Fiil)" — yeşil badge
- Bilinmeyen: "Näbelli" — gri badge
- Türkmence terimler kullanılıyor

#### 5.3 Anlam Gösterimi
- Eş sesli kelimeler için anlam bilgisi (amber renkte) gösteriliyor

---

## 6. Analiz Betikleri (Tanılama / Geçici)

Bu betikler geliştirme sürecinde oluşturulmuştur ve temizlenebilir:

| Dosya | Amaç | Konum |
|-------|-------|-------|
| `analyze_derived.py` | Fiil türetim analizi (kök vs türetilmiş) | turkmen-fst/ |
| `analyze_derived2.py` | Derin fiil türetim analizi (kök grupları) | turkmen-fst/ |
| `analyze_nouns.py` | İsim türetim analizi | turkmen-fst/ |
| `analyze_tum.py` | tum.txt format analizi | turkmen-fst/ |
| `analyze_tum2.py` | tum.txt ithalat potansiyeli | turkmen-fst/ |
| `analyze_tum_classify.py` | tum.txt kelime sınıflandırma | turkmen-fst/ |
| `analyze_tum_final.py` | tum.txt nihai sınıflandırma | turkmen-fst/ |
| `import_tum.py` | tum.txt → sözlük ithalat betiği | turkmen-fst/ |

---

## 7. Değişmeyen Dosyalar

Aşağıdaki dosyalar bu oturumda **değiştirilmedi**:

| Dosya | Açıklama |
|-------|----------|
| `turkmen_fst/analyzer.py` | Analiz motoru — parser.py tarafından kullanılıyor |
| `turkmen_fst/generator.py` | Sentez motoru |
| `turkmen_fst/phonology.py` | Fonoloji kuralları |
| `turkmen_fst/morphotactics.py` | FST state machine |
| `turkmen_fst/api.py` | FastAPI REST API |
| `turkmen_fst/cli.py` | Komut satırı arayüzü |
| `morphology.py` | Ana dizindeki sentez motoru (web çekim için) |
| `tests/` | Tüm testler (105 test, hepsi geçiyor) |
| `turkmence_sozluk_tum.txt` | Kaynak sözlük dosyası (salt okunur kullanıldı) |

---

## 8. Test Sonuçları

### Birim Testleri (105/105 Başarılı)

| Test Dosyası | Test Sayısı | Durum |
|--------------|-------------|-------|
| `test_phonology.py` | 36 | ✅ Geçti |
| `test_morphotactics.py` | 33 | ✅ Geçti |
| `test_generator.py` | 18 (4.788 vaka) | ✅ Geçti |
| `test_analyzer.py` | 18 | ✅ Geçti |

---

## 9. Son Oturum Değişiklikleri (Şubat 2026)

### 9.1 Analyzer Hata Düzeltmeleri
- **Ek soyma limiti:** 8 → 13 karakter (`_generate_stem_candidates` fonksiyonunda)
- **Yuvarlaklaşma toleransı:** `_rounding_equivalent()` fonksiyonu eklendi
- **Eksik kelime:** `defter` sözlüğe eklendi (yumuşama özelliğiyle)

### 9.2 Spellcheck API
- **Dosya:** `turkmen_fst/api.py`
- **Yeni endpoint'ler:** `POST /spellcheck`, `POST /spellcheck/batch`
- **Yardımcı fonksiyonlar:** `tokenize()`, `_edit_distance()`, `_find_similar_roots()`, `generate_suggestions()`
- **Çalışma prensibi:** kelime → `analyzer.parse()` → unknown ise hatalı + öneri üret
- **Test:** `"mugalym"` → öneri: `["mugallym", "mugallyma"]`

### 9.3 Paradigma API + Web UI
- **API:** `POST /paradigm` endpoint'i — isim (48 form) ve fiil (84 form) paradigmaları
- **Web UI:** `templates/index.html`'e 4. "Paradigma" sekmesi eklendi (emerald tema)
  - İsim: 6 hal × 4 iyelik × tekil/çoğul tablo
  - Fiil: 7 zaman × 6 şahıs × olumlu/olumsuz tablo
- **Flask:** `app.py`'ye `_build_paradigma()` fonksiyonu ve route handler eklendi

### 9.4 Stemmer/Hunspell — Denendi ve Geri Alındı
- **Neden:** Sözlükte çekimlenmiş kelimeler (kök olmayan girişler) bulunduğu tespit edildi
- **Sorun:** Stemmer çekimli kökleri olduğu gibi kabul ediyor → yanlış sonuçlar
- **Karar:** Sözlük temizliği + fiil morfolojisi doğrulaması tamamlanmadan bu özelliklere geçilmemeli
- **Önkoşullar:** → `GELECEK_PLANLARI.md` §11.2'ye kayıt edildi

### 9.5 Sözlük Temizliği ve n? POS Sınıflandırma
- **Script:** `scripts/clean_and_classify.py` (dry-run + --apply modları)
- **Phase 1 — Çekimli form kaldırma:**
  - 49 çoğul form (-lar/-ler) kaldırıldı (generator doğrulamalı)
  - 25 `n` + 24 `n?` girişi (etnik isim çoğulları: türkmenler, fransuzlar vb.)
  - İyelik/hal formları: yanlış pozitif riski yüksek → yapılmadı
- **Phase 2 — n? POS sınıflandırma:**
  - Kaynak: tum.txt (110.588 kelime) + ek kalıbı + kök doğrulama
  - 5.334 giriş sınıflandırıldı → 4.244 → n, 1.090 → adj
  - 10.615 n? olarak kaldı (belirsiz: -jy/-ji partisipleri)
  - Güvenilirlik: 4.555 HIGH, 779 MEDIUM
- **Sözlük değişim:**
  - 54.795 → 54.746 kelime (-49 çoğul)
  - n: 15.090 → 19.309 (+4.219)
  - adj: 1.998 → 3.088 (+1.090)
  - n?: 15.973 → 10.615 (-5.358)
- **Test:** 105/105 hâlâ geçiyor

### Manuel Doğrulama

| Test | Sonuç |
|------|-------|
| `kitabym` → Kitap + ym (D₁b) | ✅ |
| `kitaby` → 2 çözümleme (A₄ ve D₃b) | ✅ |
| `geldim` → Gel + di (Ö1) + m (A1) | ✅ |
| `gelmedi` → Gel + me (Olumsuz) + di (Ö1) | ✅ |
| `başlarymyz` → Baş + lar (S2) + ymyz (D₁k) | ✅ |
| Web arayüzü çoklu sonuç gösterimi | ✅ |
| Web arayüzü POS badge'leri (At/Işlık) | ✅ |
