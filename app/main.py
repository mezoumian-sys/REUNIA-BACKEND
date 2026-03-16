from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from contextlib import asynccontextmanager

from app.core.config import get_settings
from app.routers import produits, commandes, auth


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Réunia API démarrée")
    yield
    print("🛑 Réunia API arrêtée")


def create_app() -> FastAPI:
    s = get_settings()

    app = FastAPI(
        title=s.app_name,
        version=s.app_version,
        description="""
## API Réunia Boutique

Backend complet pour la gestion de la boutique de mode africaine.

### Fonctionnalités
- **Produits & Catégories** — CRUD complet avec upload d'images
- **Commandes** — Passage, suivi client, gestion admin
- **Auth** — JWT pour admin & vendeur

### Auth
Utiliser le endpoint `/auth/login` pour obtenir un token Bearer.
        """,
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # ── CORS ──────────────────────────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=s.origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(GZipMiddleware, minimum_size=1000)

    # ── ROUTERS ───────────────────────────────────────────────
    app.include_router(auth.router, prefix="/api/v1")
    app.include_router(produits.router, prefix="/api/v1")
    app.include_router(commandes.router, prefix="/api/v1")

    # ── HEALTH CHECK ──────────────────────────────────────────
    @app.get("/", tags=["Health"])
    async def root():
        return {
            "app": s.app_name,
            "version": s.app_version,
            "status": "running",
            "docs": "/docs",
        }

    @app.get("/health", tags=["Health"])
    async def health():
        return {"status": "ok"}

    return app


app = create_app()
