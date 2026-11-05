import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "SHY BOUTIQUE — La mode, avec intention",
  description: "Découvrez une sélection de vêtements et chaussures pour femme dans l'univers SHY BOUTIQUE.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="fr">
      <body>{children}</body>
    </html>
  );
}