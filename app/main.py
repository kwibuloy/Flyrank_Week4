"""FastAPI server secured with Supabase Auth.

Run with:  python -m app.main
"""

import os
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.openapi.utils import get_openapi
from fastapi.responses import HTMLResponse, JSONResponse

from app.dependencies import Unauthorized
from app.routers import auth, protected, public
from app.supabase_client import check_supabase_connection

PORT = int(os.getenv("PORT") or 3000)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Fail fast: a wrong URL or key stops the server before it takes any requests.
    check_supabase_connection()
    print(f"Server running and connected to Supabase on http://localhost:{PORT}")
    yield


app = FastAPI(
    title="Supabase Auth API",
    version="1.0.0",
    description=(
        "FastAPI API secured with Supabase Auth. Log in with POST /auth/login, copy the "
        "access_token, then click Authorize and paste it to call the protected routes."
    ),
    openapi_tags=[
        {"name": "Auth", "description": "Sign up, log in and log out"},
        {"name": "Public", "description": "Open to everyone"},
        {"name": "Protected", "description": "Requires a valid Supabase access token"},
    ],
    lifespan=lifespan,
    docs_url="/docs",  # Swagger UI
    redoc_url=None,
)

app.include_router(auth.router)
app.include_router(public.router)
app.include_router(protected.router)


@app.exception_handler(Unauthorized)
async def unauthorized(request: Request, exc: Unauthorized) -> JSONResponse:
    return JSONResponse(status_code=401, content={"error": exc.message})


@app.exception_handler(RequestValidationError)
async def bad_request_body(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Malformed JSON bodies get a JSON 400 instead of FastAPI's default 422."""
    if any(e.get("type") == "json_invalid" for e in exc.errors()):
        return JSONResponse(status_code=400, content={"error": "Request body must be valid JSON"})
    return JSONResponse(status_code=400, content={"error": "Invalid request body"})


LANDING_PAGE = """<!doctype html>
<html lang="en">
  <head><meta charset="utf-8"><title>Supabase Auth API</title></head>
  <body style="font-family: system-ui, sans-serif; margin: 40px">
    <main>
      <h1>Supabase Auth API</h1>
      <p>A FastAPI API secured with Supabase Auth.</p>
      <p>Interactive API docs: <a href="/docs">/docs</a></p>
    </main>
  </body>
</html>
"""


def custom_openapi() -> dict:
    """FastAPI documents a 422 on every route with a body, but bad_request_body()
    answers with 400 instead, so the 422 entries are removed from the docs."""
    if app.openapi_schema:
        return app.openapi_schema
    schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
        tags=app.openapi_tags,
    )
    for operations in schema["paths"].values():
        for operation in operations.values():
            operation["responses"].pop("422", None)
    for name in ("HTTPValidationError", "ValidationError"):
        schema.get("components", {}).get("schemas", {}).pop(name, None)
    app.openapi_schema = schema
    return schema


app.openapi = custom_openapi


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def home() -> str:
    return LANDING_PAGE


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="127.0.0.1", port=PORT)
