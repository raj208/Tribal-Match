"use client";

import type { ReactNode } from "react";
import { useMemo, useState } from "react";
import { AlertTriangle, FileWarning, RefreshCw, Video } from "lucide-react";

import { AdminReportsQueue } from "@/components/admin/admin-reports-queue";
import { AdminVerificationQueue } from "@/components/admin/admin-verification-queue";
import { useAdminReports } from "@/hooks/use-admin-reports";
import { useAdminVerificationQueue } from "@/hooks/use-admin-verifications";

type TabKey = "reports" | "verification";

function SummaryCard({
  title,
  value,
  helper,
  active,
  onClick,
  icon,
}: {
  title: string;
  value: string;
  helper: string;
  active: boolean;
  onClick: () => void;
  icon: ReactNode;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`card w-full p-5 text-left transition ${
        active ? "border-stone-900 ring-1 ring-stone-900" : "hover:border-stone-300"
      }`}
    >
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="text-sm text-stone-500">{title}</p>
          <p className="mt-3 text-3xl font-semibold text-stone-900">{value}</p>
          <p className="mt-2 text-sm text-stone-600">{helper}</p>
        </div>
        <span className="inline-flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-stone-100 text-stone-700">
          {icon}
        </span>
      </div>
    </button>
  );
}

export function AdminModerationDashboard() {
  const [tab, setTab] = useState<TabKey>("reports");
  const openReports = useAdminReports("open");
  const pendingVerification = useAdminVerificationQueue();

  const accessError = useMemo(() => {
    const errors = [openReports.error, pendingVerification.error].filter(Boolean);
    return errors.find((error) => error.toLowerCase().includes("admin access required")) ?? "";
  }, [openReports.error, pendingVerification.error]);

  const openReportsCount = openReports.error ? "-" : String(openReports.reports.length);
  const pendingVerificationCount = pendingVerification.error
    ? "-"
    : String(pendingVerification.items.length);
  const openReportsHelper = openReports.loading
    ? "Fetching current report volume."
    : openReports.error
    ? "Unable to load the current report count."
    : openReports.reports.length === 0
    ? "No open reports need moderator attention right now."
    : "Reports that still need moderator attention.";
  const pendingVerificationHelper = pendingVerification.loading
    ? "Fetching current verification volume."
    : pendingVerification.error
    ? "Unable to load the current verification count."
    : pendingVerification.items.length === 0
    ? "No intro videos are waiting for review right now."
    : "Intro videos waiting for approval or rejection.";

  return (
    <div className="space-y-5">
      {accessError ? (
        <div className="rounded-2xl border border-red-200 bg-red-50 p-5 text-sm text-red-800">
          <div className="flex items-start gap-3">
            <AlertTriangle className="mt-0.5 h-5 w-5 shrink-0" aria-hidden="true" />
            <div>
              <p className="font-semibold">Admin access required</p>
              <p className="mt-1">{accessError}</p>
            </div>
          </div>
        </div>
      ) : null}

      <div className="grid gap-5 lg:grid-cols-2">
        <SummaryCard
          title="Open Reports"
          value={openReports.loading ? "..." : openReportsCount}
          helper={openReportsHelper}
          active={tab === "reports"}
          onClick={() => setTab("reports")}
          icon={<FileWarning className="h-5 w-5" aria-hidden="true" />}
        />
        <SummaryCard
          title="Pending Verification"
          value={pendingVerification.loading ? "..." : pendingVerificationCount}
          helper={pendingVerificationHelper}
          active={tab === "verification"}
          onClick={() => setTab("verification")}
          icon={<Video className="h-5 w-5" aria-hidden="true" />}
        />
      </div>

      <div className="flex flex-col gap-3 rounded-2xl border border-stone-200 bg-white p-4 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex flex-wrap gap-2">
          <button
            type="button"
            onClick={() => setTab("reports")}
            className={`rounded-xl px-4 py-2 text-sm font-medium ${
              tab === "reports"
                ? "bg-stone-900 text-white"
                : "border border-stone-300 bg-white text-stone-800 hover:bg-stone-50"
            }`}
          >
            Reports
          </button>
          <button
            type="button"
            onClick={() => setTab("verification")}
            className={`rounded-xl px-4 py-2 text-sm font-medium ${
              tab === "verification"
                ? "bg-stone-900 text-white"
                : "border border-stone-300 bg-white text-stone-800 hover:bg-stone-50"
            }`}
          >
            Pending Verification
          </button>
        </div>

        <button
          type="button"
          onClick={() => {
            openReports.reload();
            pendingVerification.reload();
          }}
          disabled={openReports.refreshing || pendingVerification.refreshing}
          className="inline-flex items-center justify-center gap-2 rounded-xl border border-stone-300 bg-white px-4 py-2 text-sm font-medium text-stone-800 hover:bg-stone-50 disabled:cursor-not-allowed disabled:opacity-60"
        >
          <RefreshCw className="h-4 w-4" aria-hidden="true" />
          Refresh overview
        </button>
      </div>

      {tab === "reports" ? (
        <AdminReportsQueue onQueueChanged={openReports.reload} />
      ) : (
        <AdminVerificationQueue onQueueChanged={pendingVerification.reload} />
      )}
    </div>
  );
}
