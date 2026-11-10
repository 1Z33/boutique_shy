# Backlog backend SHY BOUTIQUE

Priorités : P0 indispensable au lancement ; P1 important ; P2 amélioration. Story Points provisoires.

| ID | Module | Travail | Priorité | SP | État de départ |
|---|---|---|---|---:|---|
| BE-001 | Fondations | Configuration FastAPI par environnement | P0 | 3 | À vérifier |
| BE-002 | DB | PostgreSQL et sessions SQLAlchemy | P0 | 3 | Fondation présente |
| BE-003 | DB | Alembic et migrations additives | P0 | 3 | Migrations appliquées localement |
| BE-004 | Sécurité | Rôles, permissions, hachage et sessions | P0 | 8 | À implémenter/vérifier |
| BE-005 | Utilisateurs | Inscription, connexion, refresh, logout | P0 | 5 | À implémenter |
| BE-006 | Utilisateurs | Profil et adresses | P1 | 3 | Modèles présents ; API à faire |
| BE-007 | Catalogue | Catégories, produits, publication | P0 | 8 | CRUD catalogue ajouté ; tests à exécuter |
| BE-008 | Catalogue | Variantes, SKU et médias | P0 | 8 | Modèles présents ; API à compléter |
| BE-009 | Catalogue | Recherche, filtres et pagination | P1 | 5 | À implémenter |
| BE-010 | Stock | Inventaire réel par variante | P0 | 3 | Modèle/migration présents |
| BE-011 | Stock | Mouvements tracés | P0 | 5 | Modèle présent ; table locale à vérifier |
| BE-012 | Stock | Réservations transactionnelles anti-surbooking | P0 | 8 | À implémenter |
| BE-013 | Stock | Expiration/libération automatique | P0 | 5 | À implémenter |
| BE-014 | Panier | Panier connecté et invité | P0 | 5 | Modèles présents ; API à faire |
| BE-015 | Checkout | Devis CDF, validation serveur, idempotence | P0 | 8 | À implémenter |
| BE-016 | Commandes | Création, snapshot, statuts, historique | P0 | 8 | Modèles présents ; API à faire |
| BE-017 | Commandes | Annulation et libération stock | P0 | 5 | À implémenter |
| BE-018 | Livraison | Zones Lubumbashi, tarifs et délais | P0 | 5 | Modèles présents ; API/configuration à faire |
| BE-019 | Livraison | Livreurs, suivi, preuve et échec | P1 | 8 | Modèle présent ; workflow à faire |
| BE-020 | Paiements | COD et collecte contrôlée | P0 | 3 | Modèle Payment ; logique à faire |
| BE-021 | Paiements | Interface commune Mobile Money | P0 | 5 | À implémenter |
| BE-022 | Paiements | Airtel Money | P0 | 8 | Intégration réelle à faire |
| BE-023 | Paiements | Orange Money | P0 | 8 | Intégration réelle à faire |
| BE-024 | Paiements | M-Pesa | P0 | 8 | Intégration réelle à faire |
| BE-025 | Paiements | Webhooks vérifiés et idempotents | P0 | 8 | À implémenter |
| BE-026 | Promotions | Codes, dates et limites | P1 | 5 | Modèle présent ; table locale à vérifier ; logique à faire |
| BE-027 | Admin | Produits, stock, commandes et clients | P0 | 8 | Partiel ; endpoints à compléter |
| BE-028 | Admin | Dashboard opérationnel | P1 | 5 | À implémenter |
| BE-029 | Notifications | File, modèles, retries et historique | P1 | 8 | Modèle présent ; worker/fournisseur à faire |
| BE-030 | 3D | API zones et placements GLB | P1 | 8 | Modèles présents ; API à faire |
| BE-031 | Analytics | Rapports ventes, paiements et stock | P1 | 8 | À implémenter |
| BE-032 | Export | CSV/XLSX | P2 | 3 | À implémenter |
| BE-033 | Audit | Journal des actions sensibles | P1 | 5 | Modèle présent ; branchement à faire |
| BE-034 | Qualité | Tests unitaires, API et migrations | P0 | 8 | Tests écrits ; exécution complète à confirmer |
| BE-035 | Qualité | Tests concurrence stock et webhooks | P0 | 8 | À écrire |
| BE-036 | Production | Logs, monitoring, sauvegarde/restauration | P0 | 8 | À implémenter |
| BE-037 | Documentation | OpenAPI et runbook | P1 | 3 | Documentation à compléter |

## Couverture des modèles SQLAlchemy

Les modèles ci-dessous sont présents dans le code backend. Leur présence dans la base ou leur disponibilité via une API doit être vérifiée séparément.

| Domaine | Modèles | Tables |
|---|---|---|
| Catalogue | Category, Product, ProductVariant | categories, products, product_variants |
| Clients | User, Address | users, addresses |
| Stock | Inventory, InventoryReservation, StockMovement | inventory, inventory_reservations, stock_movements |
| Panier | Cart, CartItem | carts, cart_items |
| Commandes | Order, OrderItem, OrderStatusHistory | orders, order_items, order_status_history |
| Paiements | Payment, PaymentWebhookEvent | payments, payment_webhook_events |
| Livraison | DeliveryZone, Delivery | delivery_zones, deliveries |
| Promotions | Promotion | promotions |
| Notifications | Notification | notifications |
| Boutique 3D | StorefrontZone3D, StorefrontPlacement3D | storefront_zones_3d, storefront_placements_3d |
| Audit | AuditLog | audit_logs |

## Incréments
1. Fondations, sécurité et catalogue.
2. Stock, panier, checkout et commandes.
3. Livraison Lubumbashi et COD.
4. Airtel, Orange et M-Pesa après accès marchand/sandbox.
5. Administration, notifications, 3D, analytics et durcissement.

## Contrôles immédiats après migration
- Confirmer `alembic current` sur `0002_commerce_foundation`.
- Vérifier le nombre réel de tables et contrôler explicitement `promotions` et `stock_movements` : ces deux tables ne sont pas visibles dans la sortie psql communiquée, malgré leurs modèles.
- Exécuter les tests de migration et les tests API ; ne pas considérer une migration réussie comme une preuve que tous les workflows métier sont terminés.

Definition of Done : critères démontrés, tests exécutés, permissions vérifiées, migration relue, OpenAPI mise à jour et logs sans secrets.
