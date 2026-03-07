# TurkmenFST — Geliştirme Notları ve Planlar

> Son güncelleme: 25 Şubat 2026

---

## 1. Proje Özeti

TurkmenFST, Türkmen Türkçesi için modüler bir morfolojik analiz ve sentez (üretim) motorudur. FST (Finite-State Transducer) mimarisinden ilham alınmış olup, Python ile geliştirilmiştir.

**Temel Yetenekler:**
- İsim çekimi: 6 hal × 6 iyelik × 2 çoğul = tam paradigma üretimi
- Fiil çekimi: 7 zaman × 6 şahıs × olumlu/olumsuz = 84 çekim formu
- Morfolojik analiz (çekimli kelime → kök + ek ayrıştırma)
- 54.000+ kelimelik zenginleştirilmiş sözlük
- REST API + Web arayüzü + CLI

---

## 2. Sohbet Kronolojisi

### Faz 1: Hunspell Sözlük İthalatı (Önceki Oturum)

- Hunspell `.dic` dosyasından kelimeler ithal edildi
- Sözlük: 1.733 → 38.480 kelimeye çıktı
- 109 fiil kökü düzeltildi (`-mak`/`-mek` → saf kök: `almak` → `al`)
- FLAG num sistemiyle AF alias bayrakları kullanıldı
- Tüm 105 test başarılı

### Faz 2: Türetilmiş Fiil Analizi

**Soru:** Sözlükteki fiillerin çoğu aynı kökten mi geliyor? (`bukul`, `bukuş`, `bukuldyr`, `bukuber` → hepsi `buk` kökünden)

**Bulgular:**
- 20.719 toplam fiil → 12.898 temel kök + 7.821 türetilmiş form
- Türetilmiş formlar Hunspell grupları /21 (5.496) ve /26'da (4.904) yoğunlaştı
- 10.277 benzersiz kök grubu, 10.442 form silinebilir (sadece kökler kalsa)

**Karar:** Şimdilik türetilmiş formlar kalsın. Analyzer henüz türetim zincirlerini çözmüyor, silmek analizi bozar.

### Faz 3: İsim Türetim Analizi

**Soru:** İsimlerde de türetim sorunu var mı?

**Bulgular:**
- 15.089 isim → 12.668 temel + 2.421 türetilmiş (sadece %16)
- Fiillerdeki %50'lik oran ile karşılaştırılınca sorun değil and

**Karar:** İsimlerde müdahaleye gerek yok.

### Faz 4: turkmence_sozluk_tum.txt Analizi

**Durum:** 111.147 satırlık ikincil sözlük dosyası mevcut.

**Format çözümlemesi:**
| Format | Anlam | Sayı |
|--------|-------|------|
| `kelime-` | Fiil kökü (tire ile sonlanır) | 13.471 |
| `kelime\|k, -ga, -gy` | Mastar + çekim alternansları | 43.660 |
| `kelime\|k, -gy` | İsim + çekim | 6.779 |
| `kelime (açıklama)` | Anlamlı kelime | 1.549 |
| Düz kelime | İsim/diğer | 43.109 |

**Kritik bulgu:** Dosyada POS etiketi YOK ("Sözleriň haýsy söz toparyna degişlidigi ýörite belgi bilen görkezilmedi")

### Faz 5: tum.txt İthalatı

**Karar:**
- 337 fiil kökünü `%<v%>` olarak ekle
- 8.855 saf kelime + 1.133 açıklamalı kelimeyi yeni `%<n?%>` etiketi ile ekle
- `%<n?%>` = "At? (Muhtemel isim)" — belirsiz POS, işlevsel olarak isim muamelesi

**Sonuç:**
- 335 fiil + 15.973 n? = 16.308 yeni kelime eklendi
- Sözlük: 38.475 → 54.783 kelimeye çıktı

### Faz 6: lexicon.py Güncellemesi

- `POS_TAG_MAP`'e `"%<n?%>": "n?"` eklendi
- `POS_DISPLAY`'e `"n?": "At? (Muhtemel isim)"` eklendi
- `get_nouns()` artık `n?` girişlerini de içeriyor
- `_compute_features()` `n?`'yi isim gibi yumuşamada değerlendiriyor
- 105/105 test geçti

### Faz 7: parser.py Yeniden Yazımı

**Eski durum:** Kalıp tabanlı (pattern-based) sözlüksüz parser. Ekleri string matching ile kesiyordu, sözlük doğrulaması yoktu.

**Yeni durum:** `turkmen-fst/turkmen_fst/analyzer.py` motorunu kullanan, 54.000+ kelimelik sözlükle doğrulanmış, generator-validasyonlu gerçek morfolojik çözümleyici.

**Yenilikler:**
- Çoklu sonuç desteği (aynı kelime birden fazla şekilde çözümlenebilir → hepsi gösteriliyor)
- Eş sesli kelime anlamları gösteriliyor (`at` → "AT (At, beygir)" / "A:T (Ad, isim)")
- İsim-fiil otomatik ayrımı
- Web template'i çoklu sonuç gösterecek şekilde güncellendi

### Faz 8: Sözlük Temizliği ve n? POS Sınıflandırma

**Script:** `scripts/clean_and_classify.py`

**Phase 1 — Çekimli form tespiti:**
- Generator-doğrulamalı çoğul form (-lar/-ler) tespiti
- 49 çoğul form kaldırıldı (25 n, 24 n?)
- İyelik/hal formları: "bölüm", "dilim" gibi gerçek kökler yüzünden yapılmadı

**Phase 2 — n? POS sınıflandırma:**
- 5.334 giriş sınıflandırıldı (tum.txt + ek kalıbı doğrulamalı)
- 4.244 → n: sözel isimler (-tma/-tme: 1.626, -dyş/-diş: 1.300), mastarlar (-mak/-mek: 424), yabancı kelimeler (-iýa/-tor/-ist/-izm/-log/-ika/-graf: 779), ajan isimleri (-çy/-çi: 60), soyut isimler (-lyk/-lik: 39), tum.txt doğrulamalı: 16
- 1.090 → adj: sıfatlar (-ly/-li: 673, -syz/-siz: 417)
- 10.615 n? olarak kaldı (belirsiz: -jy/-ji partisipleri, diğer)

**Güvenlik ilkeleri:**
- Yüksek güvenilirlik: 4.555 HIGH, 779 MEDIUM
- "Kökün çekim almış hali yine bir kök olabilir" ihtimali gözetildi
- Belirsiz durumlar n? olarak bırakıldı

---

## 3. Mevcut Durum

### Sözlük Dağılımı (54.746 kelime)

| POS | Sayı | Açıklama | Değişim |
|-----|------|----------|--------|
| v | 21.054 | Fiil kökleri | — |
| n | 19.309 | Kesin isim | +4.220 (n?→n: 4.244, çoğul kaldırma: -25+1) |
| n? | 10.615 | Muhtemel isim (henüz sınıflandırılmamış) | -5.358 |
| adj | 3.088 | Sıfat | +1.090 (n?→adj) |
| np | 548 | Özel isim | — |
| unk | 33 | Bilinmeyen | — |
| adv | 33 | Zarf | — |
| num | 26 | Sayı | — |
| pro | 14 | Zamir | — |

### Test Durumu

- ✅ 105/105 test başarılı
- ✅ 4.788/4.788 v26 referans çekim eşleşmesi (%100)
- ✅ Web arayüzü çalışıyor (parser sözlük destekli)
- ✅ API çalışıyor

---

## 4. Bilinen Sorunlar ve Kısıtlamalar

### Analyzer Kısıtlamaları

1. **Maksimum 8 karakter ek soyma:** `_generate_stem_candidates()` en fazla 8 karakter soyar. Uzun ek zincirleri (örn. `kitaplarymyzdan` = 10 karakter ek) çözülemiyor.
   - **Çözüm önerisi:** Strip limitini 12'ye çıkarmak veya katmanlı soyma yapmak

2. **İsim çoğul iyelik (B1/B2):** `gözleriňiz` gibi çoğul iyelik formları her zaman doğru çözülemiyor.

3. **Ünlü uyumu farklılıkları:** Bazı kelimelerde generator ile gerçek kullanım arasında fark var (örn. `okuwçylar` vs `okuwçular`).

4. **Türetim desteği yok:** Analyzer türetim eklerini (edilgen `-yl`, ettirgen `-dyr`, vb.) çözemiyor. Bu yüzden sözlükte türetilmiş formlar tutuluyor.

### POS Belirsizliği

- ~~15.973~~ → **10.615** kelime `n?` etiketli (5.334 sınıflandırıldı + 24 çoğul kaldırıldı)
- Sınıflandırılan n? dağılımı:
  - 1.626 sözel isim (-tma/-tme) → n
  - 1.300 sözel isim (-dyş/-diş) → n
  - 673 sıfat (-ly/-li) → adj
  - 424 mastar (-mak/-mek) → n
  - 417 sıfat (-syz/-siz) → adj
  - 779 yabancı kelime (-iýa, -tor, -ist, -izm, -log, -ika, -graf) → n
  - 60 ajan ismi (-çy/-çi) → n
  - 39 soyut isim (-lyk/-lik) → n
  - 16 tum.txt doğrulamalı isim → n
- Kalan 10.615 kelime: -jy/-ji partisipleri ve belirsiz formlar → ileri sınıflandırma gerekir

---

## 5. İleride Yapılacaklar (Kısa Vadeli)

### 5.1 Analyzer İyileştirmeleri
- [x] Ek soyma limitini 8'den 13'e çıkar — **YAPILDI**
- [x] Yuvarlaklaşma toleranslı karşılaştırma eklendi — **YAPILDI**
- [x] `n?` kelimelerini kademeli olarak doğru POS'a taşı — **YAPILDI (5.334 kelime)**
- [ ] Çoğul iyelik (B1/B2) desteğini güncel duruma getir
- [ ] Türetim eki desteği ekle (edilgen, ettirgen, işteş, dönüşlü)

### 5.2 Sözlük Zenginleştirme
- [x] Eksik kelimeleri tespit et (defter, vb.) — **YAPILDI** (`defter` eklendi)
- [ ] Ünlü düşmesi / yumuşama özelliklerini otomatik tespit
- [ ] Eş sesli kelime listesini genişlet

### 5.3 Web Arayüzü
- [x] parser.py'yi sözlük destekli hale getir
- [x] Çoklu çözümleme sonucu gösterimi
- [x] Paradigma tablosu sekmesi eklendi — **YAPILDI** (4. tab, isim + fiil)
- [ ] Eş sesli kelime anlamlarını UI'da vurgulu göster
- [ ] Kelime bulunamadığında "benzer kelime önerisi" ekle

### 5.4 API Geliştirmeleri
- [x] Spellcheck endpoint (`/spellcheck`, `/spellcheck/batch`) — **YAPILDI**
- [x] Paradigma endpoint (`/paradigm`) — **YAPILDI**
- [ ] Performans: analyzer.parse() süresini ~10ms'ye düşür (cache + trie)

---

## 5.5 Önkoşullar — Stemmer ve Hunspell için

> **ÖNEMLİ:** Aşağıdaki önkoşullar sağlanmadan Stemmer ve Hunspell geliştirmesine
> geçilmemelidir.

- [x] **İsim sözlük temizliği:** 49 çoğul çekimli form tespit edilip kaldırıldı — **YAPILDI**
  - Generator-doğrulamalı, 25 `n` + 24 `n?` çoğul form
  - İyelik/hal formları: yanlış pozitif riski yüksek → yapılmadı (bölüm, dilim gibi gerçek kökler)
- [x] **n? POS sınıflandırma:** 5.334 giriş sınıflandırıldı — **YAPILDI**
  - 4.244 → n, 1.090 → adj (tum.txt + ek kalıbı doğrulamalı)
  - 10.615 hâlâ n? (belirsiz: -jy/-ji partisipleri, diğer)
- [ ] **Fiil morfolojisi doğrulama:** Fiil çekim kurallarını tam doğrulamak/geliştirmek
- [ ] **Fiil sözlük temizliği:** Fiiller için morfoloji doğrulanmadan temizlik yapılamaz
- [ ] **Analyzer doğrulama:** Her kelimeyi doğru köke indirgediğinden emin olmak
- [ ] **Ardından:** Stemmer ve Hunspell güvenilir şekilde kurulabilir

---

## 6. İleride Yapılacaklar (Uzun Vadeli)

Ayrıntılı plan için → `GELECEK_PLANLARI.md`

### Özet:
1. **Yazım denetimi** — LibreOffice / MS Office / tarayıcı eklentisi
2. **Eğitim yazılımları** — Paradigma tabloları, alıştırma oluşturucu
3. **NLP araçları** — Stemmer, lemmatizer, arama motoru entegrasyonu
4. **Bot entegrasyonları** — Telegram, WhatsApp
5. **VS Code eklentisi** — LSP tabanlı yazım denetimi

---

## 7. Teknik Notlar

### Dizin Yapısı

```
turkmence-guncelleme/
├── app.py               ← Flask web uygulaması (ana site)
├── parser.py             ← Morfolojik çözümleyici (sözlük destekli)
├── morphology.py         ← Sentez motoru (isim/fiil çekim üretimi)
├── templates/index.html  ← Web arayüzü template'i
├── turkmence_sozluk_tum.txt  ← Kaynak sözlük (111K satır)
│
└── turkmen-fst/          ← Ana motor
    ├── data/turkmence_sozluk.txt  ← Aktif sözlük (54.746 kelime)
    ├── turkmen_fst/
    │   ├── phonology.py      ← Fonoloji kuralları
    │   ├── lexicon.py        ← Sözlük yönetimi
    │   ├── morphotactics.py  ← FST state machine
    │   ├── generator.py      ← Sentez motoru
    │   ├── analyzer.py       ← Analiz motoru
    │   ├── api.py            ← FastAPI REST API
    │   └── cli.py            ← Komut satırı arayüzü
    ├── tests/                ← 105 test
    └── web/                  ← Ayrı web arayüzü
```

### Sözlük Formatı

```
kelime<TAB>pos<TAB>özellikler
kitap	%<n%>	softening
burun	%<n%>	vowel_drop
gel	%<v%>	
admiral	%<n?%>	
```

### POS Etiketleri

| Etiket | Dahili | Görüntü | Açıklama |
|--------|--------|---------|----------|
| `%<n%>` | `n` | At (İsim) | Kesin isim |
| `%<v%>` | `v` | Işlık (Fiil) | Fiil kökü |
| `%<adj%>` | `adj` | Sypat (Sıfat) | Sıfat |
| `%<n?%>` | `n?` | At? (Muhtemel isim) | POS belirsiz |
| `%<np%>` | `np` | Özel at | Özel isim |
| `%<adv%>` | `adv` | Hal (Zarf) | Zarf |
| `%<num%>` | `num` | San (Sayı) | Sayı |
| `%<pro%>` | `pro` | Çalyşma (Zamir) | Zamir |
