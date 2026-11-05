"use client";

import { useMemo, useState } from "react";
import dynamic from "next/dynamic";
import Image from "next/image";
import { ArrowDown, ArrowRight, ArrowUpRight, Bag, Menu, Search, X } from "lucide-react";

const BoutiqueScene = dynamic(() => import("@/components/boutique-scene"), {
  ssr: false,
  loading: () => <div className="scene-loading">Préparation de votre visite…</div>,
});

const products = [
  { id: 1, name: "Robe Alba", category: "VÊTEMENTS", price: 48, image: "https://images.unsplash.com/photo-1539109136881-3be0616acf4b?w=900&q=85", note: "La pièce signature" },
  { id: 2, name: "Escarpins Élise", category: "CHAUSSURES", price: 62, image: "https://images.unsplash.com/photo-1543163521-1bf539c55dd2?w=900&q=85", note: "Ligne essentielle" },
  { id: 3, name: "Ensemble Sienna", category: "VÊTEMENTS", price: 74, image: "https://images.unsplash.com/photo-1490481651871-ab68de25d43d?w=900&q=85", note: "Élégance quotidienne" },
];

export default function Home() {
  const [menuOpen, setMenuOpen] = useState(false);
  const [cartCount, setCartCount] = useState(0);
  const [selected, setSelected] = useState<number | null>(null);
  const [showVisit, setShowVisit] = useState(false);
  const selectedProduct = useMemo(() => products.find((p) => p.id === selected), [selected]);

  return (
    <main>
      <header className="site-header">
        <button className="icon-button mobile-menu" aria-label="Ouvrir le menu" onClick={() => setMenuOpen(!menuOpen)}>{menuOpen ? <X /> : <Menu />}</button>
        <a href="#" className="wordmark" aria-label="SHY Boutique accueil">SHY<span> BOUTIQUE</span><small>MAISON DE MODE</small></a>
        <nav className={menuOpen ? "main-nav nav-open" : "main-nav"}>
          <a href="#univers" onClick={() => setMenuOpen(false)}>L’UNIVERS</a>
          <a href="#collections" onClick={() => setMenuOpen(false)}>COLLECTIONS</a>
          <a href="#maison" onClick={() => setMenuOpen(false)}>LA MAISON</a>
        </nav>
        <div className="header-actions">
          <button className="icon-button" aria-label="Rechercher"><Search size={19} /></button>
          <button className="bag-button" onClick={() => document.getElementById("collections")?.scrollIntoView({ behavior: "smooth" })}><Bag size={18} /><span>Panier ({cartCount})</span></button>
        </div>
      </header>

      <section className="immersive-hero" id="univers">
        <BoutiqueScene onSelectProduct={setSelected} />
        <div className="hero-shade" />
        <div className="hero-copy">
          <p className="eyebrow light">UNE AUTRE FAÇON DE DÉCOUVRIR LA MODE</p>
          <h1>Le style se vit.<br /><em>Il se découvre.</em></h1>
          <p className="hero-description">Entrez dans l’univers SHY. Explorez une sélection de pièces pensées pour accompagner votre allure, chaque jour.</p>
          <button className="text-link light-link" onClick={() => setShowVisit(!showVisit)}>EXPLORER LA BOUTIQUE <ArrowRight size={17} /></button>
          {showVisit && <p className="visit-hint">Déplacez la souris pour observer l’espace. Sélectionnez un présentoir pour découvrir les pièces.</p>}
        </div>
        <div className="hero-index"><span>01</span><i /> <span>UNIVERS SHY</span></div>
        <button className="scroll-cue" onClick={() => document.getElementById("collections")?.scrollIntoView({ behavior: "smooth" })}><ArrowDown size={16} /> DÉFILER</button>
        <div className="scene-label"><span className="label-dot" /> SHOWROOM VIRTUEL · VISITE INTERACTIVE</div>
        {selectedProduct && (
          <aside className="product-popover">
            <button className="popover-close" onClick={() => setSelected(null)} aria-label="Fermer"><X size={16} /></button>
            <span className="eyebrow">SÉLECTION SHY</span>
            <h3>{selectedProduct.name}</h3>
            <p>{selectedProduct.category}</p>
            <strong>{selectedProduct.price.toLocaleString("fr-FR")} $</strong>
            <button className="popover-action" onClick={() => { setCartCount((n) => n + 1); setSelected(null); }}>AJOUTER AU PANIER <ArrowRight size={15} /></button>
          </aside>
        )}
      </section>

      <section className="intro-band" id="maison">
        <p className="eyebrow">L’ART DE SE SENTIR SOI</p>
        <div className="intro-content">
          <h2>Une allure.<br /><em>Votre signature.</em></h2>
          <div><p>SHY BOUTIQUE réunit vêtements et chaussures dans une sélection féminine, libre et contemporaine. Des lignes choisies avec soin, pour celles qui savent que le style commence par soi.</p><a className="text-link dark-link" href="#collections">DÉCOUVRIR LA SÉLECTION <ArrowUpRight size={17} /></a></div>
        </div>
      </section>

      <section className="collection-section" id="collections">
        <div className="section-heading">
          <div><p className="eyebrow">LA SÉLECTION SHY</p><h2>Les pièces <em>à découvrir.</em></h2></div>
          <a className="text-link dark-link" href="#collections">TOUTE LA COLLECTION <ArrowRight size={17} /></a>
        </div>
        <div className="product-grid">
          {products.map((product, index) => (
            <article className="product-card" key={product.id}>
              <a className="product-image" href="#univers">
                <Image src={product.image} alt={product.name} fill sizes="(max-width: 700px) 90vw, 33vw" unoptimized />
                <span className="product-number">0{index + 1}</span>
                <span className="product-open"><ArrowUpRight size={18} /></span>
              </a>
              <div className="product-meta"><span>{product.category}</span><span>{product.note}</span></div>
              <div className="product-title-row"><h3>{product.name}</h3><strong>{product.price} $</strong></div>
              <button className="quick-add" onClick={() => setCartCount((n) => n + 1)}>AJOUTER AU PANIER <ArrowRight size={15} /></button>
            </article>
          ))}
        </div>
      </section>

      <section className="campaign">
        <Image src="https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?w=1800&q=90" alt="Éditorial mode SHY Boutique" fill sizes="100vw" unoptimized />
        <div className="campaign-overlay" />
        <div className="campaign-copy"><p className="eyebrow light">L’ESPRIT SHY</p><h2>La confiance<br />est le plus beau<br /><em>des accessoires.</em></h2><a className="text-link light-link" href="#collections">TROUVER VOTRE PIÈCE <ArrowRight size={17} /></a></div>
        <span className="campaign-caption">COLLECTION · ÉDITORIAL</span>
      </section>

      <footer className="site-footer">
        <div><a href="#" className="wordmark footer-mark">SHY<span> BOUTIQUE</span><small>MAISON DE MODE</small></a><p>Une sélection pensée pour votre allure.</p></div>
        <div className="footer-links"><a href="#collections">Collections</a><a href="#maison">La maison</a><a href="https://wa.me/" target="_blank" rel="noreferrer">Nous contacter</a></div>
        <div className="footer-bottom"><span>© {new Date().getFullYear()} SHY BOUTIQUE</span><span>RÉPUBLIQUE DÉMOCRATIQUE DU CONGO</span><span>MODE · STYLE · LIBERTÉ</span></div>
      </footer>
    </main>
  );
}