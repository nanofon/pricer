import asyncio, random
from crawler.sold_check import is_listing_active
from storage.repository import get_unsold_urls, mark_as_sold
import logging

logging.basicConfig(level=logging.INFO)


async def check_sold_listings(session, page, batch_size=200):
    rows = get_unsold_urls(session, limit=batch_size)

    if not rows:
        logging.info("No unsold listings to check.")
        return

    logging.info(f"Checking sold status for {len(rows)} listings")

    for listing_id, url in rows:
        try:
            active = await is_listing_active(page, url)
            if not active:
                logging.info(f"Marking as sold: {url}")
                mark_as_sold(session, listing_id)

            await asyncio.sleep(random.uniform(0.5, 1.5))

        except Exception as e:
            logging.error(f"Error checking sold status for {url}: {e}")
