# Interview Task -- Django REST API

A production-ready backend API built using **Django Rest Framework**,
demonstrating clean architecture, authentication, filtering, pagination,
order lifecycle management, stock handling, and OpenAPI documentation.

------------------------------------------------------------------------

## Tech Stack

-   Python 3.10+
-   Django
-   Django REST Framework
-   djangorestframework-simplejwt (JWT Authentication)
-   drf-spectacular (OpenAPI / Swagger)
-   SQLite (default database)
-   Gunicorn (WSGI server)
-   Docker & Docker Compose
-   uv (Python package manager)
-   pytest (testing)

------------------------------------------------------------------------

## Features

-   Product CRUD with search and advanced filtering
-   Category hierarchy (parent--child)
-   Order creation and status updates
-   Automatic stock management
-   Order status history tracking
-   JWT-based authentication
-   Pagination support
-   OpenAPI documentation (Swagger & Redoc)
-   Dockerized setup
-   Middleware-based request context handling

------------------------------------------------------------------------

## Local Setup (Using uv)

### 1. Clone the Repository

``` bash
git clone <repository-url>
cd interview_task
```

### Environment Variables

Copy the example environment file and update values as needed:

```bash
cp env.example .env

### 2. Install Dependencies

``` bash
pip install uv
uv sync
```

### 3. Apply Migrations

``` bash
python manage.py migrate
```

### 4. Create Superuser

``` bash
python manage.py createsuperuser
```

### 5. Run Development Server

``` bash
python manage.py runserver
```

------------------------------------------------------------------------

## Docker Setup

``` bash
docker-compose up --build
```

------------------------------------------------------------------------

## Authentication (JWT)

``` http
POST /api/auth/token/
```

Use header:

    Authorization: Bearer <access_token>

------------------------------------------------------------------------

## API Documentation

-   Swagger: `/api/schema/swagger-ui/`
-   Redoc: `/api/schema/redoc/`
-   OpenAPI: `/api/schema/`

------------------------------------------------------------------------

## Product Filtering

All filters are **AND-based**.

Example:

    /api/products/?active=1&min_price=1000&in_stock=true

------------------------------------------------------------------------

## Order Lifecycle

-   Order creation decreases stock
-   Status changes tracked in history
-   Cancellation restores stock
-   Status change timestamp auto-updated

------------------------------------------------------------------------

## Testing

``` bash
pytest
```

Minimum coverage includes: - Models - APIs - Signals - Middleware

------------------------------------------------------------------------

## Author

Anish Poudel
