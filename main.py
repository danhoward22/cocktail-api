import os
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.cors import CORSMiddleware

from supertokens_python import get_all_cors_headers
from supertokens_python.framework.fastapi import get_middleware

from bootstrap.supertokens import init_supertokens
from bootstrap.lifespan import lifespan
from routers.cocktails import router as cocktail_router
from routers.errors import APIError, error_body

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

@app.exception_handler(APIError)
async def api_error_handler(request: Request, exc: APIError):
    return JSONResponse(
        status_code=exc.status_code,
        content=error_body(exc.status_code, exc.message, exc.fields),
    )

@app.exception_handler(RequestValidationError)
async def validation_handler(request: Request, exc: RequestValidationError):
    fields = {}
    for err in exc.errors():
        # loc looks like ("body", "ingredients", 0, "qty"); drop "body"
        path = ".".join(str(p) for p in err["loc"] if p != "body")
        fields.setdefault(path, err["msg"])
    return JSONResponse(
        status_code=422,
        content=error_body(422, "Request validation failed.", fields),
    )

@app.exception_handler(StarletteHTTPException)
async def http_handler(request: Request, exc: StarletteHTTPException):
    # Covers 404s, 405s, and any HTTPException raised by libraries
    return JSONResponse(
        status_code=exc.status_code,
        content=error_body(exc.status_code, str(exc.detail)),
    )

app.include_router(cocktail_router)

# TODO: start server
