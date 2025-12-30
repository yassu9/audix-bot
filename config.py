import os
from dotenv import load_dotenv
load_dotenv()

class Config:
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
    FREESOUND_API_KEY = os.getenv("FREESOUND_API_KEY")
    PIXABAY_API_KEY = os.getenv("PIXABAY_API_KEY")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")