"""Configuration is loaded from .env beside this file, never from source code."""
import os
from pathlib import Path
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT / '.env', override=False)
FIREBASE_API_KEY = os.getenv('FIREBASE_API_KEY', '').strip()
FIREBASE_PROJECT_ID = os.getenv('FIREBASE_PROJECT_ID', '').strip()
OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL', '').strip().rstrip('/')
