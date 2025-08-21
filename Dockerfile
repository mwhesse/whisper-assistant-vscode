FROM python:3.10.13-slim

# Install system dependencies
RUN apt-get update --fix-missing && apt-get install -y \
    git \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages with retry logic
RUN --mount=type=cache,target=/root/.cache/pip \
    for i in {1..3}; do \
        pip install fastapi uvicorn python-multipart faster-whisper && break || sleep 15; \
    done

# Create app directory
WORKDIR /app

# Copy Python application files
COPY python-app/requirements.txt .
COPY python-app/ .

# Install Python dependencies
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt

# Create volume mount points for external model storage
# Users can mount their host directories here for persistent model storage
VOLUME ["/app/models"]

# Pre-download the model during build (only if external storage is not enabled)
# This can be skipped by setting SKIP_MODEL_DOWNLOAD=true during build
ARG SKIP_MODEL_DOWNLOAD=false
RUN if [ "$SKIP_MODEL_DOWNLOAD" != "true" ]; then \
        echo "Pre-downloading base model to container (set SKIP_MODEL_DOWNLOAD=true to skip)..." && \
        python -c "from faster_whisper import WhisperModel; WhisperModel('base', device='cpu', compute_type='int8')"; \
    else \
        echo "Skipping model pre-download - models will be downloaded at runtime"; \
    fi

# Set default environment variables for model storage
ENV ENABLE_EXTERNAL_STORAGE=false
ENV MODELS_VOLUME_PATH=/app/models
ENV HF_HOME=/app/models/.cache/huggingface

# Expose the port
EXPOSE 4445

# Run the server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "4445"]