from flask import Flask, request, render_template, flash, redirect, url_for
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'ssip_print_vending_secret_2025'
app.config['UPLOAD_FOLDER'] = '/home/raspberry-pi/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB limit
app.config['TEMPLATES_FOLDER'] = '/home/raspberry-pi/Templates'

ALLOWED_EXTENSIONS = {'pdf', 'txt', 'doc', 'docx'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def create_uploads_folder():
    """Create uploads folder if it doesn't exist"""
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
        os.chmod(app.config['UPLOAD_FOLDER'], 0o755)

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    create_uploads_folder()
    
    if request.method == 'POST':
        # Get form data
        user_name = request.form.get('name', 'Unknown')
        user_email = request.form.get('email', 'No email')
        payment_code = request.form.get('payment_code', '')
        
        # Handle file upload
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
                
                # SSIP: Payment check (prototype - replace with real payment later)
                if payment_code == 'paid':  # Simple test - use 'paid' as payment code
                    # Future: subprocess.run(['lp', file_path])  # Printer command
                    flash(f'SUCCESS! {filename} uploaded by {user_name}. READY FOR PRINT. Saved: {file_path}')
                else:
                    flash(f'File {filename} received ({os.path.getsize(file_path)} bytes). Enter "paid" to simulate payment.')
                
                return render_template('upload.html', 
                                     success=True, 
                                     name=user_name, 
                                     filename=filename,
                                     file_size=os.path.getsize(file_path))
                
            except Exception as e:
                flash(f'Error saving file: {str(e)}')
        
        flash('Invalid file type. Only PDF, TXT, DOC, DOCX allowed.')
    
    return render_template('upload.html')

@app.route('/status')
def status():
    """Check uploaded files status"""
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
    print("=== SSIP PRINT VENDING MACHINE ===")
    print("Access: http://localhost:5000")
    print("Pi IP:", os.popen('hostname -I').read().strip())
    print("Templates folder:", app.config['TEMPLATES_FOLDER'])
    print("Uploads folder:", app.config['UPLOAD_FOLDER'])
    app.run(host='0.0.0.0', port=5000, debug=True)
