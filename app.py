from flask import Flask, render_template, request
from morphology import analyze

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    final_word = ""
    
    if request.method == 'POST':
        root = request.form.get('root', '').strip()
        # Boş gelirse varsayılan değer ata
        s_code = request.form.get('sayi')
        i_code = request.form.get('iyelik')
        h_code = request.form.get('hal')
        
        if root:
            parts, final_word = analyze(root, s_code, i_code, h_code)
            result = parts
            
    return render_template('index.html', result=result, final_word=final_word)

if __name__ == '__main__':
    app.run(debug=True)