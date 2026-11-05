# SHY BOUTIQUE API

Backend e-commerce FastAPI + SQLAlchemy + PostgreSQL.

## Configuration locale

1. Créer une base PostgreSQL nommée shy_db et un utilisateur disposant des droits sur cette base.
2. Copier .env.example vers .env.
3. Renseigner DB_HOST, DB_PORT, DB_NAME=shy_db, DB_USER, DB_PASSWORD et une valeur aléatoire forte pour ADMIN_API_KEY.
4. Ne jamais committer .env ni transmettre la clé d'administration.

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
# Modifier .env avec les paramètres PostgreSQL locaux
alembic upgrade head
uvicorn app.main:app --reload
```

Linux/macOS : remplacer l'activation par source .venv/bin/activate.

## Endpoints

- GET /health : santé de l'API.
- GET /api/v1/catalog/categories : catégories actives.
- POST /api/v1/catalog/categories : créer une catégorie (header X-Admin-API-Key).
- GET /api/v1/catalog/products : catalogue avec filtres category, q, featured, limit, offset.
- GET /api/v1/catalog/products/{slug} : fiche produit publique.
- POST /api/v1/catalog/products : créer un produit et ses variantes (clé admin).
- PATCH /api/v1/catalog/products/{id} : modifier un produit (clé admin).
- POST /api/v1/catalog/products/{id}/variants : ajouter une variante (clé admin).

Documentation OpenAPI : http://localhost:8000/docs

## Modèle initial

- categories
- products
- product_variants (SKU, taille, couleur, stock)

Les routes de catalogue sont prêtes pour une première intégration. Les commandes, comptes clients, paiements Mobile Money, livraison, téléversement d'images et véritable interface d'administration restent à construire. Aucun paiement réel n'est activé.
