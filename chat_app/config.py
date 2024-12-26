import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    FLASK_SECRET_KEY = os.getenv('FLASK_SECRET_KEY')
    HUGGINGFACE_API_TOKEN = os.getenv('HUGGINGFACEHUB_API_TOKEN')
    GOOGLE_SHEET_ID = os.getenv('GOOGLE_SHEET_ID')
    GOOGLE_SHEET_GID = os.getenv('GOOGLE_SHEET_GID')