# tts-api

[![Docker Pulls](https://img.shields.io/docker/pulls/deepkeepx/tts-api?style=flat-square)](https://hub.docker.com/r/deepkeepx/tts-api) [![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg?style=flat-square)](LICENSE) [![Architecture](https://img.shields.io/badge/arch-amd64%20%7C%20arm64-blue?style=flat-square)](https://hub.docker.com/r/deepkeepx/tts-api)

[English](README.md) | **简体中文**

`tts-api` 是一个基于 **FastAPI** 构建的轻量级、完全离线的文本转语音（TTS）HTTP API 微服务。支持多种语言和 50 多种音色。模型和音色文件已全部预打包进 Docker 镜像，真正做到开箱即用，无需任何外部网络依赖。

> 💡 **Docker 镜像**: [https://hub.docker.com/r/deepkeepx/tts-api](https://hub.docker.com/r/deepkeepx/tts-api)

### ✨ 特性
- **100% 离线**：模型和音色文件全部打包在镜像内，运行时无需外部网络，确保隐私和稳定性。
- **多语言支持**：支持英语、中文、日语、西班牙语、法语、印地语、意大利语和葡萄牙语。
- **丰富音色**：内置 54 种不同音色（大部分语言提供男女声）。
- **自动清理**：自动删除生成超过 2 小时的音频文件，节省磁盘空间。
- **多架构支持**：原生支持 `linux/amd64` 和 `linux/arm64`（CPU 版本），通过 Docker Desktop 完美支持 Windows 和 Mac。
- **GPU 加速**：提供独立的 GPU 镜像版本，实现极速推理。
- **轻量且安全**：优化的构建体积，并采用非 root 用户运行，保障系统安全。

---

### 🚀 快速启动

因为模型已经内置在镜像中，你无需配置任何模型目录或下载外部文件。

#### 1. 使用 Docker Compose 运行
创建 `docker-compose.yml` 文件：

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
*注意：`./data` 目录用于存放生成的音频文件（超过 2 小时会自动清理）。*

启动服务：
```bash
docker compose up -d
```

#### 2. 或者使用单行 `docker run` 命令
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

### 🔌 API 使用说明

#### 1. 文本转语音合成
**接口**: `POST /tts`

**请求参数:**
| 参数名 | 类型 | 必填 | 默认值 | 描述 |
| :--- | :--- | :--- | :--- | :--- |
| `text` | string | 是 | - | 要合成的文本（最长 2000 字符）。 |
| `voice` | string | 否 | `af_heart` | 使用的音色 ID。 |
| `lang_code` | string | 否 | 自动推断 | 语言代码（如 `a` 为英语，`z` 为中文）。 |
| `speed` | float | 否 | `1.0` | 语速（0.5 到 2.0）。 |
| `output_format` | string | 否 | `wav` | 音频格式（`wav` 或 `flac`）。 |
| `return_base64` | bool | 否 | `true` | 是否在响应中包含 base64 音频数据。 |

**请求示例:**
```json
{
    "text": "你好，欢迎使用离线语音合成接口。",
    "voice": "zf_xiaobei",
    "return_base64": false
}
```

**成功响应 (HTTP 200):**
```json
{
    "code": 0,
    "msg": "",
    "data": {
        "format": "wav",
        "sample_rate": 24000,
        "voice": "zf_xiaobei",
        "lang_code": "z",
        "audio_url": "http://localhost:8080/audio/a1b2c3d4e5f6.wav",
        "file_path": "/app/data/a1b2c3d4e5f6.wav"
    },
    "success": true
}
```

**失败响应:**
```json
{
    "code": 1,
    "msg": "Generation failed: ...",
    "data": null,
    "success": false
}
```

#### 2. 获取支持音色
**接口**: `GET /voices`

返回按语言和性别分类的所有支持音色列表。

#### 3. 健康检查
**接口**: `GET /health`

用于容器编排。返回服务状态以及当前使用的设备（`cpu` 或 `cuda`）。

### ⚙️ 环境变量

| 变量名 | 描述 | 默认值 |
| :--- | :--- | :--- |
| `TZ` | 容器的时区 | `UTC` |

---
## 📄 开源协议

本项目基于 Apache License 2.0 协议开源 - 详情请参阅 [LICENSE](LICENSE) 文件。
Copyright 2026 DeepkeepX.