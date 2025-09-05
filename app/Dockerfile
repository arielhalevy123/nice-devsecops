# ---------- builder: בניית wheels כדי להאיץ התקנה ----------
FROM python:3.11-slim AS builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /w
COPY requirements.txt /w/requirements.txt

# עדכון pip + בניית wheels (כולל setuptools מתוקן)
RUN python -m pip install --upgrade pip setuptools wheel \
 && pip wheel --no-cache-dir -r /w/requirements.txt -w /wheels

# ---------- runtime: תלות ריצה בלבד ----------
FROM python:3.11-slim

# רק מה שנדרש בפועל ל-PIL ול-Tesseract (ללא poppler וללא libopenjp2-7)
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    libjpeg62-turbo \
    zlib1g \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app
# קבצי האפליקציה
COPY . /app

# התקנה מתוך wheels שנבנו בשכבת ה-build
COPY --from=builder /wheels /wheels
RUN pip install --no-cache-dir /wheels/*

EXPOSE 5000
CMD ["python", "app.py"]