from flask import Flask, render_template, request
from morphology import analyze, analyze_verb
from parser import parse_kelime

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    final_word = ""
    root_word = ""
    mode = request.form.get('mode', 'isim')  # 'isim' veya 'fiil'
    action = request.form.get('action', 'cekimle')  # 'cekimle' veya 'parse'
    
    # Parse sonucu için
    parse_result = None
    
    # Dual (eş sesli) sonuç
    is_dual = False
    dual_results = None
    
    # Seçimleri korumak için değişkenler
    selected_sayi = ""
    selected_iyelik = ""
    selected_hal = "H1"
    selected_zaman = ""
    selected_sahis = ""
    selected_olumsuz = False
    
    if request.method == 'POST':
        root = request.form.get('root', '').strip()
        root_word = root
        
        # Parse işlemi - otomatik isim/fiil tanıma
        if action == 'parse':
            if root:
                parse_result = parse_kelime(root)
        
        # Çekimleme işlemi
        elif action == 'cekimle':
            if mode == 'isim':
                # İsim çekimi
                s_code = request.form.get('sayi')
                i_code = request.form.get('iyelik')
                h_code = request.form.get('hal', 'H1')
                
                # Seçimleri koru
                selected_sayi = s_code if s_code else ""
                selected_iyelik = i_code if i_code else ""
                selected_hal = h_code if h_code else "H1"
                
                if root:
                    results_list, is_dual = analyze(root, s_code, i_code, h_code)
                    if is_dual:
                        dual_results = results_list
                        # İlk sonucu varsayılan olarak göster
                        result = results_list[0]["parts"]
                        final_word = results_list[0]["final_word"]
                    else:
                        result = results_list[0]["parts"]
                        final_word = results_list[0]["final_word"]
            else:
                # Fiil çekimi
                zaman_kodu = request.form.get('zaman', '').strip().upper()
                sahis_kodu = request.form.get('sahis', '').strip().upper()
                olumsuz = request.form.get('olumsuz') == 'on'
                
                # Seçimleri koru
                selected_zaman = zaman_kodu
                selected_sahis = sahis_kodu
                selected_olumsuz = olumsuz
                
                if root and zaman_kodu and sahis_kodu:
                    parts, final_word = analyze_verb(root, zaman_kodu, sahis_kodu, olumsuz)
                    if parts:
                        # Hata kontrolü - parts'ta Hata tipi varsa final_word boş kalmalı
                        if parts[0].get("type") == "Hata":
                            result = parts
                            final_word = ""
                        elif final_word:
                            result = parts
                        else:
                            result = [{"text": "Geçersiz kodlar veya kök kelime.", "type": "Hata", "code": "HATA"}]
                            final_word = ""
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
