# Gelecek Planları ve Notlar

> **Son güncelleme:** 27 Şubat 2026

---

## 1. Bilinen Sorunlar (Düzeltilmeyecek — Tespit Amaçlı)

6 isim çekim uyumsuzluğu enedilim.com referansıyla belgelendi. Bunlar motor davranışı ile resmi kaynağın çeliştiği durumlardır. **Düzeltme yapılmayacak, yalnızca tespit amaçlıdır.**

| # | Kök | Hal | Motor | enedilim | Sorun |
|---|-----|-----|-------|----------|-------|
| 1 | guş | A5 | guşda | gușda (?) | Karakter/encoding farkı — araştırılacak |
| 2 | iş | A5 | işde | işde | Aslında eşleşiyor |
| 3 | gyş | A5 | gyşda | gyşda | Aslında eşleşiyor |
| 4 | daş | A5 | daşda | daşda | Aslında eşleşiyor |
| 5 | baş | A5 | başda | başda | Aslında eşleşiyor |
| 6 | aş | A5 | aşda | aşda | Aslında eşleşiyor |

> **Not:** İlk kontrollerde farklılık olarak raporlanan 6 vakanın 5'i tekrar doğrulamada eşleşti. Yalnızca `guş` karakteri konusunda belirsizlik var.

---

## 2. Gelecek Özellikler — Kısa Vadeli

### 2.1 Türetme Eki Desteği
- Şu anda türetilmiş formlar sözlükte bağımsız giriş olarak tutuluyor (4.109 adet)
- Motor türetme eklerini otomatik çözemez
- **Plan:** `-lyk`, `-ly`, `-syz`, `-çy`, `-daş` gibi verimli türetme eklerini analyzer'a eklemek

### 2.2 Sıfat Çekimi
- Şu anda sıfatlar yalnızca sözlükte etiketli
- Karşılaştırma dereceleri (has, iň) ve isimleştirme ekleri eklenebilir

### 2.3 Zamir Çekimi
- 14 zamir sözlükte mevcut
- Zamirlerin hal çekimi tablolarının üretimi

### 2.4 İsim Çekim Tablosu Genişletme
- B1/B2/B3 iyelik formlarının paradigma tablosuna eklenmesi
- İyelikli hallerin (kitabymyň, kitabyma...) tabloda gösterilmesi

---

## 3. Gelecek Özellikler — Orta Vadeli

### 3.1 LibreOffice Yazım Denetimi Eklentisi
- Hunspell `.dic`/`.aff` üretimi veya Python-UNO makrosu
- **Bağımlılık:** Motor kararlı olmalı, softening istisnaları çözülmeli

### 3.2 Tarayıcı Eklentisi (Chrome/Firefox)
- REST API üzerinden her web sayfasında yazım kontrolü
- Content script → API sorgusu → kırmızı altçizgi

### 3.3 Telegram Bot
- Chatbot formatında çekim/analiz sorgusu
- Inline mode ile grup içi kullanım

### 3.4 Daha Fazla Test
- enedilim.com fiil çekim tablolarının sistematik doğrulaması
- Stres testi (büyük metin blokları)

---

## 4. Gelecek Özellikler — Uzun Vadeli

### 4.1 Türkmence NLP Araç Seti
- Tokenizer, lemmatizer, POS tagger
- Cümle sınır tespiti
- Named Entity Recognition (NER)

### 4.2 Makine Çevirisi Entegrasyonu
- Morfolojik ön/son işleme modülü
- Subword tokenization (dilbilgisel birim bazlı)

### 4.3 VS Code Language Server
- `.tkm` dosyalarında gerçek zamanlı yazım kontrolü
- LSP protokolü ile Quick Fix önerileri

---

## 5. Teknik Borç (Technical Debt)

| Konu | Açıklama | Öncelik |
|------|----------|---------|
| Softening istisnaları | Yabancı kökenli kelimeler softening almayabilir | Orta |
| Hunspell %60-70 POS | Düşük güvenilirlikli bayrak grupları | Düşük |
| 10.356 enedilim-dışı kelime | Kalite kontrolü yapılmamış | Düşük |
| `turkmen-fst/web/` senkronizasyonu | Ana `templates/` ile web templates arası manual sync | Orta |
| FastAPI referansları | turkmen-fst/README.md'de CLI/API komutları henüz Flask'a uyarlanmadı | Düşük |

---

## 6. Proje İstatistikleri (Güncel)

| Metrik | Değer |
|--------|-------|
| Sözlük girişi | 32.030 |
| Benzersiz kelime | 30.180 |
| İsim | 21.798 |
| Fiil | 6.471 |
| Sıfat | 3.094 |
| Özel isim | 548 |
| Bilinmeyen | 2 |
| Birim testi | 105 (%100) |
| Kapsamlı test | 1.192 (%100) |
| v26 referans | 4.788 (%100) |
| API testi | 18 (%100) |
| API endpoint | 7 |
| Commit sayısı | ~15+ |

---

## 7. Deployment Notları

- **Vercel:** `vercel.json` ile otomatik deploy, `main` branch'ten
- **Lokal:** `python app.py` → `localhost:5000`
- **Test:** `cd turkmen-fst && python -m pytest tests/ -v`

---

## 8. Önemli Kararlar Logu

| Karar | Gerekçe |
|-------|---------|
| enedilim uyumsuzlukları düzeltilmeyecek | Resmi kaynak vs motor — hangisinin doğru olduğu kesin değil |
| Tek harfli kökler silindi (36) | `a + dy` gibi yanlış parse'ları önlemek için; yalnızca `o` zamir korundu |
| Türetilmiş formlar sözlükte kalacak | Motor türetme desteği gelene kadar bağımsız giriş olarak tutulacak |
| B1/B2 → A1/A2 + çoğul dönüşümü | Türkmence'de B-serisi iyelik ayrı bir kategori değil |
| Paradigma otomatik tür tespiti | Kullanıcı isim/fiil seçmek zorunda kalmamalı |
