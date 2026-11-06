# SHY BOUTIQUE — Cahier des charges

## Vision

SHY BOUTIQUE est une boutique e-commerce de vêtements et chaussures pour femmes, destinée au marché de la République démocratique du Congo. L'expérience principale est un showroom 3D immersif, accompagné d'un parcours catalogue et d'achat classique accessible.

## Identité et design

- Positionnement féminin, luxe discret, minimaliste et éditorial.
- Palette : crème, travertin, beige naturel, bois foncé, laiton brossé et rose poudré atténué.
- Composition éditoriale, titres alignés à gauche, typographies avec empattements pour les titres et sans-serif pour l'interface.
- À proscrire : dégradé violet, fond blanc plat, néon, bordures lumineuses, boutons indigo, titres centrés, deux gros CTA concurrents, trois cartes de fonctionnalités, bento grid, coins arrondis systématiques, ombres omniprésentes, liquid glass, grille de points, bulles floues, icônes étincelles, faux compteurs, hover omniprésent, police Inter, emojis dans les titres, faux témoignages, faux prix, badge « le plus populaire » sans données et démonstrations prétendant être fonctionnelles alors qu'elles ne le sont pas.

## Expérience 3D

- Showroom avec entrée, vêtements, chaussures, nouveautés et promotions.
- Navigation souris et tactile, caméra contrôlée et transitions mesurées.
- Sélection d'un présentoir ou produit et ouverture d'une fiche HTML accessible.
- Scène progressive, modèles optimisés, textures compressées et mode catalogue alternatif si WebGL indisponible.
- Les produits de la scène doivent être reliés à des produits réels en base de données en production.
- Les modèles 3D de produits sont facultatifs ; une photographie produit peut être utilisée sur un présentoir 3D.

## E-commerce

- Catalogue, catégories, recherche, filtres et tri.
- Fiche produit avec images, tailles, couleurs, prix et stock par variante.
- Panier persistant, commande invitée ou avec compte.
- Paiement Mobile Money et paiement à la livraison.
- Livraison à domicile, zones et tarifs configurables.
- Suivi des commandes, notifications et historique.
- Administration des produits, variantes, stocks, commandes, paiements, livraisons, promotions et médias.

## Marché et paramètres

- Marché initial : RDC.
- Devise retenue : CDF uniquement. Aucun taux de conversion USD/CDF n'est utilisé dans le parcours de vente.
- Moyens de paiement : Mobile Money via un prestataire/opérateur contracté et paiement à la livraison.
- Les paiements doivent être confirmés par une preuve serveur vérifiable ; aucune déclaration cliente ne suffit.

## Médias et propriété

- Le commanditaire confie la direction artistique et l'intégration des ressources visuelles au développement.
- Photos de produits réels à obtenir auprès de la boutique ou de fournisseurs autorisés avant vente.
- Les visuels IA et éditoriaux de démonstration ne doivent pas induire la cliente en erreur sur les produits réels.
- Les créations originales, le code spécifique, les données, la documentation et les accès du projet doivent être remis au propriétaire de SHY BOUTIQUE, sous réserve des licences des composants tiers.
- Tenir un registre des licences des bibliothèques, polices, photos, textures et modèles 3D.

## Architecture cible

- Frontend : Next.js App Router, TypeScript, Tailwind CSS.
- 3D : Three.js, React Three Fiber, Drei, GSAP, Blender, GLB/glTF.
- Backend : FastAPI, SQLAlchemy, Alembic.
- Base de données : PostgreSQL.
- Médias : stockage objet/CDN (ex. Cloudinary).
- Tests : Pytest et Playwright.
- Déploiement : Docker, HTTPS, sauvegardes et surveillance.

## État de la première itération

Le dépôt contient une première homepage visuelle et une scène 3D interactive procédurale. Le panier et les produits affichés sont une démonstration locale, sans backend ni paiement. Les photographies sont éditoriales et doivent être validées/remplacées par les visuels des produits réellement vendus avant lancement.