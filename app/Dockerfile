# ---------- builder: מתקין כלים לבנייה בלבד ----------
FROM python:3.11-slim AS builder
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY app/requirements.txt /app/requirements.txt

# נעלה גרסאות pip/setuptools כדי לסגור את ה-HIGH של setuptools
RUN python -m pip install --upgrade pip setuptools wheel \
 && pip wheel --no-cache-dir --wheel-dir /wheels -r requirements.txt

# ---------- runtime: רק מה שנחוץ להרצה ----------
FROM python:3.11-slim

# ספריות ריצה (לא חבילות dev)
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
COPY app /app

# מתקינים מתוך ה-wheels שנבנו בבילדר, בלי להשאיר קומפיילרים
COPY --from=builder /wheels /wheels
RUN pip install --no-cache-dir /wheels/*

EXPOSE 5000
CMD ["python", "app.py"]