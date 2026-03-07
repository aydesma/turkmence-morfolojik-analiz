# Tabaklar (1994) PDF vs Kod Karşılaştırması

> **Kaynak:** Özcan Tabaklar, *Türkmencenin Morfolojisi*, İstanbul Üniversitesi Doktora Tezi, 1994 (210 sayfa, 23347.pdf)

## 1. İSİM ÇEKİM EKLERİ (Noun Inflection)

### 1.1 Çokluk Eki (+lAr)
| Özellik | PDF (Tabaklar §211) | Kod | Durum |
|---------|---------------------|-----|-------|
| Temel: -lar/-ler | ✅ | ✅ `isim_cekimle()` | ✅ TAM |
| Orta hece düşmesi (ogul→ogullar) | ✅ | ✅ DUSME_ADAYLARI | ✅ TAM |
| Yuvarlaklaşma (iyelik sonrası) | ✅ | ✅ (sınırlı liste) | ✅ TAM |

### 1.2 İyelik Ekleri (Possessive)
| Özellik | PDF (Tabaklar §212) | Kod | Durum |
|---------|---------------------|-----|-------|
| 1T: -(y/I)m | ✅ "birinci teklik +Im" | ✅ A1 tek | ✅ TAM |
| 2T: -(y/I)ň | ✅ "ikinci teklik +Ifi" | ✅ A2 tek | ✅ TAM |
| 3T: -(s)y/(s)I | ✅ "üçüncü teklik +I/+sI" | ✅ A3 tek | ✅ TAM |
| 1Ç: -(y/I)myz | ✅ "birinci çokluk +Omiz" | ✅ A1 cog | ✅ TAM |
| 2Ç: -(y/I)ňyz | ✅ "ikinci çokluk +Ofiiz" | ✅ A2 cog | ✅ TAM |
| 3Ç: -lary/-leri | ✅ "+lArI" (3Ç iyelik) | ❌ B3 yok | ⚠️ EKSİK |
| Orta hece düşmesi + yuvarlaklaşma | ✅ "ogul+ı>oglunı" | ✅ | ✅ TAM |

### 1.3 Aitlik Eki (+kI)
| Özellik | PDF (Tabaklar §2121) | Kod | Durum |
|---------|---------------------|-----|-------|
| Lokatif+kI: -dakI/-dekI | ✅ "astındakı, eginindäki" | ❌ | ❌ YOK |
| Genitif+kI: -nIňkI | ✅ "meninki, seniňki" | ❌ | ❌ YOK |
| Zaman+kI: düýnki, öňki | ✅ "+kI aitlik eki" | ❌ | ❌ YOK |
| +kI sonrası iyelik+hal | ✅ "soňkusyny, öňküden" | ❌ | ❌ YOK |

> **Not:** Bu bizim #6 -daky/-däki eksikliğimiz. PDF'e göre +kI eki yalnız lokatife değil, genitif ve zaman isimlerine de gelir.

### 1.4 Hal Ekleri (Cases)
| Özellik | PDF (Tabaklar §213) | Kod | Durum |
|---------|---------------------|-----|-------|
| Yalın (Nominatif) | ✅ eksiz | ✅ | ✅ TAM |
| İlgi (Genitif) +In/+nIn | ✅ ekin vokali daima dar-düz (tek heceli yuvarlak hariç) | ✅ A2 | ✅ TAM |
| Belirtme (Akkuzatif) +I/+nI | ✅ dar-düz, vokal uyumu dışı | ✅ A4 | ✅ TAM |
| Yönelme (Datif) +A/+nA | ✅ +A/+nA | ✅ A3 | ✅ TAM |
| Bulunma (Lokatif) +dA | ✅ +dA | ✅ A5 | ✅ TAM |
| Çıkma (Ablatif) +dAn | ✅ +dAn | ✅ A6 | ✅ TAM |
| Eşitlik +çA | ✅ kalıplaşmış (+çA/+çe) | ❌ | ❌ YOK |
| Instrumental +0n | ✅ pugaçdan, sövünç bilen | ❌ | ❌ YOK |
| Konsonant yumuşaması (softening) | ✅ k→g, p→b, t→d, ç→j | ✅ SOFTENING_TABLE | ✅ TAM |
| n-kaynaştırması (3T iyelik + hal) | ✅ ogluny, ornunda | ✅ (düzeltildi) | ✅ TAM |
| Orta hece düşme + yuvarlaklaşma | ✅ orun→ornunda | ✅ (düzeltildi) | ✅ TAM |

---

## 2. SIFATLAR ve SAYILAR

### 2.1 Sıra Sayı Sıfatları
| Özellik | PDF (Tabaklar §22222, §1112) | Kod | Durum |
|---------|------------------------------|-----|-------|
| +OncI yapım eki | ✅ "birinci, üçüncü, dokuzuncu" | Regex tanıma var (2024-nji) | ⚠️ KISMI |
| Yazıyla yazılan sıra sayıları | ✅ "ýedinji, birinji, ikinji" | ❌ tanınmıyor | ❌ EKSİK |
| Vokal: daima dar-düz | ✅ | Regex sadece -nji/-njy | ⚠️ KISMI |

> **Not:** PDF'e göre +OncI eki sayı isimlerinden sıra sayısı yapan **yapım ekidir**. Kodumuz bunu sadece `\d+-nji` regex ile tanıyabiliyor, yazıyla yazılan "ýedinji, birinji, ikinji, üçünji, dördünji, bäşinji, altynjy, ýedinji, sekizinji, dokuzynjy, onunjy" gibi formları tanıyamıyor.

---

## 3. FİİLDEN FİİL YAPMA EKLERİ (Voice / Derivation)

### 3.1 Olumsuzluk (-mA)
| PDF §141 | Kod | Durum |
|----------|-----|-------|
| -mA- olumsuzluk eki | ✅ her zaman kodunda neg=True | ✅ TAM |

### 3.2 Dönüşlülük (-On)
| PDF §142 | Kod | Durum |
|----------|-----|-------|
| -On dönüşlülük (gör-ün, yuv-un) | Z21 ÖZL kodda var | ⚠️ KISMI |
| Pasiflik fonksiyonu (-lA fiillere -On) | ✅ başla-n, işle-n | ❌ analyzer'da yok | ⚠️ EKSİK |

### 3.3 Edilgenlik (-Ol)
| PDF §143 | Kod | Durum |
|----------|-----|-------|
| -Ol- pasiflik (aç-ıl, dım-ıl, git-il) | Z18 GAÝ kodda var | ⚠️ KISMI |
| Her türlü fiile getirilir | ✅ çok geniş | Sadece lexikondaki gövdeler | ⚠️ KISMI |

### 3.4 İşteşlik (-Oş)
| PDF §144 | Kod | Durum |
|----------|-----|-------|
| -Oş- ortaklık (oka-ş, gürle-ş) | Z20 ŞÄR kodda var | ⚠️ KISMI |

### 3.5 Ettirgenlik/Faktitif
| PDF Bölümü | Ek | Örnek | Kodda Z17 | Durum |
|------------|-----|-------|-----------|-------|
| §145 -Ot- | -t | döre-t, boşa-t | ✅ | ⚠️ KISMI (sadece leksikon) |
| §146 -Or- | -yr/-ir/-ur/-ür | doy-ur, geç-ir, yet-ir | ✅ | ⚠️ KISMI |
| §147 -OAr- | -ar/-er | çık-ar, gop-ar, bit-ir | ✅ | ⚠️ KISMI |
| §148 -dIr/(-dUr-) | -dyr/-dir/-dur/-dür | döl-dur, güldür, düşündir | ✅ | ⚠️ KISMI |
| §149 -dAr- | -dar/-der | üg-dar, dön-der | ❌ | ❌ YOK |
| §1410 -Oz- | -uz/-iz/-üz | gork-uz, tur-uz | ❌ | ❌ YOK |
| §1411 -kez- | -kez | görk-ez | ❌ | ❌ YOK |

> **Not:** PDF'e göre Türkmencede en az 7 farklı faktitif (ettirgenlik/causative) ek tipi var. Kodumuz voice Z17/Z18 olarak generator'da var ama analyzer sadece leksikondaki türemiş gövdeleri araştırıyor, üretken morfolojik ayrıştırma yapmıyor.

---

## 4. FİİL ÇEKİMİ (Verb Conjugation)

### 4.1 Şahıs Ekleri
| PDF §311 | Tip | Kullanım | Kod | Durum |
|----------|-----|----------|-----|-------|
| Tip 1 (Zamirden) | -In, -sIn, ∅, -Is, -sInIz, -lAr | Geniş/Şimdiki | ✅ extended | ✅ TAM |
| Tip 2 (İyelikten) | -m, -n, ∅, -k, -nIz, -lAr | Geçmiş/Şart | ✅ standard | ✅ TAM |
| Tip 3 (Emir) | -AyIn, ∅/-gIn, -sIn, -AlI, -In, -sInlAr | Emir | ✅ Z9 | ✅ TAM |

### 4.2 Basit Zamanlar
| PDF Bölümü | Ek | Şahıs Tipi | Kodda | Durum |
|------------|-----|-----------|-------|-------|
| §3121 Geniş zaman | -Ar | Tip 1 | Z7 (G2 Nämälim Geljek/Aorist) | ✅ TAM |
| §3122 Şimdiki zaman | -yAr | Tip 1 | Z4 (H1 Umumy Häzirki) | ✅ TAM |
| §3123 Görülen geçmiş | -dI | Tip 2 | Z1 (Ö1 Anyk Öten) | ✅ TAM |
| §3124 Öğrenilen geçmiş | -IpdIr | N/A | Z2 (Ö2 Daş Öten) | ✅ TAM |
| §3125 Gelecek zaman | -cAk | Eksiz | Z6 (G1 Mälim Geljek) | ✅ TAM |
| §31251 İstek-gelecek | -mAkçI | Eksiz | Yok → en yakın Z6 | ⚠️ EKSİK |
| §3126 Emir | çeşitli | Tip 3 | Z9 (Buýruk) | ✅ TAM |
| §3127 Şart | -sA | Tip 2 | Z8 (Şert) | ✅ TAM |
| §3128 İstek | -A | N/A | ❌ | ❌ YOK (arkaik) |
| §3129 Gereklilik | -mAlI | Eksiz | Z10 (Hökmanlyk) | ✅ TAM |
| §3130 Bildirme (i-fiili) | -dIr | Tip 1 | Yok (ayrı) | ⚠️ EKSİK |

> **PDF Karşılıkları:**
> - PDF "Geniş zaman -Ar" = Kodda Z7 "Nämälim Geljek" (aynı ek, farklı terminoloji)
> - PDF "-mAkçI istek belirten gelecek" = Kodda tam karşılık yok (coverage'ı bu etkiler)
> - PDF "İsim fiili -dIr" = bildirme eki → kodda kopula olarak işlenmiyor

### 4.3 Birleşik Çekimler (Compound Tenses)
| PDF Bölümü | Kalıp | Kodda | Durum |
|------------|-------|-------|-------|
| §31411 Geniş zaman hikayesi | -Ar-dI | Z22 HK_GN | ✅ TAM |
| §31412 Şimdiki zamanın hikayesi | -yAr-dI | Z23 HK_ŞH | ✅ TAM |
| §31413 Öğrenilen geçmişin hikayesi | -Ip-dI | Z24 HK_ÖG | ✅ TAM |
| §31414 Gelecek zamanın hikayesi | -cAk-dI | Z25 HK_GL | ✅ TAM |
| §314141 İstek gelecek hikayesi | -mAkçI-dI | Z26 HK_NY | ✅ TAM |
| §31415 Şartın hikayesi | -sA-dI | Z27 HK_ŞR | ✅ TAM |
| §31416 Gerekliliğin hikayesi | -mAlI-dI | Z28 HK_HÖ | ✅ TAM |
| §31421 Geniş zamanın rivayeti | -Ar-mIş | Z29 RW_GN | ✅ TAM |
| §31422 Şimdiki zamanın rivayeti | -yAr-mIş | Z30 RW_ŞH | ✅ TAM |
| §31423 Öğrenilen geçmişin rivayeti | -Ip-mIş | Z31 RW_ÖG | ✅ TAM |
| §31424 Gerekliliğin rivayeti | -mAlI-mIş | Z32 RW_HÖ | ✅ TAM |
| §31431 Geniş zamanın şartı | -Ar bolsa | Z33 ŞR_GN | ✅ TAM |
| §31432 Gelecek zamanın şartı | -cAk bolsa | Z34 ŞR_GL | ✅ TAM |
| §314321 İstek gelecek şartı | -mAkçI bolsa | Z35 ŞR_NY | ✅ TAM |

> **Sonuç:** Birleşik çekimler çok iyi uyumlu! PDF'deki tüm birleşik zamanlar kodda mevcut.

### 4.4 Partisipler ve Gerundiumlar
| PDF Bölümü | Ek | Fonksiyon | Kodda | Durum |
|------------|-----|----------|-------|-------|
| §321 -An | -An/-en | Geçmiş/genel partisip | Z14 FÖ | ✅ TAM |
| §322 -dIk | -dIk/-yAn | İyelikli partisip | ❌ | ❌ YOK |
| §323 -Ar/-mAz/-cAk | geniş/gel/olumsuz part. | Z16 FG (-jAk) | ⚠️ KISMI |
| §324 -mAlI | gereklilik partisipi | ❌ (sadece Z10 fiil) | ⚠️ |
| §3311 İsim fiili partisipi | -dIgy | yardımcı eylem part. | ❌ | ❌ YOK |

#### Gerundiumlar (Converbs)
| PDF Bölümü | Ek | Fonksiyon | Kodda | Durum |
|------------|-----|----------|-------|-------|
| §331 -A/-y | -A/-y | Tekrar (bara bara) | ❌ | ❌ YOK |
| §332 -I | -I | Birleşik fiil (gidiberdim) | ❌ | ❌ YOK |
| §333 -Ip | -Ip | En işlek gerundium | Z13 FH | ✅ TAM |
| §334 -mAn | -mAn | Olumsuz gerundium | Z13 neg=True | ✅ TAM |
| §335 -AlI | -AlI bäri | Devamlılık | ❌ | ❌ YOK |
| §336 -yAnçA | -yAnçA | "-e kadar" | ❌ | ❌ YOK |
| §337 -dIkçA | -dIkçA | "-dıkça" | ❌ | ❌ YOK |
| §338 -AndA | -AndA | "-dığında" | ❌ | ❌ YOK |
| §339 -kA | -kA | "-iken" | ❌ | ❌ YOK |

> **Not:** PDF'de 9 farklı gerundium eki var, kodumuz sadece -Ip (ve olumsuz -mAn) formunu türetiyor.

---

## 5. YAPIM EKLERİ (Derivational Morphology)

### 5.1 İsimden İsim
| PDF | Ek | Örnek | Kodda | Durum |
|-----|-----|-------|-------|-------|
| §111 | +lIk | gözellIk, yoldaşlIk | ❌ | ❌ YOK |
| §112 | +çI | awçI, mugallImçI | ❌ | ❌ YOK |
| §115 | +sIz | huşsuz, parasyz | ❌ | ❌ YOK |
| §116 | +kI | ýanky, öňki, daşky, içki | ❌ | ❌ YOK |
| §117 | +cIk | guşjagaz | ❌ | ❌ YOK |
| §1110 | +çA | Türkmençe | ❌ | ❌ YOK |
| §1111 | +dAş | watandaş, pikirdaş | ❌ | ❌ YOK |
| §1112 | +ncI | birinji, ýedinji | ❌ (regexle) | ⚠️ KISMI |

### 5.2 İsimden Fiil
| PDF | Ek | Örnek | Kodda | Durum |
|-----|-----|-------|-------|-------|
| §121 | +lA | işle-, sözle- | ❌ | ❌ YOK |
| §122 | +Al | azal-, gözel- | ❌ | ❌ YOK |
| §125 | +sA | suwsa- | ❌ | ❌ YOK |

### 5.3 Fiilden İsim
| PDF | Ek | Örnek | Kodda | Durum |
|-----|-----|-------|-------|-------|
| §131 | -mAk | etmek, görmek | ❌ | ❌ YOK (infinitive) |
| §132 | -mA | görme, bişirme | ❌ | ❌ YOK |
| §133 | -Iş | barış, görüş | ❌ | ❌ YOK |
| §134 | -gI | bilgi, içgi | ❌ | ❌ YOK |
| §135 | -Im | bilim, ölçüm | ❌ | ❌ YOK |
| §136 | -Ik | kesik, açık | ❌ | ❌ YOK |
| §1310 | -An | gören, gelen → isimleşme | Z14 var | ⚠️ KISMI |

---

## 6. FONOLOJİ KARŞILAŞTIRMASI

### 6.1 Ses Olayları
| Özellik | PDF | Kod | Durum |
|---------|-----|-----|-------|
| Kalınlık-İncelik uyumu | ✅ tüm ekler | ✅ `nit` (yoğın/inçe) | ✅ TAM |
| Düzlük-Yuvarlaklık uyumu | ✅ tek heceli yuvarlak | ✅ `dit` (düz/togalak) | ✅ TAM |
| Konsonant yumuşaması (p→b, t→d, ç→j, k→g) | ✅ | ✅ SOFTENING_TABLE | ✅ TAM |
| Yumuşama istisnaları (alınma sözler) | ✅ | ✅ SOFTENING_EXCEPTIONS | ✅ TAM |
| Orta hece düşmesi | ✅ "ogul→ogluny" | ✅ DUSME_ADAYLARI | ✅ TAM |
| Orta hece yuvarlaklaşması | ✅ "orun→ornunda" | ✅ YUVARLAKLASMA_LISTESI | ✅ TAM |
| n-kaynaştırması (3T iyelik + hal) | ✅ | ✅ (düzeltildi) | ✅ TAM |
| Geniş zamanda r/l düşmesi | ✅ "al-ar→ar, gel-er→gär" | ❌ | ❌ YOK |

> **Kritik Eksik:** PDF §3121'de geniş zamanda `r` ve `l` ile biten fiillerde ek vokali ve fiil sonu konsonantı düşüp vokal uzaması anlatılıyor (al-ar→ar, gel-er→gär, otur-ar→otyr). Bu, yazı dilinde nadiren kullanılsa da konuşma dilinde çok yaygın.

---

## 7. ÖZET: KAPSAM TABLOSU

| Kategori | PDF Bölümü | Kodda | Uyum |
|----------|-----------|-------|------|
| İsim çokluk eki | §211 | ✅ | 100% |
| İyelik ekleri (1T-2Ç) | §212 | ✅ | 90% (3Ç eksik) |
| Hal ekleri (6 hal) | §213 | ✅ | 85% (eşitlik/instrumental yok) |
| Aitlik eki +kI (-daky) | §2121 | ❌ | 0% |
| Sayı & Sıra sayı | §2222 | ⚠️ | 30% (sadece rakam+nji) |
| Şahıs ekleri (3 tip) | §311 | ✅ | 100% |
| Basit zamanlar (10) | §312 | ✅ 9/10 | 90% (-mAkçI eksik) |
| Birleşik zamanlar (14) | §314 | ✅ 14/14 | 100% |
| Emir | §3126 | ✅ | 100% |
| Şart | §3127 | ✅ | 100% |
| Gereklilik | §3129 | ✅ | 100% |
| Partisipler | §32 | ✅ 3/5 | 60% |
| Gerundiumlar (Converbs) | §33 | ✅ 2/9 | 22% |
| Ettirgenlik (Causative) | §145-1412 | ⚠️ Z17 var | 40% (sadece leksikon) |
| Edilgenlik (Passive) | §142-143 | ⚠️ Z18 var | 40% (sadece leksikon) |
| İşteşlik (Reciprocal) | §144 | ⚠️ Z20 var | 40% (sadece leksikon) |
| Dönüşlülük (Reflexive) | §142 | ⚠️ Z21 var | 40% (sadece leksikon) |
| İsim fiili (Copula) | §313 | ❌ | 0% |
| Yapım ekleri (İ→İ) | §11 | ❌ | 0% |
| Yapım ekleri (İ→F) | §12 | ❌ | 0% |
| Yapım ekleri (F→İ) | §13 | ❌ | 0% |
| Yapım ekleri (F→F) | §14 | ⚠️ voice | 15% |

---

## 8. ÖNCELİK SIRASI (Coverage Etkisi)

PDF ile karşılaştırma sonucunda, coverage artışına en çok katkı sağlayacak iyileştirmeler:

### Yüksek Öncelik (corpusda çok sık)
1. **-daky/-däki aitlik eki** → Toplamda ~2-3% coverage artış beklenir
2. **Gerundium ekleri** (-yAnçA, -AndA, -AlI, -dIkçA) → ~1-2% artış
3. **Infinitive -mAk/-mek** → ~0.5-1% artış
4. **Kopula -dyr/-dir** → ~0.5-1% artış
5. **Yazılı sıra sayıları** (ýedinji, birinji...) → ~0.3% artış

### Orta Öncelik (sık ama türetilebilir)
6. **-mAkçI istek-gelecek** → ~0.2% artış
7. **Partisip + iyelik/hal** (geleniň, gelenlere) → ~1% artış
8. **-lIk, -çI, -sIz yapım ekleri** → ~1% artış (ama sözlüğe ekleme alternatifi var)
9. **Voice üretken ayrıştırma** (causative/passive morph decomp) → ~0.5% artış

### Düşük Öncelik (kalıplaşmış / seyrek)
10. Eşitlik/Instrumental hal ekleri
11. -dAr, -Oz, -kez faktitif ekleri
12. İstek kipi -A (arkaik)
13. Geniş zamanda r/l düşmesi (konuşma dili)
