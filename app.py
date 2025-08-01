from flask import Flask, render_template, request, make_response
import pdfkit
import os
import base64
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

# Criar a pasta de uploads se não existir
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Caminho do wkhtmltopdf (ajustado para Render e local)
wkhtmltopdf_path = os.getenv('WKHTMLTOPDF_PATH', r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe')
config = pdfkit.configuration(wkhtmltopdf=wkhtmltopdf_path)

@app.route('/')
def form():
    return render_template('form.html')

@app.route('/gerar', methods=['POST'])
def gerar():
    dados = request.form.to_dict()
    foto = request.files.get('foto')

    if foto:
        filename = secure_filename(foto.filename)
        foto_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        foto.save(foto_path)

        # Converter imagem para base64
        with open(foto_path, 'rb') as img_file:
            mime_type = 'image/jpeg' if filename.lower().endswith(('.jpg', '.jpeg')) else 'image/png'
            base64_img = base64.b64encode(img_file.read()).decode('utf-8')
            dados['foto_base64'] = f"data:{mime_type};base64,{base64_img}"
    else:
        dados['foto_base64'] = None

    # Gerar HTML com os dados
    rendered = render_template('resume_template.html', **dados)

    # Gerar PDF
    pdf = pdfkit.from_string(rendered, False, configuration=config)

    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename=curriculo.pdf'
    return response

if __name__ == '__main__':
    app.run(debug=True)
