from contextlib import asynccontextmanager
from fastapi import FastAPI
from database import init_dev_db, close_dev_db
from supertokens_python.recipe.userroles.asyncio import create_new_role_or_add_permissions, add_role_to_user

async def init_roles():
    await create_new_role_or_add_permissions("admin", ["read", "write:all", "delete:all"])
    await create_new_role_or_add_permissions("user", ["read", "write:self", "delete:self"])
    await add_role_to_user("public", "danhoward22@gmail.com", "admin")

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up...")
    init_dev_db()

    await init_roles()
    yield  # app runs and serves requests while paused here

    close_dev_db()
    print("Shutting down...")
    