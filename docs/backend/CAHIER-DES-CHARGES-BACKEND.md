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

## Règles critiques
- Réserver le stock dans une transaction PostgreSQL avec verrouillage de ligne.
- Recalculer prix, promotions, frais et total côté serveur.
- Vérifier signature, montant, devise, référence et commande pour chaque callback Mobile Money.
- Dédupliquer les callbacks ; aucune capture d'écran ou réponse frontend ne prouve un paiement.
- COD encaissé uniquement après collecte confirmée par un rôle autorisé.
- Refuser toute adresse hors zone de livraison Lubumbashi activée.
- Secrets fournisseurs externalisés, jamais stockés en base ou dans les logs.

## États proposés
- Commande : PENDING_PAYMENT, CONFIRMED, PROCESSING, READY_FOR_DISPATCH, OUT_FOR_DELIVERY, DELIVERED, CANCELLED, DELIVERY_FAILED, REFUNDED.
- Paiement : INITIATED, PENDING, SUCCEEDED, FAILED, CANCELLED, REFUNDED, COLLECTED.

## API indicative
Préfixe /api/v1 : /auth, /users/me, /categories, /products, /cart, /checkout/quote, /checkout, /orders, /payments, /payments/webhooks/{provider}, /delivery/zones, /deliveries, /storefront/3d, /admin/*.

## Recette
Achat invité et connecté ; prix CDF vérifiés ; concurrence stock ; expiration réservation ; callbacks falsifiés/doublons ; COD contrôlé ; adresse hors zone rejetée ; accès client limité à ses commandes ; migrations testées sur DB vierge et représentative.