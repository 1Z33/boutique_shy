# SHY BOUTIQUE frontend

## Requirements

- Node.js 20.9+
- npm

## Install and run

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:3000.

## Current prototype

The homepage includes an interactive Three.js showroom with architectural panels, clothing rails, mannequins, shoe and handbag displays, plants and lighting; editorial product imagery; a responsive navigation; and a demo cart drawer with add/remove interactions.

The current product list and cart are local demonstration state. Cart contents are not persisted and are not connected to an API, inventory, checkout or payment provider. The checkout control is deliberately disabled. Do not accept real orders from this prototype.

## Visual assets

The editorial photographs use remote Unsplash image URLs for the first visual prototype. Replace or confirm all product photography against actual supplier/product images before commercial publication. The 3D architecture is procedurally composed in React Three Fiber for this first iteration; production Blender/GLB assets can replace it later.