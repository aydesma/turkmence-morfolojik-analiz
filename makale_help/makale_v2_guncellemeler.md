# Makale v2 Güncellemeleri — IEEE TurkLang
# Bu dosya, makalede yapılacak değişiklikleri NET olarak listeler.
# Tarih: 2026-03-02

---

## 1. Ünsüz Yumuşaması İstisna Mekanizması (YENİ — Section 3/4)

### Ne değişti?
Sistem artık K/P/T/Ç ile biten tüm isimleri körlemesine yumuşatmıyor.
Corpus analizi ile keşfedilen 58 alıntı kelime **istisna** olarak işaretlendi.

### Makaledeki yeri: Section 3 (Phonology) veya Section 4 (Evaluation)

### Yazılacak paragraf (İngilizce taslak):

> **Consonant Softening Exception Handling.**
> Standard Turkmen phonology softens final K/P/T/Ç when a vowel-initial
> suffix is attached (e.g., *kitap → kitaby*). However, loanwords of
> Arabic, Persian, and European origin typically resist softening
> (e.g., *maslahat → maslahaty*, not *maslaHADy*; *prezident → prezidenti*,
> not *prezidendi*).
>
> We developed a data-driven exception discovery pipeline: for each
> K/P/T/Ç-ending noun in the lexicon, we generate both softened and
> unsoftened inflected forms, then check which form actually appears in
> a reference corpus (50 articles from metbugat.gov.tm, 33,153 tokens).
> This procedure identified 58 non-softening stems, predominantly
> Arabic/Persian loanwords (e.g., *döwlet, syýasat, halk, hökümet*)
> and European borrowings (e.g., *prezident, parlament, sport, bank*).
> These stems are marked with a `no_softening` flag in the lexicon.
>
> The discovery tool (`discover_softening_exceptions.py`) can be re-run
> on larger corpora to incrementally expand the exception list.

### Tablo (Section 4 — Evaluation):

| Metrik | Önceki | Şimdi | Artış |
|--------|--------|-------|-------|
| softening=True (kural dahilinde) | 6,997 | 6,939 | -58 |
| no_softening (istisna) | 0 | 58 | +58 |
| Corpus token kapsamı | %71.84 | %78.3 | +6.46pp |

---

## 2. Genişletilmiş Fiil Zaman Kapsamı (Section 3 — Morphotactics)

### Ne değişti?
Analyzer artık 18 zaman/kip kodunun tamamını destekliyor (önceki: sadece 1-7).

### Eklenen tense kodları:
- 8: Şart kipi (-sa/-se)
- 9: Emir kipi (imperative)
- 10: Gereklilik kipi (-maly/-meli)
- 11: Rivayet kipi (evidential)
- 12: İstek kipi (optative)
- 13: Ulaç (-yp converb)
- 14: Geçmiş ortaç (-an past participle)
- 15: Şimdiki ortaç (-ýan present participle)
- 16: Gelecek ortaç (-jak future participle)
- 17: Ettirgen çatı (-dyr causative)
- 18: Edilgen çatı (-yn passive)

### Makaledeki yeri: Section 3.3 (Verb Morphotactics) tablosuna eklenmeli

### Yazılacak not:
> The analyzer's tense coverage was extended from 7 basic tenses to all
> 18 tense/mood/aspect codes supported by the generator, including
> participles (-an, -ýan, -jak), converbs (-yp), conditional (-sa),
> imperative, necessitative (-maly), evidential, optative, causative (-dyr),
> and passive (-yn) forms.

---

## 3. Sözlük Formatı Güncellemesi (Section 3.1 — Lexicon)

### Ne değişti?
Sözlük dosyasına yeni özellik tipi eklendi: `no_softening`

### Eski format:
```
maslahat	%<n%>	softening
```

### Yeni format:
```
maslahat	%<n%>	no_softening
kitap	%<n%>	softening
```

### Makaledeki yeri: Section 3.1'deki sözlük format açıklamasına

### Yazılacak not:
> Each noun entry ending in K/P/T/Ç carries an explicit morphophonemic
> flag: `softening` (default, consonant alternation applies) or
> `no_softening` (exception, consonant remains unchanged). The current
> lexicon contains 6,939 softening entries and 58 no_softening entries.

---

## 4. Corpus Kapsamı Sonuçları (Section 4 — Evaluation)

### Güncellenecek tablo:
Makale Section 4'teki kapsamı tablosu şu verileri içerecek:

| Kaynak | Token | Benzersiz | Tanınan Token | Kapsam |
|--------|-------|-----------|---------------|--------|
| metbugat.gov.tm (50 mk) | 33,153 | 5,593 | %78.3 token | %69.4 type |

### Not:
Önceki kapsam testi (10,179 token, 13 makale) → %71.84
Fix 1+2 sonrası (aynı corpus) → %78.49
Softening mimarisi sonrası (50 makale, yeni corpus) → %78.3

Fark: %71.84 → %78.3 = **+6.46 puan**

---

## 5. BEKLEYEN BUG: Yuvarlaklaşma Kuralı Hatası

### Sorun:
`döwlet` + A2 iyelik → `döwletüň` üretiyor (YANLIŞ)
Doğrusu: `döwletiň`

### Kök neden:
Generator'daki `has_rounded_vowel()` fonksiyonu kök kelimede HERHANGİ BİR
yuvarlak ünlü varsa True dönüyor. `döwlet`'teki `ö` yuvarlak ünlü olduğu
için iyelik eki `iň` yerine `üň` seçiliyor. Ancak kuralın SON ünlüye bakması
lazım — `döwlet`'in son ünlüsü `e` (düz), dolayısıyla `iň` olmalı.

### Etkilenen kelimeler:
`ö`, `ü`, `u`, `o` içeren ama son hecelerinde `a`, `e`, `y`, `i` olan
çok heceli kelimeler. Örn: döwlet, hökümet, ösüş, höwes, ...

### Düzeltme:
`has_rounded_vowel()` fonksiyonu son heceye odaklanacak şekilde güncellenmeli.
Bu ayrı bir iş (softening ile ilgisiz).

### Makalenin bu bölümünde: Yapılacak iş olarak belirtilmeli (Section 5 — Future Work)

---

## 6. Veri-Odaklı Keşif Pipeline'ı (YENİ — Section 4 veya 5)

### Makaledeki yeri: Section 4.2 gibi yeni bir alt bölüm olabilir

### Yazılacak paragraf:
> **Data-Driven Exception Discovery.**
> We implemented an automated pipeline for discovering morphophonemic
> exceptions from raw text corpora. The pipeline:
> (1) fetches Turkmen news articles from metbugat.gov.tm,
> (2) tokenizes them into word forms,
> (3) for each K/P/T/Ç-ending noun in the lexicon, generates both
>     softened and unsoftened inflected forms using the morphological generator,
> (4) checks which form(s) appear in the corpus,
> (5) classifies stems as confirmed-softening, exception (no-softening),
>     ambiguous, or no-evidence.
>
> This pipeline can be re-run on larger corpora to incrementally
> refine the lexicon flags. In our initial run on 50 articles (33,153
> tokens), it identified 58 non-softening stems, 117 confirmed-softening
> stems, 2 ambiguous stems, and 6,635 stems with no corpus evidence.
