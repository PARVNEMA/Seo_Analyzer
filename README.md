# FastAPI Template

A production-ready, reusable FastAPI boilerplate repository for quickly starting scalable backend projects.

## Features
- **FastAPI**: Modern, fast web framework for building APIs.
- **SQLAlchemy 2.0 (Async)**: ORM for database interactions.
- **Pydantic v2**: Data validation and settings management.
- **Alembic**: Database migrations.
- **PostgreSQL**: Robust relational database.
- **Redis & Celery**: Background task processing (optional).
- **JWT Authentication**: Secure user login and access control.
- **Docker & Docker Compose**: Containerized development and production environments.
- **Pre-commit Hooks**: Linting, formatting, and type-checking before commits.
- **GitHub Actions**: Automated CI/CD pipeline.

## Architecture Overview
```
project-root/
├── app/
│   ├── main.py                 # FastAPI app instance, startup/shutdown
│   ├── core/                   # Configuration, security, logging, exceptions
│   ├── api/                    # API routers grouped by version and resource
│   ├── models/                 # SQLAlchemy ORM models
│   ├── schemas/                # Pydantic request/response models
│   ├── crud/                   # DB access layer (repository pattern)
│   ├── controllers/            # Business logic layer
│   ├── db/                     # DB session, engine, and initialization
│   ├── dependencies/           # Reusable FastAPI Depends() functions
│   ├── middlewares/            # Custom HTTP middlewares
│   └── utils/                  # Helper utilities
├── alembic/                    # Database migrations
├── tests/                      # Unit and integration tests
├── Dockerfile                  # Multi-stage build for production
├── docker-compose.yml          # Services for local dev (app, db, redis)
└── Makefile                    # Common commands
```

## Quick Start

### Local Development (without Docker)
1. Install dependencies:
   ```
   uv pip install -r requirements.txt
   ```
2. Setup environment variables:
   ```
   .venc\Scripts\activate
   cp .env.example .env

   # Edit .env with your database credentials
   ```
3. Run database migrations:
   ```bash
   make migrate
   ```
4. Start the server:
   ```bash
   make run
   ```

### Using Docker Compose
1. Setup environment variables:
   ```bash
   cp .env.example .env
   ```
2. Start all services (App, PostgreSQL, Redis):
   ```bash
   make docker-up
   ```

## Environment Variables
See `.env.example` for all configurable environment variables.

## Documentation
Once running, visit:
- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

## Testing
Run the test suite with coverage:
```bash
make test
```

## Extending the Template
1. Create a new model in `app/models/`.
2. Define Pydantic schemas in `app/schemas/`.
3. Create a CRUD class in `app/crud/`.
4. Create a controller in `app/controllers/`.
5. Add endpoints in `app/api/v1/endpoints/`.
6. Include the router in `app/api/v1/api.py`.
7. Generate an Alembic migration: `make migration msg="Added new model"`.

## License
MIT
