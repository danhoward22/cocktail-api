import os
from dotenv import load_dotenv
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from supertokens_python import get_all_cors_headers
from supertokens_python.framework.fastapi import get_middleware

from config.supertokens import init_supertokens
from routers.allow_list import router as allow_list_router

load_dotenv()

init_supertokens()

app = FastAPI()
app.add_middleware(get_middleware())

app.include_router(allow_list_router)

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
