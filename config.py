import os

from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
PROXY_URL = os.getenv("PROXY_URL")

if not BOT_TOKEN:
    raise RuntimeError("Не задан BOT_TOKEN в файле .env")

MAX_NAME = 50
MIN_TASK = 5
MAX_TASK = 1000
MAX_REQUESTS_PER_HOUR = 3