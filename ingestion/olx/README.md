# OLX Crawler (Ingestion)

This module contains a Playwright-based crawler designed to scrape listings from OLX and store them in the PostgreSQL database.

## Prerequisites
- Python 3.8+
- PostgreSQL database running (see `storage/README.md`)

## Setup
1. **Navigate to the directory:**
   ```powershell
   cd ingestion/olx
   ```

2. **Create and activate a virtual environment:**
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

3. **Install dependencies:**
   ```powershell
   pip install -r requirements.txt
   playwright install chromium
   ```

4. **Environment Configuration:**
   Ensure `.env` is configured correctly:
   ```env
   DATABASE_URL=postgresql://postgres:password@127.0.0.1:5433/pricer
   OLX_START_URL=https://www.olx.pl/elektronika/
   ```

## Usage
Run the crawler:
```powershell
python crawler.py
```

## Output
- **Database**: Listings are saved to the `listings` table in the `pricer` database via the `raw_data` JSONB column.
