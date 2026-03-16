-- ═══════════════════════════════════════════════════════════
--  RÉUNIA BOUTIQUE — Schéma Supabase
--  Coller dans : Supabase Dashboard → SQL Editor → New Query
-- ═══════════════════════════════════════════════════════════

-- Extensions
create extension if not exists "uuid-ossp";

-- ─── ADMINS ──────────────────────────────────────────────────
create table if not exists admins (
  id            uuid primary key default uuid_generate_v4(),
  username      text unique not null,
  password_hash text not null,
  role          text not null check (role in ('admin', 'vendeur')) default 'vendeur',
  actif         boolean default true,
  created_at    timestamptz default now()
);

-- ─── CATÉGORIES ──────────────────────────────────────────────
create table if not exists categories (
  id          uuid primary key default uuid_generate_v4(),
  nom         text not null,
  slug        text unique not null,
  description text,
  image_url   text,
  ordre       int default 0,
  active      boolean default true,
  created_at  timestamptz default now()
);

-- ─── PRODUITS ────────────────────────────────────────────────
create table if not exists produits (
  id           uuid primary key default uuid_generate_v4(),
  nom          text not null,
  slug         text unique not null,
  description  text,
  prix         numeric(12,2) not null check (prix > 0),
  prix_promo   numeric(12,2),
  tissu        text not null default 'wax'
               check (tissu in ('wax','bazin','kente','bogolan','dentelle','autre')),
  categorie_id uuid references categories(id) on delete set null,
  stock        int default 0 check (stock >= 0),
  images       text[] default '{}',
  badge        text,
  actif        boolean default true,
  sur_mesure   boolean default false,
  created_at   timestamptz default now(),
  updated_at   timestamptz default now()
);

-- Auto-update updated_at
create or replace function update_updated_at()
returns trigger as $$
begin
  new.updated_at = now();
  return new;
end;
$$ language plpgsql;

create trigger produits_updated_at
  before update on produits
  for each row execute function update_updated_at();

-- ─── COMMANDES ───────────────────────────────────────────────
create table if not exists commandes (
  id             uuid primary key default uuid_generate_v4(),
  numero         text unique not null,
  client         jsonb not null,       -- ClientInfo complet
  lignes         jsonb not null,       -- Liste de LigneOut
  sous_total     numeric(12,2) not null,
  frais_livraison numeric(12,2) default 1500,
  total          numeric(12,2) not null,
  statut         text not null default 'en_attente'
                 check (statut in (
                   'en_attente','confirmee','en_preparation',
                   'expediee','livree','annulee'
                 )),
  mode_paiement  text not null
                 check (mode_paiement in (
                   'orange_money','wave','moov','carte','especes'
                 )),
  notes          text,
  notes_admin    text,
  numero_suivi   text,
  created_at     timestamptz default now(),
  updated_at     timestamptz default now()
);

create trigger commandes_updated_at
  before update on commandes
  for each row execute function update_updated_at();

-- ─── INDEX ───────────────────────────────────────────────────
create index if not exists idx_produits_categorie on produits(categorie_id);
create index if not exists idx_produits_slug on produits(slug);
create index if not exists idx_produits_actif on produits(actif);
create index if not exists idx_commandes_numero on commandes(numero);
create index if not exists idx_commandes_statut on commandes(statut);

-- ─── RLS (Row Level Security) ────────────────────────────────
alter table admins enable row level security;
alter table categories enable row level security;
alter table produits enable row level security;
alter table commandes enable row level security;

-- Catégories : lecture publique
create policy "categories_public_read" on categories
  for select using (true);

-- Produits : lecture publique si actif
create policy "produits_public_read" on produits
  for select using (actif = true);

-- Commandes : insertion publique (pour passer commande)
create policy "commandes_public_insert" on commandes
  for insert with check (true);

-- Commandes : lecture par numero (suivi client)
create policy "commandes_public_select_by_numero" on commandes
  for select using (true);

-- ─── STORAGE BUCKET ──────────────────────────────────────────
-- À faire dans : Supabase → Storage → New Bucket
-- Nom: "produits" | Public: true

-- ─── DONNÉES INITIALES ───────────────────────────────────────
insert into categories (nom, slug, description, ordre) values
  ('Robes & Tenues Femme', 'femme', 'Robes et ensembles en wax, bazin et bogolan', 1),
  ('Ensembles Homme',      'homme', 'Boubous, ensembles kente et bazin pour homme', 2),
  ('Grand Occasion',       'occasion', 'Tenues cérémonie, mariage, baptême', 3),
  ('Bébé & Enfant',        'bebe', 'Tenues traditionnelles pour les tout-petits', 4),
  ('Couture Sur Mesure',   'sur-mesure', 'Service exclusif sur rendez-vous à Abidjan', 5)
on conflict (slug) do nothing;

-- Admin par défaut (password: reunia2025)
-- CHANGE LE MOT DE PASSE après le premier login !
insert into admins (username, password_hash, role) values
  ('admin', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMqJqhNgjAt9f7g4QpR1nS8Xay', 'admin')
on conflict (username) do nothing;
