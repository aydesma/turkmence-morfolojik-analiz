# Türkmence Morfolojik Analiz

Türkmen Türkçesi için kural tabanlı morfolojik analiz ve sentez sistemi.
İsim çekimi (hal, iyelik, çoğul), fiil çekimi (7 zaman × 6 şahıs) ve
cümle düzeyinde morfolojik ayrıştırma yeteneklerini barındırır.

**Canlı demo:** [turkmence-morfolojik-analiz.vercel.app](https://turkmence-morfolojik-analiz.vercel.app/)

---

## Proje Yapısı

```
├── app.py                 # Flask web uygulaması + REST API
├── morphology.py          # v26 morfolojik üretim motoru
├── parser.py              # Sözlük destekli morfolojik çözümleyici
├── templates/index.html   # Web arayüzü (4 sekmeli)
├── requirements.txt       # Python bağımlılıkları
└── turkmen-fst/           # Çekirdek motor paketi
    ├── turkmen_fst/       # Modüler FST motoru (phonology, lexicon, generator, analyzer…)
    ├── data/              # 32 000+ kelimelik zenginleştirilmiş sözlük
    ├── tests/             # 105 birim testi (%100 başarılı)
    └── web/               # Bağımsız Flask web arayüzü
```

> `turkmen-fst/` klasörünün ayrıntılı dokümantasyonu için bkz. [turkmen-fst/README.md](turkmen-fst/README.md)

---

## Özellikler

| Yetenek | Açıklama |
|---------|----------|
| **İsim çekimi** | 6 hal × 3 iyelik × 2 çoğul — tam paradigma üretimi |
| **Fiil çekimi** | 7 zaman × 6 şahıs × olumlu/olumsuz |
| **Morfolojik ayrıştırma (Derňew)** | Çekimli kelime → kök + ek zinciri |
| **Paradigma tablosu** | Otomatik tür tespiti, eş sesli kelimeler için çift paradigma, tablo kopyalama |
| **Yazım denetimi** | Sözlük + morfoloji tabanlı doğrulama ve öneri |
| **REST API** | 7 JSON endpoint (üretim, analiz, paradigma, sözlük, yazım denetimi) |
| **Fonoloji** | Ünlü uyumu, ünsüz yumuşaması, ünlü düşmesi, yuvarlaklaşma |
| **Sözlük** | 32 015 giriş, 30 154 benzersiz kelime; morfolojik etiketler |

---

## Kurulum

```bash
git clone https://github.com/aydesma/turkmence-morfolojik-analiz.git
cd turkmence-morfolojik-analiz
pip install -r requirements.txt
```

Çekirdek motoru ayrı paket olarak da kurabilirsiniz:

```bash
cd turkmen-fst
pip install -e .
```

---

## Kullanım

### Web Arayüzü

```bash
python app.py
# → http://localhost:5000
```

Dört sekmeli arayüz:
1. **At çekimi (İsim)** — Kök + hal/iyelik/çoğul seçimi → çekimli form
2. **Işlık çekimi (Fiil)** — Kök + zaman/şahıs/olumsuz → çekimli form
3. **Derňew (Analiz)** — Kelime girişi → morfolojik ayrıştırma (kök + ekler)
4. **Paradigma** — Otomatik tür tespiti ile tam çekim tablosu (eş sesli kelimeler için ikisi birden)

### REST API

API base URL: `https://turkmence-morfolojik-analiz.vercel.app/api`

#### Örnekler

**İsim çekimi:**
```bash
curl -X POST /api/generate/noun \
  -H "Content-Type: application/json" \
  -d '{"stem": "kitap", "case": "A3", "plural": true}'
# → {"result": "kitaplara", "breakdown": "kitap + lar + a", "valid": true}
```

**Fiil çekimi:**
```bash
curl -X POST /api/generate/verb \
  -H "Content-Type: application/json" \
  -d '{"stem": "gel", "tense": "1", "person": "A1"}'
# → {"result": "geldim", "breakdown": "gel + di + m", "valid": true}
```

**Morfolojik analiz:**
```bash
curl -X POST /api/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "kitabymyza geldim"}'
# → Her kelime için kök, ekler, POS bilgisi…
```

**Paradigma tablosu (otomatik tür tespiti):**
```bash
curl -X POST /api/paradigm \
  -H "Content-Type: application/json" \
  -d '{"stem": "at"}'
# → [{"type": "noun", ...}, {"type": "verb", ...}]  (eş sesli → ikisi birden)
```

```bash
curl -X POST /api/paradigm \
  -H "Content-Type: application/json" \
  -d '{"stem": "kitap", "type": "noun"}'
# → [{"type": "noun", "singular": [...], "plural": [...]}]
```

**Yazım denetimi:**
```bash
curl -X POST /api/spellcheck \
  -H "Content-Type: application/json" \
  -d '{"text": "kitobym"}'
# → {"results": [{"word": "kitobym", "correct": false, "suggestions": [...]}]}
```

**Sözlük sorgusu:**
```bash
curl /api/lexicon/kitap
# → {"word": "kitap", "found": true, "entries": [...]}
```

#### Tüm Endpoint'ler

| Metot | Yol | Açıklama |
|-------|-----|----------|
| GET | `/api/health` | Sağlık kontrolü (sözlük giriş sayısı) |
| POST | `/api/generate/noun` | İsim çekimi üretimi |
| POST | `/api/generate/verb` | Fiil çekimi üretimi |
| POST | `/api/analyze` | Morfolojik ayrıştırma (tek/çoklu kelime) |
| GET | `/api/lexicon/<word>` | Sözlük girişi sorgusu |
| POST | `/api/spellcheck` | Yazım denetimi + öneri |
| POST | `/api/paradigm` | Paradigma tablosu (auto/noun/verb) |

---

## Sözlük İstatistikleri

| POS | Sayı | Yüzde |
|-----|------|-------|
| İsim (n) | 21 798 | %68,1 |
| Fiil (v) | 6 471 | %20,2 |
| Sıfat (adj) | 3 094 | %9,7 |
| Özel isim (np) | 548 | %1,7 |
| Diğer | 104 | %0,3 |
| **Toplam** | **32 015** | **%100** |

> Sözlük oluşturma sürecinin detayları: [turkmen-fst/SOZLUK_OLUSTURMA_SURECI.md](turkmen-fst/SOZLUK_OLUSTURMA_SURECI.md)

---

## Test

```bash
# Birim testleri
cd turkmen-fst
python -m pytest tests/ -v
# 105 passed ✅

# Kapsamlı round-trip testi (üret → çözümle)
cd ..
python test_comprehensive.py
# 1192 test ✅
```

---

## Lisans

MIT
