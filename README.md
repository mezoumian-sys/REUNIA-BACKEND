# Réunia Boutique — Backend API

FastAPI + Supabase · Déployé sur Render

---

## Stack
| Couche | Tech |
|--------|------|
| API | FastAPI 0.111 |
| Base de données | Supabase (PostgreSQL) |
| Stockage images | Supabase Storage |
| Auth | JWT (python-jose) |
| Déploiement | Render.com |

---

## Structure

```
reunia-backend/
├── app/
│   ├── main.py              # Point d'entrée FastAPI
│   ├── core/
│   │   ├── config.py        # Settings (pydantic-settings)
│   │   ├── supabase.py      # Client Supabase
│   │   └── security.py      # JWT + dépendances auth
│   ├── routers/
│   │   ├── produits.py      # GET/POST/PATCH/DELETE produits & catégories
│   │   ├── commandes.py     # Passer commande, suivi, admin
│   │   └── auth.py          # Login, create admin
│   ├── schemas/
│   │   ├── produits.py      # Pydantic models produits/catégories
│   │   ├── commandes.py     # Pydantic models commandes
│   │   └── auth.py          # Pydantic models auth
│   └── services/
│       ├── produits_service.py   # Logique métier produits
│       └── commandes_service.py  # Logique métier commandes
├── supabase_schema.sql      # Schema BDD complet à coller dans Supabase
├── render.yaml              # Config déploiement Render
├── requirements.txt
└── .env.example
```

---

## Déploiement — Guide étape par étape

### 1. Supabase

1. Créer un projet sur [supabase.com](https://supabase.com)
2. Aller dans **SQL Editor** → **New Query**
3. Coller le contenu de `supabase_schema.sql` → **Run**
4. Aller dans **Storage** → **New Bucket** → Nom: `produits` → Public: ✅
5. Copier les clés :
   - `Project URL` → `SUPABASE_URL`
   - `anon public` → `SUPABASE_KEY`
   - `service_role secret` → `SUPABASE_SERVICE_KEY`

### 2. Render

1. Push le code sur GitHub
2. Aller sur [render.com](https://render.com) → **New Web Service**
3. Connecter le repo GitHub
4. Render détecte automatiquement `render.yaml`
5. Ajouter les variables d'environnement :
   ```
   SUPABASE_URL=https://xxx.supabase.co
   SUPABASE_KEY=eyJ...
   SUPABASE_SERVICE_KEY=eyJ...
   SECRET_KEY=une_clé_très_longue_et_aléatoire
   ALLOWED_ORIGINS=https://ton-site.vercel.app
   ```
6. **Deploy** → URL: `https://reunia-api.onrender.com`

### 3. Vercel (frontend)

Ajouter dans les variables d'environnement Vercel :
```
NEXT_PUBLIC_API_URL=https://reunia-api.onrender.com/api/v1
```

---

## API — Endpoints principaux

### Public (pas de token requis)
```
GET    /api/v1/categories              — Liste catégories
GET    /api/v1/produits                — Liste produits (paginée)
GET    /api/v1/produits/{id}           — Détail produit
GET    /api/v1/produits/slug/{slug}    — Produit par slug
POST   /api/v1/commandes               — Passer une commande
GET    /api/v1/commandes/suivi/{num}   — Suivre commande (ex: RN-2025-0042)
```

### Admin (Bearer token requis)
```
POST   /api/v1/auth/login              — Login → token JWT
GET    /api/v1/auth/me                 — Mon compte

POST   /api/v1/produits                — Créer produit
PATCH  /api/v1/produits/{id}           — Modifier produit
DELETE /api/v1/produits/{id}           — Archiver produit
POST   /api/v1/produits/upload-image   — Upload image → Supabase Storage

POST   /api/v1/categories              — Créer catégorie
PATCH  /api/v1/categories/{id}         — Modifier catégorie

GET    /api/v1/commandes               — Liste commandes (admin)
GET    /api/v1/commandes/stats         — Stats dashboard
PATCH  /api/v1/commandes/{id}          — Changer statut / ajouter suivi
```

### Docs interactives
```
https://reunia-api.onrender.com/docs      ← Swagger UI
https://reunia-api.onrender.com/redoc     ← ReDoc
```

---

## Développement local

```bash
# Cloner et installer
git clone ...
cd reunia-backend
pip install -r requirements.txt

# Configurer
cp .env.example .env
# Remplir les valeurs dans .env

# Lancer
uvicorn app.main:app --reload --port 8000

# API disponible sur http://localhost:8000
# Docs sur http://localhost:8000/docs
```

---

## Compte admin par défaut

| Username | Password |
|----------|----------|
| `admin`  | `reunia2025` |

**Changer le mot de passe après le premier déploiement !**

---

## Prochaines étapes

- [ ] Intégration Orange Money (CinetPay API)
- [ ] Intégration Wave CI
- [ ] Notifications WhatsApp (Twilio / Wati)
- [ ] Emails de confirmation (Resend)
- [ ] Analytics commandes avancées
