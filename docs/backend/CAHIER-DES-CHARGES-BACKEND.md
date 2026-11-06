# Cahier des charges backend SHY BOUTIQUE

## Décisions métier
- CDF uniquement ; montants gérés en entiers côté API.
- Checkout avec compte ou en invité.
- Stock réel par variante taille/couleur.
- Livraison Lubumbashi uniquement au lancement.
- Paiements : Airtel Money, Orange Money, M-Pesa et paiement à la livraison.

## Modules
1. Authentification, comptes, rôles et adresses.
2. Catégories, produits, variantes, médias et recherche.
3. Inventaire physique/réservé, mouvements, alertes et réservations temporaires.
4. Panier connecté/invité et devis checkout calculé par le serveur.
5. Commandes avec snapshots prix/SKU, statuts et historique.
6. Paiements Mobile Money : initiation serveur, callbacks vérifiés, idempotence et rapprochement ; COD avec collecte autorisée.
7. Zones, frais, délais, livreurs et preuves de livraison dans Lubumbashi.
8. Promotions, administration, notifications, analytics et exports.
9. API des zones 3D, placements produits et assets GLB/glTF.

## Modèles de données intégrés

Les modèles SQLAlchemy sont regroupés dans `backend/app/models/catalog.py` et `backend/app/models/commerce.py`. Les tables sont créées par les migrations Alembic.

| Domaine | Modèle(s) | Table(s) | Responsabilité |
|---|---|---|---|
| Catalogue | Category | categories | Classification des produits |
| Catalogue | Product | products | Fiche produit, prix et devise |
| Catalogue | ProductVariant | product_variants | SKU et déclinaisons taille/couleur |
| Clients | User | users | Identité, téléphone, email, hash du mot de passe, rôle et activation |
| Clients | Address | addresses | Adresse, quartier, repère et coordonnées du destinataire |
| Stock | Inventory | inventory | Quantités physiques/réservées et seuil d'alerte par variante |
| Stock | InventoryReservation | inventory_reservations | Réservation temporaire liée à une commande, quantité, statut et expiration |
| Stock | StockMovement | stock_movements | Mouvement de stock, motif et utilisateur responsable |
| Panier | Cart, CartItem | carts, cart_items | Panier connecté ou invité et lignes par variante |
| Commandes | Order, OrderItem, OrderStatusHistory | orders, order_items, order_status_history | Commande, snapshots des articles et historique des transitions |
| Paiements | Payment, PaymentWebhookEvent | payments, payment_webhook_events | Tentatives de paiement, références et événements fournisseurs dédupliqués |
| Livraison | DeliveryZone, Delivery | delivery_zones, deliveries | Zones, tarifs, délais, livreur, statut et preuve |
| Promotions | Promotion | promotions | Code, type/valeur de remise, seuil, limites et compteur |
| Notifications | Notification | notifications | Canal, destinataire, modèle, statut et erreur |
| Boutique 3D | StorefrontZone3D, StorefrontPlacement3D | storefront_zones_3d, storefront_placements_3d | Zones et placements 3D de produits/assets |
| Traçabilité | AuditLog | audit_logs | Acteur, action, entité et détails expurgés |

### Relations principales
- Un utilisateur peut posséder plusieurs adresses, paniers et commandes.
- Un panier contient plusieurs lignes ; chaque ligne référence une variante.
- Une commande contient des lignes snapshotées et un historique de statuts.
- Une commande peut être associée à des paiements et à une livraison.
- Une variante possède un enregistrement d'inventaire ; les réservations et mouvements référencent cet inventaire.
- Une zone de livraison est référencée par une livraison.
- Une zone 3D contient plusieurs placements ; un placement peut référencer un produit.
- Les notifications et journaux d'audit peuvent référencer un utilisateur et/ou une commande.

## Règles critiques
- Réserver le stock dans une transaction PostgreSQL avec verrouillage de ligne.
- Recalculer prix, promotions, frais et total côté serveur.
- Vérifier signature, montant, devise, référence et commande pour chaque callback Mobile Money.
- Dédupliquer les callbacks ; aucune capture d'écran ou réponse frontend ne prouve un paiement.
- COD encaissé uniquement après collecte confirmée par un rôle autorisé.
- Refuser toute adresse hors zone de livraison Lubumbashi activée.
- Secrets fournisseurs externalisés, jamais stockés en base ou dans les logs.
- Un client ne peut accéder qu'à ses propres données et commandes ; les actions sensibles nécessitent des permissions explicites.

## États proposés
- Commande : PENDING_PAYMENT, CONFIRMED, PROCESSING, READY_FOR_DISPATCH, OUT_FOR_DELIVERY, DELIVERED, CANCELLED, DELIVERY_FAILED, REFUNDED.
- Paiement : INITIATED, PENDING, SUCCEEDED, FAILED, CANCELLED, REFUNDED, COLLECTED.

## API indicative
Préfixe /api/v1 : /auth, /users/me, /categories, /products, /cart, /checkout/quote, /checkout, /orders, /payments, /payments/webhooks/{provider}, /delivery/zones, /deliveries, /storefront/3d, /admin/*.

## État de réalisation — 6 novembre 2026
- Les modèles de données et la migration `0002_commerce_foundation` sont présents dans la branche de travail.
- L'utilisateur a exécuté localement `alembic upgrade head` et `alembic current` a retourné `0002_commerce_foundation (head)`.
- Les endpoints CRUD du catalogue ont été ajoutés ; les modèles seuls ne signifient pas que les API panier, commandes, paiements, livraisons, promotions, notifications ou 3D sont opérationnelles.
- Contrôle à refaire sur la base locale : la sortie `\dt` partagée montre les tables listées, mais ne fait pas apparaître `promotions` ni `stock_movements`, alors que leurs modèles existent. Vérifier explicitement ces deux tables avant de déclarer le schéma local entièrement conforme.

## Recette
Achat invité et connecté ; prix CDF vérifiés ; concurrence stock ; expiration réservation ; callbacks falsifiés/doublons ; COD contrôlé ; adresse hors zone rejetée ; accès client limité à ses commandes ; migrations testées sur DB vierge et représentative.
