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

# Pre-download the model during build
RUN python -c "from faster_whisper import WhisperModel; WhisperModel('base', device='cpu', compute_type='int8')"

# Expose the port
EXPOSE 4445

# Run the server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "4445"]