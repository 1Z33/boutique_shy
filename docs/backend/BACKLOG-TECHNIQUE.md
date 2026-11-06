# Backlog backend SHY BOUTIQUE

Priorités : P0 indispensable au lancement ; P1 important ; P2 amélioration. Story Points provisoires.

| ID | Module | Travail | Priorité | SP |
|---|---|---|---|---:|
| BE-001 | Fondations | Configuration FastAPI par environnement | P0 | 3 |
| BE-002 | DB | PostgreSQL et sessions SQLAlchemy | P0 | 3 |
| BE-003 | DB | Alembic et migrations additives | P0 | 3 |
| BE-004 | Sécurité | Rôles, permissions, hachage et sessions | P0 | 8 |
| BE-005 | Utilisateurs | Inscription, connexion, refresh, logout | P0 | 5 |
| BE-006 | Utilisateurs | Profil et adresses | P1 | 3 |
| BE-007 | Catalogue | Catégories, produits, publication | P0 | 8 |
| BE-008 | Catalogue | Variantes, SKU et médias | P0 | 8 |
| BE-009 | Catalogue | Recherche, filtres et pagination | P1 | 5 |
| BE-010 | Stock | Inventaire réel par variante | P0 | 3 |
| BE-011 | Stock | Mouvements tracés | P0 | 5 |
| BE-012 | Stock | Réservations transactionnelles anti-surbooking | P0 | 8 |
| BE-013 | Stock | Expiration/libération automatique | P0 | 5 |
| BE-014 | Panier | Panier connecté et invité | P0 | 5 |
| BE-015 | Checkout | Devis CDF, validation serveur, idempotence | P0 | 8 |
| BE-016 | Commandes | Création, snapshot, statuts, historique | P0 | 8 |
| BE-017 | Commandes | Annulation et libération stock | P0 | 5 |
| BE-018 | Livraison | Zones Lubumbashi, tarifs et délais | P0 | 5 |
| BE-019 | Livraison | Livreurs, suivi, preuve et échec | P1 | 8 |
| BE-020 | Paiements | COD et collecte contrôlée | P0 | 3 |
| BE-021 | Paiements | Interface commune Mobile Money | P0 | 5 |
| BE-022 | Paiements | Airtel Money | P0 | 8 |
| BE-023 | Paiements | Orange Money | P0 | 8 |
| BE-024 | Paiements | M-Pesa | P0 | 8 |
| BE-025 | Paiements | Webhooks vérifiés et idempotents | P0 | 8 |
| BE-026 | Promotions | Codes, dates et limites | P1 | 5 |
| BE-027 | Admin | Produits, stock, commandes et clients | P0 | 8 |
| BE-028 | Admin | Dashboard opérationnel | P1 | 5 |
| BE-029 | Notifications | File, modèles, retries et historique | P1 | 8 |
| BE-030 | 3D | API zones et placements GLB | P1 | 8 |
| BE-031 | Analytics | Rapports ventes, paiements et stock | P1 | 8 |
| BE-032 | Export | CSV/XLSX | P2 | 3 |
| BE-033 | Audit | Journal des actions sensibles | P1 | 5 |
| BE-034 | Qualité | Tests unitaires, API et migrations | P0 | 8 |
| BE-035 | Qualité | Tests concurrence stock et webhooks | P0 | 8 |
| BE-036 | Production | Logs, monitoring, sauvegarde/restauration | P0 | 8 |
| BE-037 | Documentation | OpenAPI et runbook | P1 | 3 |

## Incréments
1. Fondations, sécurité et catalogue.
2. Stock, panier, checkout et commandes.
3. Livraison Lubumbashi et COD.
4. Airtel, Orange et M-Pesa après accès marchand/sandbox.
5. Administration, notifications, 3D, analytics et durcissement.

Definition of Done : critères démontrés, tests exécutés, permissions vérifiées, migration relue, OpenAPI mise à jour et logs sans secrets.