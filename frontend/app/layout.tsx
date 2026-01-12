import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Custom RDBMS Inventory",
  description: "Inventory management system powered by custom RDBMS",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="antialiased">
        {children}
      </body>
    </html>
  );
}