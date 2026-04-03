from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from app.config.settings import settings
import uvicorn
from app.config.database_config import init_db
from app.routers.routes import *

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    # allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)


@app.get("/")
def index():
    return RedirectResponse("/docs")


for route in V1_ROUTES:
    app.include_router(route, prefix=settings.API_V1_STR)

for route in V2_ROUTES:
    app.include_router(route, prefix=settings.API_V2_STR)


@app.on_event("startup")
def on_startup():
    init_db()


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8090, reload=True)