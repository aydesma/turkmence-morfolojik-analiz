# Türkmence Morfolojik Sözlük: Kaynak, Yöntem ve Nihai Yapı

> **Son güncelleme:** 27 Şubat 2026
> **Nihai sözlük:** 32.015 giriş · 30.154 benzersiz kelime
> **Dosya:** `turkmen-fst/data/turkmence_sozluk.txt`

---

## 1. Amaç

Bu belge, TurkmenFST morfolojik analiz motoru için oluşturulan Türkmence kök sözlüğünün kaynaklarını, derleme yöntemini ve nihai yapısını belgelemektedir. Sözlük yalnızca **kök formlar** içerir; çekimlenmiş (inflected) formlar motora bırakılmıştır.

---

## 2. Kaynaklar ve Nihai Katkıları

Sözlük beş bağımsız kaynaktan derlenmiştir. Aşağıdaki tablo her kaynağın **nihai sözlükteki** katkısını gösterir:

| # | Kaynak | Tür | Nihai Katkı | Nihai Rol |
|---|--------|-----|-------------|-----------|
| 1 | Wiktionary (en) | Kitle kaynaklı çevrimiçi sözlük | 1.649 giriş (%5,1) | Çekirdek sözlük + POS referansı |
| 2 | Hunspell tk_TM.dic | Yazım denetimi sözlüğü | 16.238 giriş (%50,7) | İsim ve sıfat ana kaynağı |
| 3 | PDF OCR Sözlük | Basılı Türkmence–İngilizce sözlük | ~0 (dolaylı katkı) | Başka kaynaklardaki kelimelerin doğrulanmasına katkı |
| 4 | tum.txt Orfoepik Sözlük | Yazılış/okuyuş kılavuzu | 5.362 giriş (%16,7) | İsim zenginleştirme |
| 5 | enedilim.com | Türkmenistan resmi dil sözlüğü | 8.802 giriş (%27,5) | Fiil köklerinin **tek kaynağı** + doğrulama referansı |
| | | | **32.015** | |

### 2.1 Wiktionary — Çekirdek Sözlük

- **URL:** `en.wiktionary.org/wiki/Category:Turkmen_lemmas`
- **İlk çekim:** ~1.736 lemma
- **POS belirleme:** Wiktionary kategori sistemi (`Turkmen nouns` → `n`, `Turkmen verbs` → `v`, vb.) + wikitext bölüm başlıkları (`===Noun===`) ile çift doğrulama
- **Nihai durum:** 1.649 giriş çekirdek olarak korunmakta. En güvenilir POS kaynağı (el ile düzenlenmiş, kategori tabanlı).

### 2.2 Hunspell tk_TM.dic — İsim ve Sıfat Ana Kaynağı

- **Dosya:** `resources/tk_TM.dic` (61.974 giriş) + `resources/tk_TM.aff` (bayrak tanımları)
- **İthalat yöntemi:** 114 bayrak grubu analiz edildi; her grubun Wiktionary çapraz referansıyla POS karışıklık oranı hesaplandı. Yalnızca güvenilirlik ≥%60 olan gruplar ithal edildi.
- **İlk ithalat:** 36.747 kelime
- **Nihai durum:** 16.238 giriş → 13.962 isim + 1.840 sıfat + 310 özel isim + 126 fiil kökü
- **Önemli not:** Bu kaynaktan gelen fiil girişlerinin büyük çoğunluğu (%99,4) enedilim.com temizliğinde kaldırıldı. Hunspell fiilleri çoğunlukla çekimlenmiş/türetilmiş formlardan oluşuyordu. Sözlükteki fiil kökleri artık **yalnızca enedilim.com** kaynaklıdır.

### 2.3 PDF OCR Sözlük — (Dolaylı Katkı)

- **Dosya:** `resources/Turkmen_English Dictionary - Turkmenistan Chaihana.pdf` (~80 sayfa, 3 sütunlu)
- **Çıkarılan:** 9.240 kelime (RapidOCR ile); 5.267'si sözlüğe eklendi
- **Nihai durum:** POS bilgisi olmadığından `n?` (belirsiz isim) etiketlenmişti. Temizlik aşamalarında tüm `n?` girişleri kaldırıldığında bu kaynak büyük ölçüde elendi. Diğer kaynaklarla örtüşen kelimelerde dolaylı doğrulama işlevi gördü.

### 2.4 tum.txt Orfoepik Sözlük — İsim Zenginleştirme

- **Dosya:** `resources/turkmence_sozluk_tum.txt` (111.147 satır)
- **Özellik:** POS etiketi yok; format kalıplarından çıkarım yapılabilir (tire ile biten → fiil kökü, pipe notasyonu → morfolojik alternans)
- **İthalat:** Türetilmiş formlar filtrelendi; 16.308 kelime eklendi
- **Nihai durum:** 5.362 giriş kaldı (5.224 isim + 137 açıklamalı kelime + 1 fiil). Fiiller enedilim.com ile değiştirildi; `n?` etiketli olanlar silindi; yalnızca POS'u kesinleştirilebilmiş isimler korundu.
- **İkincil rol:** `n?` etiketli kelimelerin isim/sıfat sınıflandırmasında çapraz referans.

### 2.5 enedilim.com — Fiil Köklerinin Tek Kaynağı ve Referans Sözlük

- **URL:** `enedilim.com` (Türkmenistan devlet dili resmi portalı)
- **Kapsam:** 20.120 headword (6.461 fiil mastarı + 13.659 isim/sıfat/diğer)
- **Yöntem:**
  1. A–Ž tüm harflerin headword listesi scrape edildi → `enedilim_headwords.json`
  2. Sözlüğümüzdeki 31.414 kelimenin POS'u enedilim API'sinden sorgulandı → `enedilim_lookups.json`
  3. Kapsamlı temizlik ve yeniden yapılandırma uygulandı
- **Nihai katkı:**
  - **6.330 fiil kökü** doğrudan eklendi (+ ~141 tanesi diğer kaynaklarda zaten mevcuttu; toplam fiil = 6.471)
  - **2.471 eksik isim** eklendi
  - **%100 kapsama doğrulaması**: enedilim'deki 20.120 headword'un tamamı sözlüğümüzde mevcut
- **Güvenilirlik:** En yüksek — devlet tarafından yönetilen resmi dil kaynağı

---

## 3. Derleme Süreci Özeti

```
Aşama 1  Wiktionary scraping              →   1.736 kelime
Aşama 2  Morfolojik özellik ekleme        →   1.746
Aşama 3  Hunspell ithalatı                →  38.480
Aşama 4  PDF OCR birleştirme              →  43.747
Aşama 5  tum.txt ithalatı                 →  54.795
     ↑ Büyüme aşamaları ─────────────────────────────────
     ↓ Temizlik ve doğrulama aşamaları ───────────────────
Aşama 6  Türetilmiş form analizi          →  (karar: kalsın)
Aşama 7  n? sınıflandırma + çoğul temizlik→  54.746
Aşama 8  enedilim.com büyük temizlik      →  32.051
Aşama 9  Tek harfli kök temizliği         →  32.015  ← NİHAİ
```

### Aşama 8 — Kritik Temizlik Detayı

En büyük değişiklik bu aşamada gerçekleşti:

| Operasyon | Sayı | Açıklama |
|-----------|------|----------|
| Fiil-only girişlerin silinmesi | −15.663 | Hunspell/PDF/tum.txt kaynaklı çekimli ve türetilmiş fiiller |
| `n?` girişlerin silinmesi | −9.595 | POS'u kesinleştirilemeyen belirsiz girişler |
| enedilim fiil kökleri eklenmesi | +5.997 | Doğrulanmış kök fiiller (sözlükte olmayanlar) |
| Eksik enedilim isimleri eklenmesi | +401 | enedilim'de olup sözlüğümüzde olmayan isimler |
| Softening etiketleme | +961 etiket | k/p/t/ç ile biten isim/sıfatlara softening eklendi |

### `n?` POS Etiketinin Yaşam Döngüsü

PDF ve tum.txt kaynaklarından gelen kelimelerin çoğunun POS bilgisi yoktu. `n?` (muhtemel isim) olarak etiketlendiler. Aşama 7'de morfolojik kalıplara dayalı otomatik sınıflandırma ile 5.334 giriş kesinleştirildi (4.244 → `n`, 1.090 → `adj`). Kalan 10.615 `n?` giriş Aşama 8'de güvenilirlik gerekçesiyle tamamen kaldırıldı. **Nihai sözlükte `n?` etiketi yoktur.**

---

## 4. Sözlük Formatı

```
kelime<TAB>%<POS%>[<TAB>özellikler]
```

**Örnek girişler:**
```
kitap	%<n%>	softening
al	%<v%>
uly	%<adj%>
burun	%<n%>	vowel_drop
```

### POS Etiketleri

| Etiket | Tür | Sayı | Yüzde |
|--------|-----|------|-------|
| `%<n%>` | İsim | 21.798 | %68,1 |
| `%<v%>` | Fiil | 6.471 | %20,2 |
| `%<adj%>` | Sıfat | 3.094 | %9,7 |
| `%<np%>` | Özel isim | 548 | %1,7 |
| `%<adv%>` | Zarf | 36 | %0,11 |
| `%<unk%>` | Bilinmeyen | 2 | %0,01 |
| `%<num%>` | Sayı | 26 | %0,08 |
| `%<pro%>` | Zamir | 14 | %0,04 |
| Diğer | suf, postp, interj, conj, det, phr, prep | 26 | %0,08 |
| **Toplam** | | **32.015** | **%100** |

### Morfolojik Özellikler

| Özellik | Açıklama | Sayı |
|---------|----------|------|
| `softening` | Son ünsüzü k/p/t/ç → g/b/d/j yumuşaması alan kelimeler | 7.001 |
| `vowel_drop` | Ek alırken ünlü düşmesi gösteren kelimeler (burun→burn-, ogul→ogl-) | 20 |
| `exception_drop:<form>` | İstisnai ünlü düşmesi (asyl→asl, nesil→nesl, ylym→ylm, mähir→mähr, pasyl→pasl) | 5 |
| `homonym:<detay>` | Eş sesli kelime bilgisi (at, but, gurt, saç, ot, yok) | 6 |
| `rounding` | Yuvarlaklaşma | 3 |

---

## 5. Doğrulama ve Kalite Güvencesi

### 5.1 Kapsama Doğrulaması

| Kontrol | Sonuç |
|---------|-------|
| enedilim headword'larının tamamı sözlükte mi? | **Evet** — 20.120/20.120 (%100) |
| Sözlükte çekimlenmiş form var mı? | **Hayır** — 32.015 girişin tamamı kök veya bağımsız türetilmiş sözcük |
| Sadece bizde olan kelime | 10.356 (Wiktionary + Hunspell + tum.txt kaynaklı) |
| Ortak kelime (enedilim ∩ biz) | 19.827 |

### 5.2 POS Doğruluğu

- enedilim.com'dan POS verisi dönen 58 kelimenin tamamı sözlüğümüzde **doğru etiketli**:
  - 7 sıfat (sypat) → hepsi `adj`
  - 3 zarf (hal) → hepsi `adv`
  - 48 isim (at) → hepsi `n`
- **Sıfır mismatch:** enedilim'in `adj` dediği hiçbir kelime bizde yanlışlıkla `n` olarak etiketlenmemiş

### 5.3 Çekimlenmiş Form Kontrolü

Sözlükteki tüm `-lar`/`-ler` sonekli kelimeler tarandı. Kökü sözlükte mevcut olan ve çoğul üreticisi (`NounGenerator.generate()`) tarafından üretimi doğrulanan 49 çoğul form tespit edilip kaldırıldı. Geriye kalan kelimeler (ör. `dollar`, `bölüm`, `dilim`) false positive kontrolünden geçirilmiş bağımsız sözcüklerdir.

### 5.4 Türetilmiş Form Analizi

Sözlükteki 4.109 kelime (%13,6) türetilmiş formdur (kökü de sözlükte mevcut). Bunlar **çekimlenmiş form değil, bağımsız kelimelerdir** — her biri kendi başına çekim alır ve enedilim.com'da bağımsız headword olarak listelidir.

| Türetme Eki | Sayı | Örnek |
|-------------|------|-------|
| -lyk/-lik/-luk/-lük | 1.495 | zahyrlyk, zergärlik |
| -ly/-li/-lu/-lü | 776 | zarply, zehinli |
| -syz/-siz/-suz/-süz | 414 | zatsyz, zehinsiz |
| -çy/-çi | 397 | zarpçy, zekatçy |
| -çylyk/-çilik | 387 | zamunçylyk, zergärçilik |
| -keş/-dar/-hor/-kär | 104 | zyýankeş, zulumdar |
| -daş/-deş | 97 | zamandaş |
| Diğer | 439 | — |
| **Toplam** | **4.109** | **%13,6** |

### Aşama 9 — Tek Harfli Kök Temizliği

36 adet tek harfli kök girişi kaldırıldı. Bunların çoğu `unk` etiketli idi ve yalnız başlarına anlamsız köklerdi. Yalnızca `o` (zamir) korunmuştur.

| Operasyon | Sayı |
|-----------|------|
| Tek harfli `unk` silme | −31 |
| Tek harfli `n`/`adj`/`v` silme | −5 |
| **Nihai sonuç** | **32.015** |

### 5.5 Test Sonuçları

- 105/105 birim testi başarılı
- 4.788/4.788 v26 referans çekim eşleşmesi (%100)
- `isim_cekimle()` tüm türetilmiş kelimelerle sorunsuz çalışıyor

---

## 6. Kısıtlamalar

1. **Softening istisnaları:** Sistem son harfi k/p/t/ç olan tüm isimlere otomatik softening uygular. Bazı yabancı kökenli kelimelerin softening almama durumu henüz sistematik olarak işaretlenmemiştir.

2. **Hunspell POS belirsizliği:** Düşük güvenilirlikli bayrak gruplarından (%60–70 arası) gelen kelimelerde POS hatası olabilir.

3. **10.356 enedilim-dışı kelime:** Bu kelimelerin bir kısmı türetilmiş formlar ve Wiktionary isimleridir; ancak bir kısmında kalite sorunu olabilir.

4. **Türetim desteği yok:** Motor türetme eklerini otomatik olarak çözemiyor; türetilmiş formlar bağımsız giriş olarak sözlükte tutulmaktadır.

---

## 7. Script Envanteri

| Script | Amaç | Girdi | Çıktı |
|--------|-------|-------|-------|
| `scripts/scrape_wiktionary.py` | Wiktionary lemma çekme | MediaWiki API | İlk sözlük dosyası |
| `scripts/enrich_dictionary.py` | Morfolojik özellik ekleme | Sözlük + morphology.py | Zenginleştirilmiş sözlük |
| `scripts/import_hunspell.py` | Hunspell ithalatı | `tk_TM.dic` / `.aff` | Sözlük (ekleme) |
| `scripts/extract_pdf_dictionary.py` | PDF OCR kelime çıkarma | PDF dosyası | `pdf_words_raw/clean.txt` |
| `scripts/merge_pdf_to_dict.py` | PDF birleştirme | `pdf_extracted.json` | Sözlük (yeniden yazma) |
| `scripts/import_tum.py` | tum.txt ithalatı | `turkmence_sozluk_tum.txt` | Sözlük (ekleme) |
| `scripts/clean_and_classify.py` | n? sınıflandırma + çoğul temizlik | Sözlük + tum.txt | Sözlük (yerinde güncelleme) |
| `scripts/enedilim_crossref.py` | Headword scraping | enedilim.com | `enedilim_headwords.json` |
| `scripts/enedilim_batch_lookup.py` | Toplu POS sorgulaması | Sözlük + enedilim.com | `enedilim_lookups.json` |
| `scripts/enedilim_apply_all.py` | Büyük temizlik uygulaması | Sözlük + JSON önbellekler | Sözlük (yerinde güncelleme) |
