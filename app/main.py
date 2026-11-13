"""FastAPI server secured with Supabase Auth.

Run with:  python -m app.main
"""

import os
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse, JSONResponse

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
    lifespan=lifespan,
    # Interactive docs are switched on in a later stage.
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)

app.include_router(auth.router)
app.include_router(public.router)
app.include_router(protected.router)


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
    </main>
  </body>
</html>
"""


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def home() -> str:
    return LANDING_PAGE


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="127.0.0.1", port=PORT)
