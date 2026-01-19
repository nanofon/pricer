import os
import sqlalchemy
from sqlalchemy import create_engine, text

# Setup DB connection
DB_URL = os.getenv(
    "DATABASE_URL", "postgresql://postgres:password@localhost:5433/pricer"
)
engine = create_engine(DB_URL)


def debug_listings():
    with engine.connect() as conn:
        print("--- Schema Check ---")
        # Check columns
        result = conn.execute(
            text(
                """
            SELECT column_name, data_type, generation_expression
            FROM information_schema.columns 
            WHERE table_name = 'listings';
        """
            )
        ).fetchall()
        columns = {row[0]: (row[1], row[2]) for row in result}
        print(f"price_predicted info: {columns.get('price_predicted', 'MISSING')}")
        print(
            f"discount_ratio_predicted type: {columns.get('discount_ratio_predicted', 'MISSING')}"
        )
        print(
            f"is_pending_repricing type: {columns.get('is_pending_repricing', 'MISSING')}"
        )

        print("\n--- Data Counts ---")

        queries = [
            ("Total listings", "SELECT COUNT(*) FROM listings"),
            ("Unsold", "SELECT COUNT(*) FROM listings WHERE sold_at IS NULL"),
            (
                "Unsold & Not Pending Repricing",
                "SELECT COUNT(*) FROM listings WHERE sold_at IS NULL AND is_pending_repricing = false",
            ),
            (
                "Unsold & Not Pending & Not Illiquid",
                "SELECT COUNT(*) FROM listings WHERE sold_at IS NULL AND is_pending_repricing = false AND NOT is_illiquid",
            ),
            (
                "Unsold & Not Pending & Not Illiquid & Price Predicted > Price",
                "SELECT COUNT(*) FROM listings WHERE sold_at IS NULL AND is_pending_repricing = false AND NOT is_illiquid AND price_predicted > price",
            ),
            (
                "Price Predicted IS NULL",
                "SELECT COUNT(*) FROM listings WHERE price_predicted IS NULL",
            ),
            (
                "Price Predicted NOT NULL",
                "SELECT COUNT(*) FROM listings WHERE price_predicted IS NOT NULL",
            ),
            (
                "Discount Ratio Predicted NOT NULL",
                "SELECT COUNT(*) FROM listings WHERE discount_ratio_predicted IS NOT NULL",
            ),
            (
                "Price New IS NULL",
                "SELECT COUNT(*) FROM listings WHERE price_new IS NULL",
            ),
            (
                "Price New = -1 (Not Found)",
                "SELECT COUNT(*) FROM listings WHERE price_new = -1",
            ),
            (
                "Price New > 0 (Found)",
                "SELECT COUNT(*) FROM listings WHERE price_new > 0",
            ),
            (
                "is_pending_repricing IS NULL",
                "SELECT COUNT(*) FROM listings WHERE is_pending_repricing IS NULL",
            ),
            (
                "is_pending_repricing = true",
                "SELECT COUNT(*) FROM listings WHERE is_pending_repricing = true",
            ),
            (
                "is_pending_repricing = false",
                "SELECT COUNT(*) FROM listings WHERE is_pending_repricing = false",
            ),
            (
                "Price New > 0 & Discount Ratio NOT NULL",
                "SELECT COUNT(*) FROM listings WHERE price_new > 0 AND discount_ratio_predicted IS NOT NULL",
            ),
            (
                "Price New > 0 & Discount Ratio NOT NULL & Generated Price > Price",
                "SELECT COUNT(*) FROM listings WHERE price_new > 0 AND discount_ratio_predicted IS NOT NULL AND (price_new * discount_ratio_predicted) > price",
            ),
        ]

        for label, sql in queries:
            try:
                count = conn.execute(text(sql)).scalar()
                print(f"{label}: {count}")
            except Exception as e:
                print(f"{label}: ERROR - {e}")

        print("\n--- Sample Good Deals ---")
        sample_sql = """
            SELECT id, price, price_new, discount_ratio_predicted, price_predicted, is_pending_repricing
            FROM listings
            WHERE price_new > 0 AND discount_ratio_predicted IS NOT NULL AND (price_new * discount_ratio_predicted) > price
            LIMIT 5
        """
        rows = conn.execute(text(sample_sql)).fetchall()
        for row in rows:
            print(
                f"ID: {row[0]}, Price: {row[1]}, Price New: {row[2]}, Ratio: {row[3]}, Pred: {row[4]}, Pending: {row[5]}"
            )


if __name__ == "__main__":
    debug_listings()
