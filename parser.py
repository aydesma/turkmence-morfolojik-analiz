# -*- coding: utf-8 -*-
"""
Türkmence Morfolojik Parser Modülü
Generator-doğrulamalı morfolojik çözümleme (Sözlük destekli)

TurkmenFST analyzer motorunu kullanarak 54.000+ kelimelik sözlük üzerinden
gerçek morfolojik analiz yapar.
"""

import os
import sys

# turkmen-fst modülünü import path'ine ekle
_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
_FST_DIR = os.path.join(_BASE_DIR, "turkmen-fst")
if _FST_DIR not in sys.path:
    sys.path.insert(0, _FST_DIR)

from turkmen_fst.lexicon import Lexicon
from turkmen_fst.analyzer import MorphologicalAnalyzer

# ===== GLOBAL MOTOR =====
_lexicon = None
_analyzer = None


def _get_analyzer():
    """Tek seferlik sözlük yükleme ve analyzer oluşturma."""
    global _lexicon, _analyzer
    if _analyzer is None:
        _lexicon = Lexicon()
        dict_path = os.path.join(_FST_DIR, "data", "turkmence_sozluk.txt")
        _lexicon.load(dict_path)
        _analyzer = MorphologicalAnalyzer(_lexicon)
    return _analyzer


def _word_type_to_tur(word_type):
    """Analyzer word_type → template tur dönüşümü."""
    return {
        "noun": "isim",
        "verb": "fiil",
        "unknown": "bilinmiyor"
    }.get(word_type, "bilinmiyor")


def _convert_result(analysis_result):
    """
    AnalysisResult → template'in beklediği dict formatına dönüştürür.
    
    Döndürür:
    {
        "basarili": True/False,
        "orijinal": "orijinal kelime",
        "kok": "bulunan kök",
        "ekler": [{"ek": "lar", "tip": "San", "kod": "S2"}, ...],
        "analiz": "Kitap (Kök) + lar (S2) + ym (D₁b)",
        "tur": "isim" / "fiil",
        "anlam": "eş sesli anlam (varsa)"
    }
    """
    ekler = []
    for s in analysis_result.suffixes:
        ekler.append({
            "ek": s.get("suffix", ""),
            "tip": s.get("type", ""),
            "kod": s.get("code", "")
        })
    
    return {
        "basarili": analysis_result.success,
        "orijinal": analysis_result.original,
        "kok": analysis_result.stem,
        "ekler": ekler,
        "analiz": analysis_result.breakdown,
        "tur": _word_type_to_tur(analysis_result.word_type),
        "anlam": getattr(analysis_result, "meaning", "")
    }


# ===== ANA PARSE FONKSİYONLARI =====

def parse_kelime(kelime):
    """
    Verilen kelimeyi morfolojik olarak çözümler.
    54.000+ kelimelik sözlük + generator doğrulaması kullanır.
    
    Tek sonuç döndürür (en iyi eşleşme).
    Birden fazla çözümleme varsa parse_kelime_multi() kullanın.
    
    Döndürür:
    {
        "basarili": True/False,
        "orijinal": "kelime",
        "kok": "kök",
        "ekler": [{"ek": ..., "tip": ..., "kod": ...}, ...],
        "analiz": "...",
        "tur": "isim" / "fiil" / "bilinmiyor"
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
    
    analyzer = _get_analyzer()
    multi = analyzer.parse(kelime)
    
    if multi.success and multi.results:
        # En iyi sonucu seç: ek sayısı fazla olan önce, sonra isim tercih et
        best = multi.results[0]
        return _convert_result(best)
    
    # Hiç sonuç yoksa
    return {
        "basarili": False,
        "orijinal": kelime,
        "kok": kelime.capitalize(),
        "ekler": [],
        "analiz": f"{kelime.capitalize()} (Kök)",
        "tur": "bilinmiyor"
    }


def parse_kelime_multi(kelime):
    """
    Verilen kelimeyi morfolojik olarak çözümler.
    Birden fazla olası çözümleme varsa hepsini döndürür.
    
    Döndürür:
    {
        "basarili": True/False,
        "orijinal": "kelime",
        "coklu": True/False,
        "sonuclar": [
            {"kok": ..., "ekler": [...], "analiz": ..., "tur": ...},
            ...
        ]
    }
    """
    kelime = kelime.strip()
    if not kelime:
        return {
            "basarili": False,
            "orijinal": kelime,
            "coklu": False,
            "sonuclar": []
        }
    
    analyzer = _get_analyzer()
    multi = analyzer.parse(kelime)
    
    if multi.success and multi.results:
        sonuclar = [_convert_result(r) for r in multi.results]
        return {
            "basarili": True,
            "orijinal": kelime,
            "coklu": len(sonuclar) > 1,
            "sonuclar": sonuclar
        }
    
    return {
        "basarili": False,
        "orijinal": kelime,
        "coklu": False,
        "sonuclar": []
    }


def parse_isim(kelime):
    """
    İsim kelimesini sözlük destekli gerçek morfolojik analizle çözümler.
    
    Döndürür:
    {
        "basarili": True/False,
        "orijinal": "orijinal kelime",
        "kok": "bulunan kök",
        "ekler": [{"ek": "lar", "tip": "San", "kod": "S2"}, ...],
        "analiz": "Kitap (Kök) + lar (S2)"
    }
    """
    kelime = kelime.strip()
    if not kelime:
        return {"basarili": False, "orijinal": kelime, "kok": "", "ekler": [], "analiz": ""}
    
    analyzer = _get_analyzer()
    results = analyzer.parse_noun(kelime)
    
    if results:
        return _convert_result(results[0])
    
    # Kök bulunamadı
    return {
        "basarili": True,
        "orijinal": kelime,
        "kok": kelime.capitalize(),
        "ekler": [],
        "analiz": f"{kelime.capitalize()} (Kök)"
    }


def parse_fiil(kelime):
    """
    Fiil kelimesini sözlük destekli gerçek morfolojik analizle çözümler.
    
    Döndürür:
    {
        "basarili": True/False,
        "orijinal": "orijinal kelime",
        "kok": "bulunan kök",
        "ekler": [{"ek": "dy", "tip": "Zaman", "kod": "Ö1"}, ...],
        "analiz": "Gel (Kök) + di (Ö1)",
        "tur": "fiil"
    }
    """
    kelime = kelime.strip()
    if not kelime:
        return {"basarili": False, "orijinal": kelime, "kok": "", "ekler": [], "analiz": "", "tur": "fiil"}
    
    analyzer = _get_analyzer()
    results = analyzer.parse_verb(kelime)
    
    if results:
        r = _convert_result(results[0])
        r["tur"] = "fiil"
        return r
    
    return {
        "basarili": True,
        "orijinal": kelime,
        "kok": kelime.capitalize(),
        "ekler": [],
        "analiz": f"{kelime.capitalize()} (Kök)",
        "tur": "fiil"
    }


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
        "geldim",
        "gitdiler",
        "ýazdym",
        "gelmedi",
    ]
    
    print("\n" + "="*60)
    print("MORFOLOJIK ÇÖZÜMLEME TESTLERİ (Sözlük Destekli)")
    print("="*60)
    for kelime in test_kelimeler:
        sonuc = parse_kelime(kelime)
        tur = sonuc.get("tur", "?")
        print(f"\n  {kelime:20s} → [{tur:5s}] {sonuc['analiz']}")
    
    print("\n" + "="*60)
    print("ÇOKLU SONUÇ TESTLERİ")
    print("="*60)
    multi_tests = ["kitaby", "aty", "guzusy"]
    for kelime in multi_tests:
        multi = parse_kelime_multi(kelime)
        print(f"\n  {kelime} ({len(multi.get('sonuclar', []))} sonuç):")
        for s in multi.get("sonuclar", []):
            print(f"    [{s.get('tur', '?'):5s}] {s['analiz']}")
