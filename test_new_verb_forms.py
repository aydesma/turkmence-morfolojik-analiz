"""
Yeni fiil çekim formları için test modülü.
Şert, Buýruk, Hökmanlyk, Nätanyş Öten, Arzuw-Ökünç,
Fiilimsi (Hal işlik, Ortak işlik), Ettirgen, Edilgen
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from morphology import fiil_cekimle, analyze_verb

# ============================================================
#  Yardımcı: fiil_cekimle sonucunu yazdır
# ============================================================
def check(label, kok, zaman, sahis, olumsuz, expected):
    result, secere = fiil_cekimle(kok, zaman, sahis, olumsuz)
    # G1 gibi zamir içerenler için sadece fiil kısmını kontrol et
    actual = result.split()[-1] if " " in result else result
    ok = actual == expected
    status = "OK" if ok else "FAIL"
    if not ok:
        print(f"  [{status}] {label}: beklenen='{expected}', gelen='{actual}' (full='{result}')")
    return ok


def run_tests():
    total = 0
    passed = 0

    # ================================================================
    #  1) ŞERT FORMASY (zaman=8)
    # ================================================================
    print("=" * 60)
    print("SERT FORMASY (zaman=8)")
    print("=" * 60)

    sert_tests = [
        # (kök, şahıs, olumsuz, beklenen)
        ("gel", "A1", False, "gelsem"),
        ("gel", "A2", False, "gelseň"),
        ("gel", "A3", False, "gelse"),
        ("gel", "B1", False, "gelsek"),
        ("gel", "B2", False, "gelseňiz"),
        ("gel", "B3", False, "gelseler"),
        ("al",  "A1", False, "alsam"),
        ("al",  "A3", False, "alsa"),
        ("oka", "A1", False, "okasam"),
        ("oka", "A3", False, "okasa"),
        # Olumsuz
        ("gel", "A1", True, "gelmesem"),
        ("gel", "A2", True, "gelmeseň"),
        ("gel", "A3", True, "gelmese"),
        ("gel", "B3", True, "gelmeseler"),
        ("al",  "A1", True, "almasam"),
        ("oka", "A1", True, "okamasam"),
    ]
    for kok, sahis, olum, beklenen in sert_tests:
        total += 1
        neg = "olum" if olum else "pos"
        if check(f"Şert {kok}/{sahis}/{neg}", kok, "8", sahis, olum, beklenen):
            passed += 1

    # ================================================================
    #  2) BUÝRUK FORMASY (zaman=9)
    # ================================================================
    print("\n" + "=" * 60)
    print("BUYRYK FORMASY (zaman=9)")
    print("=" * 60)

    buyruk_tests = [
        # Olumlu
        ("gel", "A1", False, "geleýin"),
        ("gel", "A2", False, "gel"),
        ("gel", "A3", False, "gelsin"),
        ("gel", "B1", False, "geleli"),
        ("gel", "B2", False, "geliň"),
        ("gel", "B3", False, "gelsinler"),
        ("al",  "A1", False, "alaýyn"),
        ("al",  "A2", False, "al"),
        ("al",  "A3", False, "alsyn"),
        ("al",  "B2", False, "alyň"),
        ("oka", "A1", False, "okaýyn"),
        ("oka", "A2", False, "oka"),
        ("oka", "A3", False, "okasyn"),
        ("oka", "B1", False, "okaly"),
        ("oka", "B2", False, "okaň"),
        # Tek heceli dodak: gör, dur
        ("gör", "A3", False, "görsün"),
        ("dur", "A3", False, "dursun"),
        ("gör", "B2", False, "görüň"),
        ("dur", "B2", False, "duruň"),
        ("gör", "B3", False, "görsünler"),
        ("dur", "B3", False, "dursunlar"),
        # Olumsuz
        ("gel", "A1", True, "gelmeýin"),
        ("gel", "A2", True, "gelme"),
        ("gel", "A3", True, "gelmesin"),
        ("gel", "B1", True, "gelmeli"),
        ("gel", "B2", True, "gelmeň"),
        ("gel", "B3", True, "gelmesinler"),
        ("al",  "A2", True, "alma"),
        ("dur", "A3", True, "durmasyn"),  # -ma sonrası dodak iptal
        ("gör", "A3", True, "görmesin"),
        ("dur", "B3", True, "durmasynlar"),
    ]
    for kok, sahis, olum, beklenen in buyruk_tests:
        total += 1
        neg = "olum" if olum else "pos"
        if check(f"Buýruk {kok}/{sahis}/{neg}", kok, "9", sahis, olum, beklenen):
            passed += 1

    # ================================================================
    #  3) HÖKMANLYK FORMASY (zaman=10)
    # ================================================================
    print("\n" + "=" * 60)
    print("HOKMANLYK FORMASY (zaman=10)")
    print("=" * 60)

    hokmanlyk_tests = [
        ("gel", "A3", False, "gelmeli"),
        ("al",  "A3", False, "almaly"),
        ("oka", "A3", False, "okamaly"),
        ("gör", "A3", False, "görmeli"),
        # Olumsuz (+ " däl")
    ]
    for kok, sahis, olum, beklenen in hokmanlyk_tests:
        total += 1
        neg = "olum" if olum else "pos"
        if check(f"Hökmanlyk {kok}/{sahis}/{neg}", kok, "10", sahis, olum, beklenen):
            passed += 1

    # Hökmanlyk olumsuz özel kontrol (sonuçta " däl" var)
    for kok, beklenen in [("gel", "gelmeli däl"), ("al", "almaly däl")]:
        total += 1
        result, _ = fiil_cekimle(kok, "10", "A3", True)
        ok = result == beklenen
        status = "OK" if ok else "FAIL"
        if not ok:
            print(f"  [{status}] Hökmanlyk {kok}/olum: beklenen='{beklenen}', gelen='{result}'")
        if ok:
            passed += 1

    # ================================================================
    #  4) NÄTANYŞ ÖTEN (zaman=11, Kanıtsal / Evidential)
    # ================================================================
    print("\n" + "=" * 60)
    print("NATANYS OTEN (zaman=11)")
    print("=" * 60)

    natanys_tests = [
        ("gel", "A1", False, "gelipdirin"),
        ("gel", "A2", False, "gelipdirsiň"),
        ("gel", "A3", False, "gelipdir"),
        ("gel", "B1", False, "gelipdiris"),
        ("al",  "A1", False, "alypdyryn"),
        ("al",  "A3", False, "alypdyr"),
        ("oka", "A1", False, "okapdyryn"),
        ("oka", "A3", False, "okapdyr"),
        ("gör", "A1", False, "görüpdirin"),
        ("gör", "A3", False, "görüpdir"),
        ("dur", "A1", False, "durupdyryn"),
        ("dur", "A3", False, "durupdyr"),
        # Olumsuz
        ("gel", "A1", True, "gelmändirin"),
        ("gel", "A3", True, "gelmändir"),
        ("al",  "A1", True, "almandyryn"),
        ("al",  "A3", True, "almandyr"),
    ]
    for kok, sahis, olum, beklenen in natanys_tests:
        total += 1
        neg = "olum" if olum else "pos"
        if check(f"Nätanyş {kok}/{sahis}/{neg}", kok, "11", sahis, olum, beklenen):
            passed += 1

    # ================================================================
    #  5) ARZUW-ÖKÜNÇ (zaman=12, Optative/Wish)
    # ================================================================
    print("\n" + "=" * 60)
    print("ARZUW-OKUNC (zaman=12)")
    print("=" * 60)

    arzuw_tests = [
        ("gel", "A1", False, "gelsedim"),
        ("gel", "A2", False, "gelsediň"),
        ("gel", "A3", False, "gelsedi"),
        ("gel", "B1", False, "gelsedik"),
        ("gel", "B3", False, "gelsediler"),
        ("al",  "A1", False, "alsadym"),
        ("al",  "A3", False, "alsady"),
        ("oka", "A1", False, "okasadym"),
        # Olumsuz
        ("gel", "A1", True, "gelmesedim"),
        ("al",  "A1", True, "almasadym"),
    ]
    for kok, sahis, olum, beklenen in arzuw_tests:
        total += 1
        neg = "olum" if olum else "pos"
        if check(f"Arzuw {kok}/{sahis}/{neg}", kok, "12", sahis, olum, beklenen):
            passed += 1

    # ================================================================
    #  6) FİİLİMSİ FORMLARI (zaman=13-16)
    # ================================================================
    print("\n" + "=" * 60)
    print("FIILIMSI FORMLARI (zaman=13-16)")
    print("=" * 60)

    fiilimsi_tests = [
        # Hal işlik (converb, 13)
        ("gel", "13", False, "gelip"),
        ("al",  "13", False, "alyp"),
        ("oka", "13", False, "okap"),
        ("gör", "13", False, "görüp"),
        ("dur", "13", False, "durup"),
        ("gel", "13", True,  "gelmän"),
        ("al",  "13", True,  "alman"),
        # Öten ortak (past participle, 14)
        ("gel", "14", False, "gelen"),
        ("al",  "14", False, "alan"),
        ("oka", "14", False, "okan"),
        ("gel", "14", True,  "gelmedik"),
        ("al",  "14", True,  "almadyk"),
        # Häzirki ortak (present participle, 15)
        ("gel", "15", False, "gelýän"),
        ("al",  "15", False, "alýan"),
        ("oka", "15", False, "okaýan"),
        ("gel", "15", True,  "gelmeýän"),
        ("al",  "15", True,  "almaýan"),
        # Geljek ortak (future participle, 16)
        ("gel", "16", False, "geljek"),
        ("al",  "16", False, "aljak"),
        ("gel", "16", True,  "gelmejek"),
        ("al",  "16", True,  "almajak"),
    ]
    for kok, zaman, olum, beklenen in fiilimsi_tests:
        total += 1
        neg = "olum" if olum else "pos"
        if check(f"Fiilimsi {kok}/z={zaman}/{neg}", kok, zaman, "A3", olum, beklenen):
            passed += 1

    # ================================================================
    #  7) ETTİRGEN / EDİLGEN (zaman=17-18)
    # ================================================================
    print("\n" + "=" * 60)
    print("ETTIRGEN / EDILGEN (zaman=17-18)")
    print("=" * 60)

    voice_tests = [
        # Ettirgen (causative, 17)
        ("gel", "17", "geldir"),   # ince consonant → dir
        ("al",  "17", "aldyr"),
        ("oka", "17", "okat"),     # ünlüyle biten → +t
        ("gör", "17", "gördür"),   # tek heceli dodak ince → dür
        ("dur", "17", "durdur"),   # tek heceli dodak yogyn → dur
        ("ber", "17", "berdir"),   # ince consonant → dir
        ("bar", "17", "bardyr"),   # yogyn consonant → dyr
        # Edilgen (passive, 18)
        ("gel", "18", "gelin"),    # l-ending ince → in
        ("al",  "18", "alyn"),     # l-ending yogyn → yn
        ("gör", "18", "görül"),    # tek heceli dodak ince → ül
        ("dur", "18", "durul"),    # tek heceli dodak yogyn → ul
    ]
    for item in voice_tests:
        kok, zaman, beklenen = item
        total += 1
        result, secere = fiil_cekimle(kok, zaman, "A3", False)
        ok = result == beklenen
        status = "OK" if ok else "FAIL"
        if not ok:
            print(f"  [{status}] Voice {kok}/z={zaman}: beklenen='{beklenen}', gelen='{result}'")
        if ok:
            passed += 1

    # ================================================================
    #  8) analyze_verb API testi
    # ================================================================
    print("\n" + "=" * 60)
    print("ANALYZE_VERB API TESTI")
    print("=" * 60)

    api_tests = [
        ("gel", "Ş1",  "A1", False),
        ("gel", "B1K", "A2", False),
        ("gel", "B1K", "A3", False),
        ("gel", "HK",  "A3", False),
        ("gel", "HK",  "A3", True),
        ("gel", "NÖ",  "A3", False),
        ("gel", "AÖ",  "A1", False),
        ("gel", "FH",  "A3", False),
        ("gel", "FÖ",  "A3", False),
        ("gel", "FÄ",  "A3", False),
        ("gel", "FG",  "A3", False),
        ("gel", "ETT", "A3", False),
        ("gel", "EDL", "A3", False),
    ]
    for kok, zaman_kodu, sahis, olum in api_tests:
        total += 1
        try:
            parts, final = analyze_verb(kok, zaman_kodu, sahis, olum)
            ok = len(parts) > 0 and final != "" and not final.startswith("HATA")
            if not ok:
                print(f"  [FAIL] API {kok}/{zaman_kodu}/{sahis}: parts={parts}, final='{final}'")
            else:
                passed += 1
        except Exception as e:
            print(f"  [FAIL] API {kok}/{zaman_kodu}/{sahis}: Exception: {e}")

    # ================================================================
    #  SONUÇ
    # ================================================================
    print("\n" + "=" * 60)
    print(f"SONUC: {passed}/{total} test basarili")
    if passed < total:
        print(f"  {total - passed} test basarisiz!")
    else:
        print("  Tum testler gecti!")
    print("=" * 60)
    return passed == total


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
