# -*- coding: utf-8 -*-
"""
TÜRKMEN TÜRKÇESİ MORFOLOJİK MOTORU v26.0

Sentez (üretim) tabanlı isim ve fiil çekimi motoru.
Flask web uygulaması ve CLI arayüzü destekler.

Temel kavramlar:
  - yogyn (kalın) ünlüler: a, o, u, y
  - ince ünlüler: e, ä, ö, i, ü
  - dodak (yuvarlak) ünlüler: o, ö, u, ü
  - Ünlü uyumu: ekler son ünlünün kalın/ince niteliğine göre seçilir
  - Yuvarlaklık uyumu: bazı ekler kökün yuvarlak olup olmadığına göre seçilir
"""

# ==============================================================================
#  SESLER VE TABLOLAR
# ==============================================================================

# Ünlü kümeleri
YOGYN_UNLULER = set("aouy")       # Kalın ünlüler
INCE_UNLULER = set("eäöiü")      # İnce ünlüler
DODAK_UNLULER = set("oöuü")      # Yuvarlak (dudak) ünlüler
TUM_UNLULER = YOGYN_UNLULER | INCE_UNLULER

# Şahıs zamirleri (iyelik ve fiil çekiminde kullanılır)
ZAMIRLER = {
    "A1": "Men",  "A2": "Sen",  "A3": "Ol",
    "B1": "Biz",  "B2": "Siz",  "B3": "Olar"
}

# Ünsüz yumuşama tablosu (sert → yumuşak)
YUMUSAMA_TABLOSU = {'p': 'b', 'ç': 'j', 't': 'd', 'k': 'g'}

# Eş sesli kelimeler sözlüğü
# Her eş sesli kelime için: {anahtar: (anlam_etiketi, yumuşama_izni)}
ES_SESLILER = {
    "at":   {"1": ("A:T (Ad, isim)", True),       "2": ("AT (At, beygir)", False)},
    "but":  {"1": ("BU:T (Vücut bölümü)", True),  "2": ("BUT (Temel taşı)", False)},
    "gurt": {"1": ("GU:RT (Kurt, hayvan)", True),  "2": ("GURT (Kurutulmuş süzme)", False)},
    "saç":  {"1": ("SA:Ç (Sac metal)", True),      "2": ("SAÇ (Saç kılı)", False)},
    "yok":  {"1": ("YO:K (Yok, var olmayan)", True),"2": ("YOK (Kalıntı, iz)", False)},
    "ot":   {"1": ("O:T (Ateş)", False),            "2": ("OT (Bitki)", False)}
}

# İstisna ünlü düşmeleri (özel kelimeler)
DUSME_ISTISNALARI = {
    "asyl": "asl", "pasyl": "pasl", "nesil": "nesl",
    "ylym": "ylm", "mähir": "mähr"
}

# Genel ünlü düşme adayları (son hecedeki ünlü düşer)
DUSME_ADAYLARI = {
    "burun", "alyn", "agyz", "gobek", "ogul", "erin",
    "bagyr", "sabyr", "kömür", "sygyr", "deňiz",
    "goýun", "boýun", "howuz", "tomus", "tizir",
    "köwüş", "orun", "garyn", "gelin"
}

# Özel yuvarlaklaşma listesi (y/i → u/ü dönüşümü)
# Bu kelimeler hal ekleri (A5, A6) öncesinde de yuvarlaklaşır.
YUVARLAKLASMA_LISTESI = {
    "guzy": "guzu",
    "süri": "sürü",
    "guýy": "guýu"
}

# Tek heceli fiillerde özel k/t→g/d yumuşaması yapan fiiller
TEK_HECELI_YUMUSAMA_FIIL = {"aýt", "gaýt", "et", "git"}


# ==============================================================================
#  YARDIMCI FONKSİYONLAR
# ==============================================================================

def unlu_niteligi(kelime):
    """
    Kelimenin son ünlüsüne göre kalınlık niteliğini döndürür.
    
    Returns:
        "yogyn" (kalın) veya "ince"
    """
    for harf in reversed(kelime.lower()):
        if harf in YOGYN_UNLULER:
            return "yogyn"
        if harf in INCE_UNLULER:
            return "ince"
    return "yogyn"  # Varsayılan: kalın


def yuvarlak_mi(kelime):
    """Kelimede yuvarlak (dudak) ünlü var mı kontrol eder."""
    return any(harf in DODAK_UNLULER for harf in kelime.lower())


def tam_yumusama(kok):
    """
    Ünsüz yumuşaması uygular (kökün son harfine).
    
    Kurallar: p→b, ç→j, t→d, k→g
    Örnek: kitap → kitab, agaç → agaj
    """
    if kok and kok[-1] in YUMUSAMA_TABLOSU:
        return kok[:-1] + YUMUSAMA_TABLOSU[kok[-1]]
    return kok


def dusme_uygula(kok, ek):
    """
    Ünlü düşmesi uygular: ek ünlüyle başlıyorsa, kökün son hecesindeki
    ünlü düşebilir.
    
    Örnekler:
        burun + um → burn + um (genel kural: sondan 2. harfi sil)
        asyl + y  → asl + y   (istisna tablosundan)
    """
    kok_lower = kok.lower()
    ek_lower = ek.lower()

    # Ek ünlüyle başlamıyorsa düşme olmaz
    if not ek_lower or ek_lower[0] not in TUM_UNLULER:
        return kok_lower

    # İstisna kelimeleri kontrol et
    if kok_lower in DUSME_ISTISNALARI:
        return DUSME_ISTISNALARI[kok_lower]

    # Genel düşme adayları: sondan 2. harfi (ünlü) düşür
    if kok_lower in DUSME_ADAYLARI:
        return kok_lower[:-2] + kok_lower[-1]

    return kok_lower


# ==============================================================================
#  İSİM ÇEKİMİ
# ==============================================================================

def isim_cekimle(kok, cokluk=False, iyelik=None, i_tip="tek", hal=None, yumusama_izni=True, negative=False):
    """
    Türkmen Türkçesi isim çekimi yapar (v27.0).
    
    Parametreler:
        kok    : Kök kelime (str)
        cokluk : Çoğul eki eklensin mi? (bool)
        iyelik : İyelik kodu: "A1" (men), "A2" (sen), "A3" (ol) veya None
        i_tip  : İyelik tipi: "tek" (tekil) veya "cog" (çoğul)
        hal    : Hal kodu: "A2"-"A6" veya None
        yumusama_izni : Ünsüz yumuşaması uygulanacak mı (eş sesliler için)
        negative : Olumsuzluk (däl) eklensin mi? (bool)
    
    Döndürür:
        (çekimlenmiş_kelime, şecere_str)
        Örnek: ("kitabym", "kitap + ym")
    
    Ek sırası: KÖK + [çokluk] + [iyelik] + [hal]
    """
    govde = kok.lower()
    yol = [kok]

    # Berdi Hoca kuralı: Guzy/Süri/Guýy yuvarlaklaşması
    # Sadece Çokluk ve A3 kategorilerinde kök değişir.
    yuvarlaklasma_yapildi = False
    if govde in YUVARLAKLASMA_LISTESI and (cokluk or iyelik == "A3"):
        govde = YUVARLAKLASMA_LISTESI[govde]
        yuvarlaklasma_yapildi = True

    nit_ilk = unlu_niteligi(govde)
    kok_yuvarlak = yuvarlak_mi(govde)

    # ------------------------------------------------------------------
    # 1. ÇOKLUK EKİ (-lar / -ler)
    # ------------------------------------------------------------------
    if cokluk:
        # Yuvarlaklaşma: son harf y/i ise ve kök yuvarlak ise u/ü'ye dönüşür
        if not yuvarlaklasma_yapildi and kok_yuvarlak and govde[-1] in "yi":
            govde = govde[:-1] + ("u" if nit_ilk == "yogyn" else "ü")

        ek = "lar" if unlu_niteligi(govde) == "yogyn" else "ler"
        govde += ek
        yol.append(ek)

    # ------------------------------------------------------------------
    # 2. İYELİK EKLERİ
    #    A1: Men (benim)   A2: Sen (senin)   A3: Ol (onun)
    #    i_tip="cog" → çoğul: Biz (A1), Siz (A2)
    # ------------------------------------------------------------------
    if iyelik:
        nit = unlu_niteligi(govde)
        is_unlu = govde[-1] in TUM_UNLULER
        kok_yuvarlak = yuvarlak_mi(govde)

        # --- Ek belirleme ---
        if iyelik == "A1":
            # Tekil: -m / -ym / -um     Çoğul: -myz / -ymyz / -umyz
            if is_unlu:
                ek = "m" if i_tip == "tek" else ("myz" if nit == "yogyn" else "miz")
            else:
                taban = ("um" if nit == "yogyn" else "üm") if kok_yuvarlak else ("ym" if nit == "yogyn" else "im")
                ek = taban if i_tip == "tek" else (taban + ("yz" if nit == "yogyn" else "iz"))

        elif iyelik == "A2":
            # Tekil: -ň / -yň / -uň     Çoğul: -ňyz / -yňyz / -uňyz
            if is_unlu:
                ek = "ň" if i_tip == "tek" else ("ňyz" if nit == "yogyn" else "ňiz")
            else:
                taban = ("uň" if nit == "yogyn" else "üň") if kok_yuvarlak else ("yň" if nit == "yogyn" else "iň")
                ek = taban if i_tip == "tek" else (taban + ("yz" if nit == "yogyn" else "iz"))

        elif iyelik == "A3":
            # 3. tekil iyelik — yuvarlaklaşma + su/sü veya sy/si
            yuvarlaklasti = False
            if not yuvarlaklasma_yapildi and kok_yuvarlak and govde[-1] in "yi":
                govde = govde[:-1] + ("u" if nit == "yogyn" else "ü")
                yuvarlaklasti = True
            if is_unlu:
                if yuvarlaklasti or yuvarlaklasma_yapildi:
                    ek = "su" if nit == "yogyn" else "sü"
                else:
                    ek = "sy" if nit == "yogyn" else "si"
            else:
                if yuvarlaklasma_yapildi and kok_yuvarlak:
                    ek = "u" if nit == "yogyn" else "ü"
                else:
                    ek = "y" if nit == "yogyn" else "i"

        # --- Düşme ve yumuşama ---
        govde = dusme_uygula(govde, ek)
        if yumusama_izni:
            govde = tam_yumusama(govde)
        govde += ek
        yol.append(ek)

    # ------------------------------------------------------------------
    # 3. HAL EKLERİ
    #    A2: İlgi (-yň)   A3: Yönelme (-a)   A4: Belirtme (-y/-ny)
    #    A5: Bulunma (-da) A6: Çıkma (-dan)
    # ------------------------------------------------------------------
    if hal:
        nit = unlu_niteligi(govde)
        is_unlu = govde[-1] in TUM_UNLULER
        kok_yuvarlak = yuvarlak_mi(govde)
        yol_eki = None  # Şecere için ayrı ek (ünlü değiştirme durumlarında)

        # 3. iyelikten sonra n-kaynaştırma
        n_kay = iyelik == "A3"

        # Orta Hece Yuvarlaklaşma (Ogluny, Burnuny)
        if n_kay and kok_yuvarlak and govde[-1] in "yi":
            govde = govde[:-1] + ("u" if nit == "yogyn" else "ü")

        if hal == "A2":  # İlgi hali
            if n_kay:
                ek = "nyň"
            elif is_unlu:
                ek = "nyň" if nit == "yogyn" else "niň"
            else:
                if len(kok) <= 4 and kok_yuvarlak:
                    ek = "uň" if nit == "yogyn" else "üň"
                else:
                    ek = "yň" if nit == "yogyn" else "iň"
                govde = dusme_uygula(govde, ek)
                if yumusama_izni:
                    govde = tam_yumusama(govde)

        elif hal == "A3":  # Yönelme hali
            if n_kay:
                ek = "na" if nit == "yogyn" else "ne"
            elif is_unlu:
                son = govde[-1]
                govde = govde[:-1]
                degisen = "a" if son in "ay" else "ä"
                govde += degisen
                ek = ""
                yol_eki = degisen  # Şecere için gerçek eki kaydet
            else:
                ek = "a" if nit == "yogyn" else "e"

        elif hal == "A4":  # Belirtme hali
            if n_kay:
                ek = "ny" if nit == "yogyn" else "ni"
            elif is_unlu:
                ek = "ny" if nit == "yogyn" else "ni"
            else:
                ek = "y" if nit == "yogyn" else "i"
                if yumusama_izni:
                    govde = tam_yumusama(govde)

        elif hal == "A5":  # Bulunma hali
            ek = "nda" if n_kay else ("da" if nit == "yogyn" else "de")

        elif hal == "A6":  # Çıkma hali
            ek = "ndan" if n_kay else ("dan" if nit == "yogyn" else "den")

        govde += ek
        yol.append(yol_eki if yol_eki is not None else ek)

    # 4) OLUMSUZLUK (däl)
    if negative:
        govde += " däl"
        yol.append("däl")

    return govde, " + ".join(yol)


# ==============================================================================
#  FLASK API — İSİM ÇEKİMİ
# ==============================================================================

# İyelik kodlarını görüntüleme formatına çeviren tablo
IYELIK_DISPLAY_MAP = {
    "A1": "D₁b", "A2": "D₂b", "A3": "D₃b",
    "B1": "D₁k", "B2": "D₂k", "B3": "D₃k"
}

# Web dropdown'dan gelen B1/B2/B3 → motor koduna dönüşüm
IYELIK_DONUSUM = {"B1": "A1", "B2": "A2", "B3": "A3"}


def kelimedeki_unlu_niteligi(kelime):
    """Ünlü niteliğini 'kalin'/'ince' olarak döndürür (Flask uyumluluk)."""
    return "kalin" if unlu_niteligi(kelime) == "yogyn" else "ince"


def son_harf_unlu_mu(kelime):
    """Son harf ünlü mü kontrol eder (Flask uyumluluk)."""
    if not kelime:
        return False
    return kelime[-1].lower() in TUM_UNLULER


def _build_parts(root, result, yol, s_code, i_code, h_code, cokluk, iyelik):
    """
    Çekim sonucunu 'parts' listesine dönüştürür (template'de gösterim için).
    
    Tüm ekleri şecere (yol) string'inden çıkarır — isim_cekimle ile tutarlılık sağlar.
    Her part: {"text": ek_metni, "type": ek_türü, "code": görüntüleme_kodu}
    """
    yol_parts = yol.split(" + ")
    parts = [{"text": root, "type": "Kök", "code": "Kök"}]

    idx = 1  # yol_parts[0] = kök

    # Çokluk eki (şecereden)
    if cokluk and idx < len(yol_parts):
        parts.append({"text": yol_parts[idx], "type": "Sayı", "code": s_code})
        idx += 1

    # İyelik eki (şecereden)
    if iyelik and idx < len(yol_parts):
        iyelik_eki = yol_parts[idx]
        # Hal eki de varsa, iyelik eki sondan bir önceki
        if h_code and h_code != "H1" and idx + 1 < len(yol_parts):
            parts.append({"text": iyelik_eki, "type": "Degislilik", "code": i_code})
            idx += 1
        else:
            parts.append({"text": iyelik_eki, "type": "Degislilik", "code": i_code})
            idx += 1

    # Hal eki (şecerenin son elemanı)
    if h_code and h_code != "H1" and idx < len(yol_parts):
        hal_eki = yol_parts[idx]
        display_code = h_code.replace('H', 'A')
        parts.append({"text": hal_eki, "type": "Hal", "code": display_code})

    # İyelik kodlarını görüntüleme formatına çevir (A1→D₁b, B1→D₁k, vb.)
    # Sadece iyelik (Degislilik) parçalarına uygula — hal kodları (A2-A6) etkilenmesin
    for part in parts:
        if part.get("type") == "Degislilik" and part.get("code") in IYELIK_DISPLAY_MAP:
            part["code"] = IYELIK_DISPLAY_MAP[part["code"]]

    return parts


def analyze(root, s_code, i_code, h_code, negative=False):
    """
    Flask uyumlu isim çekimi API'si.
    
    Eş sesli kelimeler için çift sonuç döndürür.
    
    Parametreler:
        root   : Kök kelime
        s_code : Çokluk kodu ("S2" veya boş)
        i_code : İyelik kodu ("A1"-"A3", "B1"-"B3" veya boş)
        h_code : Hal kodu ("H1"-"H6")
        negative : Olumsuzluk (däl) eklensin mi? (bool)
    
    Döndürür:
        (results_list, is_dual)
        results_list: [{"parts": [...], "final_word": str, "anlam": str|None}]
        is_dual: True ise eş sesli kelime (2 sonuç)
    """
    cokluk = (s_code == "S2")

    # Web dropdown kodlarını çekim motorunun beklediği kodlara dönüştür
    # B1→A1(çoğul), B2→A2(çoğul), B3→A3(tekil)
    iyelik = IYELIK_DONUSUM.get(i_code, i_code) if i_code else None
    i_tip = "cog" if i_code in ["B1", "B2"] else "tek"

    # Hal kodu dönüşümü: H2→A2, H3→A3, H4→A4, H5→A5, H6→A6
    HAL_DONUSUM = {"H2": "A2", "H3": "A3", "H4": "A4", "H5": "A5", "H6": "A6"}
    hal = HAL_DONUSUM.get(h_code) if h_code and h_code != "H1" else None

    root_lower = root.lower()

    # --- Eş sesli kelime kontrolü ---
    if root_lower in ES_SESLILER:
        results = []
        for key, (anlam, yumusama) in ES_SESLILER[root_lower].items():
            result, yol = isim_cekimle(root, cokluk, iyelik, i_tip, hal,
                                       yumusama_izni=yumusama, negative=negative)
            parts = _build_parts(root, result, yol, s_code, i_code, h_code, cokluk, iyelik)
            results.append({
                "parts": parts,
                "final_word": result,
                "anlam": anlam
            })
        return results, True

    # --- Normal kelime ---
    result, yol = isim_cekimle(root, cokluk, iyelik, i_tip, hal, negative=negative)
    parts = _build_parts(root, result, yol, s_code, i_code, h_code, cokluk, iyelik)
    return [{"parts": parts, "final_word": result, "anlam": None}], False


# ==============================================================================
#  FİİL ÇEKİMİ
# ==============================================================================

# Geçmiş zaman, dowamly ve nämälim geljek zaman şahıs ekleri ortak tablo
def _sahis_ekleri_standart(sesli_tipi, sahis):
    """Standart şahıs eki tablosu (Ö1, Ö2, Ö3 zamanları için)."""
    tablo = {
        "A1": "m",
        "A2": "ň",
        "A3": "",
        "B1": "k",
        "B2": "ňyz" if sesli_tipi == "yogyn" else "ňiz",
        "B3": "lar" if sesli_tipi == "yogyn" else "ler"
    }
    return tablo[sahis]


def _sahis_ekleri_genisletilmis(sesli_tipi, sahis):
    """Genişletilmiş şahıs eki tablosu (H1, G2 zamanları için)."""
    tablo = {
        "A1": "yn" if sesli_tipi == "yogyn" else "in",
        "A2": "syň" if sesli_tipi == "yogyn" else "siň",
        "A3": "",
        "B1": "ys" if sesli_tipi == "yogyn" else "is",
        "B2": "syňyz" if sesli_tipi == "yogyn" else "siňiz",
        "B3": "lar" if sesli_tipi == "yogyn" else "ler"
    }
    return tablo[sahis]


def _tek_heceli_dodak(govde):
    """Tek heceli ve dodak (yuvarlak) ünlülü fiil mi kontrol eder."""
    unluler = [c for c in govde.lower() if c in TUM_UNLULER]
    return len(unluler) == 1 and unluler[0] in DODAK_UNLULER


def _fiil_yumusama(govde):
    """Çok heceli veya özel tek heceli fiillerde k/t→g/d yumuşaması uygular."""
    if not govde or govde[-1] not in ('k', 't'):
        return govde
    unlu_sayisi = sum(1 for c in govde if c in TUM_UNLULER)
    if unlu_sayisi > 1 or govde in TEK_HECELI_YUMUSAMA_FIIL:
        return govde[:-1] + YUMUSAMA_TABLOSU[govde[-1]]
    return govde


def fiil_cekimle(kok, zaman, sahis, olumsuz=False):
    """
    Türkmen Türkçesi fiil çekimi yapar.
    
    Parametreler:
        kok     : Fiil kökü (str)
        zaman   : Zaman kodu ("1"-"7")
        sahis   : Şahıs kodu ("A1"-"B3")
        olumsuz : Olumsuz mu? (bool)
    
    Döndürür:
        (çekimlenmiş_fiil, şecere_str)
    
    Zaman kodları:
        1: Anyk Öten     (geçmiş zaman, kesin)
        2: Daş Öten      (geçmiş zaman, dolaylı)
        3: Dowamly Öten  (geçmiş zaman, sürekli)
        4: Umumy Häzirki (geniş zaman)
        5: Anyk Häzirki  (şimdiki zaman, kesin)
        6: Mälim Geljek  (gelecek zaman, kesin)
        7: Nämälim Geljek(gelecek zaman, belirsiz)
        8: Şert          (şart kipi)
        9: Buýruk        (emir kipi)
        10: Hökmanlyk    (gereklilik kipi)
        11: Nätanyş Öten (kanıtsal / evidential)
        12: Arzuw-Ökünç  (arzuw-ökünç / optative)
        13: Hal işlik     (converb: -yp/-ip/-up/-üp/-p)
        14: Öten ortak    (past participle: -an/-en)
        15: Häzirki ortak (present participle: -ýan/-ýän)
        16: Geljek ortak  (future participle: -jak/-jek)
        17: Ettirgen      (causative derivation)
        18: Edilgen       (passive derivation)
    """
    govde = kok.lower()
    sesli_tipi = unlu_niteligi(govde)
    unluylebiter = govde[-1] in TUM_UNLULER
    zamir = ZAMIRLER[sahis]

    # --- Mälim Geljek (6) ---
    if zaman == "6":
        zaman_eki = "jak" if sesli_tipi == "yogyn" else "jek"
        if olumsuz:
            # Olumsuz: kök + jak/jek + däl (değişiklik yok)
            sonuc = govde + zaman_eki + " däl"
            secere = f"{zamir} + {kok} + {zaman_eki} + däl"
            return f"{zamir} {sonuc}", secere
        else:
            # enedilim kuralı: kök + jak/jek + dir/dyr + kişi eki
            kopula_base = "dyr" if sesli_tipi == "yogyn" else "dir"
            kopula_person = _sahis_ekleri_genisletilmis(sesli_tipi, sahis)
            kopula_eki = kopula_base + kopula_person
            sonuc = govde + zaman_eki + kopula_eki
            secere = f"{zamir} + {kok} + {zaman_eki} + {kopula_eki}"
            return f"{zamir} {sonuc}", secere

    # --- Anyk Häzirki (5) — Özel yardımcı fiiller ---
    if zaman == "5":
        tablo = {
            "otyr":  {"A1": "yn",  "A2": "syň",  "A3": "", "B1": "ys",  "B2": "syňyz",  "B3": "lar"},
            "dur":   {"A1": "un",  "A2": "suň",  "A3": "", "B1": "us",  "B2": "suňyz",  "B3": "lar"},
            "ýatyr": {"A1": "yn",  "A2": "syň",  "A3": "", "B1": "ys",  "B2": "syňyz",  "B3": "lar"},
            "ýör":   {"A1": "ün",  "A2": "siň",  "A3": "", "B1": "üs",  "B2": "siňiz",  "B3": "ler"}
        }
        if govde not in tablo:
            return f"HATA: '{kok}' fiili Anyk Häzirki zamanda çekimlenemez", ""
        sahis_eki = tablo[govde][sahis]
        return govde + sahis_eki, f"{kok} + {sahis_eki if sahis_eki else '(0)'}"

    # --- Diğer zamanlar ---
    olumsuz_eki = ("ma" if sesli_tipi == "yogyn" else "me") if olumsuz else ""

    if zaman == "1":
        # Anyk Öten: kök + [ma] + dy/di + şahıs
        # Tek heceli dodak fiillerde: -dy/-di → -du/-dü (şahıs eki varken)
        if not olumsuz and _tek_heceli_dodak(govde) and sahis != "A3":
            zaman_eki = "du" if sesli_tipi == "yogyn" else "dü"
        else:
            zaman_eki = "dy" if sesli_tipi == "yogyn" else "di"
        sahis_eki = _sahis_ekleri_standart(sesli_tipi, sahis)

    elif zaman == "2":
        # Daş Öten
        if olumsuz:
            # enedilim kuralı: kök + män/man + di/dy + kişi
            olumsuz_eki = ""  # genel olumsuz eki kullanılmaz
            zaman_eki = "mändi" if sesli_tipi == "ince" else "mandy"
            sahis_eki = _sahis_ekleri_standart(sesli_tipi, sahis)
        else:
            # Olumlu: kök + ypdy/pdy + şahıs
            if unluylebiter:
                zaman_eki = "pdy" if sesli_tipi == "yogyn" else "pdi"
            else:
                zaman_eki = "ypdy" if sesli_tipi == "yogyn" else "ipdi"
            sahis_eki = _sahis_ekleri_standart(sesli_tipi, sahis)

    elif zaman == "3":
        # Dowamly Öten
        if olumsuz:
            # enedilim kuralı: kök + ýan/ýän + däldi + kişi (analitik yapı)
            olumsuz_eki = ""  # genel olumsuz eki kullanılmaz
            sifat_fiil = "ýan" if sesli_tipi == "yogyn" else "ýän"
            # däldi her zaman ince, kişi ekleri däldi'nin ünlü niteliğine göre
            sahis_eki_str = _sahis_ekleri_standart("ince", sahis)
            sonuc = govde + sifat_fiil + " däldi" + sahis_eki_str
            secere = f"{kok} + {sifat_fiil} + däldi + {sahis_eki_str if sahis_eki_str else '(0)'}"
            return sonuc, secere
        else:
            # Olumlu: kök + ýardy/ýärdi + şahıs
            zaman_eki = "ýardy" if sesli_tipi == "yogyn" else "ýärdi"
            sahis_eki = _sahis_ekleri_standart(sesli_tipi, sahis)

    elif zaman == "4":
        # Umumy Häzirki: kök + [ma] + ýar/ýär + şahıs
        # k/t yumuşaması (sadece olumlu formda)
        if not olumsuz:
            govde = _fiil_yumusama(govde)
        zaman_eki = "ýar" if sesli_tipi == "yogyn" else "ýär"
        sahis_eki = _sahis_ekleri_genisletilmis(sesli_tipi, sahis)

    elif zaman == "7":
        # Nämälim Geljek
        if olumsuz:
            # Olumsuzluk zaman ekine dahil: -mar/-mer (1./2. şahıs), -maz/-mez (3. şahıs)
            olumsuz_eki = ""
            if sahis in ("A3", "B3"):
                zaman_eki = "maz" if sesli_tipi == "yogyn" else "mez"
            else:
                zaman_eki = "mar" if sesli_tipi == "yogyn" else "mer"
        else:
            # k/t yumuşaması
            govde = _fiil_yumusama(govde)
            # e→ä dönüşümü
            if govde and govde[-1] == 'e':
                govde = govde[:-1] + 'ä'
            zaman_eki = "r" if unluylebiter else ("ar" if sesli_tipi == "yogyn" else "er")
        sahis_eki = _sahis_ekleri_genisletilmis(sesli_tipi, sahis)

    elif zaman == "8":
        # Şert formasy (Şart kipi): kök + [ma/me] + sa/se + kişi
        zaman_eki = "sa" if sesli_tipi == "yogyn" else "se"
        sahis_eki = _sahis_ekleri_standart(sesli_tipi, sahis)

    elif zaman == "9":
        # Buýruk formasy (Emir kipi) — her şahıs için farklı yapı
        if olumsuz:
            olumsuz_eki = "ma" if sesli_tipi == "yogyn" else "me"
            # -ma/-me ekinden sonra gövde ünlüyle biter → dodak uyumu iptal
            if sahis == "A1":
                sahis_eki = "ýyn" if sesli_tipi == "yogyn" else "ýin"
                sonuc = govde + olumsuz_eki + sahis_eki
            elif sahis == "A2":
                sonuc = govde + olumsuz_eki
                sahis_eki = ""
            elif sahis == "A3":
                sahis_eki = "syn" if sesli_tipi == "yogyn" else "sin"
                sonuc = govde + olumsuz_eki + sahis_eki
            elif sahis == "B1":
                sahis_eki = "ly" if sesli_tipi == "yogyn" else "li"
                sonuc = govde + olumsuz_eki + sahis_eki
            elif sahis == "B2":
                sahis_eki = "ň"
                sonuc = govde + olumsuz_eki + sahis_eki
            else:  # B3
                sahis_eki = "synlar" if sesli_tipi == "yogyn" else "sinler"
                sonuc = govde + olumsuz_eki + sahis_eki
            secere = f"{kok} + {olumsuz_eki} + {sahis_eki if sahis_eki else '(0)'}"
            return sonuc, secere
        else:
            # Olumlu emir
            olumsuz_eki = ""
            if sahis == "A1":
                # Men: -aýyn/-eýin veya -ýyn/-ýin (ünlüden sonra)
                if unluylebiter:
                    sahis_eki = "ýyn" if sesli_tipi == "yogyn" else "ýin"
                else:
                    sahis_eki = "aýyn" if sesli_tipi == "yogyn" else "eýin"
                sonuc = govde + sahis_eki
            elif sahis == "A2":
                # Sen: çıplak kök
                sonuc = govde
                sahis_eki = ""
            elif sahis == "A3":
                # Ol: -syn/-sin/-sun/-sün (4-yönlü)
                if _tek_heceli_dodak(govde):
                    sahis_eki = "sun" if sesli_tipi == "yogyn" else "sün"
                else:
                    sahis_eki = "syn" if sesli_tipi == "yogyn" else "sin"
                sonuc = govde + sahis_eki
            elif sahis == "B1":
                # Biz: -aly/-eli veya -ly/-li (ünlüden sonra)
                if unluylebiter:
                    sahis_eki = "ly" if sesli_tipi == "yogyn" else "li"
                else:
                    sahis_eki = "aly" if sesli_tipi == "yogyn" else "eli"
                sonuc = govde + sahis_eki
            elif sahis == "B2":
                # Siz: -yň/-iň/-uň/-üň veya -ň (ünlüden sonra)
                if unluylebiter:
                    sahis_eki = "ň"
                else:
                    if _tek_heceli_dodak(govde):
                        sahis_eki = "uň" if sesli_tipi == "yogyn" else "üň"
                    else:
                        sahis_eki = "yň" if sesli_tipi == "yogyn" else "iň"
                sonuc = govde + sahis_eki
            else:  # B3
                # Olar: -synlar/-sinler/-sunlar/-sünler
                if _tek_heceli_dodak(govde):
                    sahis_eki = "sunlar" if sesli_tipi == "yogyn" else "sünler"
                else:
                    sahis_eki = "synlar" if sesli_tipi == "yogyn" else "sinler"
                sonuc = govde + sahis_eki
            secere = f"{kok} + {sahis_eki if sahis_eki else '(0)'}"
            return sonuc, secere

    elif zaman == "10":
        # Hökmanlyk formasy (Gereklilik): kök + maly/meli [+ däl]
        zaman_eki = "maly" if sesli_tipi == "yogyn" else "meli"
        if olumsuz:
            sonuc = govde + zaman_eki + " däl"
            secere = f"{kok} + {zaman_eki} + däl"
        else:
            sonuc = govde + zaman_eki
            secere = f"{kok} + {zaman_eki}"
        return sonuc, secere

    elif zaman == "11":
        # Nätanyş Öten (Kanıtsal / Evidential): kök + ypdyr/ipdir + kişi
        # Hal işlik eki + dyr/dir
        if olumsuz:
            # Olumsuz: kök + man/män + dyr/dir + kişi
            olumsuz_eki = ""  # genel olumsuz eki kullanılmaz
            zaman_eki = "mandyr" if sesli_tipi == "yogyn" else "mändir"
            sahis_eki = _sahis_ekleri_genisletilmis(sesli_tipi, sahis)
        else:
            # Olumlu: kök + ypdyr/ipdyr + kişi
            if unluylebiter:
                zaman_eki = "pdyr" if sesli_tipi == "yogyn" else "pdir"
            else:
                if _tek_heceli_dodak(govde):
                    zaman_eki = "updyr" if sesli_tipi == "yogyn" else "üpdir"
                else:
                    zaman_eki = "ypdyr" if sesli_tipi == "yogyn" else "ipdir"
            sahis_eki = _sahis_ekleri_genisletilmis(sesli_tipi, sahis)

    elif zaman == "12":
        # Arzuw-Ökünç (Optative): kök + [ma/me] + sa/se + dy/di + kişi
        sart_eki = "sa" if sesli_tipi == "yogyn" else "se"
        gecmis_eki = "dy" if sesli_tipi == "yogyn" else "di"
        sahis_eki = _sahis_ekleri_standart(sesli_tipi, sahis)
        sonuc = govde + olumsuz_eki + sart_eki + gecmis_eki + sahis_eki
        secere = f"{kok} + {olumsuz_eki + ' + ' if olumsuz_eki else ''}{sart_eki} + {gecmis_eki} + {sahis_eki if sahis_eki else '(0)'}"
        return sonuc, secere

    elif zaman == "13":
        # Hal işlik (converb): kök + yp/ip/up/üp/p (neg: man/män)
        if olumsuz:
            olumsuz_eki = ""
            zaman_eki = "man" if sesli_tipi == "yogyn" else "män"
        else:
            if unluylebiter:
                zaman_eki = "p"
            else:
                if _tek_heceli_dodak(govde):
                    zaman_eki = "up" if sesli_tipi == "yogyn" else "üp"
                else:
                    zaman_eki = "yp" if sesli_tipi == "yogyn" else "ip"
        sonuc = govde + zaman_eki
        secere = f"{kok} + {zaman_eki}"
        return sonuc, secere

    elif zaman == "14":
        # Öten ortak işlik (past participle): kök + an/en (neg: madyk/medik)
        if olumsuz:
            olumsuz_eki = ""
            zaman_eki = "madyk" if sesli_tipi == "yogyn" else "medik"
        else:
            if unluylebiter:
                zaman_eki = "n"
            else:
                zaman_eki = "an" if sesli_tipi == "yogyn" else "en"
        sonuc = govde + zaman_eki
        secere = f"{kok} + {zaman_eki}"
        return sonuc, secere

    elif zaman == "15":
        # Häzirki ortak işlik (present participle): kök + ýan/ýän (neg: maýan/meýän)
        if olumsuz:
            olumsuz_eki = ""
            zaman_eki = "maýan" if sesli_tipi == "yogyn" else "meýän"
        else:
            zaman_eki = "ýan" if sesli_tipi == "yogyn" else "ýän"
        sonuc = govde + zaman_eki
        secere = f"{kok} + {zaman_eki}"
        return sonuc, secere

    elif zaman == "16":
        # Geljek ortak işlik (future participle): kök + jak/jek (neg: majak/mejek)
        if olumsuz:
            olumsuz_eki = ""
            zaman_eki = "majak" if sesli_tipi == "yogyn" else "mejek"
        else:
            zaman_eki = "jak" if sesli_tipi == "yogyn" else "jek"
        sonuc = govde + zaman_eki
        secere = f"{kok} + {zaman_eki}"
        return sonuc, secere

    elif zaman == "17":
        # Ettirgen (causative): kök + dyr/dir/dur/dür veya +t
        if unluylebiter:
            sonuc = govde + "t"
            secere = f"{kok} + t"
        else:
            if _tek_heceli_dodak(govde):
                ek = "dur" if sesli_tipi == "yogyn" else "dür"
            else:
                ek = "dyr" if sesli_tipi == "yogyn" else "dir"
            sonuc = govde + ek
            secere = f"{kok} + {ek}"
        return sonuc, secere

    elif zaman == "18":
        # Edilgen (passive): kök + yl/il/ul/ül veya +yn/in/un/ün
        if unluylebiter:
            if govde and govde[-2:-1] == 'l':
                ek = "n"
            else:
                ek = "l"
            sonuc = govde + ek
        elif govde and govde[-1] == 'l':
            if _tek_heceli_dodak(govde):
                ek = "un" if sesli_tipi == "yogyn" else "ün"
            else:
                ek = "yn" if sesli_tipi == "yogyn" else "in"
            sonuc = govde + ek
        else:
            if _tek_heceli_dodak(govde):
                ek = "ul" if sesli_tipi == "yogyn" else "ül"
            else:
                ek = "yl" if sesli_tipi == "yogyn" else "il"
            sonuc = govde + ek
        secere = f"{kok} + {ek}"
        return sonuc, secere

    else:
        return f"HATA: Geçersiz zaman kodu '{zaman}'", ""

    # Sonuç birleştirme
    sonuc = govde + olumsuz_eki + zaman_eki + sahis_eki
    secere = f"{kok} + {olumsuz_eki + ' + ' if olumsuz_eki else ''}{zaman_eki} + {sahis_eki if sahis_eki else '(0)'}"
    return sonuc, secere


# ==============================================================================
#  FLASK API — FİİL ÇEKİMİ
# ==============================================================================

# Web dropdown → motor zaman kodu dönüşümü
ZAMAN_DONUSUM = {
    "Ö1": "1", "Ö2": "2", "Ö3": "3",
    "H1": "4", "H2": "5",
    "G1": "6", "G2": "7",
    "Ş1": "8", "B1K": "9", "HK": "10",
    "NÖ": "11", "AÖ": "12",
    "FH": "13", "FÖ": "14", "FÄ": "15", "FG": "16",
    "ETT": "17", "EDL": "18"
}


def analyze_verb(root, zaman_kodu, sahis_kodu, olumsuz=False):
    """
    Flask uyumlu fiil çekimi API'si.
    
    Çekimi yapar ve sonucu template'e uygun 'parts' listesine dönüştürür.
    
    Döndürür:
        (parts_list, final_word)
    """
    zaman = ZAMAN_DONUSUM.get(zaman_kodu, "1")
    sesli_tipi = unlu_niteligi(root)

    # Çekim yap
    result, yol = fiil_cekimle(root, zaman, sahis_kodu, olumsuz)

    # Hata kontrolü
    if result.startswith("HATA:"):
        return [{"text": result, "type": "Hata", "code": "HATA"}], ""

    # Parts listesi oluştur
    parts = []

    # Şahıs zamiri
    parts.append({"text": ZAMIRLER.get(sahis_kodu, ""), "type": "Şahıs", "code": sahis_kodu})

    # Kök
    parts.append({"text": root, "type": "Kök", "code": "Kök"})

    # --- Zaman ve şahıs eklerini belirle ---
    if zaman_kodu in ["Ö1", "Ö2", "Ö3"]:
        # Geçmiş zamanlar
        unluylebiter = root[-1].lower() in TUM_UNLULER

        if zaman_kodu == "Ö2" and olumsuz:
            # enedilim: kök + män/man + di/dy + kişi
            zaman_eki = "mändi" if sesli_tipi == "ince" else "mandy"
            parts.append({"text": zaman_eki, "type": "Olumsuz+Zaman", "code": zaman_kodu})
            sahis_eki = _sahis_ekleri_standart(sesli_tipi, sahis_kodu)
            if sahis_eki:
                parts.append({"text": sahis_eki, "type": "Şahıs", "code": sahis_kodu})

        elif zaman_kodu == "Ö3" and olumsuz:
            # enedilim: kök + ýan/ýän + däldi + kişi (analitik)
            sifat_fiil = "ýan" if sesli_tipi == "yogyn" else "ýän"
            parts.append({"text": sifat_fiil, "type": "Sıfat-fiil", "code": "SF"})
            sahis_eki_str = _sahis_ekleri_standart("ince", sahis_kodu)
            parts.append({"text": "däldi" + sahis_eki_str, "type": "Olumsuz+Kişi", "code": zaman_kodu})

        else:
            # Ö1 (olumlu/olumsuz), Ö2 olumlu, Ö3 olumlu
            if olumsuz:
                olumsuz_ek = "ma" if sesli_tipi == "yogyn" else "me"
                parts.append({"text": olumsuz_ek, "type": "Olumsuzluk Eki", "code": "Olumsuz"})

            if zaman_kodu == "Ö1":
                if not olumsuz and _tek_heceli_dodak(root.lower()) and sahis_kodu != "A3":
                    zaman_eki = "du" if sesli_tipi == "yogyn" else "dü"
                else:
                    zaman_eki = "dy" if sesli_tipi == "yogyn" else "di"
            elif zaman_kodu == "Ö2":
                if unluylebiter:
                    zaman_eki = "pdy" if sesli_tipi == "yogyn" else "pdi"
                else:
                    zaman_eki = "ypdy" if sesli_tipi == "yogyn" else "ipdi"
            else:  # Ö3 olumlu
                zaman_eki = "ýardy" if sesli_tipi == "yogyn" else "ýärdi"

            parts.append({"text": zaman_eki, "type": "Zaman", "code": zaman_kodu})

            sahis_eki = _sahis_ekleri_standart(sesli_tipi, sahis_kodu)
            if sahis_eki:
                parts.append({"text": sahis_eki, "type": "Şahıs", "code": sahis_kodu})

    elif zaman_kodu == "H1":
        # Umumy Häzirki — k/t yumuşaması (olumlu)
        if not olumsuz:
            modified = _fiil_yumusama(root.lower())
            if modified != root.lower():
                parts[-1] = {"text": modified, "type": "Kök", "code": "Kök"}
        if olumsuz:
            zaman_eki = "maýar" if sesli_tipi == "yogyn" else "meýär"
        else:
            zaman_eki = "ýar" if sesli_tipi == "yogyn" else "ýär"
        parts.append({"text": zaman_eki, "type": "Zaman", "code": zaman_kodu})

        sahis_eki = _sahis_ekleri_genisletilmis(sesli_tipi, sahis_kodu)
        if sahis_eki:
            parts.append({"text": sahis_eki, "type": "Şahıs", "code": sahis_kodu})

    elif zaman_kodu == "H2":
        # Anyk Häzirki — sadece şahıs ekleri
        sahis_tablosu = {
            "A1": "yn", "A2": "syň", "A3": "",
            "B1": "ys", "B2": "syňyz", "B3": "lar"
        }
        sahis_eki = sahis_tablosu.get(sahis_kodu, "")
        if sahis_eki:
            parts.append({"text": sahis_eki, "type": "Şahıs", "code": sahis_kodu})

    elif zaman_kodu == "G1":
        # Mälim Geljek
        zaman_eki = "jak" if sesli_tipi == "yogyn" else "jek"
        parts.append({"text": zaman_eki, "type": "Zaman", "code": zaman_kodu})
        if olumsuz:
            parts.append({"text": "däl", "type": "Olumsuzluk", "code": "Olumsuz"})
        else:
            # enedilim: kopula + kişi eki
            kopula_base = "dyr" if sesli_tipi == "yogyn" else "dir"
            kopula_person = _sahis_ekleri_genisletilmis(sesli_tipi, sahis_kodu)
            kopula_eki = kopula_base + kopula_person
            parts.append({"text": kopula_eki, "type": "Kopula", "code": sahis_kodu})

    elif zaman_kodu == "G2":
        # Nämälim Geljek
        unluylebiter = root[-1].lower() in TUM_UNLULER
        if olumsuz:
            # -mar/-mer (1./2. şahıs), -maz/-mez (3. şahıs)
            if sahis_kodu in ("A3", "B3"):
                zaman_eki = "maz" if sesli_tipi == "yogyn" else "mez"
            else:
                zaman_eki = "mar" if sesli_tipi == "yogyn" else "mer"
        else:
            # k/t yumuşaması
            modified = _fiil_yumusama(root.lower())
            if modified != root.lower():
                parts[-1] = {"text": modified, "type": "Kök", "code": "Kök"}
            # e→ä dönüşümü
            display_root = modified
            if display_root and display_root[-1] == 'e':
                display_root = display_root[:-1] + 'ä'
                parts[-1] = {"text": display_root, "type": "Kök", "code": "Kök"}
            zaman_eki = "r" if unluylebiter else ("ar" if sesli_tipi == "yogyn" else "er")
        parts.append({"text": zaman_eki, "type": "Zaman", "code": zaman_kodu})

        sahis_eki = _sahis_ekleri_genisletilmis(sesli_tipi, sahis_kodu)
        if sahis_eki:
            parts.append({"text": sahis_eki, "type": "Şahıs", "code": sahis_kodu})

    elif zaman_kodu == "Ş1":
        # Şert formasy
        if olumsuz:
            olumsuz_ek = "ma" if sesli_tipi == "yogyn" else "me"
            parts.append({"text": olumsuz_ek, "type": "Olumsuzluk Eki", "code": "Olumsuz"})
        zaman_eki = "sa" if sesli_tipi == "yogyn" else "se"
        parts.append({"text": zaman_eki, "type": "Zaman", "code": zaman_kodu})
        sahis_eki = _sahis_ekleri_standart(sesli_tipi, sahis_kodu)
        if sahis_eki:
            parts.append({"text": sahis_eki, "type": "Şahıs", "code": sahis_kodu})

    elif zaman_kodu == "B1K":
        # Buýruk formasy
        unluylebiter_root = root[-1].lower() in TUM_UNLULER
        if olumsuz:
            olumsuz_ek = "ma" if sesli_tipi == "yogyn" else "me"
            parts.append({"text": olumsuz_ek, "type": "Olumsuzluk Eki", "code": "Olumsuz"})
            # -ma/-me ekinden sonra gövde ünlüyle biter → dodak uyumu iptal
            if sahis_kodu == "A1":
                sahis_eki = "ýyn" if sesli_tipi == "yogyn" else "ýin"
            elif sahis_kodu == "A2":
                sahis_eki = ""
            elif sahis_kodu == "A3":
                sahis_eki = "syn" if sesli_tipi == "yogyn" else "sin"
            elif sahis_kodu == "B1":
                sahis_eki = "ly" if sesli_tipi == "yogyn" else "li"
            elif sahis_kodu == "B2":
                sahis_eki = "ň"
            else:  # B3
                sahis_eki = "synlar" if sesli_tipi == "yogyn" else "sinler"
        else:
            if sahis_kodu == "A1":
                if unluylebiter_root:
                    sahis_eki = "ýyn" if sesli_tipi == "yogyn" else "ýin"
                else:
                    sahis_eki = "aýyn" if sesli_tipi == "yogyn" else "eýin"
            elif sahis_kodu == "A2":
                sahis_eki = ""
            elif sahis_kodu == "A3":
                if _tek_heceli_dodak(root.lower()):
                    sahis_eki = "sun" if sesli_tipi == "yogyn" else "sün"
                else:
                    sahis_eki = "syn" if sesli_tipi == "yogyn" else "sin"
            elif sahis_kodu == "B1":
                if unluylebiter_root:
                    sahis_eki = "ly" if sesli_tipi == "yogyn" else "li"
                else:
                    sahis_eki = "aly" if sesli_tipi == "yogyn" else "eli"
            elif sahis_kodu == "B2":
                if unluylebiter_root:
                    sahis_eki = "ň"
                else:
                    if _tek_heceli_dodak(root.lower()):
                        sahis_eki = "uň" if sesli_tipi == "yogyn" else "üň"
                    else:
                        sahis_eki = "yň" if sesli_tipi == "yogyn" else "iň"
            else:  # B3
                if _tek_heceli_dodak(root.lower()):
                    sahis_eki = "sunlar" if sesli_tipi == "yogyn" else "sünler"
                else:
                    sahis_eki = "synlar" if sesli_tipi == "yogyn" else "sinler"
        if sahis_eki:
            parts.append({"text": sahis_eki, "type": "Şahıs", "code": sahis_kodu})

    elif zaman_kodu == "HK":
        # Hökmanlyk formasy
        zaman_eki = "maly" if sesli_tipi == "yogyn" else "meli"
        parts.append({"text": zaman_eki, "type": "Zaman", "code": zaman_kodu})
        if olumsuz:
            parts.append({"text": "däl", "type": "Olumsuzluk", "code": "Olumsuz"})

    elif zaman_kodu == "NÖ":
        # Nätanyş Öten (Kanıtsal / Evidential)
        if olumsuz:
            zaman_eki = "mandyr" if sesli_tipi == "yogyn" else "mändir"
            parts.append({"text": zaman_eki, "type": "Olumsuz+Zaman", "code": zaman_kodu})
        else:
            unluylebiter_root = root[-1].lower() in TUM_UNLULER
            if unluylebiter_root:
                zaman_eki = "pdyr" if sesli_tipi == "yogyn" else "pdir"
            else:
                if _tek_heceli_dodak(root.lower()):
                    zaman_eki = "updyr" if sesli_tipi == "yogyn" else "üpdir"
                else:
                    zaman_eki = "ypdyr" if sesli_tipi == "yogyn" else "ipdir"
            parts.append({"text": zaman_eki, "type": "Zaman", "code": zaman_kodu})
        sahis_eki = _sahis_ekleri_genisletilmis(sesli_tipi, sahis_kodu)
        if sahis_eki:
            parts.append({"text": sahis_eki, "type": "Şahıs", "code": sahis_kodu})

    elif zaman_kodu == "AÖ":
        # Arzuw-Ökünç (Optative)
        if olumsuz:
            olumsuz_ek = "ma" if sesli_tipi == "yogyn" else "me"
            parts.append({"text": olumsuz_ek, "type": "Olumsuzluk Eki", "code": "Olumsuz"})
        sart_eki = "sa" if sesli_tipi == "yogyn" else "se"
        gecmis_eki = "dy" if sesli_tipi == "yogyn" else "di"
        parts.append({"text": sart_eki, "type": "Şart", "code": "Ş"})
        parts.append({"text": gecmis_eki, "type": "Zaman", "code": zaman_kodu})
        sahis_eki = _sahis_ekleri_standart(sesli_tipi, sahis_kodu)
        if sahis_eki:
            parts.append({"text": sahis_eki, "type": "Şahıs", "code": sahis_kodu})

    elif zaman_kodu in ("FH", "FÖ", "FÄ", "FG"):
        # Fiilimsi formları (şahıs eki yok)
        # parts'tan zamir kaldır (fiilimsiler zamirle kullanılmaz)
        parts = [p for p in parts if p.get("type") != "Şahıs"]
        # Eki doğrudan result'tan hesapla
        govde = root.lower()
        ek = result[len(govde):]
        if ek:
            fiilimsi_tipi = {
                "FH": "Hal işlik", "FÖ": "Öten ortak",
                "FÄ": "Häzirki ortak", "FG": "Geljek ortak"
            }
            parts.append({"text": ek, "type": fiilimsi_tipi[zaman_kodu], "code": zaman_kodu})

    elif zaman_kodu in ("ETT", "EDL"):
        # Ettirgen/Edilgen (şahıs eki yok, derivasyon)
        parts = [p for p in parts if p.get("type") != "Şahıs"]
        govde = root.lower()
        ek = result[len(govde):]
        if ek:
            tip = "Ettirgen" if zaman_kodu == "ETT" else "Edilgen"
            parts.append({"text": ek, "type": tip, "code": zaman_kodu})

    return parts, result


# ==============================================================================
#  CLI ARAYÜZÜ
# ==============================================================================

def baslat():
    """Komut satırı arayüzü — test ve geliştirme için."""
    while True:
        print("\n" + "=" * 60)
        print("🇹🇲 TÜRKMEN MORFOLOJİK MOTOR v26.0")
        print("=" * 60)
        mode = input("[1] İsim (At)  [2] Fiil (İşlik)  [Q] Çıkış\nSeçim: ").lower()
        if mode == 'q':
            break

        kok = input("Kök Söz: ").lower()
        secili_anlam = ""

        # Eş sesli kelime kontrolü
        if kok in ES_SESLILER:
            print(f"\n⚠️ '{kok}' kelimesi eş seslidir. Anlam seçin:")
            for k, v in ES_SESLILER[kok].items():
                print(f"[{k}] {v[0]}")
            secim = input("Seçim: ")
            secili_anlam = ES_SESLILER[kok].get(secim, (kok.upper(), True))[0]

        if mode == '1':
            c = input("Çokluk [e/h]: ").lower() == 'e'
            i = input("İyelik [1, 2, 3 veya boş]: ")
            it = "cog" if i and input("Tip [1] Tekil [2] Çoğul: ") == "2" else "tek"
            h = input("Hal [A2-A6 veya boş]: ").upper()
            res, anl = isim_cekimle(kok, c, "A" + i if i else None, it, h if h else None)
            if secili_anlam:
                print(f"📖 ANLAM: {secili_anlam}")
            print(f"✅ NETİCE: {res}\n🧬 ŞECERE: {anl}")

        elif mode == '2':
            print("[1] Anyk Öten [4] Umumy Häzirki [5] Anyk Häzirki [6] Mälim Geljek [7] Nämälim Geljek")
            z = input("Zaman Seçimi: ")
            s = input("Şahıs [A1-B3]: ").upper()
            o = input("Olumsuz mu? [e/h]: ").lower() == 'e'
            res, anl = fiil_cekimle(kok, z, s, o)
            print(f"\nNETİCE: {res}\nŞECERE: {anl}")


if __name__ == "__main__":
    baslat()