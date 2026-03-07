# 100K Türkmence Metin Corpus — Kaynak Araştırması

**Tarih:** 2026-03-01  
**Amaç:** Morfolojik analizörü test etmek için ~100.000 token'lık saf Türkmence metin corpusu oluşturmak  
**Mevcut Durum:** metbugat.gov.tm'den 50 makale = 33.153 token (%78.3 coverage)

---

## A. Devlet Haber Siteleri (Web Scraping)

### 1. metbugat.gov.tm ⭐ EN KOLAY
| Özellik | Değer |
|---------|-------|
| Tür | Devlet yayın hizmeti |
| Dil | %100 Türkmence |
| URL Pattern | `/newsDetails/{id}` |
| Makale Sayısı | ~3.929 makale |
| Token/Makale | ~660 token (ortalama) |
| Toplam Potansiyel | ~2.6M token |
| Scraper Durumu | **MEVCUT** — `corpus_coverage_test.py` çalışıyor |
| 100K İçin Gerekli | ~150 makale (50 zaten çekildi) |

**Avantaj:** Scraper hazır, en hızlı yol. 100 makale daha çekerek 100K'ya ulaşılabilir.  
**Dezavantaj:** Devlet haberleri → formel dil, sınırlı çeşitlilik.

---

### 2. turkmenistan.gov.tm/tk ⭐ EN BÜYÜK KAYNAK  
| Özellik | Değer |
|---------|-------|
| Tür | "Altyn Asyr" elektronik gazete |
| Dil | %100 Türkmence |
| URL Pattern | `/tk/habar/{id}/{slug}` |
| Makale Sayısı | ~103.790+ makale |
| Kategoriler | Wakalar, Resmi, Hyzmatdaşlyk, Ykdysadyýet, Jemgyýet, Medeniýet, Ylym, Sport, Kanunlar |
| Toplam Potansiyel | Milyonlarca token |
| Scraper Durumu | Yazılması gerekiyor |

**Avantaj:** Devasa arşiv, 9 farklı kategori, resmi dil.  
**Dezavantaj:** Yeni scraper yazmak gerekiyor. Rate limiting olabilir.

---

### 3. tdh.gov.tm/tk ⭐ EN KALİTELİ
| Özellik | Değer |
|---------|-------|
| Tür | Türkmenistan Döwlet Habarlar Agentligi (TDH) |
| Dil | %100 Türkmence |
| URL Pattern | `/tk/post/{id}/{slug}` |
| Makale Sayısı | ~47.876 post |
| Kategoriler | Syýasat, Ykdysadyýet, Jemgyýet, Medeniýet, Sport, Teswirlemeler |
| Arşiv | Var (`/tk/archive`) |
| Scraper Durumu | Yazılması gerekiyor |

**Avantaj:** Resmi haber ajansı, en formal ve doğru Türkmence.  
**Dezavantaj:** Yeni scraper gerekiyor.

---

### 4. turkmenportal.com/tm
| Özellik | Değer |
|---------|-------|
| Tür | Özel haber portalı |
| Dil | Türkmence (varsayılan Rusça, `/tm` prefixi gerekli) |
| Makale Sayısı | ~99.207 haber |
| Kategoriler | Siyaset, iş, spor, kültür, dünya |
| Scraper Durumu | Yazılması gerekiyor |

**Avantaj:** Yüksek hacim, çeşitli konular.  
**Dezavantaj:** Ana sayfa Rusça, Türkmence versiyon ayrı. Karışık dil riski.

---

## B. İndirilebilir Hazır Veri Setleri

### 5. Türkmen Wikipedia Dump
| Özellik | Değer |
|---------|-------|
| URL | `dumps.wikimedia.org/tkwiki/` |
| Son Dump | 2026-03-01 |
| Format | XML dump (standart MediaWiki) |
| Makale Sayısı | ~70.000 madde |
| Lisans | CC BY-SA |
| İndirme | Ücretsiz |

**Avantaj:** Hazır, indirilebilir, geniş konu çeşitliliği.  
**Dezavantaj:** Çok fazla yabancı kelime (özel isimler, bilimsel terimler). Önceki testte %67.15 coverage — metbugat'tan düşük.

---

### 6. HuggingFace Datasets (mamed0v)
| Dataset | Boyut | Açıklama |
|---------|-------|----------|
| `saillab/alpaca_turkmen_taco` | 62K satır | Alpaca format, instruction-tuning |
| `mamed0v/dolly-15k-turkmen` | 15K satır | Dolly 15K Türkmence çeviri |
| `mamed0v/TurkmenTrilingualSemi-SyntheticDictionaryDF` | 378.941 satır (189 MB) | Üç dilli sözlük, diyalog formatı |
| `mamed0v/TurkmenSpeech` | 9.55K indirme | Konuşma verisi |
| `EmreAkgul/turkmen-speech` | 120K indirme | Konuşma verisi |

**En kullanışlı:** `TurkmenTrilingualSemi-SyntheticDictionaryDF` — Türkmence cümleler içeriyor.  
**Avantaj:** Hazır, HuggingFace API ile indirilebilir, MIT lisanslı.  
**Dezavantaj:** Yapay üretilmiş cümleler, doğal dil değil. Morfolojik test için ideal değil.

---

## C. Diğer Potansiyel Kaynaklar

| Kaynak | URL | Tür |
|--------|-----|-----|
| Mejlis (Parlamento) | mejlis.gov.tm | Kanunlar, yasama metinleri |
| Medeniýet Ministrligi | medeniyet.gov.tm | Kültür haberleri |
| Bilim Ministrligi | education.gov.tm | Eğitim metinleri |
| Türkmen TV | turkmentv.gov.tm | TV haber metinleri |

---

## Strateji Önerileri

### Seçenek A — En Hızlı (1 saat)
metbugat.gov.tm scraper'ını genişlet:
- Mevcut: 50 makale = 33K token
- Ek 100 makale daha çek = +66K token
- **Toplam: ~100K token, tek kaynak**
- Scraper zaten hazır, sadece `--num-articles 150` parametresi

### Seçenek B — En İyi Çeşitlilik (3-4 saat)  
Üç kaynaktan karışık:
- metbugat.gov.tm: 50 makale (33K) ✓ mevcut
- tdh.gov.tm: 50 makale (~33K) — yeni scraper
- turkmenistan.gov.tm: 50 makale (~33K) — yeni scraper
- **Toplam: ~100K token, 3 farklı kaynak**
- Avantaj: Dil çeşitliliği, makale için daha iyi sonuç

### Seçenek C — Hazır Veri (30 dakika)
HuggingFace'den `TurkmenTrilingualSemi-SyntheticDictionary` indir:
- 378K satır, bol miktarda Türkmence cümle
- Sentetik veri → doğal dil testi için uygun değil
- **Tavsiye edilmez** — morfolojik analiz testi için doğal metin gerekli

### ⭐ Tavsiye: Seçenek A + tdh.gov.tm
1. metbugat.gov.tm'den 100 makale daha (mevcut scraper) → 100K
2. Sonra tdh.gov.tm scraper'ı yazıp 50 makale daha → 130K
3. Makale için çeşitli kaynak raporu + yüksek token sayısı

---

## Token Hesabı

| Kaynak | Makale | Token (tahmini) | Durum |
|--------|--------|-----------------|-------|
| metbugat.gov.tm (mevcut) | 50 | 33.153 | ✅ Çekildi |
| metbugat.gov.tm (ek) | 100 | ~66.000 | ⏳ Çekilecek |
| tdh.gov.tm | 50 | ~33.000 | ⏳ Scraper yazılacak |
| **TOPLAM** | **200** | **~132.000** | |

---

## Scraper Mimarisi (Planlanan)

```
corpus_lab/
├── scripts/
│   ├── corpus_coverage_test.py    # metbugat scraper (mevcut)
│   ├── scrape_tdh.py              # TDH scraper (yazılacak)
│   └── scrape_altynasyr.py        # Altyn Asyr scraper (yazılacak)
├── data/
│   ├── metbugat_corpus.txt        # metbugat verileri
│   ├── tdh_corpus.txt             # TDH verileri
│   └── combined_corpus.txt        # Birleştirilmiş corpus
└── reports/
    └── corpus_coverage_results.json
```

---

## Lisans & Etik Notlar

- Devlet siteleri: Kamu yararına yayın, akademik kullanım genellikle serbest
- Wikipedia: CC BY-SA lisansı
- HuggingFace: MIT lisansı (mamed0v datasets)
- Tüm kaynaklar için kaynak gösterimi yapılmalı
- Rate limiting'e saygı gösterilmeli (1-2 saniye bekleme arası)
- Makalede veri kaynağı olarak belirtilecek
