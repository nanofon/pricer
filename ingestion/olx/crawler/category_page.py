async def extract_listing_urls(page, list_url):
    await page.goto(list_url)

    listing_selector = '[data-cy="l-card"]'
    await page.wait_for_selector(listing_selector, timeout=10000)

    elements = await page.query_selector_all(listing_selector)

    urls = []
    for el in elements:
        link = await el.query_selector("a")
        if link:
            href = await link.get_attribute("href")
            if href:
                urls.append(
                    href if href.startswith("http") else f"https://www.olx.pl{href}"
                )
    return urls
