from flask import Flask, render_template, request, redirect, flash
import os
import shutil
from PyPDF2 import PdfReader
from formats.predefined_format import check_format  # Importing the new format checker

app = Flask(__name__)
app.secret_key = 'supersecretkey'

UPLOAD_FOLDER = 'uploads'
SEGREGATED_FOLDER = 'segregated_files'
ALLOWED_EXTENSIONS = {'pdf'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(SEGREGATED_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('No file part')
        return redirect('/')
    
    file = request.files['file']
    
    if file.filename == '':
        flash('No selected file')
        return redirect('/')
    
    if file and allowed_file(file.filename):
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(file_path)

        reader = PdfReader(file_path)

        format_passed, message = check_format(reader)
        
        if format_passed:

            flash('File uploaded and passed format check!')
            move_file_based_on_subject_code(reader, file_path, file.filename)
        else:
            flash(message)
        
        return redirect('/')

def move_file_based_on_subject_code(reader, file_path, filename):
    """
    This function extracts the subject code from the PDF, determines the corresponding
    branch and year, and moves the file into the appropriate year and branch folder.
    """
    first_page = reader.pages[0]
    text = first_page.extract_text().split('\n')
    subject_code = text[1].strip()

    branch = subject_code[:2] 
    year = subject_code[2] 

    branch_mapping = {
        'CO': 'Computer Engineering',
        'EE': 'Electrical Engineering',
        'IT': 'Information Technology',
        'ME': 'Mechanical Engineering',
        'CE': 'Civil Engineering',
        'EC': 'Electronics and Telecommunication Engineering'
    }

    year_mapping = {
        '1': 'First Year',
        '2': 'Second Year',
        '3': 'Third Year',
        '4': 'Fourth Year'
    }

    if branch in branch_mapping and year in year_mapping:

        target_folder = os.path.join(SEGREGATED_FOLDER, year_mapping[year], branch_mapping[branch])
        os.makedirs(target_folder, exist_ok=True)

        shutil.move(file_path, os.path.join(target_folder, filename))
        flash(f"File moved to {target_folder} successfully!")
    else:
        flash("Invalid subject code format or unsupported branch/year.")

if __name__ == '__main__':
    app.run(debug=True)
