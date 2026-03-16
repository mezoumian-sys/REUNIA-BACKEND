from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime
from enum import Enum


# ─── STATUT COMMANDE ──────────────────────────────────────────
class StatutCommande(str, Enum):
    en_attente = "en_attente"
    confirmee = "confirmee"
    en_preparation = "en_preparation"
    expediee = "expediee"
    livree = "livree"
    annulee = "annulee"


class ModePaiement(str, Enum):
    orange_money = "orange_money"
    wave = "wave"
    moov = "moov"
    carte = "carte"
    especes = "especes"


# ─── LIGNE DE PANIER ──────────────────────────────────────────
class LigneBase(BaseModel):
    produit_id: str
    quantite: int = Field(..., ge=1, le=100)
    taille: Optional[str] = None
    couleur: Optional[str] = None


class LigneOut(LigneBase):
    id: str
    prix_unitaire: float
    sous_total: float
    produit_nom: str
    produit_image: Optional[str] = None


# ─── CLIENT INFO ──────────────────────────────────────────────
class ClientInfo(BaseModel):
    nom: str = Field(..., min_length=2, max_length=100)
    prenom: str = Field(..., min_length=2, max_length=100)
    telephone: str = Field(..., min_length=8, max_length=20)
    email: Optional[str] = None
    adresse: str = Field(..., min_length=5)
    ville: str = Field(..., min_length=2)
    commune: Optional[str] = None
    instructions: Optional[str] = None


# ─── COMMANDE ─────────────────────────────────────────────────
class CommandeCreate(BaseModel):
    client: ClientInfo
    lignes: List[LigneBase] = Field(..., min_length=1)
    mode_paiement: ModePaiement
    notes: Optional[str] = None


class CommandeUpdate(BaseModel):
    statut: Optional[StatutCommande] = None
    notes_admin: Optional[str] = None
    numero_suivi: Optional[str] = None


class CommandeOut(BaseModel):
    id: str
    numero: str                    # ex: RN-2025-0042
    client: ClientInfo
    lignes: List[LigneOut]
    sous_total: float
    frais_livraison: float
    total: float
    statut: StatutCommande
    mode_paiement: ModePaiement
    notes: Optional[str] = None
    notes_admin: Optional[str] = None
    numero_suivi: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PaginatedCommandes(BaseModel):
    items: List[CommandeOut]
    total: int
    page: int
    per_page: int
    pages: int
