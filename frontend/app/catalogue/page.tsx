"use client";

import Image from "next/image";
import Link from "next/link";
import { useMemo, useState, useEffect } from "react";
import { ArrowLeft, Search, X, ShoppingCart } from "lucide-react";
import { DEMO_PRODUCTS, DemoProduct } from "@/data/demo-products";
import "./catalogue.css";

type Category = "Tout" | "Vêtements" | "Chaussures";


export default function CataloguePage() {
  const [category, setCategory] = useState<Category>("Tout");
  const [query, setQuery] = useState("");
  const [sort, setSort] = useState("featured");
  const [selected, setSelected] = useState<DemoProduct | null>(null);
  const [buying, setBuying] = useState(false);
  const [cart, setCart] = useState<DemoProduct[]>([]);
  const [showCart, setShowCart] = useState(false);
  const [account, setAccount] = useState<{name:string;email:string} | null>(null);
  const [form, setForm] = useState({name:"",email:"",password:""});

  useEffect(() => {
    try {
      const c = localStorage.getItem("cart"); if (c) setCart(JSON.parse(c));
      const a = localStorage.getItem("account"); if (a) setAccount(JSON.parse(a));
    } catch {}
  }, []);

  const persistCart = (next: DemoProduct[]) => { setCart(next); localStorage.setItem("cart", JSON.stringify(next)); };
  const persistAccount = (acc: {name:string;email:string}) => { setAccount(acc); localStorage.setItem("account", JSON.stringify(acc)); };
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
        <nav><Link href="/">ACCUEIL</Link><Link href="/#maison">LA MAISON</Link><button onClick={()=>setShowCart(true)} style={{background:"none",border:"none",cursor:"pointer",color:"inherit"}} aria-label="Panier"><ShoppingCart size={18}/> ({cart.length})</button></nav>
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
          <article className="catalogue-product" key={product.id} onClick={()=>setSelected(product)} style={{cursor:"pointer"}}>
            <div className="catalogue-image">
              <Image src={product.image} alt={product.name} fill sizes="(max-width: 700px) 90vw, 33vw" unoptimized />
              <span className="catalogue-number">{String(index+1).padStart(2,"0")}</span>
              <span className="catalogue-image-caption">{product.category.toUpperCase()}</span>
            </div>
            <div className="catalogue-product-meta"><span>{product.note}</span><span>APERÇU</span></div>
            <div className="catalogue-product-title"><h2>{product.name}</h2><strong>{product.price} {product.currency}</strong></div>
            <p className="catalogue-demo-note">Article de démonstration · Prix indicatif</p>
          </article>
        ))}
      </section>
      {filtered.length===0 && <section className="catalogue-empty"><p>Aucune pièce trouvée.</p><button onClick={()=>{setQuery("");setCategory("Tout");}}>EFFACER LES FILTRES</button></section>}
      {selected && (
        <div className="catalogue-modal" onClick={()=>{setSelected(null);setBuying(false);}} style={{position:"fixed",inset:0,background:"rgba(0,0,0,0.6)",display:"flex",alignItems:"center",justifyContent:"center",zIndex:50}} role="dialog" aria-modal="true">
          <div onClick={(e)=>e.stopPropagation()} style={{background:"#fff",maxWidth:480,width:"90%",padding:24,borderRadius:8}}>
            <Image src={selected.image} alt={selected.name} width={432} height={320} unoptimized style={{width:"100%",height:"auto"}} />
            <h2>{selected.name}</h2>
            <p>{selected.note}</p>
            <p><strong>{selected.price} {selected.currency}</strong></p>
            <p style={{fontSize:12,color:"#888"}}>Article de démonstration · Prix indicatif</p>
            {!buying ? (
              <button onClick={()=>setBuying(true)} style={{marginTop:12,padding:"10px 16px",background:"#514438",color:"#fff",border:"none",cursor:"pointer"}}>Acheter</button>
            ) : account ? (
              <div style={{marginTop:12}}>
                <p>Ajouté au panier pour {account.name}.</p>
                <button onClick={()=>{persistCart([...cart, selected!]); setSelected(null); setBuying(false);}} style={{padding:"10px 16px",background:"#514438",color:"#fff",border:"none",cursor:"pointer"}}>Confirmer l&apos;ajout</button>
              </div>
            ) : (
              <div style={{marginTop:12}}>
                <p>Pour finaliser votre achat, veuillez créer un compte.</p>
                <input placeholder="Nom" value={form.name} onChange={e=>setForm({...form,name:e.target.value})} style={{display:"block",marginBottom:8,width:"100%"}} />
                <input placeholder="Email" value={form.email} onChange={e=>setForm({...form,email:e.target.value})} style={{display:"block",marginBottom:8,width:"100%"}} />
                <input type="password" placeholder="Mot de passe" value={form.password} onChange={e=>setForm({...form,password:e.target.value})} style={{display:"block",marginBottom:8,width:"100%"}} />
                <button onClick={()=>{persistAccount({name:form.name,email:form.email}); setBuying(true);}} style={{padding:"10px 16px",background:"#514438",color:"#fff",border:"none",cursor:"pointer"}}>Créer un compte</button>
                <button onClick={()=>setBuying(false)} style={{marginLeft:8,padding:"10px 16px",background:"transparent",border:"1px solid #514438",cursor:"pointer"}}>Annuler</button>
              </div>
            )}
            <button onClick={()=>{setSelected(null);setBuying(false);}} style={{position:"absolute",top:16,right:16,background:"transparent",border:"none",fontSize:20,cursor:"pointer"}} aria-label="Fermer">×</button>
          </div>
        </div>
      )}
      {showCart && (
        <div style={{position:"fixed",inset:0,background:"rgba(0,0,0,0.6)",display:"flex",justifyContent:"flex-end",zIndex:60}} onClick={()=>setShowCart(false)}>
          <div onClick={e=>e.stopPropagation()} style={{background:"#fff",width:360,maxWidth:"90%",padding:24,overflowY:"auto"}}>
            <h2>Panier ({cart.length})</h2>
            {cart.length===0 && <p>Panier vide.</p>}
            {cart.map((p,i)=>(
              <div key={i} style={{display:"flex",gap:8,marginBottom:12,alignItems:"center"}}>
                <Image src={p.image} alt={p.name} width={60} height={60} unoptimized style={{objectFit:"cover"}} />
                <div style={{flex:1}}><div>{p.name}</div><div>{p.price} {p.currency}</div></div>
                <button onClick={()=>persistCart(cart.filter((_,idx)=>idx!==i))} style={{background:"none",border:"none",cursor:"pointer"}} aria-label="Retirer">×</button>
              </div>
            ))}
            {cart.length>0 && <div style={{marginTop:16,fontWeight:"bold"}}>Total: {cart.reduce((s,p)=>s+p.price,0)} USD</div>}
            <button onClick={()=>setShowCart(false)} style={{marginTop:16}}>Fermer</button>
          </div>
        </div>
      )}
      <footer className="catalogue-footer"><span>© {new Date().getFullYear()} SHY BOUTIQUE</span><span>RÉPUBLIQUE DÉMOCRATIQUE DU CONGO</span><Link href="/"><ArrowLeft size={14}/> RETOUR À L’ACCUEIL</Link></footer>
    </main>
  );
}
