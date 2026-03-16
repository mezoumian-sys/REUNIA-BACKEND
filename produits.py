from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List
from datetime import datetime
from enum import Enum


# ─── CATÉGORIE ────────────────────────────────────────────────
class CategorieBase(BaseModel):
    nom: str = Field(..., min_length=2, max_length=100)
    slug: str = Field(..., min_length=2, max_length=100)
    description: Optional[str] = None
    image_url: Optional[str] = None
    ordre: int = 0
    active: bool = True


class CategorieCreate(CategorieBase):
    pass


class CategorieUpdate(BaseModel):
    nom: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    ordre: Optional[int] = None
    active: Optional[bool] = None


class CategorieOut(CategorieBase):
    id: str
    created_at: datetime
    nb_produits: Optional[int] = 0

    class Config:
        from_attributes = True


# ─── PRODUIT ──────────────────────────────────────────────────
class TissuEnum(str, Enum):
    wax = "wax"
    bazin = "bazin"
    kente = "kente"
    bogolan = "bogolan"
    dentelle = "dentelle"
    autre = "autre"


class ProduitBase(BaseModel):
    nom: str = Field(..., min_length=2, max_length=200)
    slug: str = Field(..., min_length=2, max_length=200)
    description: Optional[str] = None
    prix: float = Field(..., gt=0)
    prix_promo: Optional[float] = Field(None, gt=0)
    tissu: TissuEnum = TissuEnum.wax
    categorie_id: str
    stock: int = Field(default=0, ge=0)
    images: List[str] = []       # liste d'URLs Supabase Storage
    badge: Optional[str] = None  # "Nouveau", "Bestseller", "Édition limitée"
    actif: bool = True
    sur_mesure: bool = False


class ProduitCreate(ProduitBase):
    pass


class ProduitUpdate(BaseModel):
    nom: Optional[str] = None
    description: Optional[str] = None
    prix: Optional[float] = None
    prix_promo: Optional[float] = None
    tissu: Optional[TissuEnum] = None
    categorie_id: Optional[str] = None
    stock: Optional[int] = None
    images: Optional[List[str]] = None
    badge: Optional[str] = None
    actif: Optional[bool] = None
    sur_mesure: Optional[bool] = None


class ProduitOut(ProduitBase):
    id: str
    created_at: datetime
    updated_at: datetime
    categorie: Optional[CategorieOut] = None

    class Config:
        from_attributes = True


# ─── PAGINATION ───────────────────────────────────────────────
class PaginatedProduits(BaseModel):
    items: List[ProduitOut]
    total: int
    page: int
    per_page: int
    pages: int
