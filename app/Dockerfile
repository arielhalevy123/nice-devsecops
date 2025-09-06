# ---------- 1) Build Python wheels ----------
FROM python:3.11-slim AS wheels
ENV PIP_NO_CACHE_DIR=1
WORKDIR /app
COPY requirements.txt .
RUN python -m pip install --upgrade pip setuptools wheel \
 && pip wheel --no-cache-dir --wheel-dir /wheels -r requirements.txt

# ---------- 2) Runtime image with secure OpenJPEG & Tesseract ----------
FROM python:3.11-slim

# סביבת עבודה
ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    TESSDATA_PREFIX=/usr/share/tesseract-ocr/5/tessdata \
    OPENJPEG_VER=2.5.4 \
    DEBIAN_FRONTEND=noninteractive

WORKDIR /app

# נוסיף מקור ל-unstable ונעשה pin כך שרק libopenjp2-7 יבוא משם
RUN set -eux; \
    echo 'deb http://deb.debian.org/debian unstable main' > /etc/apt/sources.list.d/unstable.list; \
    printf 'Package: *\nPin: release a=unstable\nPin-Priority: 100\n' > /etc/apt/preferences.d/99-unstable; \
    printf 'Package: libopenjp2-7\nPin: release a=unstable\nPin-Priority: 1001\n' > /etc/apt/preferences.d/99-libopenjp2; \
    \
    apt-get update; \
    # תלויות ריצה ל-Tesseract (ללא openjpeg הישנה – ניטפל בה מיד אחרי זה)
    apt-get install -y --no-install-recommends \
        tesseract-ocr tesseract-ocr-heb tesseract-ocr-eng \
        libjpeg62-turbo zlib1g libtiff6 libpng16-16 libwebp7 ca-certificates curl; \
    \
    # ננסה קודם לשדרג את libopenjp2-7 לגרסה מתוקנת (2.5.4) מ־unstable
    if ! apt-get install -y -t unstable 'libopenjp2-7=2.5.4-*'; then \
        echo '*** Falling back to building OpenJPEG from source (runtime will be safe) ***'; \
        apt-get install -y --no-install-recommends build-essential cmake; \
        curl -fsSL -o /tmp/openjpeg.tar.gz \
          "https://codeload.github.com/uclouvain/openjpeg/tar.gz/refs/tags/v${OPENJPEG_VER}"; \
        mkdir -p /tmp/oj && tar -xzf /tmp/openjpeg.tar.gz -C /tmp/oj --strip-components=1; \
        cmake -S /tmp/oj -B /tmp/oj-build \
              -DCMAKE_BUILD_TYPE=Release \
              -DBUILD_SHARED_LIBS=ON \
              -DBUILD_CODEC=OFF -DBUILD_MJ2=OFF -DBUILD_JPIP=OFF -DBUILD_JPWL=OFF \
              -DBUILD_TESTS=OFF -DBUILD_DOC=OFF \
              -DCMAKE_INSTALL_PREFIX=/usr/local; \
        cmake --build /tmp/oj-build -j"$(nproc)" --target install; \
        rm -rf /tmp/openjpeg.tar.gz /tmp/oj /tmp/oj-build; \
        # נחליף את הספרייה המערכתית בליב החדשה ונשאיר את החבילה הרשומה (כדי לא לשבור תלויות)
        if [ -f /usr/lib/x86_64-linux-gnu/libopenjp2.so.7 ]; then \
          dpkg-divert --quiet --local --rename \
            --divert /usr/lib/x86_64-linux-gnu/libopenjp2.so.7.debian \
            --add /usr/lib/x86_64-linux-gnu/libopenjp2.so.7 || true; \
          ln -sf /usr/local/lib/libopenjp2.so.7 /usr/lib/x86_64-linux-gnu/libopenjp2.so.7; \
        fi; \
        ldconfig; \
        # ניקוי כלי בנייה
        apt-get purge -y --auto-remove build-essential cmake || true; \
    else \
        # אם הותקנה 2.5.4 בהצלחה – ננעל אותה כדי שלא תרדוג במהלך התקנות אחרות
        apt-mark hold libopenjp2-7; \
    fi; \
    rm -rf /var/lib/apt/lists/*

# קבצי האפליקציה ותלויות פייתון
COPY . /app
COPY --from=wheels /wheels /wheels
RUN pip install --no-index --find-links=/wheels -r requirements.txt && rm -rf /wheels

# תיקיות עבודה לקבצים שהאפליקציה שומרת
RUN mkdir -p /app/uploads /app/data \
 && adduser --system --home /nonexistent --ingroup nogroup --disabled-login appuser \
 && chown -R appuser:nogroup /app

# הקשחות בסיסיות
USER appuser
EXPOSE 5000
# HEALTHCHECK (אופציונלי – בטל אם אין לך /health)
# HEALTHCHECK --interval=30s --timeout=5s --retries=3 CMD curl -fsS http://127.0.0.1:5000/health || exit 1

CMD ["python", "app.py"]