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

# Initialize Jinja2 templates
templates = Jinja2Templates(directory="templates")

# Serve templates
@app.get("/")
async def root(request: Request):
    """Serve the main page."""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/login")
async def login_page(request: Request):
    """Serve the login page."""
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/groups")
async def groups_page(request: Request):
    """Serve the groups page."""
    return templates.TemplateResponse("groups.html", {"request": request})


@app.get("/students")
async def students_page(request: Request):
    """Serve the students page."""
    return templates.TemplateResponse("students.html", {"request": request})


@app.get("/attendance")
async def attendance_page(request: Request):
    """Serve the attendance page."""
    return templates.TemplateResponse("attendance.html", {"request": request})


@app.get("/payments")
async def payments_page(request: Request):
    """Serve the new payments page."""
    return templates.TemplateResponse("payments_new.html", {"request": request})

@app.get("/payments-old")
async def payments_old_page(request: Request):
    """Serve the old payments page (backup)."""
    return templates.TemplateResponse("payments.html", {"request": request})


@app.get("/statistics")
async def statistics_page(request: Request):
    """Serve the statistics page."""
    return templates.TemplateResponse("statistics.html", {"request": request})


@app.get("/test-unpaid")
async def test_unpaid_page():
    """Serve test page for unpaid students API."""
    return FileResponse("test_unpaid_api.html")


@app.get("/tournaments")
async def tournaments_page(request: Request):
    """Serve the tournaments page."""
    return templates.TemplateResponse("tournaments.html", {"request": request})


@app.get("/settings")
async def settings_page(request: Request):
    """Serve the settings page."""
    return templates.TemplateResponse("settings.html", {"request": request})


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
