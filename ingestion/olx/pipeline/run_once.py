import random, asyncio, logging
from playwright.async_api import async_playwright
from config import OLX_URLS, USER_AGENT
from crawler.heartbeat import update_heartbeat
from crawler.listing_page import extract_listing_details
from crawler.category_page import extract_listing_urls
from storage.session import init_db
from storage.repository import save_raw_listing, listing_exists
from pipeline.check_sold import check_sold_listings
from pipeline.check_new_prices import check_new_prices_batch

logging.basicConfig(level=logging.INFO)


async def run_once():
    session = init_db()

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent=USER_AGENT)
        page = await context.new_page()

        for category_url in OLX_URLS:
            try:
                await page.goto(category_url)
            except Exception as e:
                logging.error(
                    f"pipeline -> run_once: Error going to {category_url}: {e}"
                )
                continue
            try:
                await page.click("button#onetrust-accept-btn-handler", timeout=5000)
            except:
                pass

            try:
                current_url = category_url
                page_number = 1
                consecutive_duplicates = 0
 
                update_heartbeat()

                logging.info(
                    f"pipeline -> run_once: --- Processing {category_url} Page {page_number} ---"
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
                            break
                        else:
                            consecutive_duplicates = 0

                    data = await extract_listing_details(page, url)
                    save_raw_listing(session, data)
                    logging.info(f"pipeline -> run_once: Saved listing: {url}")
                    await asyncio.sleep(random.uniform(1, 2.5))

                page_number += 1

                if "?" in current_url:
                    # Remove existing page parameter if present
                    base_url = current_url.split("?")[0]
                    current_url = f"{base_url}?page={page_number}"
                else:
                    current_url = f"{url}?page={page_number}"

                batch_count = 1

                while True:
                    logging.info(
                        f"pipeline -> run_once: Checking prices for a batch {batch_count}"
                    )
                    if not await check_new_prices_batch(session, page, limit=20):
                        break
                    batch_count += 1

                batch_count = 1

                while True:
                    logging.info(
                        f"pipeline -> run_once: Checking sold status for a batch {batch_count}"
                    )
                    if not await check_sold_listings(session, page, batch_size=200):
                        break
                    batch_count += 1

                logging.info(
                    f"pipeline -> run_once: Moving to page {page_number}: {current_url}"
                )
                await asyncio.sleep(random.uniform(2, 4))

            except Exception as e:
                logging.error(
                    f"pipeline -> run_once: Error processing {category_url}: {e}"
                )
                continue

            finally:
                logging.info(f"pipeline -> run_once: Closing session and browser")
                session.close()
                await browser.close()
