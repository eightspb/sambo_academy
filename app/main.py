"""Main FastAPI application."""
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.templating import Jinja2Templates
from contextlib import asynccontextmanager

from app.config import settings
from app.database import engine, Base
from app.api import auth, groups, students, attendance, subscriptions, payments, tournaments, settings as settings_api


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events for the application."""
    # Startup: Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield
    
    # Shutdown
    await engine.dispose()


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description="PWA application for Sambo Academy management",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(auth.router)
app.include_router(groups.router)
app.include_router(students.router)
app.include_router(attendance.router)
app.include_router(subscriptions.router)
app.include_router(payments.router)
app.include_router(tournaments.router)
app.include_router(settings_api.router)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Mount templates for component loading
app.mount("/templates", StaticFiles(directory="templates"), name="templates")

# Serve templates
@app.get("/")
async def root():
    """Serve the main page."""
    return FileResponse("templates/index.html")


@app.get("/login")
async def login_page():
    """Serve the login page."""
    return FileResponse("templates/login.html")


@app.get("/groups")
async def groups_page():
    """Serve the groups page."""
    return FileResponse("templates/groups.html")


@app.get("/students")
async def students_page():
    """Serve the students page."""
    return FileResponse("templates/students.html")


@app.get("/attendance")
async def attendance_page():
    """Serve the attendance page."""
    return FileResponse("templates/attendance.html")


@app.get("/payments")
async def payments_page():
    """Serve the new payments page."""
    return FileResponse("templates/payments_new.html")

@app.get("/payments-old")
async def payments_old_page():
    """Serve the old payments page (backup)."""
    return FileResponse("templates/payments.html")


@app.get("/statistics")
async def statistics_page():
    """Serve the statistics page."""
    return FileResponse("templates/statistics.html")


@app.get("/test-unpaid")
async def test_unpaid_page():
    """Serve test page for unpaid students API."""
    return FileResponse("test_unpaid_api.html")


@app.get("/tournaments")
async def tournaments_page():
    """Serve the tournaments page."""
    return FileResponse("templates/tournaments.html")


@app.get("/settings")
async def settings_page():
    """Serve the settings page."""
    return FileResponse("templates/settings.html")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
