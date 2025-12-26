from fastapi import FastAPI, Depends, Query, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from .database import get_db, get_listings, get_stats, get_categories, get_schema
from fastapi.middleware.cors import CORSMiddleware
import logging
import traceback

from typing import Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="OLX Listings API")

origins = [
    "http://localhost:3000",
    "http://localhost:8000",
    "http://localhost:4321",
    "http://127.0.0.1:4321",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def debug_exception_handler(request: Request, exc: Exception):
    error_msg = "".join(traceback.format_exception(None, exc, exc.__traceback__))
    logger.error(f"Global exception: {error_msg}")
    print(error_msg)  # Force print
    return JSONResponse(
        status_code=500,
        content={"message": "Internal Server Error", "detail": str(exc)},
    )


@app.get("/")
def root():
    return {"message": "OLX Listings API is running. Go to /docs for Swagger UI."}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/stats")
def stats(db: Session = Depends(get_db)):
    stats = get_stats(db)
    return stats


@app.get("/categories")
def categories(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Items per page"),
):
    categories = get_categories(db, page, size)
    return categories


@app.get("/listings")
def listings(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Items per page"),
):
    listings = get_listings(db, page, size)
    return listings


@app.get("/schema")
def schema(db: Session = Depends(get_db)):
    schema = get_schema(db)
    return schema
