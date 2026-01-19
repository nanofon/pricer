import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_stats(db):
    sql = text(
        """
    SELECT
        SUM(CASE WHEN sold_at IS NULL THEN 1 ELSE 0 END) AS total_current_deals,
        SUM(CASE WHEN embeddings IS NOT NULL AND sold_at IS NULL THEN 1 ELSE 0 END) AS vectorized_deals,
        SUM(CASE WHEN price_new > 0 AND sold_at IS NULL THEN 1 ELSE 0 END) AS price_new_known_deals,
        SUM(CASE WHEN price_new > 0 AND sold_at IS NULL AND price_predicted > 0 THEN 1 ELSE 0 END) AS priced_deals,
        SUM(CASE WHEN price_predicted > price AND sold_at IS NULL THEN 1 ELSE 0 END) AS deals_above_predicted,
        SUM(CASE WHEN price_predicted > price AND sold_at IS NULL AND is_illiquid = false AND is_invalid = false THEN 1 ELSE 0 END) AS valid_deals,
        SUM(CASE WHEN median_survival_days IS NOT NULL AND sold_at IS NULL THEN 1 ELSE 0 END) AS deals_with_eta
    FROM listings;
    """
    )
    result = db.execute(sql)
    return result.mappings().all()


def get_listings(db, page: int = 1, size: int = 20):
    offset = (page - 1) * size
    sql = text(
        f"""
    SELECT
        id,
        name,
        description,
        category,
        city,
        image,
        url,
        price,
        price_predicted,
        price_predicted - price as price_difference,
        median_survival_days,
        EXTRACT(EPOCH FROM (NOW() - created_at)) / 86400 AS current_days_on_market
    FROM listings
    WHERE sold_at IS NULL AND is_invalid = false AND is_illiquid = false AND is_pending_repricing = false AND price_predicted > price
    ORDER BY price_difference DESC
    LIMIT {size} OFFSET {offset}
    """
    )
    result = db.execute(sql)
    return result.mappings().all()


def get_categories(db, page: int = 1, size: int = 20):
    offset = (page - 1) * size
    sql = text(
        f"""
    SELECT 
        category,
        COUNT(*) as deal_count,
        SUM(price_predicted - price) as total_diff,
        AVG(price_predicted - price) as mean_diff,
        AVG(median_survival_days) as predicted_median_survival_days,
        AVG(EXTRACT(EPOCH FROM (NOW() - created_at)) / 86400) as mean_current_days_on_market
    FROM listings
    WHERE price_predicted > price AND sold_at IS NULL
    GROUP BY category
    ORDER BY total_diff DESC
    LIMIT {size} OFFSET {offset}
    """
    )
    result = db.execute(sql)
    return result.mappings().all()


def get_schema(db):
    sql = text("""SELECT * FROM listings LIMIT 1""")
    result = db.execute(sql)
    return result.mappings().all()


def get_next_best(db, exclude_tuple: tuple[int]):
    sql = text(
        """
    SELECT
        id,
        name,
        description,
        category,
        city,
        image,
        url,
        price,
        price_predicted,
        price_predicted - price as price_difference,
        median_survival_days,
        EXTRACT(EPOCH FROM (NOW() - created_at)) / 86400 AS current_days_on_market,
        price_new,
        is_invalid
    FROM listings
    WHERE sold_at IS NULL AND id NOT IN :exclude_tuple AND is_pending_repricing = false AND price_predicted > price AND NOT is_illiquid
    ORDER BY price_difference DESC
    LIMIT 1
    """
    )
    result = db.execute(sql, {"exclude_tuple": exclude_tuple})
    return result.mappings().first()


def update_price_new(db, listing_id: int, price: float):
    sql = text(
        """
    UPDATE listings
    SET price_new = :price,
    is_pending_repricing = true
    WHERE id = :listing_id
    RETURNING id
    """
    )
    result = db.execute(sql, {"listing_id": listing_id, "price": int(price)})
    db.commit()
    updated_row = result.mappings().first()
    if not updated_row:
        raise HTTPException(status_code=404, detail="Listing not found")
    return {"status": "success"}


def set_illiquid(db, listing_id: int):
    sql = text(
        """
    UPDATE listings
    SET is_illiquid = true
    WHERE id = :listing_id
    RETURNING id
    """
    )
    result = db.execute(sql, {"listing_id": listing_id})
    db.commit()
    updated_row = result.mappings().first()
    if not updated_row:
        raise HTTPException(status_code=404, detail="Listing not found")
    return {"status": "success"}


def set_invalid(db, listing_id: int):
    sql = text(
        """
    UPDATE listings
    SET is_invalid = true
    WHERE id = :listing_id
    RETURNING id
    """
    )
    result = db.execute(sql, {"listing_id": listing_id})
    db.commit()
    updated_row = result.mappings().first()
    if not updated_row:
        raise HTTPException(status_code=404, detail="Listing not found")
    return {"status": "success"}
