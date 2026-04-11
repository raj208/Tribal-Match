import type { ReactNode } from "react";

import { AuthGuard } from "@/components/auth/auth-guard";
import { AppSidebar } from "@/components/layout/app-sidebar";

export default function AppLayout({ children }: { children: ReactNode }) {
  return (
    <AuthGuard>
      <div className="min-h-screen">
        <div className="container-shell py-6">
          <div className="grid gap-6 md:grid-cols-[260px_minmax(0,1fr)]">
            <AppSidebar />

            <div className="space-y-6">
              <div className="card p-5">
                <p className="text-sm text-stone-500">Authenticated area</p>
                <h1 className="mt-1 text-2xl font-semibold">Tribal Match App</h1>
                <p className="mt-2 text-sm text-stone-600">
                  You are signed in. Protected pages now require an active session.
                </p>
              </div>

              {children}
            </div>
          </div>
        </div>
      </div>
    </AuthGuard>
  );
}