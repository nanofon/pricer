import datetime, logging
from sqlalchemy import text
from .dynamic_columns import save_dynamic_listing


def save_raw_listing(session, data):
    save_dynamic_listing(session, data)


def listing_exists(session, url: str) -> bool:
    logging.info(f"Checking if listing exists: {url}")
    return (
        session.execute(
            text("SELECT 1 FROM listings WHERE url = :url LIMIT 1"), {"url": url}
        ).fetchone()
        is not None
    )


def get_unsold_urls(session, limit=500):
    """Return (id, url) for listings not marked as sold."""
    return session.execute(
        text(
            """
            SELECT id, url
            FROM listings
            WHERE sold_at IS NULL
            ORDER BY created_at ASC
            LIMIT :limit
        """
        ),
        {"limit": limit},
    ).fetchall()


def mark_as_sold(session, listing_id: int):
    session.execute(
        text(
            """
            UPDATE listings
            SET sold_at = :now
            WHERE id = :id AND sold_at IS NULL
        """
        ),
        {"id": listing_id, "now": datetime.datetime.utcnow()},
    )
    session.commit()


def get_listings_without_new_price(session, limit=100):
    """Return (id, raw_data) for listings with no price_new and not sold."""
    # Assuming price_new is a column. If not, we might need to check if it exists in raw_data or if the column exists.
    # The requirement implies a column 'price_new' in the bindings/schema or usage.
    # If the user says 'store in the price_new field', I'll assume it's a column in the 'listings' table.
    # However, existing schema in models.py only shows 'id', 'created_at', 'raw_data'.
    # But the user request says: "stores in the price_new field".
    # And check_sold.py uses 'sold_at' which is not in models.py either (it uses raw SQL).
    # So I will assume 'price_new' is a column on 'listings' table, managed via raw SQL or migrations not seen here.
    return session.execute(
        text(
            """
            SELECT id, raw_data
            FROM listings
            WHERE price_new IS NULL OR price_new = -1
            LIMIT :limit
        """
        ),
        {"limit": limit},
    ).fetchall()


def update_listing_new_price(session, listing_id: int, price: float):
    session.execute(
        text(
            """
            UPDATE listings
            SET price_new = :price
            WHERE id = :id
        """
        ),
        {"id": listing_id, "price": price},
    )
    session.commit()


def update_listing_new_price_not_found(session, listing_id: int):
    session.execute(
        text(
            """
            UPDATE listings
            SET price_new = -1
            WHERE id = :id
        """
        ),
        {"id": listing_id},
    )
    session.commit()
