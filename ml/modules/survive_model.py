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

MODEL_PATH = "/app/models/survive_model.cbm"

# Define categorical features globally
CATEGORICAL_FEATURES = [
    "category",
    "sku",
    "condition",
    "city",
    "seller_id",
]


def preprocess_data(df):
    df["created_at"] = pd.to_datetime(df["created_at"], utc=True).dt.tz_localize(None)
    df["sold_at"] = pd.to_datetime(
        df["sold_at"], utc=True, errors="coerce"
    ).dt.tz_localize(None)

    # Fill NaT values - use pd.NaT as mask, not fillna (which can cause dtype issues)
    sold_at_mask = df["sold_at"].isna()
    df.loc[sold_at_mask, "sold_at"] = pd.Timestamp.now()

    # Ensure both are datetime64[ns] dtype
    df["sold_at"] = pd.to_datetime(df["sold_at"])
    df["created_at"] = pd.to_datetime(df["created_at"])

    # Calculate time_on_market
    df["time_on_market"] = (df["sold_at"] - df["created_at"]).dt.days
    df["created_at"] = pd.to_datetime(df["created_at"]).astype(int) / 10**9

    df["price"] = df["price"].astype(int)
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
    df = df.drop("sold_at", axis=1)

    return df


def run_predictions(model):
    """Predicts prices for all records where price_predicted is NULL."""
    logger.info("Running prediction pass for new records...")

    # Fetch records that have embeddings but no prediction yet
    query = """
        SELECT id, created_at, sold_at, category, 
               sku, price, condition, city, 
               seller_id, embeddings::text as embeddings
        FROM listings 
        WHERE embeddings IS NOT NULL AND price IS NOT NULL
    """

    df = pd.read_sql(query, engine)

    if df.empty:
        logger.info("No new records to predict.")
        return

    df = preprocess_data(df)

    # Prepare features to match training format
    # Training X columns order (from train_cycle):
    # price, created_at, category, sku, condition, city, seller_id, emb_0...

    # Preprocess creates time_on_market, so we must drop it
    X = df.drop(["id", "time_on_market"], axis=1)

    # Ensure column order matches training
    # Note: price is first in train query. created_at is second.
    cols = (
        ["price", "created_at"]
        + CATEGORICAL_FEATURES
        + [c for c in X.columns if c.startswith("emb_")]
    )
    X = X[cols]

    # Generate predictions and round to INT
    preds = model.predict(X)
    df["median_survival_days"] = np.round(preds).astype(int)

    # Bulk update using a temporary table
    with engine.begin() as conn:
        conn.execute(
            text(
                "CREATE TEMP TABLE tmp_survival_preds (id INT, median_survival_days INT) ON COMMIT DROP"
            )
        )

        # Upload just the mapping
        df[["id", "median_survival_days"]].to_sql(
            "tmp_survival_preds", conn, if_exists="append", index=False
        )

        # Join update - FIXED: use price_predicted instead of pred
        conn.execute(
            text(
                """
            UPDATE listings 
            SET median_survival_days = tmp_survival_preds.median_survival_days
            FROM tmp_survival_preds
            WHERE listings.id = tmp_survival_preds.id
        """
            )
        )

    logger.info(f"Successfully updated {len(df)} records with median_survival_days.")


def train_cycle():
    # 2. FETCH DATA (Excluding zero prices)
    query = """
        SELECT price, created_at, sold_at, category, 
               sku, condition, city, 
               seller_id, embeddings::text as embeddings
        FROM listings 
        WHERE price > 0 AND embeddings IS NOT NULL
    """
    df = pd.read_sql(query, engine)

    df = preprocess_data(df)

    if df["time_on_market"].value_counts().shape[0] < 2:
        logger.info("Not enough data to train yet...")
        return None

    # 3. DEFINE X and y
    y = df["time_on_market"]
    X = df.drop("time_on_market", axis=1)

    logger.info(f"Training data shape: X={X.shape}, y={y.shape}")

    # 5. INITIALIZE MODEL
    model = CatBoostRegressor(
        iterations=1000,
        learning_rate=0.05,
        depth=6,
        loss_function="Quantile:alpha=0.5",
        verbose=100,
    )

    logger.info("Model initialized")

    # 6. TRAINING (Incremental if possible)
    if os.path.exists(MODEL_PATH):
        logger.info(f"Found existing model at {MODEL_PATH}. Resuming training...")
        try:
            model.fit(X, y, cat_features=CATEGORICAL_FEATURES, init_model=MODEL_PATH)
        except Exception as e:
            logger.warning(
                f"Incremental training failed: {e}. Falling back to training from scratch..."
            )
            model.fit(X, y, cat_features=CATEGORICAL_FEATURES)
    else:
        logger.info("No existing model found. Training survival model from scratch...")
        model.fit(X, y, cat_features=CATEGORICAL_FEATURES)

    # 7. PERSIST
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    model.save_model(MODEL_PATH)
    logger.info(f"Survival model saved successfully at {MODEL_PATH}")
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
