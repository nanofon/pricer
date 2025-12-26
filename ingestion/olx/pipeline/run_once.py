import random, asyncio, logging
from playwright.async_api import async_playwright
from config import OLX_URL, USER_AGENT
from crawler.heartbeat import update_heartbeat
from crawler.listing_page import extract_listing_details
from crawler.category_page import extract_listing_urls
from storage.session import init_db
from storage.repository import save_raw_listing, listing_exists
from pipeline.check_sold import check_sold_listings

logging.basicConfig(level=logging.INFO)


async def run_once():
    session = init_db()

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent=USER_AGENT)
        page = await context.new_page()

        try:
            await page.goto(OLX_URL)
            try:
                await page.click("button#onetrust-accept-btn-handler", timeout=5000)
            except:
                pass

            current_url = OLX_URL
            page_number = 1
            consecutive_duplicates = 0

            while True:
                update_heartbeat()

                # DEBUG await check_sold_listings(session, page, batch_size=200)

                logging.info(
                    f"pipeline -> run_once: --- Processing Page {page_number} ---"
                )

                urls = await extract_listing_urls(page, current_url)
                logging.info(f"pipeline -> run_once: Extracted {len(urls)} urls")

                for url in urls:
                    if listing_exists(session, url):
                        consecutive_duplicates += 1
                        if consecutive_duplicates >= 10:
                            logging.info(
                                f"pipeline -> run_once: Too many duplicates, exiting"
                            )
                            return
                    else:
                        consecutive_duplicates = 0

                    data = await extract_listing_details(page, url)
                    save_raw_listing(session, data)
                    logging.info(f"pipeline -> run_once: Saved listing: {url}")
                    await asyncio.sleep(random.uniform(1, 2.5))

                # Build next page URL using ?page= parameter
                page_number += 1

                # Check if base URL already has query parameters
                if "?" in OLX_URL:
                    # Remove existing page parameter if present
                    base_url = OLX_URL.split("?")[0]
                    current_url = f"{base_url}?page={page_number}"
                else:
                    current_url = f"{OLX_URL}?page={page_number}"

                logging.info(
                    f"pipeline -> run_once: Moving to page {page_number}: {current_url}"
                )
                await asyncio.sleep(random.uniform(2, 4))

        finally:
            logging.info(f"pipeline -> run_once: Closing session and browser")
            session.close()
            await browser.close()
