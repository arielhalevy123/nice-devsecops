# --- stage קטן לבניית OpenJPEG מתוקן ---
FROM debian:bookworm-slim AS oj-builder
ARG DEBIAN_FRONTEND=noninteractive
ARG OPENJPEG_VER=2.5.4
RUN apt-get update && apt-get install -y --no-install-recommends \
      build-essential cmake curl ca-certificates \
  && curl -L -o openjpeg.tar.gz https://github.com/uclouvain/openjpeg/archive/refs/tags/v${OPENJPEG_VER}.tar.gz \
  && tar -xzf openjpeg.tar.gz && rm openjpeg.tar.gz \
  && cmake -S openjpeg-${OPENJPEG_VER} -B build \
        -DCMAKE_BUILD_TYPE=Release \
        -DBUILD_SHARED_LIBS=ON \
        -DBUILD_CODEC=OFF -DBUILD_MJ2=OFF -DBUILD_JPIP=OFF -DBUILD_JPWL=OFF -DBUILD_TESTS=OFF -DBUILD_DOC=OFF \
        -DCMAKE_INSTALL_PREFIX=/usr/local \
  && cmake --build build -j"$(nproc)" --target install

# --- ה-runtime שלך (כפי שהוא היום) ---
FROM python:3.11-slim
ENV PYTHONUNBUFFERED=1
ENV TESSDATA_PREFIX=/usr/share/tesseract-ocr/5/tessdata
WORKDIR /app

# Tesseract + תלויות (ישאירו את libopenjp2-7, אבל נדרוס אותה מיד אח״כ)
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr tesseract-ocr-heb tesseract-ocr-eng \
    libjpeg62-turbo zlib1g libtiff6 libpng16-16 libwebp7 \
 && rm -rf /var/lib/apt/lists/*

# ⬇️ להחליף את libopenjp2.so.7 הבעייתית בגרסה מתוקנת
COPY --from=oj-builder /usr/local/lib/libopenjp2.so* /usr/local/lib/
RUN ldconfig

# שאר השלבים שלך...
COPY . /app
COPY --from=builder /wheels /wheels
RUN pip install --no-index --find-links=/wheels -r requirements.txt && rm -rf /wheels
RUN mkdir -p /app/uploads /app/data
EXPOSE 5000
CMD ["python", "app.py"]