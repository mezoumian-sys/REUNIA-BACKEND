import math
import uuid
from datetime import datetime
from typing import Optional
from fastapi import HTTPException
from app.core.supabase import get_supabase, get_supabase_admin
from app.schemas.commandes import CommandeCreate, CommandeUpdate, StatutCommande


FRAIS_LIVRAISON = 1500.0   # FCFA — Abidjan


def _generate_numero() -> str:
    """Génère un numéro de commande unique : RN-2025-XXXX"""
    year = datetime.utcnow().year
    uid = str(uuid.uuid4().int)[:4].zfill(4)
    return f"RN-{year}-{uid}"


async def create_commande(data: CommandeCreate) -> dict:
    db = get_supabase()
    admin = get_supabase_admin()

    # 1. Vérifier stock et récupérer prix pour chaque ligne
    lignes_enrichies = []
    sous_total = 0.0

    for ligne in data.lignes:
        res = db.table("produits").select("id,nom,prix,prix_promo,stock,images,actif").eq("id", ligne.produit_id).single().execute()
        produit = res.data

        if not produit or not produit["actif"]:
            raise HTTPException(404, f"Produit {ligne.produit_id} introuvable")
        if produit["stock"] < ligne.quantite:
            raise HTTPException(400, f"Stock insuffisant pour « {produit['nom']} » (dispo: {produit['stock']})")

        prix = produit["prix_promo"] or produit["prix"]
        st = prix * ligne.quantite
        sous_total += st

        lignes_enrichies.append({
            "id": str(uuid.uuid4()),
            "produit_id": ligne.produit_id,
            "produit_nom": produit["nom"],
            "produit_image": produit["images"][0] if produit["images"] else None,
            "quantite": ligne.quantite,
            "taille": ligne.taille,
            "couleur": ligne.couleur,
            "prix_unitaire": prix,
            "sous_total": st,
        })

    total = sous_total + FRAIS_LIVRAISON

    # 2. Créer la commande
    commande_id = str(uuid.uuid4())
    payload = {
        "id": commande_id,
        "numero": _generate_numero(),
        "client": data.client.model_dump(),
        "lignes": lignes_enrichies,
        "sous_total": sous_total,
        "frais_livraison": FRAIS_LIVRAISON,
        "total": total,
        "statut": StatutCommande.en_attente,
        "mode_paiement": data.mode_paiement,
        "notes": data.notes,
    }
    res = admin.table("commandes").insert(payload).execute()

    # 3. Décrémenter le stock
    for ligne in data.lignes:
        prod = db.table("produits").select("stock").eq("id", ligne.produit_id).single().execute()
        new_stock = prod.data["stock"] - ligne.quantite
        admin.table("produits").update({"stock": new_stock}).eq("id", ligne.produit_id).execute()

    return res.data[0]


async def list_commandes(
    page: int = 1,
    per_page: int = 20,
    statut: Optional[StatutCommande] = None,
    search: Optional[str] = None,
) -> dict:
    db = get_supabase()
    offset = (page - 1) * per_page

    q = db.table("commandes").select("*", count="exact")
    if statut:
        q = q.eq("statut", statut)
    if search:
        q = q.ilike("numero", f"%{search}%")

    res = q.order("created_at", desc=True).range(offset, offset + per_page - 1).execute()
    total = res.count or 0

    return {
        "items": res.data or [],
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": math.ceil(total / per_page) if total else 0,
    }


async def get_commande(commande_id: str) -> dict | None:
    db = get_supabase()
    res = db.table("commandes").select("*").eq("id", commande_id).single().execute()
    return res.data


async def get_commande_by_numero(numero: str) -> dict | None:
    db = get_supabase()
    res = db.table("commandes").select("*").eq("numero", numero).single().execute()
    return res.data


async def update_commande_statut(commande_id: str, data: CommandeUpdate) -> dict:
    admin = get_supabase_admin()
    payload = data.model_dump(exclude_none=True)
    res = admin.table("commandes").update(payload).eq("id", commande_id).execute()
    return res.data[0]


async def get_stats() -> dict:
    """Stats résumées pour le dashboard admin"""
    db = get_supabase()

    commandes = db.table("commandes").select("total,statut,created_at").execute().data or []
    produits = db.table("produits").select("id,actif").execute().data or []
    categories = db.table("categories").select("id").execute().data or []

    total_commandes = len(commandes)
    ca_total = sum(c["total"] for c in commandes if c["statut"] != "annulee")
    en_attente = sum(1 for c in commandes if c["statut"] == "en_attente")
    livrees = sum(1 for c in commandes if c["statut"] == "livree")

    return {
        "total_commandes": total_commandes,
        "ca_total": ca_total,
        "commandes_en_attente": en_attente,
        "commandes_livrees": livrees,
        "total_produits": len([p for p in produits if p["actif"]]),
        "total_categories": len(categories),
    }
