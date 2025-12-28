from flask import Flask, request, render_template, flash
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'ssip_print_vending_secret_2025'
app.config['UPLOAD_FOLDER'] = '/home/raspberry-pi/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

ALLOWED_EXTENSIONS = {'pdf', 'txt', 'doc', 'docx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def create_uploads_folder():
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
        os.chmod(app.config['UPLOAD_FOLDER'], 0o755)

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    create_uploads_folder()
    
    if request.method == 'POST':
        user_name = request.form.get('name', 'Unknown')
        user_email = request.form.get('email', 'No email')
        payment_code = request.form.get('payment_code', '')
        
        if 'file' not in request.files:
            flash('No file selected')
            return render_template('upload.html')
        
        file = request.files['file']
        if file.filename == '':
            flash('No file selected')
            return render_template('upload.html')
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            
            try:
                file.save(file_path)
                if payment_code == 'paid':
                    flash(f'SUCCESS! {filename} READY FOR PRINT. Saved: {file_path}')
                else:
                    flash(f'File {filename} received. Enter "paid" to simulate payment.')
                
                return render_template('upload.html', 
                                     success=True, 
                                     name=user_name, 
                                     filename=filename,
                                     file_size=os.path.getsize(file_path))
            except Exception as e:
                flash(f'Error: {str(e)}')
        
        flash('Invalid file type')
    
    return render_template('upload.html')

@app.route('/status')
def status():
    files = []
    if os.path.exists(app.config['UPLOAD_FOLDER']):
        for filename in os.listdir(app.config['UPLOAD_FOLDER']):
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            files.append({
                'name': filename,
                'size': os.path.getsize(filepath),
                'time': os.path.getmtime(filepath)
            })
    return render_template('status.html', files=files)

if __name__ == '__main__':
    create_uploads_folder()
    print("=== SSIP PRINT VENDING ===")
    print("Templates must be in: /home/raspberry-pi/Templates/")
    app.run(host='0.0.0.0', port=5000, debug=True)
