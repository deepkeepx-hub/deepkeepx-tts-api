# ==========================================
# Stage 1: Download models using a pure CPU environment
# This completely prevents CUDA initialization errors on GitHub Actions
# ==========================================
FROM python:3.11-slim AS model_downloader

WORKDIR /app

# Install CPU-only PyTorch specifically for downloading
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pre-install spacy model
RUN pip install --no-cache-dir spacy && \
    pip install --no-cache-dir https://hf-mirror.com/spacy/en_core_web_sm/resolve/main/en_core_web_sm-any-py3-none-any.whl

# Set HuggingFace mirror and cache directory
ENV HF_ENDPOINT=https://hf-mirror.com
ENV HF_HOME=/root/.cache/huggingface

# Download the models
RUN python -c "from kokoro import KPipeline; KPipeline(lang_code='a'); KPipeline(lang_code='z')"


# ==========================================
# Stage 2: Final Production Image
# ==========================================
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
RUN pip install --no-cache-dir spacy && \
    pip install --no-cache-dir https://hf-mirror.com/spacy/en_core_web_sm/resolve/main/en_core_web_sm-any-py3-none-any.whl

# 4. Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Security setup (non-root user)
RUN useradd -m -u 1000 appuser && \
    mkdir -p /app/data && \
    chown -R appuser:appuser /app

# 6. Copy the pre-downloaded models from Stage 1
# Create the cache directory first, then copy and assign permissions
RUN mkdir -p /home/appuser/.cache
COPY --from=model_downloader --chown=appuser:appuser /root/.cache/huggingface /home/appuser/.cache/huggingface

# 7. Switch to non-root user and set environment variables
USER appuser
ENV HOME=/home/appuser
ENV HF_HOME=/home/appuser/.cache/huggingface
# Set offline mode since models are now physically inside the image
ENV HF_HUB_OFFLINE=1

# 8. Copy source code
COPY --chown=appuser:appuser . .

EXPOSE 8080
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]