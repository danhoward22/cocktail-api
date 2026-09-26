import os
from dotenv import load_dotenv
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from supertokens_python import get_all_cors_headers
from supertokens_python.framework.fastapi import get_middleware

from bootstrap.supertokens import init_supertokens
from bootstrap.lifespan import lifespan
from routers.cocktails import router as cocktail_router


load_dotenv(dotenv_path=".env.dev",override=True)

init_supertokens()

app = FastAPI(lifespan=lifespan)
app.add_middleware(get_middleware())

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        os.environ.get("WEBSITE_DOMAIN"),
        os.environ.get("API_DOMAIN"),
    ],
    allow_credentials=True,
    allow_methods=["GET", "PUT", "POST", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["Content-Type"] + get_all_cors_headers(),
)

# TODO: start server
app.include_router(cocktail_router)
