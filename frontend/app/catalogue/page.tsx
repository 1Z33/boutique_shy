"use client";

import Image from "next/image";
import Link from "next/link";
import { useMemo, useState } from "react";
import { ArrowLeft, ArrowUpRight, Search, X } from "lucide-react";
import { DEMO_PRODUCTS } from "@/data/demo-products";
import "./catalogue.css";

type Category = "Tout" | "Vêtements" | "Chaussures";

export const metadata = undefined;

export default function CataloguePage() {
  const [category, setCategory] = useState<Category>("Tout");
  const [query, setQuery] = useState("");
  const [sort, setSort] = useState("featured");
  const filtered = useMemo(() => {
    const term = query.trim().toLocaleLowerCase("fr");
    const list = DEMO_PRODUCTS.filter((p) =>
      (category === "Tout" || p.category === category) &&
      (!term || (p.name + " " + p.category + " " + p.note).toLocaleLowerCase("fr").includes(term))
    );
    if (sort === "price-asc") list.sort((a,b) => a.price-b.price);
    if (sort === "price-desc") list.sort((a,b) => b.price-a.price);
    if (sort === "name") list.sort((a,b) => a.name.localeCompare(b.name, "fr"));
    return list;
  }, [category, query, sort]);

  return (
    <main className="catalogue-page">
      <header className="catalogue-header">
        <Link href="/" className="catalogue-brand">SHY <span>BOUTIQUE</span><small>MAISON DE MODE</small></Link>
        <nav><Link href="/">ACCUEIL</Link><Link href="/#maison">LA MAISON</Link></nav>
      </header>
      <section className="catalogue-intro">
        <p className="catalogue-eyebrow">COLLECTION · 01 — SHY BOUTIQUE</p>
        <h1>Les pièces <em>à découvrir.</em></h1>
        <p>Une sélection féminine de vêtements et chaussures, pensée pour accompagner chaque allure.</p>
      </section>
      <section className="catalogue-tools" aria-label="Rechercher et filtrer les articles">
        <div className="catalogue-count"><strong>{filtered.length.toString().padStart(2,"0")}</strong><span>ARTICLES DANS LA SÉLECTION</span></div>
        <div className="catalogue-controls">
          <label className="catalogue-search"><Search size={16}/><input value={query} onChange={(e)=>setQuery(e.target.value)} placeholder="Rechercher une pièce"/>{query && <button onClick={()=>setQuery("")} aria-label="Effacer"><X size={15}/></button>}</label>
          <div className="catalogue-filters">
            {(["Tout","Vêtements","Chaussures"] as Category[]).map((item)=><button key={item} className={category===item?"active":""} onClick={()=>setCategory(item)}>{item}</button>)}
          </div>
          <select className="catalogue-sort" value={sort} onChange={(e)=>setSort(e.target.value)} aria-label="Trier les articles">
            <option value="featured">Ordre de sélection</option><option value="price-asc">Prix croissant</option><option value="price-desc">Prix décroissant</option><option value="name">Nom</option>
          </select>
        </div>
      </section>
      <section className="catalogue-grid" aria-label="Collection de 50 articles">
        {filtered.map((product,index)=>(
          <article className="catalogue-product" key={product.id}>
            <div className="catalogue-image">
              <Image src={product.image} alt={product.name} fill sizes="(max-width: 700px) 90vw, 33vw" unoptimized />
              <span className="catalogue-number">{String(index+1).padStart(2,"0")}</span>
              <span className="catalogue-image-caption">{product.category.toUpperCase()}</span>
            </div>
            <div className="catalogue-product-meta"><span>{product.note}</span><span>APERÇU</span></div>
            <div className="catalogue-product-title"><h2>{product.name}</h2><strong>{product.price} $</strong></div>
            <p className="catalogue-demo-note">Article de démonstration · Prix indicatif</p>
          </article>
        ))}
      </section>
      {filtered.length===0 && <section className="catalogue-empty"><p>Aucune pièce trouvée.</p><button onClick={()=>{setQuery("");setCategory("Tout");}}>EFFACER LES FILTRES</button></section>}
      <footer className="catalogue-footer"><span>© {new Date().getFullYear()} SHY BOUTIQUE</span><span>RÉPUBLIQUE DÉMOCRATIQUE DU CONGO</span><Link href="/"><ArrowLeft size={14}/> RETOUR À L’ACCUEIL</Link></footer>
    </main>
  );
}
