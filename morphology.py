# -*- coding: utf-8 -*-
"""
TÜRKMEN TÜRKÇESİ MORFOLOJİK MOTORU v16.6 (Web)
Sentez (üretim) tabanlı isim ve fiil çekimi
"""

yogyn = set("aouy")
ince = set("eäöiü")
dodak = set("oöuü")
unluler = yogyn | ince
zamirler = {"A1": "Men", "A2": "Sen", "A3": "Ol", "B1": "Biz", "B2": "Siz", "B3": "Olar"}

# Eş sesli sözlüğü
es_sesliler = {
    "at": {"1": ("A:T (Ad, isim)", True), "2": ("AT (At, beygir)", False)},
    "but": {"1": ("BU:T (Vücut bölümü)", True), "2": ("BUT (Temel taşı)", False)},
    "gurt": {"1": ("GU:RT (Kurt, hayvan)", True), "2": ("GURT (Kurutulmuş süzme)", False)},
    "saç": {"1": ("SA:Ç (Sac metal)", True), "2": ("SAÇ (Saç kılı)", False)},
    "yok": {"1": ("YO:K (Yok, var olmayan)", True), "2": ("YOK (Kalıntı, iz)", False)},
    "ot": {"1": ("O:T (Ateş)", False), "2": ("OT (Bitki)", False)}
}

istisnalar = {"asyl": "asl", "pasyl": "pasl", "nesil": "nesl", "ylym": "ylm", "mähir": "mähr"}
genel_dusme_adaylari = {"burun", "alyn", "agyz", "gobek", "ogul", "erin", "bagyr", "sabyr", "kömür", "sygyr", "deňiz"}
yuvarlaklasma_listesi = {"guzy": "guzu", "süri": "sürü", "guýy": "guýu"}

def unlu_niteligi(kelime):
    for h in reversed(kelime.lower()):
        if h in yogyn: return "yogyn"
        if h in ince: return "ince"
    return "yogyn"

def yuvarlak_mi(kelime):
    return any(h in dodak for h in kelime.lower())

def tam_yumusama(kok):
    degisim = {'p': 'b', 'ç': 'j', 't': 'd', 'k': 'g'}
    if kok and kok[-1] in degisim:
        return kok[:-1] + degisim[kok[-1]]
    return kok

def dusme_uygula(kok, ek):
    k = kok.lower(); e = ek.lower()
    if not e or e[0] not in unluler: return k
    if k in istisnalar: return istisnalar[k]
    if k in genel_dusme_adaylari: return k[:-2] + k[-1]
    return k

def isim_cekimle(kok, cokluk=False, iyelik=None, i_tip="tek", hal=None, yumusama_izni=True):
    res = kok.lower()
    yol = [kok]
    is_ozel = res in yuvarlaklasma_listesi
    
    # 1. ÇOKLUK
    if cokluk:
        if is_ozel: res = yuvarlaklasma_listesi[res]
        ek = "lar" if unlu_niteligi(res) == "yogyn" else "ler"
        res += ek; yol.append(ek)

    # 2. İYELİK
    if iyelik:
        nit = unlu_niteligi(res); is_unlu = res[-1] in unluler; kok_yuvarlak = yuvarlak_mi(res)
        if iyelik == "A3" and is_ozel and not cokluk: 
            res = yuvarlaklasma_listesi[res]
            # Yuvarlaklasma sonrası değerleri yeniden hesapla
            nit = unlu_niteligi(res); is_unlu = res[-1] in unluler; kok_yuvarlak = yuvarlak_mi(res)
        
        # Ek Belirleme (Yuvarlaklık Koruma Mantığı)
        if iyelik == "A1":
            if is_unlu: ek = "m" if i_tip=="tek" else ("myz" if nit=="yogyn" else "miz")
            else:
                base = ("um" if nit=="yogyn" else "üm") if kok_yuvarlak else ("ym" if nit=="yogyn" else "im")
                ek = base if i_tip=="tek" else (base + ("yz" if nit=="yogyn" else "iz"))
        elif iyelik == "A2":
            if is_unlu: ek = "ň" if i_tip=="tek" else ("ňyz" if nit=="yogyn" else "ňiz")
            else:
                base = ("uň" if nit=="yogyn" else "üň") if kok_yuvarlak else ("yň" if nit=="yogyn" else "iň")
                ek = base if i_tip=="tek" else (base + ("yz" if nit=="yogyn" else "iz"))
        elif iyelik == "A3":
            if is_unlu:
                ek = ("su" if kok_yuvarlak else "sy") if nit == "yogyn" else ("sü" if kok_yuvarlak else "si")
            else:
                ek = ("u" if nit=="yogyn" else "ü") if kok_yuvarlak else ("y" if nit=="yogyn" else "i")
        
        # Düşme ve Yumuşama
        if ek and ek[0] in unluler:
            res_dusen = dusme_uygula(res, ek)
            if res_dusen != res: res = res_dusen; yol = [res]
            if yumusama_izni: res = tam_yumusama(res)
        res += ek; yol.append(ek)

    # 3. HAL
    if hal:
        if hal in ["A5", "A6"] and is_ozel and not cokluk and not iyelik: res = yuvarlaklasma_listesi[res]
        nit = unlu_niteligi(res); is_unlu = res[-1] in unluler; n_kay = "n" if iyelik == "A3" else "" 
        
        if hal == "A2": ek = n_kay + ("nyň" if is_unlu else ("yň" if nit=="yogyn" else "iň"))
        elif hal == "A3":
            if n_kay: ek = "na" if nit=="yogyn" else "ne"
            elif is_unlu:
                son = res[-1]; res = res[:-1]; ek = "a" if son in "ay" else "ä"
            else: ek = "a" if nit=="yogyn" else "e"
        elif hal == "A4":
            # n_kay varsa (3. tekil iyelikten sonra) veya ünlüyle bitiyorsa ny/ni gelir
            if n_kay or is_unlu:
                ek = "ny" if nit == "yogyn" else "ni"
            else:
                ek = "y" if nit == "yogyn" else "i"
        elif hal == "A5": ek = n_kay + ("da" if nit == "yogyn" else "de")
        elif hal == "A6": ek = n_kay + ("dan" if nit == "yogyn" else "den")
        
        if not n_kay and ek and ek[0] in unluler:
            res = dusme_uygula(res, ek)
            if yumusama_izni and hal in ["A2", "A3", "A4"] and not is_unlu: res = tam_yumusama(res)
        res += ek; yol.append(ek)
        
    return res, " + ".join(yol)


# --- FLASK API UYUMLULUĞU ---

def kelimedeki_unlu_niteligi(kelime):
    nit = unlu_niteligi(kelime)
    return "kalin" if nit == "yogyn" else "ince"

def son_harf_unlu_mu(kelime):
    if not kelime: return False
    return kelime[-1].lower() in unluler


def _build_parts(root, result, yol, s_code, i_code, h_code, cokluk, iyelik):
    """Tek bir çekim sonucu için parts listesi oluşturur."""
    parts = [{"text": root, "type": "Kök", "code": "Kök"}]
    
    if cokluk:
        ek = "lar" if unlu_niteligi(root) == "yogyn" else "ler"
        parts.append({"text": ek, "type": "Sayı", "code": s_code})
    
    if iyelik:
        yol_parts = yol.split(" + ")
        if len(yol_parts) > (2 if cokluk else 1):
            iyelik_eki = yol_parts[2 if cokluk else 1]
            parts.append({"text": iyelik_eki, "type": "Degislilik", "code": i_code})
    
    if h_code and h_code != "H1":
        yol_parts = yol.split(" + ")
        if len(yol_parts) > 1:
            hal_eki = yol_parts[-1]
            display_code = h_code.replace('H', 'A')
            parts.append({"text": hal_eki, "type": "Hal", "code": display_code})
    
    # [Display] A1..B3 kodlarını D₁b..D₃k formatına çevir
    display_map = {
        "A1": "D₁b", "A2": "D₂b", "A3": "D₃b", 
        "B1": "D₁k", "B2": "D₂k", "B3": "D₃k"
    }
    
    for part in parts:
        if part.get("code") in display_map:
            part["code"] = display_map[part["code"]]
            
    return parts


def analyze(root, s_code, i_code, h_code):
    """Flask uyumlu isim çekimi API'si - eş sesliler için çift sonuç döndürür."""
    cokluk = (s_code == "S2")
    
    # İyelik kodu dönüşümü: B1->A1(cog), B2->A2(cog), B3->A3(tek)
    iyelik_map = {"B1": "A1", "B2": "A2", "B3": "A3"}
    iyelik = iyelik_map.get(i_code, i_code) if i_code else None
    i_tip = "cog" if i_code in ["B1", "B2"] else "tek"
    
    # Hal kodu dönüşümü (H2->A2, H3->A3, vb.)
    hal_map = {"H2": "A2", "H3": "A3", "H4": "A4", "H5": "A5", "H6": "A6"}
    hal = hal_map.get(h_code) if h_code and h_code != "H1" else None
    
    root_lower = root.lower()
    
    # Eş sesli kelime kontrolü
    if root_lower in es_sesliler:
        results = []
        for key, (anlam, yumusama) in es_sesliler[root_lower].items():
            result, yol = isim_cekimle(root, cokluk, iyelik, i_tip, hal, yumusama_izni=yumusama)
            parts = _build_parts(root, result, yol, s_code, i_code, h_code, cokluk, iyelik)
            results.append({
                "parts": parts,
                "final_word": result,
                "anlam": anlam
            })
        return results, True  # is_dual=True
    
    # Normal kelime
    result, yol = isim_cekimle(root, cokluk, iyelik, i_tip, hal)
    parts = _build_parts(root, result, yol, s_code, i_code, h_code, cokluk, iyelik)
    return [{"parts": parts, "final_word": result, "anlam": None}], False


# --- FİİL ÇEKİMİ ---

fiil_zamirler = zamirler

def fiil_cekimle(kok, zaman, sahis, olumsuz=False):
    res = kok.lower(); nit = unlu_niteligi(res); is_unlu = res[-1] in unluler; zamir = zamirler[sahis]
    if zaman == "6": # Mälim Geljek
        z_ek = "jak" if nit == "yogyn" else "jek"
        final = res + z_ek + (" däl" if olumsuz else "")
        return f"{zamir} {final}", f"{zamir} + {kok} + {z_ek}" + (" + däl" if olumsuz else "")
    if zaman == "5": # Anyk Häzirki
        tablo = {"otyr":{"A1":"yn","A2":"syň","A3":"","B1":"ys","B2":"syňyz","B3":"lar"}, "dur":{"A1":"un","A2":"suň","A3":"","B1":"us","B2":"suňyz","B3":"lar"}, "ýatyr":{"A1":"yn","A2":"syň","A3":"","B1":"ys","B2":"syňyz","B3":"lar"}, "ýör":{"A1":"ün","A2":"siň","A3":"","B1":"üs","B2":"siňiz","B3":"ler"}}
        if res not in tablo:
            return f"HATA: '{kok}' fiili Anyk Häzirki zamanda çekimlenemez", ""
        s_ek = tablo[res][sahis]
        return (res + s_ek), f"{kok} + {s_ek if s_ek else '(0)'}"
    o_ek = ("ma" if nit=="yogyn" else "me") if olumsuz else ""
    if zaman == "1": # Anyk Öten
        z_ek = "dy" if nit=="yogyn" else "di"; s_ek = {"A1":"m","A2":"ň","A3":"","B1":"k","B2":"ňyz" if nit=="yogyn" else "ňiz","B3":"lar" if nit=="yogyn" else "ler"}[sahis]
    elif zaman == "2": # Daş Öten (Ö2)
        if is_unlu:
            z_ek = "pdy" if nit=="yogyn" else "pdi"
        else:
            z_ek = "ypdy" if nit=="yogyn" else "ipdi"
        s_ek = {"A1":"m","A2":"ň","A3":"","B1":"k","B2":"ňyz" if nit=="yogyn" else "ňiz","B3":"lar" if nit=="yogyn" else "ler"}[sahis]
    elif zaman == "3": # Dowamly Öten (Ö3)
        z_ek = "ýardy" if nit=="yogyn" else "ýärdi"; s_ek = {"A1":"m","A2":"ň","A3":"","B1":"k","B2":"ňyz" if nit=="yogyn" else "ňiz","B3":"lar" if nit=="yogyn" else "ler"}[sahis]
    elif zaman == "4": # Umumy Häzirki
        z_ek = "ýar" if nit=="yogyn" else "ýär"; s_ek = {"A1":"ym" if nit=="yogyn" else "im","A2":"syň" if nit=="yogyn" else "siň","A3":"","B1":"yk" if nit=="yogyn" else "ik","B2":"syňyz" if nit=="yogyn" else "siňiz","B3":"lar" if nit=="yogyn" else "ler"}[sahis]
    elif zaman == "7": # Nämälim Geljek
        if olumsuz: z_ek = "maz" if nit=="yogyn" else "mez"
        else: z_ek = "r" if is_unlu else ("ar" if nit=="yogyn" else "er")
        s_ek = {"A1":"yn" if nit=="yogyn" else "in","A2":"syň" if nit=="yogyn" else "siň","A3":"","B1":"ys" if nit=="yogyn" else "is","B2":"syňyz" if nit=="yogyn" else "siňiz","B3":"lar" if nit=="yogyn" else "ler"}[sahis]
    else:
        return f"HATA: Geçersiz zaman kodu '{zaman}'", ""
    return (res + o_ek + z_ek + s_ek), f"{kok} + {o_ek + ' + ' if o_ek else ''}{z_ek} + {s_ek if s_ek else '(0)'}"


def analyze_verb(root, zaman_kodu, sahis_kodu, olumsuz=False):
    """Flask uyumlu fiil çekimi API'si"""
    
    # Zaman kodu dönüşümü (Ö1->1, H1->4, H2->5, G1->6, G2->7)
    zaman_map = {"Ö1": "1", "Ö2": "2", "Ö3": "3", "H1": "4", "H2": "5", "G1": "6", "G2": "7"}
    zaman = zaman_map.get(zaman_kodu, "1")
    
    # Çekimle
    result, yol = fiil_cekimle(root, zaman, sahis_kodu, olumsuz)
    
    # Hata kontrolü
    if result.startswith("HATA:"):
        return [{"text": result, "type": "Hata", "code": "HATA"}], ""
    
    # Parts formatını oluştur
    parts = []
    nit = unlu_niteligi(root)
    
    # Şahıs zamiri
    parts.append({"text": zamirler.get(sahis_kodu, ""), "type": "Şahıs", "code": sahis_kodu})
    
    # Kök
    parts.append({"text": root, "type": "Kök", "code": "Kök"})
    
    # Zaman ve şahıs eklerini belirle
    if zaman_kodu == "Ö1":
        if olumsuz:
            olumsuz_eki = "ma" if nit == "yogyn" else "me"
            parts.append({"text": olumsuz_eki, "type": "Olumsuzluk Eki", "code": "Olumsuz"})
        z_ek = "dy" if nit == "yogyn" else "di"
        parts.append({"text": z_ek, "type": "Zaman", "code": zaman_kodu})
        s_ek = {"A1":"m","A2":"ň","A3":"","B1":"k","B2":"ňyz" if nit=="yogyn" else "ňiz","B3":"lar" if nit=="yogyn" else "ler"}[sahis_kodu]
        if s_ek:
            parts.append({"text": s_ek, "type": "Şahıs", "code": sahis_kodu})
    
    elif zaman_kodu == "Ö2":
        is_unlu = root[-1].lower() in unluler
        if olumsuz:
            olumsuz_eki = "ma" if nit == "yogyn" else "me"
            parts.append({"text": olumsuz_eki, "type": "Olumsuzluk Eki", "code": "Olumsuz"})
        if is_unlu:
            z_ek = "pdy" if nit == "yogyn" else "pdi"
        else:
            z_ek = "ypdy" if nit == "yogyn" else "ipdi"
        parts.append({"text": z_ek, "type": "Zaman", "code": zaman_kodu})
        s_ek = {"A1":"m","A2":"ň","A3":"","B1":"k","B2":"ňyz" if nit=="yogyn" else "ňiz","B3":"lar" if nit=="yogyn" else "ler"}[sahis_kodu]
        if s_ek:
            parts.append({"text": s_ek, "type": "Şahıs", "code": sahis_kodu})
    
    elif zaman_kodu == "Ö3":
        if olumsuz:
            olumsuz_eki = "ma" if nit == "yogyn" else "me"
            parts.append({"text": olumsuz_eki, "type": "Olumsuzluk Eki", "code": "Olumsuz"})
        z_ek = "ýardy" if nit == "yogyn" else "ýärdi"
        parts.append({"text": z_ek, "type": "Zaman", "code": zaman_kodu})
        s_ek = {"A1":"m","A2":"ň","A3":"","B1":"k","B2":"ňyz" if nit=="yogyn" else "ňiz","B3":"lar" if nit=="yogyn" else "ler"}[sahis_kodu]
        if s_ek:
            parts.append({"text": s_ek, "type": "Şahıs", "code": sahis_kodu})
    
    elif zaman_kodu == "H1":
        if olumsuz:
            z_ek = "maýar" if nit == "yogyn" else "meýär"
        else:
            z_ek = "ýar" if nit == "yogyn" else "ýär"
        parts.append({"text": z_ek, "type": "Zaman", "code": zaman_kodu})
        s_ekleri = {"A1":"ym" if nit=="yogyn" else "im","A2":"syň" if nit=="yogyn" else "siň","A3":"","B1":"yk" if nit=="yogyn" else "ik","B2":"syňyz" if nit=="yogyn" else "siňiz","B3":"lar" if nit=="yogyn" else "ler"}
        s_ek = s_ekleri[sahis_kodu]
        if s_ek:
            parts.append({"text": s_ek, "type": "Şahıs", "code": sahis_kodu})
    
    elif zaman_kodu == "H2":
        s_ekleri = {"A1":"yn","A2":"syň","A3":"","B1":"ys","B2":"syňyz","B3":"lar"}
        s_ek = s_ekleri.get(sahis_kodu, "")
        if s_ek:
            parts.append({"text": s_ek, "type": "Şahıs", "code": sahis_kodu})
    
    elif zaman_kodu == "G1":
        z_ek = "jak" if nit == "yogyn" else "jek"
        parts.append({"text": z_ek, "type": "Zaman", "code": zaman_kodu})
        if olumsuz:
            parts.append({"text": "däl", "type": "Olumsuzluk", "code": "Olumsuz"})
    
    elif zaman_kodu == "G2":
        is_unlu = root[-1].lower() in unluler
        if olumsuz:
            z_ek = "maz" if nit == "yogyn" else "mez"
        else:
            z_ek = "r" if is_unlu else ("ar" if nit == "yogyn" else "er")
        parts.append({"text": z_ek, "type": "Zaman", "code": zaman_kodu})
        s_ekleri = {"A1":"yn" if nit=="yogyn" else "in","A2":"syň" if nit=="yogyn" else "siň","A3":"","B1":"ys" if nit=="yogyn" else "is","B2":"syňyz" if nit=="yogyn" else "siňiz","B3":"lar" if nit=="yogyn" else "ler"}
        s_ek = s_ekleri[sahis_kodu]
        if s_ek:
            parts.append({"text": s_ek, "type": "Şahıs", "code": sahis_kodu})
    
    return parts, result


# --- CLI ARAYÜZÜ ---

def baslat():
    while True:
        print("\n" + "="*60 + "\n🇹🇲 TÜRKMEN MORFOLOJİK MOTOR v16.6\n" + "="*60)
        mode = input("[1] İsim (At)  [2] Fiil (İşlik)  [Q] Çıkış\nSeçim: ").lower()
        if mode == 'q': break
        
        kok = input("Kök Söz: ").lower()
        yumusama_izni, secili_anlam = True, ""

        if kok in es_sesliler:
            print(f"\n⚠️ '{kok}' kelimesi eş seslidir. Anlam seçin:")
            for k, v in es_sesliler[kok].items(): print(f"[{k}] {v[0]}")
            secim = input("Seçim: ")
            secili_anlam, yumusama_izni = es_sesliler[kok].get(secim, (kok.upper(), True))

        if mode == '1':
            c = input("Çokluk [e/h]: ").lower() == 'e'
            i = input("İyelik [1, 2, 3 veya boş]: ")
            it = "cog" if i and input("Tip [1] Tekil [2] Çoğul: ") == "2" else "tek"
            h = input("Hal [A2-A6 veya boş]: ").upper()
            res, anl = isim_cekimle(kok, c, "A"+i if i else None, it, h if h else None, yumusama_izni)
            if secili_anlam: print(f"📖 ANLAM: {secili_anlam}")
            print(f"✅ NETİCE: {res}\n🧬 ŞECERE: {anl}")
        elif mode == '2':
            print("[1] Anyk Öten [4] Umumy Häzirki [5] Anyk Häzirki [6] Mälim Geljek [7] Nämälim Geljek")
            z = input("Zaman Seçimi: "); s = input("Şahıs [A1-B3]: ").upper(); o = input("Olumsuz mu? [e/h]: ").lower() == 'e'
            res, anl = fiil_cekimle(kok, z, s, o)
            print(f"\nNETİCE: {res}\nŞECERE: {anl}")
        else: continue

if __name__ == "__main__":
    baslat()