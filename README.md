<p align="center">
  <img src="https://raw.githubusercontent.com/mwhesse/whisperx-assistant-vscode/main/images/whisperx-assistant.png" alt="WhisperX Assistant">
</p>

# WhisperX Assistant: Your Voice-Driven Coding Companion

[![Visual Studio Marketplace Version](https://img.shields.io/visual-studio-marketplace/v/mwhesse.whisperx-assistant?style=flat&logo=visual-studio-code&logoColor=white&label=VS%20Marketplace&color=007ACC)](https://marketplace.visualstudio.com/items?itemName=mwhesse.whisperx-assistant)
[![Visual Studio Marketplace Installs](https://img.shields.io/visual-studio-marketplace/i/mwhesse.whisperx-assistant?style=flat&logo=visual-studio-code&logoColor=white&label=Installs&color=blue)](https://marketplace.visualstudio.com/items?itemName=mwhesse.whisperx-assistant)
[![Visual Studio Marketplace Rating](https://img.shields.io/visual-studio-marketplace/r/mwhesse.whisperx-assistant?style=flat&logo=visual-studio-code&logoColor=white&label=Rating&color=yellow)](https://marketplace.visualstudio.com/items?itemName=mwhesse.whisperx-assistant)

WhisperX Assistant is an extension for Visual Studio Code that transcribes your spoken words into text within the VSCode & Cursor editor. This hands-free approach to coding allows you to focus on your ideas instead of your typing.

✨ **Features:**

- Cross-platform audio recording with SoX (default) or custom recording commands
- Multiple API options: Local Docker, OpenAI, or Groq
- Configurable recording tools (ffmpeg, arecord, etc.) for advanced users
- Optimized for integration with AI coding assistants like Cursor

WhisperX Assistant can also be integrated with other powerful AI tools, such as Chat GPT-4 or [Cursor](https://www.cursor.so/), to create a dynamic, AI-driven development environment.

# Powered by OpenAI Whisper

By default, WhisperX Assistant utilizes Whisper AI on your _local machine_, offering a free voice transcription service. For this, the base model of Whisper is used, balancing accuracy and performance. **In the future, we will support other models.**

There is also the option to use the OpenAI API or Groq API to transcribe your audio for remote transcription. **Note: This requires an API key.**

For more details about Whisper, visit the [Whisper OpenAI GitHub page](https://github.com/openai/whisper).

## Getting Started: Installation Instructions

To install and setup WhisperX Assistant, follow these steps:

1.  **Install a recording tool**: WhisperX Assistant uses SoX by default for microphone recording, but you can also configure a custom recording command using alternatives like ffmpeg.

    ### Option A: SoX (Default - Recommended)

    - **MacOS**: Using the Homebrew package manager:
      ```bash
      brew install sox
      ```
    - **Windows**: Using the Chocolatey package manager:
      ```bash
      choco install sox.portable
      ```
      **Note for Windows Users:** Some users have reported issues with newer SoX versions not recognizing the default audio device. If you encounter this, installing version 14.4.1 specifically might resolve the problem:
      ```bash
      choco install sox.portable --version=14.4.1
      ```
    - **Ubuntu/Debian**:
      ```bash
      sudo apt install sox
      ```
    - **Other Linux distributions**: Use your package manager (e.g., `yum install sox`, `pacman -S sox`)

    ### Option B: Custom Recording Command (Alternative)

    **Linux users experiencing audio cutoff issues with SoX can use ffmpeg instead:**

    - **Ubuntu/Debian**:
      ```bash
      sudo apt install ffmpeg
      ```
    - **MacOS**:
      ```bash
      brew install ffmpeg
      ```
    - **Windows**:
      ```bash
      choco install ffmpeg
      ```

    After installation, configure the custom recording command in VS Code settings (see [Custom Recording Commands](#custom-recording-commands) section below).

2.  Install Docker to enable the local Whisper model or use the OpenAI API or Groq API for remote transcription.
    - If using local transcription, follow the instructions in the [Local Development with Faster Whisper](#local-development-with-faster-whisper) section.
    - If using remote transcription, follow the instructions in the [Multiple API Options](#multiple-api-options) section.
3.  Install the WhisperX Assistant extension into Visual Studio Code or Cursor.

# How to Use WhisperX Assistant

1. **Initialization**: Upon loading Visual Studio Code, the extension verifies the correct installation of SoX (or your custom recording command if configured). If any issues are detected, an error message will be displayed.

Once initialization is complete, a microphone icon will appear in the bottom right status bar.

  <img src="https://raw.githubusercontent.com/mwhesse/whisperx-assistant-vscode/main/images/microphone.png" alt="WhisperX Assistant icon" style="width: 144px; height: auto; ">

2. **Starting the Recording**: Activate the extension by clicking on the quote icon or using the shortcut `Command+M` (for Mac) or `Control+M` (for Windows). You can record for as long as you like, but remember, the longer the recording, the longer the transcription process. The recording time will be displayed in the status bar.

  <img src="https://raw.githubusercontent.com/mwhesse/whisperx-assistant-vscode/main/images/recording.png" alt="Recording icon" style="width: 100px; height: auto;">

3. **Stopping the Recording**: Stop the recording using the same shortcut (`Command+M` or `Control+M`). The extension icon in the status bar will change to a loading icon, and a progress message will be displayed, indicating that the transcription is underway.

  <img src="https://raw.githubusercontent.com/mwhesse/whisperx-assistant-vscode/main/images/transcribing.png" alt="Transcribing" style="width: 360px; height: auto; ">

4. **Transcription**: Once the transcription is complete, the text will be saved to the clipboard. This allows you to use the transcription in any program, not just within Visual Studio Code. If an editor is active, the transcription will be pasted there automatically.

  <img src="https://raw.githubusercontent.com/mwhesse/whisperx-assistant-vscode/main/images/transcribed.png" alt="Transcribed" style="width: 400px; height: auto; ">

**Tip**: A good microphone will improve transcription accuracy, although it is not a requirement.

**Tip**: For an optimal experience, consider using the Cursor.so application to directly call the Chat GPT-4 API for code instructions. This allows you to use your voice to instruct GPT to refactor your code, write unit tests, and implement various improvements.

## Custom Recording Commands

WhisperX Assistant uses SoX by default, but you can configure a custom recording command if you prefer alternatives like ffmpeg or need to work around platform-specific issues.

### When to Use Custom Recording Commands

- **Linux users experiencing audio cutoff**: Some Linux distributions have issues with SoX cutting off the last few seconds of recordings
- **Advanced users**: Want to use specific audio settings or recording tools
- **Specific microphone requirements**: Need to target a particular audio device

### Configuration

1. Open VS Code settings (`Cmd/Ctrl + ,`)
2. Search for "WhisperX Assistant"
3. Find "Custom Recording Command"
4. Enter your command with the `$AUDIO_FILE` placeholder

**Important**: Your command MUST include `$AUDIO_FILE` where the output file should be saved.

### Platform-Specific Examples

#### macOS (ffmpeg)

```bash
ffmpeg -f avfoundation -i :1 -ac 1 -ar 16000 -sample_fmt s16 $AUDIO_FILE
```

_Note: Replace `:1` with the appropriate device number from `ffmpeg -f avfoundation -list_devices true -i ""`_

#### Linux (ffmpeg with PulseAudio)

```bash
ffmpeg -f pulse -i default -ac 1 -ar 16000 -sample_fmt s16 $AUDIO_FILE
```

#### Linux (ffmpeg with ALSA)

```bash
ffmpeg -f alsa -i default -ac 1 -ar 16000 -sample_fmt s16 $AUDIO_FILE
```

#### Windows (ffmpeg)

```bash
ffmpeg -f dshow -i audio="Microphone" -ac 1 -ar 16000 -sample_fmt s16 $AUDIO_FILE
```

#### Alternative Tools

**Linux with arecord:**

```bash
arecord -f S16_LE -c 1 -r 16000 $AUDIO_FILE
```

**Any platform with custom settings:**

```bash
sox -t pulseaudio default -c 1 -r 16000 $AUDIO_FILE gain -3
```

### Troubleshooting Custom Commands

- **Command validation error**: Ensure your command includes `$AUDIO_FILE`
- **No audio recorded**: Check your audio device permissions and microphone access
- **Command not found**: Verify the recording tool (ffmpeg, arecord, etc.) is installed and in your PATH
- **Still experiencing cutoffs**: Try adjusting buffer settings or switching recording tools

### Finding Your Audio Device

**macOS (ffmpeg):**

```bash
ffmpeg -f avfoundation -list_devices true -i ""
```

**Linux (PulseAudio):**

```bash
pactl list sources short
```

**Linux (ALSA):**

```bash
arecord -l
```

**Windows (ffmpeg):**

```bash
ffmpeg -list_devices true -f dshow -i dummy
```

## Using WhisperX Assistant with Cursor.so

To enhance your development experience with Cursor.so and WhisperX Assistant, follow these simple steps:

1.  Start the recording: Press `Command+M` (Mac) or `Control+M` (Windows).
2.  Speak your instructions clearly.
3.  Stop the recording: Press `Command+M` (Mac) or `Control+M` (Windows).
    _Note: This initiates the transcription process._
4.  Open the Cursor dialog: Press `Command+K` or `Command+L`.
    _Important: Do this **before** the transcription completes._
5.  The transcribed text will automatically populate the Cursor dialog. Here, you can edit the text or add files/docs, then press `Enter` to execute the GPT query.

By integrating Cursor.so with WhisperX Assistant, you can provide extensive instructions without the need for typing, significantly enhancing your development workflow.

# Platform Compatibility

WhisperX Assistant has been tested and supports:

- **macOS**: Full support with SoX (default) and ffmpeg (custom)
- **Windows**: Full support with SoX (default) and ffmpeg (custom)
- **Linux**: Full support with SoX (default) and ffmpeg (custom) - _Note: Some distributions may experience audio cutoff issues with SoX, for which ffmpeg is recommended_

If you encounter any platform-specific issues, please consider using the [custom recording command](#custom-recording-commands) feature or report the issue on our GitHub repository.

## Local Development with Faster Whisper

This extension supports using a local Faster Whisper model through Docker. This provides fast transcription locally and doesn't require an API key.

### Quick Start with Docker

To get started with local transcription, use our Docker image:

```bash
docker run -d -p 4445:4445 --name whisperx-assistant mwhesse/whisperx-assistant:latest
```

Then configure VSCode:

1. Open VSCode settings (File > Preferences > Settings)
2. Search for "WhisperX Assistant"
3. Set "Api Provider" to "localhost"
4. Set "Api Key" to any non-empty string (e.g., "localhost-dummy-key")

That's it! You can now use the extension with your local Whisper server.

### External Model Storage

By default, models are downloaded and stored inside the Docker container, which means they're lost when the container is recreated. To persist models outside the container, you can use external storage.

#### Benefits of External Model Storage

- **Persistence**: Models survive container restarts and updates
- **Performance**: Avoid re-downloading models on container recreation
- **Storage Management**: Better control over where models are stored
- **Sharing**: Share models between multiple container instances

#### Quick Setup for External Storage

**Basic external storage setup:**

```bash
# Create a directory for models on your host
mkdir -p ~/.whisperx-models

# Run with external storage enabled
docker run -d -p 4445:4445 \
  -e ENABLE_EXTERNAL_STORAGE=true \
  -v ~/.whisperx-models:/app/models \
  --name whisperx-assistant \
  mwhesse/whisperx-assistant:latest
```

**Custom cache directory:**

```bash
# Create a custom directory for models
mkdir -p /path/to/your/models

# Run with custom external storage location
docker run -d -p 4445:4445 \
  -e ENABLE_EXTERNAL_STORAGE=true \
  -e MODELS_CACHE_DIR=/app/models \
  -v /path/to/your/models:/app/models \
  --name whisperx-assistant \
  mwhesse/whisperx-assistant:latest
```

#### Using Docker Compose

For easier management, use the provided [`docker-compose.yml`](docker-compose.yml) file:

```bash
# External storage (recommended)
docker compose --profile external up -d

# Custom storage location
HOME=/path/to/your/home docker compose --profile custom up -d

# GPU-enabled with external storage
docker compose --profile gpu up -d

# Development mode with external storage
docker compose --profile dev up -d
```

#### Environment Variables for Model Storage

- `ENABLE_EXTERNAL_STORAGE`: Enable/disable external storage (default: `false`)
- `MODELS_CACHE_DIR`: Custom cache directory path inside container (default: `/app/models`)
- `MODELS_VOLUME_PATH`: Volume mount path inside container (default: `/app/models`)
- `HF_HOME`: HuggingFace cache directory (auto-configured when external storage is enabled)

### Docker Configuration Options

#### Memory Limits

If you're experiencing memory issues, you can limit the container's memory:

```bash
docker run -d -p 4445:4445 --memory=4g --name whisperx-assistant mwhesse/whisperx-assistant:latest
```

#### GPU Support

If you have a CUDA-capable GPU:

```bash
docker run -d -p 4445:4445 --gpus all --name whisperx-assistant mwhesse/whisperx-assistant:latest
```

#### Container Management

```bash
# Stop the server
docker stop whisperx-assistant

# Start the server
docker start whisperx-assistant

# Remove the container
docker rm whisperx-assistant

# View logs
docker logs whisperx-assistant

# Update to latest version
docker pull mwhesse/whisperx-assistant:latest
docker stop whisperx-assistant
docker rm whisperx-assistant
docker run -d -p 4445:4445 mwhesse/whisperx-assistant:latest
```

### Troubleshooting

1. Check if the server is running:

   ```bash
   curl http://localhost:4445/v1/health
   ```

2. **Common Issues:**

   **Server Issues:**
   - **First startup delay**: The model is downloaded on first use, which may take a few minutes
   - **Memory issues**: Try using the `--memory=4g` flag as shown above
   - **Port conflicts**: If port 4445 is in use, you can map to a different port:
         ```bash
         docker run -d -p 5000:4445 mwhesse/whisperx-assistant:latest
         ```
         Then update the custom endpoint in VSCode settings to `http://localhost:5000`

   **Model Storage Issues:**
   - **Models not persisting**: Ensure you're using the `-v` flag to mount a host directory when external storage is enabled
   - **Permission errors**: Make sure the mounted directory has proper permissions:
     ```bash
     mkdir -p ~/.whisperx-models
     chmod 755 ~/.whisperx-models
     ```
   - **Models not found after restart**: Check that the volume mount path is correct and the directory exists
   - **Storage location confusion**: Verify environment variables are set correctly:
     ```bash
     docker exec whisperx-assistant env | grep -E "(ENABLE_EXTERNAL_STORAGE|MODELS_CACHE_DIR|HF_HOME)"
     ```
   - **Disk space issues**: Large models require significant space (up to 3GB for large models). Check available space:
     ```bash
     df -h ~/.whisperx-models
     ```
   - **Multiple model locations**: If models appear in different locations, check the priority order in logs:
     ```bash
     docker logs whisperx-assistant | grep -i "cache directory"
     ```

3. **Debugging Model Storage:**

   ```bash
   # Check what models are detected as downloaded
   curl http://localhost:4445/v1/models/downloaded
   
   # Check model storage configuration
   docker exec whisperx-assistant env | grep -E "(ENABLE_|MODELS_|HF_)"
   
   # List files in external storage
   ls -la ~/.whisperx-models/
   
   # Check container logs for storage-related messages
   docker logs whisperx-assistant | grep -i "storage\|cache\|model"
   ```

4. **Migrating Existing Models:**

   If you have models in the container and want to move them to external storage:
   
   ```bash
   # Copy models from running container to host
   docker cp whisperx-assistant:/root/.cache/huggingface ~/.whisperx-models/
   
   # Restart container with external storage
   docker stop whisperx-assistant
   docker rm whisperx-assistant
   docker run -d -p 4445:4445 \
     -e ENABLE_EXTERNAL_STORAGE=true \
     -v ~/.whisperx-models:/app/models \
     --name whisperx-assistant \
     mwhesse/whisperx-assistant:latest
   ```

### Advanced: Building from Source

If you want to customize the server, you can build from our Dockerfile:

1. Get the Dockerfile from our repository
2. Build the image:
   ```bash
   docker build -t whisperx-assistant-local .
   docker run -d -p 4445:4445 whisperx-assistant-local
   ```
## Running the Python App Outside Docker

The WhisperX Assistant API is now available as a standalone Python application that can be run outside of Docker. This is useful for development, testing, or when you prefer not to use Docker.

### Python App Structure

The Python application is located in the [`python-app/`](python-app/) directory with the following structure:

```
python-app/
├── main.py                    # FastAPI application entry point
├── config.py                  # Configuration management
├── transcription_service.py   # Transcription service logic
├── run.py                     # Convenience script to run the app
├── requirements.txt           # Production dependencies
├── test_requirements.txt      # Test dependencies
├── pytest.ini               # Pytest configuration
├── .env.example              # Environment variables example
├── .gitignore               # Git ignore rules
├── README.md                # Detailed Python app documentation
└── tests/                   # Test suite
    ├── __init__.py
    ├── test_main.py
    └── test_transcription_service.py
```

### Quick Start (Python App)

1. **Prerequisites:**
   - Python 3.10 or higher
   - FFmpeg installed on your system

2. **Setup:**
   ```bash
   cd python-app
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   python run.py
   ```
   
   Or use the convenience script with options:
   ```bash
   python run.py --model small --port 8000 --install-deps
   ```

4. **Test the application:**
   ```bash
   pip install -r test_requirements.txt
   pytest
   ```

### Configuration Options

The Python app can be configured using environment variables or command-line arguments:

- `--model`: Whisper model size (tiny, base, small, medium, large)
- `--device`: Device for inference (cpu, cuda)
- `--host`: Host to bind to (default: 0.0.0.0)
- `--port`: Port to bind to (default: 4445)
- `--install-deps`: Automatically install dependencies

For more detailed information about running and configuring the Python application, see the [`python-app/README.md`](python-app/README.md) file.

### Benefits of Running Outside Docker

- **Development**: Easier debugging and code modification
- **Testing**: Run comprehensive test suites
- **Performance**: Direct access to system resources
- **Customization**: Easy configuration and model selection
- **Integration**: Better integration with development tools

### Docker Commands Quick Reference

**Build the Docker image:**
```bash
docker build -t whisperx-assistant .
```

**Run the container:**
```bash
docker run -d -p 4445:4445 --name whisperx-assistant whisperx-assistant
```

**Stop/Start/Remove container:**
```bash
docker stop whisperx-assistant
docker start whisperx-assistant
docker rm whisperx-assistant
```

**View logs:**
```bash
docker logs whisperx-assistant
```

# Multiple API Options

Whisper Assistant offers three ways to transcribe your audio:

1. **Local Docker Server** (Default): Run Whisper locally using our Docker container for privacy and no remote API costs
2. **OpenAI Cloud API**: A powerful cloud option using OpenAI's Whisper-1 model for fast, accurate transcription (requires API key)
3. **Groq Cloud API**: A powerful cloud option using Groq's Whisper Large v3 Turbo model for fast, accurate transcription (requires API key)

## Configuring the API Provider

1. Open VSCode settings (File > Preferences > Settings)
2. Search for "Whisper Assistant"
3. Set "Api Provider" to one of:
   - `localhost` (default)
   - `openai`
   - `groq`
4. Enter your API key:
   - For localhost: Any non-empty string (e.g., "localhost-dummy-key")
   - For OpenAI: Get your key from [OpenAI's console](https://platform.openai.com/api-keys)
   - For Groq: Get your key from [GROQ's console](https://console.groq.com)

When using localhost (default), you can customize the endpoint URL in settings if you're running the Docker container on a different port or host.

## Attribution

[Microphone icons created by kliwir art - Flaticon](https://www.flaticon.com/free-icons/microphone)
