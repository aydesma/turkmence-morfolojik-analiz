# Corpus Lab — README
# Klasör Yapısı ve Amaç

Bu klasör, Türkmence metinlerden (corpus) morfolojik analiz sistemimizi
iyileştirmek için kullandığımız **veri odaklı keşif** (data-driven discovery)
sürecini barındırır.

## Klasör Yapısı

```
corpus_lab/
├── README.md                          ← Bu dosya
├── sozluk_degisiklik_log.txt          ← Sözlükte yapılan her değişikliğin kaydı
├── data/                              ← İndirilen ham corpus verileri
│   └── metbugat_50_articles.json      ← metbugat.gov.tm'den çekilen 50 makale
├── reports/                           ← Analiz raporları (JSON/TXT)
│   ├── softening_report.json          ← Yumuşama istisna keşif raporu
│   ├── corpus_coverage_results*.json  ← Corpus kapsamı test sonuçları
│   ├── vowel_drop_report.txt          ← Ünlü düşme analiz raporu
│   └── lexicon_validation_report.*    ← Sözlük doğrulama raporu
└── scripts/                           ← Keşif ve analiz scriptleri
    ├── discover_softening_exceptions.py  ← Yumuşama istisnası keşif aracı
    ├── corpus_coverage_test.py           ← Corpus kapsamı test aracı
    └── vowel_drop_analysis.py            ← Ünlü düşme analiz aracı
```

## Pipeline (İş Akışı)

```
1. Corpus Toplama
   metbugat.gov.tm → HTML çekme → metin çıkarma → tokenize

2. Keşif (Discovery)
   Her KPTÇ isim × çekim kombinasyonu → generator ile üret
   → yumuşamış/yumuşamamış formları karşılaştır
   → corpus'ta hangi form varsa ona göre sınıflandır

3. Doğrulama
   İstisna adayları → frekans analizi → elle doğrulama

4. Uygulama
   phonology.py → SOFTENING_EXCEPTIONS listesi güncelle
   turkmence_sozluk.txt → no_softening işareti ekle
   sozluk_degisiklik_log.txt → değişikliği kaydet

5. Test
   105 birim testi + 1192 round-trip → gerileme kontrolü
   corpus_coverage_test.py → etki ölçümü
```

## Kullanım

```bash
# Yeni istisna keşfi (daha fazla makale ile)
python corpus_lab/scripts/discover_softening_exceptions.py --articles 100

# Corpus kapsamı testi
python corpus_lab/scripts/corpus_coverage_test.py --source metbugat
```
