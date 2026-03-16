import math
import uuid
from typing import Optional
from app.core.supabase import get_supabase, get_supabase_admin
from app.schemas.produits import ProduitCreate, ProduitUpdate, CategorieCreate, CategorieUpdate


# ══════════════════════════════════════════
#  CATÉGORIES
# ══════════════════════════════════════════

async def list_categories(active_only: bool = True) -> list:
    db = get_supabase()
    q = db.table("categories").select("*, produits(count)")
    if active_only:
        q = q.eq("active", True)
    res = q.order("ordre").execute()
    return res.data or []


async def get_categorie(categorie_id: str) -> dict | None:
    db = get_supabase()
    res = db.table("categories").select("*").eq("id", categorie_id).single().execute()
    return res.data


async def create_categorie(data: CategorieCreate) -> dict:
    db = get_supabase_admin()
    payload = data.model_dump()
    payload["id"] = str(uuid.uuid4())
    res = db.table("categories").insert(payload).execute()
    return res.data[0]


async def update_categorie(categorie_id: str, data: CategorieUpdate) -> dict:
    db = get_supabase_admin()
    payload = data.model_dump(exclude_none=True)
    res = db.table("categories").update(payload).eq("id", categorie_id).execute()
    return res.data[0]


async def delete_categorie(categorie_id: str) -> bool:
    db = get_supabase_admin()
    db.table("categories").delete().eq("id", categorie_id).execute()
    return True


# ══════════════════════════════════════════
#  PRODUITS
# ══════════════════════════════════════════

async def list_produits(
    page: int = 1,
    per_page: int = 12,
    categorie_id: Optional[str] = None,
    tissu: Optional[str] = None,
    search: Optional[str] = None,
    actif_only: bool = True,
) -> dict:
    db = get_supabase()
    offset = (page - 1) * per_page

    q = db.table("produits").select("*, categories(*)", count="exact")

    if actif_only:
        q = q.eq("actif", True)
    if categorie_id:
        q = q.eq("categorie_id", categorie_id)
    if tissu:
        q = q.eq("tissu", tissu)
    if search:
        q = q.ilike("nom", f"%{search}%")

    res = q.order("created_at", desc=True).range(offset, offset + per_page - 1).execute()

    total = res.count or 0
    return {
        "items": res.data or [],
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": math.ceil(total / per_page) if total else 0,
    }


async def get_produit(produit_id: str) -> dict | None:
    db = get_supabase()
    res = (
        db.table("produits")
        .select("*, categories(*)")
        .eq("id", produit_id)
        .single()
        .execute()
    )
    return res.data


async def get_produit_by_slug(slug: str) -> dict | None:
    db = get_supabase()
    res = (
        db.table("produits")
        .select("*, categories(*)")
        .eq("slug", slug)
        .single()
        .execute()
    )
    return res.data


async def create_produit(data: ProduitCreate) -> dict:
    db = get_supabase_admin()
    payload = data.model_dump()
    payload["id"] = str(uuid.uuid4())
    res = db.table("produits").insert(payload).execute()
    return res.data[0]


async def update_produit(produit_id: str, data: ProduitUpdate) -> dict:
    db = get_supabase_admin()
    payload = data.model_dump(exclude_none=True)
    res = db.table("produits").update(payload).eq("id", produit_id).execute()
    return res.data[0]


async def delete_produit(produit_id: str) -> bool:
    db = get_supabase_admin()
    # Soft delete
    db.table("produits").update({"actif": False}).eq("id", produit_id).execute()
    return True


# ══════════════════════════════════════════
#  UPLOAD IMAGE → Supabase Storage
# ══════════════════════════════════════════

async def upload_image(file_bytes: bytes, filename: str, bucket: str = "produits") -> str:
    """Upload une image et retourne son URL publique"""
    db = get_supabase_admin()
    ext = filename.rsplit(".", 1)[-1].lower()
    unique_name = f"{uuid.uuid4()}.{ext}"
    path = f"images/{unique_name}"

    db.storage.from_(bucket).upload(
        path=path,
        file=file_bytes,
        file_options={"content-type": f"image/{ext}"},
    )

    url = db.storage.from_(bucket).get_public_url(path)
    return url
