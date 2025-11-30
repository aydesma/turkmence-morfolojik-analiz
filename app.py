from flask import Flask, render_template, request
from morphology import analyze, analyze_verb

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    final_word = ""
    root_word = ""
    mode = request.form.get('mode', 'isim')  # 'isim' veya 'fiil'
    
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
                parts, final_word = analyze(root, s_code, i_code, h_code)
                result = parts
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
                         selected_sayi=selected_sayi,
                         selected_iyelik=selected_iyelik,
                         selected_hal=selected_hal,
                         selected_zaman=selected_zaman,
                         selected_sahis=selected_sahis,
                         selected_olumsuz=selected_olumsuz)

if __name__ == '__main__':
    app.run(debug=True)
