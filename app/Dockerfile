# ---------- builder: בונה Leptonica (ללא openjpeg) + Tesseract + wheels ----------
FROM python:3.11-slim AS builder
ARG DEBIAN_FRONTEND=noninteractive
ENV LD_LIBRARY_PATH=/usr/local/lib
WORKDIR /w

# כלי build ותלויות לקומפילציה
RUN apt-get update && apt-get install -y --no-install-recommends \
    git curl ca-certificates \
    build-essential autoconf automake libtool pkg-config cmake \
    libpng-dev libjpeg62-turbo-dev zlib1g-dev libtiff-dev libwebp-dev \
 && rm -rf /var/lib/apt/lists/*

# --- Leptonica (CMake; ללא OpenJPEG) ---
ENV LEPT_VER=1.84.1
ENV PKG_CONFIG_PATH=/usr/local/lib/pkgconfig:$PKG_CONFIG_PATH
RUN curl -L -o leptonica.tar.gz https://github.com/DanBloomberg/leptonica/archive/refs/tags/${LEPT_VER}.tar.gz \
 && tar -xzf leptonica.tar.gz && rm leptonica.tar.gz \
 && cmake -S leptonica-${LEPT_VER} -B leptonica-build \
      -DCMAKE_BUILD_TYPE=Release \
      -DCMAKE_INSTALL_PREFIX=/usr/local \
      -DBUILD_SHARED_LIBS=ON \
      -DOPENJPEG_SUPPORT=OFF \
      -DSW_BUILD=OFF \
 && cmake --build leptonica-build -j"$(nproc)" \
 && cmake --install leptonica-build \
 && ldconfig \
 # tesseract מחפש lept.pc – נוסיף קישור סימבולי
 && ln -sf /usr/local/lib/pkgconfig/lept_Release.pc /usr/local/lib/pkgconfig/lept.pc
# --- Tesseract (מהמקור) ---
ENV TESSERACT_VER=5.4.0
RUN curl -L -o tesseract.tar.gz https://github.com/tesseract-ocr/tesseract/archive/refs/tags/${TESSERACT_VER}.tar.gz \
 && tar -xzf tesseract.tar.gz && rm tesseract.tar.gz \
 && cd tesseract-${TESSERACT_VER} \
 && ./autogen.sh \
 && PKG_CONFIG_PATH=/usr/local/lib/pkgconfig ./configure --prefix=/usr/local \
 && make -j"$(nproc)" && make install && ldconfig

# מודלי שפה (heb + eng + osd)
RUN mkdir -p /usr/local/share/tessdata \
 && curl -L -o /usr/local/share/tessdata/eng.traineddata https://github.com/tesseract-ocr/tessdata_fast/raw/main/eng.traineddata \
 && curl -L -o /usr/local/share/tessdata/heb.traineddata https://github.com/tesseract-ocr/tessdata_fast/raw/main/heb.traineddata \
 && curl -L -o /usr/local/share/tessdata/osd.traineddata https://github.com/tesseract-ocr/tessdata_fast/raw/main/osd.traineddata

# Wheels של פייתון
COPY requirements.txt /w/requirements.txt
RUN python -m pip install --upgrade pip setuptools wheel \
 && pip wheel --no-cache-dir -r /w/requirements.txt -w /wheels

# ---------- runtime: מינימום תלות ריצה, בלי openjpeg/poppler ----------
FROM python:3.11-slim
ARG DEBIAN_FRONTEND=noninteractive
ENV LD_LIBRARY_PATH=/usr/local/lib
ENV TESSDATA_PREFIX=/usr/local/share/tessdata
ENV PYTHONUNBUFFERED=1
WORKDIR /app

# ספריות ריצה נדרשות ל-Pillow/Leptonica/Tesseract (ללא openjpeg וללא poppler-utils)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libjpeg62-turbo zlib1g libtiff6 libpng16-16 libwebp7 \
 && rm -rf /var/lib/apt/lists/*

# להעתיק את Tesseract/Leptonica מה-builder
COPY --from=builder /usr/local /usr/local

# קבצי האפליקציה + wheels
COPY . /app
COPY --from=builder /wheels /wheels
RUN pip install --no-cache-dir /wheels/*

# תיקיות נתונים
RUN mkdir -p /app/uploads /app/data

EXPOSE 5000
CMD ["python", "app.py"]