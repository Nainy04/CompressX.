from flask import Flask, render_template, request, send_file, redirect, url_for
import os
from zipfile import ZipFile
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Configure upload and compressed directories
UPLOAD_FOLDER = 'uploads'
COMPRESSED_FOLDER = 'compressed'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['COMPRESSED_FOLDER'] = COMPRESSED_FOLDER


os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(COMPRESSED_FOLDER, exist_ok=True)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return 'No file part'
    file_allowed =['png','jpeg','txt']
    file = request.files['file']
    if file.filename == '':
        return 'No selected file'
    
    if file:
        filename = secure_filename(file.filename)
        extention = filename.split
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Create a ZIP file
        # using zip for now but hear will be actual compresing algorithm
        
        zip_filename = f"{filename}.zip"
        zip_filepath = os.path.join(app.config['COMPRESSED_FOLDER'], zip_filename)
        with ZipFile(zip_filepath, 'w') as zipf:
            zipf.write(filepath, filename)

        return redirect(url_for('download', filename=zip_filename))

@app.route('/download/<filename>')
def download(filename):
    return send_file(os.path.join(app.config['COMPRESSED_FOLDER'], filename), as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
