# -*- coding: utf-8 -*-
"""
TurkmenFST — Komut Satırı Arayüzü (cli.py)

Kullanım:
    python -m turkmen_fst generate --stem kitap --plural --poss 1sg --case abl
    python -m turkmen_fst analyze kitabym
    python -m turkmen_fst serve --port 8000
    python -m turkmen_fst interactive
"""

from __future__ import annotations
import argparse
import json
import os
import sys

from turkmen_fst.phonology import PhonologyRules
from turkmen_fst.lexicon import Lexicon, HOMONYMS
from turkmen_fst.morphotactics import VerbMorphotactics
from turkmen_fst.generator import MorphologicalGenerator
from turkmen_fst.analyzer import MorphologicalAnalyzer


# ==============================================================================
#  SÖZLÜK YOLU
# ==============================================================================

def _find_lexicon_path() -> str:
    """Sözlük dosyasını bul."""
    candidates = [
        os.path.join(os.path.dirname(__file__), "..", "data", "turkmence_sozluk.txt"),
        os.path.join(os.path.dirname(__file__), "..", "..", "turkmence_sozluk.txt"),
        os.path.join(os.path.dirname(__file__), "..", "..", "data", "turkmence_sozluk.txt"),
    ]
    for path in candidates:
        real = os.path.realpath(path)
        if os.path.exists(real):
            return real
    return ""


def _load_lexicon() -> Lexicon:
    """Sözlüğü yükle."""
    lexicon = Lexicon()
    path = _find_lexicon_path()
    if path:
        count = lexicon.load(path)
        return lexicon
    return lexicon


# ==============================================================================
#  GENERATE KOMUTU
# ==============================================================================

def cmd_generate(args):
    """İsim veya fiil çekimi yapar."""
    lexicon = _load_lexicon()
    gen = MorphologicalGenerator(lexicon)

    if args.type == "noun":
        # Poss kodu dönüşümü
        poss_map = {"1sg": "A1", "2sg": "A2", "3sg": "A3", "1pl": "B1", "2pl": "B2"}
        poss = poss_map.get(args.poss) if args.poss else None
        poss_type = "cog" if args.poss and args.poss.endswith("pl") else "tek"

        # Case kodu dönüşümü
        case_map = {"gen": "A2", "dat": "A3", "acc": "A4", "loc": "A5", "abl": "A6"}
        case = case_map.get(args.case) if args.case else None

        result = gen.generate_noun(args.stem, args.plural, poss, poss_type, case)
        
        print(f"Kök:     {args.stem}")
        print(f"Sonuç:   {result.word}")
        print(f"Şecere:  {result.breakdown}")
        if args.json:
            print(json.dumps({
                "stem": args.stem, "result": result.word,
                "breakdown": result.breakdown, "morphemes": result.morphemes
            }, ensure_ascii=False, indent=2))

    elif args.type == "verb":
        tense = args.tense or "1"
        person = args.person or "A1"
        result = gen.generate_verb(args.stem, tense, person, args.negative)
        
        print(f"Kök:     {args.stem}")
        print(f"Zaman:   {VerbMorphotactics.TENSE_DISPLAY.get(tense, tense)}")
        print(f"Sonuç:   {result.word}")
        print(f"Şecere:  {result.breakdown}")
        if args.json:
            print(json.dumps({
                "stem": args.stem, "result": result.word,
                "breakdown": result.breakdown, "morphemes": result.morphemes
            }, ensure_ascii=False, indent=2))


# ==============================================================================
#  ANALYZE KOMUTU
# ==============================================================================

def cmd_analyze(args):
    """Kelimeyi morfolojik olarak analiz eder."""
    lexicon = _load_lexicon()
    analyzer = MorphologicalAnalyzer(lexicon)

    for word in args.words:
        result = analyzer.parse(word)
        print(f"\n{'='*40}")
        print(f"Kelime:  {result.original}")
        print(f"Kök:     {result.stem}")
        print(f"Tür:     {result.word_type}")
        print(f"Analiz:  {result.breakdown}")
        if result.suffixes:
            print("Ekler:")
            for s in result.suffixes:
                print(f"  - {s.get('suffix', '')} ({s.get('type', '')}, {s.get('code', '')})")
        if args.json:
            print(json.dumps({
                "original": result.original, "stem": result.stem,
                "type": result.word_type, "breakdown": result.breakdown,
                "suffixes": result.suffixes
            }, ensure_ascii=False, indent=2))


# ==============================================================================
#  SERVE KOMUTU
# ==============================================================================

def cmd_serve(args):
    """FastAPI sunucusunu başlatır."""
    try:
        import uvicorn
        from turkmen_fst.api import app
        print(f"🚀 TurkmenFST API sunucusu başlatılıyor: http://localhost:{args.port}")
        print(f"📖 Swagger UI: http://localhost:{args.port}/docs")
        uvicorn.run(app, host=args.host, port=args.port)
    except ImportError:
        print("HATA: uvicorn ve fastapi kurulu değil.")
        print("Kurulum: pip install fastapi uvicorn")
        sys.exit(1)


# ==============================================================================
#  İNTERAKTİF MOD
# ==============================================================================

def cmd_interactive(args):
    """Etkileşimli komut satırı arayüzü."""
    lexicon = _load_lexicon()
    gen = MorphologicalGenerator(lexicon)
    analyzer = MorphologicalAnalyzer(lexicon)

    while True:
        print("\n" + "=" * 60)
        print("🇹🇲 TurkmenFST — Morfolojik Analiz Sistemi v1.0")
        print("=" * 60)
        mode = input("[1] İsim (At)  [2] Fiil (İşlik)  [3] Analiz  [Q] Çıkış\nSeçim: ").lower()
        
        if mode == 'q':
            break

        if mode == '1':
            stem = input("Kök Söz: ").lower()
            
            # Eş sesli kontrolü
            if stem in HOMONYMS:
                print(f"\n⚠️ '{stem}' eş sesli kelimedir:")
                for k, (anlam, _) in HOMONYMS[stem].items():
                    print(f"  [{k}] {anlam}")
                input("Seçim: ")  # Bilgi amaçlı
            
            plural = input("Çokluk [e/h]: ").lower() == 'e'
            poss_input = input("İyelik [1, 2, 3 veya boş]: ")
            poss = None
            poss_type = "tek"
            if poss_input:
                poss_type = "cog" if input("Tip [1] Tekil [2] Çoğul: ") == "2" else "tek"
                poss = "A" + poss_input
            case_input = input("Hal [A2-A6 veya boş]: ").upper()
            case = case_input if case_input else None

            result = gen.generate_noun(stem, plural, poss, poss_type, case)
            print(f"\n✅ NETİCE: {result.word}")
            print(f"🧬 ŞECERE: {result.breakdown}")

        elif mode == '2':
            stem = input("Fiil Kökü: ").lower()
            print("[1] Anyk Öten [2] Daş Öten [3] Dowamly [4] Umumy Häz.")
            print("[5] Anyk Häz.  [6] Mälim Gel. [7] Nämälim Gel.")
            tense = input("Zaman: ")
            person = input("Şahıs [A1-B3]: ").upper()
            negative = input("Olumsuz mu? [e/h]: ").lower() == 'e'
            
            result = gen.generate_verb(stem, tense, person, negative)
            print(f"\n✅ NETİCE: {result.word}")
            print(f"🧬 ŞECERE: {result.breakdown}")

        elif mode == '3':
            word = input("Kelime: ")
            result = analyzer.parse(word)
            print(f"\nKök:    {result.stem}")
            print(f"Tür:    {result.word_type}")
            print(f"Analiz: {result.breakdown}")


# ==============================================================================
#  ANA GİRİŞ NOKTASI
# ==============================================================================

def main():
    """CLI ana giriş noktası."""
    parser = argparse.ArgumentParser(
        prog="turkmen_fst",
        description="TurkmenFST — Türkmen Türkçesi Morfolojik Analiz Sistemi"
    )
    subparsers = parser.add_subparsers(dest="command", help="Komutlar")

    # generate komutu
    gen_parser = subparsers.add_parser("generate", help="Morfolojik üretim")
    gen_parser.add_argument("--stem", required=True, help="Kök kelime")
    gen_parser.add_argument("--type", choices=["noun", "verb"], default="noun", help="Kelime türü")
    gen_parser.add_argument("--plural", action="store_true", help="Çoğul eki")
    gen_parser.add_argument("--poss", choices=["1sg", "2sg", "3sg", "1pl", "2pl"], help="İyelik")
    gen_parser.add_argument("--case", choices=["gen", "dat", "acc", "loc", "abl"], help="Hal")
    gen_parser.add_argument("--tense", choices=["1","2","3","4","5","6","7"], help="Zaman (fiil)")
    gen_parser.add_argument("--person", choices=["A1","A2","A3","B1","B2","B3"], help="Şahıs (fiil)")
    gen_parser.add_argument("--negative", action="store_true", help="Olumsuz (fiil)")
    gen_parser.add_argument("--json", action="store_true", help="JSON çıktı")
    gen_parser.set_defaults(func=cmd_generate)

    # analyze komutu
    analyze_parser = subparsers.add_parser("analyze", help="Morfolojik analiz")
    analyze_parser.add_argument("words", nargs="+", help="Analiz edilecek kelimeler")
    analyze_parser.add_argument("--json", action="store_true", help="JSON çıktı")
    analyze_parser.set_defaults(func=cmd_analyze)

    # serve komutu
    serve_parser = subparsers.add_parser("serve", help="API sunucusu başlat")
    serve_parser.add_argument("--port", type=int, default=8000, help="Port (varsayılan: 8000)")
    serve_parser.add_argument("--host", default="127.0.0.1", help="Host (varsayılan: 127.0.0.1)")
    serve_parser.set_defaults(func=cmd_serve)

    # interactive komutu
    interactive_parser = subparsers.add_parser("interactive", help="Etkileşimli mod")
    interactive_parser.set_defaults(func=cmd_interactive)

    args = parser.parse_args()
    
    if args.command is None:
        # Argüman yoksa etkileşimli moda geç
        cmd_interactive(args)
    else:
        args.func(args)


if __name__ == "__main__":
    main()
