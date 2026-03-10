# Makale Güncellemesi İçin Kullanılabilecek Bilgiler — v2

> **Tarih:** 10 Mart 2026  
> **Proje:** TurkmenFST — Türkmence Morfolojik Analiz Sistemi  
> **Repo:** `github.com/aydesma/turkmence-morfolojik-analiz`  
> **Son commit:** `bc1baf8`  

Bu dosya, IEEE TurkLang makalesi (v2) güncellemesi için projenin **tüm geliştirme sürecini**, yapılan değişiklikleri, kullanılan kaynakları, test sonuçlarını, sözlük sağlık raporunu ve gelecek planlarını kapsamlı şekilde belgelemektedir.

---

## İÇİNDEKİLER

1. [Kapsam Gelişim Tarihçesi](#1-kapsam-gelişim-tarihçesi)
2. [Sözlük (Lexicon) Durumu ve Sağlık Raporu](#2-sözlük-lexicon-durumu-ve-sağlık-raporu)
3. [Motor (Engine) Geliştirmeleri](#3-motor-engine-geliştirmeleri)
4. [Bug Düzeltmeleri — Detaylı](#4-bug-düzeltmeleri--detaylı)
5. [Corpus Lab Pipeline](#5-corpus-lab-pipeline)
6. [Kayıp Analizi — Puan Nerede Gidiyor?](#6-kayıp-analizi--puan-nerede-gidiyor)
7. [Yapılan Tüm Değişiklikler — Kronolojik](#7-yapılan-tüm-değişiklikler--kronolojik)
8. [Test Sonuçları ve Doğrulama](#8-test-sonuçları-ve-doğrulama)
9. [Kullanılan Kaynaklar](#9-kullanılan-kaynaklar)
10. [Gelecek Planları ve Yol Haritası](#10-gelecek-planları-ve-yol-haritası)
11. [Makalede Güncellenecek Bölümler](#11-makalede-güncellenecek-bölümler)
12. [Referans Dosya Haritası](#12-referans-dosya-haritası)

---

## 1. Kapsam Gelişim Tarihçesi

### 1.1 Token Kapsam Yolculuğu

```
%73.28 ──→ %78.3 ──→ %81.45 ──→ %92.59 ──→ %95.99 ──→ %96.37
  │          │          │           │           │          │
  │          │          │           │           │          └─ Faz 3b: Bug fix + 58 giriş
  │          │          │           │           └─ Faz 3a: Özel isimler, fiil formları
  │          │          │           └─ Faz 2: enedilim entegrasyonu + büyük temizlik
  │          │          └─ Faz 1: Hunspell/PDF/tum.txt ithalatı
  │          └─ Softening istisna keşfi (data-driven pipeline)
  └─ İlk corpus testi (Wiktionary çekirdek sözlük)
```

### 1.2 Verilerle Özet

| Faz | Tarih | Token Kapsam | Type Kapsam | Sözlük Giriş | Açıklama |
|-----|-------|-------------|-------------|---------------|----------|
| Başlangıç | Şubat 2026 | %73.28 | ~%55 | ~1,736 | Wiktionary çekirdeği |
| Softening | Şubat 2026 | %78.30 | — | ~32,015 | 58 softening istisnası keşfi |
| Motor v1 | Şubat 2026 | %81.45 | — | ~32,015 | Tüm kaynaklar ithal, büyük temizlik |
| Motor v2 | Şubat 2026 | %92.59 | — | ~32,015 | 18 zaman/kip, participle, converb |
| Faz 3a | Mart 2026 | %95.99 | %70.12 | ~32,682 | Özel isimler, verbal noun+poss+case |
| **Faz 3b** | **Mart 2026** | **%96.37** | **%70.84** | **32,738** | **Bug fix + 58 yeni giriş** |

### 1.3 Toplam İyileşme

- **Token kapsam:** %73.28 → %96.37 = **+23.09 puan**
- **Sözlük büyümesi:** 1,736 → 32,738 = **+31,002 giriş** (×18.9 büyüme)
- **Tanınan token:** ~24,300 → 634,950 (658,881 toplam corpus)

---

## 2. Sözlük (Lexicon) Durumu ve Sağlık Raporu

### 2.1 Genel İstatistikler (Güncel — 10 Mart 2026)

| Metrik | Değer |
|--------|-------|
| **Toplam giriş** | **32,738** |
| **Benzersiz kelime** | **30,753** |
| Eş sesli kelime (homonym) | 1,954 (çoklu giriş) |
| Dosya | `turkmen-fst/data/turkmence_sozluk.txt` |
| Format | `kelime<TAB>%<POS%>[<TAB>özellikler]` |

### 2.2 POS (Sözcük Türü) Dağılımı

| POS Etiketi | Tür | Sayı | Yüzde |
|------------|-----|------|-------|
| `%<n%>` | İsim | 21,929 | %66.97 |
| `%<v%>` | Fiil | 6,494 | %19.83 |
| `%<adj%>` | Sıfat | 3,152 | %9.63 |
| `%<np%>` | Özel isim | 1,036 | %3.16 |
| `%<adv%>` | Zarf | 56 | %0.17 |
| `%<num%>` | Sayı | 26 | %0.08 |
| `%<pro%>` | Zamir | 14 | %0.04 |
| `%<postp%>` | Edat | 7 | %0.02 |
| `%<suf%>` | Sonek | 5 | %0.02 |
| `%<interj%>` | Ünlem | 5 | %0.02 |
| `%<conj%>` | Bağlaç | 5 | %0.02 |
| `%<det%>` | Belirteç | 4 | %0.01 |
| `%<unk%>` | Bilinmeyen | 2 | %0.01 |
| `%<phr%>` | Öbek | 2 | %0.01 |
| `%<prep%>` | Öntakı | 1 | <0.01 |
| **Toplam** | | **32,738** | **%100** |

### 2.3 Morfofonemik Özellikler

| Özellik | Açıklama | Sayı |
|---------|----------|------|
| `softening` | k/p/t/ç → g/b/d/j yumuşama | 8,192 |
| `no_softening` | Yumuşama istisnası (alıntı kelime) | 251 |
| `vowel_drop` | Ünlü düşmesi (burun→burn-) | 22 |
| `exception_drop` | İstisnai ünlü düşmesi (asyl→asl) | 7 |
| `homonym` | Eş sesli kelime bilgisi | 8 |
| `rounding` | Yuvarlaklaşma (guzy→guzu) | 3 |

### 2.4 Sözlük Sağlık Kontrolü

#### POS Etiketleri Doğru mu?
- **EVET** — enedilim.com'dan POS verisi dönen 58 kelimenin tamamı sözlükte doğru etiketli
- **Sıfır mismatch**: adj/n/adv sınıflandırmasında hata yok
- Fiil kökleri %100 enedilim.com kaynaklı (en güvenilir kaynak)
- İsim/sıfat ayrımı Wiktionary + Hunspell çapraz referansıyla doğrulanmış

#### Kelimeler Gerçekten Kök mü?
- **EVET** — Çekimlenmiş form yok (Aşama 8'de 15,663 çekimli form silindi)
- 4,109 türetilmiş form var ama bunlar **bağımsız sözcüklerdir** (enedilim.com'da bağımsız headword)
- `n?` belirsiz etiket kalmamış (tamamı Aşama 7-8'de ya sınıflandırıldı ya silindi)

#### Softening Etiketleri Doğru mu?
- Data-driven keşif pipeline'ı ile 58 istisna ilk kez keşfedildi
- Corpus doğrulamasıyla 24 ek istisna eklendi (Faz 3b)
- Toplam 251 no_softening kaydı mevcut
- Yanlış softening riski düşük (corpus'ta test edilmiş)

#### Kaynak Güvenilirliği
| Kaynak | Güvenilirlik | Nihai Katkı |
|--------|-------------|-------------|
| enedilim.com (resmi) | ★★★★★ | 8,802 giriş (%26.9) |
| Wiktionary | ★★★★☆ | 1,649 giriş (%5.0) |
| Hunspell tk_TM | ★★★☆☆ | 16,238 giriş (%49.6) |
| tum.txt orfoepik | ★★★☆☆ | 5,362 giriş (%16.4) |
| PDF OCR | ★★☆☆☆ | ~0 (dolaylı katkı) |
| Corpus keşfi | ★★★★☆ | ~700+ giriş (Faz 3a+3b) |

---

## 3. Motor (Engine) Geliştirmeleri

### 3.1 İsim Çekim Motoru (NounGenerator)
- 6 hal eki (yalın, ilgi, yönelme, belirtme, bulunma, çıkma)
- 3 iyelik düzeyi (A1-A3 tekil) + çoğul (B1-B3→A1-A2+lar)
- Ünsüz yumuşaması (data-driven softening/no_softening)
- Ünlü düşmesi (20 kelime + 5 istisna)
- Yuvarlaklaşma (3 kelime)
- Eş sesli kelime desteği (homonym etiketi)

### 3.2 Fiil Çekim Motoru (VerbGenerator)
18 zaman/kip/form kodu destekleniyor:

| Kod | Zaman/Kip | Olumsuzluk Tipi |
|-----|-----------|-----------------|
| Ö1 | Anyk Öten (kesin geçmiş) | Sentetik (-mA) |
| Ö2 | Daş Öten (uzak geçmiş) | Kaynaşık (fused) |
| Ö3 | Dowamly Öten (sürekli geçmiş) | Analitik (däl) |
| H1 | Umumy Häzirki (geniş zaman) | Sentetik (-mA) |
| H2 | Anyk Häzirki (şimdiki zaman) | Analitik (**yok**) |
| G1 | Mälim Geljek (kesin gelecek) | Analitik (däl) |
| G2 | Nämälim Geljek (belirsiz gelecek) | Kaynaşık (fused) |
| Ş1 | Şert (şart kipi) | Sentetik (-mA) |
| B1K | Buýruk (emir kipi) | Özel kalıplar |
| HK | Hökmanlyk (gereklilik) | Analitik (däl) |
| NÖ | Nätanyş Öten (rivayet) | Kaynaşık (fused+copula) |
| AÖ | Arzuw-Ökünç (dilek-pişmanlık) | Sentetik |
| FH | Hal işlik (converb/ulaç) | -man/-män |
| FÖ | Öten ortak (past participle) | -madyk/-medik |
| FÄ | Häzirki ortak (present participle) | -maýan/-meýän |
| FG | Geljek ortak (future participle) | -majak/-mejek |
| ETT | Ettirgen (causative) | — |
| EDL | Edilgen (passive) | — |

### 3.3 Morfolojik Analiz (Analyzer)
- İsim ayrıştırma: çekimli kelime → kök + ekler
- Fiil ayrıştırma: çekimli kelime → kök + zaman + şahıs
- Cümle düzeyinde analiz (çoklu kelime)
- Sözlük destekli kök doğrulama
- Çapraz tekilleştirme (aynı kelime hem isim hem fiil parslandığında)
- `breakdown_key` ile aynı çözümlemenin farklı sonuçlarının tekilleştirilmesi
- Copula katmanı (-dyr/-dir soyma + altını analiz etme)
- Türetme eki desteği: `-çIlIk`, `-Iş` (yeni eklendi Faz 3b)
- Verbal noun + possessive + case pattern desteği (yeni eklendi Faz 3a)
- Predikative `-dIgI` parser (yeni eklendi Faz 3a)

### 3.4 Web Arayüzü
- 4 sekmeli arayüz: İsim, Fiil, Derňew (Analiz), Paradigma
- Paradigma otomatik tür tespiti (sözlükten isim/fiil belirleme)
- Eş sesli kelimeler için çift paradigma
- "Tablony kopyala" butonu
- Responsive tasarım
- 18 zaman/kip dropdown'ları 4 optgroup ile

### 3.5 REST API
7 endpoint:
- `GET /api/health` — sağlık kontrolü
- `POST /api/generate/noun` — isim çekimi
- `POST /api/generate/verb` — fiil çekimi
- `POST /api/analyze` — morfolojik analiz
- `GET /api/lexicon/<word>` — sözlük sorgusu
- `POST /api/spellcheck` — yazım denetimi + öneri
- `POST /api/paradigm` — paradigma tablosu

---

## 4. Bug Düzeltmeleri — Detaylı

### Faz 3b (Mart 2026) — En Son Oturum

#### 4.1 G2 (Nämälim Geljek) e→ä Kuralı HATALI İDİ → DÜZELTİLDİ ✅
- **Sorun:** `gel + er → gäler` üretiyordu, doğrusu `geler`
- **Kök neden:** Tense 7 ve `_compound_base(sub="genis")`'te e→ä dönüşümü yanlışlıkla uygulanıyordu
- **Düzeltme:** 4 lokasyondan e→ä satırları kaldırıldı (generator.py + morphology.py)
- **Etki:** Tüm G2 çekimleri düzeldi

#### 4.2 H2 (Anyk Häzirki) "yok" Olumsuzluk EKSİKTİ → EKLENDİ ✅
- **Sorun:** H2 olumsuzluk hiç desteklenmiyordu
- **Kural:** TABLE VIII'e göre H2 "yok" ile analitik olumsuzluk yapıyor
- **Düzeltme:** Tense 5'e olumsuz mod eklendi: `result + " yok"`
- **Etki:** `oturýaryn yok`, `durýaryn yok` gibi formlar artık üretiliyor

#### 4.3 Web morphology.py Senkronizasyon Eksiklikleri → DÜZELTİLDİ ✅
- **Sorun:** Converb (tense 13) ve past participle (tense 14) için `_fiil_yumusama()` ve e→ä uygulanmıyordu
- **Düzeltme:** morphology.py'de converb ve participle bölümlerine fiil yumuşaması + e→ä eklendi

#### 4.4 Accusative (A4) e→ä Dönüşümü EKSİKTİ → EKLENDİ ✅
- **Sorun:** `wezipe → wezipeni` üretiyordu, doğrusu `wezipäni`
- **Kural:** Belirtme hali ekinde (-nI) son ünlü `e` ise `ä`'ye dönüşür
- **Düzeltme:** generator.py ve morphology.py'de A4 case'ine e→ä eklendi
- **Etki:** `wezipäni`, `tejribäni` gibi formlar artık doğru

#### 4.5 Past Participle (t14) e→ä Dönüşümü EKSİKTİ → EKLENDİ ✅
- **Sorun:** Geçmiş zaman sıfat-fiilinde e→ä uygulanmıyordu
- **Düzeltme:** Tense 14'e e→ä eklendi
- **Etki:** `dörän`, `gülän` gibi formlar artık doğru üretiliyor

#### 4.6 Softening İstisnaları (24 kelime) → EKLENDİ ✅
- **Sorun:** wekiliýet, häkimiýet, sammit, ast, port, durk, surat, adalat, amanat gibi kelimeler yanlış yumuşatılıyordu
- **Düzeltme:** phonology.py'de SOFTENING_EXCEPTIONS'a 24 yeni kelime eklendi
- morphology.py'de YUMUSAMA_ISTISNALARI'na aynı 24 kelime eklendi

### Önceki Fazlarda Düzeltilen Buglar

| Tarih | Hata | Düzeltme | Commit |
|-------|------|----------|--------|
| Şubat 2026 | `ýygnajak` duplikasyon | Fiil üretiminde tekilleştirme | `cbb063a` |
| Şubat 2026 | B1/B2 iyelik yanlış çekim | B1/B2 → A1/A2 + çoğul dönüşümü | `407198c` |
| Şubat 2026 | Eş sesli kelime çapraz duplikasyon | analyzer.py cross-dedup | `407198c` |
| Şubat 2026 | Tek harfli köklerden yanlış parse | 36 tek harfli kök silindi | `5cc3575` |
| Şubat 2026 | poss_type API None override | `data.get("poss_type", "tek")` | — |
| Şubat 2026 | paradigm endpoint hata | `not result` + auto default | — |
| Şubat 2026 | H1 kişi ekleri `-ym/-ik` → `-yn/-is` | genişletilmiş paradigma | `fe28801` |
| Şubat 2026 | G2 olumsuz çift olumsuzluk | düzeltildi | `fe28801` |
| Şubat 2026 | Ö1 dodak yuvarlaklaşması | tek hece+dodak → `-du/-dü` | `fe28801` |
| Şubat 2026 | Ö2 olumsuz kalıp | `-me+ipdi` → `-män+di` | `fe28801` |
| Şubat 2026 | Ö3 olumsuz kalıp | `-me+ýärdi` → `-ýän däldi` analitik | `fe28801` |
| Şubat 2026 | G1 olumlu kopula | `-jekdirin/-jakdyryn` eklendi | `fe28801` |

### Bilinen Ama Düzeltilmemiş Sorun
- **Yuvarlaklaşma uyumu hatası:** `döwlet → döwletüň` (yanlış), doğrusu `döwletiň`. `has_rounded_vowel()` fonksiyonu kökün herhangi bir yerindeki yuvarlak ünlüye bakıyor, son heceye bakmalı. Düzeltme gelecek faz için planlandı.

---

## 5. Corpus Lab Pipeline

### 5.1 Genel Bakış

`corpus_lab/` klasörü, morfolojik analiz motorunun gerçek metin üzerindeki performansını ölçmek ve iyileştirmek için geliştirilmiş bir veri bilimi pipeline'ıdır.

### 5.2 Pipeline Adımları

```
┌─────────────────────────────────────────────────────┐
│           CORPUS LAB PİPELİNE                       │
├─────────────────────────────────────────────────────┤
│                                                     │
│  1. CORPUS TOPLAMA                                  │
│     └─ build_corpus.py                              │
│        ├─ metbugat.gov.tm'den haber makaleleri      │
│        ├─ HTML temizleme + Türkmence metin çıkarma  │
│        └─ metbugat_corpus.txt (düz metin)           │
│                                                     │
│  2. TOKENİZASYON + ANALİZ                           │
│     └─ analyze_corpus.py                            │
│        ├─ Metin → kelime tokenları                  │
│        ├─ Her token → analyzer.parse()              │
│        ├─ Tanınan / tanınmayan sınıflandırma        │
│        └─ corpus_analysis_*.json (frekans verileri) │
│                                                     │
│  3. KAPSAM TESTİ                                    │
│     └─ run_local_coverage.py                        │
│        ├─ Token kapsam: tanınan/toplam              │
│        ├─ Type kapsam: benzersiz tanınan/toplam     │
│        ├─ Hata kategorileme (10 kategori)           │
│        └─ corpus_coverage_local.json (sonuçlar)     │
│                                                     │
│  4. İSTİSNA KEŞFİ (Data-Driven)                     │
│     └─ discover_softening_exceptions.py              │
│        ├─ k/p/t/ç-biten her isim için               │
│        ├─ Yumuşamış + yumuşamamış form üret          │
│        ├─ Corpus'ta hangisi var → karar              │
│        └─ softening_report.json (58 istisna)         │
│                                                     │
│  5. SÖZLÜK DOĞRULAMA                                │
│     └─ validate_lexicon.py                           │
│        ├─ POS dağılımı kontrolü                     │
│        ├─ Çekimli form tespiti                      │
│        ├─ Softening tutarlılık kontrolü             │
│        └─ lexicon_validation_report.json             │
│                                                     │
│  6. GAP ANALİZİ                                     │
│     └─ Tanınmayan tokenlerin kategorilenmesi         │
│        ├─ diger (İngilizce + karmaşık morfoloji)     │
│        ├─ fiil_cekimi (eksik fiil formları)          │
│        ├─ cok_ekli_isim (çok ekli formlar)           │
│        ├─ yabanci (yabancı kelimeler)                │
│        ├─ yapim_ekli (türetme eki sorunları)         │
│        ├─ ettirgen_edilgen (çatı sorunları)           │
│        └─ diğer alt kategoriler                      │
│                                                     │
│  7. İYİLEŞTİRME DÖNGÜSÜ                            │
│     └─ Sonuçlara göre:                              │
│        ├─ Sözlüğe yeni kelime ekleme                │
│        ├─ Motor kurallarını düzeltme                 │
│        ├─ İstisna listesi genişletme                 │
│        └─ Tekrar test → kapsam artışı ölçme          │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### 5.3 Corpus İstatistikleri

| Metrik | Değer |
|--------|-------|
| Kaynak | metbugat.gov.tm (Türkmenistan resmi haber ajansı) |
| Makale sayısı | ~500+ haber makalesi |
| Toplam token | 658,881 |
| Benzersiz type | 29,187 |
| Dil | Türkmence (Latin alfabe) |
| Format | Düz metin, satır bazlı |
| Meta veri | `metbugat_corpus_meta.json` (URL, tarih, başlık) |

### 5.4 Kapsam Testi Çalıştırma

```bash
# Lokal kapsam testi
cd turkmence-guncelleme
python corpus_lab/scripts/run_local_coverage.py
# → corpus_lab/reports/corpus_coverage_local.json
```

### 5.5 Softening İstisna Keşif Pipeline'ı (Makaleye Önemli)

Bu pipeline makalede **Section 4.2** olarak yeni bir alt bölüm olabilir:

> **Data-Driven Exception Discovery.**  
> We implemented an automated pipeline for discovering morphophonemic exceptions from raw text corpora. The pipeline:  
> (1) fetches Turkmen news articles from metbugat.gov.tm,  
> (2) tokenizes them into word forms,  
> (3) for each K/P/T/Ç-ending noun in the lexicon, generates both softened and unsoftened inflected forms using the morphological generator,  
> (4) checks which form(s) appear in the corpus,  
> (5) classifies stems as confirmed-softening, exception (no-softening), ambiguous, or no-evidence.

---

## 6. Kayıp Analizi — Puan Nerede Gidiyor?

### 6.1 Genel Durum
- **Tanınan token:** 634,950 / 658,881 = **%96.37**
- **Tanınmayan token:** 23,931 (%3.63)
- **Tanınan type:** 20,676 / 29,187 = **%70.84**
- **Tanınmayan type:** 8,511 (%29.16)

### 6.2 Hata Kategorileri (10 Kategori)

| # | Kategori | Type Sayısı | Token Sayısı | % (kayıp payı) | Açıklama |
|---|----------|------------|-------------|-----------------|----------|
| 1 | **diger** | 7,230 | 20,059 | **83.8%** | İngilizce kelimeler + karmaşık Türkmen morfolojisi |
| 2 | fiil_cekimi | 435 | 1,179 | 4.9% | Birleşik fiiller, eksik çekim kalıpları |
| 3 | cok_ekli_isim | 315 | 819 | 3.4% | 4+ ekli formlar (gazananlaryny) |
| 4 | yabanci | 67 | 727 | 3.0% | İngilizce/Rusça kelimeler |
| 5 | yapim_ekli | 203 | 513 | 2.1% | -lyk/-çylyk bileşik türetmeler |
| 6 | ettirgen_edilgen | 213 | 502 | 2.1% | Causative/passive çekim eksikleri |
| 7 | fiilimsi_zarf | 34 | 68 | 0.3% | Converb+case/poss formları |
| 8 | ozel_isim | 9 | 56 | 0.2% | Çok ekli özel isimler |
| 9 | tireli_bilesik | 4 | 7 | <0.1% | Tireli bileşik kelimeler |
| 10 | sira_sayi | 1 | 1 | <0.1% | Sıra sayıları |

### 6.3 En Sık Tanınmayan Kelimeler

| Kelime | Token | Kategori | Analiz |
|--------|-------|----------|--------|
| `and` | 502 | yabanci | İngilizce bağlaç — filtrelenebilir |
| `services` | 501 | yabanci | İngilizce — filtrelenebilir |
| `other` | 501 | yabanci | İngilizce — filtrelenebilir |
| `şatdyryn` | 100 | fiil_cekimi | şat+dyr+yn → compound verb |
| `belleýşi` | 63 | yapim_ekli | bellemek + -ýş + iyelik |
| `allatagaladan` | 60 | diger | allatagala + ablative |
| `nýu` | 52 | yabanci | "New" (New York) |
| `wekiliýetiniň` | 88 | diger | wekiliýet + poss + gen (düzeltildi) |
| `sammite` | 47 | diger | sammit + dative (düzeltildi) |
| `ýork` | 35 | yabanci | "York" — özel isim |
| `taýýardyrys` | 34 | fiil_cekimi | taýýar + dyr + ys → compound |
| `ltd` | 32 | yabanci | Kısaltma |
| `nygtaýşy` | 31 | yapim_ekli | nygtamak + -ýş + iyelik |
| `ynanmagyňyzy` | 31 | cok_ekli_isim | ynanmak + gerund + poss + acc |

### 6.4 İyileştirme Potansiyeli

| Aksiyon | Tahmini Token Kazancı | Zorluk |
|---------|----------------------|--------|
| İngilizce kelime filtresi | ~1,500+ token | Kolay |
| Ettirgen/edilgen fiil çekimi | ~500 token | Orta |
| Çok ekli isim pattern | ~800 token | Zor |
| -ýş verbal noun + poss | ~300 token | Orta |
| Birleşik fiil (compound verb) | ~400 token | Zor |
| Daha fazla sözlük girişi | ~2,000 token | Orta |
| **Toplam potansiyel** | **~5,500 token** | |
| **Potansiyel kapsam** | **~%97.2** | |

---

## 7. Yapılan Tüm Değişiklikler — Kronolojik

### Faz 1: Temel İnşa (Şubat 2026 başı)

1. **Wiktionary çekirdeği oluşturuldu** — `scrape_wiktionary.py` ile 1,736 lemma çekildi
2. **Morfolojik özellikler eklendi** — `enrich_dictionary.py` ile softening, vowel_drop etiketleri
3. **Hunspell ithalatı** — `import_hunspell.py` ile 16,238 giriş (114 bayrak grubu analizi)
4. **PDF OCR sözlük** — `extract_pdf_dictionary.py` ile 5,267 kelime (çoğu sonra elendi)
5. **tum.txt ithalatı** — `import_tum.py` ile 5,362 isim
6. **enedilim.com entegrasyonu** — 6,471 fiil kökü + 2,471 eksik isim eklendi
7. **Büyük temizlik** — 54,795 → 32,015 (n? silme, çekimli form silme)
8. **Tek harfli kök temizliği** — 36 giriş silindi → 32,015

### Faz 2: Motor Geliştirme (Şubat 2026 ortası–sonu)

9. **İsim çekim motoru tamamlandı** — 6 hal, 3 iyelik, softening, vowel_drop
10. **Fiil çekim motoru tamamlandı** — 7 temel zaman (Ö1-G2)
11. **8 fiil çekim düzeltmesi** — enedilim.com referansıyla (commit `fe28801`)
12. **5 yeni kip/form eklendi** — Ş1, B1K, HK, NÖ, AÖ
13. **4 fiilimsi formu eklendi** — FH, FÖ, FÄ, FG (converb + 3 participle)
14. **2 işlik derejesi eklendi** — ETT (causative), EDL (passive)
15. **Analyzer tamamlandı** — isim/fiil ayrıştırma, copula soyma, cross-dedup
16. **Web arayüzü oluşturuldu** — 4 sekmeli, paradigma, kopyalama
17. **REST API tamamlandı** — 7 endpoint
18. **124 yeni test yazıldı** — `test_new_verb_forms.py`, tümü başarılı

### Faz 3a: Corpus-Driven İyileştirme (Mart 2026 başı)

19. **Corpus lab pipeline kuruldu** — metbugat.gov.tm'den 658K token corpus
20. **Softening istisna keşfi** — data-driven pipeline ile 58 istisna bulundu
21. **Coverage %81.45 → %92.59** — Motor iyileştirmeleri
22. **Coverage %92.59 → %95.99** — Özel isim ekleme, verbal noun+poss+case pattern
23. **Sözlüğe ~680 yeni giriş eklendi** — Özel isimler, eksik kelimeler
24. **Predikative -dIgI parser eklendi**

### Faz 3b: Bug Fix + Polish (Mart 2026 — Bu Oturum)

25. **G2 e→ä kuralı düzeltildi** — 4 lokasyondan kaldırıldı
26. **H2 "yok" olumsuzluk eklendi** — generator.py + morphology.py
27. **Web morphology.py senkronize edildi** — converb/participle fiil yumuşaması
28. **A4 accusative e→ä eklendi** — wezipäni, tejribäni düzeldi
29. **Past participle e→ä eklendi** — dörän, gülän düzeldi
30. **24 softening istisnası eklendi** — wekiliýet, häkimiýet, sammit, ast, port vb.
31. **58 yeni sözlük girişi eklendi** — Çeşitli isim, fiil, sıfat, özel isim
32. **-çIlIk ve -Iş türetme eki desteği eklendi** — analyzer.py
33. **POS etiketi düzeltmesi** — `%<post%>` → `%<postp%>` (garamazdan, astynda)
34. **Coverage %95.99 → %96.37** — Tüm düzeltmelerin toplu etkisi

---

## 8. Test Sonuçları ve Doğrulama

### 8.1 Birim Test Sonuçları

| Test Seti | Sayı | Başarı | Durum |
|-----------|------|--------|-------|
| pytest (turkmen-fst/tests/) | 105 | %100 | ✅ |
| Yeni fiil formları | 124 | %100 | ✅ |
| Kapsamlı round-trip | 1,192 | %100 | ✅ |
| v26 referans eşleşme | 4,788 | %100 | ✅ |
| API endpoint testleri | 18 | %100 | ✅ |
| **Toplam** | **6,227** | **%100** | **✅** |

### 8.2 Corpus Kapsam Sonuçları

| Test | Token Kapsam | Type Kapsam | Corpus Boyutu |
|------|-------------|-------------|---------------|
| İlk test (Şubat) | %73.28 | — | ~10K token |
| Softening sonrası | %78.30 | — | 33K token |
| Motor v2 sonrası | %92.59 | — | 658K token |
| Faz 3a sonrası | %95.99 | %70.12 | 658K token |
| **Faz 3b sonrası** | **%96.37** | **%70.84** | **658K token** |

### 8.3 enedilim.com Doğrulaması
- 20,120 headword'un tamamı sözlükte mevcut (**%100 kapsama**)
- 58 POS çapraz kontrol: sıfır mismatch
- 4 fiil çekim uyumsuzluğu tespit ve düzeltildi

---

## 9. Kullanılan Kaynaklar

### 9.1 Sözlük Kaynakları

| # | Kaynak | URL/Dosya | Katkı |
|---|--------|-----------|-------|
| 1 | Wiktionary | `en.wiktionary.org/wiki/Category:Turkmen_lemmas` | 1,649 çekirdek lemma |
| 2 | Hunspell tk_TM | `resources/tk_TM.dic` + `.aff` | 16,238 isim/sıfat |
| 3 | PDF OCR Sözlük | Turkmen-English Dictionary (Chaihana) | Dolaylı doğrulama |
| 4 | tum.txt | `resources/turkmence_sozluk_tum.txt` | 5,362 isim |
| 5 | enedilim.com | Resmi Türkmenistan dil portalı | 8,802 giriş (fiil tek kaynağı) |
| 6 | Corpus keşfi | metbugat.gov.tm | ~700+ yeni giriş |

### 9.2 Corpus Kaynakları

| Kaynak | Tür | Kullanım |
|--------|-----|----------|
| metbugat.gov.tm | Resmi haber ajansı | Ana test corpus'u (658K token) |

### 9.3 Potansiyel Ek Corpus Kaynakları (Araştırılan)

| Kaynak | Durum | Not |
|--------|-------|-----|
| turkmenistan.gov.tm | Araştırıldı | Haber metinleri, henüz entegre edilmedi |
| tdh.gov.tm | Araştırıldı | Türkmenistan Devlet Haberleri |
| Türkmen Wikipedia | Araştırıldı | ~6,000 makale |
| HuggingFace turkmen datasets | Araştırıldı | Sınırlı kaynak mevcut |

### 9.4 Referans Akademik Kaynaklar
- Apertium turkmen-turkish dil çifti (karşılaştırmalı analiz yapıldı)
- Türkmence gramer literetürü (fiil çekim tabloları — TABLE VIII)

---

## 10. Gelecek Planları ve Yol Haritası

### 10.1 Kısa Vadeli (%97+ Hedefi)

| # | Aksiyon | Tahmini Etki | Zorluk |
|---|---------|-------------|--------|
| 1 | İngilizce kelime filtresi (and, services, other) | +~1,500 token | Kolay |
| 2 | Ettirgen/edilgen fiil çekim analizi genişletme | +~500 token | Orta |
| 3 | Daha fazla sözlük girişi (corpus'tan keşif) | +~2,000 token | Orta |
| 4 | Yuvarlaklaşma uyumu bug fix (döwletüň→döwletiň) | Kalite | Kolay |
| 5 | Compound verb pattern desteği (taýýardyrys) | +~400 token | Orta |

### 10.2 Orta Vadeli (%98+ Hedefi)

| # | Aksiyon | Açıklama |
|---|---------|----------|
| 6 | Çok ekli isim pattern'leri | ynanmagyňyzy gibi 4+ ekli formlar |
| 7 | Verbal noun + -ýş + iyelik | belleýşi, nygtaýşy gibi formlar |
| 8 | Daha fazla türetme eki desteği | -lA, -lAş, -lAn (isimden fiil) |
| 9 | Genişletilmiş softening keşfi | Daha büyük corpus'ta çalıştırma |
| 10 | Zamir çekim paradigması | 14 zamir için hal tablosu |

### 10.3 Uzun Vadeli

| # | Aksiyon | Açıklama |
|---|---------|----------|
| 11 | LibreOffice yazım denetimi eklentisi | Hunspell .dic/.aff üretimi |
| 12 | Tarayıcı eklentisi (Chrome/Firefox) | REST API üzerinden web yazım kontrolü |
| 13 | Türkmence NLP araç seti | Tokenizer, lemmatizer, POS tagger |
| 14 | Makine çevirisi entegrasyonu | Morfolojik ön/son işleme |

### 10.4 Detaylı %100 Kapsam Planı (YUZ_YUZDE_PLAN.md'den)

**Faz 1 — Kolay Kazanımlar (Tahmini ~%97.5):**
1. "diger" kategorisindeki saf İngilizce kelimeleri filtreleme
2. Sözlüğe 200-300 yüksek frekanslı eksik kelime ekleme
3. Ettirgen/edilgen kök sözlüğü genişletme

**Faz 2 — Motor İyileştirme (Tahmini ~%98.5):**
4. Compound verb (birleşik fiil) parser'ı
5. -ýş verbal noun + iyelik + hal pattern desteği
6. Daha fazla türetme eki zinciri

**Faz 3 — Kalite ve Kenar Durumlar (Tahmini ~%99):**
7. Tireli bileşik kelime desteği
8. Sıra sayı parser'ı
9. Yuvarlaklaşma uyumu bug fix

**Faz 4 — İnce Ayar (Tahmini ~%99.5+):**
10. Kalan özel isimler
11. Nadir morfolojik kalıplar
12. Kısaltma ve sembol işleme

---

## 11. Makalede Güncellenecek Bölümler

### Section 3.1 — Lexicon
- Sözlük boyutu: 1,736 → **32,738** giriş
- 5 kaynak detayı (Wiktionary, Hunspell, tum.txt, enedilim.com, corpus keşfi)
- `no_softening` flag açıklaması
- 9 aşamalı derleme süreci

### Section 3.2 — Phonology (Ünsüz Yumuşaması İstisnaları)
- Data-driven softening exception keşif pipeline'ı açıklaması
- 8,192 softening + 251 no_softening istatistiği
- Alıntı kelime analizi (Arapça/Farsça/Avrupa kökenli)

### Section 3.3 — Verb Morphotactics
- Zaman kapsam güncellemesi: 7 → **18** zaman/kip/form
- Olumsuzluk stratejileri tablosu (sentetik/kaynaşık/analitik/yok)
- Fiilimsi (participle) ve ulaç (converb) formları

### Section 4 — Evaluation
- Corpus istatistikleri: 658,881 token, 29,187 type
- Token kapsam: **%96.37**
- Type kapsam: **%70.84**
- Hata kategorisi dağılımı (10 kategori tablosu)

### Section 4.2 (YENİ) — Data-Driven Exception Discovery
- Softening keşif pipeline'ı detaylı açıklama
- Corpus-driven iyileştirme döngüsü

### Section 5 — Future Work
- %100 yol haritası (4 fazlı plan)
- NLP araç seti vizyonu
- LibreOffice/tarayıcı eklentisi planları

---

## 12. Referans Dosya Haritası

### Ana Proje Dosyaları

| Dosya | Açıklama |
|-------|----------|
| `app.py` | Flask web uygulaması + REST API |
| `morphology.py` | Web isim/fiil generator (bağımsız, API-dışı) |
| `parser.py` | Web morfolojik analiz (turkmen-fst analyzer wrapper) |
| `templates/index.html` | 4 sekmeli web arayüzü |

### Motor Dosyaları (turkmen-fst/)

| Dosya | Açıklama |
|-------|----------|
| `turkmen_fst/analyzer.py` | Morfolojik parser (kelime → kök + ekler) |
| `turkmen_fst/generator.py` | İsim/fiil çekim üretici |
| `turkmen_fst/lexicon.py` | Sözlük yükleme + sorgulama |
| `turkmen_fst/phonology.py` | Ses bilgisi kuralları (yumuşama, ünlü düşmesi) |
| `data/turkmence_sozluk.txt` | Ana sözlük dosyası (32,738 giriş) |

### Corpus Lab Dosyaları

| Dosya | Açıklama |
|-------|----------|
| `corpus_lab/scripts/build_corpus.py` | Corpus toplama (metbugat.gov.tm) |
| `corpus_lab/scripts/analyze_corpus.py` | Corpus tokenizasyon + analiz |
| `corpus_lab/scripts/run_local_coverage.py` | Kapsam testi |
| `corpus_lab/scripts/discover_softening_exceptions.py` | Softening istisna keşfi |
| `corpus_lab/scripts/validate_lexicon.py` | Sözlük doğrulama |
| `corpus_lab/data/metbugat_corpus.txt` | Ham corpus (658K token) |
| `corpus_lab/reports/corpus_coverage_local.json` | Son kapsam sonuçları |

### Dokümantasyon Dosyaları (makale_help/)

| Dosya | İçerik |
|-------|--------|
| `YAPILAN_ISLER.md` | Tamamlanan özellikler ve düzeltmeler |
| `YAPILANLAR.md` | Dosya bazlı kod değişiklikleri |
| `NOTLAR.md` | Geliştirme notları (8 faz) |
| `makale_v2_guncellemeler.md` | IEEE TurkLang v2 güncelleme detayları |
| `GELECEK_PLANLARI.md` | Gelecek planları (kısa/orta/uzun vade) |
| `SOZLUK_OLUSTURMA_SURECI.md` | Sözlük derleme pipeline'ı (5 kaynak, 9 aşama) |
| `APERTIUM_KARSILASTIRMA.md` | TurkmenFST vs Apertium vs enedilim karşılaştırma |
| `MAKALE_MIMARI_REFERANS.md` | Sistem mimarisi referansı (Section 4 için) |
| `MAKALE_SOZLUK_REFERANS.md` | Sözlük derleme referansı (Section 3 için) |
| `SECTION_3_4_ENGLISH.md` | Makale §3-§4 İngilizce metin taslağı |

### Test Dosyaları

| Dosya | Açıklama |
|-------|----------|
| `turkmen-fst/tests/` | 105 birim test (pytest) |
| `testler/test_comprehensive.py` | 1,192 kapsamlı round-trip test |
| `testler/test_new_verb_forms.py` | 124 yeni fiil form testi |
| `scripts/test_v26_comparison.py` | 4,788 v26 referans eşleşme testi |

---

## ÖZET

| Metrik | Başlangıç | Şimdi | Değişim |
|--------|-----------|-------|---------|
| Token kapsam | %73.28 | **%96.37** | +23.09pp |
| Type kapsam | ~%55 | **%70.84** | +~16pp |
| Sözlük girişi | 1,736 | **32,738** | ×18.9 |
| Benzersiz kelime | 1,700 | **30,753** | ×18.1 |
| Zaman/kip kodu | 7 | **18** | ×2.57 |
| Birim test | 0 | **6,227** | — |
| API endpoint | 0 | **7** | — |
| Softening istisnası | 0 | **251** | — |
| Bug düzeltme | — | **16+** | — |

> **Son güncelleme:** 10 Mart 2026
