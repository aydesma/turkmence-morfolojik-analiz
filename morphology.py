# -*- coding: utf-8 -*-
"""
TÜRKMEN TÜRKÇESİ MORFOLOJİK MOTORU v26.0
Sentez (üretim) tabanlı isim ve fiil çekimi
[cite_start]Gökçür (2018) ve Kullanıcı Tanımlı Anlam Sözlüğü [cite: 347-389]
"""

# Tüm fonksiyonlar (unlu_niteligi, dusme_kontrol, isim_cekimle, fiil_cekimle) 
# yukarıdaki v15.3 kurallarını içerecek şekilde bu blokta birleşmiştir.

yogyn = set("aouy")
ince = set("eäöiü")
dodak = set("oöuü")
unluler = yogyn | ince
zamirler = {"A1": "Men", "A2": "Sen", "A3": "Ol", "B1": "Biz", "B2": "Siz", "B3": "Olar"}
istisnalar = {"asyl": "asl", "pasyl": "pasl", "nesil": "nesl", "ylym": "ylm", "mähir": "mähr"}
yon_sozcukleri = {"bäri", "aňry", "ýokary", "ileri"}
genel_dusme_adaylari = {"burun", "alyn", "agyz", "gobek", "ogul", "erin", "bagyr", "sabyr", "kömür"}

# [v26.0] Eş yazılımlı kelimeler - p, ç, t, k ile bitenlerde çift çekim
dual_cekilecekler = {
    "at": {"kisa": "At, beygir", "uzun": "Ad, isim"},
    "but": {"kisa": "Evin temelini ayakta tutan taş", "uzun": "İnsan vücudunun kalça ile diz arasındaki bölümü"},
    "gurt": {"kisa": "Kurutulmuş, süzme", "uzun": "Kurt"},
    "saç": {"kisa": "Baş derisini kaplayan kıllar", "uzun": "Yassı demir çelik ürünü, sac"},
    "yok": {"kisa": "Kalıntı, iz", "uzun": "Var olmayan, yok"}
}

diger_es_sesliler = {
    "baş": "1. Kafa, baş. 2. Yara, çıban.",
    "biz": "1. Şahıs zamiri. 2. Tığ, çuvaldız.",
    "daş": "1. Uzak, dış. 2. Taş, kaya."
}

def unlu_niteligi(kelime):
    for h in reversed(kelime.lower()):
        if h in yogyn: return "yogyn"
        if h in ince: return "ince"
    return "yogyn"

def yuvarlak_mi(kelime):
    return any(h in dodak for h in kelime.lower())

def hece_sayisi(kelime):
    return sum(1 for h in kelime if h in unluler)

def tam_yumusama(kok):
    degisim = {'p': 'b', 'ç': 'j', 't': 'd', 'k': 'g'}
    if kok and kok[-1] in degisim:
        return kok[:-1] + degisim[kok[-1]]
    return kok

def dusme_kontrol(kok, ek):
    k = kok.lower()
    e = ek.lower()
    if not e: return k
    if k in yon_sozcukleri and e[0] in set("dklrs"): return k[:-1]
    if e[0] in unluler:
        if k in istisnalar: return istisnalar[k]
        if k in genel_dusme_adaylari: return k[:-2] + k[-1]
        if k.endswith(("ýyş", "ýiş")): return k[:-2] + k[-1]
        if hece_sayisi(k) == 2 and k[-1] in set("zlnrsş"):
            u_list = [h for h in k if h in unluler]
            if len(u_list) == 2 and u_list[1] in set("yiuü"):
                pos = k.rfind(u_list[1]); 
                if pos > 0 and k[pos-1] not in set("zdj"): return k[:pos] + k[pos+1:]
    return k

def isim_cekimle(kok, cokluk=False, iyelik=None, i_tip="tek", hal=None, yumusama_izni=True):
    res = kok.lower()
    yol = [kok]
    
    # [v26.0] BERDİ HOCA ÖZEL KURALI: Guzy/Süri Yuvarlaklaşması
    # Sadece San (Çokluk), A3 ve B3 kategorilerinde kök değişir.
    if res in ["guzy", "süri"] and (cokluk or iyelik in ["A3", "B3"]):
        res = "guzu" if res == "guzy" else "sürü"
    
    if cokluk:
        ek = "lar" if unlu_niteligi(res) == "yogyn" else "ler"
        res += ek; yol.append(ek)
    if iyelik:
        nit = unlu_niteligi(res); is_unlu = res[-1] in unluler; is_dodak = yuvarlak_mi(res)
        if iyelik == "A1":
            if is_unlu: ek = "m" if i_tip=="tek" else ("myz" if nit=="yogyn" else "miz")
            else:
                base = ("um" if nit=="yogyn" else "üm") if is_dodak else ("ym" if nit=="yogyn" else "im")
                ek = base if i_tip=="tek" else (base + ("yz" if nit=="yogyn" else "iz"))
        elif iyelik == "A2":
            if is_unlu: ek = "ň" if i_tip=="tek" else ("ňyz" if nit=="yogyn" else "ňiz")
            else:
                base = ("uň" if nit=="yogyn" else "üň") if is_dodak else ("yň" if nit=="yogyn" else "iň")
                ek = base if i_tip=="tek" else (base + ("yz" if nit=="yogyn" else "iz"))
        elif iyelik == "B1":
            # Biz (1. Çoğul)
            if is_unlu: ek = ("myz" if nit=="yogyn" else "miz")
            else:
                base = ("um" if nit=="yogyn" else "üm") if is_dodak else ("ym" if nit=="yogyn" else "im")
                ek = base + ("yz" if nit=="yogyn" else "iz")
        elif iyelik == "B2":
            # Siz (2. Çoğul)
            if is_unlu: ek = ("ňyz" if nit=="yogyn" else "ňiz")
            else:
                base = ("uň" if nit=="yogyn" else "üň") if is_dodak else ("yň" if nit=="yogyn" else "iň")
                ek = base + ("yz" if nit=="yogyn" else "iz")
        elif iyelik == "A3":
            # [v26.0] Ol (3. Tekil): Suffix rounds if stem is rounded (sürüsü)
            if is_unlu: ek = ("su" if is_dodak else "sy") if nit=="yogyn" else ("sü" if is_dodak else "si")
            else: ek = "u" if (nit=="yogyn" and is_dodak) else ("ü" if is_dodak else ("y" if nit=="yogyn" else "i"))
        elif iyelik == "B3":
            # [v26.0] Olar (3. Çoğul): Suffix stays unrounded (sürüsi)
            ek = ("sy" if nit=="yogyn" else "si") if is_unlu else ("y" if nit=="yogyn" else "i")
        res = dusme_kontrol(res, ek)
        if ek and ek[0] in unluler and yumusama_izni: res = tam_yumusama(res)
        res += ek; yol.append(ek)
    if hal:
        nit = unlu_niteligi(res); is_unlu = res[-1] in unluler; n_kay = "n" if iyelik == "A3" else "" 
        if hal == "A2": ek = n_kay + ("nyň" if is_unlu else ("yň" if nit=="yogyn" else "iň"))
        elif hal == "A3":
            if n_kay: ek = "na" if nit=="yogyn" else "ne"
            elif is_unlu:
                son = res[-1]; res = res[:-1]; ek = "a" if son in "ay" else "ä"
            else: ek = "a" if nit=="yogyn" else "e"
        elif hal == "A4": ek = n_kay + ("ny" if is_unlu else ("y" if nit=="yogyn" else "i"))
        elif hal == "A5": ek = n_kay + ("da" if nit == "yogyn" else "de")
        elif hal == "A6": ek = n_kay + ("dan" if nit == "yogyn" else "den")
        res_temp = dusme_kontrol(res, ek)
        if hal in ["A2", "A3", "A4"] and not is_unlu: res_temp = tam_yumusama(res_temp)
        res = res_temp + ek; yol.append(ek)
    return res, " + ".join(yol)

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
        z_ek = "dy" if nit=="yogyn" else "di"; s_ek = {"A1":"m","A2":"ň","A3":"","B1":"k","B2":"ňyz","B3":"lar" if nit=="yogyn" else "ler"}[sahis]
    elif zaman == "2": # Daş Öten (Ö2)
        # -ypdy/-ipdi eki (ünsüz sonrası), -pdy/-pdi (ünlü sonrası)
        if is_unlu:
            z_ek = "pdy" if nit=="yogyn" else "pdi"
        else:
            z_ek = "ypdy" if nit=="yogyn" else "ipdi"
        s_ek = {"A1":"m","A2":"ň","A3":"","B1":"k","B2":"ňyz","B3":"lar" if nit=="yogyn" else "ler"}[sahis]
    elif zaman == "3": # Dowamly Öten (Ö3)
        z_ek = "ýardy" if nit=="yogyn" else "ýärdi"; s_ek = {"A1":"m","A2":"ň","A3":"","B1":"k","B2":"ňyz","B3":"lar" if nit=="yogyn" else "ler"}[sahis]
    elif zaman == "4": # Umumy Häzirki
        z_ek = "ýar" if nit=="yogyn" else "ýär"; s_ek = {"A1":"ym" if nit=="yogyn" else "im","A2":"syň" if nit=="yogyn" else "siň","A3":"","B1":"yk" if nit=="yogyn" else "ik","B2":"syňyz" if nit=="yogyn" else "siňiz","B3":"lar" if nit=="yogyn" else "ler"}[sahis]
    elif zaman == "7": # Nämälim Geljek
        if olumsuz: z_ek = "maz" if nit=="yogyn" else "mez"
        else: z_ek = "r" if is_unlu else ("ar" if nit=="yogyn" else "er")
        s_ek = {"A1":"yn" if nit=="yogyn" else "in","A2":"syň" if nit=="yogyn" else "siň","A3":"","B1":"ys" if nit=="yogyn" else "is","B2":"syňyz" if nit=="yogyn" else "siňiz","B3":"lar" if nit=="yogyn" else "ler"}[sahis]
    else:
        return f"HATA: Geçersiz zaman kodu '{zaman}'", ""
    return (res + o_ek + z_ek + s_ek), f"{kok} + {o_ek + ' + ' if o_ek else ''}{z_ek} + {s_ek if s_ek else '(0)'}"


# --- FLASK API UYUMLULUĞU ---

# Ünlü niteliği yardımcı fonksiyonları (eski API uyumu için)
def kelimedeki_unlu_niteligi(kelime):
    nit = unlu_niteligi(kelime)
    return "kalin" if nit == "yogyn" else "ince"

def son_harf_unlu_mu(kelime):
    if not kelime: return False
    return kelime[-1].lower() in unluler


def analyze(root, s_code, i_code, h_code):
    """Flask uyumlu isim çekimi API'si"""
    cokluk = (s_code == "S2")
    
    # İyelik kodu dönüşümü (A1, A2, A3, B1, B2, B3)
    iyelik = i_code if i_code else None
    
    # Hal kodu dönüşümü (H2->A2, H3->A3, vb.)
    hal_map = {"H2": "A2", "H3": "A3", "H4": "A4", "H5": "A5", "H6": "A6"}
    hal = hal_map.get(h_code) if h_code and h_code != "H1" else None
    
    # İyelik tipi belirleme (B1, B2 için çoğul)
    i_tip = "cog" if i_code in ["B1", "B2"] else "tek"
    
    # Çekimle
    result, yol = isim_cekimle(root, cokluk, iyelik, i_tip, hal)
    
    # Parts formatını oluştur
    parts = [{"text": root, "type": "Kök", "code": "Kök"}]
    
    if cokluk:
        ek = "lar" if unlu_niteligi(root) == "yogyn" else "ler"
        parts.append({"text": ek, "type": "Sayı", "code": s_code})
    
    if iyelik:
        # Yol'dan eki çıkar
        yol_parts = yol.split(" + ")
        if len(yol_parts) > (2 if cokluk else 1):
            iyelik_eki = yol_parts[2 if cokluk else 1]
            parts.append({"text": iyelik_eki, "type": "Degislilik", "code": i_code})
    
    if hal:
        # Hal eki
        yol_parts = yol.split(" + ")
        if len(yol_parts) > 1:
            hal_eki = yol_parts[-1]
            if hal_eki != "(uzun)":
                display_code = h_code.replace('H', 'A')
                parts.append({"text": hal_eki, "type": "Hal", "code": display_code})
    
    return parts, result


# Fiil zamirler (eski API uyumu için)
fiil_zamirler = zamirler

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
        print("\n" + "="*60 + "\n🇹🇲 TÜRKMEN MORFOLOJİK MOTOR v26.0\n" + "="*60)
        mode = input("[1] İsim (At)  [2] Fiil (İşlik)  [Q] Çıkış\nSeçim: ").lower()
        if mode == 'q': break
        
        kok = input("Kök Söz (örn: süri, guzy, at, saç, yok): ").lower()
        if mode == '1':
            c = input("Çokluk (lar/ler) [e/h]: ").lower() == 'e'
            i = input("İyelik [1:Men, 2:Sen, 3:Ol, 4:Olar, boş]: ")
            iy_kod = {"1":"A1", "2":"A2", "3":"A3", "4":"B3"}.get(i)
            it = "cog" if i in ["1", "2"] and input("Tip [1] Tekil [2] Çoğul: ") == "2" else "tek"
            h = input("Hal [A2-A6 veya boş]: ").upper()
            
            # [v26.0] Eş yazılımlı kelime kontrolü
            if kok in dual_cekilecekler:
                print(f"\n💡 '{kok}' eş yazılımlı çekimleri:")
                res_k, _ = isim_cekimle(kok, c, iy_kod, it, h if h else None, yumusama_izni=False)
                print(f"✅ {dual_cekilecekler[kok]['kisa']}: {res_k}")
                res_u, _ = isim_cekimle(kok, c, iy_kod, it, h if h else None, yumusama_izni=True)
                print(f"✅ {dual_cekilecekler[kok]['uzun']}: {res_u}")
                continue
            elif kok in diger_es_sesliler:
                res, anl = isim_cekimle(kok, c, iy_kod, it, h if h else None)
                print(f"\nNETİCE: {res}\n📖 Anlamlar: {diger_es_sesliler[kok]}")
                continue
            else:
                res, anl = isim_cekimle(kok, c, iy_kod, it, h if h else None)
        elif mode == '2':
            print("[1] Anyk Öten [4] Umumy Häzirki [5] Anyk Häzirki [6] Mälim Geljek [7] Nämälim Geljek")
            z = input("Zaman Seçimi: "); s = input("Şahıs [A1-B3]: ").upper(); o = input("Olumsuz mu? [e/h]: ").lower() == 'e'
            res, anl = fiil_cekimle(kok, z, s, o)
        else: continue
        
        print(f"\nNETİCE: {res}\nŞECERE: {anl}")

if __name__ == "__main__":
    baslat()