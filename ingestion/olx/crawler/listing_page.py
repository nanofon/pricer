import datetime, json, logging

logging.basicConfig(level=logging.INFO)


async def extract_listing_details(page, url):
    await page.goto(url)
    await page.wait_for_load_state("domcontentloaded")

    data = {
        "url": url,
        "crawled_at": str(datetime.datetime.now()),
    }

    try:
        ld_script = await page.query_selector('script[type="application/ld+json"]')

        if ld_script:
            ld = json.loads(await ld_script.inner_text())
            data["name"] = ld.get("name", None)
            data["description"] = ld.get("description", None)
            data["category"] = ld.get("category", None)
            data["image"] = ld.get("image", [None])[0]
            data["sku"] = ld.get("sku", None)
            data["city"] = (
                ld.get("offers", None).get("areaServed", None).get("name", None)
            )
            data["price"] = (
                int(ld.get("offers", None).get("price", None))
                if "offers" in ld
                else None
            )
            match ld.get("offers", None).get("itemCondition", None):
                case "https://schema.org/NewCondition":
                    data["condition"] = "new"
                case "https://schema.org/UsedCondition":
                    data["condition"] = "used"
                case "https://schema.org/RefurbishedCondition":
                    data["condition"] = "refurbished"
                case "https://schema.org/DamagedCondition":
                    data["condition"] = "damaged"
                case _:
                    data["condition"] = "unknown"
    except Exception as e:
        logging.error(f"crawler -> listing_page: Error parsing JSON-LD for {url}: {e}")

    try:
        user_link = await page.query_selector('a[href*="/oferty/uzytkownik/"]')
        if user_link:
            seller_url = await user_link.get_attribute("href")
            data["seller_id"] = seller_url.split("/")[3] if seller_url else None
    except Exception as e:
        logging.error(f"crawler -> listing_page: Error parsing seller for {url}: {e}")
    return data
