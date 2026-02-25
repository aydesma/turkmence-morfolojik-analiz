# -*- coding: utf-8 -*-
"""
TurkmenFST — Web Uygulaması (Flask)

Çalıştırma:
    cd turkmen-fst/web
    python app.py
"""

import sys
import os

# turkmen_fst paketini import edebilmek için yolu ayarla
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from flask import Flask, render_template, request
from turkmen_fst.generator import MorphologicalGenerator
from turkmen_fst.analyzer import MorphologicalAnalyzer
from turkmen_fst.lexicon import Lexicon


# ==============================================================================
#  UYGULAMA KURULUMU
# ==============================================================================

app = Flask(__name__)

# Sözlük yükleme
_lexicon = Lexicon()
_data_paths = [
    os.path.join(os.path.dirname(__file__), "..", "data", "turkmence_sozluk.txt"),
    os.path.join(os.path.dirname(__file__), "..", "..", "turkmence_sozluk.txt"),
]
for p in _data_paths:
    if os.path.exists(p):
        _lexicon.load(os.path.realpath(p))
        break

_generator = MorphologicalGenerator(_lexicon)
_analyzer = MorphologicalAnalyzer(_lexicon)


# ==============================================================================
#  ANA SAYFA
# ==============================================================================

@app.route('/', methods=['GET', 'POST'])
def index():
    """Ana sayfa: isim/fiil çekimi, parse ve paradigma işlemleri."""

    # Sonuç değişkenleri
    result = None
    final_word = ""
    root_word = ""
    parse_result = None
    parse_results_all = None
    is_dual = False
    dual_results = None
    paradigma_data = None
    paradigma_type = None

    # Mod ve aksiyon bilgisi
    mode = request.form.get('mode', 'isim')
    action = request.form.get('action', 'cekimle')

    # Kullanıcı seçimlerini koruma
    selected_sayi = ""
    selected_iyelik = ""
    selected_hal = "H1"
    selected_zaman = ""
    selected_sahis = ""
    selected_olumsuz = False

    if request.method == 'POST':
        root = request.form.get('root', '').strip()
        root_word = root

        # --- Parse işlemi ---
        if action == 'parse' and root:
            multi = _analyzer.parse(root)
            results_list = []
            for r in multi.results:
                results_list.append({
                    "basarili": r.success,
                    "orijinal": r.original,
                    "kok": r.stem,
                    "ekler": [{"ek": s.get("suffix", ""), "tip": s.get("type", ""), "kod": s.get("code", "")}
                              for s in r.suffixes],
                    "analiz": r.breakdown,
                    "tur": {"noun": "isim", "verb": "fiil"}.get(r.word_type, "bilinmiyor"),
                    "anlam": getattr(r, "meaning", "")
                })
            if results_list:
                parse_result = results_list[0]
                if len(results_list) > 1:
                    parse_results_all = results_list

        # --- Paradigma tablosu ---
        elif action == 'paradigma' and root:
            paradigma_type = request.form.get('paradigma_type', 'noun')
            paradigma_data = _build_paradigma(root, paradigma_type)

        # --- Çekimleme işlemi ---
        elif action == 'cekimle':
            if mode == 'isim':
                s_code = request.form.get('sayi')
                i_code = request.form.get('iyelik')
                h_code = request.form.get('hal', 'H1')

                selected_sayi = s_code or ""
                selected_iyelik = i_code or ""
                selected_hal = h_code or "H1"

                if root:
                    results_list, is_dual = _generator.analyze_noun(root, s_code, i_code, h_code)
                    if is_dual:
                        dual_results = results_list
                    result = results_list[0]["parts"]
                    final_word = results_list[0]["final_word"]

            else:
                zaman_kodu = request.form.get('zaman', '').strip().upper()
                sahis_kodu = request.form.get('sahis', '').strip().upper()
                olumsuz = request.form.get('olumsuz') == 'on'

                selected_zaman = zaman_kodu
                selected_sahis = sahis_kodu
                selected_olumsuz = olumsuz

                if root and zaman_kodu and sahis_kodu:
                    parts, final_word = _generator.analyze_verb(root, zaman_kodu, sahis_kodu, olumsuz)
                    if parts and parts[0].get("type") == "Hata":
                        result = parts
                        final_word = ""
                    elif parts and final_word:
                        result = parts
                    else:
                        result = [{"text": "Geçersiz kodlar veya kök kelime.", "type": "Hata", "code": "HATA"}]
                        final_word = ""

    return render_template('index.html',
                           result=result,
                           final_word=final_word,
                           root=root_word,
                           mode=mode,
                           action=action,
                           parse_result=parse_result,
                           parse_results_all=parse_results_all,
                           is_dual=is_dual,
                           dual_results=dual_results,
                           paradigma_data=paradigma_data,
                           paradigma_type=paradigma_type,
                           selected_sayi=selected_sayi,
                           selected_iyelik=selected_iyelik,
                           selected_hal=selected_hal,
                           selected_zaman=selected_zaman,
                           selected_sahis=selected_sahis,
                           selected_olumsuz=selected_olumsuz)


# ==============================================================================
#  PARADIGMA
# ==============================================================================

def _build_paradigma(stem, ptype):
    """Paradigma tablosu verileri oluşturur."""
    CASE_NAMES = {
        None: ("—", "Baş düşüm (Yalın)"),
        "A2": ("A₂", "Eýelik düşüm"),
        "A3": ("A₃", "Barlag düşüm"),
        "A4": ("A₄", "Tabyn düşüm"),
        "A5": ("A₅", "Ýerlik düşüm"),
        "A6": ("A₆", "Çykyş düşüm"),
    }

    TENSE_NAMES = {
        "1": "Anyk öten zaman",
        "2": "Daş öten zaman",
        "3": "Dowamly öten zaman",
        "4": "Umumy häzirki zaman",
        "5": "Anyk häzirki zaman",
        "6": "Mälim geljek zaman",
        "7": "Nämälim geljek zaman",
    }

    PERSON_NAMES = {
        "A1": "Men", "A2": "Sen", "A3": "Ol",
        "B1": "Biz", "B2": "Siz", "B3": "Olar",
    }

    if ptype == "noun":
        cases = [None, "A2", "A3", "A4", "A5", "A6"]
        poss_codes = [None, "A1", "A2", "A3"]

        def gen_row(plural, case):
            code, name = CASE_NAMES[case]
            row = {"code": code, "name": name, "forms": []}
            for poss in poss_codes:
                r = _generator.generate_noun(stem, plural=plural,
                                              possessive=poss, case=case)
                row["forms"].append(r.word if r.is_valid else "—")
            return row

        return {
            "type": "noun",
            "stem": stem,
            "poss_headers": ["Ø", "D₁b (meniň)", "D₂b (seniň)", "D₃b (onuň)"],
            "singular": [gen_row(False, c) for c in cases],
            "plural": [gen_row(True, c) for c in cases],
        }

    elif ptype == "verb":
        persons = ["A1", "A2", "A3", "B1", "B2", "B3"]
        tenses = []
        for t_code in ["1", "2", "3", "4", "5", "6", "7"]:
            rows = []
            for p_code in persons:
                pos_r = _generator.generate_verb(stem, t_code, p_code, negative=False)
                neg_r = _generator.generate_verb(stem, t_code, p_code, negative=True)
                rows.append({
                    "person": PERSON_NAMES[p_code],
                    "positive": pos_r.word if pos_r.is_valid else "—",
                    "negative": neg_r.word if neg_r.is_valid else "—",
                })
            tenses.append({
                "code": t_code,
                "name": TENSE_NAMES[t_code],
                "rows": rows,
            })
        return {
            "type": "verb",
            "stem": stem,
            "tenses": tenses,
        }

    return None


if __name__ == '__main__':
    app.run(debug=True, port=5001)
