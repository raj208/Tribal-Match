import { PageShell } from "@/components/shared/page-shell";
import { getApiHealth, getApiModules } from "@/lib/api/meta";

export default async function DashboardPage() {
  let health: Awaited<ReturnType<typeof getApiHealth>> | null = null;
  let modules: Awaited<ReturnType<typeof getApiModules>>["modules"] = [];
  let err = "";

  try {
    const [healthRes, modulesRes] = await Promise.all([
      getApiHealth(),
      getApiModules(),
    ]);

    health = healthRes;
    modules = modulesRes.modules;
  } catch (e) {
    err = e instanceof Error ? e.message : "Unable to reach backend";
  }

  return (
    <PageShell
      title="Dashboard"
      description="This page confirms that the frontend app shell is working and that the backend foundation is reachable."
    >
      {err ? (
        <div className="card border-red-200 p-5">
          <p className="text-sm font-medium text-red-700">Backend connection failed</p>
          <p className="mt-2 text-sm text-red-600">{err}</p>
          <p className="mt-3 text-sm text-stone-600">
            Make sure your FastAPI server is running on port 8000.
          </p>
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
                  Registered backend modules
                </h3>
                <p className="mt-1 text-sm text-stone-600">
                  These are the modular monolith domains currently wired into the API router.
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
                  <p className="mt-1 text-sm text-stone-500">
                    {module.base_path}
                  </p>
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