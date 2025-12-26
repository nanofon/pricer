import json
from playwright.async_api import TimeoutError as PlaywrightTimeout


async def is_listing_active(page, url: str) -> bool:
    """
    Returns False if listing is sold / removed.
    """

    try:
        resp = await page.goto(url, wait_until="domcontentloaded", timeout=15000)
    except PlaywrightTimeout:
        return False

    if resp is None or resp.status >= 400:
        return False

    # Wait for page to settle
    try:
        await page.wait_for_load_state("networkidle", timeout=5000)
    except PlaywrightTimeout:
        pass

    # Check for "sold" or "removed" indicators
    # Option 1: Look for specific error elements
    try:
        error_element = await page.query_selector('[data-testid="error-page"]')
        if error_element:
            return False
    except:
        pass

    # Option 2: Check JSON-LD for price/offers (active listings have price data)
    try:
        ld_script = await page.query_selector('script[type="application/ld+json"]')
        if ld_script:
            ld_content = await ld_script.inner_text()
            ld_data = json.loads(ld_content)
            # If listing has offers with price, it's active
            if "offers" in ld_data and "price" in ld_data.get("offers", {}):
                return True
        # If no JSON-LD or no price data, continue to text-based checks
    except Exception:
        pass

    # Option 3: Text-based check as fallback
    content = await page.text_content("body") or ""

    SOLD_MARKERS = [
        "ogłoszenie nie jest już dostępne",
        "ogłoszenie zostało zakończone",
        "ogłoszenie usunięte",
        "nie znaleziono",
    ]

    return not any(marker in content.lower() for marker in SOLD_MARKERS)
