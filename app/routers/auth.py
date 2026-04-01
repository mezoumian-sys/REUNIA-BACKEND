import uuid
from fastapi import APIRouter, HTTPException, Depends
from app.schemas.auth import AdminLogin, TokenOut, AdminCreate, AdminOut
from app.core.security import (
    hash_password, verify_password,
    create_access_token, require_admin,
)
from app.core.supabase import get_supabase, get_supabase_admin

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login", response_model=TokenOut)
async def login(data: AdminLogin):
    db = get_supabase()
    res = db.table("admins").select("*").eq("username", data.username).eq("actif", True).execute()
    if not res.data:
        raise HTTPException(401, "Identifiants incorrects")
    admin = res.data[0]
    if not verify_password(data.password, admin["password_hash"]):
        raise HTTPException(401, "Identifiants incorrects")
    token = create_access_token({
        "sub": admin["id"],
        "username": admin["username"],
        "role": admin["role"],
    })
    return TokenOut(access_token=token, role=admin["role"], username=admin["username"])


@router.post("/admins", response_model=AdminOut)
async def create_admin(data: AdminCreate, current=Depends(require_admin)):
    if current.get("role") != "admin":
        raise HTTPException(403, "Seul un admin peut créer des comptes")
    db = get_supabase_admin()
    exists = db.table("admins").select("id").eq("username", data.username).execute()
    if exists.data:
        raise HTTPException(400, "Ce nom d'utilisateur est déjà pris")
    payload = {
        "id": str(uuid.uuid4()),
        "username": data.username,
        "password_hash": hash_password(data.password),
        "role": data.role,
        "actif": True,
    }
    res = db.table("admins").insert(payload).execute()
    return res.data[0]


@router.get("/me", response_model=AdminOut)
async def get_me(current=Depends(require_admin)):
    db = get_supabase()
    res = db.table("admins").select("id,username,role,actif").eq("id", current["sub"]).single().execute()
    return res.data
