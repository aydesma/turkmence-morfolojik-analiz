# -*- coding: utf-8 -*-
"""
Türkmen Morfolojik Analiz — Flask Web Uygulaması

Kullanıcıdan kök kelime ve çekim parametreleri alır,
morphology motorunu çağırır ve sonuçları template'e aktarır.
"""
from flask import Flask, render_template, request
from morphology import analyze, analyze_verb
from parser import parse_kelime, parse_kelime_multi

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
                           selected_sayi=selected_sayi,
                           selected_iyelik=selected_iyelik,
                           selected_hal=selected_hal,
                           selected_zaman=selected_zaman,
                           selected_sahis=selected_sahis,
                           selected_olumsuz=selected_olumsuz)


if __name__ == '__main__':
    app.run(debug=True)

