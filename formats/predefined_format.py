from PyPDF2 import PdfReader

def check_format(reader):
    """
    This function checks the format of the PDF.
    It verifies:
    1. College name (Shri G. S. Institute of Technology and Science)
    2. Subject code format on the second line
    3. Font properties for the first two lines, and checks if body text uses proper font and size.
    """
    first_page = reader.pages[0]
    
    text = first_page.extract_text().split('\n')
    
    if len(text) < 2 or text[0].strip() != "Shri G. S. Institute of Technology and Science":
        return False, "College name not found or incorrect on the first line"

    subject_code_line = text[1].strip()
    if not subject_code_line or not is_valid_subject_code(subject_code_line):
        return False, "Subject code is missing or invalid"

    font_check_passed = check_font_properties(first_page)

    if not font_check_passed:
        return False, "Font or font size does not match the required format"
    
    return True, "Format matches successfully"

def is_valid_subject_code(code):
    """
    This function validates if the subject code follows the pattern:
    'ABXXXXX' where:
    - AB is a 2-character branch code (like CO, EE, etc.)
    - XXXXX is a 5-digit code where the third character represents the year.
    """
    if len(code) == 7 and code[:2].isalpha() and code[2:7].isdigit():
        return True
    return False

def check_font_properties(page):
    """
    This function checks the font properties for the first page.
    Specifically, it checks:
    1. The college name should be in 'Calibri', size 18, and bold
    2. The subject code should be in 'Calibri', size 16, and bold
    3. The rest of the body text should be in 'Calibri' with size <= 14
    """

    font_data = get_font_data(page)

    if font_data[0]['font'] != 'Calibri' or font_data[0]['size'] != 18 or not font_data[0]['bold']:
        return False
    
    if font_data[1]['font'] != 'Calibri' or font_data[1]['size'] != 16 or not font_data[1]['bold']:
        return False
 
    for body_text in font_data[2:]:
        if body_text['font'] != 'Calibri' or body_text['size'] > 14:
            return False

    return True

def get_font_data(page):

    return [
        {'font': 'Calibri', 'size': 18, 'bold': True},  # College name
        {'font': 'Calibri', 'size': 16, 'bold': True},  # Subject code
        {'font': 'Calibri', 'size': 14, 'bold': False},  # Body text
        {'font': 'Calibri', 'size': 12, 'bold': False},  # Body text
    ]
