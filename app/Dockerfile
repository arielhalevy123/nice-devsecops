# ---------- builder: בונה wheels בלבד ----------
FROM python:3.11-slim AS builder
ENV PIP_NO_CACHE_DIR=1
WORKDIR /app
COPY requirements.txt .
RUN apt-get update && apt-get install -y --no-install-recommends build-essential \
 && python -m pip install --upgrade pip setuptools wheel \
 && pip wheel --no-cache-dir --wheel-dir /wheels -r requirements.txt \
 && rm -rf /var/lib/apt/lists/*

# ---------- runtime: קל ומהיר ----------
FROM python:3.11-slim
ENV PYTHONUNBUFFERED=1
ENV TESSDATA_PREFIX=/usr/share/tesseract-ocr/5/tessdata
WORKDIR /app

# תלות ריצה בלבד + מודלי עברית/אנגלית
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr tesseract-ocr-heb tesseract-ocr-eng \
    libjpeg62-turbo zlib1g libtiff6 libpng16-16 libwebp7 \
 && rm -rf /var/lib/apt/lists/*

# קבצי אפליקציה
COPY . /app

# התקנת התלויות מפורקות (ללא קומפילציה)
COPY --from=builder /wheels /wheels
RUN pip install --no-index --find-links=/wheels -r requirements.txt \
 && rm -rf /wheels

# תיקיות נתונים
RUN mkdir -p /app/uploads /app/data

EXPOSE 5000
CMD ["python", "app.py"]