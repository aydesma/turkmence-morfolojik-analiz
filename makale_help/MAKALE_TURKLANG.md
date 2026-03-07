# TurkmenFST: Türkmen Türkçesi için Kural Tabanlı Morfolojik Analiz ve Sentez Sistemi

**Esma Aydın¹, Muhammed Kumcu²**

¹ [TODO: Kurum Bilgisi — Üniversite, Bölüm], Türkiye  
² [TODO: Kurum Bilgisi — Üniversite, Bölüm], Türkiye  
E-posta: [TODO: iletişim e-postaları]

---

## Öz

Bu çalışmada, Türkmen Türkçesi için geliştirilen kural tabanlı morfolojik analiz ve sentez sistemi TurkmenFST tanıtılmaktadır. Sonlu durum dönüştürücü (Finite-State Transducer — FST) mimarisinden ilham alan sistem, isim çekimi (6 hal × 3 iyelik × 2 çoğul), fiil çekimi (7 zaman × 6 şahıs × olumlu/olumsuz) ve çekimli kelimeden köke ulaşan morfolojik çözümleme yetenekleri sunmaktadır. Sistemin sözlük bileşeni, beş bağımsız kaynağın birleştirilmesi ve kapsamlı kalite kontrolü sonucunda oluşturulan 32.015 giriş ve 30.154 benzersiz kök kelimeden meydana gelmektedir. Fonoloji modülü, Türkmen Türkçesine özgü ünlü uyumu, ünsüz yumuşaması, ünlü düşmesi ve yuvarlaklaşma kurallarını biçimsel olarak tanımlamaktadır. Her çekim adımı, FST ilhamlı bir morfotaktik durum makinesi (state machine) üzerinden doğrulanmakta ve böylece yalnızca dilbilgisel olarak geçerli ek dizilimlerinin üretilmesi güvence altına alınmaktadır. Değerlendirme sonuçları, 4.788 referans çekim vakasında %100 doğruluk, 105 birim testinde tam başarı ve 1.192 tur-dönüş (round-trip) testinde morfolojik tutarlılık göstermektedir. Sistem, açık kaynaklı bir Python paketi olarak sunulmakta; Flask tabanlı web arayüzü, REST API ve paradigma üretimi ile dil öğrenimi, yazım denetimi ve doğal dil işleme uygulamalarına temel oluşturmaktadır.

**Anahtar kelimeler:** Türkmen Türkçesi, morfolojik analiz, morfolojik sentez, sonlu durum dönüştürücü, kural tabanlı sistem, sözlük derleme, doğal dil işleme

---

## Abstract

**TurkmenFST: A Rule-Based Morphological Analysis and Generation System for Turkmen**

In this study, we present TurkmenFST, a rule-based morphological analysis and generation system developed for the Turkmen language. Inspired by Finite-State Transducer (FST) architecture, the system provides noun inflection (6 cases × 3 possessives × 2 plurals), verb conjugation (7 tenses × 6 persons × affirmative/negative), and morphological parsing from inflected surface forms back to root morphemes. The lexicon component comprises 32,015 entries and 30,154 unique root words, compiled from five independent sources with extensive quality assurance. The phonology module formally defines vowel harmony, consonant softening, vowel elision, and rounding rules specific to Turkmen. Each inflection step is validated through an FST-inspired morphotactic state machine, ensuring that only grammatically valid suffix sequences are generated. Evaluation results demonstrate 100% accuracy across 4,788 reference inflection cases, full success in 105 unit tests, and morphological consistency in 1,192 round-trip tests. The system is provided as an open-source Python package with a Flask-based web interface, REST API, and paradigm generation, serving as a foundation for language learning, spell checking, and natural language processing applications.

**Keywords:** Turkmen language, morphological analysis, morphological generation, finite-state transducer, rule-based system, lexicon compilation, natural language processing

---

## 1. Giriş

Türk dilleri, sondan eklemeli (aglütinatif) yapılarıyla doğal dil işleme (DDİ) alanında özgün zorluklar barındırmaktadır. Bir kök kelimeye ard arda eklenen çekim ve türetme ekleri, tek bir kelimede onlarca farklı biçimbirim (morfem) taşınmasına olanak tanır. Bu durum, bilgi erişimi, makine çevirisi ve metin madenciliği gibi uygulamalarda morfolojik çözümleme ve sentez araçlarını zorunlu kılmaktadır.

Türkiye Türkçesi (Oflazer, 1994; Çöltekin, 2010; Yıldız vd., 2019), Kazakça (Kessikbayeva ve Cicekli, 2014), Kırgızca (Washington vd., 2012), Özbek Türkçesi (Bakaev ve Bakaeva, 2021) ve Tatar Türkçesi (Gökgöz ve Kurt, 2011) gibi Türk dilleri için çeşitli morfolojik çözümleyiciler geliştirilmiş olmasına karşın, Türkmen Türkçesi DDİ kaynakları açısından görece az çalışılmış bir dil konumundadır. Tantuğ, Adalı ve Oflazer (2007), Türkmence–Türkçe makine çevirisi bağlamında sonlu durum temelli bir morfolojik çözümleyiciden söz etmişlerse de bu çözümleyicinin sözlük kapsamının sınırlı olduğunu belirtmişlerdir. Günümüze değin Türkmen Türkçesi için geniş sözlük kapsamına sahip, açık kaynaklı ve kapsamlı bir morfolojik analiz/sentez sistemi kamuya açık hâle getirilmemiştir.

Bu çalışmanın temel katkıları şunlardır:

1. **Kapsamlı sözlük:** Beş bağımsız kaynağın (Wiktionary, Hunspell tk_TM, PDF OCR sözlük, orfoepik sözlük ve Türkmenistan resmi dil portalı enedilim.com) birleştirilmesiyle 32.015 kök sözcükten oluşan etiketli sözlük.
2. **Modüler motor:** Fonoloji, morfotaktik, sentez ve analiz modüllerinden oluşan ve sonlu durum otomatları mimarisinden ilham alan modüler Python paketi.
3. **İsim ve fiil çekimi:** 6 hâl × 3 iyelik × 2 çoğul isim paradigması ile 7 zaman × 6 şahıs × olumlu/olumsuz fiil paradigması.
4. **Morfolojik çözümleme:** Çekimli yüzey formunu ters mühendislikle köke ve eklere ayıran, üretici doğrulamalı analiz modülü.
5. **Açık kaynak ve web erişimi:** MIT lisansıyla kamuya açık Python paketi, Flask tabanlı web arayüzü, REST API ve canlı demo.

Makalenin geri kalanı şu şekilde düzenlenmiştir: Bölüm 2'de ilgili çalışmalar incelenmiş; Bölüm 3'te Türkmen Türkçesinin morfolojik yapısı özetlenmiş; Bölüm 4'te sistem mimarisi ayrıntılandırılmış; Bölüm 5'te sözlük derleme süreci açıklanmış; Bölüm 6'da web arayüzü ve API sunulmuş; Bölüm 7'de değerlendirme sonuçları verilmiş; Bölüm 8'de tartışma ve gelecek çalışmalar ele alınmıştır.

## 2. İlgili Çalışmalar

### 2.1. Türk Dilleri için Morfolojik Çözümleyiciler

Türk dilleri için morfolojik işleme uzun bir araştırma geçmişine sahiptir. Oflazer (1994), Türkiye Türkçesi için Xerox sonlu durum araçları kullanarak iki düzeyli (two-level) morfolojik çözümleyici geliştirmiş ve bu çalışma uzun yıllar boyunca diğer Türk dilleri için referans niteliğinde olmuştur. Çöltekin (2010) bu geleneği sürdürerek TRmorph adlı açık kaynaklı bir Türkçe morfolojik çözümleyici ortaya koymuştur. Yıldız, Avar ve Ercan (2019) ise hız ve genişletilebilirlik odaklı açık bir Türkçe morfolojik çözümleyici sunmuştur.

Diğer Türk dilleri bağlamında Washington, Ipasov ve Tyers (2012) Kırgızca için sonlu durum morfolojik dönüştürücü geliştirmiş; Washington, Salimzyanov ve Tyers (2014) bu yaklaşımı Tatarca ve Kazakça'yı da kapsayacak şekilde genişletmişlerdir. Kessikbayeva ve Cicekli (2014) Kazak dili için Xerox sonlu durum araçları ile kural tabanlı bir morfolojik çözümleyici oluşturmuşlardır. Bakaev ve Bakaeva (2021) aynı yaklaşımı Özbek Türkçesine uygulamışlardır.

### 2.2. Türkmen Türkçesi Çalışmaları

Türkmen Türkçesi özelinde DDİ çalışmaları oldukça sınırlıdır. Tantuğ, Adalı ve Oflazer (2007), Türkmence–Türkçe makine çevirisi sistemi bağlamında Türkmen morfolojik çözümleyicisinden yararlanmışlardır; ancak bu çözümleyicinin kök kelime kapsamının görece sınırlı olduğunu ve çıktılarında belirsizlikler bulunduğunu raporlamışlardır. Söz konusu sistem kamuya açık kaynak olarak paylaşılmamıştır.

Gatiatullin, Suleymanov ve Prokopyev (2024) TurkLang bilgi grafi projesinde Türkmen Türkçesini de kapsayan çok dilli dilbilimsel kaynaklar geliştirmişlerdir; ancak bu çalışma ontolojik modellemeye odaklanmakta olup bağımsız bir morfolojik çözümleyici sunmamaktadır.

Bildiğimiz kadarıyla, bu çalışma Türkmen Türkçesi için geniş sözlük kapsamına sahip (32.015 kök), açık kaynaklı ve kamuya erişilebilir ilk kapsamlı morfolojik analiz ve sentez sistemidir.

### 2.3. Sonlu Durum Morfolojisi

Beesley ve Karttunen (2003), sonlu durum morfolojisinin kuramsal çerçevesini ortaya koyan temel çalışmayı yapmışlardır. Bu yaklaşımda morfolojik kurallar, sonlu durum dönüştürücüler aracılığıyla biçimsel olarak ifade edilmekte; bir dönüştürücü girdi dizgisini (kök + ek kodları) çıktı dizgisine (yüzey formu) dönüştürmektedir. İki düzeyli morfoloji (Koskenniemi, 1983) ve Xerox sonlu durum araçları (XFST) bu alandaki standart yaklaşımlar olagelmiştir.

TurkmenFST, bu kuramsal çerçeveyi Python tabanlı bir uygulamada yeniden yorumlamaktadır. Geleneksel XFST yaklaşımından farklı olarak, fonolojik kurallar ayrı bir Python modülünde kodlanmış, ek sırası doğrulaması ise bağımsız bir durum makinesi üzerinden gerçekleştirilmiştir. Bu tasarım, araçların belirli bir sonlu durum çerçevesine bağımlılığını ortadan kaldırırken modüllerliğini ve genişletilebilirliğini artırmaktadır.

## 3. Türkmen Türkçesinin Morfolojik Yapısı

Türkmen Türkçesi, Oğuz grubuna ait sondan eklemeli bir Türk dilidir. Ses sistemi, Kiril ve Latin alfabe geçişleriyle biçimlenmiş kendine özgü özellikler taşır. Morfolojik açıdan Türkmen Türkçesi, diğer Türk dillerinde de yaygın olan ünlü uyumu, ünsüz yumuşaması ve ünlü düşmesi süreçlerini barındırmaktadır.

### 3.1. Ses Bilgisi (Fonoloji)

Türkmen Türkçesinde ünlüler art (kalın/yogyn: a, o, u, y) ve ön (ince: e, ä, ö, i, ü) ayrımına göre sınıflandırılır. Ünlü uyumu kuralı gereği, bir kelimeye eklenen ekler kökteki ünlünün kalın/ince niteliğine göre belirlenir.

Ünsüz yumuşaması sürecinde, kök sonundaki sert ünsüzler (p, ç, t, k) ünlü ile başlayan ek aldığında yumuşak karşılıklarına (b, j, d, g) dönüşür:

- *kitap* + *ym* → *kitabym* (kitabım)
- *agaç* + *yň* → *agajyň* (ağacın)

Ünlü düşmesi, belirli köklerin ek aldığında son hecedeki ünlüyü yitirmesidir:

- *burun* + *y* → *burny* (burnu)
- *ogul* + *y* → *ogly* (oğlu)

Bunların yanı sıra bazı köklerde düzensiz ünlü düşmesi görülür:

- *asyl* → *asly* (aslı)
- *mähir* → *mähri* (mehri)

Yuvarlaklaşma kuralı, yuvarlak ünlü taşıyan bazı köklerin ek aldığında ünlü değişimine uğramasını ifade eder:

- *guzy* → *guzu+sy* (kuzusu)

### 3.2. İsim Çekimi

Türkmen Türkçesinde isimler şu sırayla çekim eki alır: **KÖK + [çoğul] + [iyelik] + [hâl]**. Bu sıralama, diğer Türk dillerindeki genel yapıyı yansıtmaktadır.

**Hâl ekleri:**

| Hâl | Kod | Ek | Örnek (kitap) |
|-----|-----|-----|----------------|
| Yalın | A1 | ∅ | kitap |
| İlgi | A2 | -(n)yň | kitabyň |
| Yönelme | A3 | -(n)a | kitaba |
| Belirtme | A4 | -(n)y | kitaby |
| Bulunma | A5 | -(n)da | kitapda |
| Çıkma | A6 | -(n)dan | kitapdan |

**İyelik ekleri:**

| Kişi | Kod | Ek | Örnek (kitap) |
|------|-----|-----|----------------|
| 1. tekil | A1 | -(y)m | kitabym |
| 2. tekil | A2 | -(y)ň | kitabyň |
| 3. tekil | A3 | -(s)y | kitaby |

**Çoğul eki:** *-lar / -ler* (ünlü uyumuna tabi)

### 3.3. Fiil Çekimi

Türkmen Türkçesinde fiiller **KÖK + [olumsuzluk] + zaman + [şahıs]** sırasında çekim alır. Sistem yedi zaman kipini desteklemektedir:

| Kod | Zaman | Türkmence Adı | Örnek (gel-) |
|-----|-------|---------------|-------------|
| Ö1 | Belirli geçmiş | Anyk Öten | geldim |
| Ö2 | Belirsiz geçmiş | Daş Öten | gelipdim |
| Ö3 | Sürekli geçmiş | Dowamly Öten | gelýärdim |
| H1 | Geniş şimdiki | Umumy Häzirki | gelýärin |
| H2 | Kesin şimdiki | Anyk Häzirki | gelýän |
| G1 | Belirli gelecek | Mälim Geljek | geljek |
| G2 | Belirsiz gelecek | Nämälim Geljek | gelerin |

Her zaman kipi, altı şahıs (A1–A3 tekil, B1–B3 çoğul) ve olumlu/olumsuz biçimlerde çekimlenebilir. Olumsuzluk eki olarak *-ma / -me* kullanılmakla birlikte bazı zamanlarda olumsuzluk perifrastik (yardımcı yapıyla) ifade edilmektedir:

- Sürekli geçmiş olumsuz: *gel-ýän däldi* (analitik olumsuzluk)
- Kesin şimdiki olumsuz: *gel-ýän däldi*

## 4. Sistem Mimarisi

TurkmenFST, modüler bir yapıda tasarlanmış olup beş temel bileşenden oluşmaktadır: fonoloji modülü, sözlük yöneticisi, morfotaktik durum makinesi, sentez (üretim) motoru ve analiz (çözümleme) motoru. Şekil 1'de sistemin genel mimarisi gösterilmektedir.

```
┌──────────────────────────────────────────────────────────────┐
│                    TurkmenFST Mimarisi                       │
│                                                              │
│  ┌─────────────┐   ┌──────────────┐   ┌──────────────────┐  │
│  │  phonology   │   │   lexicon     │   │  morphotactics   │  │
│  │  .py         │   │   .py         │   │  .py             │  │
│  │             │   │              │   │                  │  │
│  │ • Ünlü uyumu│   │ • 32.015 kök │   │ • State machine  │  │
│  │ • Yumuşama  │   │ • POS etiketi│   │ • Ek sırası      │  │
│  │ • Ünlü düşme│   │ • Morfolojik │   │   doğrulaması    │  │
│  │ • Yuvarlak. │   │   özellikler │   │ • İsim/Fiil FST  │  │
│  └──────┬──────┘   └──────┬───────┘   └────────┬─────────┘  │
│         │                 │                     │            │
│         └────────┬────────┘─────────────────────┘            │
│                  ▼                                           │
│  ┌──────────────────────────────────────────────────────┐    │
│  │              generator.py (Sentez)                    │    │
│  │  Kök + Ek parametreleri → Çekimli yüzey formu        │    │
│  │  • NounGenerator  • VerbGenerator                     │    │
│  └───────────────────────┬──────────────────────────────┘    │
│                          ▼                                   │
│  ┌──────────────────────────────────────────────────────┐    │
│  │              analyzer.py (Analiz)                     │    │
│  │  Çekimli yüzey formu → Kök + Ek çözümlemesi          │    │
│  │  Strateji: Generator-doğrulamalı ters çözümleme      │    │
│  └──────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐    │
│  │  app.py — Flask Web + REST API (7 endpoint)           │    │
│  └──────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────┘
```

*Şekil 1.* TurkmenFST sistem mimarisi. Fonoloji, sözlük ve morfotaktik modülleri çekirdek bileşenleri oluşturmakta; sentez ve analiz motorları bu çekirdek üzerinde çalışmaktadır.

### 4.1. Fonoloji Modülü (phonology.py)

Fonoloji modülü, Türkmen Türkçesinin sesbilimsel kurallarını biçimsel olarak tanımlar. Modül, dört temel kural grubunu işlemektedir:

**Ünlü nitelik belirleme:** Bir kökün son ünlüsü incelenerek kalın (yogyn) veya ince niteliği belirlenir. Bu nitelik, eklerin ünlüsünü yönetir.

**Ünsüz yumuşaması:** Sert ünsüzlerin (p → b, ç → j, t → d, k → g) ünlüyle başlayan ek öncesinde değişimi. Sözlük girişindeki `softening` etiketi bu kuralın uygulanıp uygulanmayacağını belirler. 7.001 kelime bu etiketle işaretlenmiştir.

**Ünlü düşmesi:** Belirli köklerin (burun, ogul, agyz vb.) ek aldığında son hecedeki ünlüyü yitirmesi. İki alt kategori tanımlanmıştır: (i) düzenli ünlü düşmesi (20 kelime, `vowel_drop` etiketi) ve (ii) düzensiz ünlü düşmesi (5 kelime, `exception_drop` etiketi: asyl → asl, nesil → nesl, ylym → ylm, mähir → mähr, pasyl → pasl).

**Yuvarlaklaşma:** Belirli köklerde düz ünlülerin yuvarlak biçimlerle yer değiştirmesi (ör. guzy → guzu).

Bu kurallar statik veri yapıları ve fonksiyonlar olarak kodlanmış; diğer modüller tarafından doğrudan çağrılabilir hâle getirilmiştir.

### 4.2. Sözlük Modülü (lexicon.py)

Sözlük modülü, 32.015 giriş içeren metin tabanlı sözlük dosyasını yükler ve kelime sorgulama işlemlerini gerçekleştirir. Her sözlük girişi üç bileşen taşır:

```
kelime<TAB>%<POS%>[<TAB>özellikler]
```

**Örnek:**
```
kitap    %<n%>    softening
al       %<v%>
burun    %<n%>    vowel_drop
asyl     %<n%>    exception_drop:asl
at       %<n%>    softening;homonym:1=AT_(Ad,_isim)|yes;2=AT_(At,_beygir)|no
```

Sözcük türü (POS) etiketi, isim (`n`), fiil (`v`), sıfat (`adj`), özel isim (`np`) ve diğer kategorileri kapsamaktadır. Morfolojik özellikler, ünsüz yumuşaması izni, ünlü düşmesi türü ve eş seslilik bilgisini içermektedir. Eş sesli kelimeler (ör. *at* — ad/beygir; *ot* — ateş/bitki) özel `homonym` etiketi ile işaretlenmiş olup analiz ve paradigma üretiminde her iki anlamın da sunulması sağlanmaktadır.

### 4.3. Morfotaktik Durum Makinesi (morphotactics.py)

Ek sırası kuralları, Beesley ve Karttunen'in (2003) sonlu durum morfolojisi modelinden ilham alan bir durum makinesiyle biçimselleştirilmiştir. İsim ve fiil çekimleri için ayrı durum makineleri tanımlanmıştır:

**İsim FST:**
```
STEM → [PLURAL] → [POSSESSIVE] → [CASE] → FINAL
```

**Fiil FST:**
```
V_STEM → [NEGATION] → TENSE → [PERSON] → FINAL
```

Her durum geçişi bir morfolojik kategoriyle (MorphCategory) etiketlenmiştir. Durum makinesi, geçersiz ek dizilimlerini (ör. çoğuldan sonra tekrar çoğul, hâl ekinden sonra iyelik) reddederek yalnızca dilbilgisel olarak geçerli çekim yollarının üretilmesini sağlamaktadır.

Her bir durumun `is_final` özelliği, o durumda üretimin sonlandırılıp sonlandırılamayacağını belirtir. Örneğin, fiil kök durumu `is_final=False` olarak işaretlenmiştir; zaman eki eklenmeden fiil üretimi tamamlanamaz.

### 4.4. Sentez Motoru (generator.py)

Sentez motoru, kök ve ek parametrelerini alarak çekimli yüzey formunu üretir. İki ana sınıf tanımlanmıştır:

**NounGenerator:** İsim çekimi gerçekleştirir. Çekim süreci şu adımlardan oluşur:

1. Kök sözlükte aranır ve morfolojik özellikleri (softening, vowel_drop) alınır.
2. Morfotaktik durum makinesi üzerinden ek sırası doğrulanır.
3. Çoğul eki varsa *-lar/-ler* ünlü uyumuna göre eklenir.
4. İyelik eki varsa gerekli fonolojik kurallar (yumuşama, düşme) uygulanarak eklenir.
5. Hâl eki uygulanır; iyelikli/iyeliksiz duruma göre tampon ünsüz (n) belirlenir.
6. Sonuç, çekimli form ve parçalanmış ek dizisi (breakdown) olarak döndürülür.

**VerbGenerator:** Fiil çekimi gerçekleştirir. Yedi zaman kipi için farklı ek kalıpları uygulanır. Her zaman–şahıs–olumsuzluk kombinasyonu için üretim kuralları, Türkmenistan resmi dil portalı enedilim.com'daki çekim tablolarıyla doğrulanmıştır.

Üretim sonucu `GenerationResult` veri yapısıyla döndürülmekte olup çekimli kelime (`word`), parçalanmış gösterim (`breakdown`), kök (`stem`) ve uygulanan morfem listesi (`morphemes`) bilgilerini içermektedir.

### 4.5. Analiz Motoru (analyzer.py)

Analiz motoru, çekimli bir yüzey formunu kök ve ek dizisine ayırmaktadır. Sistem, **üretici doğrulamalı ters çözümleme** (reverse generation) stratejisi kullanmaktadır:

1. Giriş kelimesinin olası kök adayları sözlükten belirlenir.
2. Her kök adayı için olası tüm ek kombinasyonları sentez motoru aracılığıyla üretilir.
3. Üretilen yüzey formu giriş kelimesiyle karşılaştırılır; eşleşme durumunda analiz başarılı sayılır.

Bu yaklaşımın temel avantajı, fonolojik kuralların analiz modülünde ayrıca kodlanmasına gerek olmamasıdır; sentez motorunun kuralları dolaylı olarak devreye girer. Böylece sentez ve analiz arasında %100 tutarlılık garanti altına alınmaktadır.

Analiz sonucunda başarılı olan tüm çözümlemeler döndürülmektedir. Eş sesli kelimeler (ör. *at*: isim "ad" veya isim "beygir" veya fiil "atmak") için birden fazla çözümleme üretilebilir. Çapraz tekilleştirme (cross-deduplication) mekanizması, aynı kelimeden kaynaklanan özdeş sonuçları eleyerek kullanıcıya anlamlı ve tekrarsız çıktı sunmaktadır.

## 5. Sözlük Derleme Süreci

TurkmenFST'nin sözlük bileşeni, beş birbirinden bağımsız kaynağın 9 aşamalı bir derleme hattı (pipeline) ile birleştirilmesiyle oluşturulmuştur. Nihai sözlük 32.015 giriş ve 30.154 benzersiz kök kelime içermektedir. Bu bölümde kaynaklar, birleştirme yöntemi, kalite güvence süreçleri ve otomatik doğrulama sonuçları ayrıntılı olarak açıklanmaktadır.

### 5.1. Kaynaklar

Sözlüğü besleyen beş kaynak, güvenilirlik düzeyleri ve katkı oranlarıyla birlikte Tablo 1'de özetlenmiştir.

| # | Kaynak | Tür | Giriş Hacmi | Nihai Katkı |
|---|--------|-----|-------------|-------------|
| K1 | Wiktionary (en) | Kitle kaynaklı çevrimiçi sözlük | 1.736 lemma | 1.649 (%5,1) |
| K2 | Hunspell tk_TM.dic | Yazım denetimi sözlüğü | 61.974 giriş | 16.238 (%50,7) |
| K3 | PDF OCR Sözlük | Basılı Türkmence–İngilizce sözlük | 9.240 kelime | ~0 (dolaylı) |
| K4 | Orfografik Sözlük | Resmi yazım kılavuzu (110.000 söz) | 111.147 satır | 5.362 (%16,7) |
| K5 | enedilim.com | Türkmenistan resmi dil portalı | 20.120 headword | 8.802 (%27,5) |
| | | | **Toplam** | **32.015** |

*Tablo 1.* Sözlük kaynaklarının ham hacmi ve nihai sözlüğe katkıları.

#### 5.1.1. K1 — Wiktionary

Çekirdek sözlük, İngilizce Wiktionary'nin MediaWiki API'si üzerinden otomatik olarak elde edilmiştir. `Turkmen nouns`, `Turkmen verbs`, `Turkmen adjectives` kategori ağaçları taranarak 1.736 lemma çekilmiş ve her bir girdinin sözcük türü doğrudan kategori etiketinden atanmıştır. Bu kaynak iki temel işlev görmüştür: (i) ilk çekirdek sözlüğü oluşturmak, (ii) sonraki Hunspell ithalatında "doğruluk tabanı" (ground truth) olarak POS dağılım karşılaştırması yapmak.

#### 5.1.2. K2 — Hunspell tk_TM

Hunspell yazım denetimi sözlüğü (`tk_TM.dic`, 61.974 giriş; `tk_TM.aff`, 9.796 satır) 114 bayrak grubundan oluşmaktaydi. Hunspell formatında bayrak grupları doğrudan POS bilgisi taşımadığından, her grup için Wiktionary ile çapraz kontrol yapılarak POS dağılımı ve güvenilirlik oranı hesaplanmıştır. Bu süreç iki aşamadan oluşmaktadır:

**Aşama A — Çapraz referans analizi:** Her bayrak grubundaki kelimelerin kaçının Wiktionary'de hangi POS ile kayıtlı olduğu belirlenmiştir. Örneğin Grup 27'deki 3.064 kelimenin %95'i Wiktionary'de isim, Grup 30'daki 457 kelimenin %92'si sıfat olarak yer almaktaydı.

**Aşama B — Eşik tabanlı seçim:** Güvenilirlik oranı %60 ve üzerinde olan yaklaşık 50 grup ithal edilmek üzere seçilmiş; kalan ~40 grup bilinçli olarak dışlanmıştır. Dışlanan grupların başlıca nedenleri Tablo 2'de sunulmaktadır.

| Dışlama Nedeni | Örnek Gruplar | Kelime Sayısı | Açıklama |
|----------------|---------------|---------------|----------|
| Türetilmiş fiil formları | 24, 25, 34, 35, 36 | ~8.056 | Ettirgen (-t/-let), geçmiş (-d), kısaltma (-l) |
| Türetilmiş isim formları | 28, 39 | ~4.881 | -lyg/-lig ekli formlar |
| Karışık POS | 0, 4, 37, 52, 62, 81 | ~3.589 | İsim+sayı, bağlaç+zarf karışık |
| Yetersiz eşleşme | 12, 31, 41, 45, 49, 57, ... | ~2.594 | Wiktionary eşleşme oranı çok düşük |
| Az girdili gruplar | 15, 16, 18, 51, 72, 97 | ~27 | İstatistiksel olarak anlamsız |

*Tablo 2.* Hunspell'den dışlanan bayrak grubu kategorileri ve gerekçeleri.

Bu tasarım kararının ardındaki temel ilke, türetilmiş formların (ör. ettirgen *agart-*, isim *adalyg*) sözlüğe ayrı kök olarak eklenmemesidir. Morfolojik motor bu ekleri zaten üretken biçimde uygulayabildiğinden, türetilmiş bir formu bağımsız giriş olarak kaydetmek hem artıklık yaratır hem de analiz motorunda yanlış çözümlemeye neden olur. Sonuç olarak Hunspell'den ithal edilen 16.238 giriş; 13.962 isim, 1.840 sıfat, 310 özel isim ve 126 fiil kökünden oluşmaktadır.

#### 5.1.3. K3 — PDF OCR Sözlük

Basılı bir Türkmence–İngilizce sözlük, RapidOCR ile sayısallaştırılmıştır. Toplam 9.240 kelime elde edilmiş olmakla birlikte, OCR çıktısı POS bilgisi içermediğinden bu kelimelerin çoğunluğu sonraki temizlik aşamalarında elenmiştir. K3 kaynağının asıl katkısı, diğer kaynaklardan gelen kelimelerin mevcudiyet doğrulamasını sağlamak olmuştur.

#### 5.1.4. K4 — Orfografik Sözlük

Türkmenistan Ylymlar Akademiyası'nın Magtymguly adlı Dil ve Edebiyat Enstitüsü tarafından hazırlanan *Türkmen diliniň orfografik sözlügi* (Kyýasowa, Geldimyradow ve Durdyýew, 2016), 110.000'den fazla sözcüğü kapsayan resmi yazım kılavuzudur. Sözlük, asıl ve türetilmiş sözcükleri, fiilleri, sıfatları ve çeşitli yapım ekleriyle oluşturulan formları içermekte; yalnızca doğru yazılışları göstermekte, anlamları veya gramer bilgisi vermemektedir. 1962, 1963 ve 1989 tarihli önceki orfografik sözlüklere dayanmakta olup Türkmenistan'ın II. Lingüistik Kurultayı'nın orfografi kararlarını esas almaktadır.

Bu kaynak, dijital ortamda 111.147 satır olarak işlenmiştir. Dosyadaki giriş türleri şu şekilde sınıflanmaktadır:

| Giriş Türü | Gösterim | Örnek | Sayı |
|-------------|----------|-------|------|
| Fiil kökü | tire ile biten | *gel-*, *al-*, *oka-* | 13.418 |
| Türetilmiş isim | boru (|) notasyonu | *abadançyly\|k, -gy* | — |
| Basit sözcük | düz metin | *adam*, *kitap* | 40.897 |

*Tablo 3.* Orfografik sözlüğün dijital dosyasındaki giriş türleri.

Sınıflandırma üç ardışık strateji ile yapılmıştır: (i) tire ile biten girdiler otomatik olarak fiil kökü etiketlenmiş, (ii) Hunspell ile çapraz referans üzerinden POS belirlenmiş, (iii) kalan girdiler son-ek sezgisel kurallarıyla (heuristic) sınıflandırılmıştır. Türetilmiş formlar filtrelendikten sonra 5.362 giriş (5.224 isim) nihai sözlüğe dahil edilmiştir.

#### 5.1.5. K5 — enedilim.com

enedilim.com, Türkmenistan devletinin resmi dil portalıdır ve bu çalışmada en güvenilir kaynak olarak kabul edilmiştir. Portaldan 20.120 başlık kelimesi (headword) taranmış; bunların 6.461'i fiil mastarı, 13.659'u isim/sıfat/diğer giriş olarak tespit edilmiştir. Bu kaynağın kritik katkıları şunlardır:

1. Sözlüğümüzdeki 31.414 kelimenin POS bilgisi portal API'si üzerinden sorgulanarak kapsamlı çapraz doğrulama yapılmıştır.
2. Nihai sözlükteki 6.471 fiil kökünün **tamamı** enedilim.com tarafından doğrulanmıştır.
3. Portal çekim tablosu API'si sunduğundan, her fiilin paradigması kontrol edilmiş; motorumuzda 8 çekim kuralı düzeltmesi bu karşılaştırmadan çıkmıştır (bkz. Bölüm 7.4).

### 5.2. Derleme Süreci

Sözlük derleme hattı, büyüme ve temizlik olmak üzere iki ana fazdan oluşmaktadır (Şekil 2). Süreç, 8 Python scripti ve 1 manuel müdahale ile toplam 9 aşamada tamamlanmıştır.

[Şekil 2 — Sözlük derleme hattı akış diyagramı. (Bkz. Mermaid şablonu.)]

#### 5.2.1. Büyüme Fazı (Aşama 1–4)

| Aşama | Kaynak | İşlem | Kümülatif Boyut |
|-------|--------|-------|-----------------|
| 1 | K1 — Wiktionary | MediaWiki API ile çekirdek oluşturma | 1.736 |
| 2 | K2 — Hunspell | Bayrak analizi + eşik tabanlı ithalat | 38.480 |
| 3 | K3 — PDF OCR | RapidOCR ile birleştirme | 43.747 |
| 4 | K4 — Orfografik Söz. | Üç-strateji sınıflandırma ile ekleme | 54.795 |

*Tablo 4.* Büyüme fazı aşamaları ve kümülatif sözlük boyutu.

#### 5.2.2. Temizlik Fazı (Aşama 5–9)

| Aşama | İşlem | Değişim | Kümülatif |
|-------|-------|---------|-----------|
| 5 | Türetilmiş form tespiti ve etiketleme | — | 54.795 |
| 6 | POS etiketi belirsiz (`n?`) girdilerin silinmesi | −10.615 | 44.180 |
| 7 | enedilim.com çapraz kontrol; çekimli/türetilmiş fiil silme | −15.663 | 28.517 |
| 8 | Doğrulanmış fiil kökü + isim ekleme (enedilim) | +8.802 | 37.319* |
| 9 | Tek harfli kök silme (analiz belirsizliği) | −36 | **32.015** |

*Tablo 5.* Temizlik fazı aşamaları. (*) Aşama 7 ve 8 tek script içinde gerçekleştirilmiştir; ara toplam nettir.

POS etiketi belirsiz 10.615 girdinin silinmesi (Aşama 6) önemli bir tasarım kararıdır. Hunspell ve PDF OCR kaynaklarından gelen bu girişlere güvenilir bir sözcük türü atanamadığından, belirsiz etiketli (`n?`) verilerin morfolojik motorda yanlış çekim üretmesi riski görülmüş ve kalite lehine kapsam daraltılmıştır.

enedilim.com ile yapılan çapraz kontrolde (Aşama 7–8), sözlükte çekimli form olarak bulunan 15.663 fiil girişi (ör. *gelýär*, *alyndy* gibi yüzey formları) kaldırılmış; bunların yerine 5.997 doğrulanmış fiil kökü ve 2.805 isim eklenmiştir. Bu adım, sözlüğün "kök sözlük" (stem lexicon) niteliğine kavuşmasında belirleyici olmuştur.

Son olarak Aşama 9'da, 36 tek harfli kök girişi analiz motorunda aşırı belirsizlik yarattığından kaldırılmıştır (yalnızca zamir *o* korunmuştur). Örneğin, tek harfli kök *a* mevcut olduğunda analiz motoru gerçekte *a+dy* = "adı" ayrıştırması üretmekte ve pek çok kelime için yanlış pozitifler ortaya çıkmaktaydı.

### 5.3. Hunspell Bayrak Grubu Analiz Yöntemi

Hunspell yazım denetimi sözlükleri, her kelimeye bir veya daha fazla bayrak numarası atayarak çekim ve türetme kurallarını belirtir. tk_TM sözlüğünde 114 farklı bayrak grubu bulunmaktadır. Bu bayrak grupları yapısal olarak POS bilgisi içermediğinden, her grubun baskın sözcük türünü belirlemek üzere özgün bir çapraz referans yöntemi geliştirilmiştir.

Yöntem şu adımlardan oluşur:

1. **Wiktionary örtüşme hesabı:** Her bayrak grubundaki kelimelerin Wiktionary'deki POS dağılımı hesaplanır. Örneğin, Grup 27'deki 3.064 kelimeden 2.911'i Wiktionary'de isim olarak kayıtlıysa, bu grubun güvenilirlik oranı %95 olarak belirlenir.

2. **POS atama:** Grubun baskın POS kategorisi, güvenilirlik oranı %60 eşiğini aşıyorsa atanır. Aksi hâlde grup atlanır (SKIP).

3. **Türetilmiş form filtreleme:** Bayrak grubunun .aff dosyasındaki ek kuralları incelenir. Eğer grup sistematik olarak türetme eki ekliyorsa (ör. Grup 24: ettirgen *-t*, Grup 28: isimleştirme *-lyg*), bu gruptaki kelimelerin tümü kök değil türetilmiş form kabul edilerek dışlanır.

İthal edilen ana bayrak grupları ve güvenilirlik oranları Tablo 6'da özetlenmiştir.

| POS | Grup Sayısı | Temsili Gruplar (güvenilirlik) | Toplam Kelime |
|-----|-------------|-------------------------------|---------------|
| İsim (n) | 20 | 27 (%95), 38 (%96), 54 (%100), 17 (%90) | 13.962 |
| Sıfat (adj) | 13 | 30 (%92), 42 (%100), 44 (%100), 32 (%86) | 1.840 |
| Özel isim (np) | 9 | 2 (%100), 5 (%81), 9 (%100) | 310 |
| Fiil (v) | 4 | 21, 23, 26, 33 (kök formlar) | 126* |

*Tablo 6.* Hunspell'den ithal edilen bayrak gruplarının POS dağılımı. (*) Hunspell'deki fiil grupları çekimli form ağırlıklıdır; kök olarak yalnızca 126 giriş nihai sözlüğe kabul edilmiştir. Fiil köklerinin büyük çoğunluğu K5 (enedilim.com) kaynağından gelmiştir.

### 5.4. Morfolojik Etiketleme

Sözlükteki her giriş, sözcük türü (POS) etiketinin yanı sıra morfolojik özellik etiketleriyle de işaretlenmiştir. Bu etiketler, çekim motorunun fonolojik kuralları doğru uygulaması için gereklidir. Her giriş şu formatta saklanmaktadır:

```
kelime<TAB>%<POS%>[<TAB>özellikler]
```

Örnek girdiler:

```
kitap    %<n%>    softening
burun    %<n%>    vowel_drop
asyl     %<n%>    exception_drop:asl
at       %<n%>    softening;homonym:1=AT_(Ad)|yes;2=AT_(At)|no
gözel    %<adj%>
```

Morfolojik özellik etiketlerinin türleri ve sözlükteki dağılımları Tablo 7'de gösterilmiştir.

| Özellik | Açıklama | Sayı |
|---------|----------|------|
| `softening` | Sert ünsüz (p/ç/t/k) yumuşaması uygulanan kökler | 7.001 |
| `vowel_drop` | Ünlü düşmesi adayları (burun→burn, ogul→ogl) | 20 |
| `exception_drop` | Düzensiz ünlü düşmesi (asyl→asl, mähir→mähr) | 5 |
| `homonym` | Eş sesli kelime bilgisi (at: ad/beygir, ot: ateş/bitki) | 6 |
| `rounding` | Yuvarlaklaşma (guzy→guzu, süri→sürü) | 3 |

*Tablo 7.* Sözlükteki morfolojik özellik etiketleri, açıklamaları ve sayıları.

Eş sesli kelimeler (`homonym`) özellikle dikkat gerektirmektedir. Örneğin *at* kökü için iki farklı anlam tanımlanmış olup yumuşama izni anlama göre farklılık gösterir: "A:T" (ad, isim) anlamında yumuşama uygulanırken (ör. *adym*), "AT" (beygir) anlamında uygulanmaz (ör. *atym*). Paradigma üretiminde her iki anlam ayrı tablo olarak sunulmaktadır.

### 5.5. Kalite Güvencesi ve Otomatik Doğrulama

Sözlüğün kalitesi, derleme süreci boyunca 12 farklı doğrulama yöntemi ile güvence altına alınmıştır. Bu yöntemler üç katmanda düzenlenmiştir: (a) derleme sırasında uygulanan kontroller, (b) derleme sonrası çapraz doğrulamalar ve (c) otomatik doğrulama scripti ile gerçekleştirilen kapsamlı testler.

#### 5.5.1. Derleme Sırasında Uygulanan Kontroller

1. **Hunspell bayrak analizi:** 114 bayrak grubunun tamamı Wiktionary POS dağılımı ile karşılaştırılmış; yalnızca güvenilirlik oranı ≥%60 olan ~50 grup ithal edilmiştir.
2. **Türetilmiş form filtreleme:** Hunspell'in ettirgen (-t), geçmiş zaman (-d), isimleştirme (-lyg/-lig) gibi türetme eki uygulayan ~12.937 girdisi sözlüğe dahil edilmemiştir.
3. **Çekimli form silme:** enedilim.com çapraz kontrolünde, sözlükte kök yerine çekimli form olarak bulunan 15.663 fiil girişi kaldırılmıştır.
4. **Tek harfli kök temizliği:** 36 tek harfli kök, analiz motorunda aşırı belirsizlik yarattığından silinmiştir.

#### 5.5.2. Derleme Sonrası Çapraz Doğrulamalar

5. **enedilim.com kapsama doğrulaması:** Portaldaki 20.120 başlık kelimesinin tamamının sözlükte bulunduğu doğrulanmıştır (%100 kapsama).
6. **enedilim.com POS doğrulaması:** POS bilgisi dönen 58 kelime örnekleminin tamamı sözlüğümüzde doğru etiketlenmiştir (sıfır uyumsuzluk).
7. **Çoğul form kontrolü:** Sözlükteki tüm *-lar/-ler* sonekli kelimeler taranmış; kökü mevcut olan 49 çoğul form tespit edilerek kaldırılmıştır.

#### 5.5.3. Otomatik Doğrulama

Son aşamada, dört bölümden oluşan kapsamlı bir doğrulama scripti geliştirilmiş ve sözlüğün tamamı üzerinde çalıştırılmıştır. Bu doğrulamanın sonuçları aşağıda sunulmaktadır.

**Genel kalite metrikleri:**

| Metrik | Sonuç |
|--------|-------|
| Benzersiz kelime | 30.154 |
| Tekrar eden giriş (duplikasyon) | 0 |
| Orfografik sözlük (K4) kapsamı | %75,0 (22.609/30.154) |
| Fiil kökü kapsamı (K4'te tire ile biten) | %49,8 (3.225/6.471) |
| Geçersiz karakter içeren giriş | 475 (%1,6) |

Geçersiz karakter içeren 475 girdinin çoğunluğu OCR hataları (Kiril harfler: *-лер*), kodlama bozuklukları (*altьn*, *bä¢*) ve Türkmen Latin alfabesinde bulunmayan harflerden (*x*, *v*, *c*) kaynaklanmaktadır.

**Hunspell kök doğrulaması:** Sözlüğümüzden Hunspell'de de yer alan 26.434 kelimenin orfografik sözlükle çapraz kontrolü yapılmıştır. 16.874 kelime kök olarak doğrulanmış; 2.795 kelime orfografik sözlüğün boru (|) notasyonuyla işaretlediği türetilmiş formlar olarak tespit edilmiştir. Türetilmiş form olarak işaretlenen bu kelimelerin (ör. *azatlyk*, *balykçy*, *garaşsyzlyk*) sözlüğümüzde bağımsız giriş olarak tutulması bilinçli bir karardır; motor henüz türetme morfolojisini desteklemediğinden, bu kelimeler silinmesi hâlinde çekim ve analiz dışında kalacaktır. Ayrıca bu sözcükler Türkmen dilinde leksikalleşmiş formlar olarak kabul görmektedir.

**POS etiketi doğruluğu:** İsim etiketli olup orfografik sözlükte fiil kökü (tire-ekli) olarak da bulunan yalnızca 19 kelime tespit edilmiştir (*bag*, *garyn*, *ýel*, *gözel*, *ýaman* vb.). Bunların tamamı dilbilimsel olarak çok kategorili (multi-POS) kelimeler olup gerçek bir etiketleme hatası bulunmamaktadır. Öte yandan 988 isim etiketli kelime sıfat türeten ek (*-ly/-li/-syz/-siz*) taşımaktadır. Bu durum, Türk dillerinde *-ly/-li* (sahiplik) ve *-syz/-siz* (yoksunluk) ekli sözcüklerin hem isim hem sıfat işlevi görebilmesi ile açıklanır ve Türkmen Türkçesine özgü bir sorun değildir.

**Fiil çekim doğrulaması:** Sözlükteki 6.471 fiil kökü üzerinden 9 farklı zaman/kip ile toplam 58.239 çekimli form üretilmiş ve orfografik sözlük (K4) ile karşılaştırılmıştır. Eşleşme oranı %1,3 (785/58.239) olarak ölçülmüştür. Bu düşük oran **beklenen ve doğru** bir sonuçtur: orfografik sözlük bir sözcük listesidir, derlem (corpus) değildir; dolayısıyla *aldy*, *gelýär*, *bolaryn* gibi çekimli formlar madde başı olarak yer almaz. Eşleşen formlar dilbilimsel açıdan anlamlıdır: en yüksek eşleşme %10,2 ile geçmiş zaman ortaçları (*-an/-en*; ör. *açylan*, *gelen*) ve %1,0 ile gelecek zaman formu (*-ar/-er*; ör. *açar*, *salar*) görülmektedir. Bu ortaçlar ve geniş zaman formları, Türkmen dilinde sıfat veya isim olarak leksikalleşerek sözlüğe bağımsız madde başı olarak girmiştir. Düşük eşleşme oranı, sözlüğümüzün "kök sözlük" niteliğinde olduğunu — yani çekimli formların motor tarafından kurallarla üretildiğini — teyit etmektedir.

### 5.6. Sözcük Türü Dağılımı

Nihai sözlükteki sözcük türü dağılımı Tablo 8'de sunulmaktadır.

| POS | Sayı | Oran |
|-----|------|------|
| İsim (n) | 21.798 | %68,1 |
| Fiil (v) | 6.471 | %20,2 |
| Sıfat (adj) | 3.094 | %9,7 |
| Özel isim (np) | 548 | %1,7 |
| Diğer (adv, num, pro, vb.) | 104 | %0,3 |
| **Toplam** | **32.015** | **%100** |

*Tablo 8.* Nihai sözlükteki sözcük türü dağılımı.

İsim ağırlıklı dağılım (%68,1), Türk dillerinin aglütinatif yapısının doğal bir yansımasıdır. Fiil köklerinin %20,2 oranında yer alması, sınırlı sayıda fiil kökünün geniş bir çekim uzayını karşıladığını göstermektedir: 6.471 kök × 7 zaman × 6 şahıs × 2 kutup = teorik olarak 542.364 çekimli form üretebilmektedir.

### 5.7. Orfografik Sözlük ile Kapsam Karşılaştırması

Orfografik sözlük (K4), 110.000 sözcükle bu çalışmadaki en geniş kapsamlı referans kaynağıdır. Sözlüğümüzün bu referansla örtüşme oranına ilişkin analiz, sözlüğün kapsamını ve sınırlılıklarını değerlendirmek için önemlidir.

| Metrik | Değer |
|--------|-------|
| Orfografik sözlük benzersiz söz (tahmini) | ~101.986 |
| Orfografik sözlükteki fiil kökü | 13.418 |
| Sözlüğümüzden orfografik sözlükte bulunan | 22.609 (%75,0) |
| Sözlüğümüzdeki fiillerden orfografik sözlükte bulunan | 3.225 (%49,8) |
| Orfografik sözlükteki fiil kökleri bizde bulunmayan | 10.142 |

*Tablo 9.* TurkmenFST sözlüğünün orfografik sözlükle kapsam karşılaştırması.

%75'lik genel kapsam oranı değerlendirilirken, örtüşmeyen %25'in (7.545 kelime) büyük bölümünün özel isimler (orfografik sözlükte sınırlı), teknik terimler ve yabancı kökenli sözcüklerden oluştuğu not edilmelidir. Ayrıca orfografik sözlüğün boru (|) ve parantez gibi özel notasyonları, tam metin eşleştirmesinde yapay "bulunamadı" sonuçları üretebilmektedir. Fiil kapsamının %49,8'de kalması ise iki kaynağın farklı kapsam ve notasyon sistemi kullanmasından kaynaklanmaktadır; sözlüğümüzdeki tüm fiil kökleri enedilim.com üzerinden %100 doğrulanmıştır.

Orfografik sözlükte olup sözlüğümüzde bulunmayan 10.142 fiil kökü, genişleme için önemli bir fırsat sunmaktadır. Bu köklerin eklenmesi, gelecek çalışmalar (Bölüm 8.2) kapsamında değerlendirilecektir.

## 6. Web Arayüzü ve API

Sistem, Flask çerçevesi üzerinde çalışan bir web uygulaması ve RESTful API olarak sunulmaktadır. Uygulama Vercel platformuna dağıtılmış olup `https://turkmence-morfolojik-analiz.vercel.app/` adresinden erişilebilir durumdadır.

### 6.1. Web Arayüzü

Web arayüzü dört sekmeden oluşmaktadır:

1. **İsim Çekimi (At çekimi):** Kullanıcı kök kelime, hâl, iyelik ve çoğul parametrelerini seçerek çekimli formu ve parçalanmış gösterimini görebilmektedir.

2. **Fiil Çekimi (Işlık çekimi):** Kök fiil, zaman, şahıs ve olumsuzluk parametreleriyle çekim formu üretilmektedir.

3. **Morfolojik Analiz (Derňew):** Kullanıcı tarafından girilen kelime veya cümle morfolojik bileşenlerine ayrıştırılmakta; kök, ekler ve ek türleri görselleştirilmektedir.

4. **Paradigma:** Bir kelimenin tam çekim tablosu otomatik olarak üretilmektedir. Sistem, sözlüğe bakarak kelimenin sözcük türünü (isim/fiil) otomatik belirlemekte; eş sesli kelimeler (ör. *at*) için hem isim hem fiil paradigmalarını birlikte sunmaktadır.

### 6.2. REST API

Sistem, 7 RESTful endpoint sunmaktadır:

| Endpoint | Yöntem | İşlev |
|----------|--------|-------|
| `/api/health` | GET | Sağlık kontrolü ve sözlük istatistikleri |
| `/api/generate/noun` | POST | İsim çekimi üretimi |
| `/api/generate/verb` | POST | Fiil çekimi üretimi |
| `/api/analyze` | POST | Morfolojik ayrıştırma |
| `/api/lexicon/<word>` | GET | Sözlük girişi sorgulama |
| `/api/spellcheck` | POST | Yazım denetimi ve öneri |
| `/api/paradigm` | POST | Paradigma tablosu üretimi |

*Tablo 10.* REST API endpointleri.

API, JSON formatında istek alıp yanıt döndürmekte; böylece dış uygulamalar (mobil uygulama, tarayıcı eklentisi, chatbot vb.) ile entegrasyona olanak tanımaktadır.

## 7. Değerlendirme

### 7.1. Sentez Doğruluğu

Sentez motorunun doğruluğu, v26.0 referans çekim tablosunda yer alan 4.788 isim çekim vakası üzerinden değerlendirilmiştir. Referans tablosu, seçilmiş kök kelimeler üzerinden tüm hâl × iyelik × çoğul kombinasyonlarının el ile doğrulanmış çıktılarını içermektedir.

| Test Seti | Test Sayısı | Başarılı | Doğruluk |
|-----------|-------------|----------|----------|
| v26 referans çekim | 4.788 | 4.788 | %100 |
| Birim testleri | 105 | 105 | %100 |
| Round-trip testler | 1.192 | 1.192 | %100 |
| API endpointleri | 18 | 18 | %100 |

*Tablo 11.* Değerlendirme sonuçları.

**v26 referans doğrulama:** 4.788 çekim vakasının tamamında motor çıktısı referans sonuçlarla birebir eşleşmektedir.

**Birim testleri:** 105 pytest birim testi; fonoloji kuralları (36 test), morfotaktik durum makinesi (33 test), sentez motoru (15 test + 4.788 referans) ve analiz motoru (21 test) olmak üzere dört modülü kapsamaktadır.

**Round-trip (tur-dönüş) testleri:** 1.192 kelime üretilmiş, ardından analiz motoruna verilmiş ve çıktısının orijinal parametrelerle tutarlılığı doğrulanmıştır. Bu test, sentez ve analiz modülleri arasındaki tutarlılığı ölçmektedir.

### 7.2. Analiz Kapsamı

Analiz motoru, üretici doğrulamalı stratejisi nedeniyle sentez motorunun ürettiği her formu çözümleyebilmektedir. Bununla birlikte, sözlükte bulunmayan kök kelimeler için analiz yapılamamaktadır. Sözlüğün 32.015 kök kelime içermesi ve enedilim.com'un 20.120 başlık kelimesinin tamamını kapsaması, yüksek düzeyde kapsama sağlamaktadır.

### 7.3. Diğer Sistemlerle Karşılaştırma

Doğrudan karşılaştırma için Türkmen Türkçesine özgü açık kaynaklı bir morfolojik çözümleyici bulunmamaktadır. Bununla birlikte, Tablo 12'de kardeş Türk dilleri için geliştirilmiş çözümleyicilerin sözlük kapsamları sunulmaktadır:

| Sistem | Dil | Sözlük Boyutu | Yaklaşım |
|--------|-----|---------------|----------|
| TurkmenFST (bu çalışma) | Türkmen | 32.015 kök | Kural tabanlı, Python |
| Tantuğ vd. (2007) | Türkmen | ~1.200 kök* | FST (Xerox) |
| Oflazer (1994) | Türkçe | ~30.000+ kök | İki düzeyli, XFST |
| TRmorph (Çöltekin, 2010) | Türkçe | ~50.000+ kök | FST (foma) |
| Washington vd. (2012) | Kırgızca | ~14.000 kök | FST (lttoolbox) |
| Kessikbayeva & Cicekli (2014) | Kazakça | ~35.000 kök | İki düzeyli, XFST |
| Bakaev & Bakaeva (2021) | Özbekçe | ~1.200 kök | FST (Xerox) |

*Tablo 12.* Türk dilleri morfolojik çözümleyicilerinin karşılaştırması. (*Tantuğ vd.'nin bildirdiği yaklaşık değer.)

[TODO: Karşılaştırma tablosundaki sözlük boyut değerleri kesin rakamlarla doğrulanmalıdır. Bazı değerler ilgili makalelerdeki yaklaşık ifadelerden çıkarılmıştır.]

### 7.4. Fiil Çekim Doğrulaması

Fiil çekim kuralları enedilim.com'daki paradigma tablolarıyla karşılaştırılmış ve 8 düzeltme yapılmıştır:

1. Belirsiz geçmiş (Ö2) olumsuz: *-madym* → *-mändim*
2. Belirsiz geçmiş (Ö2) çoğul olumsuz: ince ünlü uyumu düzeltmesi
3. Sürekli geçmiş (Ö3) olumsuz: *-mýärdi* → *-ýän däldi* (analitik olumsuzluk)
4. Sürekli geçmiş (Ö3) B3 olumlu: çoğul eki düzeltmesi
5. Kesin şimdiki (H2) olumsuz biçim düzeltmesi
6. Belirli gelecek (G1) A1 olumlu: *-jak* → *-jakdyryn*

Bu düzeltmeler, resmi kaynak verilerine dayalı ampirik doğrulamayı yansıtmaktadır.

## 8. Tartışma ve Gelecek Çalışmalar

### 8.1. Katkılar ve Sınırlılıklar

TurkmenFST, Türkmen Türkçesi için bildiğimiz kadarıyla en geniş kapsamlı açık kaynaklı morfolojik çözümleyici ve üreticidir. 32.015 kök kelimelik sözlüğü, Tantuğ vd.'nin (2007) ~1.200 kökle çalışan sisteminin yaklaşık 27 katı büyüklüğündedir. Sistemin modüler mimarisi, yeni dil kurallarının ve sözlük genişletmelerinin bağımsız olarak eklenebilmesine olanak tanımaktadır.

Bununla birlikte, bazı sınırlılıklar mevcuttur:

1. **Türetme eki desteği yoktur.** Sistem yalnızca çekim (inflection) morfolojisini kapsamaktadır; türetme (derivation) morfolojisi henüz desteklenmemektedir. Sözlükteki 4.109 türetilmiş form bağımsız giriş olarak tutulmaktadır.

2. **Ünsüz yumuşaması istisnaları:** Son harfi k, p, t, ç olan tüm isimlere otomatik yumuşama uygulanmaktadır. Bazı yabancı kökenli kelimelerin yumuşama almama durumu henüz sistematik olarak işaretlenmemiştir.

3. **Sözlük kalite farklılıkları:** enedilim.com kapsamındaki 19.827 kelime en yüksek güvenilirliğe sahipken, diğer kaynaklardan gelen 10.356 kelimede POS doğruluğu daha düşük olabilir.

4. **Sıfat ve zamir çekimi:** Sıfat karşılaştırma dereceleri ve zamir hâl çekimi henüz kapsam dışındadır.

### 8.2. Gelecek Çalışmalar

Kısa vadede türetme eklerinin (*-lyk, -ly, -syz, -çy, -daş*) analiz modülüne eklenmesi, sıfat karşılaştırma ve zamir çekim desteğinin geliştirilmesi planlanmaktadır.

Orta vadede LibreOffice yazım denetimi eklentisi, tarayıcı uzantısı ve eğitim amaçlı etkileşimli modüller üzerinde çalışılması hedeflenmektedir.

Uzun vadede, TurkmenFST'nin ürettiği morfolojik ayrıştırma verisinin makine öğrenimi tabanlı DDİ araçlarının (POS etiketleyici, bağımlılık ayrıştırıcı, adlandırılmış varlık tanıma) eğitim verisini zenginleştirmesi; ayrıca makine çevirisi sistemlerinde morfolojik ön/son işleme modülü olarak kullanılması öngörülmektedir.

## 9. Sonuç

Bu çalışmada, Türkmen Türkçesi için kapsamlı bir kural tabanlı morfolojik analiz ve sentez sistemi olan TurkmenFST sunulmuştur. Sistem, 32.015 kök kelimelik zenginleştirilmiş sözlük, FST ilhamlı morfotaktik durum makinesi, modüler fonoloji kuralları, isim (6 hâl × 3 iyelik × 2 çoğul) ve fiil (7 zaman × 6 şahıs × olumlu/olumsuz) çekim motorları, üretici doğrulamalı analiz modülü ve web/API erişim katmanından oluşmaktadır. 4.788 referans çekim vakasında %100 doğruluk, 105 birim testinde tam başarı ve 1.192 tur-dönüş testinde morfolojik tutarlılık elde edilmiştir.

TurkmenFST, MIT lisansıyla açık kaynak olarak sunulmaktadır ve `https://github.com/aydesma/turkmence-morfolojik-analiz` adresinden erişilebilir durumdadır. Canlı demo `https://turkmence-morfolojik-analiz.vercel.app/` üzerinde kullanıma açıktır. Sistemin, Türkmen Türkçesi için DDİ araçlarının geliştirilmesinde temel bir kaynak olarak hizmet etmesi hedeflenmektedir.

---

## Kaynaklar

Bakaev, I. I. ve Bakaeva, R. I. (2021). Creation of a morphological analyzer based on finite-state techniques for the Uzbek language. *Journal of Physics: Conference Series*, 1791(1), 012068.

Beesley, K. R. ve Karttunen, L. (2003). *Finite State Morphology*. CSLI Publications, Stanford, CA.

Çöltekin, Ç. (2010). A freely available morphological analyzer for Turkish. *Proceedings of the 7th International Conference on Language Resources and Evaluation (LREC 2010)*, 820–827.

Gatiatullin, A., Prokopyev, N. vd. (2024). Linguistic knowledge graph "Turklang" as universal model for linguistic resources and tools in Turkic languages. *IEEE International Conference on Computational Linguistics*, 1–8.

Gökgöz, E. ve Kurt, A. (2011). Two-level Qazan Tatar morphology. *Proceedings of the 1st Workshop on Language Technology for Turkic Languages*, 11–18.

Kessikbayeva, G. ve Cicekli, I. (2014). Rule based morphological analyzer of Kazakh language. *Proceedings of the 2014 Joint Meeting of SIGMORPHON and SIGFSM*, 46–54.

Koskenniemi, K. (1983). *Two-Level Morphology: A General Computational Model for Word-Form Recognition and Production*. Publications of the Department of General Linguistics, University of Helsinki, No. 11.

Kyýasowa, G., Geldimyradow, A. ve Durdyýew, H. (2016). *Türkmen diliniň orfografik sözlügi* [Orthographic Dictionary of the Turkmen Language]. (G. Berdimuhamedow, Gen. Ed.). Türkmen döwlet neşirýat gullugy. 110 000 söz.

Oflazer, K. (1994). Two-level description of Turkish morphology. *Literary and Linguistic Computing*, 9(2), 137–148.

Tantuğ, A. C., Adalı, E. ve Oflazer, K. (2007). A MT system from Turkmen to Turkish employing finite state and statistical methods. *Proceedings of Machine Translation Summit XI*, 459–465.

Washington, J. N., Ipasov, M. ve Tyers, F. M. (2012). A finite-state morphological transducer for Kyrgyz. *Proceedings of the 8th International Conference on Language Resources and Evaluation (LREC 2012)*, 934–940.

Washington, J. N., Salimzyanov, I. ve Tyers, F. M. (2014). Finite-state morphological transducers for three Kypchak languages. *Proceedings of the 9th International Conference on Language Resources and Evaluation (LREC 2014)*, 3378–3385.

Yıldız, O. T., Avar, B. ve Ercan, G. (2019). An open, extendible, and fast Turkish morphological analyzer. *Proceedings of the International Conference on Recent Advances in Natural Language Processing (RANLP 2019)*, 1364–1372.

[TODO: Kaynakların cilt, sayfa numaraları ve DOI'leri doğrulanmalıdır. Ayrıca aşağıdaki potansiyel ek kaynaklar değerlendirilebilir:
- Türkmen Türkçesi grameriyle ilgili dilbilim referansları (Clark, 1998 veya Saparow & Mamedow gibi)
- enedilim.com resmi referansı
- Apertium projesindeki Türkmen dil çiftleri (varsa)]

---

## Ekler

### Ek A. İsim Çekim Paradigma Örneği

*kitap* (kitap) kökünün tam çekim tablosu:

| Hâl | Tekil | Çoğul |
|-----|-------|-------|
| Yalın (A1) | kitap | kitaplar |
| İlgi (A2) | kitabyň | kitaplaryň |
| Yönelme (A3) | kitaba | kitaplara |
| Belirtme (A4) | kitaby | kitaplary |
| Bulunma (A5) | kitapda | kitaplarda |
| Çıkma (A6) | kitapdan | kitaplardan |

*Tablo A1.* İyeliksiz isim çekim paradigması.

| Hâl | 1. Tekil İyelik | 2. Tekil İyelik | 3. Tekil İyelik |
|-----|-----------------|-----------------|-----------------|
| Yalın (A1) | kitabym | kitabyň | kitaby |
| İlgi (A2) | kitabymyň | kitabyňyň | kitabynyň |
| Yönelme (A3) | kitabyma | kitabyňa | kitabyna |
| Belirtme (A4) | kitabymy | kitabyňy | kitabyny |
| Bulunma (A5) | kitabymda | kitabyňda | kitabynda |
| Çıkma (A6) | kitabymdan | kitabyňdan | kitabyndan |

*Tablo A2.* İyelikli isim çekim paradigması.

### Ek B. Fiil Çekim Paradigma Örneği

*gel-* (gelmek) fiilinin belirli geçmiş (Ö1) çekim tablosu:

| Şahıs | Olumlu | Olumsuz |
|--------|--------|---------|
| A1 (men) | geldim | gelmedim |
| A2 (sen) | geldiň | gelmediň |
| A3 (ol) | geldi | gelmedi |
| B1 (biz) | geldik | gelmedik |
| B2 (siz) | geldiňiz | gelmediňiz |
| B3 (olar) | geldiler | gelmediler |

*Tablo B1.* Belirli geçmiş (Anyk Öten) zaman çekim paradigması.

### Ek C. Sistem Ekran Görüntüleri

[TODO: Web arayüzünün dört sekmesinin ekran görüntüleri eklenecek:
1. İsim çekimi sekmesi — kitap kökünün A3 (yönelme) çekimi
2. Fiil çekimi sekmesi — gel kökünün Ö1 A1 çekimi
3. Derňew (analiz) sekmesi — "kitabymyza geldim" analizi
4. Paradigma sekmesi — "at" eş sesli çift paradigma]

---

## Yazarlar Hakkında

[TODO: Kısa yazar biyografileri eklenecek — araştırma alanları, kurum bilgileri]

---

### Makale Hakkında Düzenleme Notları (Gönderim Öncesi Yapılacaklar)

> Bu bölüm makale dosyasından gönderim öncesinde çıkarılacaktır.

1. **Kurum bilgileri (TODO × 2):** Yazar bağlantıları ve e-posta adresleri eklenmeli.
2. **Kaynakça doğrulama:** Tüm referansların cilt, sayı, sayfa ve DOI bilgileri teyit edilmeli. Özellikle Tantuğ vd. 2007 ve Washington vd. 2012/2014 makalelerinin kesin bibliyografik bilgileri kontrol edilmeli.
3. **Ek kaynaklar:** Türkmen Türkçesi grameri üzerine geleneksel dilbilim referansı eklenmesi düşünülebilir (ör. Clark, L. (1998). *Turkmen Reference Grammar*. Harrassowitz).
4. **Karşılaştırma tablosu (Tablo 6):** Diğer sistemlerin sözlük boyutları kesin rakamlarla doğrulanmalı. Tantuğ vd.'nin ~1.200 değeri makaleden çıkarım olup kesin ifade kontrol edilmeli.
5. **Ekran görüntüleri (Ek C):** Web arayüzünün 4 sekmesinden temsili ekran görüntüleri alınıp makaleye eklenmeli.
6. **Yazar biyografileri:** Kısa araştırmacı tanıtımları yazılmalı.
7. **TurkLang şablon uyumu:** TurkLang konferansının güncel şablonu (genellikle Springer CCIS veya LNCS formatı) temin edilip makale bu şablona aktarılmalı. Şablon genellikle LaTeX veya Word formatında sunulmaktadır.
8. **Sayfa sınırlaması:** TurkLang bildirileri genellikle 10–15 sayfa aralığındadır; mevcut metin bu aralığa uygundur. Gerekirse ekler kısaltılabilir.
9. **Şekil kalitesi:** Mimari diyagramı (Şekil 1) yüksek çözünürlüklü bir grafik (TikZ, draw.io veya Lucidchart) ile yeniden oluşturulmalı.
10. **Etik beyan:** enedilim.com verilerinin kullanım koşulları kontrol edilmeli; gerekirse veri toplama yöntemine ilişkin etik beyan eklenmelidir.
11. **Türkçe/İngilizce karar:** TurkLang, genellikle Türkçe ve İngilizce bildiri kabul etmektedir. İstenen dile göre metnin tamamı gözden geçirilmelidir.
