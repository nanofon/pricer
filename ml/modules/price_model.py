import os
import time
import pandas as pd
import numpy as np
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from sqlalchemy import create_engine, text
from catboost import CatBoostRegressor, Pool

# 1. SETUP ENGINE
DB_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@db:5432/pricer")
engine = create_engine(DB_URL)

MODEL_PATH = "/app/models/price_model.cbm"

# Define categorical features globally
CATEGORICAL_FEATURES = [
    "category",
    "sku",
    "condition",
    "city",
    "seller_id",
]


def preprocess_data(df):
    df["created_at"] = pd.to_datetime(df["created_at"]).astype(int) / 10**9
    df["embeddings"] = df["embeddings"].apply(
        lambda x: [float(val) for val in x.strip("[]").split(",")]
    )

    for col in CATEGORICAL_FEATURES:
        null_count = df[col].isna().sum()
        if null_count > 0:
            logger.warning(f"Column {col} has {null_count} null values")
            df[col] = df[col].fillna("UNKNOWN")

    embeddings_array = np.array(df["embeddings"].tolist())

    embedding_cols = [f"emb_{i}" for i in range(embeddings_array.shape[1])]
    embedding_df = pd.DataFrame(
        embeddings_array, columns=embedding_cols, index=df.index
    )

    df = pd.concat([df, embedding_df], axis=1)
    df = df.drop("embeddings", axis=1)

    return df


def run_predictions(model):
    """Predicts prices for all records where price_predicted is NULL."""
    logger.info("Running prediction pass for new records...")

    # Fetch records that have embeddings but no prediction yet
    query = """
        SELECT id, created_at, category, 
               sku, condition, city, 
               seller_id, embeddings::text as embeddings
        FROM listings 
        WHERE embeddings IS NOT NULL
    """

    df = pd.read_sql(query, engine)

    if df.empty:
        logger.info("No new records to predict.")
        return

    df = preprocess_data(df)

    # Prepare features to match training format
    X = df.drop("id", axis=1)

    # Generate predictions and round to INT
    preds = model.predict(X)
    df["price_predicted"] = np.round(preds).astype(int)

    # Bulk update using a temporary table
    with engine.begin() as conn:
        conn.execute(
            text(
                "CREATE TEMP TABLE tmp_preds (id INT, price_predicted INT) ON COMMIT DROP"
            )
        )

        # Upload just the mapping
        df[["id", "price_predicted"]].to_sql(
            "tmp_preds", conn, if_exists="append", index=False
        )

        # Join update - FIXED: use price_predicted instead of pred
        conn.execute(
            text(
                """
            UPDATE listings 
            SET price_predicted = tmp_preds.price_predicted
            FROM tmp_preds
            WHERE listings.id = tmp_preds.id
        """
            )
        )

    logger.info(f"Successfully updated {len(df)} records with price_predicted.")


def train_cycle():
    # 2. FETCH DATA (Excluding zero prices)
    query = """
        SELECT price, created_at, category, 
               sku, condition, city, 
               seller_id, embeddings::text as embeddings
        FROM listings 
        WHERE price > 0 AND embeddings IS NOT NULL
    """
    df = pd.read_sql(query, engine)

    if len(df) < 100:
        logger.info("Not enough data to train yet...")
        return None

    df = preprocess_data(df)

    # 3. DEFINE X and y
    y = df["price"]
    X = df.drop("price", axis=1)

    logger.info(f"Training data shape: X={X.shape}, y={y.shape}")

    # 5. INITIALIZE MODEL
    model = CatBoostRegressor(
        iterations=500, learning_rate=0.05, loss_function="RMSE", verbose=100
    )

    logger.info("Model initialized")

    # 6. TRAINING (without incremental - not supported with embeddings expanded)
    logger.info("Training pricing model from scratch...")
    model.fit(X, y, cat_features=CATEGORICAL_FEATURES)

    # 7. PERSIST
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    model.save_model(MODEL_PATH)
    logger.info(f"Pricing model saved successfully at {MODEL_PATH}")
    return model


if __name__ == "__main__":
    logger.info("Trainer started")
    while True:
        try:
            model = train_cycle()
            if model is not None:
                run_predictions(model)
            else:
                logger.info("Skipping predictions - no model trained")
        except Exception as e:
            logger.error(f"Training error: {e}", exc_info=True)
        time.sleep(3600)  # Re-check every hour
