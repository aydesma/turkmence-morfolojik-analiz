# -*- coding: utf-8 -*-
"""
TÜRKMEN TÜRKÇESİ MORFOLOJİK MOTORU v12.0
Sentez (üretim) tabanlı isim ve fiil çekimi
"""

yogyn = set("aouy")
ince = set("eäöiü")
unluler = yogyn | ince

# Sabit İstisnalar ve Özel Gruplar
istisnalar = {"asyl": "asl", "pasyl": "pasl", "nesil": "nesl", "ylym": "ylm", "mähir": "mähr"}
yon_sozcukleri = {"bäri", "aňry", "ýokary", "ileri"}
zamirler = {"A1": "Men", "A2": "Sen", "A3": "Ol", "B1": "Biz", "B2": "Siz", "B3": "Olar"}

# --- FONETİK MOTOR FONKSİYONLARI ---

def unlu_niteligi(kelime):
    for h in reversed(kelime.lower()):
        if h in yogyn: return "yogyn"
        if h in ince: return "ince"
    return "yogyn"

def hece_sayisi(kelime):
    return sum(1 for h in kelime if h in unluler)

def kural_yumusama(kok):
    degisim = {'p': 'b', 'ç': 'c', 't': 'd', 'k': 'g'}
    return kok[:-1] + degisim[kok[-1]] if kok and kok[-1] in degisim else kok

def dusme_algoritmasi(kok, ek):
    res_kok = kok.lower()
    ek_lower = ek.lower()
    if not ek_lower: return res_kok

    # 1. Yön Sözcükleri (Bäri + de -> Bärde)
    if res_kok in yon_sozcukleri and ek_lower[0] in set("dklrs"):
        return res_kok[:-1]

    # 2. Ünlü ile başlayan eklerde düşme kontrolleri
    if ek_lower[0] in unluler:
        # a) İstisnalar (Ylym -> ylmy)
        if res_kok in istisnalar: return istisnalar[res_kok]
        
        # b) Türetilmiş Ekler (-ýyş -> ýaşaýşym)
        if res_kok.endswith(("ýyş", "ýiş")):
            return res_kok[:-2] + res_kok[-1]
            
        # c) Genel Kural (2 heceli, z,l,n,r,s,ş bitişli, zdj olmayan)
        if hece_sayisi(res_kok) == 2 and res_kok[-1] in set("zlnrsş"):
            u_list = [h for h in res_kok if h in unluler]
            if len(u_list) >= 2:
                dar_unlu = u_list[1]
                if dar_unlu in set("yiuü"):
                    pos = res_kok.rfind(dar_unlu)
                    if pos > 0 and res_kok[pos-1] not in set("zdj"):
                        return res_kok[:pos] + res_kok[pos+1:]
    return res_kok

# --- MODÜL 1: İSİM ÇEKİMİ (AT) ---

def isim_cekimle(kok, cokluk=False, iyelik=None, i_tip="tek", hal=None):
    res = kok.lower()
    yol = [kok]
    
    if cokluk:
        ek = "lar" if unlu_niteligi(res) == "yogyn" else "ler"
        res += ek
        yol.append(ek)

    if iyelik:
        nit = unlu_niteligi(res)
        is_unlu = res[-1] in unluler
        h_say = hece_sayisi(res)
        
        # İyelik eki belirleme (A3+ ve A3- kuralları dahil)
        if iyelik == "A1":
            if is_unlu: ek = "m" if i_tip=="tek" else ("myz" if nit=="yogyn" else "miz")
            else:
                base = ("um" if nit=="yogyn" else "üm") if (h_say < 2 and any(h in "oöuü" for h in res)) else ("ym" if nit=="yogyn" else "im")
                ek = base if i_tip=="tek" else (base + ("yz" if nit=="yogyn" else "iz"))
        elif iyelik == "A2":
            if is_unlu: ek = "ň" if i_tip=="tek" else ("ňyz" if nit=="yogyn" else "ňiz")
            else:
                base = ("uň" if nit=="yogyn" else "üň") if (h_say < 2 and any(h in "oöuü" for h in res)) else ("yň" if nit=="yogyn" else "iň")
                ek = base if i_tip=="tek" else (base + ("yz" if nit=="yogyn" else "iz"))
        elif iyelik == "A3":
            ek = ("sy" if nit == "yogyn" else "si") if is_unlu else ("y" if nit == "yogyn" else "i")
        elif iyelik == "B1":
            if is_unlu: ek = "myz" if nit=="yogyn" else "miz"
            else:
                base = ("um" if nit=="yogyn" else "üm") if (h_say < 2 and any(h in "oöuü" for h in res)) else ("ym" if nit=="yogyn" else "im")
                ek = base + ("yz" if nit=="yogyn" else "iz")
        elif iyelik == "B2":
            if is_unlu: ek = "ňyz" if nit=="yogyn" else "ňiz"
            else:
                base = ("uň" if nit=="yogyn" else "üň") if (h_say < 2 and any(h in "oöuü" for h in res)) else ("yň" if nit=="yogyn" else "iň")
                ek = base + ("yz" if nit=="yogyn" else "iz")
        elif iyelik == "B3":
            ek = ("sy" if nit == "yogyn" else "si") if is_unlu else ("y" if nit == "yogyn" else "i")
        else:
            ek = ""

        res = dusme_algoritmasi(res, ek)
        if ek and ek[0] in unluler: res = kural_yumusama(res)
        res += ek
        yol.append(ek)

    if hal:
        nit = unlu_niteligi(res)
        n_kay = "n" if iyelik == "A3" or iyelik == "B3" else ""
        if hal == "A3": # Ýöneliş
            ek = "a" if nit == "yogyn" else "e"
            if iyelik == "A3" or iyelik == "B3": 
                res += "na" if nit == "yogyn" else "ne"
                yol.append("na" if nit == "yogyn" else "ne")
            elif res[-1] in unluler:
                son = res[-1]
                if son == "a": ek = ""
                elif son == "e": res = res[:-1] + "ä"; ek = ""
                elif son == "y": res = res[:-1] + "a"; ek = ""
                elif son == "i": res = res[:-1] + "ä"; ek = ""
                res += ek
                yol.append(ek if ek else "(uzun)")
            else: 
                res = kural_yumusama(res)
                res += ek
                yol.append(ek)
        else: # A2, A4, A5, A6
            base = {"A2":"yň", "A4":"y", "A5":"da", "A6":"dan"}
            ek = base[hal] if nit == "yogyn" else base[hal].replace("a","e").replace("y","i")
            res = dusme_algoritmasi(res, n_kay + ek)
            res += n_kay + ek
            yol.append(n_kay + ek)
            
    return res, " + ".join(yol)


# --- MODÜL 2: FİİL ÇEKİMİ (İŞLİK) ---

def fiil_cekimle(kok, zaman, sahis, olumsuz=False):
    res = kok.lower()
    nit = unlu_niteligi(res)
    is_unlu = res[-1] in unluler
    zamir = zamirler[sahis]
    
    if zaman == "6": # Mälim Geljek
        z_ek = "jak" if nit == "yogyn" else "jek"
        final = res + z_ek + (" däl" if olumsuz else "")
        return f"{zamir} {final}", f"{zamir} + {kok} + {z_ek}" + (" + däl" if olumsuz else "")

    if zaman == "5": # Anyk Häzirki
        tablo = {"otyr":{"A1":"yn","A2":"syň","A3":"","B1":"ys","B2":"syňyz","B3":"lar"},
                 "dur":{"A1":"un","A2":"suň","A3":"","B1":"us","B2":"suňyz","B3":"lar"},
                 "ýatyr":{"A1":"yn","A2":"syň","A3":"","B1":"ys","B2":"syňyz","B3":"lar"},
                 "ýör":{"A1":"ün","A2":"siň","A3":"","B1":"üs","B2":"siňiz","B3":"ler"}}
        if res not in tablo:
            return f"HATA: '{kok}' fiili Anyk Häzirki zamanda çekimlenemez", ""
        s_ek = tablo[res][sahis]
        return f"{zamir} {res + s_ek}", f"{zamir} + {kok} + {s_ek if s_ek else '(0)'}"

    o_ek = ("ma" if nit=="yogyn" else "me") if olumsuz else ""
    if zaman == "1": # Anyk Öten
        z_ek = "dy" if nit=="yogyn" else "di"
        s_ek = {"A1":"m","A2":"ň","A3":"","B1":"k","B2":"ňyz","B3":"lar" if nit=="yogyn" else "ler"}[sahis]
    elif zaman == "4": # Umumy Häzirki
        z_ek = "ýar" if nit=="yogyn" else "ýär"
        s_ek = {"A1":"yn" if nit=="yogyn" else "in","A2":"syň" if nit=="yogyn" else "siň","A3":"","B1":"ys" if nit=="yogyn" else "is","B2":"syňyz" if nit=="yogyn" else "siňiz","B3":"lar" if nit=="yogyn" else "ler"}[sahis]
    elif zaman == "7": # Nämälim Geljek
        if olumsuz: z_ek = "maz" if nit=="yogyn" else "mez"
        else: z_ek = "r" if is_unlu else ("ar" if nit=="yogyn" else "er")
        s_ek = {"A1":"yn" if nit=="yogyn" else "in","A2":"syň" if nit=="yogyn" else "siň","A3":"","B1":"ys" if nit=="yogyn" else "is","B2":"syňyz" if nit=="yogyn" else "siňiz","B3":"lar" if nit=="yogyn" else "ler"}[sahis]
    else:
        return f"HATA: Geçersiz zaman kodu '{zaman}'", ""

    return f"{zamir} {res + o_ek + z_ek + s_ek}", f"{zamir} + {kok} + {o_ek + ' + ' if o_ek else ''}{z_ek} + {s_ek if s_ek else '(0)'}"


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
    
    elif zaman_kodu == "H1":
        if olumsuz:
            z_ek = "maýar" if nit == "yogyn" else "meýär"
        else:
            z_ek = "ýar" if nit == "yogyn" else "ýär"
        parts.append({"text": z_ek, "type": "Zaman", "code": zaman_kodu})
        s_ekleri = {"A1":"yn" if nit=="yogyn" else "in","A2":"syň" if nit=="yogyn" else "siň","A3":"","B1":"ys" if nit=="yogyn" else "is","B2":"syňyz" if nit=="yogyn" else "siňiz","B3":"lar" if nit=="yogyn" else "ler"}
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
        print("\n" + "="*45 + "\n🇹🇲 TÜRKMEN MORFOLOJİK MOTOR v12.0 (Sentez)\n" + "="*45)
        mode = input("[1] İsim (At) Çekimle\n[2] Fiil (İşlik) Çekimle\n[Q] Çıkış\nSeçim: ").lower()
        if mode == 'q': break
        
        kok = input("Kök: ").lower()
        if mode == '1':
            c = input("San (lar/ler) [e/h]: ").lower() == 'e'
            i = input("İyelik [1, 2, 3 veya boş]: ")
            i_t = "cog" if i and input("İyelik Tipi [1] Tekil [2] Çoğul: ") == "2" else "tek"
            h = input("Hal [A2, A3, A4, A5, A6 veya boş]: ").upper()
            res, anl = isim_cekimle(kok, c, "A"+i if i else None, i_t, h if h else None)
        else:
            print("[1] Anyk Öten [4] Umumy Häzirki [5] Anyk Häzirki [6] Mälim Geljek [7] Nämälim Geljek")
            z = input("Zaman: ")
            s = input("Şahıs [A1...B3]: ").upper()
            o = input("Olumsuz mu? [e/h]: ").lower() == 'e'
            res, anl = fiil_cekimle(kok, z, s, o)
        
        print(f"\nNETİCE: {res}\nŞECERE: {anl}")

if __name__ == "__main__":
    baslat()