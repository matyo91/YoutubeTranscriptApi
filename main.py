from fastapi import FastAPI, HTTPException, Security, Depends
from fastapi.security.api_key import APIKeyHeader
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import NoTranscriptFound, VideoUnavailable, TranscriptsDisabled
from youtube_transcript_api.formatters import JSONFormatter, TextFormatter, WebVTTFormatter, SRTFormatter
from enum import Enum
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

load_dotenv()

class TranscriptFormat(str, Enum):
    JSON = "json"
    TEXT = "text"
    WEBVTT = "webvtt"
    SRT = "srt"

app = FastAPI(
    title="YouTube Transcript API",
    description="Fetch video transcripts via an API",
    version="0.1.0",
    contact={
        "name": "API Support",
        "url": "https://github.com/yoanbernabeu/YoutubeTranscriptApi"
    },
    license_info={
        "name": "MIT",
    }
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En production, spécifiez les domaines autorisés
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Key configuration
API_KEY = os.getenv("API_KEY")
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def get_api_key(api_key_header: str = Security(api_key_header)):
    if not API_KEY:
        return None
    if api_key_header == API_KEY:
        return api_key_header
    raise HTTPException(
        status_code=401,
        detail="Invalid API Key"
    )

@app.get("/")
def read_root():
    return {
        "message": "Welcome to the YouTube Transcript API",
        "description": "This API allows you to extract subtitles from YouTube videos",
        "endpoints": {
            "/transcript": "Get video subtitles (formats: json, text, webvtt, srt)",
            "/transcripts": "List available subtitles for a video"
        },
        "documentation": "/docs"
    }

@app.get("/transcript")
async def get_transcript(
    video_id: str, 
    language: str = "en", 
    format: TranscriptFormat = TranscriptFormat.JSON,
    api_key: str = Depends(get_api_key)
):
    """
    Fetch transcript for a given YouTube video ID and language.
    Available formats: json, text, webvtt, srt
    """
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=[language])
        
        # If format is TEXT, process transcript to include word-level timestamps
        if format == TranscriptFormat.TEXT:
            word_level_transcript = []
            for segment in transcript:
                words = segment['text'].split()
                # Calculate approximate time per word
                segment_duration = segment.get('duration', 0)
                time_per_word = segment_duration / len(words) if words else 0
                start_time = segment['start']
                
                # Add timestamp for each word
                for i, word in enumerate(words):
                    word_time = start_time + (i * time_per_word)
                    formatted_time = f"[{int(word_time//60):02d}:{int(word_time%60):02d}.{int((word_time%1)*1000):03d}]"
                    word_level_transcript.append(f"{formatted_time} {word}")
            
            formatted_transcript = "\n".join(word_level_transcript)
        else:
            formatters = {
                TranscriptFormat.JSON: JSONFormatter(),
                TranscriptFormat.TEXT: TextFormatter(),
                TranscriptFormat.WEBVTT: WebVTTFormatter(),
                TranscriptFormat.SRT: SRTFormatter()
            }
            formatter = formatters[format]
            formatted_transcript = formatter.format_transcript(transcript)
        
        content_types = {
            TranscriptFormat.JSON: "application/json",
            TranscriptFormat.TEXT: "text/plain",
            TranscriptFormat.WEBVTT: "text/vtt",
            TranscriptFormat.SRT: "text/plain"
        }
        
        return Response(
            content=formatted_transcript,
            media_type=content_types[format]
        )
        
    except NoTranscriptFound:
        raise HTTPException(status_code=404, detail="Transcript not found for the specified language.")
    except VideoUnavailable:
        raise HTTPException(status_code=404, detail="Video is unavailable.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/transcripts")
async def list_transcripts(
    video_id: str,
    api_key: str = Depends(get_api_key)
):
    """
    List all available transcripts for a given YouTube video ID.
    """
    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        available_transcripts = []
        
        for transcript in transcript_list:
            available_transcripts.append({
                "language": transcript.language,
                "language_code": transcript.language_code,
                "is_generated": transcript.is_generated,
                "is_translatable": transcript.is_translatable
            })
            
        return {
            "video_id": video_id,
            "available_transcripts": available_transcripts
        }
        
    except TranscriptsDisabled:
        raise HTTPException(status_code=404, detail="Transcripts are disabled for this video.")
    except VideoUnavailable:
        raise HTTPException(status_code=404, detail="Video is unavailable.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
