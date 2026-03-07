# Mermaid Diyagram Şablonları — §5 Sözlük Derleme Süreci

> **Kullanım:** Bu kodları https://mermaid.live adresine yapıştırarak PNG olarak indirebilirsiniz.
> Her diyagramı ayrı ayrı yapıştırın. Dikey format kullanılmıştır (TD = Top-Down).

---

## Şekil 2 — Sözlük Derleme Hattı Akış Diyagramı

**Konumu:** §5.2 Derleme Süreci paragrafından sonra, Tablo 4'ten önce.

```mermaid
flowchart TD
    subgraph BÜYÜME["📥 BÜYÜME FAZI"]
        direction TB
        K1["🌐 K1 — Wiktionary\n1.736 lemma\n(POS ground truth)"]
        A1["Çekirdek Sözlük\n1.736"]
        K1 --> A1

        K2["📖 K2 — Hunspell tk_TM\n61.974 giriş · 114 bayrak"]
        BA["Bayrak Analizi\n(Wiktionary çapraz ref.)"]
        K2 --> BA
        BA -->|"~50 grup\n≥%60 güvenilirlik"| IMP["İthalat\n+16.238"]
        BA -->|"~40 grup\natlandı"| SKIP["❌ SKIP\nTüretilmiş / Karışık"]
        A1 --> A2["38.480"]
        IMP --> A2

        K3["📄 K3 — PDF OCR\n9.240 kelime"]
        A2 --> A3["43.747"]
        K3 -->|"+5.267"| A3

        K4["📕 K4 — Orfografik Sözlük\n111.147 satır · 110.000 söz\n(Kyýasowa vd. 2016)"]
        CLS["Üç-Strateji\nSınıflandırma"]
        K4 --> CLS
        CLS -->|"+11.048"| A4["54.795"]
        A3 --> A4
    end

    subgraph TEMİZLİK["🧹 TEMİZLİK FAZI"]
        direction TB
        A4 --> C1["Türetilmiş form tespiti"]
        C1 --> C2["n? silme\n−10.615"]
        C2 --> C3["44.180"]

        K5["🏛️ K5 — enedilim.com\n20.120 headword\nResmi dil portalı"]
        K5 --> CROSS["Çapraz Kontrol"]
        C3 --> CROSS
        CROSS -->|"−15.663\nçekimli form"| C4["Temizlenmiş"]
        CROSS -->|"+8.802\nkök ekleme"| C4

        C4 --> C5["Tek harfli kök silme\n−36"]
        C5 --> FINAL["✅ NİHAİ SÖZLÜK\n32.015 giriş\n30.154 benzersiz kelime"]
    end

    style BÜYÜME fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
    style TEMİZLİK fill:#fff3e0,stroke:#e65100,stroke-width:2px
    style FINAL fill:#1b5e20,color:#fff,stroke:#1b5e20,stroke-width:3px
    style SKIP fill:#ffcdd2,stroke:#c62828
    style K1 fill:#e3f2fd,stroke:#1565c0
    style K2 fill:#e3f2fd,stroke:#1565c0
    style K3 fill:#e3f2fd,stroke:#1565c0
    style K4 fill:#e3f2fd,stroke:#1565c0
    style K5 fill:#e3f2fd,stroke:#1565c0
```

---

## Şekil 3 — Hunspell Bayrak Grubu Analiz ve Filtreleme Süreci

**Konumu:** §5.3 Hunspell Bayrak Grubu Analiz Yöntemi bölümünde, Tablo 6'dan önce.

```mermaid
flowchart TD
    HUN["Hunspell tk_TM.dic\n61.974 giriş\n114 bayrak grubu"]
    
    HUN --> ANA["Wiktionary Çapraz Referans Analizi\nHer grup → POS dağılımı hesapla"]
    
    ANA --> DEC{"Güvenilirlik\n≥ %60?"}
    
    DEC -->|"Evet"| IMP_BOX
    DEC -->|"Hayır"| SKIP_BOX
    
    subgraph IMP_BOX["✅ İTHAL EDİLEN ~50 GRUP"]
        direction TB
        N["İsim (n)\n20 grup · 13.962 kelime\nGrup 27 (%95), 38 (%96)\n54 (%100), 17 (%90)"]
        ADJ["Sıfat (adj)\n13 grup · 1.840 kelime\nGrup 30 (%92), 42 (%100)\n44 (%100), 32 (%86)"]
        NP["Özel İsim (np)\n9 grup · 310 kelime\nGrup 2 (%100), 5 (%81)\n9 (%100)"]
        V["Fiil (v)\n4 grup · 126 kök\nGrup 21, 23, 26, 33"]
    end
    
    subgraph SKIP_BOX["❌ DIŞLANAN ~40 GRUP"]
        direction TB
        S1["Türetilmiş Fiiller\nGrup 24,25,34,35,36\n~8.056 kelime\n(ettirgen -t, geçmiş -d)"]
        S2["Türetilmiş İsimler\nGrup 28, 39\n~4.881 kelime\n(-lyg/-lig ekleri)"]
        S3["Karışık POS\nGrup 0,4,37,52,62,81\n~3.589 kelime"]
        S4["Yetersiz / Nadir\n~2.621 kelime"]
    end
    
    IMP_BOX --> TOTAL["Toplam İthalat\n16.238 giriş"]
    
    style HUN fill:#bbdefb,stroke:#1565c0,stroke-width:2px
    style ANA fill:#e8eaf6,stroke:#283593
    style DEC fill:#fff9c4,stroke:#f57f17,stroke-width:2px
    style IMP_BOX fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
    style SKIP_BOX fill:#ffebee,stroke:#c62828,stroke-width:2px
    style TOTAL fill:#1b5e20,color:#fff,stroke-width:3px
    style N fill:#c8e6c9,stroke:#388e3c
    style ADJ fill:#c8e6c9,stroke:#388e3c
    style NP fill:#c8e6c9,stroke:#388e3c
    style V fill:#c8e6c9,stroke:#388e3c
    style S1 fill:#ffcdd2,stroke:#e53935
    style S2 fill:#ffcdd2,stroke:#e53935
    style S3 fill:#ffcdd2,stroke:#e53935
    style S4 fill:#ffcdd2,stroke:#e53935
```

---

## Şekil 4 — Otomatik Sözlük Doğrulama Sonuçları Özeti

**Konumu:** §5.5.3 Otomatik Doğrulama başlangıcında veya sonunda.

```mermaid
flowchart TD
    DICT["Nihai Sözlük\n32.015 giriş\n30.154 benzersiz"]
    
    DICT --> V1
    DICT --> V2
    DICT --> V3
    DICT --> V4
    
    subgraph V1["§1 GENEL KALİTE"]
        direction TB
        V1A["Duplikasyon: 0 ✅"]
        V1B["Geçersiz karakter: 475\n(%1,6 hata oranı)"]
        V1C["K4 kapsamı: %75,0\n(22.609 / 30.154)"]
    end
    
    subgraph V2["§2 HUNSPELL KÖK KONTROLÜ"]
        direction TB
        V2A["Kontrol: 26.434"]
        V2B["Doğrulanan kök:\n16.874 (%63,8) ✅"]
        V2C["Türetilmiş şüpheli:\n2.795 (%10,6)\n(kasıtlı — leksikalleşmiş)"]
    end
    
    subgraph V3["§3 POS DOĞRULUĞU"]
        direction TB
        V3A["İsim→Fiil çakışma: 19\n(tamamı multi-POS) ✅"]
        V3B["İsim→Sıfat belirsizlik: 988\n(-ly/-syz ekleri)\n(Türk dili özelliği)"]
        V3C["Hunspell POS farkı: 1.727\n(bayrak grubu sınırlılığı)"]
    end
    
    subgraph V4["§4 FİİL ÇEKİM KONTROLÜ"]
        direction TB
        V4A["6.471 kök × 9 zaman\n= 58.239 form üretildi"]
        V4B["K4 eşleşme: %1,3\n(beklenen — K4 sözlük,\nderlem değil) ✅"]
        V4C["En yüksek: FÖ ortaç\n%10,2 (leksikalleşmiş)"]
    end
    
    style DICT fill:#1565c0,color:#fff,stroke-width:3px
    style V1 fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
    style V2 fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    style V3 fill:#fff3e0,stroke:#e65100,stroke-width:2px
    style V4 fill:#f3e5f5,stroke:#6a1b9a,stroke-width:2px
```

---

## Şekil 5 — Kaynak Katkı Oranları (Pasta Grafik)

**Konumu:** §5.1 Kaynaklar bölümünde Tablo 1'den sonra (opsiyonel).

```mermaid
pie title Sözlük Kaynak Katkı Oranları (32.015 giriş)
    "K2 — Hunspell tk_TM" : 50.7
    "K5 — enedilim.com" : 27.5
    "K4 — Orfografik Sözlük" : 16.7
    "K1 — Wiktionary" : 5.1
```

---

## Şekil 6 — POS Dağılımı (Pasta Grafik)

**Konumu:** §5.6 Sözcük Türü Dağılımı bölümünde Tablo 8'den sonra (opsiyonel).

```mermaid
pie title Sözcük Türü Dağılımı (30.154 benzersiz)
    "İsim (n) — 21.798" : 68.1
    "Fiil (v) — 6.471" : 20.2
    "Sıfat (adj) — 3.094" : 9.7
    "Özel İsim (np) — 548" : 1.7
    "Diğer — 104" : 0.3
```
