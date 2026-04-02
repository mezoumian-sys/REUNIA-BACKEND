import logging
logging.basicConfig(level=logging.DEBUG)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.config import get_settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Réunia API démarrée")
    yield

def create_app() -> FastAPI:
    s = get_settings()
    app = FastAPI(
        title=s.app_name,
        version=s.app_version,
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    from app.routers import auth, produits, commandes
    app.include_router(auth.router, prefix="/api/v1")
    app.include_router(produits.router, prefix="/api/v1")
    app.include_router(commandes.router, prefix="/api/v1")

    @app.get("/")
    async def root():
        return {"app": s.app_name, "status": "running", "docs": "/docs"}

    @app.get("/health")
    async def health():
        return {"status": "ok"}

    return app

app = create_app()
