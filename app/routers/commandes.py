from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional
from app.schemas.commandes import (
    CommandeCreate, CommandeUpdate, CommandeOut,
    PaginatedCommandes, StatutCommande,
)
from app.services.commandes_service import (
    create_commande, list_commandes, get_commande,
    get_commande_by_numero, update_commande_statut, get_stats,
)
from app.core.security import require_admin

router = APIRouter(tags=["Commandes"])

@router.post("/commandes", response_model=CommandeOut)
async def passer_commande(data: CommandeCreate):
    try:
        return await create_commande(data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))

@router.get("/commandes/suivi/{numero}", response_model=CommandeOut)
async def suivre_commande(numero: str):
    c = await get_commande_by_numero(numero.upper())
    if not c:
        raise HTTPException(404, "Commande introuvable")
    return c

@router.get("/commandes/stats")
async def dashboard_stats(_=Depends(require_admin)):
    return await get_stats()

@router.get("/commandes", response_model=PaginatedCommandes)
async def list_cmd(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    statut: Optional[StatutCommande] = None,
    search: Optional[str] = None,
    _=Depends(require_admin),
):
    return await list_commandes(page, per_page, statut, search)

@router.get("/commandes/{commande_id}", response_model=CommandeOut)
async def get_cmd(commande_id: str, _=Depends(require_admin)):
    c = await get_commande(commande_id)
    if not c:
        raise HTTPException(404, "Commande introuvable")
    return c

@router.patch("/commandes/{commande_id}", response_model=CommandeOut)
async def update_cmd(commande_id: str, data: CommandeUpdate, _=Depends(require_admin)):
    return await update_commande_statut(commande_id, data)
