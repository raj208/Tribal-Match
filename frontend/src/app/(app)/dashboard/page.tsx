"use client";

import { useEffect, useState } from "react";

import { PageShell } from "@/components/shared/page-shell";
import { useDashboardSummary } from "@/hooks/use-dashboard-summary";
import { getApiHealth, getApiModules } from "@/lib/api/meta";

type Health = Awaited<ReturnType<typeof getApiHealth>>;
type Modules = Awaited<ReturnType<typeof getApiModules>>["modules"];

export default function DashboardPage() {
  const { summary, loading: summaryLoading, error: summaryError } = useDashboardSummary();
  const [health, setHealth] = useState<Health | null>(null);
  const [modules, setModules] = useState<Modules>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;

    Promise.all([getApiHealth(), getApiModules()])
      .then(([healthRes, modulesRes]) => {
        if (!active) return;
        setHealth(healthRes);
        setModules(modulesRes.modules);
      })
      .catch((err: Error) => {
        if (!active) return;
        setError(err.message || "Unable to reach backend");
      })
      .finally(() => {
        if (!active) return;
        setLoading(false);
      });

    return () => {
      active = false;
    };
  }, []);

  return (
    <PageShell
      title="Dashboard"
      description="This page confirms that your session is active and the backend foundation is reachable."
    >
      {loading ? (
        <div className="card p-6 text-sm text-stone-600">Loading dashboard...</div>
      ) : error ? (
        <div className="card border-red-200 p-5">
          <p className="text-sm font-medium text-red-700">Backend connection failed</p>
          <p className="mt-2 text-sm text-red-600">{error}</p>
        </div>
      ) : (
        <>
          <div className="grid gap-4 md:grid-cols-3">
            <div className="card p-5">
              <p className="text-sm text-stone-500">API status</p>
              <p className="mt-2 text-2xl font-semibold text-stone-900">
                {health?.status ?? "unknown"}
              </p>
            </div>

            <div className="card p-5">
              <p className="text-sm text-stone-500">App name</p>
              <p className="mt-2 text-2xl font-semibold text-stone-900">
                {health?.app_name ?? "-"}
              </p>
            </div>

            <div className="card p-5">
              <p className="text-sm text-stone-500">Environment</p>
              <p className="mt-2 text-2xl font-semibold text-stone-900">
                {health?.env ?? "-"}
              </p>
            </div>
          </div>

          <div className="card p-6">
            <div className="flex items-center justify-between gap-4">
              <div>
                <h3 className="text-lg font-semibold text-stone-900">
                  Dashboard summary payload
                </h3>
                <p className="mt-1 text-sm text-stone-600">
                  Temporary raw response from <code>/dashboard/summary</code> for
                  frontend integration testing.
                </p>
              </div>
            </div>

            {summaryLoading ? (
              <div className="mt-5 rounded-2xl border border-stone-200 bg-stone-50 p-4 text-sm text-stone-600">
                Loading dashboard summary...
              </div>
            ) : summaryError ? (
              <div className="mt-5 rounded-2xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
                {summaryError}
              </div>
            ) : (
              <pre className="mt-5 overflow-x-auto rounded-2xl bg-stone-950 p-4 text-xs text-stone-100">
                {JSON.stringify(summary, null, 2)}
              </pre>
            )}
          </div>

          <div className="card p-6">
            <div className="flex items-center justify-between gap-4">
              <div>
                <h3 className="text-lg font-semibold text-stone-900">
                  Registered backend modules
                </h3>
                <p className="mt-1 text-sm text-stone-600">
                  These are the backend domains currently wired into the API router.
                </p>
              </div>

              <span className="soft-badge bg-green-100 text-green-700">
                {modules.length} modules
              </span>
            </div>

            <div className="mt-5 grid gap-3 md:grid-cols-2 xl:grid-cols-3">
              {modules.map((module) => (
                <div key={module.name} className="rounded-2xl border border-stone-200 p-4">
                  <p className="text-base font-semibold text-stone-900">
                    {module.name}
                  </p>
                  <p className="mt-1 text-sm text-stone-500">{module.base_path}</p>
                  <span className="mt-3 inline-flex rounded-full bg-stone-100 px-3 py-1 text-xs font-medium text-stone-700">
                    {module.status}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </>
      )}
    </PageShell>
  );
}
