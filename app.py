from flask import Flask, render_template, request, redirect, url_for
import os
import shutil
import fitz  # PyMuPDF for PDF processing

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

# Ensure upload and organized directories exist
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

if not os.path.exists('organized_pdfs'):
    os.makedirs('organized_pdfs')

# Allowed file extensions
ALLOWED_EXTENSIONS = {'pdf'}

# Check if uploaded file is a PDF
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def validate_and_extract_details(file_path):
    doc = fitz.open(file_path)
    
    if doc.page_count < 1:
        print("Returning: PDF is empty or invalid, None")
        return "The PDF is empty or invalid.", None

    page = doc[0]
    text = page.get_text("text").splitlines()
    doc.close()

    text = [line.strip() for line in text if line.strip()]
    
    print("Extracted text:", text)

    if len(text) < 7:
        print("Returning: PDF doesn't have enough lines, None")
        return "The PDF does not contain the expected number of lines for validation.", None

    college_name = "SHRI G.S. INSTITUTE OF TECHNOLOGY & SCIENCE,INDORE"
    if text[0].strip() != college_name:
        print("Returning: Incorrect college name, None")
        return "The college name is incorrect or improperly formatted.", None

    department_mapping = {
        "CO": "Computer Engineering",
        "EE": "Electrical Engineering",
        "ME": "Mechanical Engineering",
        "EC": "Electronics and Telecommunication Engineering"
    }
    department_name_line = text[1]
    subject_code = text[4].split(":")[0].strip()

    if len(subject_code) < 2 or subject_code[:2] not in department_mapping:
        print("Returning: Invalid subject code, None")
        return "Invalid or unrecognized subject code for department validation.", None
    
    department_name = f"DEPARTMENT OF {department_mapping[subject_code[:2]].upper()}"
    if department_name_line.strip() != department_name:
        print("Returning: Incorrect department name, None")
        return "The department name does not match the expected department based on the subject code.", None

    year_mapping = {
        '1': 'Ist',
        '2': 'IInd',
        '3': 'IIIrd',
        '4': 'IVth'
    }
    if len(subject_code) < 3 or subject_code[2] not in year_mapping:
        print("Returning: Invalid year, None")
        return "Invalid year detected in the subject code.", None
    
    year = year_mapping[subject_code[2]]
    program_year_line = text[2].strip()
    if not (program_year_line.startswith("B.TECH") or program_year_line.startswith("M.TECH")):
        print("Returning: Program missing or incorrect, None")
        return "The program (B.TECH/M.TECH) is missing or incorrectly formatted.", None
    if year not in program_year_line:
        print("Returning: Year mismatch, None")
        return "The year does not match the expected format (Ist/IInd/IIIrd/IVth)."

    if len(subject_code) < 4 or not subject_code[3].isdigit():
        print("Returning: Semester identifier invalid, None")
        return "The semester identifier is missing or not a valid number in the subject code."

    semester_number = int(subject_code[3])
    semester_type = "B" if semester_number % 2 != 0 else "A"
    expected_semester = f"SEMESTER- {semester_type}"
    if text[3].strip() != expected_semester:
        print("Returning: Incorrect semester info, None")
        return f"The semester information is incorrect. Expected {expected_semester}.", None

    if not subject_code.startswith(subject_code[:2]) or len(subject_code) != 7:
        print("Returning: Subject code format incorrect, None")
        return "The subject code format is incorrect. Expected format: ABXXXXX.", None

    course_objectives_found = any("COURSE OBJECTIVES" in line for line in text)
    course_outcomes_found = any("COURSE OUTCOMES" in line for line in text)

    if not course_objectives_found or not course_outcomes_found:
        print("Returning: Missing course objectives or outcomes, None")
        return "The PDF is missing 'Course Objectives' or 'Course Outcomes' headings.", None

    # Everything passed; return details
    details = {
        "department": department_mapping[subject_code[:2]],
        "year": year,
        "semester": semester_type
    }
    print("Returning: Validation successful, details:", details)
    return "PDF validated successfully!", details

# Organize the file into folders based on validation details
def organize_pdf(file_path, details):
    base_dir = 'organized_pdfs'
    department_folder = os.path.join(base_dir, details["department"])
    year_folder = os.path.join(department_folder, details["year"])
    semester_folder = os.path.join(year_folder, f"Semester-{details['semester']}")

    os.makedirs(semester_folder, exist_ok=True)
    shutil.move(file_path, os.path.join(semester_folder, os.path.basename(file_path)))

# Main page (upload form)
@app.route('/')
def index():
    message = request.args.get('message')
    return render_template('upload.html', message=message)

# Process the uploaded PDF
@app.route('/process', methods=['POST'])
def process_pdf():
    if 'file' not in request.files:
        return redirect(url_for('index', message="No file part found. Please upload a PDF."))
    
    file = request.files['file']
    if file.filename == '' or not allowed_file(file.filename):
        return redirect(url_for('index', message="Invalid file type. Only PDFs are allowed."))

    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(file_path)

    # Add logging here to track what's being returned
    validation_result, details = validate_and_extract_details(file_path)
    print("Validation Result:", validation_result)
    print("Details:", details)

    if details:
        organize_pdf(file_path, details)
        success_message = f'PDF validated and organized successfully in {details["department"]} -> {details["year"]} -> Semester-{details["semester"]}.'
        return redirect(url_for('index', message=success_message))
    else:
        return redirect(url_for('index', message=validation_result))


if __name__ == '__main__':
    app.run(debug=True)
