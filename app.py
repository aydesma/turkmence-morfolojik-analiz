# -*- coding: utf-8 -*-
"""
Türkmen Morfolojik Analiz — Flask Web Uygulaması + REST API

Web arayüzü ve JSON API endpoint'lerini tek Flask uygulamasında sunar.

Web:  GET/POST /
API:  POST /api/generate/noun, /api/generate/verb, /api/analyze,
      GET  /api/lexicon/<word>, /api/health
"""
import os, sys, re
from flask import Flask, render_template, request, jsonify
from morphology import analyze, analyze_verb
from parser import parse_kelime, parse_kelime_multi

# turkmen-fst modülünü import et (paradigma tablosu için)
_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
_FST_DIR = os.path.join(_BASE_DIR, "turkmen-fst")
if _FST_DIR not in sys.path:
    sys.path.insert(0, _FST_DIR)

from turkmen_fst.lexicon import Lexicon
from turkmen_fst.generator import MorphologicalGenerator

# Global generator instance
_lexicon = Lexicon()
_dict_path = os.path.join(_FST_DIR, "data", "turkmence_sozluk.txt")
if os.path.exists(_dict_path):
    _lexicon.load(_dict_path)
_generator = MorphologicalGenerator(_lexicon)

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():
    """Ana sayfa: isim/fiil çekimi ve parse işlemleri."""

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

    # Kullanıcı seçimlerini koruma (form geri doldurmak için)
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
            # Çoklu sonuç al
            multi = parse_kelime_multi(root)
            if multi.get("basarili") and multi.get("sonuclar"):
                # İlk sonucu ana parse_result olarak göster
                parse_result = multi["sonuclar"][0]
                # Birden fazla sonuç varsa hepsini gönder
                if len(multi["sonuclar"]) > 1:
                    parse_results_all = multi["sonuclar"]
            else:
                # Tek sonuç moduna düş
                parse_result = parse_kelime(root)

        # --- Paradigma tablosu ---
        elif action == 'paradigma' and root:
            paradigma_type = request.form.get('paradigma_type', 'noun')
            paradigma_data = _build_paradigma(root, paradigma_type)

        # --- Çekimleme işlemi ---
        elif action == 'cekimle':
            if mode == 'isim':
                # İsim çekimi parametreleri
                s_code = request.form.get('sayi')
                i_code = request.form.get('iyelik')
                h_code = request.form.get('hal', 'H1')

                # Seçimleri koru
                selected_sayi = s_code or ""
                selected_iyelik = i_code or ""
                selected_hal = h_code or "H1"

                if root:
                    results_list, is_dual = analyze(root, s_code, i_code, h_code)
                    if is_dual:
                        dual_results = results_list
                    # İlk sonucu her durumda result/final_word'e ata
                    result = results_list[0]["parts"]
                    final_word = results_list[0]["final_word"]

            else:
                # Fiil çekimi parametreleri
                zaman_kodu = request.form.get('zaman', '').strip().upper()
                sahis_kodu = request.form.get('sahis', '').strip().upper()
                olumsuz = request.form.get('olumsuz') == 'on'

                # Seçimleri koru
                selected_zaman = zaman_kodu
                selected_sahis = sahis_kodu
                selected_olumsuz = olumsuz

                if root and zaman_kodu and sahis_kodu:
                    parts, final_word = analyze_verb(root, zaman_kodu, sahis_kodu, olumsuz)
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


# ==============================================================================
#  REST API ENDPOINT'LERİ (/api/...)
# ==============================================================================

from turkmen_fst.analyzer import MorphologicalAnalyzer
_analyzer = MorphologicalAnalyzer(_lexicon)

# Tokenizer
_WORD_RE = re.compile(r"[a-zA-ZçÇäÄöÖüÜňŇýÝşŞžŽîÎ'-]+", re.UNICODE)

def _tokenize(text):
    return [{"word": m.group(), "start": m.start(), "end": m.end()}
            for m in _WORD_RE.finditer(text)]

def _edit_distance(a, b):
    if len(a) < len(b):
        return _edit_distance(b, a)
    if len(b) == 0:
        return len(a)
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a):
        curr = [i + 1]
        for j, cb in enumerate(b):
            cost = 0 if ca == cb else 1
            curr.append(min(curr[j] + 1, prev[j + 1] + 1, prev[j] + cost))
        prev = curr
    return prev[-1]

def _find_similar_roots(word, max_distance=2, max_results=10):
    w = word.lower()
    wlen = len(w)
    candidates = []
    for key in _lexicon._entries:
        if abs(len(key) - wlen) > max_distance:
            continue
        dist = _edit_distance(w, key)
        if 0 < dist <= max_distance:
            candidates.append((dist, key))
    candidates.sort()
    return [c[1] for c in candidates[:max_results]]

def _generate_suggestions(wrong_word, max_suggestions=5):
    multi = _analyzer.parse(wrong_word)
    if multi.success and any(r.word_type != "unknown" for r in multi.results):
        return []
    return _find_similar_roots(wrong_word, max_distance=2, max_results=max_suggestions)

def _format_morphemes(morphemes, possessive=None):
    result = []
    for m in (morphemes or []):
        if isinstance(m, dict):
            result.append({
                "morpheme": m.get("morpheme", ""),
                "type": m.get("type", ""),
                "code": m.get("code", ""),
            })
        elif isinstance(m, (list, tuple)) and len(m) >= 2:
            result.append({
                "type": m[0],
                "morpheme": m[1],
            })
    return result


@app.route('/api/health', methods=['GET'])
def api_health():
    """API sağlık kontrolü."""
    entries = len(_lexicon._entries) if hasattr(_lexicon, '_entries') else 0
    return jsonify({"status": "ok", "lexicon_entries": entries})


@app.route('/api/generate/noun', methods=['POST'])
def api_generate_noun():
    """İsim çekimi API endpoint'i."""
    data = request.get_json(silent=True) or {}
    stem = data.get("stem", "").strip()
    if not stem:
        return jsonify({"error": "stem alanı zorunludur"}), 400

    plural = data.get("plural", False)
    possessive = data.get("possessive")
    poss_type = data.get("poss_type")
    case = data.get("case")

    result = _generator.generate_noun(stem, plural=plural,
                                       possessive=possessive,
                                       poss_type=poss_type,
                                       case=case)
    if not result.is_valid:
        return jsonify({"error": result.error}), 400

    return jsonify({
        "result": result.word,
        "breakdown": result.breakdown,
        "stem": result.stem,
        "morphemes": _format_morphemes(result.morphemes, possessive),
        "valid": True
    })


@app.route('/api/generate/verb', methods=['POST'])
def api_generate_verb():
    """Fiil çekimi API endpoint'i."""
    data = request.get_json(silent=True) or {}
    stem = data.get("stem", "").strip()
    tense = data.get("tense", "").strip()
    person = data.get("person", "").strip()
    negative = data.get("negative", False)

    if not stem or not tense or not person:
        return jsonify({"error": "stem, tense ve person alanları zorunludur"}), 400

    result = _generator.generate_verb(stem, tense, person, negative)
    if not result.is_valid:
        return jsonify({"error": result.error}), 400

    return jsonify({
        "result": result.word,
        "breakdown": result.breakdown,
        "stem": result.stem,
        "morphemes": _format_morphemes(result.morphemes),
        "valid": True
    })


@app.route('/api/analyze', methods=['POST'])
def api_analyze():
    """Morfolojik analiz (kelime çözümleme) API endpoint'i.

    Tek kelime: {"word": "kitabym"}
    Çoklu metin: {"text": "kitabymyza geldim"}
    """
    data = request.get_json(silent=True) or {}
    text = data.get("text", "").strip() or data.get("word", "").strip()
    if not text:
        return jsonify({"error": "word veya text alanı zorunludur"}), 400

    words = _tokenize(text)
    all_words = []
    for w in words:
        multi = _analyzer.parse(w["word"])
        results_list = []
        for r in multi.results:
            results_list.append({
                "stem": r.stem,
                "word_type": r.word_type,
                "breakdown": r.breakdown,
                "suffixes": r.suffixes,
                "meaning": r.meaning
            })
        all_words.append({
            "word": multi.original,
            "success": multi.success,
            "count": multi.count,
            "results": results_list
        })

    # Tek kelime gönderildiyse dizi yerine tek obje döndür
    if len(all_words) == 1:
        return jsonify(all_words[0])

    return jsonify({"words": all_words})


@app.route('/api/lexicon/<word>', methods=['GET'])
def api_lexicon(word):
    """Sözlük sorgusu API endpoint'i."""
    from turkmen_fst.lexicon import POS_DISPLAY
    entries = _lexicon.lookup(word)
    entry_list = []
    pos_display = None
    for entry in entries:
        entry_list.append({
            "word": entry.word,
            "pos": entry.pos,
            "features": entry.features
        })
        if pos_display is None:
            pos_display = POS_DISPLAY.get(entry.pos)

    return jsonify({
        "word": word,
        "found": len(entries) > 0,
        "entries": entry_list,
        "pos_display": pos_display
    })


@app.route('/api/spellcheck', methods=['POST'])
def api_spellcheck():
    """Yazım denetimi API endpoint'i."""
    data = request.get_json(silent=True) or {}
    text = data.get("text", "").strip()
    if not text:
        return jsonify({"error": "text alanı zorunludur"}), 400

    tokens = _tokenize(text)
    results = []
    error_count = 0

    for tok in tokens:
        w = tok["word"]
        multi = _analyzer.parse(w)
        is_correct = False
        analysis_str = None

        if multi.success and multi.results:
            for r in multi.results:
                if r.word_type != "unknown":
                    is_correct = True
                    analysis_str = r.breakdown
                    break

        suggestions = []
        if not is_correct:
            error_count += 1
            suggestions = _generate_suggestions(w)

        results.append({
            "word": w,
            "correct": is_correct,
            "start": tok["start"],
            "end": tok["end"],
            "suggestions": suggestions,
            "analysis": analysis_str
        })

    return jsonify({
        "text": text,
        "word_count": len(tokens),
        "error_count": error_count,
        "results": results
    })


@app.route('/api/paradigm', methods=['POST'])
def api_paradigm():
    """Paradigma tablosu API endpoint'i."""
    data = request.get_json(silent=True) or {}
    stem = data.get("stem", "").strip()
    ptype = data.get("type", "noun")
    if not stem:
        return jsonify({"error": "stem alanı zorunludur"}), 400

    result = _build_paradigma(stem, ptype)
    if result is None:
        return jsonify({"error": f"Geçersiz tür: '{ptype}'"}), 400
    return jsonify(result)


if __name__ == '__main__':
    app.run(debug=True)

