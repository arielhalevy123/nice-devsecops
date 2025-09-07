import os
import re
import pytesseract
import uuid
import urllib.parse
import json
from werkzeug.utils import secure_filename
import pypdfium2 as pdfium
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__, static_folder='frontend', static_url_path='') 
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
link_counter = 0

COUNTER_FILE = 'data/counter.txt'

def read_counter():
    try:
        with open(COUNTER_FILE, 'r') as f:
            return int(f.read())
    except:
        return 1321  # מספר ברירת מחדל אם הקובץ לא קיים או לא תקין

def save_counter(value):
    with open(COUNTER_FILE, 'w') as f:
        f.write(str(value))

def clean_date_string(date_str):
    try:
        parts = date_str.strip().split("/")
        if len(parts) != 3:
            return None

        day, month, year = parts
        if len(year) > 4:
            year = year[:4]

        day = day.zfill(2)
        month = month.zfill(2)
        fixed_date_str = f"{day}/{month}/{year}"

        parsed_date = datetime.strptime(fixed_date_str, "%d/%m/%Y")

        today = datetime.today()
        two_years_ago = today - timedelta(days=730)

        if not (two_years_ago <= parsed_date <= today):
            print(f"⚠️ תאריך מחוץ לטווח: {fixed_date_str}")
            return None

        if parsed_date < datetime(2023, 10, 7):
            print(f"❌ תאריך מוקדם מדי: {fixed_date_str}")
            return "TOO_EARLY"

        return parsed_date.strftime("%Y-%m-%d")

    except Exception as e:
        print(f"שגיאה בתיקון תאריך: {date_str} | {e}")
        return None

def pdf_pages_to_pil_images(pdf_path, scale=2):
    """
    רינדור עמודי PDF לתמונות PIL באמצעות pypdfium2 (ללא poppler/openjpeg).
    scale≈DPI/100, כלומר scale=2 ~ 200DPI.
    """
    pdf = pdfium.PdfDocument(pdf_path)
    for i in range(len(pdf)):
        page = pdf[i]
        pil_image = page.render(scale=scale).to_pil()
        yield pil_image

def extract_service_dates_from_pdf(path):
    text = ""
    # המרה לעמודים כ־תמונות עם pypdfium2 במקום pdf2image
    for img in pdf_pages_to_pil_images(path, scale=2):
        text += pytesseract.image_to_string(img, lang='heb+eng') + "\n"

    print("📄 טקסט שחולץ:\n", text)

    start_index = text.find("תאריך תחילה")
    if start_index != -1:
        text = text[start_index:]

    raw_dates = re.findall(r'\d{1,2}/\d{1,2}/\d{4}', text)

    dates = []
    for i, d in enumerate(raw_dates):
        if i < 2:  # דילוג על 4 התאריכים הראשונים
            continue
        fixed = clean_date_string(d)
        if fixed == "TOO_EARLY":
            return "TOO_EARLY"
        if fixed == "INVALID_RANGE":
            return "INVALID_RANGE"
        if fixed:
            dates.append(fixed)

    print("📆 תאריכים לאחר עיבוד:", dates)

    if len(dates) % 2 != 0:
        print(f"⚠️ מספר תאריכים אי זוגי ({len(dates)}), מתעלם מהראשון: {dates[0]}")
        dates = dates[1:]

    date_ranges = []
    for i in range(0, len(dates) - 1, 2):
        date_ranges.append((dates[i], dates[i + 1]))

    print("📊 זוגות תאריכים שנמצאו:", date_ranges)
    return date_ranges

def build_miluimnik_link(date_ranges, service_before, user_flags):
    formatted_ranges = []
    # שומר על הלוגיקה המקורית (גם אם הסדר נראה הפוך בקוד המקורי)
    for start, end in date_ranges:
        formatted_ranges.append({
            "startDate": start,
            "endDate": end,
            "id": str(uuid.uuid4())
        })

    query = {
        "serviceBefore": service_before,
        "dateRanges": formatted_ranges,
        **user_flags
    }

    encoded_query = urllib.parse.urlencode({
        k: json.dumps(v) if isinstance(v, list) else v
        for k, v in query.items()
    })

    return f"https://miluimnik.info/?{encoded_query}"

@app.route('/')
def serve_index():
    return send_from_directory('frontend', 'index.html')

@app.route('/generate-link', methods=['POST'])
def generate_link():
    if 'file' not in request.files:
        return jsonify({'error': 'לא נשלח קובץ'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'לא נבחר קובץ'}), 400

    if not file.filename.lower().endswith('.pdf'):
        return jsonify({'error': 'ניתן להעלות רק קובץ PDF'}), 400

    filename = f"{uuid.uuid4()}.pdf"
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)

    service_dates = extract_service_dates_from_pdf(file_path)

    try:
        os.remove(file_path)
    except Exception as e:
        print(f"שגיאה במחיקת קובץ זמני: {e}")

    if service_dates == "INVALID_RANGE":
        return jsonify({'error': 'הקובץ מכיל תאריכים לפני 07/10/2023. יש להעלות טופס 3010 עדכני.'}), 400
    
    if service_dates == "TOO_EARLY":
        return jsonify({'error': 'הקובץ מכיל תאריכים מוקדמים מ-07/10/2023. יש להעלות טופס 3010 עדכני עם שירות לאחר תאריך זה.'}), 400
   
    if not service_dates:
        return jsonify({'error': 'לא נמצאו תאריכי שירות בקובץ'}), 400
    
    service_before = request.form.get('serviceBefore', '0')
    user_flags = {
        "isCombat": str('isCombat' in request.form).lower(),
        "hasChildren": str('hasChildren' in request.form).lower(),
        "hasChildrenSpecial": str('hasChildrenSpecial' in request.form).lower(),
        "didVacationCancelled": str('didVacationCancelled' in request.form).lower(),
        "isOld": str('isOld' in request.form).lower(),
        "isStudent": str('isStudent' in request.form).lower(),
        "isIndependent": str('isIndependent' in request.form).lower()
    }
    link_counter = read_counter()
    link_counter += 1
    save_counter(link_counter)
    
    link = build_miluimnik_link(service_dates, service_before, user_flags)
    return jsonify({'link': link, 'counter': link_counter})

@app.after_request
def add_csp_header(response):
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; "
        "script-src 'self'; "
        "style-src 'self'; "
        "img-src 'self' data:; "
        "font-src 'self'; "
        "connect-src 'self'; "
        "object-src 'none'; "
        "base-uri 'self'; "
        "form-action 'self'; "
        "frame-ancestors 'none'; "
        "media-src 'self'; "
        "manifest-src 'self'; "
        "require-trusted-types-for 'script';"
    )
    response.headers['X-Frame-Options'] = 'DENY'
    return response
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)