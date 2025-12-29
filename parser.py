# -*- coding: utf-8 -*-
"""
Türkmence Morfolojik Parser Modülü
Sözlük tabanlı kök tanıma ve ek ayırma işlemleri
"""

import os

# ===== TEMEL TANIMLAR =====
unluler = set("aeäuüyiöo")
kalin_unluler = set("aouy")
ince_unluler = set("eäiüö")

# Ünlü düşmesine meyilli kelimeler
dusme_sozlugu = {
    "burun": "burn", "alyn": "aln", "agyz": "agz", 
    "göbek": "göbk", "ogul": "ogl", "erin": "ern"
}

# Tersine çevrilmiş düşme sözlüğü (düşmüş -> orijinal)
dusme_ters = {v: k for k, v in dusme_sozlugu.items()}

# ===== SÖZLÜK YÜKLEYİCİ =====
def sozluk_yukle():
    """tk_TM.dic dosyasından kelimeleri yükler"""
    sozluk = set()
    
    # Dosya yolunu bul
    script_dir = os.path.dirname(os.path.abspath(__file__))
    dic_path = os.path.join(script_dir, "tk_TM.dic")
    
    if not os.path.exists(dic_path):
        print(f"Uyarı: Sözlük dosyası bulunamadı: {dic_path}")
        return sozluk
    
    try:
        with open(dic_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.isdigit():  # İlk satır (sayı) atla
                    continue
                # Hunspell formatı: kelime/flaglar veya sadece kelime
                if "/" in line:
                    kelime = line.split("/")[0]
                else:
                    kelime = line
                sozluk.add(kelime.lower())
    except Exception as e:
        print(f"Sözlük yüklenirken hata: {e}")
    
    return sozluk

# Sözlüğü bir kez yükle
SOZLUK = sozluk_yukle()

# ===== EK SÖZLÜĞÜ (Hiyerarşik - Uzundan Kısaya Sıralı) =====
# Not: Aynı eki birden fazla kategoride kontrol etmemek için dikkatli sıralama gerekli

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

def kok_sozlukte_mi(kok):
    """Kökün sözlükte olup olmadığını kontrol eder"""
    return kok.lower() in SOZLUK

def kok_bul(kelime):
    """
    Verilen kelime için olası kökleri kontrol eder.
    Hem doğrudan hem de ses değişimleri uygulanmış halleri dener.
    """
    kelime_lower = kelime.lower()
    
    # 1. Direkt sözlükte mi?
    if kok_sozlukte_mi(kelime_lower):
        return kelime_lower
    
    # 2. Yumuşama geri alınmış hali sözlükte mi?
    sert = yumusamayi_geri_al(kelime_lower)
    if sert != kelime_lower and kok_sozlukte_mi(sert):
        return sert
    
    # 3. Düşme geri alınmış hali sözlükte mi?
    dusme = dusmeyi_geri_al(kelime_lower)
    if dusme != kelime_lower and kok_sozlukte_mi(dusme):
        return dusme
    
    return None

# ===== ANA PARSE FONKSİYONU =====

def parse_isim(kelime):
    """
    İsim kelimesini kök ve eklerine ayırır.
    
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
    
    # Tam eşleşme - kelime doğrudan sözlükte mi?
    if kok_sozlukte_mi(kelime):
        sonuc["basarili"] = True
        sonuc["kok"] = kelime.capitalize()
        sonuc["analiz"] = f"{kelime.capitalize()} (Kök)"
        return sonuc
    
    # Ekleri ayırmaya çalış (sondan başa)
    temp = kelime
    ekler = []
    
    # 1. KATMAN: HAL EKLERİ
    for kod, ek_listesi in EK_SOZLUGU["HAL"].items():
        for ek in ek_listesi:
            if temp.endswith(ek) and len(temp) > len(ek) + 1:  # Kök en az 2 harf
                kalan = temp[:-len(ek)]
                
                # Ses değişimi varsa geri al
                kalan_kontrol = kalan
                if ek[0] in unluler or ek.startswith("n"):
                    kalan_kontrol = yumusamayi_geri_al(kalan)
                    kalan_kontrol = dusmeyi_geri_al(kalan_kontrol)
                
                # Kök sözlükte mi kontrol et
                bulunan_kok = kok_bul(kalan) or kok_bul(kalan_kontrol)
                if bulunan_kok:
                    sonuc["basarili"] = True
                    sonuc["kok"] = bulunan_kok.capitalize()
                    sonuc["ekler"] = [{"ek": ek, "tip": "Hal", "kod": kod}]
                    sonuc["analiz"] = f"{bulunan_kok.capitalize()} (Kök) + {ek} ({kod})"
                    return sonuc
                
                # Kök bulunamadıysa eki kaydet ve devam et
                ekler.insert(0, {"ek": ek, "tip": "Hal", "kod": kod})
                temp = kalan
                break
        else:
            continue
        break
    
    # 2. KATMAN: İYELİK EKLERİ
    for kod, ek_listesi in EK_SOZLUGU["IYELIK"].items():
        for ek in ek_listesi:
            if temp.endswith(ek) and len(temp) > len(ek) + 1:
                kalan = temp[:-len(ek)]
                
                # Ses değişimi kontrolü
                kalan_kontrol = kalan
                if ek[0] in unluler:
                    kalan_kontrol = yumusamayi_geri_al(kalan)
                    kalan_kontrol = dusmeyi_geri_al(kalan_kontrol)
                
                bulunan_kok = kok_bul(kalan) or kok_bul(kalan_kontrol)
                if bulunan_kok:
                    sonuc["basarili"] = True
                    sonuc["kok"] = bulunan_kok.capitalize()
                    sonuc["ekler"] = [{"ek": ek, "tip": "İyelik", "kod": kod}] + ekler
                    analiz_parts = [f"{bulunan_kok.capitalize()} (Kök)", f"{ek} ({kod})"]
                    for e in ekler:
                        analiz_parts.append(f"{e['ek']} ({e['kod']})")
                    sonuc["analiz"] = " + ".join(analiz_parts)
                    return sonuc
                
                ekler.insert(0, {"ek": ek, "tip": "İyelik", "kod": kod})
                temp = kalan
                break
        else:
            continue
        break
    
    # 3. KATMAN: ÇOKLUK EKLERİ
    for kod, ek_listesi in EK_SOZLUGU["COKL"].items():
        for ek in ek_listesi:
            if temp.endswith(ek) and len(temp) > len(ek) + 1:
                kalan = temp[:-len(ek)]
                
                bulunan_kok = kok_bul(kalan)
                if bulunan_kok:
                    sonuc["basarili"] = True
                    sonuc["kok"] = bulunan_kok.capitalize()
                    sonuc["ekler"] = [{"ek": ek, "tip": "Çoğul", "kod": kod}] + ekler
                    analiz_parts = [f"{bulunan_kok.capitalize()} (Kök)", f"{ek} ({kod})"]
                    for e in ekler:
                        analiz_parts.append(f"{e['ek']} ({e['kod']})")
                    sonuc["analiz"] = " + ".join(analiz_parts)
                    return sonuc
                
                ekler.insert(0, {"ek": ek, "tip": "Çoğul", "kod": kod})
                temp = kalan
                break
        else:
            continue
        break
    
    # Kök bulunduysa (sözlükte)
    bulunan_kok = kok_bul(temp)
    if bulunan_kok and ekler:
        sonuc["basarili"] = True
        sonuc["kok"] = bulunan_kok.capitalize()
        sonuc["ekler"] = ekler
        analiz_parts = [f"{bulunan_kok.capitalize()} (Kök)"]
        for e in ekler:
            analiz_parts.append(f"{e['ek']} ({e['kod']})")
        sonuc["analiz"] = " + ".join(analiz_parts)
        return sonuc
    
    # ===== FALLBACK: Sözlükte bulunamadı, otomatik parse =====
    return parse_isim_fallback(orijinal)

def parse_isim_fallback(kelime):
    """
    Sözlükte bulunamayan kelimeler için sondan başa otomatik parse.
    """
    orijinal = kelime
    temp = kelime.lower().strip()
    ekler = []
    
    sonuc = {
        "basarili": True,  # Fallback her zaman "başarılı" sayılır
        "orijinal": orijinal,
        "kok": "",
        "ekler": [],
        "analiz": "",
        "uyari": "Kök kelime sözlükte bulunamadı, analiz tam otomatik yapılmıştır."
    }
    
    # 1. HAL EKLERİ
    for kod, ek_listesi in EK_SOZLUGU["HAL"].items():
        for ek in ek_listesi:
            if temp.endswith(ek) and len(temp) > len(ek) + 1:
                ekler.insert(0, {"ek": ek, "tip": "Hal", "kod": kod})
                temp = temp[:-len(ek)]
                # Ses değişimi geri al
                if ek[0] in unluler or ek.startswith("n"):
                    temp = yumusamayi_geri_al(temp)
                    temp = dusmeyi_geri_al(temp)
                break
        else:
            continue
        break
    
    # 2. İYELİK EKLERİ
    for kod, ek_listesi in EK_SOZLUGU["IYELIK"].items():
        for ek in ek_listesi:
            if temp.endswith(ek) and len(temp) > len(ek) + 1:
                ekler.insert(0, {"ek": ek, "tip": "İyelik", "kod": kod})
                temp = temp[:-len(ek)]
                if ek[0] in unluler:
                    temp = yumusamayi_geri_al(temp)
                    temp = dusmeyi_geri_al(temp)
                break
        else:
            continue
        break
    
    # 3. ÇOKLUK EKLERİ
    for kod, ek_listesi in EK_SOZLUGU["COKL"].items():
        for ek in ek_listesi:
            if temp.endswith(ek) and len(temp) > len(ek):
                ekler.insert(0, {"ek": ek, "tip": "Çoğul", "kod": kod})
                temp = temp[:-len(ek)]
                break
        else:
            continue
        break
    
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
    visited = set()  # Döngü önleme
    
    def parse_yol(temp, ekler, ziyaret_id):
        """Tek bir parse yolunu takip et"""
        if ziyaret_id in visited:
            return
        visited.add(ziyaret_id)
        
        # Kök bulunduysa sonuç ekle
        bulunan_kok = kok_bul(temp)
        if bulunan_kok and ekler:
            analiz_parts = [f"{bulunan_kok.capitalize()} (Kök)"]
            for e in ekler:
                analiz_parts.append(f"{e['ek']} ({e['kod']})")
            sonuclar.append({
                "kok": bulunan_kok.capitalize(),
                "ekler": list(ekler),
                "analiz": " + ".join(analiz_parts)
            })
            return  # Kök bulundu, bu yol tamamlandı
        
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
                        tip = {"HAL": "Hal", "IYELIK": "İyelik", "COKL": "Çoğul"}[kategori]
                        yeni_ekler = [{"ek": ek, "tip": tip, "kod": kod}] + list(ekler)
                        ziyaret_key = f"{kalan}|{kod}"
                        parse_yol(kalan, yeni_ekler, ziyaret_key)
    
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
# Fiil çekimlerinde kullanılan ekler (sondan başa parse için sıralı)

FIIL_EK_SOZLUGU = {
    # ŞAHIS EKLERİ (Fiil sonunda)
    "SAHIS": {
        "B3": ["lar", "ler"],                                    # 3. çoğul
        "B2": ["syňyz", "siňiz", "ňyz", "ňiz"],                 # 2. çoğul
        "B1": ["ys", "is", "s", "k"],                           # 1. çoğul
        "A2": ["syň", "siň", "ň"],                              # 2. tekil
        "A1": ["yn", "in", "n", "m"],                           # 1. tekil
        "A3": []                                                 # 3. tekil (ek yok)
    },
    
    # ZAMAN EKLERİ (Olumlu)
    "ZAMAN_OLUMLU": {
        # Geçmiş Zamanlar (Öten Zaman)
        "Ö1": ["dyňyz", "diňiz", "tyňyz", "tiňiz",              # -dy/-di/-ty/-ti (+şahıs)
               "dym", "dim", "tym", "tim",
               "dyň", "diň", "tyň", "tiň", 
               "dyk", "dik", "tyk", "tik",
               "dylar", "diler", "tylar", "tiler",
               "dy", "di", "ty", "ti"],
        "Ö2": ["ypdylar", "ipdiler", "updylar", "üpdiler",      # -yp/-ip + -dy/-di
               "yptymlar", "iptimler", "uptumlar", "üptümler",  # -yp/-ip + -ty/-ti (t-varyant)
               "ypdym", "ipdim", "updym", "üpdim",
               "yptym", "iptim", "uptum", "üptüm",              # 1. tekil t-varyant
               "ypdyň", "ipdiň", "updyň", "üpdiň",
               "yptyň", "iptiň", "uptuň", "üptüň",              # 2. tekil t-varyant
               "ypdyk", "ipdik", "updyk", "üpdik",
               "yptyk", "iptik", "uptuk", "üptük",              # 1. çoğul t-varyant
               "ypdyňyz", "ipdiňiz", "updyňyz", "üpdiňiz",
               "yptyňyz", "iptiňiz", "uptuňyz", "üptüňiz",      # 2. çoğul t-varyant
               "ypty", "ipti", "upty", "üpti",
               "ypdy", "ipdi", "updy", "üpdi"],
        "Ö3": ["ýardylar", "ýärdiler",                          # Dowamly öten
               "ýardym", "ýärdim", "ýardyň", "ýärdiň",
               "ýardyk", "ýärdik", "ýardyňyz", "ýärdiňiz",
               "ýardy", "ýärdi"],
        
        # Şimdiki Zamanlar (Häzirki Zaman)
        "H1": ["ýaryn", "ýärin", "ýarsyň", "ýärsiň",            # Umumy häzirki
               "ýarys", "ýäris", "ýarsyňyz", "ýärsiňiz",
               "ýarlar", "ýärler", "ýar", "ýär"],
        "H2": ["ýandyryn", "ýändirim", "ýandyrsyň", "ýändirsiň", # Anyk häzirki
               "ýandyr", "ýändir"],
        
        # Gelecek Zamanlar (Geljek Zaman)
        "G1": ["jaklar", "jekler", "jak", "jek"],               # Mälim geljek
        "G2": ["aryn", "erin", "arsyň", "ersiň",                # Nämälim geljek
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

# Fiil kökleri için ek set - sözlükten ayırt edilecek
# Not: Aslında sözlükte fiiller de var, ama doğrulama için kullanacağız


def parse_fiil(kelime):
    """
    Çekimli fiili kök ve eklerine ayırır.
    
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
    
    # Olumlu ve olumsuz zaman eklerini dene
    for olumsuz_mu, zaman_dict in [(True, FIIL_EK_SOZLUGU["ZAMAN_OLUMSUZ"]), 
                                    (False, FIIL_EK_SOZLUGU["ZAMAN_OLUMLU"])]:
        for zaman_kodu, ek_listesi in zaman_dict.items():
            for ek in ek_listesi:
                if kelime_lower.endswith(ek) and len(kelime_lower) > len(ek):
                    kalan = kelime_lower[:-len(ek)]
                    
                    # Kökü sözlükte ara
                    bulunan_kok = kok_bul(kalan)
                    
                    # Ünsüz yumuşaması kontrol (Ö2 için özellikle)
                    if not bulunan_kok:
                        sert_kok = yumusamayi_geri_al(kalan)
                        if sert_kok != kalan:
                            bulunan_kok = kok_bul(sert_kok)
                    
                    if bulunan_kok:
                        sonuc["basarili"] = True
                        sonuc["kok"] = bulunan_kok.capitalize()
                        
                        # Eki parçala: zaman + şahıs
                        tip = "Olumsuz Zaman" if olumsuz_mu else "Zaman"
                        sonuc["ekler"] = [{"ek": ek, "tip": tip, "kod": zaman_kodu}]
                        sonuc["analiz"] = f"{bulunan_kok.capitalize()} (Kök) + {ek} ({zaman_kodu})"
                        return sonuc
    
    # Fallback - kök tahmini yap
    return parse_fiil_fallback(orijinal)


def parse_fiil_fallback(kelime):
    """
    Sözlükte bulunamayan fiiller için otomatik parse.
    """
    orijinal = kelime
    temp = kelime.lower().strip()
    
    sonuc = {
        "basarili": True,
        "orijinal": orijinal,
        "kok": "",
        "ekler": [],
        "analiz": "",
        "tur": "fiil",
        "uyari": "Kök kelime sözlükte bulunamadı, analiz tam otomatik yapılmıştır."
    }
    
    # Olumsuz ekleri önce kontrol et
    for zaman_kodu, ek_listesi in FIIL_EK_SOZLUGU["ZAMAN_OLUMSUZ"].items():
        for ek in ek_listesi:
            if temp.endswith(ek) and len(temp) > len(ek) + 1:
                sonuc["ekler"].insert(0, {"ek": ek, "tip": "Olumsuz Zaman", "kod": zaman_kodu})
                temp = temp[:-len(ek)]
                break
        else:
            continue
        break
    
    # Olumlu ekleri kontrol et (olumsuz bulunamadıysa)
    if not sonuc["ekler"]:
        for zaman_kodu, ek_listesi in FIIL_EK_SOZLUGU["ZAMAN_OLUMLU"].items():
            for ek in ek_listesi:
                if temp.endswith(ek) and len(temp) > len(ek) + 1:
                    sonuc["ekler"].insert(0, {"ek": ek, "tip": "Zaman", "kod": zaman_kodu})
                    temp = temp[:-len(ek)]
                    break
            else:
                continue
            break
    
    # Kalan kısım kök
    sonuc["kok"] = temp.capitalize()
    
    analiz_parts = [f"{temp.capitalize()} (Kök)"]
    for e in sonuc["ekler"]:
        analiz_parts.append(f"{e['ek']} ({e['kod']})")
    sonuc["analiz"] = " + ".join(analiz_parts)
    
    return sonuc


def parse_kelime(kelime):
    """
    Verilen kelimeyi otomatik olarak isim veya fiil olarak parse eder.
    Önce isim olarak dener, başarısız olursa fiil olarak dener.
    
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
    
    # Önce isim olarak parse et
    isim_sonuc = parse_isim(kelime)
    isim_sonuc["tur"] = "isim"
    
    # İsim parse başarılıysa ve sözlükte bulunduysa
    if isim_sonuc["basarili"] and "uyari" not in isim_sonuc:
        return isim_sonuc
    
    # Fiil olarak parse et
    fiil_sonuc = parse_fiil(kelime)
    
    # Fiil parse başarılıysa ve sözlükte bulunduysa
    if fiil_sonuc["basarili"] and "uyari" not in fiil_sonuc:
        return fiil_sonuc
    
    # İkisi de fallback'e düştüyse, isim tahminini döndür
    # (Türkmencede isim çekimi daha yaygın)
    if isim_sonuc["basarili"]:
        return isim_sonuc
    
    return fiil_sonuc


# ===== TEST =====
if __name__ == "__main__":
    print(f"Sözlük yüklendi: {len(SOZLUK)} kelime")
    
    test_kelimeler = [
        "ankara",           # Özel isim - kök olarak kalmalı
        "kitap",            # Kök
        "kitabym",          # kitap + ym
        "kitaplarymyzdan",  # kitap + lar + ymyz + dan
        "başlarymyz",       # baş + lar + ymyz
        "gözleriňiz",       # göz + ler + iňiz
        "mekdepde",         # mekdep + de
        "defterim",         # defter + im
        "okuwçylar",        # okuwçy + lar
    ]
    
    print("\n" + "="*50)
    print("İSİM PARSE TESTLERİ:")
    for kelime in test_kelimeler:
        sonuc = parse_isim(kelime)
        print(f"\n{kelime} → {sonuc['analiz']}")
        if "uyari" in sonuc:
            print(f"  ⚠️ {sonuc['uyari']}")
    
    fiil_testleri = [
        "geldim",           # gel + dy + m
        "gitdiler",         # git + di + ler
        "okadym",           # oka + dy + m
        "ýazdym",           # ýaz + dy + m
        "gelmedi",          # gel + me + di
        "gitjek",           # git + jek
        "geler",            # gel + er
    ]
    
    print("\n" + "="*50)
    print("FİİL PARSE TESTLERİ:")
    for kelime in fiil_testleri:
        sonuc = parse_fiil(kelime)
        print(f"\n{kelime} → {sonuc['analiz']}")
        if "uyari" in sonuc:
            print(f"  ⚠️ {sonuc['uyari']}")

