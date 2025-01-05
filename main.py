from fastapi import FastAPI, HTTPException
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import NoTranscriptFound, VideoUnavailable, TranscriptsDisabled
from youtube_transcript_api.formatters import JSONFormatter, TextFormatter, WebVTTFormatter, SRTFormatter
from enum import Enum
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware

class TranscriptFormat(str, Enum):
    JSON = "json"
    TEXT = "text"
    WEBVTT = "webvtt"
    SRT = "srt"

app = FastAPI(
    title="YouTube Transcript API",
    description="Fetch video transcripts via an API",
    version="1.0",
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
def get_transcript(video_id: str, language: str = "en", format: TranscriptFormat = TranscriptFormat.JSON):
    """
    Fetch transcript for a given YouTube video ID and language.
    Available formats: json, text, webvtt, srt
    """
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=[language])
        
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
def list_transcripts(video_id: str):
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
