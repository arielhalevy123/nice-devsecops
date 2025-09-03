FROM python:3.10-slim

# התקנות מערכת להפעלת tesseract ו-pdf2image
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    poppler-utils \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    libjpeg-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# תיקיית העבודה
WORKDIR /app

# העתקת כל הקבצים
COPY . /app

# התקנת ספריות פייתון
RUN pip install --no-cache-dir -r requirements.txt

# פתיחת פורט 5000
EXPOSE 5000

# הרצת האפליקציה
CMD ["python", "app.py"]