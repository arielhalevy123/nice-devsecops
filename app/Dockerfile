# ---------- builder: כלים לבנייה בלבד ----------
FROM python:3.11-slim AS builder
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /w
# הקובץ נמצא ישירות בתוך app/, אז במסלול היחסי זה רק requirements.txt
COPY requirements.txt .
# סוגר פגיעויות של setuptools ומכין wheels
RUN python -m pip install --upgrade pip setuptools wheel \
 && pip wheel --no-cache-dir -r requirements.txt -w /wheels

# ---------- runtime: רק מה שנדרש להרצה ----------
FROM python:3.11-slim
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    poppler-utils \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    libjpeg62-turbo \
    zlib1g \
    libopenjp2-7 \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app
# כל קבצי האפליקציה (מתוך app/) נכנסים
COPY . /app
# מתקינים מה-wheels שנבנו בבילדר
COPY --from=builder /wheels /wheels
RUN pip install --no-cache-dir /wheels/*

EXPOSE 5000
CMD ["python", "app.py"]