# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **External Model Storage Support**: Hybrid storage system allowing models to be stored outside Docker containers
  - New environment variables for storage configuration:
    - `ENABLE_EXTERNAL_STORAGE`: Toggle external storage on/off (default: false)
    - `MODELS_CACHE_DIR`: Custom cache directory path inside container
    - `MODELS_VOLUME_PATH`: Volume mount path inside container (default: `/app/models`)
    - Enhanced `HF_HOME` and `TRANSFORMERS_CACHE` support
  - Volume mount support in Dockerfile with `/app/models` volume point
  - Build-time option `SKIP_MODEL_DOWNLOAD` to skip pre-downloading models during build
  - Comprehensive Docker Compose examples with multiple profiles:
    - `external`: Basic external storage setup
    - `custom`: Custom storage location configuration
    - `gpu`: GPU-enabled with external storage
    - `dev`: Development mode with source mounting
    - `default`: Traditional internal storage (backward compatibility)
  - Storage configuration information in `/v1/health` API endpoint
  - Complete documentation section in README.md for external storage setup
  - Troubleshooting guide for storage-related issues
  - Test script (`test_external_storage.py`) for validating storage functionality
  - Migration instructions for moving from internal to external storage

### Changed
- **Enhanced Models Service**: Updated `ModelsService` class to prioritize external storage when enabled
  - Modified cache path detection to check external storage first
  - Enhanced model download detection across multiple storage locations
  - Improved logging for storage configuration and model detection
- **API Documentation**: Updated FastAPI app description to mention external storage support
- **Configuration Management**: Extended `Config` class with storage-related settings and helper methods
- **Environment File**: Updated `.env.example` with comprehensive storage configuration options

### Technical Details
- **Backward Compatibility**: All existing Docker setups continue working unchanged (default behavior preserved)
- **Storage Priority**: When external storage is enabled, external paths are checked first before fallback to internal storage
- **Flexible Configuration**: Supports various storage backends including custom directories and standard HuggingFace cache locations
- **Container Optimization**: Models can be shared between multiple container instances when using external storage

### Files Modified
- `python-app/config.py`: Added storage configuration classes and methods
- `python-app/models_service.py`: Enhanced with external storage support and prioritization logic
- `python-app/main.py`: Added storage information to health endpoint
- `python-app/.env.example`: Documented all new environment variables
- `Dockerfile`: Added volume mounts and build-time configuration options
- `README.md`: Added comprehensive external storage documentation and troubleshooting

### Files Added
- `docker-compose.yml`: Complete examples for different storage scenarios
- `test_external_storage.py`: Validation and testing script for storage functionality

### Benefits
- **Persistence**: Models survive container restarts, updates, and rebuilds
- **Performance**: Eliminates need to re-download models on container recreation
- **Storage Management**: Better control over model storage location and disk usage
- **Development Workflow**: Improved development experience with persistent models
- **Resource Sharing**: Multiple containers can share the same model cache
- **Debugging**: Enhanced troubleshooting capabilities with detailed storage information

---

## Previous Releases

_No previous releases documented. This represents the first major feature addition with external storage support._

---

### Legend

- **Added** for new features
- **Changed** for changes in existing functionality  
- **Deprecated** for soon-to-be removed features
- **Removed** for now removed features
- **Fixed** for any bug fixes
- **Security** for vulnerability fixes

### Migration Notes

For users upgrading to this version:

1. **No Breaking Changes**: Existing setups continue working without modification
2. **Optional Feature**: External storage is disabled by default
3. **Easy Migration**: Follow the migration guide in README.md to move models to external storage
4. **Testing**: Use the provided test script to validate your storage configuration

### Support

- For issues related to external storage, see the troubleshooting section in README.md
- Use the test script to diagnose storage-related problems
- Check the Docker Compose examples for reference configurations