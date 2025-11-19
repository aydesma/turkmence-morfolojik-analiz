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
    # İlk versiyondaki mantık (Kullanıcı isteği üzerine korundu)
    for h in kelime.lower():
        if h in kalin_unluler: return "kalin"
        elif h in ince_unluler: return "ince"
    return "ince"

def kelimedeki_unlu_niteligi_tam(kelime):
    # İlk versiyondaki mantık (Kullanıcı isteği üzerine korundu)
    for h in kelime.lower():
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
        if h_code != "H1": # H1 boş ektir
            current_word, suffix = hal_func[h_code](current_word)
            # Ekranda 'H' yerine 'A' görünsün diye kodu değiştiriyoruz: H3 -> A3
            display_code = h_code.replace('H', 'A') 
            parts.append({"text": suffix, "type": "Hal", "code": display_code})
            
    return parts, current_word
