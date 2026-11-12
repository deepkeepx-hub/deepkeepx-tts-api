FROM python:3.11-slim

# 1. System dependencies
RUN apt-get update -o Acquire::Retries=5 && \
    apt-get install -y --no-install-recommends espeak-ng && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 2. Install PyTorch (CPU or GPU based on build argument)
ARG TARGET_DEVICE=cpu
RUN if [ "$TARGET_DEVICE" = "gpu" ]; then \
        pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cu121 --timeout 120 --retries 5 ; \
    else \
        pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu --timeout 120 --retries 5 ; \
    fi

# 3. Pre-install spacy and en_core_web_sm
# Try official source first (fast on GitHub Actions), fallback to hf-mirror (for local builds in China)
RUN pip install --no-cache-dir spacy && \
    (pip install --no-cache-dir https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.8.0/en_core_web_sm-3.8.0-py3-none-any.whl || \
     pip install --no-cache-dir https://hf-mirror.com/spacy/en_core_web_sm/resolve/main/en_core_web_sm-any-py3-none-any.whl)

# 4. Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Security setup (non-root user)
RUN useradd -m -u 1000 appuser && \
    mkdir -p /app/data && \
    chown -R appuser:appuser /app

USER appuser
ENV HOME=/home/appuser
ENV HF_HOME=/home/appuser/.cache/huggingface

# 6. Copy source code
COPY --chown=appuser:appuser . .

# 7. Download and pre-package models during build (Using HF mirror for stable download)
ENV HF_ENDPOINT=https://hf-mirror.com
RUN python -c "from kokoro import KPipeline; KPipeline(lang_code='a'); KPipeline(lang_code='z')"

EXPOSE 8080
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]