# OLX Listings API

This is a FastAPI-based service that serves OLX listing data stored in a PostgreSQL database. It is designed to work in conjunction with the ingestion crawler.

## Prerequisites

- **Python 3.8+**
- **PostgreSQL**: A running PostgreSQL instance (or Docker container).
- **Environment Variables**: A `.env` file configured with the database connection string.

## Installation

1.  **Create a virtual environment** (recommended):
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

2.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configuration**:
    Ensure you have offset `.env` file in this directory with the `DATABASE_URL` variable:
    ```env
    DATABASE_URL=postgresql://user:password@localhost:5432/dbname
    ```

## Running the API

Start the development server using Uvicorn:

```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`.

## Endpoints

### `GET /`
Health check endpoint.
- **Response**: `{"message": "OLX Listings API is running. Go to /docs for Swagger UI."}`

### `GET /listings`
Retrieve a paginated list of listings.
- **Query Parameters**:
    - `page` (int): Page number (default: 1).
    - `size` (int): Number of items per page (default: 50, max: 100).
- **Response**: A list of listing objects.

### Documentation
Interactive API documentation (Swagger UI) is available at:
- `http://localhost:8000/docs`

## Development
- `main.py`: Entry point for the FastAPI application.
- `database.py`: Database connection and query logic (SQLAlchemy).
- `test_db.py`: Script to test database connectivity.
