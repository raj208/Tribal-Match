import type { ReactNode } from "react";

import { AppSidebar } from "@/components/layout/app-sidebar";

export default function AppLayout({ children }: { children: ReactNode }) {
  return (
    <div className="min-h-screen">
      <div className="container-shell py-6">
        <div className="grid gap-6 md:grid-cols-[260px_minmax(0,1fr)]">
          <AppSidebar />

          <div className="space-y-6">
            <div className="card p-5">
              <p className="text-sm text-stone-500">Authenticated area</p>
              <h1 className="mt-1 text-2xl font-semibold">Tribal Match App</h1>
              <p className="mt-2 text-sm text-stone-600">
                This is the protected app shell. Real auth and route guards will come later.
              </p>
            </div>

            {children}
          </div>
        </div>
      </div>
    </div>
  );
}