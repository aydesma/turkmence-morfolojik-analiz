# -*- coding: utf-8 -*-
"""
TÜRKMEN MORFOLOJİK MOTORU v26.0 — Referans Program (test amaçlı)
Kullanıcının sağladığı orijinal Python programı.
"""
import sys
import json

# --- VERİ SETLERİ ---
yogyn = set("aouy")
ince = set("eäöiü")
unluler = yogyn | ince

istisnalar = {"asyl": "asl", "pasyl": "pasl", "nesil": "nesl", "ylym": "ylm", "mähir": "mähr"}
dusme_adaylari = {"burun", "alyn", "agyz", "gobek", "ogul", "erin", "bagyr", "sabyr", "kömür", "sygyr", "deňiz", "goýun", "boýun", "howuz", "tomus", "tizir", "köwüş", "orun", "garyn", "gelin"}

def unlu_niteligi(kelime):
    for h in reversed(kelime.lower()):
        if h in yogyn: return "yogyn"
        if h in ince: return "ince"
    return "yogyn"

def yuvarlak_mi(kelime):
    return any(h in "oöuü" for h in kelime.lower())

def tam_yumusama(kok):
    degisim = {'p': 'b', 'ç': 'j', 't': 'd', 'k': 'g'}
    if kok and kok[-1] in degisim: return kok[:-1] + degisim[kok[-1]]
    return kok

def dusme_uygula(kok, ek):
    k = kok.lower()
    if not ek or ek[0] not in unluler: return k
    if k in istisnalar: return istisnalar[k]
    if k in dusme_adaylari: return k[:-2] + k[-1]
    return k

# --- ANA MOTOR ---
def isim_cekimle(kok, cokluk=False, iyelik=None, i_tip="tek", hal=None):
    res = kok.lower()
    yol = [kok]
    nit_ilk = unlu_niteligi(res)
    kok_yuvarlak = yuvarlak_mi(res)

    # 1. SAN (Sayı)
    if cokluk:
        if kok_yuvarlak and res[-1] in "yi":
            res = res[:-1] + ("u" if nit_ilk == "yogyn" else "ü")
        ek = "lar" if unlu_niteligi(res) == "yogyn" else "ler"
        res += ek; yol.append(ek)

    # 2. DEGİŞLİLİK (İyelik)
    if iyelik:
        nit = unlu_niteligi(res); is_unlu = res[-1] in unluler; kok_yuvarlak = yuvarlak_mi(res)
        
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
            if kok_yuvarlak and res[-1] in "yi": res = res[:-1] + ("u" if nit=="yogyn" else "ü")
            ek = ("sy" if nit == "yogyn" else "si") if is_unlu else (("y" if nit=="yogyn" else "i"))
        
        res = dusme_uygula(res, ek); res = tam_yumusama(res); res += ek; yol.append(ek)

    # 3. DÜŞÜM (Hal)
    if hal:
        nit = unlu_niteligi(res); is_unlu = res[-1] in unluler; kok_yuvarlak = yuvarlak_mi(res)
        
        n_kay = iyelik == "A3"
        
        # Orta Hece Yuvarlaklaşma (Ogluny, Burnuny)
        if n_kay and kok_yuvarlak and res[-1] in "yi":
            res = res[:-1] + ("u" if nit == "yogyn" else "ü")

        if hal == "A2": # İlgi
            if n_kay: ek = "nyň"
            elif is_unlu: ek = "nyň" if nit=="yogyn" else "niň"
            else:
                if len(kok) <= 4 and kok_yuvarlak: ek = "uň" if nit=="yogyn" else "üň"
                else: ek = "yň" if nit=="yogyn" else "iň"
                res = dusme_uygula(res, ek); res = tam_yumusama(res)

        elif hal == "A3": # Yönelme
            if n_kay: ek = "na" if nit=="yogyn" else "ne"
            elif is_unlu:
                son = res[-1]; res = res[:-1]; res += "a" if son in "ay" else "ä"; ek = ""
            else: ek = "a" if nit=="yogyn" else "e"

        elif hal == "A4": # Belirtme
            if n_kay: ek = "ny" if nit=="yogyn" else "ni"
            elif is_unlu: ek = "ny" if nit=="yogyn" else "ni"
            else: ek = "y" if nit=="yogyn" else "i"; res = tam_yumusama(res)

        elif hal == "A5": ek = "nda" if n_kay else ("da" if nit=="yogyn" else "de")
        elif hal == "A6": ek = "ndan" if n_kay else ("dan" if nit=="yogyn" else "den")
        
        res += ek; yol.append(ek)
        
    return res.upper(), " + ".join(yol)


# ============================================================
# TEST ÜRETECİ — Kapsamlı test sonuçları üretir
# ============================================================
def generate_tests():
    """Tüm kombinasyonlar için test sonuçları üretir."""
    
    # Çeşitli test kelimeler
    test_kelimeleri = [
        # Temel kelimeler
        "kitap", "adam", "iş", "göz", "gyz", "süt", "el", "ýol",
        # Ünlüyle biten
        "alma", "eşe", "oba", "süri", "guzy",
        # Düşme adayları
        "burun", "alyn", "agyz", "gobek", "ogul", "erin", "bagyr", "sabyr",
        "kömür", "sygyr", "deňiz", "goýun", "boýun", "howuz", "tomus",
        "tizir", "köwüş", "orun", "garyn", "gelin",
        # İstisnalar
        "asyl", "pasyl", "nesil", "ylym", "mähir",
        # Yuvarlak ünlülü
        "okuw", "öý", "köl", "gol", "otly",
        # Kısa kelimeler
        "at", "ot", "it", "et", "ok",
        # Uzun kelimeler
        "mugallym", "mekdep", "hassahana", "awtobus",
        # Yumuşama adayları
        "kitap", "agaç", "mekdep", "toprak",
        # Yuvarlak + yi sonu
        "guýy",
    ]
    
    # Tekil/Çoğul kişi tipleri
    iyelik_kodlari = [None, "A1", "A2", "A3"]
    i_tipleri = ["tek", "cog"]
    hal_kodlari = [None, "A2", "A3", "A4", "A5", "A6"]
    cokluk_secenekleri = [False, True]

    results = []
    
    for kelime in test_kelimeleri:
        for cokluk in cokluk_secenekleri:
            for iyelik in iyelik_kodlari:
                for i_tip in i_tipleri:
                    # i_tip sadece iyelik varken anlamlı, None ise sadece "tek" yap
                    if not iyelik and i_tip == "cog":
                        continue
                    for hal in hal_kodlari:
                        try:
                            sonuc, secere = isim_cekimle(kelime, cokluk, iyelik, i_tip, hal)
                            results.append({
                                "kelime": kelime,
                                "cokluk": cokluk,
                                "iyelik": iyelik,
                                "i_tip": i_tip,
                                "hal": hal,
                                "sonuc": sonuc,
                                "secere": secere
                            })
                        except Exception as e:
                            results.append({
                                "kelime": kelime,
                                "cokluk": cokluk,
                                "iyelik": iyelik,
                                "i_tip": i_tip,
                                "hal": hal,
                                "sonuc": f"HATA: {str(e)}",
                                "secere": ""
                            })
    
    return results


if __name__ == "__main__":
    results = generate_tests()
    with open("v26_test_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"Toplam {len(results)} test sonucu üretildi → v26_test_results.json")
