# --- STAGE 1: Shared Base ---
FROM python:3.10-slim AS base
WORKDIR /app
# Install system deps
RUN apt-get update && apt-get install -y libpq-dev gcc && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir --upgrade pip
# Install common libs
RUN pip install --no-cache-dir sqlalchemy psycopg2-binary pandas numpy

# --- STAGE 2: Embedder (Heavy ML) ---
FROM base AS embedder
# Install Torch CPU only (save space)
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu
RUN pip install --no-cache-dir sentence-transformers
# Pre-download model
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('paraphrase-multilingual-mpnet-base-v2')"
# Copy folder structure so imports work
COPY embedder/ ./embedder/
# Run from the module
CMD ["python", "-u", "embedder/embedder.py"]

# --- STAGE 3: ML (CatBoost) ---
FROM base AS ml
RUN pip install --no-cache-dir catboost
COPY ml/ /app/
CMD ["python", "-u", "run_all.py"]

# --- STAGE 4: Backend (FastAPI) ---
FROM base AS api
RUN pip install --no-cache-dir fastapi uvicorn
# This CMD works because we preserved the /api folder
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]