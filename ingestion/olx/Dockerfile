# --- STAGE 5: Crawler (Playwright) ---
# We MUST switch base image for Playwright to get browsers
FROM mcr.microsoft.com/playwright/python:v1.40.0-jammy AS crawler
WORKDIR /app
# Re-install DB libs because this is a different OS image
RUN pip install --no-cache-dir pipeline sqlalchemy psycopg2-binary playwright 
RUN playwright install chromium
COPY ingestion/olx /app
CMD ["python", "-u", "main.py"]