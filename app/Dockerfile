# ---------- builder: בונים Tesseract/Leptonica בלי openjpeg + wheels ----------
FROM python:3.11-slim AS builder

ARG DEBIAN_FRONTEND=noninteractive
WORKDIR /w

# כלי build ותלויות לפיתוח (לכילוף בזמן ריצה לא נצטרך את זה)
RUN apt-get update && apt-get install -y --no-install-recommends \
    git curl ca-certificates \
    build-essential autoconf automake libtool pkg-config cmake \
    libpng-dev libjpeg62-turbo-dev zlib1g-dev libtiff-dev libwebp-dev \
 && rm -rf /var/lib/apt/lists/*

# --- Leptonica (בלי openjpeg) ---
# גרסה יציבה (אפשר לשנות אם תרצה)
ENV LEPT_VER=1.84.1
RUN curl -L -o leptonica.tar.gz https://github.com/DanBloomberg/leptonica/archive/refs/tags/$LEPT_VER.tar.gz \
 && tar -xzf leptonica.tar.gz && rm leptonica.tar.gz \
 && cd leptonica-$LEPT_VER \
 && ./autobuild && ./configure --prefix=/usr/local --without-openjpeg \
 && make -j"$(nproc)" && make install

# --- Tesseract ---
# תלוי רק ב-leptonica; אין תלות ב-openjpeg
ENV TESSERACT_VER=5.4.0
RUN curl -L -o tesseract.tar.gz https://github.com/tesseract-ocr/tesseract/archive/refs/tags/$TESSERACT_VER.tar.gz \
 && tar -xzf tesseract.tar.gz && rm tesseract.tar.gz \
 && cd tesseract-$TESSERACT_VER \
 && ./autogen.sh \
 && PKG_CONFIG_PATH=/usr/local/lib/pkgconfig ./configure --prefix=/usr/local \
 && make -j"$(nproc)" && make install && ldconfig

# קבצי שפה (fast = מהיר; אפשר להחליף ל-best)
RUN mkdir -p /usr/local/share/tessdata \
 && curl -L -o /usr/local/share/tessdata/eng.traineddata https://github.com/tesseract-ocr/tessdata_fast/raw/main/eng.traineddata \
 && curl -L -o /usr/local/share/tessdata/heb.traineddata https://github.com/tesseract-ocr/tessdata_fast/raw/main/heb.traineddata \
 && curl -L -o /usr/local/share/tessdata/osd.traineddata https://github.com/tesseract-ocr/tessdata_fast/raw/main/osd.traineddata

# Python wheels
COPY requirements.txt /w/requirements.txt
RUN python -m pip install --upgrade pip setuptools wheel \
 && pip wheel --no-cache-dir -r /w/requirements.txt -w /wheels

# ---------- runtime: רק תלויות הרצה (ללא libopenjp2) ----------
FROM python:3.11-slim

ARG DEBIAN_FRONTEND=noninteractive
ENV LD_LIBRARY_PATH=/usr/local/lib
WORKDIR /app

# תלויות דינמיות קלות לתמונות – בלי openjpeg
RUN apt-get update && apt-get install -y --no-install-recommends \
    libjpeg62-turbo zlib1g libtiff6 libpng16-16 libwebp7 \
 && rm -rf /var/lib/apt/lists/*

# מעתיקים את tesseract+leptonica שנבנו
COPY --from=builder /usr/local /usr/local

# אפליקציה + wheels
COPY . /app
COPY --from=builder /wheels /wheels
RUN pip install --no-cache-dir /wheels/*

EXPOSE 5000
CMD ["python", "app.py"]