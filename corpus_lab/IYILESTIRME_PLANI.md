# Corpus Analiz Raporu & İyileştirme Planı

**Tarih:** 2026-03-02  
**Corpus:** metbugat.gov.tm — 1000 makale  
**Token:** 697.285 | **Type:** 30.684

---

## MEVCUT DURUM

| Metrik | Değer |
|--------|-------|
| Token Coverage | **73.28%** (510.965 / 697.285) |
| Type Coverage | **47.21%** (14.487 / 30.684) |
| Tanınmayan Token | 186.320 |
| Tanınmayan Type | 16.197 |
| POS: Noun | 12.327 type |
| POS: Verb | 2.160 type |

---

## TANINMAYAN KELİME KATEGORİLERİ

### 1. suffix_problem — Kök var ama ek çözümlenemedi (58.8%, ~109K token)

En büyük kategori. Sözlükte kök mevcut ama grammar engine eki ekleyemiyor.

**Alt-kategoriler:**

| Alt-problem | Örnek Kelimeler | Token Etkisi | Çözüm |
|-------------|----------------|-------------|-------|
| **Compound word + suffix** | `şäheriniň`, `prezidentiniň`, `ministrliginiň`, `bölüminiň` | ~5K+ | İyelik + iyelik zincirleme eki desteği |
| **Causative verb -dür/-dir** | `ösdürmek`, `gönükdirilen`, `ösdürmegiň` | ~3K+ | Causative (ettirgen) fiil morfolojisi |
| **-daky/-däki locative adj** | `bilelikdäki`, `çäklerinde` | ~2K+ | -dAky sıfat eki desteği |
| **-ly/-li/-lyk adjective** | `üstünlikli`, `halkara` | ~1K+ | -lI / -lIk sıfat yapımı |
| **Hyphenated compounds** | `hem-de`, `beýläk-de`, `has-da` | ~6K+ | Bileşik kelime (tire ile) desteği |
| **-mek/-mak infinitive verbs** | `ösdürmek`, `geçirmek` | ~2K+ | Fiil mastar formu (infinitive) |
| **Passive / reflexive verbs** | `gönükdirilen`, `alnyp` | ~2K+ | Edilgen fiil çekimi |
| **Proper nouns + suffix** | `berdimuhamedow`, `berdimuhamedowyň` | ~2K+ | Özel isim + ek morfolojisi |

### 2. short_word — Kısa kelime / ek parçacığı (21.3%, ~40K token)

Bunların çoğu tokenizasyon sorunları — tireli kelimelerden ayrılan ek parçaları:

| Kelime | × | Gerçek Kaynak |
|--------|---|---------------|
| `nji` | 3856 | `1-nji`, `2-nji` (sıra sayıları) |
| `la`, `le` | 3382 | `habar-la`, `ösüş-le` (instrumental eki -lA) |
| `ly`, `li` | 2168 | `üstünlik-li`, `many-ly` (-lI sıfat eki) |
| `ry`, `ri` | 2232 | Tireden sonra kalan ekin parçası |
| `ra`, `ta`, `na`, `ma`, `ka`, `bi`, `gi` vd. | ~8K | Tireli bileşik kelime parçaları |

**Asıl sorun:** Tokenizer tireli kelimeleri ayırıyor. `1-nji` → `nji`, `şol bir-de` → `de`

### 3. unknown_turkmen — Bilinmeyen Türkmence (10.1%, ~19K token)

Türkmen harfleriyle yazılmış ama kök veya ek bulunamayan:

| Kelime | × | Analiz |
|--------|---|--------|
| `ösüş` | 1023 | **Sözlükte yok** — çok sık isim, eklenmeli |
| `munuň` | 655 | `munuň` = bu'nun. `mun` sözlükte yok → zamirler desteği |
| `etmäge` | 416 | `et-` fiili + `-mäge` (directional infinitive) — yeni fiil formu |
| `öňünde` | 384 | `öň` + `ünde` (postposition) — postposition desteği |
| `oňyn` | 378 | `oňyn` = positive/olumlu — sözlükte yok |
| `edýän` | 368 | `et-` fiili + `-ýän` (present participle) — parser bunu bulmalı |
| `ösüşi`, `ösüşiň` | 684 | `ösüş` kökü eklendikten sonra çözülür |
| `ynanýaryn` | 302 | `ynan-` + `ýaryn` (present 1sg) — zaten olmalı? |

### 4. unknown_other — Yabancı / Özel (5.2%, ~10K token)

| Kelime | × | Tür |
|--------|---|-----|
| `alnyp` | 1152 | Turkmen: `al-` + passive `-yn` + converb `-yp` → fiil morfolojisi |
| `yglan` | 414 | Turkmen kelime — sözlükte yok |
| `innowasion` | 328 | Yabancı kökenli sıfat |
| `edip` | 309 | `et-` + `-ip` converb → fiil morfolojisi |
| `ugry` | 188 | `ugur` + iyelik → sözlükte var mı? |
| `eden` | 170 | `et-` + `-en` past participle → fiil morfolojisi |

### 5. missing_stem — Ek var, kök yok (4.0%, ~7.5K token)

| Kelime | × | Kök | Durum |
|--------|---|-----|-------|
| `mundan` | 1312 | `mun-` (zammi) | Zamir desteği gerekli |
| `bmg-niň` | 1002 | `BMG` (kısaltma) | Kısaltma + ek desteği |
| `ynanyşmak` | 972 | `ynan-` + `-yş` + `-mak` | Reciprocal fiil |
| `adyndaky` | 932 | `at` + `yndaky` | Zincirleme iyelik + -daky |
| `ýunesko-nyň` | 116 | `ÝUNESKO` (kısaltma) | Kısaltma + ek desteği |
| `abş-nyň` | 56 | `ABŞ` (kısaltma) | Kısaltma + ek desteği |

### 6. english_word + foreign_latin (0.7%, ~1.3K token)

İhmal edilebilir — `and`, `services`, `expo`, `visa` gibi yabancı kelimeler.

---

## İYİLEŞTİRME PLANI — ÖNCELİK SIRASI

### Faz 1: Quick Wins — Tokenizer + Sözlük (~5 saat)
**Beklenen etki: +5-8% coverage (73% → 78-81%)**

| # | İş | Etki (token) | Süre |
|---|-----|-------------|------|
| 1.1 | **Tireli kelime tokenizasyonu düzelt** | +40K | 2 saat |
|     | `1-nji` → tek token, `hem-de` → tek token |  |  |
| 1.2 | **Sık kullanılan eksik kökleri sözlüğe ekle** | +10K | 2 saat |
|     | `ösüş`, `oňyn`, `yglan`, `innowasion`, `munuň/mundan` (zamirler) |  |  |
| 1.3 | **Kısaltma + ek desteği** | +3K | 1 saat |
|     | `BMG-niň`, `ABŞ-nyň`, `ÝUNESKO-nyň` gibi tireli kısaltmalar |  |  |

### Faz 2: Grammar Engine Genişletme (~10-15 saat)
**Beklenen etki: +8-12% coverage (81% → 89-93%)**

| # | İş | Etki (token) | Süre |
|---|-----|-------------|------|
| 2.1 | **Causative verb -dIr/-dUr** | +5K | 3 saat |
|     | `ösdürmek`, `gönükdirmek`, `alyp barmak` |  |  |
| 2.2 | **Converb -Ip / -yp** | +5K | 2 saat |
|     | `edip`, `alyp`, `bolup`, `geçip` |  |  |
| 2.3 | **Participle -ýAn / -(y)An / -(y)en** | +4K | 2 saat |
|     | `edýän`, `eden`, `gönükdirilen` |  |  |
| 2.4 | **-dAky/-dÄki locative adjective** | +3K | 1 saat |
|     | `bilelikdäki`, `arasyndaky`, `adyndaky` |  |  |
| 2.5 | **-lI / -lIk adjective/noun formation** | +3K | 1 saat |
|     | `üstünlikli`, `halkara`, `netijeli` |  |  |
| 2.6 | **Infinitive -mAk / -mAge / -megIň** | +3K | 2 saat |
|     | `ösdürmek`, `etmäge`, `ösdürmegiň` |  |  |
| 2.7 | **Düzelt: Rounding bug (döwletüň)** | +2K | 2 saat |
|     | `has_rounded_vowel()` → son hece kontrolü |  |  |
| 2.8 | **Possessive chain İyelik-zincirleme** | +5K | 3 saat |
|     | `şäheriniň`, `prezidentiniň`, `ministrliginiň` |  |  |

### Faz 3: İleri Morfoloji (~10 saat)
**Beklenen etki: +3-5% coverage (93% → 96-98%)**

| # | İş | Etki (token) | Süre |
|---|-----|-------------|------|
| 3.1 | **Passive voice -Il** | +2K | 3 saat |
|     | `gönükdirilen`, tüm edilgen yapılar |  |  |
| 3.2 | **Reciprocal -Iş** | +1K | 2 saat |
|     | `ynanyşmak`, `görüşmek` |  |  |
| 3.3 | **Postpositions + suffixes** | +2K | 2 saat |
|     | `öňünde`, `üçin`, `bilen`, `barada` |  |  |
| 3.4 | **Compound verb support** | +2K | 3 saat |
|     | `alyp barmak`, `eýe bolmak`, `kabul etmek` |  |  |

---

## HEDEF TAKViMi

| Faz | Coverage | Token | Açıklama |
|-----|----------|-------|----------|
| Şimdi | **73.28%** | 510K/697K | Mevcut durum |
| Faz 1 sonrası | ~**80%** | 558K/697K | Tokenizer + sözlük |
| Faz 2 sonrası | ~**91%** | 634K/697K | Grammar engine |
| Faz 3 sonrası | ~**96%** | 669K/697K | İleri morfoloji |

---

## CORPUS İSTATİSTİKLERİ

```
Kaynak:       metbugat.gov.tm
Makale:       1000
Token:        697,285
Type:         30,684
Dosya:        corpus_lab/data/metbugat_corpus.txt (6.33 MB)
Çekim:        24 dakika, 0 hata
Analiz:       71 saniye
```

---

## DOSYA YAPISI

```
corpus_lab/
├── data/
│   ├── metbugat_corpus.txt          # 1000 makale ham metin (6.33 MB)
│   └── metbugat_corpus_meta.json    # Makale meta bilgileri
├── reports/
│   └── corpus_analysis_1000.json    # Detaylı analiz sonuçları
├── scripts/
│   ├── build_corpus.py              # Corpus scraper (resume destekli)
│   └── analyze_corpus.py            # Coverage analyzer + kategorileme
└── IYILESTIRME_PLANI.md             # Bu dosya
```

---

## ÖNCELİK → HEMEN BAŞLANACAKLAR

Faz 1 en büyük getiri/efor oranına sahip. Öneriler:

1. **Tokenizer'da tireli kelime desteği** (en büyük single fix — 40K token)
   - `1-nji` → `birinci` veya `1-nji` atomik token olarak tanı
   - `hem-de`, `has-da`, `beýläk-de` → sözlüğe bileşik kelime olarak ekle
   - Tireli kelimeleri bölmeden önce tam kelime olarak dene

2. **En sık 50 eksik kökü sözlüğe ekle**
   - `ösüş` (1023×), `oňyn` (378×), `yglan` (414×), `innowasion` (328×)
   - `mun-` (zamir kökü), `şu`, `ol` + ekleri

3. **Kısaltma desteği** 
   - `BMG-niň`, `ABŞ-nyň` → tire + ek ayrıştırma kuralı
