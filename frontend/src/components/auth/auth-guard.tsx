"use client";

import { useEffect, type ReactNode } from "react";
import { usePathname, useRouter } from "next/navigation";

import { useAuth } from "@/hooks/use-auth";

export function AuthGuard({ children }: { children: ReactNode }) {
  const { user, loading } = useAuth();
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    if (!loading && !user) {
      const next = pathname ? `?next=${encodeURIComponent(pathname)}` : "";
      router.replace(`/login${next}`);
    }
  }, [loading, pathname, router, user]);

  if (loading) {
    return (
      <div className="container-shell py-10">
        <div className="card p-6 text-sm text-stone-600">
          Checking session...
        </div>
      </div>
    );
  }

  if (!user) {
    return (
      <div className="container-shell py-10">
        <div className="card p-6 text-sm text-stone-600">
          Redirecting to login...
        </div>
      </div>
    );
  }

  return <>{children}</>;
}