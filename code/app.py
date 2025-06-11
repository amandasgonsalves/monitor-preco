import os
from flask import Flask, render_template, request, jsonify, send_file
import pandas as pd
from main import GoogleShoppingScraper
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max-limit

# Ensure the upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'xlsx', 'xls'}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search_product', methods=['POST'])
def search_product():
    product_name = request.form.get('product_name')
    if not product_name:
        return jsonify({'error': 'Nome do produto não pode estar vazio'}), 400

    scraper = GoogleShoppingScraper()
    try:
        results = scraper.search_product(product_name)
        if results:
            filename = scraper.save_to_file(product_name, results)
            with open(filename, 'r', encoding='utf-8') as file:
                content = file.read()
            return jsonify({'results': content})
        else:
            return jsonify({'error': 'Nenhum resultado encontrado'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        scraper.close()

@app.route('/process_excel', methods=['POST'])
def process_excel():
    if 'file' not in request.files:
        return jsonify({'error': 'Nenhum arquivo enviado'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Nenhum arquivo selecionado'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Formato de arquivo não permitido. Use .xlsx ou .xls'}), 400

    try:
        # Save the uploaded file
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Read the Excel file
        df = pd.read_excel(filepath)
        
        if 'Produto' not in df.columns:
            return jsonify({'error': 'A planilha deve ter uma coluna chamada "nome"'}), 400

        # Process each product
        results = []
        scraper = GoogleShoppingScraper()
        
        try:
            for product_name in df['Produto'].dropna():
                print(f"Processando produto: {product_name}")
                search_results = scraper.search_product(product_name)
                if search_results:
                    filename = scraper.save_to_file(product_name, search_results)
                    with open(filename, 'r', encoding='utf-8') as file:
                        content = file.read()
                    results.append({
                        'product_name': product_name,
                        'content': content
                    })
        finally:
            scraper.close()

        return jsonify({'results': results})

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        # Clean up the uploaded file
        if os.path.exists(filepath):
            os.remove(filepath)

if __name__ == '__main__':
    app.run(debug=True)
