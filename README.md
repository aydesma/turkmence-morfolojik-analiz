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
    ├── data/              # 30 000+ kelimelik zenginleştirilmiş sözlük
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
| **Morfolojik ayrıştırma** | Çekimli kelime → kök + ek zinciri |
| **Paradigma tablosu** | Bir kelimenin tüm çekim formlarını tek tabloda gösterir |
| **Yazım denetimi** | Sözlük + morfoloji tabanlı doğrulama ve öneri |
| **REST API** | JSON tabanlı entegrasyon noktaları |
| **Fonoloji** | Ünlü uyumu, ünsüz yumuşaması, ünlü düşmesi, yuvarlaklaşma |
| **Sözlük** | 30 000+ kelime; ünsüz yumuşaması, ünlü düşmesi gibi morfolojik etiketler |

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
1. **İsim çekimi** — Kök + hal/iyelik/çoğul seçimi → çekimli form
2. **Fiil çekimi** — Kök + zaman/şahıs/olumsuz → çekimli form
3. **Derňew (Analiz)** — Cümle veya kelime girişi → morfolojik ayrıştırma
4. **Paradigma** — Bir kelimenin tüm isim çekim tablosu

### REST API

API base URL: `https://turkmence-morfolojik-analiz.vercel.app/api`

#### Örnekler

**İsim çekimi:**
```bash
curl -X POST /api/generate/noun \
  -H "Content-Type: application/json" \
  -d '{"stem": "kitap", "case": "A3", "plural": true}'
# → {"result": "kitaplara", "breakdown": "kitap + lar + a", "valid": true, ...}
```

**Fiil çekimi:**
```bash
curl -X POST /api/generate/verb \
  -H "Content-Type: application/json" \
  -d '{"stem": "gel", "tense": "1", "person": "A1"}'
# → {"result": "geldim", "breakdown": "gel + di + m", "valid": true, ...}
```

**Morfolojik analiz:**
```bash
curl -X POST /api/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "kitabymyza geldim"}'
# → Her kelime için kök, ekler, POS bilgisi…
```

**Paradigma tablosu:**
```bash
curl -X POST /api/paradigm \
  -H "Content-Type: application/json" \
  -d '{"stem": "kitap"}'
# → 6 hal × tekil/çoğul × iyeliksiz çekim tablosu
```

**Yazım denetimi:**
```bash
curl -X POST /api/spellcheck \
  -H "Content-Type: application/json" \
  -d '{"word": "kitobym"}'
# → {"found": false, "suggestions": ["kitabym", ...]}
```

**Sözlük sorgusu:**
```bash
curl /api/lexicon/kitap
# → {"word": "kitap", "pos": "noun", "features": ["softening"], ...}
```

#### Tüm Endpoint'ler

| Metot | Yol | Açıklama |
|-------|-----|----------|
| GET | `/api/health` | Sağlık kontrolü |
| POST | `/api/generate/noun` | İsim çekimi üretimi |
| POST | `/api/generate/verb` | Fiil çekimi üretimi |
| POST | `/api/analyze` | Morfolojik ayrıştırma |
| GET | `/api/lexicon/<word>` | Sözlük girişi sorgusu |
| POST | `/api/spellcheck` | Yazım denetimi + öneri |
| POST | `/api/paradigm` | Tam paradigma tablosu |

---

## Test

```bash
cd turkmen-fst
python -m pytest tests/ -v
# 105 passed ✅
```

---

## Lisans

MIT
