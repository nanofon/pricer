import datetime
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
