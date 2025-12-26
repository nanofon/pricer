import os
import time
import logging
import psycopg2
from psycopg2.extras import execute_values
from sentence_transformers import SentenceTransformer

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ml-worker")

# Configuration
DB_URL = os.getenv("DATABASE_URL", "postgres://postgres:password@db:5432/pricer")
MODEL_NAME = "paraphrase-multilingual-mpnet-base-v2"
BATCH_SIZE = 50

# Initialize Model (This will now load from the local cache)
logger.info(f"Loading model: {MODEL_NAME}")
model = SentenceTransformer(MODEL_NAME)


def get_connection():
    return psycopg2.connect(DB_URL)


def process_undone_listings():
    with get_connection() as conn:
        with conn.cursor() as cur:
            # 1. Fetch listings that need vectors
            cur.execute(
                """
                SELECT id, name, description 
                FROM listings 
                WHERE embeddings IS NULL 
                LIMIT %s
            """,
                (BATCH_SIZE,),
            )
            rows = cur.fetchall()

            if not rows:
                return 0

            # 2. Prepare text (Combining Title + Description for better context)
            ids = [row[0] for row in rows]
            # We clean None values to empty strings to avoid errors
            texts = [f"{row[1] or ''} {row[2] or ''}".strip() for row in rows]

            # 3. Generate Embeddings
            logger.info(f"Encoding batch of {len(texts)} listings...")
            embeddings = model.encode(texts, normalize_embeddings=True)

            # 4. Bulk Update using pgvector-friendly format
            # We convert numpy array to list for psycopg2
            data_to_update = [(embeddings[i].tolist(), ids[i]) for i in range(len(ids))]

            execute_values(
                cur,
                """
                UPDATE listings SET embeddings = v.vec
                FROM (VALUES %s) AS v(vec, id)
                WHERE listings.id = v.id
            """,
                data_to_update,
            )

            conn.commit()
            return len(ids)


if __name__ == "__main__":
    logger.info("Worker started. Waiting for new listings...")
    while True:
        try:
            processed_count = process_undone_listings()
            if processed_count > 0:
                logger.info(f"Successfully processed {processed_count} listings.")
            else:
                # Idle: wait a bit before checking again
                time.sleep(300)

        except Exception as e:
            logger.error(f"Error in worker loop: {e}")
            time.sleep(300)  # Wait before retry
