# Corpus Coverage Gap Analysis Report

**Tarih:** 2025-01-20  
**Corpus:** metbugat_corpus.txt (697,285 token, 3,000 makale)  
**Örneklem:** 20,000 token (5,504 benzersiz type)

---

## 1. Mevcut Durum

| Metrik | Önceki (Fix Öncesi) | Şimdiki (Fix Sonrası) | Fark |
|--------|---------------------|-----------------------|------|
| Token Coverage | 73.26% | **75.56%** | +2.30% |
| Type Coverage | 61.68% | **64.53%** | +2.85% |
| Tanınan Type | 3,395 | **3,552** | +157 |
| Tanınmayan Type | 2,109 | **1,952** | -157 |

### Uygulanan Düzeltmeler (Bu Oturum)
1. **n-kaynaştırma ünlü uyumu** — A3 iyelikten sonra A2/A5/A6 hal ekleri her zaman kalın (nyň/nda/ndan) oluyordu, ince ünlüler için (niň/nde/nden) düzeltildi.
2. **Orta Hece Yuvarlaklaşma kapsamı** — Sadece `DUSME_ADAYLARI` ve `YUVARLAKLASMA_LISTESI` kelimelerine sınırlandırıldı (önceden TÜM yuvarlak ünlülü kelimelere uygulanıyordu).
3. **döwür eklendi** — `DUSME_ADAYLARI` / `VOWEL_DROP_CANDIDATES` listesine eklendi.

---

## 2. Hata Kategori Dağılımı

| # | Kategori | Type | Token | Token% | Kümülatif |
|---|----------|------|-------|--------|-----------|
| 1 | **diger** | 1,293 | 3,032 | 15.16% | 90.72% |
| 2 | **fiilimsi_zarf** | 183 | 523 | 2.61% | 93.33% |
| 3 | **tireli_bilesik** | 158 | 498 | 2.49% | 95.82% |
| 4 | **ettirgen_edilgen** | 143 | 325 | 1.62% | 97.45% |
| 5 | **yapim_ekli** | 53 | 134 | 0.67% | 98.12% |
| 6 | **fiil_cekimi** | 58 | 112 | 0.56% | 98.68% |
| 7 | **sira_sayi** | 1 | 99 | 0.50% | 99.17% |
| 8 | **ozel_isim** | 6 | 72 | 0.36% | 99.53% |
| 9 | **cok_ekli_isim** | 43 | 57 | 0.29% | 99.82% |
| 10 | **yabanci** | 14 | 37 | 0.18% | 100.00% |

---

## 3. "Diger" Kategorisi Derinlemesine Analiz (3,032 token, %62)

"Diger" kategorisi en büyük dilimdir ve birkaç alt-gruptan oluşur:

### 3.1. Tokenizer Fragmanları (~1,500 token, ~%31 of unrec)
1-3 harflik parçalar: `la`, `le`, `ry`, `ri`, `li`, `ra`, `ly`, `dy`, `de`, `ta`, `bi`, `na`, `ny`, `ma`, `gy`, `ka`, `ti`, `mi`, `my`, `sy`, `di`, `ty`, `ni`, `ki`, `du`, `se`, `gi`, `ha`, `bo`...

**Kaynak:** Corpus'taki özel isimler, URL'ler, sayı-kelime birleşimleri, eksik tire ile ayrılan kelimeler.  
**Çözüm:** Tokenizer regex iyileştirmesi + minimum kelime uzunluğu filtresi (3+ harf).

### 3.2. Sözlükte Eksik Kökler (~500 token, ~%10)
| Kelime | Frekans | Açıklama |
|--------|---------|----------|
| ösüş | 27 | gelişme (isim) |
| yglan | 18 | ilan (fiil kökü) |
| galkynyşy | 13 | yükseliş+A3 |
| halkbank | 20 | özel isim/kurum |
| döwletara | 13 | devletlerarası |
| şunda | 13 | burada (zamir) |
| oňyn | 11 | olumlu (sıfat) |
| birnäçe | 10 | birkaç (zamir) |
| edýän | 14 | yapan (sıfat-fiil) |
| gülläp | 17 | çiçek açarak (zarf-fiil) |

**Çözüm:** Bu kelimelerin sözlüğe eklenmesi. ~100-200 kök ekleme ile bu alt-kategori büyük oranda çözülür.

### 3.3. -dAky/-dÄki Sıfat Eki (~200 token, ~%4)
`adyndaky`, `arasyndaky`, `bilelikdäki`, `respublikasyndaky`, `türkmenistandaky`

**Çözüm:** `-daky/-däki/-ndaky/-ndäki` sıfat türetme eki desteği (göreceli sıfat). Analyzer'a postposition/sıfat morfolojisi eklenmeli.

### 3.4. Zamir/İşaret Sözcükleri (~150 token, ~%3)
`mundan`, `munuň`, `şolaryň`, `şunda`

**Çözüm:** Zamir paradigması (bu/şu/ol) hal çekimlerinin analyzer'a eklenmesi.

### 3.5. Bare Suffix Fragments (~400 token, ~%8)
`nyň`, `niň`, `den`, `ler`, `lik`, `lan`, `len`, `mak`, `mek`, `dyr`

**Kaynak:** Tikre ile ayrılan kelimelerden (Berdimuhamedow-yň → "yň" ayrı token olur).  
**Çözüm:** Tokenizer'da tire sonrası eklerin ana kelimeye birleştirilmesi.

---

## 4. %100 Hedefi İçin Yol Haritası

### Faz 1: Kolay Kazanımlar → %82-85 hedef (+7-10%)
| Eylem | Tahmini Kazanım | Zorluk |
|-------|----------------|--------|
| **Sözlük genişletme** (100-200 kök) | +3-4% | Kolay |
| **-nji sıra sayı** eki desteği | +0.5% | Kolay |
| **Tokenizer minimum uzunluk filtresi** (3+ harf) | +3-4% | Kolay |
| **Zamir paradigması** (bu/şu/ol hal çekimleri) | +0.5% | Orta |

### Faz 2: Fiilimsi & Zarf Desteği → %88-90 hedef (+5-7%)
| Eylem | Tahmini Kazanım | Zorluk |
|-------|----------------|--------|
| **-yp/-ip zarf-fiil** (converb) desteği | +1.5% | Orta |
| **-mAk/-mAge mastar** (infinitive) çekimi | +1% | Orta |
| **-dAky/-dÄki** sıfat eki | +1% | Orta |
| **Tireli bileşik kelime** tokenizer/analizi | +2.5% | Orta |

### Faz 3: Türetme Morfolojisi → %95 hedef (+5-7%)
| Eylem | Tahmini Kazanım | Zorluk |
|-------|----------------|--------|
| **Ettirgen/edilgen** (-dyr/-dir, -yl/-il) çekimi | +1.6% | Zor |
| **-ly/-li yapım eki** (sıfat türetme) | +0.7% | Orta |
| **-lyk/-lik yapım eki** (isim türetme) | +0.3% | Orta |
| **Geçmiş zaman -dy/-di** fiil çekimi | +0.5% | Orta |
| **Sıfat-fiil -ýän/-ýan, -en/-an** | +1% | Zor |
| **Multi-suffix zincir analizi** geliştirme | +0.5% | Zor |

### Faz 4: Tam Kapsam → %98-100 hedef (+3-5%)
| Eylem | Tahmini Kazanım | Zorluk |
|-------|----------------|--------|
| **Özel isim veritabanı** (Berdimuhamedow vb.) | +0.4% | Kolay |
| **Yabancı kelime veritabanı** | +0.2% | Kolay |
| **Bileşik kelime analizi** (gelişmiş) | +0.5% | Zor |
| **Corpus-driven sözlük genişletme** (ikinci tur) | +1-2% | Orta |
| **Nadir fiil çekimleri ve istisna halleri** | +0.5% | Zor |

---

## 5. Öncelik Sıralaması (ROI Bazlı)

1. 🔴 **Tokenizer iyileştirmesi** — Fragment temizleme ile hemen +3-4% kazanım
2. 🔴 **Sözlük genişletme (100-200 kök)** — Corpus frekansına göre eksik köklerin eklenmesi (+3%)
3. 🟡 **-nji sıra sayı eki** — Tek bir ek ile +0.5% (çok kolay)
4. 🟡 **Tireli bileşik tokenizer** — hem-de, beýläk-de vs. (+2.5%)
5. 🟡 **-yp/-ip converb + -mAk infinitive** — Fiilimsi desteği (+2.5%)
6. 🟡 **-daky/-däki sıfat eki** — Göreceli sıfat desteği (+1%)
7. 🟠 **Ettirgen/edilgen morfolojisi** — Karmaşık ama yüksek getiri (+1.6%)
8. 🟠 **Yapım ekleri (-ly/-li, -lyk/-lik)** — Sıfat/isim türetme (+1%)
9. ⚪ **Zamir paradigması** — Sınırlı sayıda kelime (+0.5%)
10. ⚪ **Özel isim + yabancı kelime DB** — Düşük getiri (+0.6%)

---

## 6. Sonuç

| Hedef | Kapsamdan | Kapsama | Gereken Çalışma |
|-------|-----------|---------|----------------|
| Faz 1 | 75.56% | ~83% | 1-2 gün |
| Faz 2 | ~83% | ~90% | 3-5 gün |
| Faz 3 | ~90% | ~95% | 1-2 hafta |
| Faz 4 | ~95% | ~98-100% | 2-4 hafta |

**En hızlı kazanım:** Tokenizer fragment filtresi + sözlük genişletme ile **~83%** hedefine ulaşılabilir.  
**Gerçekçi kısa vadeli hedef:** Faz 1 + Faz 2 ile **~90%** coverage.
