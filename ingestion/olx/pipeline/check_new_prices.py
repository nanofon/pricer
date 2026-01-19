import asyncio
import logging
import random
import re
from playwright.async_api import async_playwright
from storage.session import init_db
from storage.repository import (
    get_listings_without_new_price,
    update_listing_new_price,
    update_listing_new_price_not_found,
)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"


async def get_ceneo_price(page, query, listing_price):
    try:
        logging.info(f"Searching Ceneo for: {query}")
        # Build search URL
        search_url = f"https://www.ceneo.pl/;szukaj-{query};0112-1.htm"
        await page.goto(search_url)

        # Strategies:
        # 1. Look for product list items on search page.
        # 2. Extract price from the first relevant item.

        # Selectors for search results
        # Items: .js_category-list-item (or .cat-prod-row)
        # Price: .price-format

        # Wait for results or "not found" message
        try:
            await page.wait_for_selector(
                ".js_category-list-item, .cat-prod-row, .product-top__price, .product-offers__price, .not-found",
                timeout=5000,
            )
        except:
            logging.info("No results selector found (timeout).")
            return None

        # Check for explicit "not found" element
        if await page.query_selector(".not-found"):
            logging.info(f"No results found for '{query}' on Ceneo.")
            return None

        # Check list items - robust selector for different Ceneo layouts
        product_rows = await page.query_selector_all(
            ".js_category-list-item, .cat-prod-row"
        )

        prices = []

        if product_rows:
            logging.info(f"Found {len(product_rows)} products on search page.")
            # Iterate over first few results and get prices
            for row in product_rows:
                price_elem = await row.query_selector(".price-format")
                if price_elem:
                    text_price = await price_elem.inner_text()
                    # cleanup text
                    clean_price = (
                        text_price.replace(",", ".").replace(" ", "").replace("zł", "")
                    )
                    try:
                        prices.append(float(clean_price))
                    except ValueError:
                        pass
        else:
            # Check if we are on a product page
            price_elem = await page.query_selector(
                ".product-top__price .price-format"
            )  # check top price
            if not price_elem:
                price_elem = await page.query_selector(
                    ".product-offers__price .price-format"
                )  # or offers price

            if price_elem:
                text_price = await price_elem.inner_text()
                clean_price = (
                    text_price.replace(",", ".").replace(" ", "").replace("zł", "")
                )
                try:
                    prices.append(float(clean_price))
                except ValueError:
                    pass

        if prices:
            min_price = min([p for p in prices if p > listing_price])
            logging.info(f"Min price found: {min_price}")
            return min_price

        return None

    except Exception as e:
        logging.error(f"Error scraping Ceneo for {query}: {e}")
        return None


async def check_new_prices_batch(session, page, limit=20):
    """
    Checks for new prices for a batch of listings.
    Returns True if any items were processed, False otherwise.
    """
    listings = get_listings_without_new_price(session, limit=limit)

    if not listings:
        logging.info("No listings to check for new prices.")
        return False

    logging.info(f"Checking new prices for {len(listings)} listings...")

    for row in listings:
        listing_id = row.id
        raw_data = row.raw_data

        title = raw_data.get("name")

        if not title:
            logging.warning(f"No name for listing {listing_id}, skipping.")
            update_listing_new_price_not_found(session, listing_id)
            continue

        listing_price = raw_data.get("price", 0)

        price = await get_ceneo_price(page, title, listing_price)

        if price:
            update_listing_new_price(session, listing_id, price)
            logging.info(f"Updated listing {listing_id} with price {price}")
        else:
            update_listing_new_price_not_found(session, listing_id)
            logging.info(f"Price not found for listing {listing_id}, marked as -1")

        sleep_time = random.uniform(2, 5)
        await asyncio.sleep(sleep_time)

    return True


async def check_new_prices_loop():
    session = init_db()
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent=USER_AGENT)
        page = await context.new_page()

        try:
            while True:
                processed = await check_new_prices_batch(session, page, limit=20)
                if not processed:
                    logging.info("Sleeping...")
                    await asyncio.sleep(60)
        except Exception as e:
            logging.error(f"Critical error in check_new_prices loop: {e}")
        finally:
            session.close()
            await browser.close()


if __name__ == "__main__":
    asyncio.run(check_new_prices_loop())
