from fastapi import FastAPI, Depends, Query, Request
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy.orm import Session
from .database import (
    get_db,
    get_listings,
    get_stats,
    get_categories,
    get_schema,
    get_next_best,
    update_price_new,
    set_illiquid,
)
import logging
import traceback

from pydantic import BaseModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="OLX Listings API")


@app.exception_handler(Exception)
async def debug_exception_handler(request: Request, exc: Exception):
    error_msg = "".join(traceback.format_exception(None, exc, exc.__traceback__))
    logger.error(f"Global exception: {error_msg}")
    print(error_msg)  # Force print
    return JSONResponse(
        status_code=500,
        content={"message": "Internal Server Error", "detail": str(exc)},
    )


@app.get("/api")
def root():
    return RedirectResponse(url="/api/docs")


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/stats")
def stats(db: Session = Depends(get_db)):
    stats = get_stats(db)
    return stats


@app.get("/api/categories")
def categories(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Items per page"),
):
    categories = get_categories(db, page, size)
    return categories


@app.get("/api/listings")
def listings(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Items per page"),
):
    listings = get_listings(db, page, size)
    return listings


@app.get("/api/schema")
def schema(db: Session = Depends(get_db)):
    schema = get_schema(db)
    return schema


@app.get("/api/listings/next-best")
def next_best(
    db: Session = Depends(get_db),
    exclude: str = Query(None, description="Comma-separated list of IDs to exclude"),
):
    if exclude:
        ids_list = [int(x.strip()) for x in exclude.split(",") if x.strip()]
    else:
        ids_list = []
    excluded_tuple = tuple(ids_list) if ids_list else (0,)
    listings = get_next_best(db, excluded_tuple)
    return listings


class PriceUpdate(BaseModel):
    price: float


@app.post("/api/listings/{listing_id}/price_new")
def price_new(
    listing_id: int,
    payload: PriceUpdate,
    db: Session = Depends(get_db),
):
    update_price_new(db, listing_id, payload.price)
    return {
        "status": "success",
        "message": f"Listing {listing_id} price of new updated successfully",
    }


@app.post("/api/listings/{listing_id}/illiquid")
def illiquid(
    listing_id: int,
    db: Session = Depends(get_db),
):
    set_illiquid(db, listing_id)
    return {
        "status": "success",
        "message": f"Listing {listing_id} marked as illiquid",
    }


@app.post("/api/listings/{listing_id}/invalid")
def invalid(
    listing_id: int,
    db: Session = Depends(get_db),
):
    set_invalid(db, listing_id)
    return {
        "status": "success",
        "message": f"Listing {listing_id} marked as invalid",
    }
