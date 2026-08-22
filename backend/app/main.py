"""
FastAPI application entrypoint.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.database import Base, engine
from app.api.routes import auth, documents, search, tasks, analytics, activity_logs

# Create tables if they don't exist yet (idempotent).
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI-Powered Task & Knowledge Management System",
    description="Admin uploads documents & assigns tasks. Users semantically search documents and complete tasks.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(documents.router)
app.include_router(search.router)
app.include_router(tasks.router)
app.include_router(analytics.router)
app.include_router(activity_logs.router)


@app.get("/", tags=["health"])
def health_check():
    return {"status": "ok", "service": "ai-task-kb-backend"}
