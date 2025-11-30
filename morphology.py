# Temel Tanımlar
unluler = set("aeäuüyiöo")
kalin_unluler = set("aouy")
ince_unluler = set("eäiüö")
duz_unluler = set("aäeyi")
yuvarlak_unluler = set("oöuü")

def son_harf_unlu_mu(kelime):
    if not kelime: return False
    return kelime[-1].lower() in unluler

def kelimedeki_unlu_niteligi(kelime):
    # DÜZELTME: Kelimeyi ters çevirip (reversed) tarıyoruz.
    # Böylece 'gözler' kelimesinde 'e' harfini bulup ona göre karar veriyor.
    for h in reversed(kelime.lower()):
        if h in kalin_unluler: return "kalin"
        elif h in ince_unluler: return "ince"
    return "ince"

def kelimedeki_unlu_niteligi_tam(kelime):
    # DÜZELTME: Burada da tersten tarama yapıyoruz.
    for h in reversed(kelime.lower()):
        if h in kalin_unluler:
            return "kalin-duz" if h in duz_unluler else "kalin-yuvarlak"
        elif h in ince_unluler:
            return "ince-duz" if h in duz_unluler else "ince-yuvarlak"
    return "ince-duz"

# --- EKLER ---
# Sayı (San)
def sayi_S2(kelime):
    nitelik = kelimedeki_unlu_niteligi(kelime)
    suffix = "lar" if nitelik == "kalin" else "ler"
    return kelime + suffix, suffix

# İyelik (Degislilik)
def iyelik_A1(kelime): 
    if son_harf_unlu_mu(kelime): return kelime + "m", "m"
    nitelik = kelimedeki_unlu_niteligi_tam(kelime)
    map_ek = {"kalin-duz": "ym", "kalin-yuvarlak": "um", "ince-duz": "im", "ince-yuvarlak": "üm"}
    suffix = map_ek.get(nitelik, "im")
    return kelime + suffix, suffix

def iyelik_A2(kelime): 
    if son_harf_unlu_mu(kelime): return kelime + "ň", "ň"
    nitelik = kelimedeki_unlu_niteligi_tam(kelime)
    map_ek = {"kalin-duz": "yň", "kalin-yuvarlak": "uň", "ince-duz": "iň", "ince-yuvarlak": "üň"}
    suffix = map_ek.get(nitelik, "iň")
    return kelime + suffix, suffix

def iyelik_A3(kelime): 
    nitelik = kelimedeki_unlu_niteligi(kelime)
    kalin = nitelik == "kalin"
    suffix = ""
    if son_harf_unlu_mu(kelime): suffix = "sy" if kalin else "si"
    else: suffix = "y" if kalin else "i"
    return kelime + suffix, suffix

def iyelik_B1(kelime): 
    nitelik_tam = kelimedeki_unlu_niteligi_tam(kelime)
    kalin = nitelik_tam.startswith("kalin")
    if son_harf_unlu_mu(kelime): 
        suffix = "myz" if kalin else "miz"
    else:
        map_ek = {"kalin-duz": "ymyz", "kalin-yuvarlak": "umyz", "ince-duz": "imiz", "ince-yuvarlak": "ümiz"}
        suffix = map_ek.get(nitelik_tam, "imiz")
    return kelime + suffix, suffix

def iyelik_B2(kelime): 
    nitelik_tam = kelimedeki_unlu_niteligi_tam(kelime)
    kalin = nitelik_tam.startswith("kalin")
    if son_harf_unlu_mu(kelime): 
        suffix = "ňyz" if kalin else "ňiz"
    else:
        map_ek = {"kalin-duz": "yňyz", "kalin-yuvarlak": "uňyz", "ince-duz": "iňiz", "ince-yuvarlak": "üňiz"}
        suffix = map_ek.get(nitelik_tam, "iňiz")
    return kelime + suffix, suffix

# Hal (Düşüm)
def hal_H1(kelime): return kelime, "" 
def hal_H2(kelime): 
    res, suf = iyelik_A2(kelime)
    return res, suf

def hal_H3(kelime): 
    nitelik = kelimedeki_unlu_niteligi(kelime)
    kalin = nitelik == "kalin"
    suffix = ""
    if kelime.endswith(("sy", "si", "y", "i")): suffix = "na" if kalin else "ne"
    else: suffix = "a" if kalin else "e"
    return kelime + suffix, suffix

def hal_H4(kelime): 
    nitelik = kelimedeki_unlu_niteligi(kelime)
    kalin = nitelik == "kalin"
    suffix = ""
    if son_harf_unlu_mu(kelime): suffix = "ny" if kalin else "ni"
    else: suffix = "y" if kalin else "i"
    return kelime + suffix, suffix

def hal_H5(kelime): 
    nitelik = kelimedeki_unlu_niteligi(kelime)
    kalin = nitelik == "kalin"
    suffix = ""
    if kelime.endswith(("sy", "si", "y", "i")): suffix = "nda" if kalin else "nde"
    else: suffix = "da" if kalin else "de"
    return kelime + suffix, suffix

def hal_H6(kelime): 
    nitelik = kelimedeki_unlu_niteligi(kelime)
    kalin = nitelik == "kalin"
    suffix = ""
    if kelime.endswith(("sy", "si", "y", "i")): suffix = "ndan" if kalin else "nden"
    else: suffix = "dan" if kalin else "den"
    return kelime + suffix, suffix

# Fonksiyon Sözlükleri
sayi_func = {"S2": sayi_S2}
iyelik_func = {"A1": iyelik_A1, "A2": iyelik_A2, "A3": iyelik_A3, "B1": iyelik_B1, "B2": iyelik_B2, "B3": iyelik_A3}
hal_func = {"H1": hal_H1, "H2": hal_H2, "H3": hal_H3, "H4": hal_H4, "H5": hal_H5, "H6": hal_H6}

def analyze(root, s_code, i_code, h_code):
    current_word = root
    parts = [{"text": root, "type": "Kök", "code": "Kök"}]

    # 1. Sayı
    if s_code in sayi_func:
        current_word, suffix = sayi_func[s_code](current_word)
        parts.append({"text": suffix, "type": "Sayı", "code": s_code})
    
    # 2. İyelik
    if i_code in iyelik_func:
        current_word, suffix = iyelik_func[i_code](current_word)
        parts.append({"text": suffix, "type": "Degislilik", "code": i_code})

    # 3. Hal
    if h_code in hal_func:
        if h_code != "H1": 
            current_word, suffix = hal_func[h_code](current_word)
            display_code = h_code.replace('H', 'A') 
            parts.append({"text": suffix, "type": "Hal", "code": display_code})
            
    return parts, current_word

# ==============================================================================
# FİİL ÇEKİMİ FONKSİYONLARI
# ==============================================================================

# Zamirler
fiil_zamirler = {
    "A1": "Men", "A2": "Sen", "A3": "Ol",
    "B1": "Biz", "B2": "Siz", "B3": "Olar"
}

def ek_sec_fiil(kelime, kalin_ek, ince_ek):
    """Ünlü niteliğine göre ek seçer (fiil çekimi için)."""
    nitelik = kelimedeki_unlu_niteligi(kelime)
    return kalin_ek if nitelik == "kalin" else ince_ek

# ------------------------------------------------------------------------------
# I. ZAMAN EKLERİ VE ŞAHIS ÇEKİMLERİ (Öten Zaman)
# ------------------------------------------------------------------------------

def cekim_T1(kok, sahis_kodu, olumsuz=False):
    """Anyk Öten Zaman (-dy, -di / -mady, -medi)"""
    zaman_eki = ek_sec_fiil(kok, "dy", "di")
    if olumsuz:
        zaman_eki = ek_sec_fiil(kok, "mady", "medi")
    govde = kok + zaman_eki
    sahis_ekleri = {"A1": "m", "A2": "ň", "A3": "", "B1": "k", "B2": "ňiz", "B3": "ler"}
    if sahis_kodu == "B3" and not olumsuz:
        return fiil_zamirler.get(sahis_kodu, "") + " " + kok + ek_sec_fiil(kok, "dy", "di") + "ler"
    return fiil_zamirler.get(sahis_kodu, "") + " " + govde + sahis_ekleri.get(sahis_kodu, "")

def cekim_T2(kok, sahis_kodu, olumsuz=False):
    """Daş Öten Zaman (Düzeltilmiş: -ypdy/di + Şahıs Ekleri / -mandy/-mändi + Şahıs Ekleri)"""
    sahis_ekleri = {"A1": "m", "A2": "ň", "A3": "", "B1": "k", "B2": "ňiz", "B3": "ler"} 
    kok_unlu_ile_bitiyor = kok[-1].lower() in "aäeeyiıioöuü"
    if olumsuz:
        olumsuz_eki = ek_sec_fiil(kok, "mandy", "mändi")
        govde = kok + olumsuz_eki 
        if sahis_kodu == "B3":
             return fiil_zamirler.get(sahis_kodu, "") + " " + govde + ek_sec_fiil(kok, "lar", "ler")
        return fiil_zamirler.get(sahis_kodu, "") + " " + govde + sahis_ekleri.get(sahis_kodu, "")
    else:
        # Yuvarlaklık kontrolü (Basitleştirilmiş)
        ilk_unlu_kalin = kelimedeki_unlu_niteligi(kok) == "kalin"
        if ilk_unlu_kalin:
            temel_ek = "yp" if "o" not in kok and "u" not in kok else "up"
        else:
            temel_ek = "ip" if "ö" not in kok and "ü" not in kok else "üp"
        # KRİTİK DÜZELTME: Kök ünlü ile bitiyorsa, temel ekteki ünlü düşer.
        if kok_unlu_ile_bitiyor:
            temel_ek = temel_ek[1] # 'yp' -> 'p', 'up' -> 'p', vb.
        gecmis_eki = ek_sec_fiil(kok, "dy", "di") 
        govde = kok + temel_ek + gecmis_eki 
        if sahis_kodu == "B3":
            return fiil_zamirler.get(sahis_kodu, "") + " " + govde + ek_sec_fiil(kok, "lar", "ler")
        return fiil_zamirler.get(sahis_kodu, "") + " " + govde + sahis_ekleri.get(sahis_kodu, "")

# ------------------------------------------------------------------------------
# II. ZAMAN EKLERİ VE ŞAHIS ÇEKİMLERİ (Häzirki Zaman)
# ------------------------------------------------------------------------------

def cekim_H1(kok, sahis_kodu, olumsuz=False):
    """Umumy Häzirki Zaman (-ýar, -ýär / -maýar, -meýär)"""
    zaman_eki = ek_sec_fiil(kok, "ýar", "ýär")
    if olumsuz:
        zaman_eki = ek_sec_fiil(kok, "maýar", "meýär")
    govde = kok + zaman_eki
    sahis_ekleri = {"A1": "yn", "A2": "syň", "A3": "", "B1": "ys", "B2": "syňyz", "B3": "lar"}
    return fiil_zamirler.get(sahis_kodu, "") + " " + govde + sahis_ekleri.get(sahis_kodu, "")

def cekim_H2(kok, sahis_kodu, olumsuz=False):
    """Anyk Häzirki Zaman (Otyr-, ýatyr-, dur-, ýör-)"""
    if kok not in ["otyr", "ýatyr", "dur", "ýör"]:
        return fiil_zamirler.get(sahis_kodu, "") + " ❗ Bu zaman formy diňe 'otyr', 'ýatyr', 'dur', 'ýör' işlikleri üçin ulanylýar."
    govde = kok
    sahis_ekleri = {"A1": "yn", "A2": "syň", "A3": "", "B1": "ys", "B2": "syňyz", "B3": "lar"}
    return fiil_zamirler.get(sahis_kodu, "") + " " + govde + sahis_ekleri.get(sahis_kodu, "")

# ------------------------------------------------------------------------------
# III. ZAMAN EKLERİ VE ŞAHIS ÇEKİMLERİ (Geljek Zaman)
# ------------------------------------------------------------------------------

def cekim_G1(kok, sahis_kodu, olumsuz=False):
    """Mälim Geljek Zaman (-jak, -jek / + däl) - Şahıs Eki Yok"""
    zaman_eki = ek_sec_fiil(kok, "jak", "jek")
    fiil_formu = kok + zaman_eki
    sonuc = fiil_zamirler.get(sahis_kodu, "Zamir") + " " + fiil_formu
    if olumsuz:
        return sonuc + " däl"
    return sonuc

def cekim_G2(kok, sahis_kodu, olumsuz=False):
    """Nämälim Geljek Zaman / Geniş Zaman (-ar, -er / -maz, -mez)"""
    sahis_ekleri = {"A1": "in", "A2": "siň", "A3": "", "B1": "is", "B2": "siňiz", "B3": "ler"}
    if not olumsuz:
        zaman_eki = ek_sec_fiil(kok, "ar", "er")
        govde = kok + zaman_eki
        ek = sahis_ekleri.get(sahis_kodu, "")
        return fiil_zamirler.get(sahis_kodu, "") + " " + govde + ek
    else:
        zaman_eki = ek_sec_fiil(kok, "maz", "mez")
        govde = kok + zaman_eki
        if sahis_kodu in ["A1", "A2", "B1", "B2"]:
            ek = sahis_ekleri.get(sahis_kodu, "") 
            return fiil_zamirler.get(sahis_kodu, "") + " " + govde + ek
        else:
            if sahis_kodu == "B3":
                 return fiil_zamirler.get(sahis_kodu, "") + " " + govde + ek_sec_fiil(kok, "lar", "ler")
            return fiil_zamirler.get(sahis_kodu, "") + " " + govde

# Fiil çekim fonksiyonları sözlüğü
fiil_cekim_fonksiyonlari = {
    "T1": cekim_T1, "T2": cekim_T2,
    "H1": cekim_H1, "H2": cekim_H2,
    "G1": cekim_G1, "G2": cekim_G2
}

def analyze_verb(root, zaman_kodu, sahis_kodu, olumsuz=False):
    """Fiil çekimi analiz fonksiyonu - ekleri ayrı ayrı hesaplayıp döndürür"""
    if zaman_kodu not in fiil_cekim_fonksiyonlari or sahis_kodu not in fiil_zamirler:
        return None, None
    
    fonk = fiil_cekim_fonksiyonlari[zaman_kodu]
    sonuc = fonk(root, sahis_kodu, olumsuz)
    
    # Hata kontrolü (sonuçta ❗ varsa hata var demektir)
    if "❗" in sonuc:
        return [{"text": sonuc.split(" ", 1)[1] if " " in sonuc else sonuc, "type": "Hata", "code": "HATA"}], ""
    
    # Parts oluştur - sıralama: Şahıs -> Kök -> Zaman -> Olumsuzluk
    parts = []
    
    # Şahıs bilgisini en başa ekle
    parts.append({"text": fiil_zamirler.get(sahis_kodu, ""), "type": "Şahıs", "code": sahis_kodu})
    
    # Kök
    parts.append({"text": root, "type": "Kök", "code": "Kök"})
    
    # Zaman ekini hesapla
    zaman_eki = ""
    if zaman_kodu == "T1":
        zaman_eki = ek_sec_fiil(root, "mady", "medi") if olumsuz else ek_sec_fiil(root, "dy", "di")
    elif zaman_kodu == "T2":
        if olumsuz:
            zaman_eki = ek_sec_fiil(root, "mandy", "mändi")
        else:
            kok_unlu_ile_bitiyor = root[-1].lower() in "aäeeyiıioöuü"
            ilk_unlu_kalin = kelimedeki_unlu_niteligi(root) == "kalin"
            if ilk_unlu_kalin:
                temel_ek = "yp" if "o" not in root and "u" not in root else "up"
            else:
                temel_ek = "ip" if "ö" not in root and "ü" not in root else "üp"
            if kok_unlu_ile_bitiyor:
                temel_ek = temel_ek[1]  # 'yp' -> 'p', 'up' -> 'p', vb.
            gecmis_eki = ek_sec_fiil(root, "dy", "di")
            zaman_eki = temel_ek + gecmis_eki
    elif zaman_kodu == "H1":
        zaman_eki = ek_sec_fiil(root, "maýar", "meýär") if olumsuz else ek_sec_fiil(root, "ýar", "ýär")
    elif zaman_kodu == "H2":
        zaman_eki = ""  # H2 için zaman eki yok, kök aynen kalıyor
    elif zaman_kodu == "G1":
        zaman_eki = ek_sec_fiil(root, "jak", "jek")
    elif zaman_kodu == "G2":
        zaman_eki = ek_sec_fiil(root, "maz", "mez") if olumsuz else ek_sec_fiil(root, "ar", "er")
    
    if zaman_eki:
        parts.append({"text": zaman_eki, "type": "Zaman", "code": zaman_kodu})
    
    # Şahıs ekini hesapla
    sahis_eki = ""
    if zaman_kodu == "G1":
        sahis_eki = ""  # G1'de şahıs eki yok
    elif zaman_kodu in ["T1", "T2"]:
        sahis_ekleri = {"A1": "m", "A2": "ň", "A3": "", "B1": "k", "B2": "ňiz", "B3": "ler"}
        if sahis_kodu == "B3" and zaman_kodu == "T1" and not olumsuz:
            sahis_eki = ek_sec_fiil(root, "lar", "ler")
        else:
            sahis_eki = sahis_ekleri.get(sahis_kodu, "")
    elif zaman_kodu in ["H1", "H2"]:
        sahis_ekleri = {"A1": "yn", "A2": "syň", "A3": "", "B1": "ys", "B2": "syňyz", "B3": "lar"}
        sahis_eki = sahis_ekleri.get(sahis_kodu, "")
    elif zaman_kodu == "G2":
        sahis_ekleri = {"A1": "in", "A2": "siň", "A3": "", "B1": "is", "B2": "siňiz", "B3": "ler"}
        if olumsuz and sahis_kodu == "B3":
            sahis_eki = ek_sec_fiil(root, "lar", "ler")
        elif olumsuz and sahis_kodu == "A3":
            sahis_eki = ""
        else:
            sahis_eki = sahis_ekleri.get(sahis_kodu, "")
    
    if sahis_eki:
        parts.append({"text": sahis_eki, "type": "Şahıs Eki", "code": sahis_kodu})
    
    # Olumsuzluk (sadece G1'de "däl" olarak eklenir)
    if olumsuz and zaman_kodu == "G1":
        parts.append({"text": "däl", "type": "Olumsuzluk", "code": "Olumsuz"})
    elif olumsuz and zaman_kodu != "G1":
        # Diğer zamanlarda olumsuzluk zaman eki içinde
        pass
    
    return parts, sonuc