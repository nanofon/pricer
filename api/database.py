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
        SUM(CASE WHEN price_predicted IS NOT NULL AND sold_at IS NULL THEN 1 ELSE 0 END) AS priced_deals,
        SUM(CASE WHEN median_survival_days IS NOT NULL AND sold_at IS NULL THEN 1 ELSE 0 END) AS deals_with_eta,
        SUM(CASE WHEN price_predicted > price AND sold_at IS NULL THEN 1 ELSE 0 END) AS deals_above_predicted
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
    WHERE price_predicted > price AND sold_at IS NULL
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
