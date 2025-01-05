# YouTube Transcript REST API

A REST API wrapper around [youtube-transcript-api](https://pypi.org/project/youtube-transcript-api/) Python package. This API allows you to fetch YouTube video transcripts (subtitles) in various formats.

## Features

- Get transcripts in multiple formats (JSON, Text, WebVTT, SRT)
- List available transcripts for a video
- Optional API key protection
- Docker ready

## Quick Start

One-liner to run with Docker:
```bash
docker run -p 8000:8000 yoanbernabeu/youtubetranscriptapi:latest
```

## Installation

### Using Docker Compose (recommended)
```bash
# Without API key protection
docker compose up -d

# With API key protection
API_KEY=your_secret_key_here docker compose up -d
```

### Manual Installation
```bash
# Clone repository
git clone https://github.com/yourusername/YoutubeTranscriptApi.git
cd YoutubeTranscriptApi

# Install dependencies
pip install -r requirements.txt

# Run server
uvicorn main:app --reload
```

## API Usage

### Get Transcript
```bash
# JSON format (default)
curl "http://localhost:8000/transcript?video_id=VIDEO_ID&language=en"

# Other formats (text, webvtt, srt)
curl "http://localhost:8000/transcript?video_id=VIDEO_ID&language=en&format=srt"
```

### List Available Transcripts
```bash
curl "http://localhost:8000/transcripts?video_id=VIDEO_ID"
```

### Using API Key (if enabled)
```bash
curl -H "X-API-Key: your_secret_key_here" "http://localhost:8000/transcript?video_id=VIDEO_ID"
```

## API Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI JSON: http://localhost:8000/openapi.json

## Environment Variables

- `API_KEY`: Optional. If set, will require this key for protected endpoints.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Credits

This project is a REST API wrapper around the excellent [youtube-transcript-api](https://pypi.org/project/youtube-transcript-api/) Python package.
