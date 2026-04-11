import type { ReactNode } from "react";

type PageShellProps = {
  title: string;
  description?: string;
  action?: ReactNode;
  children?: ReactNode;
};

export function PageShell({
  title,
  description,
  action,
  children,
}: PageShellProps) {
  return (
    <section className="space-y-5">
      <div className="flex flex-col gap-4 rounded-2xl border border-stone-200 bg-white p-6 shadow-sm md:flex-row md:items-start md:justify-between">
        <div>
          <h2 className="text-2xl font-semibold text-stone-900">{title}</h2>
          {description ? (
            <p className="mt-2 max-w-2xl text-sm text-stone-600">
              {description}
            </p>
          ) : null}
        </div>

        {action ? <div>{action}</div> : null}
      </div>

      {children ? <div className="space-y-5">{children}</div> : null}
    </section>
  );
}