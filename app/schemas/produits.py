from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class TissuEnum(str, Enum):
    wax = "wax"
    bazin = "bazin"
    kente = "kente"
    bogolan = "bogolan"
    dentelle = "dentelle"
    autre = "autre"

class CategorieBase(BaseModel):
    nom: str
    slug: str
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
    class Config:
        from_attributes = True

class ProduitBase(BaseModel):
    nom: str
    slug: str
    description: Optional[str] = None
    prix: float
    prix_promo: Optional[float] = None
    tissu: TissuEnum = TissuEnum.wax
    categorie_id: str
    stock: int = 0
    images: List[str] = []
    badge: Optional[str] = None
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
    class Config:
        from_attributes = True

class PaginatedProduits(BaseModel):
    items: List[ProduitOut]
    total: int
    page: int
    per_page: int
    pages: int
