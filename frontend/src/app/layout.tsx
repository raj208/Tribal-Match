import "./globals.css";
import type { Metadata } from "next";
import type { ReactNode } from "react";

import { AuthProvider } from "@/components/providers/auth-provider";

export const metadata: Metadata = {
  title: "Tribal Match",
  description: "Trust-first community matchmaking platform",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-stone-50 text-stone-900 antialiased">
        <AuthProvider>{children}</AuthProvider>
      </body>
    </html>
  );
}