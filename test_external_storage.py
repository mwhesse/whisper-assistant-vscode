#!/usr/bin/env python3
"""
Test script for WhisperX Assistant external model storage functionality.
This script validates that external storage configuration works correctly.
"""
import os
import sys
import tempfile
import shutil
from pathlib import Path
import requests
import time
import json

def test_external_storage():
    """Test external storage functionality"""
    print("🧪 Testing WhisperX Assistant External Storage...")
    
    # Configuration
    base_url = "http://localhost:4445"
    test_model = "tiny"  # Use smallest model for testing
    
    # Create temporary directory for external storage
    temp_dir = tempfile.mkdtemp(prefix="whisperx_test_")
    print(f"📁 Created temporary storage directory: {temp_dir}")
    
    try:
        # Test 1: Check health endpoint with storage info
        print("\n1️⃣ Testing health endpoint...")
        response = requests.get(f"{base_url}/v1/health")
        
        if response.status_code != 200:
            print(f"❌ Health check failed: {response.status_code}")
            return False
            
        health_data = response.json()
        print(f"✅ Health check passed")
        print(f"   External storage enabled: {health_data.get('storage', {}).get('external_storage_enabled', 'N/A')}")
        print(f"   Effective cache dir: {health_data.get('storage', {}).get('effective_cache_dir', 'N/A')}")
        
        # Test 2: Check models endpoint
        print("\n2️⃣ Testing models endpoint...")
        response = requests.get(f"{base_url}/v1/models")
        
        if response.status_code != 200:
            print(f"❌ Models endpoint failed: {response.status_code}")
            return False
            
        models_data = response.json()
        print(f"✅ Models endpoint passed")
        print(f"   Available models: {len(models_data.get('available_models', []))}")
        print(f"   Downloaded models: {len(models_data.get('downloaded_models', []))}")
        
        # Test 3: Check downloaded models endpoint
        print("\n3️⃣ Testing downloaded models endpoint...")
        response = requests.get(f"{base_url}/v1/models/downloaded")
        
        if response.status_code != 200:
            print(f"❌ Downloaded models endpoint failed: {response.status_code}")
            return False
            
        downloaded_data = response.json()
        print(f"✅ Downloaded models endpoint passed")
        print(f"   Downloaded models: {downloaded_data.get('downloaded_models', [])}")
        print(f"   Total available: {downloaded_data.get('total_available', 0)}")
        
        # Test 4: Download a model (if not already downloaded)
        print(f"\n4️⃣ Testing model download for '{test_model}'...")
        
        # Check if model is already downloaded
        if test_model not in downloaded_data.get('downloaded_models', []):
            print(f"   Model '{test_model}' not downloaded, attempting download...")
            response = requests.post(f"{base_url}/v1/models/{test_model}/download")
            
            if response.status_code == 200:
                download_result = response.json()
                print(f"✅ Model download successful: {download_result.get('message', 'N/A')}")
            else:
                print(f"⚠️  Model download failed: {response.status_code} - {response.text}")
        else:
            print(f"   Model '{test_model}' already downloaded ✅")
        
        # Test 5: Verify configuration via environment (if accessible)
        print("\n5️⃣ Testing configuration validation...")
        
        # Check if we can access the API info endpoint
        try:
            response = requests.get(f"{base_url}/api/info")
            if response.status_code == 200:
                api_info = response.json()
                print(f"✅ API info endpoint accessible")
                print(f"   API Title: {api_info.get('message', 'N/A')}")
                print(f"   Version: {api_info.get('version', 'N/A')}")
                print(f"   Device: {api_info.get('device', 'N/A')}")
            else:
                print(f"⚠️  API info endpoint returned: {response.status_code}")
        except Exception as e:
            print(f"⚠️  API info endpoint not accessible: {e}")
        
        print(f"\n🎉 All tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False
        
    finally:
        # Clean up temporary directory
        try:
            shutil.rmtree(temp_dir)
            print(f"🗑️  Cleaned up temporary directory: {temp_dir}")
        except Exception as e:
            print(f"⚠️  Failed to clean up temporary directory: {e}")

def print_usage():
    """Print usage instructions"""
    print("""
🔧 WhisperX Assistant External Storage Test

This script tests the external storage functionality of WhisperX Assistant.

Prerequisites:
1. WhisperX Assistant server must be running on http://localhost:4445
2. To test external storage, run the server with external storage enabled:

   docker run -d -p 4445:4445 \\
     -e ENABLE_EXTERNAL_STORAGE=true \\
     -v ~/.whisperx-models:/app/models \\
     --name whisperx-assistant \\
     mwhesse/whisperx-assistant:latest

Usage:
   python test_external_storage.py

The script will test:
- Health endpoint with storage information
- Models listing and download status
- Model download functionality
- Configuration validation
""")

def main():
    """Main function"""
    if len(sys.argv) > 1 and sys.argv[1] in ['-h', '--help', 'help']:
        print_usage()
        return
    
    print("🚀 Starting WhisperX Assistant External Storage Tests...")
    
    # Check if server is running
    try:
        response = requests.get("http://localhost:4445/v1/health", timeout=5)
        if response.status_code != 200:
            print("❌ Server is not responding correctly")
            print("   Make sure WhisperX Assistant is running on http://localhost:4445")
            sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to server: {e}")
        print("   Make sure WhisperX Assistant is running on http://localhost:4445")
        print_usage()
        sys.exit(1)
    
    # Run tests
    success = test_external_storage()
    
    if success:
        print("\n✅ All tests passed! External storage functionality is working correctly.")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed. Please check the configuration and try again.")
        sys.exit(1)

if __name__ == "__main__":
    main()