from flask import Flask, render_template, request, make_response
import pdfkit
import os
import base64
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Caminho para wkhtmltopdf
config = pdfkit.configuration(
    wkhtmltopdf=r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
)

UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def formulario():
    return render_template('form.html')

@app.route('/gerar', methods=['POST'])
def gerar_pdf():
    dados = request.form.to_dict()
    foto = request.files.get('foto')
    foto_base64 = None

    if foto and foto.filename != '':
        filename = secure_filename(foto.filename)
        foto_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        foto.save(foto_path)

        # Converte a imagem para base64
        with open(foto_path, 'rb') as img_file:
            encoded = base64.b64encode(img_file.read()).decode('utf-8')
            mime_type = 'image/jpeg' if filename.lower().endswith(('jpg', 'jpeg')) else 'image/png'
            foto_base64 = f"data:{mime_type};base64,{encoded}"

        os.remove(foto_path)

    # Gera o HTML com a imagem embutida
    rendered = render_template('resume_template.html', dados=dados, foto_url=foto_base64)
    pdf = pdfkit.from_string(rendered, False, configuration=config)

    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=curriculo.pdf'
    return response

if __name__ == '__main__':
    app.run(debug=True)
