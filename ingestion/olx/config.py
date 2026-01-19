import os

OLX_URLS = [
    "https://www.olx.pl/" + category + "?search%5Border%5D=created_at:desc"
    for category in os.getenv("OLX_START_URL").split(",")
]
DATABASE_URL = os.getenv("DATABASE_URL")
HEARTBEAT_FILE = "/tmp/crawler_heartbeat"
USER_AGENT = "Mozilla/5.0 ..."
