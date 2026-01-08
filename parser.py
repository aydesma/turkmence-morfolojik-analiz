# -*- coding: utf-8 -*-
"""
Türkmence Morfolojik Parser Modülü
Kalıp tabanlı kök tanıma ve ek ayırma işlemleri (Sözlüksüz)
"""

# ===== TEMEL TANIMLAR =====
unluler = set("aeäuüyiöo")
kalin_unluler = set("aouy")
ince_unluler = set("eäiüö")

# Ünlü düşmesine meyilli kelimeler
dusme_sozlugu = {
    "burun": "burn", "alyn": "aln", "agyz": "agz", 
    "göbek": "göbk", "ogul": "ogl", "erin": "ern",
    "kömür": "kömr", "bagyr": "bagr", "sabyr": "sabr"
}

# Tersine çevrilmiş düşme sözlüğü (düşmüş -> orijinal)
dusme_ters = {v: k for k, v in dusme_sozlugu.items()}

# ===== EK SÖZLÜĞÜ (Hiyerarşik - Uzundan Kısaya Sıralı) =====

EK_SOZLUGU = {
    "HAL": {
        "A6": ["ndan", "nden", "dan", "den"],  # Çıkma hali
        "A5": ["nda", "nde", "da", "de"],      # Bulunma hali
        "A4": ["ny", "ni", "y", "i"],          # Belirtme hali
        "A3": ["na", "ne", "a", "e"],          # Yönelme hali
        "A2": ["nyň", "niň", "nuň", "nüň", "yň", "iň", "uň", "üň", "ň"]  # İlgi hali
    },
    "IYELIK": {
        "B2": ["yňyz", "iňiz", "uňyz", "üňiz", "ňyz", "ňiz"],  # 2. çoğul
        "B1": ["ymyz", "imiz", "umyz", "ümiz", "myz", "miz"],  # 1. çoğul  
        "A2": ["yň", "iň", "uň", "üň", "ň"],                   # 2. tekil
        "A1": ["ym", "im", "um", "üm", "m"],                   # 1. tekil
        "A3": ["sy", "si", "y", "i"]                           # 3. tekil
    },
    "COKL": {
        "S2": ["lar", "ler"]  # Çoğul
    }
}

# ===== YARDIMCI FONKSİYONLAR =====

def unlu_niteligi(kelime):
    """Kelimenin son ünlüsüne göre kalın/ince niteliği döndürür"""
    for h in reversed(kelime.lower()):
        if h in kalin_unluler:
            return "kalin"
        if h in ince_unluler:
            return "ince"
    return "ince"

def yumusamayi_geri_al(govde):
    """Ünsüz yumuşamasını geri alır (b->p, d->t, vb.)"""
    degisim = {'b': 'p', 'd': 't', 'c': 'ç', 'g': 'k'}
    if govde and govde[-1] in degisim:
        return govde[:-1] + degisim[govde[-1]]
    return govde

def dusmeyi_geri_al(govde):
    """Ünlü düşmesini geri alır (burn->burun)"""
    govde_lower = govde.lower()
    if govde_lower in dusme_ters:
        return dusme_ters[govde_lower]
    return govde

# ===== ANA PARSE FONKSİYONU =====

def parse_isim(kelime):
    """
    İsim kelimesini kök ve eklerine ayırır (kalıp tabanlı).
    
    Döndürür:
    {
        "basarili": True/False,
        "orijinal": "orijinal kelime",
        "kok": "bulunan kök",
        "ekler": [{"ek": "lar", "tip": "Çoğul", "kod": "S2"}, ...],
        "analiz": "baş + lar + ymyz + dan"
    }
    """
    orijinal = kelime
    kelime = kelime.lower().strip()
    
    # Sonuç yapısı
    sonuc = {
        "basarili": False,
        "orijinal": orijinal,
        "kok": "",
        "ekler": [],
        "analiz": ""
    }
    
    # Boş kelime kontrolü
    if not kelime:
        return sonuc
    
    temp = kelime
    ekler = []
    
    # 1. KATMAN: HAL EKLERİ
    for kod, ek_listesi in EK_SOZLUGU["HAL"].items():
        for ek in ek_listesi:
            if temp.endswith(ek) and len(temp) > len(ek) + 1:
                ekler.insert(0, {"ek": ek, "tip": "Düşüm", "kod": kod})
                temp = temp[:-len(ek)]
                # Ses değişimi geri al
                if ek[0] in unluler or ek.startswith("n"):
                    temp = yumusamayi_geri_al(temp)
                    temp = dusmeyi_geri_al(temp)
                break
        else:
            continue
        break
    
    # 2. KATMAN: İYELİK EKLERİ
    for kod, ek_listesi in EK_SOZLUGU["IYELIK"].items():
        for ek in ek_listesi:
            if temp.endswith(ek) and len(temp) > len(ek) + 1:
                ekler.insert(0, {"ek": ek, "tip": "Degişlilik", "kod": kod})
                temp = temp[:-len(ek)]
                if ek[0] in unluler:
                    temp = yumusamayi_geri_al(temp)
                    temp = dusmeyi_geri_al(temp)
                break
        else:
            continue
        break
    
    # 3. KATMAN: ÇOKLUK EKLERİ
    for kod, ek_listesi in EK_SOZLUGU["COKL"].items():
        for ek in ek_listesi:
            if temp.endswith(ek) and len(temp) > len(ek):
                ekler.insert(0, {"ek": ek, "tip": "San", "kod": kod})
                temp = temp[:-len(ek)]
                break
        else:
            continue
        break
    
    # Sonuç oluştur
    sonuc["basarili"] = True
    sonuc["kok"] = temp.capitalize()
    sonuc["ekler"] = ekler
    
    # Analiz string'i oluştur
    analiz_parts = [f"{temp.capitalize()} (Kök)"]
    for e in ekler:
        analiz_parts.append(f"{e['ek']} ({e['kod']})")
    sonuc["analiz"] = " + ".join(analiz_parts)
    
    return sonuc


def parse_isim_multi(kelime):
    """
    İsim kelimesini ÇOKLU SONUÇ döndürerek parse eder.
    Belirsiz durumlarda birden fazla olası parse sonucu döndürür.
    """
    orijinal = kelime
    kelime_lower = kelime.lower().strip()
    
    sonuclar = []
    visited = set()
    
    def parse_yol(temp, ekler, ziyaret_id):
        """Tek bir parse yolunu takip et"""
        if ziyaret_id in visited:
            return
        visited.add(ziyaret_id)
        
        if len(temp) < 2:
            return
        
        # Her ek türünü dene
        tum_ekler = [
            ("HAL", EK_SOZLUGU["HAL"]),
            ("IYELIK", EK_SOZLUGU["IYELIK"]),
            ("COKL", EK_SOZLUGU["COKL"])
        ]
        
        for kategori, ek_dict in tum_ekler:
            for kod, ek_listesi in ek_dict.items():
                for ek in ek_listesi:
                    if temp.endswith(ek) and len(temp) > len(ek) + 1:
                        kalan = temp[:-len(ek)]
                        tip = {"HAL": "Düşüm", "IYELIK": "Degişlilik", "COKL": "San"}[kategori]
                        yeni_ekler = [{"ek": ek, "tip": tip, "kod": kod}] + list(ekler)
                        ziyaret_key = f"{kalan}|{kod}"
                        parse_yol(kalan, yeni_ekler, ziyaret_key)
        
        # Bu nokta bir kök olabilir
        if ekler:
            analiz_parts = [f"{temp.capitalize()} (Kök)"]
            for e in ekler:
                analiz_parts.append(f"{e['ek']} ({e['kod']})")
            sonuclar.append({
                "kok": temp.capitalize(),
                "ekler": list(ekler),
                "analiz": " + ".join(analiz_parts)
            })
    
    # Parse başlat
    parse_yol(kelime_lower, [], kelime_lower)
    
    # Tekrarlananları kaldır
    unique = []
    seen = set()
    for s in sonuclar:
        if s["analiz"] not in seen:
            seen.add(s["analiz"])
            unique.append(s)
    
    if unique:
        return {
            "basarili": True,
            "orijinal": orijinal,
            "coklu": len(unique) > 1,
            "sonuclar": unique
        }
    else:
        return parse_isim(kelime)


# ===== FİİL EK SÖZLÜĞÜ =====

FIIL_EK_SOZLUGU = {
    # ŞAHIS EKLERİ (Fiil sonunda)
    "SAHIS": {
        "B3": ["lar", "ler"],
        "B2": ["syňyz", "siňiz", "ňyz", "ňiz"],
        "B1": ["ys", "is", "s", "k"],
        "A2": ["syň", "siň", "ň"],
        "A1": ["yn", "in", "n", "m"],
        "A3": []
    },
    
    # ZAMAN EKLERİ (Olumlu)
    "ZAMAN_OLUMLU": {
        "Ö1": ["dyňyz", "diňiz", "tyňyz", "tiňiz",
               "dym", "dim", "tym", "tim",
               "dyň", "diň", "tyň", "tiň", 
               "dyk", "dik", "tyk", "tik",
               "dylar", "diler", "tylar", "tiler",
               "dy", "di", "ty", "ti"],
        "Ö2": ["ypdylar", "ipdiler", "updylar", "üpdiler",
               "yptymlar", "iptimler", "uptumlar", "üptümler",
               "ypdym", "ipdim", "updym", "üpdim",
               "yptym", "iptim", "uptum", "üptüm",
               "ypdyň", "ipdiň", "updyň", "üpdiň",
               "yptyň", "iptiň", "uptuň", "üptüň",
               "ypdyk", "ipdik", "updyk", "üpdik",
               "yptyk", "iptik", "uptuk", "üptük",
               "ypdyňyz", "ipdiňiz", "updyňyz", "üpdiňiz",
               "yptyňyz", "iptiňiz", "uptuňyz", "üptüňiz",
               "ypty", "ipti", "upty", "üpti",
               "ypdy", "ipdi", "updy", "üpdi"],
        "Ö3": ["ýardylar", "ýärdiler",
               "ýardym", "ýärdim", "ýardyň", "ýärdiň",
               "ýardyk", "ýärdik", "ýardyňyz", "ýärdiňiz",
               "ýardy", "ýärdi"],
        "H1": ["ýaryn", "ýärin", "ýarsyň", "ýärsiň",
               "ýarys", "ýäris", "ýarsyňyz", "ýärsiňiz",
               "ýarlar", "ýärler", "ýar", "ýär"],
        "H2": ["ýandyryn", "ýändirim", "ýandyrsyň", "ýändirsiň",
               "ýandyr", "ýändir"],
        "G1": ["jaklar", "jekler", "jak", "jek"],
        "G2": ["aryn", "erin", "arsyň", "ersiň",
               "arys", "eris", "arsyňyz", "ersiňiz",
               "arlar", "erler", "ar", "er"]
    },
    
    # ZAMAN EKLERİ (Olumsuz)
    "ZAMAN_OLUMSUZ": {
        "Ö1": ["madylar", "mediler", "mady", "medi",
               "madym", "medim", "madyň", "mediň",
               "madyk", "medik", "madyňyz", "mediňiz"],
        "Ö2": ["mandylar", "mändiler", "mandy", "mändi",
               "mandym", "mändim", "mandyň", "mändiň",
               "mandyk", "mändik", "mandyňyz", "mändiňiz"],
        "Ö3": ["maýardylar", "meýärdiler", "maýardy", "meýärdi"],
        "H1": ["maýarlar", "meýärler", "maýar", "meýär"],
        "H2": ["maýandyr", "meýändir"],
        "G1": ["majak", "mejek"],
        "G2": ["mazlar", "mezler", "maz", "mez",
               "mazyn", "mezin", "mazsyň", "mezsiň",
               "mazys", "mezis", "mazsyňyz", "mezsiňiz"]
    }
}


def parse_fiil(kelime):
    """
    Çekimli fiili kök ve eklerine ayırır (kalıp tabanlı).
    
    Döndürür:
    {
        "basarili": True/False,
        "orijinal": "orijinal kelime",
        "kok": "bulunan kök",
        "ekler": [{"ek": "dy", "tip": "Zaman", "kod": "Ö1"}, ...],
        "analiz": "gel + dy + m",
        "tur": "fiil"
    }
    """
    orijinal = kelime
    kelime_lower = kelime.lower().strip()
    
    sonuc = {
        "basarili": False,
        "orijinal": orijinal,
        "kok": "",
        "ekler": [],
        "analiz": "",
        "tur": "fiil"
    }
    
    if not kelime_lower:
        return sonuc
    
    temp = kelime_lower
    
    # Olumsuz ekleri önce kontrol et
    for zaman_kodu, ek_listesi in FIIL_EK_SOZLUGU["ZAMAN_OLUMSUZ"].items():
        for ek in ek_listesi:
            if temp.endswith(ek) and len(temp) > len(ek) + 1:
                sonuc["basarili"] = True
                sonuc["kok"] = temp[:-len(ek)].capitalize()
                sonuc["ekler"] = [{"ek": ek, "tip": "Olumsuz Zaman", "kod": zaman_kodu}]
                sonuc["analiz"] = f"{temp[:-len(ek)].capitalize()} (Kök) + {ek} ({zaman_kodu})"
                return sonuc
    
    # Olumlu ekleri kontrol et
    for zaman_kodu, ek_listesi in FIIL_EK_SOZLUGU["ZAMAN_OLUMLU"].items():
        for ek in ek_listesi:
            if temp.endswith(ek) and len(temp) > len(ek):
                kalan = temp[:-len(ek)]
                
                # Ünsüz yumuşaması kontrol (Ö2 için)
                sert_kok = yumusamayi_geri_al(kalan)
                
                sonuc["basarili"] = True
                sonuc["kok"] = sert_kok.capitalize() if sert_kok != kalan else kalan.capitalize()
                sonuc["ekler"] = [{"ek": ek, "tip": "Zaman", "kod": zaman_kodu}]
                sonuc["analiz"] = f"{sonuc['kok']} (Kök) + {ek} ({zaman_kodu})"
                return sonuc
    
    # Hiçbir ek bulunamadıysa kelimeyi kök olarak kabul et
    sonuc["basarili"] = True
    sonuc["kok"] = kelime_lower.capitalize()
    sonuc["analiz"] = f"{kelime_lower.capitalize()} (Kök)"
    
    return sonuc


def parse_kelime(kelime):
    """
    Verilen kelimeyi otomatik olarak isim veya fiil olarak parse eder.
    Önce fiil olarak dener (daha spesifik ekler), başarısız olursa isim olarak dener.
    
    Döndürür:
    {
        "basarili": True/False,
        "orijinal": "kelime",
        "kok": "kök",
        "ekler": [...],
        "analiz": "...",
        "tur": "isim" / "fiil"
    }
    """
    kelime = kelime.strip()
    
    if not kelime:
        return {
            "basarili": False,
            "orijinal": kelime,
            "kok": "",
            "ekler": [],
            "analiz": "",
            "tur": "bilinmiyor"
        }
    
    # Önce fiil olarak parse et (zaman ekleri daha spesifik)
    fiil_sonuc = parse_fiil(kelime)
    
    # Fiil eki bulunduysa fiil olarak döndür
    if fiil_sonuc["basarili"] and fiil_sonuc["ekler"]:
        return fiil_sonuc
    
    # İsim olarak parse et
    isim_sonuc = parse_isim(kelime)
    isim_sonuc["tur"] = "isim"
    
    return isim_sonuc


# ===== TEST =====
if __name__ == "__main__":
    test_kelimeler = [
        "kitap",
        "kitabym",
        "kitaplarymyzdan",
        "başlarymyz",
        "gözleriňiz",
        "mekdepde",
        "defterim",
        "okuwçylar",
    ]
    
    print("\n" + "="*50)
    print("İSİM PARSE TESTLERİ:")
    for kelime in test_kelimeler:
        sonuc = parse_isim(kelime)
        print(f"\n{kelime} → {sonuc['analiz']}")
    
    fiil_testleri = [
        "geldim",
        "gitdiler",
        "okadym",
        "ýazdym",
        "gelmedi",
        "gitjek",
        "geler",
    ]
    
    print("\n" + "="*50)
    print("FİİL PARSE TESTLERİ:")
    for kelime in fiil_testleri:
        sonuc = parse_fiil(kelime)
        print(f"\n{kelime} → {sonuc['analiz']}")
