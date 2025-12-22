# Temel Tanımlar
unluler = set("aeäuüyiöo")
kalin_unluler = set("aouy")
ince_unluler = set("eäiüö")
duz_unluler = set("aäeyi")
yuvarlak_unluler = set("oöuü")

# Ünlü düşmesine meyilli kelimeler
dusmeye_meyilli = {"burun", "alın", "agyz", "göbek", "ogul", "erin"}

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

def kural_hece_dusmesi(kok):
    """Ünlü düşmesi kuralı: burun → burnum (u düşer)"""
    if kok.lower() in dusmeye_meyilli:
        # Son ünlüyü bul ve düşür
        return kok[:-2] + kok[-1]  # sondan ikinci harfi (ünlüyü) at
    return kok

# --- EKLER ---
# Sayı (San)
def sayi_S2(kelime):
    nitelik = kelimedeki_unlu_niteligi(kelime)
    suffix = "lar" if nitelik == "kalin" else "ler"
    return kelime + suffix, suffix

# İyelik (Degislilik)
def iyelik_A1(kelime): 
    if son_harf_unlu_mu(kelime): return kelime + "m", "m"
    # Ünlü düşmesi uygula
    kelime_islem = kural_hece_dusmesi(kelime)
    nitelik = kelimedeki_unlu_niteligi_tam(kelime_islem)
    map_ek = {"kalin-duz": "ym", "kalin-yuvarlak": "um", "ince-duz": "im", "ince-yuvarlak": "üm"}
    suffix = map_ek.get(nitelik, "im")
    return kelime_islem + suffix, suffix

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
    if son_harf_unlu_mu(kelime):
        nitelik_tam = kelimedeki_unlu_niteligi_tam(kelime)
        kalin = nitelik_tam.startswith("kalin")
        suffix = "myz" if kalin else "miz"
        return kelime + suffix, suffix
    else:
        # Ünlü düşmesi uygula
        kelime_islem = kural_hece_dusmesi(kelime)
        nitelik_tam = kelimedeki_unlu_niteligi_tam(kelime_islem)
        kalin = nitelik_tam.startswith("kalin")
        map_ek = {"kalin-duz": "ymyz", "kalin-yuvarlak": "umyz", "ince-duz": "imiz", "ince-yuvarlak": "ümiz"}
        suffix = map_ek.get(nitelik_tam, "imiz")
        return kelime_islem + suffix, suffix

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

# Sessiz ünsüzler
voiceless_consonants = set("fstkçşhp")

def ek_sec_fiil(kelime, kalin_ek, ince_ek):
    """Ünlü niteliğine göre ek seçer (fiil çekimi için)."""
    nitelik = kelimedeki_unlu_niteligi(kelime)
    return kalin_ek if nitelik == "kalin" else ince_ek

def unsus_yumusamasi_T2(kok):
    """T2 için ünsüz yumuşaması"""
    if not kok: return kok
    son_harf = kok[-1].lower()
    govde = kok[:-1]
    if son_harf == 'p': return govde + 'b' 
    elif son_harf == 't': return govde + 'd' 
    elif son_harf == 'ç': return govde + 'c'
    elif son_harf == 'k': return govde + 'g' 
    return kok

def get_T1_suffix(kok, olumsuz):
    """T1 için zaman eki hesaplama (sessiz ünsüz kontrolü ile)"""
    nitelik = kelimedeki_unlu_niteligi(kok)
    is_voiceless = kok[-1].lower() in voiceless_consonants
    kalin = "kalin" if nitelik == "kalin" else "ince"
    
    if olumsuz:
        return "mady" if kalin == "kalin" else "medi"
    else: 
        if is_voiceless:
            return "ty" if kalin == "kalin" else "ti"
        else:
            return "dy" if kalin == "kalin" else "di"

# ------------------------------------------------------------------------------
# I. ZAMAN EKLERİ VE ŞAHIS ÇEKİMLERİ (Öten Zaman)
# ------------------------------------------------------------------------------

def cekim_T1(kok, sahis_kodu, olumsuz=False):
    """Anyk Öten Zaman (-dy, -di, -ty, -ti / -mady, -medi)"""
    zaman_eki_govde = get_T1_suffix(kok, olumsuz)
    govde = kok + zaman_eki_govde
    sahis_ekleri = {"A1": "m", "A2": "ň", "A3": "", "B1": "k", "B2": "ňiz"} 
    
    if sahis_kodu == "B3":
        plural_suffix = ek_sec_fiil(kok, "lar", "ler")
        return fiil_zamirler.get(sahis_kodu, "") + " " + govde + plural_suffix
    
    return fiil_zamirler.get(sahis_kodu, "") + " " + govde + sahis_ekleri.get(sahis_kodu, "")

def cekim_T2(kok, sahis_kodu, olumsuz=False):
    """Daş Öten Zaman (ünsüz yumuşaması ile)"""
    sahis_ekleri_kalin = {"A1": "m", "A2": "ň", "A3": "", "B1": "k", "B2": "ňyz", "B3": "lar"}
    sahis_ekleri_ince = {"A1": "m", "A2": "ň", "A3": "", "B1": "k", "B2": "ňiz", "B3": "ler"} 
    kalin = kelimedeki_unlu_niteligi(kok) == "kalin"
    sahis_ekleri = sahis_ekleri_kalin if kalin else sahis_ekleri_ince
    kok_unlu_ile_bitiyor = kok[-1].lower() in "aäeeyiıioöuü"
    
    if olumsuz:
        olumsuz_eki = ek_sec_fiil(kok, "mandy", "mändi")
        govde = kok + olumsuz_eki 
        if sahis_kodu == "B3": 
            return fiil_zamirler.get(sahis_kodu, "") + " " + govde + ek_sec_fiil(kok, "lar", "ler")
        return fiil_zamirler.get(sahis_kodu, "") + " " + govde + sahis_ekleri.get(sahis_kodu, "")
    else:
        kok_islem = unsus_yumusamasi_T2(kok)
        ilk_unlu_kalin = kelimedeki_unlu_niteligi(kok_islem) == "kalin"
        
        if ilk_unlu_kalin:
            temel_ek = "yp" if "o" not in kok_islem and "u" not in kok_islem else "up"
        else:
            temel_ek = "ip" if "ö" not in kok_islem and "ü" not in kok_islem else "üp"
            
        if kok_unlu_ile_bitiyor: 
            temel_ek = temel_ek[1] 
        gecmis_eki = ek_sec_fiil(kok, "ty", "ti") 
        govde = kok_islem + temel_ek + gecmis_eki 
        
        if sahis_kodu == "B3": 
            return fiil_zamirler.get(sahis_kodu, "") + " " + govde + ek_sec_fiil(kok, "lar", "ler")
        return fiil_zamirler.get(sahis_kodu, "") + " " + govde + sahis_ekleri.get(sahis_kodu, "")

def cekim_T3(kok, sahis_kodu, olumsuz=False):
    """Dowamly Öten Zaman (ýardy/di, ardy/di / maýardy/di, mezdi/mazdy)"""
    kalin = kelimedeki_unlu_niteligi(kok) == "kalin"
    
    # 1. Ana Zaman Gövdesi (Häzirki/Geniş Zaman Formu)
    if not olumsuz:
        zaman_formu = ek_sec_fiil(kok, "ýar", "ýär")
    else:
        zaman_formu = ek_sec_fiil(kok, "maýar", "meýär")
    
    # 2. Öten Zaman Eki (dy/di)
    gecmis_eki = "dy" if kalin else "di"
    
    govde = kok + zaman_formu + gecmis_eki
    sahis_ekleri = {"A1": "m", "A2": "ň", "A3": "", "B1": "k", "B2": "ňiz"} 
    
    if sahis_kodu == "B3":
        plural_suffix = ek_sec_fiil(kok, "lar", "ler")
        return fiil_zamirler.get(sahis_kodu, "") + " " + govde + plural_suffix
    
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
    kalin = kelimedeki_unlu_niteligi(kok) == "kalin"
    
    if kalin: 
        sahis_ekleri = {"A1": "yn", "A2": "syň", "A3": "", "B1": "ys", "B2": "syňyz", "B3": "lar"}
    else: 
        sahis_ekleri = {"A1": "in", "A2": "siň", "A3": "", "B1": "is", "B2": "siňiz", "B3": "ler"}
    
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
    kalin = kelimedeki_unlu_niteligi(kok) == "kalin"
    if kalin: 
        sahis_ekleri = {"A1": "yn", "A2": "syň", "A3": "", "B1": "ys", "B2": "syňyz", "B3": "lar"}
    else: 
        sahis_ekleri = {"A1": "in", "A2": "siň", "A3": "", "B1": "is", "B2": "siňiz", "B3": "ler"}
    
    if not olumsuz:
        zaman_eki = ek_sec_fiil(kok, "ar", "er")
        govde = kok + zaman_eki
        ek = sahis_ekleri.get(sahis_kodu, "")
        return fiil_zamirler.get(sahis_kodu, "") + " " + govde + ek
    else:
        zaman_eki = ek_sec_fiil(kok, "maz", "mez")
        govde = kok + zaman_eki
        if sahis_kodu in sahis_ekleri:
            ek = sahis_ekleri.get(sahis_kodu, "") 
            return fiil_zamirler.get(sahis_kodu, "") + " " + govde + ek
        else:
            if sahis_kodu == "B3": 
                return fiil_zamirler.get(sahis_kodu, "") + " " + govde + ek_sec_fiil(kok, "lar", "ler")
            return fiil_zamirler.get(sahis_kodu, "") + " " + govde

# Fiil çekim fonksiyonları sözlüğü (Öten zaman: Ö1, Ö2, Ö3)
fiil_cekim_fonksiyonlari = {
    "Ö1": cekim_T1, "Ö2": cekim_T2, "Ö3": cekim_T3,
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
    
    # Olumsuzluk eki (me/ma) - Ö1 için ayrı göster
    olumsuzluk_eki = ""
    if olumsuz and zaman_kodu == "Ö1":
        kalin = kelimedeki_unlu_niteligi(root) == "kalin"
        olumsuzluk_eki = "ma" if kalin else "me"
        parts.append({"text": olumsuzluk_eki, "type": "Olumsuzluk Eki", "code": "Olumsuz"})
    
    # Zaman ekini hesapla
    zaman_eki = ""
    if zaman_kodu == "Ö1":
        # Olumsuzluk ekini çıkardık, sadece di/dy/ti/ty kalsın
        kalin = kelimedeki_unlu_niteligi(root) == "kalin"
        is_voiceless = root[-1].lower() in voiceless_consonants
        if olumsuz:
            # "medi" yerine sadece "di" - çünkü "me" ayrı eklendi
            zaman_eki = "dy" if kalin else "di"
        else:
            if is_voiceless:
                zaman_eki = "ty" if kalin else "ti"
            else:
                zaman_eki = "dy" if kalin else "di"
    elif zaman_kodu == "Ö2":
        if olumsuz:
            zaman_eki = ek_sec_fiil(root, "mandy", "mändi")
        else:
            kok_unlu_ile_bitiyor = root[-1].lower() in "aäeeyiıioöuü"
            kok_islem = unsus_yumusamasi_T2(root)
            ilk_unlu_kalin = kelimedeki_unlu_niteligi(kok_islem) == "kalin"
            if ilk_unlu_kalin:
                temel_ek = "yp" if "o" not in kok_islem and "u" not in kok_islem else "up"
            else:
                temel_ek = "ip" if "ö" not in kok_islem and "ü" not in kok_islem else "üp"
            if kok_unlu_ile_bitiyor:
                temel_ek = temel_ek[1]
            gecmis_eki = ek_sec_fiil(root, "ty", "ti")
            zaman_eki = temel_ek + gecmis_eki
    elif zaman_kodu == "Ö3":
        kalin = kelimedeki_unlu_niteligi(root) == "kalin"
        if not olumsuz:
            zaman_formu = ek_sec_fiil(root, "ýar", "ýär")
        else:
            zaman_formu = ek_sec_fiil(root, "maýar", "meýär")
        gecmis_eki = "dy" if kalin else "di"
        zaman_eki = zaman_formu + gecmis_eki
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
    elif zaman_kodu in ["Ö1", "Ö2", "Ö3"]:
        kalin = kelimedeki_unlu_niteligi(root) == "kalin"
        if kalin:
            sahis_ekleri = {"A1": "m", "A2": "ň", "A3": "", "B1": "k", "B2": "ňyz"}
        else:
            sahis_ekleri = {"A1": "m", "A2": "ň", "A3": "", "B1": "k", "B2": "ňiz"}
        if sahis_kodu == "B3":
            sahis_eki = ek_sec_fiil(root, "lar", "ler")
        else:
            sahis_eki = sahis_ekleri.get(sahis_kodu, "")
    elif zaman_kodu == "H1":
        kalin = kelimedeki_unlu_niteligi(root) == "kalin"
        if kalin:
            sahis_ekleri = {"A1": "yn", "A2": "syň", "A3": "", "B1": "ys", "B2": "syňyz", "B3": "lar"}
        else:
            sahis_ekleri = {"A1": "in", "A2": "siň", "A3": "", "B1": "is", "B2": "siňiz", "B3": "ler"}
        sahis_eki = sahis_ekleri.get(sahis_kodu, "")
    elif zaman_kodu == "H2":
        sahis_ekleri = {"A1": "yn", "A2": "syň", "A3": "", "B1": "ys", "B2": "syňyz", "B3": "lar"}
        sahis_eki = sahis_ekleri.get(sahis_kodu, "")
    elif zaman_kodu == "G2":
        kalin = kelimedeki_unlu_niteligi(root) == "kalin"
        if kalin:
            sahis_ekleri = {"A1": "yn", "A2": "syň", "A3": "", "B1": "ys", "B2": "syňyz", "B3": "lar"}
        else:
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