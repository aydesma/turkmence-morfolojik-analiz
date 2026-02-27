# Yapılan İşler — Tamamlanan Özellikler ve Düzeltmeler

> **Son güncelleme:** 28 Şubat 2026

---

## 1. Sözlük Oluşturma (v1 → v32K)

| Tarih | İş | Detay |
|-------|----|-------|
| Şubat 2026 | Wiktionary çekirdeği | 1.736 lemma, POS etiketi ile |
| Şubat 2026 | Hunspell ithalatı | 16.238 giriş (bayrak analizi ile POS sınıflandırma) |
| Şubat 2026 | PDF OCR sözlük | ~5.267 kelime çıkarıldı (sonra büyük kısmı elendi) |
| Şubat 2026 | tum.txt orfoepik sözlük | 5.362 isim |
| Şubat 2026 | enedilim.com entegrasyonu | 6.471 fiil kökü + 2.471 eksik isim |
| Şubat 2026 | Büyük temizlik (Aşama 8) | 54.795 → 32.051 (n? ve çekimli form silme) |
| Şubat 2026 | Tek harfli kök temizliği | 36 giriş silindi (yalnızca `o` zamir korundu) → 32.015 |

**Nihai:** 32.015 giriş · 30.154 benzersiz kelime · 5 kaynak

---

## 2. Morfolojik Motor (generator.py)

### İsim Çekimi
- [x] 6 hal (yalın, ilgi, yönelme, belirtme, bulunma, çıkma)
- [x] 3 iyelik düzeyi (A1 tekil, A2 tekil, A3 tekil)
- [x] B1/B2 iyelik → A1/A2 + çoğul mantığına dönüştürme (önceki hata düzeltildi)
- [x] Çoğul (-lar/-ler, ünlü uyumu)
- [x] Ünsüz yumuşaması (softening: p→b, t→d, ç→j, k→g)
- [x] Ünlü düşmesi (vowel_drop: burun→burn-, ogul→ogl-)
- [x] İstisna ünlü düşmesi (exception_drop: asyl→asl, mähir→mähr)
- [x] Yuvarlaklaşma (göl→göller)
- [x] Eş sesli kelimeler (homonym etiketi)
- [x] Sözlük tabanlı softening etiketleri (7.001 kelime otomatik etiketli)

### Fiil Çekimi
- [x] 7 temel zaman: Ö1, Ö2, Ö3, H1, H2, G1, G2
- [x] 6 şahıs: A1–A3 tekil, B1–B3 çoğul
- [x] Olumlu / olumsuz
- [x] 8 fiil çekim düzeltmesi (commit fe28801 — enedilim.com incelemesiyle tetiklendi):
  - H1 kişi ekleri: `-ym/-ik` → `-yn/-is` (genişletilmiş paradigma)
  - G2 olumsuz: çift olumsuzluk hatası giderildi
  - G2 olumsuz: A1/A2/B1/B2 `-mar/-mer`, A3/B3 `-maz/-mez` ayrımı
  - Ö1 dodak yuvarlaklaşması: tek hece+dodak → `-du/-dü`
  - G2 olumlu: `e→ä` dönüşümü
  - H1/G2: k/t ünsüz yumuşaması (`okat→okadýar`)
  - G1 B3: çoğul eki `-lar/-ler` eklendi
  - Yardımcı: `_tek_heceli_dodak`, `_fiil_yumusama` fonksiyonları
- [x] 4 enedilim uyumsuzluğu DÜZELTİLDİ ✅:
  - ✅ Ö2 olumsuz: `-me+ipdi` → `-män+di` kalıbına geçirildi
  - ✅ Ö3 olumsuz: `-me+ýärdi` → `-ýän däldi` analitik yapıya geçirildi
  - ✅ G1 olumlu: kopula kişi ekleri (`-jekdirin/-jakdyryn`) eklendi
  - — Ö3 B3 olumlu: mevcut haliyle bırakıldı

### Yeni Kipler ve Formlar (Şubat 2026)
- [x] **5 yeni kip/form:**
  - Ş1 — Şert formasy (Şart kipi): `-sa/-se` + şahıs eki
  - B1K — Buýruk formasy (Emir kipi): şahıs bazlı özel kalıplar (A2=çıplak kök, A3=-syn/-sin, B2=-yň/-iň...)
  - HK — Hökmanlyk formasy (Gereklilik kipi): `-maly/-meli` [+ `däl`]
  - NÖ — Nätanyş Öten (Kanıtsal/Evidential): `-ypdyr/-ipdir` + kopula kişi eki
  - AÖ — Arzuw-Ökünç (Dilek-Pişmanlık/Optative): `-sa/-se` + `-dy/-di` + şahıs eki
- [x] **4 fiilimsi (ortaklyk) formu:**
  - FH — Hal işlik (converb/ulaç): `-yp/-ip/-up/-üp/-p` (olumsuz: `-man/-män`)
  - FÖ — Öten ortak (past participle): `-an/-en` (olumsuz: `-madyk/-medik`)
  - FÄ — Häzirki ortak (present participle): `-ýan/-ýän` (olumsuz: `-maýan/-meýän`)
  - FG — Geljek ortak (future participle): `-jak/-jek` (olumsuz: `-majak/-mejek`)
- [x] **2 işlik derejesi (fiil çatısı):**
  - ETT — Ettirgen (causative): `-dyr/-dir/-dur/-dür` veya `-t` (ünlüyle biten kökler)
  - EDL — Edilgen (passive): `-yl/-il/-ul/-ül` veya `-yn/-in/-un/-ün` (l-sonu kökler)
- [x] **Toplam 18 zaman/kip/form kodu** (ZAMAN_DONUSUM sözlüğü): Ö1–G2 (7) + Ş1/B1K/HK/NÖ/AÖ (5) + FH/FÖ/FÄ/FG (4) + ETT/EDL (2)
- [x] Hem `morphology.py` hem `turkmen-fst/turkmen_fst/generator.py` senkron güncellendi
- [x] Web arayüzü dropdown'ları 4 optgroup ile güncellendi (İşlik Formalary, Fiilimsi, Işlik Derejeleri)
- [x] 124 yeni test (test_new_verb_forms.py): tümü başarılı ✅

---

## 3. Morfolojik Analiz (analyzer.py)

- [x] İsim ayrıştırma: çekimli kelime → kök + ekler
- [x] Fiil ayrıştırma: çekimli kelime → kök + ekler
- [x] Cümle düzeyinde analiz (çoklu kelime)
- [x] Sözlük destekli kök doğrulama
- [x] Çapraz tekilleştirme (aynı kelime isim+fiil olarak ayrıştırıldığında tekil sonuç)
- [x] breakdown_key ile aynı breakdown farklı kişi sonuçlarının tekilleştirilmesi

---

## 4. Web Arayüzü (templates/index.html)

- [x] 4 sekmeli arayüz: İsim, Fiil, Derňew, Paradigma
- [x] Paradigma otomatik tür tespiti (sözlükten bakarak isim/fiil belirleme)
- [x] Eş sesli kelimeler için çift paradigma (hem isim hem fiil tablosu)
- [x] "Tablony kopyala" butonu (clipboard'a tablo kopyalama)
- [x] "Awtomatik" radio seçeneği (varsayılan)
- [x] Responsive tasarım

---

## 5. REST API (app.py)

- [x] `GET /api/health` — sağlık kontrolü (sözlük giriş sayısı)
- [x] `POST /api/generate/noun` — isim çekimi üretimi
- [x] `POST /api/generate/verb` — fiil çekimi üretimi
- [x] `POST /api/analyze` — morfolojik ayrıştırma
- [x] `GET /api/lexicon/<word>` — sözlük girişi sorgusu
- [x] `POST /api/spellcheck` — yazım denetimi + öneri
- [x] `POST /api/paradigm` — paradigma tablosu (auto/noun/verb)
- [x] poss_type varsayılan "tek" hatası düzeltildi
- [x] paradigm endpoint list return + auto default düzeltmesi
- [x] 18/18 API testi başarılı

---

## 6. Hata Düzeltmeleri (Bug Fixes)

| Tarih | Hata | Düzeltme | Commit |
|-------|------|----------|--------|
| Şubat 2026 | `ýygnajak` duplikasyon | Fiil üretiminde tekilleştirme | `cbb063a` |
| Şubat 2026 | B1/B2 iyelik yanlış çekim | B1/B2 → A1/A2 + çoğul dönüşümü | `407198c` |
| Şubat 2026 | Eş sesli kelime çapraz duplikasyon | analyzer.py cross-dedup | `407198c` |
| Şubat 2026 | Tek harfli köklerden yanlış parse (`a + dy`) | 36 tek harfli kök silindi | `5cc3575` |
| Şubat 2026 | `derneý` → `aty` çift sonuç | Tek harfli kök temizliği ile çözüldü | `5cc3575` |
| Şubat 2026 | poss_type API None override | `data.get("poss_type", "tek")` | (uncommitted) |
| Şubat 2026 | paradigm endpoint `result is None` | `not result` + auto default | (uncommitted) |

---

## 7. Test Kapsamı

| Test Seti | Sayı | Durum |
|-----------|------|-------|
| Birim testleri (pytest) | 105 | ✅ %100 |
| Yeni fiil form testleri (test_new_verb_forms.py) | 124 | ✅ %100 |
| Kapsamlı round-trip (test_comprehensive.py) | 1.192 | ✅ %100 |
| v26 referans eşleşme | 4.788 | ✅ %100 |
| API endpoint testleri | 18 | ✅ %100 |

---

## 8. Dağıtım

- [x] Vercel deployment: `turkmence-morfolojik-analiz.vercel.app`
- [x] GitHub: `aydesma/turkmence-morfolojik-analiz` (main branch)
- [x] requirements.txt güncel
