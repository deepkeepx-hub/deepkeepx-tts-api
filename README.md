# tts-api

[![Docker Pulls](https://img.shields.io/docker/pulls/deepkeepx/tts-api?style=flat-square)](https://hub.docker.com/r/deepkeepx/tts-api) [![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg?style=flat-square)](LICENSE) [![Architecture](https://img.shields.io/badge/arch-amd64%20%7C%20arm64-blue?style=flat-square)](https://hub.docker.com/r/deepkeepx/tts-api)

**English** | [简体中文](README_zh.md)

`tts-api` is a lightweight, fully offline Text-to-Speech (TTS) HTTP API microservice built with **FastAPI** and an advanced TTS engine. It supports multiple languages and over 50 voices. The models and voice files are completely pre-packaged into the Docker image, making it plug-and-play without any external network dependency.

> 💡 **Docker Image**: [https://hub.docker.com/r/deepkeepx/tts-api](https://hub.docker.com/r/deepkeepx/tts-api)

### ✨ Features
- **100% Offline**: Models and voice files are pre-packaged inside the image. No external API calls or internet required at runtime.
- **Multi-Language Support**: Supports English, Chinese, Japanese, Spanish, French, Hindi, Italian, and Portuguese.
- **Rich Voices**: Built-in support for 54 different voices (female and male for most languages).
- **Auto Cleanup**: Automatically deletes generated audio files older than 2 hours to save disk space.
- **Multi-Architecture**: Native support for `linux/amd64` and `linux/arm64` (CPU version). Windows and Mac are fully supported via Docker Desktop.
- **GPU Acceleration**: Separate GPU image available for blazing-fast inference on NVIDIA GPUs.
- **Lightweight & Secure**: Optimized build (minimal footprint), running as a non-root user.

---

### 🚀 Quick Start

Since the models are built into the image, you don't need to configure any data volumes for models or download external files.

#### 1. Run with Docker Compose
Create a `docker-compose.yml` file:

```yaml
services:
  tts-api:
    image: deepkeepx/tts-api:latest-cpu
    container_name: tts-api
    restart: always
    ports:
      - "8080:8080"
    environment:
      - TZ=Asia/Shanghai
    volumes:
      - ./data:/app/data
```
*Note: The `./data` directory is where generated audio files will be stored temporarily before auto-cleanup.*

Start the service:
```bash
docker compose up -d
```

#### 2. Or Run with a single `docker run` command
```bash
docker run -d \
    --name tts-api \
    --restart always \
    -p 8080:8080 \
    -e TZ=Asia/Shanghai \
    -v ./data:/app/data \
    deepkeepx/tts-api:latest-cpu
```

---

### 🔌 API Usage

#### 1. Text-to-Speech Synthesis
**Endpoint**: `POST /tts`

**Request Body:**
| Parameter | Type | Required | Default | Description |
| :--- | :--- | :--- | :--- | :--- |
| `text` | string | Yes | - | The text to synthesize (max 2000 chars). |
| `voice` | string | No | `af_heart` | The voice ID to use. |
| `lang_code` | string | No | inferred | Language code (e.g., `a` for English, `z` for Chinese). |
| `speed` | float | No | `1.0` | Speech speed (0.5 to 2.0). |
| `output_format` | string | No | `wav` | Audio format (`wav` or `flac`). |
| `return_base64` | bool | No | `true` | Whether to include base64 audio data in the response. |

**Request Example:**
```json
{
    "text": "Hello world, this is an offline TTS test.",
    "voice": "af_heart",
    "return_base64": false
}
```

**Success Response (HTTP 200):**
```json
{
    "code": 0,
    "msg": "",
    "data": {
        "format": "wav",
        "sample_rate": 24000,
        "voice": "af_heart",
        "lang_code": "a",
        "audio_url": "http://localhost:8080/audio/a1b2c3d4e5f6.wav",
        "file_path": "/app/data/a1b2c3d4e5f6.wav"
    },
    "success": true
}
```

**Error Response:**
```json
{
    "code": 1,
    "msg": "Generation failed: ...",
    "data": null,
    "success": false
}
```

#### 2. List Available Voices
**Endpoint**: `GET /voices`

Returns a complete JSON object of all supported voices categorized by language and gender.

#### 3. Health Check
**Endpoint**: `GET /health`

Used for container orchestration. Returns service status and the active device (`cpu` or `cuda`).

### ⚙️ Environment Variables

| Variable | Description | Default |
| :--- | :--- | :--- |
| `TZ` | Timezone for the container | `UTC` |

---
## 📄 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.
Copyright 2026 DeepkeepX.