from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional
from app.schemas.produits import (
    ProduitCreate, ProduitUpdate, ProduitOut, PaginatedProduits,
    CategorieCreate, CategorieUpdate, CategorieOut,
)
from app.services.produits_service import (
    list_categories, get_categorie, create_categorie, update_categorie, delete_categorie,
    list_produits, get_produit, get_produit_by_slug, create_produit, update_produit, delete_produit,
)
from app.core.security import require_admin

router = APIRouter(tags=["Produits"])

@router.get("/categories", response_model=list[CategorieOut])
async def get_categories(active_only: bool = True):
    return await list_categories(active_only)

@router.get("/categories/{categorie_id}", response_model=CategorieOut)
async def get_cat(categorie_id: str):
    cat = await get_categorie(categorie_id)
    if not cat:
        raise HTTPException(404, "Catégorie introuvable")
    return cat

@router.post("/categories", response_model=CategorieOut)
async def create_cat(data: CategorieCreate, _=Depends(require_admin)):
    return await create_categorie(data)

@router.patch("/categories/{categorie_id}", response_model=CategorieOut)
async def update_cat(categorie_id: str, data: CategorieUpdate, _=Depends(require_admin)):
    return await update_categorie(categorie_id, data)

@router.delete("/categories/{categorie_id}")
async def delete_cat(categorie_id: str, _=Depends(require_admin)):
    await delete_categorie(categorie_id)
    return {"message": "Catégorie supprimée"}

@router.get("/produits", response_model=PaginatedProduits)
async def get_produits(
    page: int = Query(1, ge=1),
    per_page: int = Query(12, ge=1, le=50),
    categorie_id: Optional[str] = None,
    tissu: Optional[str] = None,
    search: Optional[str] = None,
    actif_only: bool = True,
):
    return await list_produits(page, per_page, categorie_id, tissu, search, actif_only)

@router.get("/produits/slug/{slug}", response_model=ProduitOut)
async def get_by_slug(slug: str):
    p = await get_produit_by_slug(slug)
    if not p:
        raise HTTPException(404, "Produit introuvable")
    return p

@router.get("/produits/{produit_id}", response_model=ProduitOut)
async def get_prod(produit_id: str):
    p = await get_produit(produit_id)
    if not p:
        raise HTTPException(404, "Produit introuvable")
    return p

@router.post("/produits", response_model=ProduitOut)
async def create_prod(data: ProduitCreate, _=Depends(require_admin)):
    return await create_produit(data)

@router.patch("/produits/{produit_id}", response_model=ProduitOut)
async def update_prod(produit_id: str, data: ProduitUpdate, _=Depends(require_admin)):
    return await update_produit(produit_id, data)

@router.delete("/produits/{produit_id}")
async def delete_prod(produit_id: str, _=Depends(require_admin)):
    await delete_produit(produit_id)
    return {"message": "Produit archivé"}
