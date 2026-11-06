export type DemoProduct = {
  id: number;
  name: string;
  category: "Vêtements" | "Chaussures";
  price: number;
  currency: "USD";
  image: string;
  note: string;
  slug: string;
  demo: true;
};

export const DEMO_PRODUCTS: DemoProduct[] = [
  { id: 1, name: "Robe Alba", category: "Vêtements", price: 48, currency: "USD", image: "https://images.unsplash.com/photo-1539109136881-3be0616acf4f?auto=format&fit=crop&w=900&q=82", note: "La pièce signature", slug: "article-01", demo: true },
  { id: 2, name: "Robe Solène", category: "Vêtements", price: 56, currency: "USD", image: "https://images.unsplash.com/photo-1490481651871-ab68de25d43d?auto=format&fit=crop&w=900&q=82", note: "Ligne fluide", slug: "article-02", demo: true },
  { id: 3, name: "Robe Amara", category: "Vêtements", price: 64, currency: "USD", image: "https://images.unsplash.com/photo-1483985988355-763728e1935b?auto=format&fit=crop&w=900&q=82", note: "Élégance urbaine", slug: "article-03", demo: true },
  { id: 4, name: "Robe Céleste", category: "Vêtements", price: 59, currency: "USD", image: "https://images.unsplash.com/photo-1485230895905-ec40ba36b9bc?auto=format&fit=crop&w=900&q=82", note: "Silhouette légère", slug: "article-04", demo: true },
  { id: 5, name: "Robe Noémie", category: "Vêtements", price: 72, currency: "USD", image: "https://images.unsplash.com/photo-1529139574466-a303027c1d8b?auto=format&fit=crop&w=900&q=82", note: "Coupe contemporaine", slug: "article-05", demo: true },
  { id: 6, name: "Robe Élora", category: "Vêtements", price: 68, currency: "USD", image: "https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=900&q=82", note: "Allure affirmée", slug: "article-06", demo: true },
  { id: 7, name: "Robe Sienna", category: "Vêtements", price: 74, currency: "USD", image: "https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?auto=format&fit=crop&w=900&q=82", note: "Élégance quotidienne", slug: "article-07", demo: true },
  { id: 8, name: "Robe Maëlys", category: "Vêtements", price: 52, currency: "USD", image: "https://images.unsplash.com/photo-1525507119028-ed4c629a60a3?auto=format&fit=crop&w=900&q=82", note: "Douceur naturelle", slug: "article-08", demo: true },
  { id: 9, name: "Robe Inès", category: "Vêtements", price: 61, currency: "USD", image: "https://images.unsplash.com/photo-1551232864-3f0890e580d9?auto=format&fit=crop&w=900&q=82", note: "Essentiel féminin", slug: "article-09", demo: true },
  { id: 10, name: "Robe Naïa", category: "Vêtements", price: 66, currency: "USD", image: "https://images.unsplash.com/photo-1509631179647-0177331693ae?auto=format&fit=crop&w=900&q=82", note: "Esprit soirée", slug: "article-10", demo: true },
  { id: 11, name: "Ensemble Sora", category: "Vêtements", price: 82, currency: "USD", image: "https://images.unsplash.com/photo-1512316609839-ce289d3eba0a?auto=format&fit=crop&w=900&q=82", note: "Coordonné moderne", slug: "article-11", demo: true },
  { id: 12, name: "Ensemble Aïcha", category: "Vêtements", price: 78, currency: "USD", image: "https://images.unsplash.com/photo-1566206091558-7f218b696731?auto=format&fit=crop&w=900&q=82", note: "Ligne structurée", slug: "article-12", demo: true },
  { id: 13, name: "Ensemble Mila", category: "Vêtements", price: 88, currency: "USD", image: "https://images.unsplash.com/photo-1524504388940-b1c1722653e1?auto=format&fit=crop&w=900&q=82", note: "Minimalisme chic", slug: "article-13", demo: true },
  { id: 14, name: "Blouse Iris", category: "Vêtements", price: 34, currency: "USD", image: "https://images.unsplash.com/photo-1564257577-3f2f1f8a3d7f?auto=format&fit=crop&w=900&q=82", note: "Détail délicat", slug: "article-14", demo: true },
  { id: 15, name: "Blouse Yara", category: "Vêtements", price: 39, currency: "USD", image: "https://images.unsplash.com/photo-1551163943-3f6a855d1153?auto=format&fit=crop&w=900&q=82", note: "Légèreté au quotidien", slug: "article-15", demo: true },
  { id: 16, name: "Chemise Diane", category: "Vêtements", price: 42, currency: "USD", image: "https://images.unsplash.com/photo-1598554747436-c9293d6a588f?auto=format&fit=crop&w=900&q=82", note: "Classique revisité", slug: "article-16", demo: true },
  { id: 17, name: "Top Naya", category: "Vêtements", price: 29, currency: "USD", image: "https://images.unsplash.com/photo-1551488831-00ddcb6c6bd3?auto=format&fit=crop&w=900&q=82", note: "L'essentiel", slug: "article-17", demo: true },
  { id: 18, name: "Top Eden", category: "Vêtements", price: 31, currency: "USD", image: "https://images.unsplash.com/photo-1566206091558-7f218b696731?auto=format&fit=crop&w=900&q=82", note: "Ligne épurée", slug: "article-18", demo: true },
  { id: 19, name: "Pantalon Alix", category: "Vêtements", price: 49, currency: "USD", image: "https://images.unsplash.com/photo-1594633312681-425c7b97ccd1?auto=format&fit=crop&w=900&q=82", note: "Coupe élégante", slug: "article-19", demo: true },
  { id: 20, name: "Pantalon Jade", category: "Vêtements", price: 53, currency: "USD", image: "https://images.unsplash.com/photo-1503342217505-b0a15ec3261c?auto=format&fit=crop&w=900&q=82", note: "Mouvement libre", slug: "article-20", demo: true },
  { id: 21, name: "Jupe Livia", category: "Vêtements", price: 44, currency: "USD", image: "https://images.unsplash.com/photo-1583496661160-fb5886a0aaaa?auto=format&fit=crop&w=900&q=82", note: "Silhouette délicate", slug: "article-21", demo: true },
  { id: 22, name: "Jupe Romy", category: "Vêtements", price: 46, currency: "USD", image: "https://images.unsplash.com/photo-1584917865442-de89df76afd3?auto=format&fit=crop&w=900&q=82", note: "Touche raffinée", slug: "article-22", demo: true },
  { id: 23, name: "Veste Mona", category: "Vêtements", price: 89, currency: "USD", image: "https://images.unsplash.com/photo-1548126032-079a0fb0099d?auto=format&fit=crop&w=900&q=82", note: "Pièce de caractère", slug: "article-23", demo: true },
  { id: 24, name: "Blazer Alba", category: "Vêtements", price: 96, currency: "USD", image: "https://images.unsplash.com/photo-1591047139829-d91aecb6caea?auto=format&fit=crop&w=900&q=82", note: "Tailoring féminin", slug: "article-24", demo: true },
  { id: 25, name: "Cardigan Lune", category: "Vêtements", price: 58, currency: "USD", image: "https://images.unsplash.com/photo-1576566588028-4147f3842f27?auto=format&fit=crop&w=900&q=82", note: "Confort sophistiqué", slug: "article-25", demo: true },
  { id: 26, name: "Escarpins Élise", category: "Chaussures", price: 62, currency: "USD", image: "https://images.unsplash.com/photo-1543163521-1bf539c55dd2?auto=format&fit=crop&w=900&q=82", note: "Ligne essentielle", slug: "article-26", demo: true },
  { id: 27, name: "Sandales Nala", category: "Chaussures", price: 45, currency: "USD", image: "https://images.unsplash.com/photo-1543163521-1bf539c55dd2?auto=format&fit=crop&w=900&q=82", note: "Élégance estivale", slug: "article-27", demo: true },
  { id: 28, name: "Mules Ava", category: "Chaussures", price: 49, currency: "USD", image: "https://images.unsplash.com/photo-1515347619252-60a4bf4fff4f?auto=format&fit=crop&w=900&q=82", note: "Facilité chic", slug: "article-28", demo: true },
  { id: 29, name: "Ballerines Zoé", category: "Chaussures", price: 42, currency: "USD", image: "https://images.unsplash.com/photo-1560343090-f0409e92791a?auto=format&fit=crop&w=900&q=82", note: "Grâce au quotidien", slug: "article-29", demo: true },
  { id: 30, name: "Bottines Romane", category: "Chaussures", price: 78, currency: "USD", image: "https://images.unsplash.com/photo-1608256246200-53e635b5b65f?auto=format&fit=crop&w=900&q=82", note: "Caractère affirmé", slug: "article-30", demo: true },
  { id: 31, name: "Bottes Élina", category: "Chaussures", price: 94, currency: "USD", image: "https://images.unsplash.com/photo-1608231387042-66d1773070a5?auto=format&fit=crop&w=900&q=82", note: "Allure intemporelle", slug: "article-31", demo: true },
  { id: 32, name: "Sneakers Aya", category: "Chaussures", price: 59, currency: "USD", image: "https://images.unsplash.com/photo-1542291026-7eec264c27ff?auto=format&fit=crop&w=900&q=82", note: "Esprit contemporain", slug: "article-32", demo: true },
  { id: 33, name: "Sneakers June", category: "Chaussures", price: 64, currency: "USD", image: "https://images.unsplash.com/photo-1549298916-b41d501d3772?auto=format&fit=crop&w=900&q=82", note: "Confort urbain", slug: "article-33", demo: true },
  { id: 34, name: "Sandales Lila", category: "Chaussures", price: 52, currency: "USD", image: "https://images.unsplash.com/photo-1460353581641-37baddab0fa2?auto=format&fit=crop&w=900&q=82", note: "Ligne solaire", slug: "article-34", demo: true },
  { id: 35, name: "Talons Sofia", category: "Chaussures", price: 69, currency: "USD", image: "https://images.unsplash.com/photo-1600185365483-26d7a4cc7519?auto=format&fit=crop&w=900&q=82", note: "Élégance du soir", slug: "article-35", demo: true },
  { id: 36, name: "Mocassins Alma", category: "Chaussures", price: 71, currency: "USD", image: "https://images.unsplash.com/photo-1514989940723-e8e51635b782?auto=format&fit=crop&w=900&q=82", note: "Classique moderne", slug: "article-36", demo: true },
  { id: 37, name: "Compensées Inaya", category: "Chaussures", price: 57, currency: "USD", image: "https://images.unsplash.com/photo-1531310197839-ccf54634509e?auto=format&fit=crop&w=900&q=82", note: "Hauteur maîtrisée", slug: "article-37", demo: true },
  { id: 38, name: "Sandales Eden", category: "Chaussures", price: 48, currency: "USD", image: "https://images.unsplash.com/photo-1562273138-f46be4ebdf33?auto=format&fit=crop&w=900&q=82", note: "Légèreté d'été", slug: "article-38", demo: true },
  { id: 39, name: "Escarpins Mina", category: "Chaussures", price: 75, currency: "USD", image: "https://images.unsplash.com/photo-1515347619252-60a4bf4fff4f?auto=format&fit=crop&w=900&q=82", note: "Ligne sophistiquée", slug: "article-39", demo: true },
  { id: 40, name: "Mules Sacha", category: "Chaussures", price: 54, currency: "USD", image: "https://images.unsplash.com/photo-1543163521-1bf539c55dd2?auto=format&fit=crop&w=900&q=82", note: "Simplicité précieuse", slug: "article-40", demo: true },
  { id: 41, name: "Baskets Louna", category: "Chaussures", price: 61, currency: "USD", image: "https://images.unsplash.com/photo-1600185365483-26d7a4cc7519?auto=format&fit=crop&w=900&q=82", note: "Style décontracté", slug: "article-41", demo: true },
  { id: 42, name: "Bottines Thaïs", category: "Chaussures", price: 83, currency: "USD", image: "https://images.unsplash.com/photo-1608256246200-53e635b5b65f?auto=format&fit=crop&w=900&q=82", note: "Signature urbaine", slug: "article-42", demo: true },
  { id: 43, name: "Sandales Maïa", category: "Chaussures", price: 46, currency: "USD", image: "https://images.unsplash.com/photo-1460353581641-37baddab0fa2?auto=format&fit=crop&w=900&q=82", note: "Esprit vacances", slug: "article-43", demo: true },
  { id: 44, name: "Escarpins Dalia", category: "Chaussures", price: 72, currency: "USD", image: "https://images.unsplash.com/photo-1543163521-1bf539c55dd2?auto=format&fit=crop&w=900&q=82", note: "Finition raffinée", slug: "article-44", demo: true },
  { id: 45, name: "Mocassins Léna", category: "Chaussures", price: 68, currency: "USD", image: "https://images.unsplash.com/photo-1514989940723-e8e51635b782?auto=format&fit=crop&w=900&q=82", note: "Élégance facile", slug: "article-45", demo: true },
  { id: 46, name: "Sneakers Romy", category: "Chaussures", price: 58, currency: "USD", image: "https://images.unsplash.com/photo-1549298916-b41d501d3772?auto=format&fit=crop&w=900&q=82", note: "Énergie quotidienne", slug: "article-46", demo: true },
  { id: 47, name: "Ballerines Alba", category: "Chaussures", price: 43, currency: "USD", image: "https://images.unsplash.com/photo-1560343090-f0409e92791a?auto=format&fit=crop&w=900&q=82", note: "Délicatesse", slug: "article-47", demo: true },
  { id: 48, name: "Talons Naomie", category: "Chaussures", price: 79, currency: "USD", image: "https://images.unsplash.com/photo-1600185365483-26d7a4cc7519?auto=format&fit=crop&w=900&q=82", note: "Soirée élégante", slug: "article-48", demo: true },
  { id: 49, name: "Sandales Ysé", category: "Chaussures", price: 51, currency: "USD", image: "https://images.unsplash.com/photo-1562273138-f46be4ebdf33?auto=format&fit=crop&w=900&q=82", note: "Ligne naturelle", slug: "article-49", demo: true },
  { id: 50, name: "Bottes Salomé", category: "Chaussures", price: 99, currency: "USD", image: "https://images.unsplash.com/photo-1608231387042-66d1773070a5?auto=format&fit=crop&w=900&q=82", note: "Présence affirmée", slug: "article-50", demo: true }
];
