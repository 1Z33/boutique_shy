# SHY BOUTIQUE

Luxury women's fashion e-commerce for the Democratic Republic of the Congo, featuring an immersive 3D boutique experience.

## Product direction

- Editorial, feminine and minimal luxury identity.
- Warm palette: cream, travertine, dark walnut, brushed brass and muted rose.
- Immersive 3D showroom with a conventional accessible shopping flow.
- Clothing, shoes, bags and accessories for women.
- RDC market, USD/CDF-ready pricing, Mobile Money and cash on delivery.
- Home delivery.

## Repository layout

- frontend/: Next.js, TypeScript and React Three Fiber.
- backend/: FastAPI, SQLAlchemy, Alembic and PostgreSQL.
- docs/: product requirements and technical architecture.

## Local development

1. Configure PostgreSQL and create a database named shy_db.
2. Copy backend/.env.example to backend/.env and fill in the local database credentials and a private ADMIN_API_KEY.
3. In backend/, install requirements, run alembic upgrade head, then uvicorn app.main:app --reload.
4. Copy frontend/.env.example to frontend/.env.local, then run npm install and npm run dev in frontend/.

See backend/README.md and frontend/README.md for full instructions.

The catalogue route at /catalogue reads products from the FastAPI API. The initial home-page cards and 3D product popovers remain prototype content. Payment, orders, delivery and full admin workflows are not active yet.

> Product imagery currently included in the prototype is editorial demo imagery. It must be replaced or confirmed against the actual inventory before commercial launch.
