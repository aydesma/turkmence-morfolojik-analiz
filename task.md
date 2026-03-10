# TASK.MD — Türkmence Morfolojik Analiz Görev Takibi

## Mevcut Durum
- **Token coverage**: 96.37% (634,950 / 658,881) ← başlangıç 95.99%
- **Type coverage**: 70.84% (20,676 / 29,187) ← başlangıç 70.12%
- **Tanınmayan token**: 23,931 (3.63%)
- **Sözlük**: 32,756 giriş
- **Son commit**: `21dbd56` → düzeltmeler uygulandı

---

## 1. KAYIP ANALİZİ — Puan Nerede Gidiyor?

| Kategori | Tür Sayısı | Token Sayısı | % (toplam kayıp) | Açıklama |
|----------|-----------|-------------|-------------------|----------|
| diger | 7,380 | 22,020 | **83.3%** | İngilizce kelimeler (and, services, other) + karmaşık Türkmen morfolojisi |
| fiil_cekimi | 448 | 1,395 | 5.3% | Birleşik fiiller, bazı yanlış sınıflandırılmış özel isimler |
| cok_ekli_isim | 338 | 1,064 | 4.0% | Çok ekli isimler (gazananlaryny, kuwwatlyklaryny) |
| yabanci | 72 | 756 | 2.9% | Yabancı kelimeler (corporation, engineering) |
| yapim_ekli | 214 | 536 | 2.0% | Yapım ekli kelimeler (kiberhowpsuzlyk, umumymilli) |
| ettirgen_edilgen | 219 | 511 | 1.9% | Ettirgen/edilgen (deňeşdirilende, aýdylanda) |
| fiilimsi_zarf | 36 | 98 | 0.4% | Zarf-fiil formları |
| ozel_isim | 9 | 56 | 0.2% | Özel isimler (türkmenistanlylaryň) |
| tireli_bilesik | 4 | 7 | <0.1% | Tireli bileşikler (abş-ly) |
| sira_sayi | 1 | 1 | <0.1% | Sıra sayıları |

### En Sık Tanınmayan Kelimeler (token>30):
- `and` (502), `services` (501), `other` (501) — İngilizce spam → filtrelenebilir
- `şatdyryn` (100) — fiil çekimi → şat+dyr+yn → sözlüğe eklenmeli
- `wekiliýetiniň` (88), `wekiliýeti` (60) — wekiliýet sözlükte yok
- `belleýşi` (63) — bellemek'ten -ýş türevi
- `allatagaladan` (60) — allatagala sözlükte yok
- `garamazdan` (26) — edat, sözlüğe eklenmeli
- `astynda` (39) — aşagynda? ast+ynda, postposition
- `sammite` (47), `sammitine` (38), `sammitiniň` (25) — sammit sözlükte yok

---

## 2. BUG DÜZELTMELER

### 2.1 ✅ G2 (Nämälim Geljek) e→ä Kuralı DÜZELTİLDİ
**Dosya**: `generator.py` tense 7 ve `_compound_base()` (genis)
**Sorun**: `gel + er → gäler` üretiyor ama doğrusu `geler`.  
e→ä dönüşümü G2'de (nämälim geljek) UYGULANMAMALI.  
Bu kural sadece converb (-p) ve muhtemelen başka yerlerde geçerli.  
**Çözüm**: Tense 7 ve `_compound_base(sub="genis")`'ten e→ä satırlarını kaldır.  
**Etki**: Tüm G2 çekimleri düzelir. Compound tense base'leri de düzelir.

### 2.2 ✅ H2 (Anyk Häzirki) Olumsuzluk — "yok" Kuralı EKLENDİ
**Dosya**: `generator.py` tense 5  
**Sorun**: H2 şu an olumsuzluk desteklemiyor. TABLE VIII'e göre H2 "yok" ile analitik olumsuzluk yapıyor.  
**Kural**: `otyryn yok` (oturmuyorum), `duryn yok` (durmuyorum) — fiil + "yok" postposition  
**Çözüm**: Tense 5'e olumsuz mod ekle: `result + " yok"`

### 2.3 ✅ Web morphology.py Converb (tense 13) DÜZELTİLDİ
**Dosya**: `morphology.py` tense 13  
**Sorun**: `_fiil_yumusama()` ve e→ä dönüşümü uygulanmıyor.  
API'deki generator.py'de düzeltildi ama web versiyonunda hâlâ eski kod.  
**Çözüm**: morphology.py tense 13'e fiil yumuşaması ve e→ä ekle.

### 2.4 ✅ Web morphology.py Past Participle (tense 14) DÜZELTİLDİ
**Dosya**: `morphology.py` tense 14  
**Sorun**: `_fiil_yumusama()` uygulanmıyor (eden, giden vb. üretilemiyor).  
API'deki generator.py'de var ama web'de yok.

---

## 3. COPULA MEKANİZMASI

### Mevcut Durum:
- **Generator**: Copula (dyr/dir/dur/dür) sadece NÖ (tense 11) içinde fused suffix olarak kullanılıyor (-ypdyr/-ipdir)
- **Analyzer**: `_COPULA` listesi var, `parse_derived_verb()` ve `parse()` içinde opsiyonel son katman olarak soyuluyor
- **G1 (Mälim Geljek)**: "kopulasız" yazılmış — doğru, G1'de copula yok

### Türkmen'de Copula Nasıl Çalışır:
- Copula (-dIr/-dyr) bir **bildiriş eki**dir, bağımsız fiil çekimi değil
- İsim/sıfat yüklemlerinde kullanılır: `uly+dyr` (büyüktür), `talyp+dyr` (öğrencidir)
- Fiil çekimlerinde: sadece NÖ (nätanyş öten) ve rapor edilmiş formlarda
- Analyzer'da copula katmanı doğru çalışıyor (soyma + altını analiz etme)

### Durum: ✅ Mevcut implementasyon yeterli
Copula analyzer'da opsiyonel son katman olarak doğru çalışıyor.  
Generator'da ise NÖ'de fused form olarak doğru uygulanıyor.

---

## 4. ZAMAN KODLARI TABLOSU (Doğru Eşleştirme)

| Kod | Zaman Adı | Motor Kodu | Durum |
|-----|-----------|------------|-------|
| Ö1 | Anyk Öten | 1 | ✅ |
| Ö2 | Daş Öten | 2 | ✅ |
| Ö3 | Dowamly Öten | 3 | ✅ |
| H1 | Umumy Häzirki | 4 | ✅ |
| H2 | Anyk Häzirki | 5 | ✅ "yok" olumsuzluk eklendi |
| G1 | Mälim Geljek | 6 | ✅ |
| G2 | Nämälim Geljek | 7 | ✅ e→ä kuralı düzeltildi |
| NÖ | Nätanyş Öten | 11 | ✅ |
| Ş1 | Şert | 8 | ✅ |
| B1K | Buýruk | 9 | ✅ |
| HK | Hökmanlyk | 10 | ✅ |
| AÖ | Arzuw-Ökünç | 12 | ✅ |

### Olumsuzluk Stratejileri (TABLE VIII):
| Strateji | Zamanlar | Mekanizma |
|----------|----------|-----------|
| Sentetik | Ö1, H1, Ş1 | kök + -mA/-me + zaman_eki |
| Kaynaşık (fused) | Ö2, G2, NÖ | kök + fused_negation |
| Analitik | Ö3, G1, HK | fiil_formu + "däl" |
| Analitik (yok) | **H2** | fiil_formu + "yok" |

---

## 5. ÜNLÜ DÜŞMESİ (VOWEL ELISION) KURALI 

### Kullanıcının Tarifi:
- İki heceli kök
- Birinci hece açık (ünlü ile bitiyor), ikinci hece kapalı (ünsüzle bitiyor)
- **Dar** ünlü düşer (y, i, u, ü)
- Sadece ünlüyle başlayan eklerden önce
- Kısıtlama: düşen ünlüden önceki ünsüz **yumuşak** ünsüz olmalı (d ve z HARİÇ)

### Mevcut Uygulama:
- Hardcoded liste: `VOWEL_DROP_CANDIDATES` (30 kelime)
- `VOWEL_DROP_EXCEPTIONS` (5 kelime: asyl→asl, pasyl→pasl, nesil→nesl, ylym→ylm, mähir→mähr)
- `apply_vowel_drop()`: sadece listedeki kelimeler için çalışır

### Değerlendirme:
Hardcoded liste pragmatik bir yaklaşım ve corpus'ta iyi çalışıyor.  
Algoritmasal bir kural eklemek isteğe bağlı ama false positive riski var.  
**Durum**: ✅ Yeterli (ihtiyaç duyulursa genişletilebilir)

---

## 6. YUVARLAKLAŞMA UYUMU (ROUNDING HARMONY)

### Mevcut Uygulama:
- `YUVARLAKLASMA_LISTESI`: 3 kelime (guzy→guzu, süri→sürü, guýy→guýu)
- Çokluk eki ve 3. iyelik öncesinde y/i → u/ü dönüşümü
- `_rounding_equivalent()`: Toleranslı karşılaştırma (u↔y, ü↔i)

### Değerlendirme:
**Durum**: ✅ Yeterli — corpus'ta sorun görülmüyor

---

## 7. YAPIM EKLERİ (DERIVATION SUFFIXES)

### Mevcut Desteklenen:
- `-lI` (isimden sıfat: suwly, güýçli)
- `-lIk` (isim/sıfattan isim: dostluk, baýlyk)
- `-sIz` (yokluk: işsiz, howpsuz)
- `-çI` (meslek: işçi, ýolçy)
- `-dAş` (ortaklık: watandaş, ýoldaş)

### Eksik Olan Önemli Ekler:
| Ek | Tür | Örnek | Öncelik |
|----|------|-------|---------|
| `-çIlIk` | İsimden isim | işçilik, dostçylyk | YÜKSEK |
| `-kI` | Yer sıfat | öýdäki, şäherdäki | DÜŞÜK (daky ile kısmen var) |
| `-ncI` | Sıra sayı | birinji, ikinji | VAR (parse'da) |
| `-lA` | İsimden fiil | başla, işle | ORTA (sözlükte fiil olarak) |
| `-lAş` | İsimden fiil | döwrebaplaş | ORTA |
| `-lAn` | İsimden fiil | güýçlen | ORTA |
| `-gI/-gIç` | Fiilden isim | bilgi, kesgiç | DÜŞÜK |
| `-mA` | Fiilden isim | ýaşama, gelme | DÜŞÜK (mastar ile örtüşür) |
| `-Iş` | Fiilden isim | barlaýyş, gidiş | ORTA |

### Aksiyon:
`_DERIVATION` listesine `-çIlIk` ekini ekle (en yüksek ROI).

---

## 8. WEB vs API FARKLARI

### parser.py
✅ Zaten turkmen-fst analyzer'ı kullanıyor. Senkron.

### morphology.py
Sadece **generator** (üretim) tarafında farklar var:
| Fark | Web (morphology.py) | API (generator.py) | Düzeltme |
|------|---------------------|---------------------|----------|
| Converb (t13) fiil yumuşama | ❌ Yok | ✅ Var | Eklenecek |
| Converb (t13) e→ä | ❌ Yok | ✅ Var | Eklenecek |
| Past participle (t14) fiil yumuşama | ❌ Yok | ✅ Var | Eklenecek |
| G2 e→ä | ❌ VAR (yanlış) | ❌ VAR (yanlış) | **İKİSİNDEN DE KALDIRILACAK** |
| H2 yok olumsuzluk | ❌ Yok | ❌ Yok | İkisine de eklenecek |

---

## 9. SÖZLÜK SAĞLIK KONTROLÜ

### Bilinen Sorunlar:
- POS etiketleri genel olarak doğru (n, v, adj, np)
- Bazı kelimeler kök yerine türemiş form olabilir — corpus analiziyle doğrulanmalı
- Eş sesli kelimeler (ES_SESLILER / HOMONYMS) doğru işaretlenmiş

### Sözlüğe Eklenmesi Gereken Kelimeler (yüksek token):
| Kelime | Token | Tür | Not |
|--------|-------|-----|-----|
| wekiliýet | 148+ | n | wekiliýetiniň(88)+wekiliýeti(60) |
| sammit | 110+ | n | sammite+sammitine+sammitiniň |
| allatagala | 60 | n | Tanrı (edat? isim?) |
| ast | 39 | n | astynda (postposition) |
| garamazdan | 26 | post | -e garamazdan (edat) |
| seljeriş | 25 | n | seljermek'ten -Iş |
| bedenterbiýe | 27 | n | bedenterbiýäni |
| port | 24 | n | portunyň |
| durk | 21 | n | durkuny |

---

## 10. YAPILACAKLAR ÖNCELİK SIRASI

1. ✅ **BUG**: G2 e→ä kuralını kaldır (generator.py + morphology.py)
2. ✅ **BUG**: H2 "yok" olumsuzluk ekle (generator.py + morphology.py)
3. ✅ **SYNC**: Web morphology.py converb/participle düzeltmeleri
4. ✅ **DICT**: Yüksek token kelimeler sözlüğe ekle (~58 giriş)
5. ✅ **MOTOR**: `-çIlIk` ve `-Iş` yapım eki desteği
6. ✅ **BUG**: Softening exceptions (24 kelime: -ýet, sammit, ast, port vb.)
7. ✅ **BUG**: Accusative (A4) e→ä dönüşümü eksikti (wezipäni, tejribäni)
8. ✅ **BUG**: Past participle (t14) e→ä dönüşümü eksikti (dörän, gülän)
9. ✅ **DICT**: Eksik özel isimler eklendi (Mämmedow, Halaç, Ahmed vb.)
10. ✅ **TEST**: Full coverage test → 96.37% token, 70.84% type

### Sonraki Adımlar:
- ⬜ Ettirgen/edilgen verb formları analizi (deňeşdirilende, aýdylanda → ~500 token)
- ⬜ Çok ekli isim pattern'leri (gazananlaryny, ynanmagyňyzy → ~800 token)
- ⬜ Compound verb patterns (etjeklerine → ~300 token)
- ⬜ İngilizce kelime filtresi (and, services, other → ~1500 token)

---

*Son güncelleme: 2025-06-08*
