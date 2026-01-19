import asyncio, datetime, random
from .run_once import run_once
import logging

logging.basicConfig(level=logging.INFO)


async def service_loop():
    while True:
        logging.info(f"pipeline -> service: Cycle start: {datetime.datetime.now()}")
        try:
            await run_once()
        except Exception as e:
            logging.error(f"pipeline -> service: CRITICAL ERROR: {e}")

        sleep = random.uniform(1500, 2700)
        logging.info(f"pipeline -> service: Sleeping {sleep/60:.1f} minutes")
        await asyncio.sleep(sleep)
