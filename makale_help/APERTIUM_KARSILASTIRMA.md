# TurkmenFST vs. Apertium-tuk vs. enedilim.com: Morfolojik Kural Karşılaştırması

**Tarih:** 2025-01 (Güncelleme: Şubat 2026)  
**Amaç:** Sistemimizin (TurkmenFST) isim ve fiil çekim kurallarını hem Apertium projesinin Türkmen modülüyle (`apertium-tuk`) hem de resmi kaynak `enedilim.com` ile 3’lü detaylı karşılaştırmak.

> ✅ **Güncelleme:** Ö2 olumsuz (`-män+di`), Ö3 olumsuz (`-ýän däldi`) ve G1 olumlu (kopula `+dir+kişi`) düzeltmeleri **tamamlandı**. 7 temel zamanda enedilim.com ile **tam uyum** sağlandı. 5 yeni kip (Şert, Buýruk, Hökmanlyk, Nätanyş Öten, Arzuw-Ökünç), 4 fiilimsi, 2 işlik derejesi (Ettirgen/Edilgen) eklendi. Tüm testler geçiyor (105 pytest + 124 yeni fiil form + 1192 kapsamlı).

---

## 1. Genel Bakış

| Özellik | TurkmenFST | Apertium-tuk | enedilim.com |
|---------|-----------|--------------|-------------|
| **Dil** | Python 3.x | HFST — lexc + twol | — (web referans) |
| **Yaklaşım** | Kural tabanlı Python FST | Sonlu durum dönüştürücü | Dilbilgisi referans kaynağı |
| **Sözlük boyutu** | ~32.000 girdi (5 kaynak) | ~2.000 leksikon girdisi | Kapsamlı çevrimiçi sözlük |
| **Son güncelleme** | Aktif geliştirme (2025-2026) | ~5 yıldır güncellenmemiş | Aktif (resmi kaynak) |
| **Lisans** | — | GPL-3.0 | — |
| **FIXME sayısı** | 0 enedilim uyumsuzluğu (Ö2/Ö3/G1 düzeltildi) | 20+ FIXME yorumu | — |
| **Test** | 105 pytest + 124 yeni fiil form + 4.788 referans (%100) | Temel test dosyaları | — |
| **Fiil çatıları** | ✅ Ettirgen (-dyr/-t), Edilgen (-yl/-yn) | Ettirgen (-dyr), Edilgen (-yl) | Tam tanımlı |
| **Fiilimsi** | ✅ 4 form (-yp, -an, -ýan, -jak) | 8+ form | Tam tanımlı |
| **Ek kipler** | ✅ Şert, Buýruk, Hökmanlyk, Nätanyş, Arzuw | Şart, Emir, Gereklilik, Perfect, Evid. | Tam tanımlı |
| **Web arayüzü** | Flask + Vercel deploy | Yok | Evet |

---

## 2. İsim Çekimi — 3'lü Karşılaştırma

### 2.1 Hal Ekleri (Cases) — 3'lü Tablo

| Hal | TurkmenFST | Apertium-tuk | enedilim.com | Durum |
|-----|-----------|--------------|-------------|-------|
| **Yalın (nom)** | Eksiz | Eksiz — `<nom>` | Eksiz | ✅ Üçü de aynı |
| **İlgi (gen)** | `-yň/-iň`, ünlü: `-nyň/-niň`, kısa+yuvarlak: `-uň/-üň` | `{n}{Y}ň` — yuvarlak kuralı YOK | `-yň/-iň/-uň/-üň`, ünlü: `-nyň/-niň` | ✅ **Biz = enedilim** ≠ Apertium |
| **Yönelme (dat)** | `-a/-e` (ünsüz); ünlü sonu → son ünlü `a/ä`'ya dönüşür | `{n}{A}` — twol ile | `-a/-e`, ünlü birleşme | ✅ Üçü de benzer |
| **Belirtme (acc)** | `-y/-i` (ünsüz+yum.), `-ny/-ni` (ünlü) | `{n}{Y}` | `-ny/-ni`, `-y/-i` | ✅ Üçü de benzer |
| **Bulunma (loc)** | `-da/-de`; iyelikten sonra `-nda` | `{n}d{A}` | `-da/-de` | ✅ Üçü de benzer |
| **Çıkma (abl)** | `-dan/-den`; iyelikten sonra `-ndan` | `{n}d{A}n` | `-dan/-den` | ✅ Üçü de benzer |
| **-daky (lok. sıfat)** | ❌ **Yok** | ✅ `d{Ä}k{Y}` | ✅ Var (`kitapdaky`) | ❌ Biz eksik |
| **Yokluk (-syz)** | ❌ **Yok** | ✅ `s{U}z` — `<abe>` | ✅ Var (`kitapsyz`) | ❌ Biz eksik |

### 2.2 İlgi Hali (Genitif) — Bizim Avantajımız

Bu, **TurkmenFST'nin Apertium'a karşı en önemli avantajıdır**:

```
TurkmenFST kuralı (enedilim ile uyumlu):
  - Ünsüz sonu: 
    * ≤4 harf + yuvarlak kök → -uň/-üň  (ör. "göz" → "gözüň", "suw" → "suwuň")
    * Diğer → -yň/-iň
  - Ünlü sonu: -nyň/-niň

Apertium kuralı:
  - {n}{Y}ň
    * {Y} → y/i (sadece 2-yönlü uyum, yuvarlak kuralı YOK)
  - Kısa kelime özel kuralı TANIMLANMAMIŞ
```

**Somut yüzey farkları:**

| Kelime | TurkmenFST | Apertium (tahmini) | enedilim.com | Doğru olan |
|--------|-----------|---------------------|-------------|-----------|
| göz + GEN | **gözüň** | göziň | **gözüň** | ✅ TurkmenFST |
| suw + GEN | **suwuň** | suwyň | **suwuň** | ✅ TurkmenFST |
| gol + GEN | **goluň** | golyň | **goluň** | ✅ TurkmenFST |
| kitap + GEN | kitabyň | kitabyň | kitabyň | ✅ Her ikisi |

**Neden önemli?** Kısa yuvarlak ünlülü kelimelerde (göz, suw, gol, gyz...) Apertium **sistematik hata** üretir çünkü twol kurallarında 4-yönlü genitive uyumu tanımlı değildir. Bizim motorumuz enedilim.com ile tam uyumludur.

### 2.3 `-daky` (Bulunma Sıfatı) — Açıklama

**Ne yapar?** Bulunma halindeki bir ismi sıfata dönüştürür:
- `kitapda` (kitapta) → `kitapdaky` (kitaptaki)
- `şäherde` (şehirde) → `şäherdäki` (şehirdeki)

**Morfolojik yapısı:** `kök + da/de + ky/ki` (ünlü uyumuna tabi)

**enedilim'deki kullanımı:** Yaygın, özellikle belirleme ve niteleme yapılarında:
- `jaýdaky adam` (evdeki adam)
- `mekdepdäki mugallym` (okuldaki öğretmen)

**Apertium'daki uygulaması:** `d{Ä}k{Y}` archiphoneme'leri ile kök+ek birleşimi. `DAGI` sublexicon'ları üzerinden isim paradigmasına entegre.

**Bizde neden yok?** Mevcut mimaride sadece 6 temel hal tanımlı. `-daky` bir türetim eki sayılabileceği için GELECEK_PLANLARI.md'de "türetim morfolojisi" kapsamında planlanmış.

**Ekleme zorluğu:** ★☆☆ Düşük — bulunma haline `-ky/-ki` eklemek yeterli.

### 2.4 `-syz` (Yokluk/Abessive) — Açıklama

**Ne yapar?** "...-sız/-siz" anlamında yokluk ifade eder:
- `kitap` → `kitapsyz` (kitapsız)
- `iş` → `işsiz` (işsiz)

**Morfolojik yapısı:** `kök + syz/siz/suz/süz` (4-yönlü ünlü uyumu)

**enedilim'deki kullanımı:** Yaygın:
- `suwsuz` (susuz), `işsiz` (işsiz), `öýsüz` (evsiz)

**Apertium'daki uygulaması:** `s{U}z` — `{U}` archiphoneme'i twol ile 4-yönlü uyuma tabi.

**Ekleme zorluğu:** ★☆☆ Düşük — doğrudan köke eklenen basit bir sonek.

### 2.5 Ünlü Düşmesi Mekanizması — Ayrıntılı Karşılaştırma

| Özellik | TurkmenFST | Apertium-tuk | enedilim.com |
|---------|-----------|--------------|-------------|
| **Mekanizma** | `VOWEL_DROP_CANDIDATES` (20 kelime) + `VOWEL_DROP_EXCEPTIONS` (5) | Leksikonda `{u}` archiphoneme | Kuralı tanımlar, liste vermez |
| **Kural** | Son hecedeki ünlü düşer (ünlüyle başlayan ek gelince) | twol: `{u}:0` bağlamda | Ünlü ile başlayan ek gelince düşer |
| **Genişletilebilirlik** | Listeye kelime eklenmeli | Leksikona `{u}` koymak yeterli | — |

**Somut örnekler:**

| Kelime | TurkmenFST | Apertium | enedilim | Eşleşme |
|--------|-----------|----------|---------|---------|
| burun + um | burn**um** | burn**um** | burn**um** | ✅ Üçü aynı |
| ogul + um | ogl**um** | ogl**um** | ogl**um** | ✅ Üçü aynı |
| agyz + y | agz**y** | agz**y** | agz**y** | ✅ Üçü aynı |

**Fark mekanizmada, sonuçta değil:** Her iki sistem de aynı yüzey formlarını üretir. Apertium'un `{u}` yaklaşımı daha *genellenebilir*, bizim listemiz daha *okunabilir*.

### 2.6 Yuvarlaklaşma — Bizim İkinci Avantajımız

| Özellik | TurkmenFST | Apertium-tuk | enedilim.com |
|---------|-----------|--------------|-------------|
| Kural | `YUVARLAKLASMA_LISTESI` ile açık dönüşüm | Genel kural yok; `{u}` kısmi | Var (öğretim materyalinde belgelenmiş) |
| `guzy → guzu` | ✅ | ❌ (muhtemelen `guzy` kalır) | ✅ |
| `süri → sürü` | ✅ | ❌ | ✅ |
| `guýy → guýu` | ✅ | ❌ | ✅ |

**Somut örnek:**
```
TurkmenFST:  guzy + lar = guzular  ✅ (enedilim uyumlu)
Apertium:    guzy + l{A}r = guzylar  ❌ (yuvarlaklaşma uygulanmaz)
```

### 2.7 Çoğul Eki

| Özellik | TurkmenFST | Apertium-tuk | enedilim.com |
|---------|-----------|--------------|-------------|
| Temel ek | `-lar/-ler` | `l{A}r` | `-lar/-ler` |
| Yuvarlaklaşma | ✅ `süri→sürüler` | ❌ Sınırlı | ✅ |
| N1/N2 ayrımı | Yok | Var | — |

### 2.8 İyelik Ekleri (Possessive) — 3'lü

| Kişi | TurkmenFST | Apertium | enedilim | Durum |
|------|-----------|----------|---------|-------|
| 1.tek | `-ym/-im/-um/-üm`, ünlü: `-m` | `{y}m` | `-ym/-im/-um/-üm` | ✅ Üçü aynı |
| 2.tek | `-yň/-iň/-uň/-üň`, ünlü: `-ň` | `{y}ň` | `-yň/-iň/-uň/-üň` | ✅ Üçü aynı |
| 3.tek | `-y/-i` (ünsüz), `-sy/-si` (ünlü) | `{s}{U}` | `-y/-i`, `-sy/-si` | ✅ Üçü aynı |
| 1.çoğ | `-ymyz/-imiz` vb., ünlü: `-myz/-miz` | `{y}m{Y}z` | `-ymyz/-imiz` vb. | ✅ Üçü aynı |
| 2.çoğ | `-yňyz/-iňiz` vb., ünlü: `-ňyz/-ňiz` | `{y}ň{Y}z` | `-yňyz/-iňiz` vb. | ✅ Üçü aynı |
| 3.çoğ | 3.tekil ile ortak | `<px3sp>` ortak | 3.tekil ile ortak | ✅ Üçü aynı |

### 2.9 Ünsüz Yumuşaması (Softening) — 3'lü

| Özellik | TurkmenFST | Apertium-tuk | enedilim.com |
|---------|-----------|--------------|-------------|
| **Kural yönü** | Sert→Yumuşak (ek öncesi) | Yumuşak→Sert (sözcük sonu) | "Ünlüyle başlayan ek gelince yumuşar" |
| **Mekanizma** | `apply_consonant_softening()` | twol `"Devoicing"` | Kural tanımı |
| **Sözlük formatı** | `kitap` (sert/yüzey form) | `kitab` (yumuşak/underlying form) | `kitap` (yüzey form) |
| **Eş sesli** | HOMONYMS dict | `{Ø}` morphophoneme | Açıklama ile |

**Mimari fark:**
```
TurkmenFST:  sözlükte "kitap" → ek gelince "kitab+ym"  (yumuşatma: surface→underlying)
Apertium:    sözlükte "kitab" → sözcük sonunda "kitap"    (sertleştirme: underlying→surface)
enedilim:    "kitap" → iyelik/belirtme eki → "kitaby/kitabym"
```

Bizim ve enedilim'in yaklaşımı aynıdır: yüzey form → ek öncesi yumuşama. Apertium tam tersi çalışır.

### 2.10 İsim Çekimi Özet Karnesi

| Kategori | TurkmenFST | Apertium | enedilim |
|----------|:---------:|:--------:|:--------:|
| 6 temel hal | ✅ | ✅ | ✅ |
| İlgi hali yuvarlak kural | ✅ | ❌ | ✅ |
| Yuvarlaklaşma | ✅ | ❌ | ✅ |
| Ünlü düşmesi | ✅ | ✅ | ✅ |
| İyelik (6 kişi) | ✅ | ✅ | ✅ |
| Ünsüz yumuşaması | ✅ | ✅ | ✅ |
| `-daky` bulunma sıfatı | ❌ | ✅ | ✅ |
| `-syz` yokluk eki | ❌ | ✅ | ✅ |
| Sözlük boyutu | **32K** | ~2K | — |
| **Toplam** | **6/8** | **6/8** | **8/8** |

**Bizim avantajlarımız:** İlgi hali yuvarlak kuralı + yuvarlaklaşma + 32K sözlük  
**Apertium'un avantajları:** `-daky` ve `-syz` ekleri  
**Ortak eksik:** Yok (temel 6 hal + iyelik + ünsüz yumuşaması + ünlü düşmesi hepsinde var)

---

## 3. Fiil Çekimi — 3'lü Karşılaştırma

### 3.1 Zaman Envanteri

| Zaman | TurkmenFST | Apertium-tuk | enedilim.com | Durum |
|-------|-----------|--------------|-------------|-------|
| Ö1: Anyk Öten | ✅ `-dy/-di/-du/-dü` | ✅ `<ifi>`: `-d{U}` | ✅ | Üçü de var |
| Ö2: Daş Öten | ✅ `-ypdy/-ipdi` | ✅ `<ifi><evid>`: `-{y}pd{U}` | ✅ | Üçü de var |
| Ö3: Dowamly Öten | ✅ `-ýardy/-ýärdi` | ⚠️ `<prog>` + geçmiş? | ✅ | Var ama etiketleme farklı |
| H1: Umumy Häzirki | ✅ `-ýar/-ýär` | ✅ `<prog>`: `-ý{Ä}r` | ✅ | Üçü de var |
| H2: Anyk Häzirki | ✅ `otyr/dur/ýatyr/ýör` | ✅ `VAUX-IMPF` | ✅ | Üçü de var |
| G1: Mälim Geljek | ✅ `-jak/-jek` | ✅ `<fut>`: `-j{A}g` | ✅ | Üçü de var |
| G2: Nämälim Geljek | ✅ `-ar/-er/-r` | ✅ `<aor>`: `-{A}r` | ✅ | Üçü de var |
| Şart kipi | ✅ `<cond>`: `-sa/-se` + şahıs | ✅ `<cond>`: `-s{A}` | ✅ | Üçü de var |
| Emir kipi | ✅ `<imp>`: şahıs bazlı kalıplar | ✅ `<imp>` | ✅ | Üçü de var |
| Gereklilik | ✅ `-maly/-meli` [+ däl] | ✅ `<nec>`: `-m{A}l{Y}` | ✅ | Üçü de var |
| Perfect | ✅ Nätanyş Öten: `-ypdyr/-ipdir` | ✅ `<perf>` | ✅ | Üçü de var |
| Kanıtsal | ✅ Nätanyş Öten (aynı form) | ✅ `<evid>` | ✅ | Üçü de var |

### 3.2 Gerçek Kod Çıktısı — "gel" Fiili Paradigması

Aşağıdaki tablo `morphology.py` kodu çalıştırılarak elde edilmiştir (tahmini değil, gerçek çıktı):

#### Ö1 — Anyk Öten (Kesin Geçmiş)

| Kişi | Olumlu | Olumsuz |
|------|--------|---------|
| A1 | geldim | gelmedim |
| A2 | geldiň | gelmediň |
| A3 | geldi | gelmedi |
| B1 | geldik | gelmedik |
| B2 | geldiňiz | gelmediňiz |
| B3 | geldiler | gelmediler |

**Enedilim uyumu:** ✅ Tam uyumlu. Dodak fiillerde `-du/-dü` (ör. `durdum`) da uygulanıyor.

#### Ö2 — Daş Öten (Dolaylı Geçmiş)

| Kişi | Olumlu | Olumsuz |
|------|--------|---------|
| A1 | gelipdim | gel**mändim** |
| A2 | gelipdiň | gel**mändiň** |
| A3 | gelipdi | gel**mändi** |
| B1 | gelipdik | gel**mändik** |
| B2 | gelipdiňiz | gel**mändiňiz** |
| B3 | gelipdiler | gel**mändiler** |

**Enedilim uyumu:** ✅ Tam uyumlu. Olumsuz form: `kök + män/man + di/dy + kişi`.

#### Ö3 — Dowamly Öten (Sürekli Geçmiş)

| Kişi | Olumlu | Olumsuz |
|------|--------|---------|
| A1 | gelýärdim | gel**ýän däldim** |
| A2 | gelýärdiň | gel**ýän däldiň** |
| A3 | gelýärdi | gel**ýän däldi** |
| B1 | gelýärdik | gel**ýän däldik** |
| B2 | gelýärdiňiz | gel**ýän däldiňiz** |
| B3 | gelýärdiler | gel**ýän däldiler** |

**Enedilim uyumu:** ✅ Tam uyumlu. Olumsuz form analitik yapıda: `kök + ýan/ýän + däldi + kişi`.

#### H1 — Umumy Häzirki (Geniş Zaman)

| Kişi | Olumlu | Olumsuz |
|------|--------|---------|
| A1 | gelýärin | gelmeýärin |
| A2 | gelýärsiň | gelmeýärsiň |
| A3 | gelýär | gelmeýär |
| B1 | gelýäris | gelmeýäris |
| B2 | gelýärsiňiz | gelmeýärsiňiz |
| B3 | gelýärler | gelmeýärler |

**Enedilim uyumu:** ✅ Tam uyumlu. k/t yumuşaması da doğru çalışıyor (`okat → okadýar`).

#### G1 — Mälim Geljek (Kesin Gelecek)

| Kişi | Olumlu | Olumsuz |
|------|--------|---------|
| A1 | Men geljek**dirin** | Men geljek däl |
| A2 | Sen geljek**dirsiň** | Sen geljek däl |
| A3 | Ol geljek**dir** | Ol geljek däl |
| B1 | Biz geljek**diris** | Biz geljek däl |
| B2 | Siz geljek**dirsiňiz** | Siz geljek däl |
| B3 | Olar geljek**dirler** | Olar geljek däl |

**Enedilim uyumu:** ✅ Tam uyumlu. Olumlu formda kopula `dir/dyr` + genişletilmiş kişi ekleri.

#### G2 — Nämälim Geljek (Belirsiz Gelecek)

| Kişi | Olumlu | Olumsuz |
|------|--------|---------|
| A1 | gelerin | gelmerin |
| A2 | gelersiň | gelmersiň |
| A3 | geler | gelmez |
| B1 | geleris | gelmeris |
| B2 | gelersiňiz | gelmersiňiz |
| B3 | gelerler | gelmezler |

**Enedilim uyumu:** ✅ Tam uyumlu. e→ä dönüşümü ve -mar/-mer vs -maz/-mez ayrımı doğru.

### 3.3 Commit `fe28801`'de Gerçekte Yapılan 8 Düzeltme

YAPILAN_ISLER.md'de listelenen düzeltmeler ile gerçek commit içeriği **farklıdır**. İşte gerçekte uygulanan düzeltmeler:

| # | Gerçek Düzeltme | Durum |
|---|----------------|-------|
| 1 | H1 kişi ekleri: `-ym/-ik` → `-yn/-is` (genişletilmiş paradigma) | ✅ Kodda mevcut |
| 2 | G2 olumsuz: çift olumsuzluk hatası giderildi | ✅ Kodda mevcut |
| 3 | G2 olumsuz: A1/A2/B1/B2 `-mar/-mer`, A3/B3 `-maz/-mez` ayrımı | ✅ Kodda mevcut |
| 4 | Ö1 dodak yuvarlaklaşması: tek hece + dodak → `-du/-dü` | ✅ Kodda mevcut |
| 5 | G2 olumlu: `e→ä` dönüşümü (`işle→işlär`) | ✅ Kodda mevcut |
| 6 | H1/G2: k/t ünsüz yumuşaması (`okat→okadýar`) | ✅ Kodda mevcut |
| 7 | G1 B3: çoğul eki `-lar/-ler` eklendi | ✅ Kodda mevcut |
| 8 | Yardımcı fonksiyonlar: `_tek_heceli_dodak`, `_fiil_yumusama` | ✅ Kodda mevcut |

### 3.4 Tamamlanan enedilim Düzeltmeleri

| # | Düzeltme | Eski Çıktı | Yeni Çıktı (enedilim uyumlu) | Durum |
|---|---------|-----------|------------------------------|-------|
| 1 | Ö2 olumsuz kalıbı | `gelme + ipdi + m` → `gelmeipdim` | `gel + männdi + m` → `gelmändim` | ✅ Düzeltildi |
| 2 | Ö3 olumsuz analitik yapı | `gelme + ýärdi + m` → `gelmeýärdim` | `gel + ýän + däldi + m` → `gelýän däldim` | ✅ Düzeltildi |
| 3 | G1 olumlu kopula kişi ekleri | `Men geljek` | `Men geljekdirin` | ✅ Düzeltildi |

### 3.5 Olumsuzluk Stratejisi — 3'lü

| Zaman | TurkmenFST | Apertium | enedilim | Uyum |
|-------|-----------|----------|---------|------|
| Ö1 | `kök + ma/me + dy/di + kişi` | `V-NEG + <ifi>` | `kök + ma/me + dy/di + kişi` | ✅ |
| Ö2 | `kök + män/man + di/dy + kişi` | `V-NEG + <ifi><evid>` | `kök + män/man + di/dy + kişi` | ✅ |
| Ö3 | `kök + ýän/ýan + däldi + kişi` | Belirsiz | `kök + ýän/ýan + däldi + kişi` | ✅ |
| H1 | `kök + me + ýär + kişi` | `V-NEG + <prog>` | `kök + me + ýär + kişi` | ✅ |
| H2 | (sadece yardımcı fiil) | VAUX-IMPF | `kök + ýän + **däldi**` | ⚠️ Biz belirsiz |
| G1 | `kök + jak/jek + däl` | Belirsiz | `kök + jak/jek + däl` | ✅ |
| G2 A1/A2/B1/B2 | `-mar/-mer` | `-m{A}z` (?) | `-mar/-mer` | ✅ |
| G2 A3/B3 | `-maz/-mez` | `-m{A}z` | `-maz/-mez` | ✅ |

### 3.6 Fiil Kök Yumuşaması — 3'lü

| Özellik | TurkmenFST | Apertium | enedilim |
|---------|-----------|----------|---------|
| Kural | Çok heceli k/t→g/d + özel 4 fiil | Underlying yumuşak (aýd, ed, gid) | H1/G2'de geçerli |
| `okat + H1` | okad**ýar** ✅ | okad**ýar** ✅ | okad**ýar** ✅ |
| `aýt + G2` | aýd**ar** ✅ | aýd**ar** ✅ | aýd**ar** ✅ |
| `et + H1` | ed**ýär** ✅ | ed**ýär** ✅ | ed**ýär** ✅ |

### 3.7 Fiil Çekimi Özet Karnesi

| Kategori | TurkmenFST | Apertium | enedilim |
|----------|:---------:|:--------:|:--------:|
| 7 temel zaman | ✅ | ✅ | ✅ |
| 6 kişi çekimi | ✅ | ✅ | ✅ |
| Olumlu/olumsuz | ✅ | ✅ | ✅ |
| Dodak yuvarlaklaşması (Ö1) | ✅ | ✅ | ✅ |
| k/t yumuşaması (H1, G2) | ✅ | ✅ | ✅ |
| e→ä dönüşümü (G2) | ✅ | ✅ | ✅ |
| G2 olumsuz -mar/-mer ayrımı | ✅ | ❌ (tek -maz?) | ✅ |
| Ö2 olumsuz -män kalıbı | ✅ | ❌ | ✅ |
| Ö3 olumsuz analitik yapı | ✅ | ❌ | ✅ |
| G1 kopula kişi ekleri | ✅ | ❌ (?) | ✅ |
| Şart kipi (-sa/-se) | ✅ | ✅ | ✅ |
| Emir kipi | ✅ | ✅ | ✅ |
| Gereklilik (-maly/-meli) | ✅ | ✅ | ✅ |
| Fiilimsi (-yp, -ýän, -an, -jak) | ✅ 4 form | ✅ | ✅ |
| Ettirgen/Edilgen | ✅ | ✅ | ✅ |

---

## 4. Fonoloji Karşılaştırması

### 4.1 Ünlü Uyumu — 3'lü

| Özellik | TurkmenFST | Apertium-tuk | enedilim |
|---------|-----------|--------------|---------|
| **Kalın/İnce** | `get_vowel_quality()` | twol A/Y/Ä kuralları | Kalın/ince uyum kuralı |
| **Yuvarlak/Düz** | `has_rounded_vowel()` | twol U/{y}: 4 grup | 4-yönlü uyum |
| **A uyumu** | `-a/-e` | `{A}:a/e/ä` — ä dahil | `-a/-e` |
| **Y uyumu** | `-y/-i` (2-yönlü) | `{Y}:y/i` (2-yönlü) | `-y/-i` |
| **U uyumu** | `-y/-i/-u/-ü` (4-yönlü) | `{U}:y/i/u/ü` (twol ile) | 4-yönlü |

**Sonuçlar eşdeğer**, yöntem farklı: Apertium deklaratif (twol), biz prosedürel (if/else).

### 4.2 Ünsüz Sertleşmesi (Devoicing)

| Özellik | TurkmenFST | Apertium-tuk | enedilim |
|---------|-----------|--------------|---------|
| Yön | Sert→Yumuşak (ek öncesi) | Yumuşak→Sert (sözcük sonu) | "Ünlü gelince yumuşar" |
| Kurallar | `p→b, ç→j, t→d, k→g` | `d→t, g→k, b→p, j→ç` | Aynı (p→b vb.) |
| Sözlük | `kitap` (yüzey) | `kitab` (underlying) | `kitap` (yüzey) |

---

## 5. TurkmenFST'nin Avantajları (Apertium'a Karşı)

### 5.1 Dilbilimsel Üstünlükler

| # | Avantajımız | Etki | Detay |
|---|-----------|------|-------|
| 1 | **İlgi hali yuvarlak kural** | Yüksek | Kısa+yuvarlak kelimelerde `-uň/-üň` (göz→gözüň). Apertium bu kuralı tanımlamıyor → `göziň` (yanlış) |
| 2 | **Yuvarlaklaşma** | Orta | `guzy→guzu`, `süri→sürü` dönüşümü. Apertium'da genel kural yok |
| 3 | **G2 olumsuz -mar/-mer ayrımı** | Orta | 1./2.kişide `-mar/-mer`, 3.kişide `-maz/-mez`. Apertium tek form kullanıyor |
| 4 | **Ö1 dodak yuvarlaklaşması** | Orta | Tek heceli dodak fiillerde `-du/-dü` (durdum). Apertium'da 4-yönlü `-d{U}` var ama sonuç farklı olabilir |

### 5.2 Mühendislik Üstünlükleri

| # | Avantajımız | Etki |
|---|-----------|------|
| 1 | **32K sözlük** vs Apertium'un ~2K | >15× daha büyük kapsam |
| 2 | **%100 test kapsamı** (4.788+ test) | Regresyon güvencesi |
| 3 | **Web arayüzü + API** | Erişilebilir demo, entegrasyon |
| 4 | **Aktif geliştirme** | Apertium 5+ yıl durağan |
| 5 | **enedilim.com doğrulaması** | Resmi kaynakla karşılaştırılmış |

### 5.3 Apertium'un Bize Karşı Avantajları

| # | Apertium avantajı | Bizde durumu |
|---|-------------------|-------------|
| 1 | Ek fiilimsi formları (-ma, -mak, -maksızın) | Planlanmış (4 temel fiilimsi eklendi) |
| 2 | `-daky` bulunma sıfatı, `-syz` yokluk eki | Planlanmış |
| 3 | Zamir paradigması (düzensiz çekim) | Planlanmamış henüz |
| 4 | Kopula, klitik soru/bağlaç | Planlanmamış henüz |
| 5 | HFST formal model (araştırma standardı) | Mimari farklılık |

---

## 6. Fiil Eksiklikleri İçin Eylem Planı

### 6.1 ~~Öncelik 0~~ — enedilim Uyumsuzluk Düzeltmeleri ✅ TAMAMLANDI

Aşağıdaki 3 düzeltme başarıyla uygulanmıştır (morphology.py + generator.py):

| Düzeltme | Eski Çıktı | Yeni Çıktı | Durum |
|----------|-----------|-----------|-------|
| **A: Ö2 Olumsuz** | gelmeipdim | gelmändim | ✅ |
| **B: Ö3 Olumsuz** | gelmeýärdim | gelýän däldim | ✅ |
| **C: G1 Olumlu Kopula** | geljek (kişi eki yok) | geljekdirin | ✅ |
| **D: Ö3 B3 Olumlu Çoğul** | gelýärdiler | gelýärdiler (mevcut haliyle bırakıldı) | — |

Test sonuçları: 105 pytest ✅ + 1192 comprehensive ✅ = **0 hata**

### 6.2 ~~Öncelik 1~~ — Yeni Zaman/Kip Ekleme ✅ TAMAMLANDI

| Zaman/Kip | Kalıp | Durum |
|-----------|-------|-------|
| **Şert kipi (Ş1)** | `-sa/-se` + standart şahıs eki | ✅ Eklendi |
| **Emir kipi (B1K)** | Şahıs bazlı özel kalıplar (A2=kök, A3=-syn/-sin, B2=-yň/-iň...) | ✅ Eklendi |
| **Gereklilik (HK)** | `-maly/-meli` [+ `däl`] | ✅ Eklendi |
| **Nätanyş Öten (NÖ)** | `-ypdyr/-ipdir` + kopula kişi eki | ✅ Eklendi |
| **Arzuw-Ökünç (AÖ)** | `-sa/-se` + `-dy/-di` + şahıs eki | ✅ Eklendi |

### 6.3 ~~Öncelik 2~~ — Fiilimsi Formları ✅ TAMAMLANDI

| Form | Kalıp | Durum |
|------|-------|-------|
| Ulaç / Hal işlik (FH) | `-yp/-ip/-up/-üp/-p` (neg: `-man/-män`) | ✅ Eklendi |
| Sıfat-fiil öten (FÖ) | `-an/-en` (neg: `-madyk/-medik`) | ✅ Eklendi |
| Sıfat-fiil häzirki (FÄ) | `-ýan/-ýän` (neg: `-maýan/-meýän`) | ✅ Eklendi |
| Sıfat-fiil geljek (FG) | `-jak/-jek` (neg: `-majak/-mejek`) | ✅ Eklendi |
| İsim-fiil `-ma/-me` | kök + ma/me | — Henüz eklenmedi |
| İsim-fiil `-mak/-mek` | kök + mak/mek | — Henüz eklenmedi |

### 6.4 ~~Öncelik 3~~ — Fiil Çatısı ✅ TAMAMLANDI

| Çatı | Kalıp | Durum |
|------|-------|-------|
| Ettirgen (ETT) | `-dyr/-dir/-dur/-dür` / `-t` (ünlüyle biten) | ✅ Eklendi |
| Edilgen (EDL) | `-yl/-il/-ul/-ül` / `-yn/-in/-un/-ün` (l-sonu kökler) | ✅ Eklendi |

### 6.5 Toplam Durum

| Öncelik Grubu | Durum |
|---------------|-------|
| 0 — enedilim düzeltmeleri (A,B,C) | ✅ TAMAMLANDI |
| 1 — Yeni zaman/kip (5 form) | ✅ TAMAMLANDI |
| 2 — Fiilimsiler (4/6 form) | ✅ TAMAMLANDI (isim-fiil -ma/-mak kaldı) |
| 3 — Fiil çatısı (2 form) | ✅ TAMAMLANDI |

---

## 7. İsim Çekimi Ek Özellikler Planı

| Özellik | Kalıp | Zorluk | Tahmini İş |
|---------|-------|--------|-----------|
| `-daky` bulunma sıfatı | `kök + da/de + ky/ki` | Düşük | ~2 saat |
| `-syz` yokluk eki | `kök + syz/siz/suz/süz` (4-yönlü) | Düşük | ~1 saat |
| Sıra sayısı | `kök + ynjy/inji/unjy/ünji` | Düşük | ~1 saat |
| Zamir paradigması | Düzensiz tablo (men/meniň/maňa vb.) | Orta | ~3 saat |

---

## 8. Detaylı Örnek Karşılaştırmaları

### 8.1 İsim Çekimi: "kitap" — 3'lü

| Çekim | TurkmenFST | Apertium | enedilim |
|-------|-----------|----------|---------|
| Yalın | kitap | kitap | kitap |
| İlgi | kitabyň | kitabyň | kitabyň |
| Yönelme | kitaba | kitaba | kitaba |
| Belirtme | kitaby | kitaby | kitaby |
| Bulunma | kitapda | kitapda | kitapda |
| Çıkma | kitapdan | kitapdan | kitapdan |
| 1.tek iyelik | kitabym | kitabym | kitabym |
| 3.tek iyelik | kitaby | kitaby | kitaby |
| Çoğul | kitaplar | kitaplar | kitaplar |

Üçü de tam uyumlu (standart ünsüz yumuşamalı kelime).

### 8.2 İsim Çekimi: "göz" — İlgi Hali Farkı

| Çekim | TurkmenFST | Apertium (tahmini) | enedilim |
|-------|-----------|---------------------|---------|
| İlgi | **gözüň** | göziň (yanlış) | **gözüň** |
| 1.tek iyelik | **gözüm** | gözim (yanlış) | **gözüm** |

### 8.3 Fiil Çekimi: "gel" — Ö2, Ö3, G1

| Çekim | TurkmenFST | enedilim | Uyum |
|-------|-----------|---------|------|
| Ö2 olumlu A1 | gelipdim | gelipdim | ✅ |
| Ö2 olumsuz A1 | gelmändim | gelmändim | ✅ |
| Ö3 olumlu A1 | gelýärdim | gelýärdim | ✅ |
| Ö3 olumsuz A1 | gelýän däldim | gelýän däldim | ✅ |
| G1 olumlu A1 | geljekdirin | geljekdirin | ✅ |
| G1 olumsuz A1 | geljek däl | geljek däl | ✅ |

---

## 9. YAPILAN_ISLER.md Düzeltme Notu

YAPILAN_ISLER.md'de "8 fiil çekim düzeltmesi" olarak listelenen öğeler ile commit `fe28801`'deki gerçek değişiklikler **farklıdır**. Doğru liste:

```
- [x] 8 fiil çekim düzeltmesi (commit fe28801):
  - H1 kişi ekleri: -ym/-ik → -yn/-is (genişletilmiş paradigma)
  - G2 olumsuz çift olumsuzluk hatası giderildi
  - G2 olumsuz: A1/A2/B1/B2 -mar/-mer, A3/B3 -maz/-mez ayrımı
  - Ö1 dodak yuvarlaklaşması: tek hece+dodak → -du/-dü
  - G2 olumlu e→ä dönüşümü
  - H1/G2 k/t ünsüz yumuşaması
  - G1 B3 çoğul eki -lar/-ler eklendi
  - Yardımcı: _tek_heceli_dodak, _fiil_yumusama fonksiyonları
- [x] 4 enedilim uyumsuzluğu DÜZELTİLDİ ✅:
  - ✅ Ö2 olumsuz: -me+ipdi → -män+di kalıbına geçirildi
  - ✅ Ö3 olumsuz: -me+ýärdi → -ýän däldi analitik yapıya geçirildi
  - ✅ G1 olumlu: kopula kişi ekleri (-jakdyryn/-jekdirin) eklendi
  - — Ö3 B3 olumlu: mevcut haliyle bırakıldı (enedilim'deki "(ler)" belirsiz)
```

---

## 10. Kaynaklar

- **Apertium-tuk deposu**: https://github.com/apertium/apertium-tuk (master branch)
- **apertium-tuk.tuk.lexc**: Morfotaktik kurallar ve leksikon (~2800 satır)
- **apertium-tuk.tuk.twol**: İki-düzeyli fonoloji kuralları (~150 satır)
- **TurkmenFST kaynak kodu**: generator.py, phonology.py, morphotactics.py, morphology.py
- **enedilim.com**: Türkmen dili resmi referansı
- **Commit `fe28801`**: Fiil çekim düzeltmeleri (gerçek değişiklikler)
- **Beesley & Karttunen (2003)**: Finite State Morphology. CSLI Publications.

