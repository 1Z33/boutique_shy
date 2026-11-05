import Image from "next/image";
import Link from "next/link";
import "./catalogue.css";

type Variant = {
  id: number;
  sku: string;
  size: string | null;
  color: string | null;
  stock_quantity: number;
  is_active: boolean;
};

type Product = {
  id: number;
  category_id: number;
  name: string;
  slug: string;
  description: string | null;
  price: string;
  currency: "USD" | "CDF";
  images: string[];
  is_active: boolean;
  is_featured: boolean;
  variants: Variant[];
};

async function getProducts(): Promise<Product[]> {
  const api = process.env.API_URL ?? "http://localhost:8000";
  try {
    const response = await fetch(`${api}/api/v1/catalog/products?limit=60`, { cache: "no-store" });
    if (!response.ok) return [];
    return (await response.json()) as Product[];
  } catch {
    return [];
  }
}

export const metadata = {
  title: "Collections | SHY BOUTIQUE",
  description: "Découvrez la sélection de vêtements et chaussures pour femme de SHY BOUTIQUE.",
};

export default async function CataloguePage() {
  const products = await getProducts();
  return (
    <main className="catalogue-page">
      <header className="catalogue-header">
        <Link href="/" className="catalogue-brand">SHY <span>BOUTIQUE</span><small>MAISON DE MODE</small></Link>
        <nav><Link href="/">ACCUEIL</Link><Link href="/#maison">LA MAISON</Link></nav>
      </header>
      <section className="catalogue-intro">
        <p className="catalogue-eyebrow">LA SÉLECTION SHY</p>
        <h1>Les pièces <em>à découvrir.</em></h1>
        <p>Une sélection féminine, choisie avec soin. Chaque pièce raconte une allure.</p>
      </section>
      {products.length ? (
        <section className="catalogue-grid" aria-label="Produits disponibles">
          {products.map((product) => {
            const available = product.variants.some((variant) => variant.is_active && variant.stock_quantity > 0);
            const image = product.images[0];
            return (
              <article className="catalogue-product" key={product.id}>
                <Link href={`/catalogue/${product.slug}`} className="catalogue-image">
                  {image ? <Image src={image} alt={product.name} fill sizes="(max-width: 700px) 90vw, 33vw" unoptimized /> : <span>SHY BOUTIQUE</span>}
                </Link>
                <div className="catalogue-product-meta"><span>{product.is_featured ? "SÉLECTION SHY" : "COLLECTION"}</span><span>{available ? "DISPONIBLE" : "STOCK À CONFIRMER"}</span></div>
                <div className="catalogue-product-title"><h2>{product.name}</h2><strong>{Number(product.price).toLocaleString("fr-FR")} {product.currency === "USD" ? "$" : "FC"}</strong></div>
                <Link href={`/catalogue/${product.slug}`} className="catalogue-detail">DÉCOUVRIR LA PIÈCE <span>↗</span></Link>
              </article>
            );
          })}
        </section>
      ) : (
        <section className="catalogue-empty">
          <p>La collection se prépare.</p>
          <span>Les articles ajoutés par SHY BOUTIQUE apparaîtront ici dès que le catalogue sera connecté.</span>
        </section>
      )}
      <footer className="catalogue-footer"><span>© {new Date().getFullYear()} SHY BOUTIQUE</span><span>RÉPUBLIQUE DÉMOCRATIQUE DU CONGO</span></footer>
    </main>
  );
}
