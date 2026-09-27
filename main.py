import os
from dotenv import load_dotenv
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from supertokens_python import get_all_cors_headers
from supertokens_python.framework.fastapi import get_middleware

from bootstrap.supertokens import init_supertokens
from bootstrap.lifespan import lifespan
from routers.cocktails import router as cocktail_router

env_type = os.getenv("APP_ENV")
env_file = ".env"
if env_type: env_file += f".{env_type}"

if os.path.exists(env_file):
    load_dotenv(dotenv_path=env_file, override=True)
    print(f"Variables loaded from {env_file}")
else:
    load_dotenv()
    
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
    allow_methods=["GET", "PUT", "POST", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type"] + get_all_cors_headers(),
)

app.include_router(cocktail_router)

# TODO: start server
