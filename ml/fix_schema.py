import os
import sqlalchemy
from sqlalchemy import create_engine, text

# Setup DB connection
DB_URL = os.getenv(
    "DATABASE_URL", "postgresql://postgres:password@localhost:5433/pricer"
)
engine = create_engine(DB_URL)


def fix_schema():
    with engine.connect() as conn:
        # Check current type
        result = conn.execute(
            text(
                """
            SELECT data_type 
            FROM information_schema.columns 
            WHERE table_name = 'listings' AND column_name = 'discount_ratio_predicted';
        """
            )
        ).fetchone()

        if result:
            current_type = result[0]
            print(f"Current type of discount_ratio_predicted: {current_type}")

            if (
                current_type != "double precision"
                and current_type != "real"
                and current_type != "float"
            ):
                print("Altering column to FLOAT...")
                conn.execute(
                    text(
                        "ALTER TABLE listings ALTER COLUMN discount_ratio_predicted TYPE FLOAT;"
                    )
                )
                conn.commit()
                print("Column altered successfully.")
            else:
                print("Column is already a float type.")
        else:
            print("Column discount_ratio_predicted not found!")


if __name__ == "__main__":
    fix_schema()
