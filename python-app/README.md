# Whisper Assistant API

A FastAPI-based audio transcription service using OpenAI's Whisper model via the `faster-whisper` library.

## Features

- Audio transcription using Whisper models
- OpenAI-compatible API endpoints
- Support for multiple languages
- Configurable via environment variables
- Comprehensive test suite
- Docker support

## Project Structure

```
python-app/
├── main.py                    # FastAPI application entry point
├── config.py                  # Configuration management
├── transcription_service.py   # Transcription service logic
├── requirements.txt           # Production dependencies
├── test_requirements.txt      # Test dependencies
├── pytest.ini               # Pytest configuration
├── tests/                    # Test suite
│   ├── __init__.py
│   ├── test_main.py
│   └── test_transcription_service.py
└── README.md                 # This file
```

## Installation and Setup

### Prerequisites

- Python 3.10 or higher
- FFmpeg (for audio processing)

### Install FFmpeg

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

**Windows:**
Download from [https://ffmpeg.org/download.html](https://ffmpeg.org/download.html)

### Python Environment Setup

1. **Create a virtual environment:**
   ```bash
   cd python-app
   python -m venv venv
   ```

2. **Activate the virtual environment:**
   
   **Linux/macOS:**
   ```bash
   source venv/bin/activate
   ```
   
   **Windows:**
   ```bash
   venv\Scripts\activate
   ```

3. **Install dependencies:**
   
   **For most systems:**
   ```bash
   pip install -r requirements.txt
   ```
   
   **For Windows (if you encounter Rust compilation errors):**
   ```bash
   pip install --only-binary=all -r requirements.txt
   ```
   
   **Alternative for Windows (if above fails):**
   ```bash
   pip install fastapi uvicorn[standard] python-multipart
   pip install --only-binary=all faster-whisper
   ```

4. **Install test dependencies (optional):**
   ```bash
   pip install -r test_requirements.txt
   ```

## Running the Application

### Development Mode

```bash
python main.py
```

The API will be available at `http://localhost:4445`

### Production Mode

```bash
uvicorn main:app --host 0.0.0.0 --port 4445
```

### Using Custom Configuration

Set environment variables to customize the application:

```bash
export WHISPER_MODEL=small
export PORT=8000
export DEFAULT_LANGUAGE=fr
python main.py
```

## Configuration Options

The application can be configured using environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST` | `0.0.0.0` | Server host |
| `PORT` | `4445` | Server port |
| `WHISPER_MODEL` | `base` | Whisper model size (tiny, base, small, medium, large) |
| `WHISPER_DEVICE` | `cpu` | Device for inference (cpu, cuda) |
| `WHISPER_COMPUTE_TYPE` | `int8` | Compute type for inference |
| `CORS_ORIGINS` | `*` | Allowed CORS origins (comma-separated) |
| `DEFAULT_LANGUAGE` | `en` | Default transcription language |
| `API_TITLE` | `Whisper Assistant API` | API title |
| `API_VERSION` | `1.0.0` | API version |

## API Endpoints

### Health Check
```
GET /v1/health
```

### Root Information
```
GET /
```

### Audio Transcription
```
POST /v1/audio/transcriptions
```

**Parameters:**
- `file`: Audio file (multipart/form-data)
- `language`: Language code (optional, default: "en")
- `model_name`: Model name (optional, for compatibility)

**Example using curl:**
```bash
curl -X POST "http://localhost:4445/v1/audio/transcriptions" \
     -H "accept: application/json" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@audio.wav" \
     -F "language=en"
```

## Testing

### Run All Tests
```bash
pytest
```

### Run Tests with Coverage
```bash
pip install pytest-cov
pytest --cov=. --cov-report=html
```

### Run Specific Test File
```bash
pytest tests/test_main.py
```

### Run Tests in Verbose Mode
```bash
pytest -v
```

## Docker Usage

### Build and Run with Docker
```bash
# From the project root directory
docker build -t whisperx-assistant .
docker run -p 4445:4445 whisperx-assistant
```

### Using Docker Compose (if available)
```bash
docker-compose up --build
```

## Development

### Code Style
The project follows Python best practices. Consider using:
- `black` for code formatting
- `flake8` for linting
- `mypy` for type checking

### Adding New Features
1. Create feature branch
2. Add implementation in appropriate module
3. Add comprehensive tests
4. Update documentation
5. Submit pull request

## Troubleshooting

### Common Issues

1. **FFmpeg not found:**
   - Ensure FFmpeg is installed and in your PATH
   - On Windows, you may need to add FFmpeg to system PATH

2. **Model download fails:**
   - Check internet connection
   - The first run downloads the Whisper model (can take time)

3. **Memory issues:**
   - Use smaller models (tiny, base) for limited memory
   - Consider using GPU if available

4. **Port already in use:**
   - Change the PORT environment variable
   - Kill existing processes using the port

5. **Windows: Rust compilation errors (tokenizers package):**
   - Use the `--only-binary=all` flag: `pip install --only-binary=all -r requirements.txt`
   - Or install dependencies individually:
     ```bash
     pip install fastapi uvicorn[standard] python-multipart
     pip install --only-binary=all faster-whisper
     ```
   - Alternative: Install Visual Studio Build Tools or use pre-compiled wheels

6. **Windows: "Microsoft Visual C++ 14.0 is required" error:**
   - Install Microsoft C++ Build Tools from https://visualstudio.microsoft.com/visual-cpp-build-tools/
   - Or use the `--only-binary=all` approach above

### Logs
The application uses Python's logging module. Set log level:
```bash
export PYTHONPATH=.
python -c "import logging; logging.basicConfig(level=logging.DEBUG)"
python main.py
```

## License

This project is licensed under the same license as the parent project.