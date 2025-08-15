#!/usr/bin/env python3
"""
Convenience script to run the WhisperX Assistant API
"""
import argparse
import os
import sys
import subprocess
from pathlib import Path

def check_ffmpeg():
    """Check if FFmpeg is installed"""
    try:
        subprocess.run(['ffmpeg', '-version'], 
                      stdout=subprocess.DEVNULL, 
                      stderr=subprocess.DEVNULL, 
                      check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import fastapi
        import uvicorn
        import faster_whisper
        return True
    except ImportError as e:
        print(f"Missing dependency: {e}")
        return False

def install_dependencies():
    """Install required dependencies"""
    print("Installing dependencies...")
    try:
        # Try normal installation first
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'],
                      check=True)
        return True
    except subprocess.CalledProcessError:
        print("Normal installation failed, trying Windows-compatible approach...")
        try:
            # Try with --only-binary=all for Windows compatibility
            subprocess.run([sys.executable, '-m', 'pip', 'install', '--only-binary=all', '-r', 'requirements.txt'],
                          check=True)
            return True
        except subprocess.CalledProcessError:
            print("Binary-only installation failed, trying individual packages...")
            try:
                # Install packages individually
                packages = ['fastapi==0.104.1', 'uvicorn[standard]==0.24.0', 'python-multipart==0.0.6', 'jinja2==3.1.2']
                for package in packages:
                    subprocess.run([sys.executable, '-m', 'pip', 'install', package], check=True)
                
                # Try to install faster-whisper with binary-only
                subprocess.run([sys.executable, '-m', 'pip', 'install', '--only-binary=all', 'faster-whisper==0.9.0'],
                              check=True)
                return True
            except subprocess.CalledProcessError:
                print("Failed to install dependencies. Please install manually:")
                print("pip install fastapi uvicorn[standard] python-multipart jinja2")
                print("pip install --only-binary=all faster-whisper")
                return False

def main():
    parser = argparse.ArgumentParser(description='Run WhisperX Assistant API')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', type=int, default=4445, help='Port to bind to')
    parser.add_argument('--model', default='base', 
                       choices=['tiny', 'base', 'small', 'medium', 'large'],
                       help='Whisper model to use')
    parser.add_argument('--device', default='cpu', choices=['cpu', 'cuda'],
                       help='Device to use for inference')
    parser.add_argument('--install-deps', action='store_true',
                       help='Install dependencies before running')
    parser.add_argument('--check-only', action='store_true',
                       help='Only check dependencies, do not run')
    
    args = parser.parse_args()
    
    # Set environment variables
    os.environ['HOST'] = args.host
    os.environ['PORT'] = str(args.port)
    os.environ['WHISPER_MODEL'] = args.model
    os.environ['WHISPER_DEVICE'] = args.device
    
    print("WhisperX Assistant API Setup")
    print("=" * 30)
    
    # Check FFmpeg
    print("Checking FFmpeg...", end=" ")
    if check_ffmpeg():
        print("✓ Found")
    else:
        print("✗ Not found")
        print("\nFFmpeg is required for audio processing.")
        print("Please install FFmpeg:")
        print("  Ubuntu/Debian: sudo apt-get install ffmpeg")
        print("  macOS: brew install ffmpeg")
        print("  Windows: Download from https://ffmpeg.org/download.html")
        if not args.check_only:
            sys.exit(1)
    
    # Install dependencies if requested
    if args.install_deps:
        if not install_dependencies():
            sys.exit(1)
    
    # Check dependencies
    print("Checking Python dependencies...", end=" ")
    if check_dependencies():
        print("✓ Found")
    else:
        print("✗ Missing")
        print("\nPlease install dependencies:")
        print("  pip install -r requirements.txt")
        print("Or run with --install-deps flag")
        if not args.check_only:
            sys.exit(1)
    
    if args.check_only:
        print("\n✓ All checks passed!")
        return
    
    print(f"\nStarting server on {args.host}:{args.port}")
    print(f"Using model: {args.model} on {args.device}")
    print("Press Ctrl+C to stop")
    print("-" * 30)
    
    # Import and run the app
    try:
        from main import app
        import uvicorn
        uvicorn.run(app, host=args.host, port=args.port)
    except KeyboardInterrupt:
        print("\nServer stopped")
    except Exception as e:
        print(f"Error starting server: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()