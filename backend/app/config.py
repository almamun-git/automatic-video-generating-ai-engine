import os
from pathlib import Path
from dotenv import load_dotenv, find_dotenv

# Load .env from project root even when running from backend/
load_dotenv(find_dotenv(usecwd=True) or Path(__file__).resolve().parents[2] / '.env')

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
SHOTSTACK_API_KEY = os.getenv("SHOTSTACK_API_KEY")
SHOTSTACK_STAGE = "v1"

if not all([GEMINI_API_KEY, PEXELS_API_KEY, ELEVENLABS_API_KEY, SHOTSTACK_API_KEY]):
    raise ValueError("One or more API keys are missing. Please check your .env file.")
