from contextlib import asynccontextmanager
from fastapi import FastAPI
from database import init_dev_db, close_dev_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up...")
    init_dev_db()

    yield  # app runs and serves requests while paused here

    close_dev_db()
    print("Shutting down...")
    