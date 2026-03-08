# Türkmence Morfolojik Analizör — %100 Kapsama Planı

**Tarih:** 2026-03-08  
**Mevcut durum:** %92.59 token / %62.71 type kapsama (tam corpus, 658K token)  
**Hedef:** %100 token kapsama  

## Mevcut Kapsama

| Metrik          | Sayı         | Kapsama  |
|-----------------|--------------|----------|
| Token tanınan   | 610,080      | 92.59%   |
| Token bilinmeyen| 48,801       | 7.41%    |
| Type tanınan    | 18,302       | 62.71%   |
| Type bilinmeyen | 10,885       | 37.29%   |

## Bilinmeyen Kelime Kategorileri (token etkisine göre)

| # | Kategori | Type | Token | Token% | Aksiyon |
|---|----------|------|-------|--------|---------|
| 1 | **Sözlükte olmayan kelimeler** | ~3000 | ~16000 | ~33% | Sözlük genişletme |
| 2 | **Bilinen kök + karmaşık ek** | 1,912 | 8,830 | 14.3% | Motor iyileştirme |
| 3 | **Sınıflandırılamayan** | 2,291 | 7,658 | 12.4% | Karma (sözlük + motor) |
| 4 | **Tireli bileşik kelimeler** | 682 | 4,928 | 8.0% | Tire işleme |
| 5 | **Özel isimler (soyadlar)** | 1,085 | 4,340 | 7.0% | Toplu sözlük ekleme |
| 6 | **Fiilimsi + hal ekleri** | 394 | 2,213 | 3.6% | Motor: VN + hal |
| 7 | **İngilizce kelimeler** | 22 | 1,616 | 2.6% | İngilizce sözlük |
| 8 | **Bileşik kelimeler** | 226 | 1,271 | 2.1% | Sözlük + bileşik kural |
| 9 | **Ettirgen/edilgen zincirler** | 362 | 1,657 | 2.7% | Motor: fiil zincirleri |
| 10| **Converb (-Ip)** | 30 | 930 | 1.5% | Motor: converb düzeltme |
| 11| **-lAýyn zarfları** | 15 | 168 | 0.3% | Yeni ek tanıma |
| 12| **Ödünç kelimeler** | 38 | 97 | 0.2% | Sözlük ekleme |

---

## FAZ 1: Sözlük Genişletme (Tahmini: %92.59 → %95+ token)

### 1.1 Yaygın Eksik Kelimeler (~200 kelime)
Sözlükte bulunmayan ama corpus'ta sık geçen kelimeler:

**İsimler:**
- kararnama (85), itergi (137), logistika (75), sammit (47+40+38),
- ahalteke (182), nebitgaz (223), wekiliýet (51+60+88),
- kafedra (186), ediş (72), geçiriji (49), nusgawy (60),
- toplum (×), innowasiýa (14), telekommunikasiýa (16), 
- serhetabat (46), parlamentara (85), konsultatiw (53),
- inklýuziw (48), metan (46), noutbuk (38), plenar (82),
- franzuz → fransuz (40), sebitara (60), hökümetara (77),
- umumybilim (53), hazarýaka (39), geosyýasy (34)

**Sıfatlar:**
- innowasion (351), geoykdysady (36), ylmy-tehniki, taryhy-medeni
- wise (prezident) → wise-prezident bileşiği

**Fiiller (yoksa ekle):**
- güllemek, işlemek, bellemek, mübäreklemek, terbiýelemek,
- jemlemek, eýelemek, beslemek, kesgitlemek, diňlemek,
- hödürlemek, dörämek, gözlemek

### 1.2 Özel İsimler (~1200 kelime)
Corpus'taki soyadlar ve kişi isimleri:

**Soyadlar (türkmen patronimik kalıpları -ow/-owa/-ýew/-ýewa):**
- Otomatik oluşturulabilir: gurbangulyýewiç (165), atabaýewa (108), 
  annaýew (78), çakyýew (57), kulyýewa (55), atagulyýew (52),
  annamämmedow (49), orazdurdyýewa (48), atahallyýew (48), 
  mirziýoýew (47), seýidowa (44), garryýew (43), çaryýew (37),
  tokaýew (32), geldimyradow (47), myradowy (38)

**Kişi isimleri (eksik olanlar):**
- şawkat (88), oguljahan (100), mohammed (79), ilham (51),
  hamad (47), wladimir (37), antoniu (35), masud (34), muhammad (32),
  ali (53), emomali (32)

**Bölge/Yer isimleri:**
- tatarystan (62), hyrat (70), astrahan (36)

### 1.3 İngilizce Kelimeler (~25 kelime)
- article (1000), bin (196), golf (48), holding (36), expo (35),
  smart (×), online (×), etc.

### 1.4 Ödünç Kelimeler (~40 kelime)
- telekommunikasiýa (16), bosniýa (6), nawigasiýa (3), 
  demografiýa (3), narkologiýa (3), horeografiýa (3), 
  delimitasiýa (2), monetizasiýa (2), reabilitasiýa (2), 
  paralimpiýa (2), etc.

---

## FAZ 2: Morfolojik Motor İyileştirmeleri (Tahmini: %95 → %98+ token)

### 2.1 Fiilimsi + Hal Eki İşleme (3.6% = 2,213 token)
Fiiller `-mAk`/`-mEk` fiilimsi haliyle hal eki aldığında tanınmıyor:
```
gatnaşmagynda    = gatnaşmak + -yg + -ynda  (locative VN)
ösdürilmegine    = ösdürilmek + -gi + -ne   (dative VN)  
ösmegine         = ösmek + -gi + -ne
geçirilmegine    = geçirilmek + -gi + -ne
döredilmeginiň   = döredilmek + -gi + -niň  (genitive VN)
```
**Çözüm:** `parse_verb` veya yeni `parse_verbal_noun` fonksiyonu: 
Fiilimsi `-mAg/-mEg` + iyelik ve hal eklerini tanısın.

### 2.2 İsim-Fiil -Iş/-Uş Formları (bolşy, ulanyş, açylyş)
```
bolşy       = bol + -uş + -y    (verbal noun + possessive)
nygtalyşy   = nygtal + -yş + -y
açylyş      = açyl + -yş        (verbal noun)
belleýşi    = belle + -ýş + -i
ulanyş      = ulan + -yş
```
**Çözüm:** `-Iş/-Uş/-yş` fiilimsi eki ve bunun üzerine isim eki almasını destekle.

### 2.3 Sıfat-fiil / İşteş -IjI (Agentive) (ýetiriji, jemleýji, sürüjisi)
```
ýetiriji     = ýetir + -iji     (agent noun)
jemleýji     = jemle + -ýji
sürüjisi     = sür + -üji + -si (agent + possessive)
geçiriji     = geçir + -iji
```
**Çözüm:** `-IjI/-ÝjI` sıfat-fiil eki ekle, isimleşebildiğinden hal ekleri de alsın.

### 2.4 -dIgInI / -dYgYny Konu/Kanıt Formları
Bu formlar "...olduğunu/...ettiğini" anlamındadır:
```
goýýandygym       = goý + -ýan + -dyg + -ym    (progressive+topic+1sg)
taýýardygyny      = taýýar + -dyg + -yny        (adj+topic+3sg)
ygrarlydygyny     = ygrarly + -dyg + -yny
bardygyny         = bar + -dyg + -yny
boljakdygyna      = bol + -jak + -dyg + -yna
zerurdygyny       = zerur + -dyg + -yny
möhümdigi/ini     = möhüm + -dig + -ini
eýedigini         = eýe + -dig + -ini
durýandygyny      = dur + -ýan + -dyg + -yny
```
**Çözüm:** `-dIg/-dYg` konu-kanıt eki + iyelik/hal ekleri destekle.
Bu kalıp hem fiil hem de sıfat köklerine gelebiliyor.

### 2.5 İyelik + Hal Eki Zincirleri
Mevcut motor basit iyelik+hal destekliyor ama bazı kombinasyonlar eksik:
```
kafedrasynyň       = kafedra + -sy + -nyň    (poss3sg + genitive)
wekiliýetiniň      = wekiliýet + -iniň       (poss3sg + genitive)
teleradioýaýlymynyň = ... + -ynyň
çäräniň            = çäre + -niň             (genitive, ä→e ünlü?)
hepdäniň           = hepde + -(n)iň          (genitive)
ömrüňiziň          = ömür + -üňiz + -iň      (poss2pl + genitive)
birleşmesiniň      = birleşme + -siniň       (poss3 + gen)
geňeşliginiň       = geňeşlik + -iniň
sergä              = sergi + -ä              (dative, i→e?)
çärä               = çäre + -ä?  
derejä             = dereje + -ä             (dative)
```
**Çözüm:** 
- İyelik+genitif, iyelik+datif gibi zincirleri düzelt
- `çäre→çäräniň`, `dereje→derejä`, `sergi→sergä` gibi ünlü değişimlerini kontrol et

### 2.6 Ettirgen/Edilgen Fiil Zincirleri (2.7%)
```
döwrebaplaşdyrmak      = döwrebap + -laş + -dyr + -mak
diwersifikasiýalaşdyrmak = ... + -laş + -dyr + -mak
sanlylaşdyrmak         = sanly + -laş + -dyr + -mak
ösdürilmegine          = ös + -dür + -il + -mek + -i + -ne
pugtalandyrylmagyna    = pugtalan + -dyr + -yl + -mak + -y + -na
ýokarlandyrylmagyna    = ýokarlan + -dyr + -yl + -mak + -y + -na
```
**Çözüm:** `-lAş` + `-dYr` + `-Yl` gibi çoklu yapım eki zincirlerini destekle.

### 2.7 Converb -Ip Düzeltmeleri (1.5%)
29 fiil kökü converb formunu üretemiyor (genellikle -lAp formu):
```
gülläp     = gülle + -p   (güllemek converb)
işläp      = işle + -p    
belläp     = belle + -p
mübärekläp = mübärekle + -p
terbiýeläp = terbiýele + -p
```
**Çözüm:** Bu fiillerin sözlükte olduğunu kontrol et, yoksa ekle.
Ayrıca -lA fiillerinin converb formunu (-lAp) üretebilmeyi kontrol et.

### 2.8 -lAýyn Zarf Ekleri (0.3%)
```
ulgamlaýyn      = ulgam + -laýyn     (manner adverb)
mowzuklaýyn     = mowzuk + -laýyn
şertnamalaýyn   = şertnama + -laýyn
tapgyrlaýyn     = tapgyr + -laýyn
```
**Çözüm:** `-lAýyn/-leýin` zarf yapım ekini tanı.

---

## FAZ 3: Yapısal İyileştirmeler (Tahmini: %98 → %99+ token)

### 3.1 Tireli Bileşik Kelime Desteği (8.0%)
Corpus'ta çok sık tireli bileşikler var:
```
durmuş-ykdysady (350), söwda-ykdysady (307), haýyr-sahawat (272),
ýaşaýyş-durmuş (196), syýasy-diplomatik (163), premýer-ministri (116),
maddy-enjamlaýyn (107), ýangyç-energetika (100)
```
**Çözüm seçenekleri:**
1. Bilinen bileşikleri sözlüğe ekle
2. Analizörde tire-bileşik kural: her iki yarıyı ayrı analiz et, birleştir
3. En sık 200 tireli bileşiği sözlüğe ekle

### 3.2 Kısaltma + Ek Kalıpları
```
bmg-ä (11), hhr-iň (11), şhg-ä (5), gfr-iň (4), abş-a (3)
```
**Çözüm:** Büyük harf kısaltma + tire + küçük harf ek kalıbını tanı.

### 3.3 Bileşik Kelime Kuralları
```
türkmennebit (93), türkmengaz (93), şähergurluşyk (42),
türkmenhaly (38), türkmenhowaýollary (38), türkmenhimiýa (36)
```
**Çözüm:** "türkmen-" ön eki gibi yaygın bileşik köklerini destekle,
veya en sık bileşikleri sözlüğe toplu ekle.

---

## FAZ 4: İnce Ayar (Tahmini: %99 → %100 token)

### 4.1 Ünlü Uyumu / Ses Değişiklikleri
- çäre → çäräniň (genitive)
- dereje → derejä (dative)  
- sergi → sergä (dative)

### 4.2 Kalan Özel Durumlar
- allatagaladan (60), sagbolsun (56) → kalıplaşmış ifadeler
- satyn (56) → "satyn almak" bileşik yapısı
- gezekki (48) → sıfat türevi

### 4.3 Sıra Sayı Kalıntıları
- kenji (1) → hatalı yazım

---

## Uygulama Öncelik Sırası

| Adım | Aksiyon | Tahmini Token Etkisi | Zorluk |
|------|---------|---------------------|--------|
| 1 | Yaygın eksik kelimeleri sözlüğe ekle (200+) | +5,000 token (~0.8%) | Kolay |
| 2 | Soyadları toplu ekle (1000+) | +4,000 token (~0.6%) | Kolay |
| 3 | Fiilimsi+hal (-mAgInda) desteği | +2,200 token (~0.3%) | Orta |
| 4 | -dIgInI/-dYgYny formları | +3,000 token (~0.5%) | Orta |
| 5 | Converb -lAp düzeltmeleri | +900 token (~0.1%) | Kolay |
| 6 | -Iş/-Uş fiilimsi eki | +1,500 token (~0.2%) | Orta |
| 7 | -IjI agentive eki | +1,000 token (~0.2%) | Orta |
| 8 | İyelik+hal zinciri düzeltmeleri | +3,000 token (~0.5%) | Zor |
| 9 | Ettirgen/edilgen zincirleri | +1,600 token (~0.2%) | Zor |
| 10| Tireli bileşikler sözlüğe ekle | +4,900 token (~0.7%) | Kolay |
| 11| İngilizce/yabancı kelimeler | +1,600 token (~0.2%) | Kolay |
| 12| -lAýyn zarf eki | +170 token (~0.0%) | Kolay |
| 13| Bileşik kelime kuralları | +1,300 token (~0.2%) | Orta |
| 14| Ödünç kelimeler | +100 token (~0.0%) | Kolay |
| **Toplam** | | **~30,000+ token (~4.5%)** | |

**Not:** Bazı kategoriler örtüşüyor. Gerçekçi hedef: Faz 1-2 ile %97-98, Faz 3-4 ile %99+ ulaşılabilir.

---

## Kullanılan Veri Kaynakları
- Corpus: `corpus_lab/data/metbugat_corpus.txt` (658,881 token)
- Sözlük: `turkmen-fst/data/turkmence_sozluk.txt` (30,474 giriş)
- Gap analiz raporu: `corpus_lab/reports/full_gap_analysis.json`
- Coverage raporu: `corpus_lab/reports/corpus_coverage_local.json`
