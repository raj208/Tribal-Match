import type { ReactNode } from "react";

import { PublicHeader } from "@/components/layout/public-header";

export default function PublicLayout({ children }: { children: ReactNode }) {
  return (
    <div className="min-h-screen">
      <PublicHeader />
      <div className="container-shell py-10">{children}</div>
      <footer className="border-t border-stone-200 bg-white">
        <div className="container-shell py-6 text-sm text-stone-500">
          Tribal Match MVP foundation
        </div>
      </footer>
    </div>
  );
}