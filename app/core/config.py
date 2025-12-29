import os

from dotenv import load_dotenv

load_dotenv()

API_TOKEN = os.getenv("API_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")

if not API_TOKEN:
    raise RuntimeError("API_TOKEN is not set")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set")
