"use client";

import { useEffect, useMemo, useState } from "react";
import {
  AlertTriangle,
  CheckCircle2,
  Eye,
  FileWarning,
  RefreshCw,
  ShieldCheck,
} from "lucide-react";

import {
  type AdminReportStatusFilter,
  useAdminReportDetail,
  useAdminReports,
  useUpdateAdminReportStatus,
} from "@/hooks/use-admin-reports";
import {
  formatModerationDate,
  formatModerationLabel,
  getProfileStatusMeta,
  getReportEmptyState,
  getReportStatusMeta,
  isHiddenProfile,
} from "@/lib/admin-moderation-display";
import type { ReportStatus } from "@/types";
import type {
  AdminReportDetail,
  AdminReportListItem,
  AdminReportProfileSummary,
  AdminReportUserSummary,
} from "@/types/admin-moderation";

const STATUS_OPTIONS: Array<AdminReportStatusFilter> = [
  "all",
  "open",
  "reviewed",
  "resolved",
];

const UPDATE_STATUS_OPTIONS: ReportStatus[] = ["open", "reviewed", "resolved"];

function getUserLabel(user: AdminReportUserSummary) {
  return user.email || user.id;
}

function StatusBadge({ status }: { status: ReportStatus }) {
  const meta = getReportStatusMeta(status);

  return <span className={`soft-badge ${meta.badgeClass}`}>{meta.label}</span>;
}

function ProfileStatusBadge({
  profileStatus,
}: {
  profileStatus: AdminReportProfileSummary["profile_status"];
}) {
  const meta = getProfileStatusMeta(profileStatus);

  return <span className={`soft-badge ${meta.badgeClass}`}>{meta.label}</span>;
}

function ErrorPanel({
  title,
  error,
  onRetry,
}: {
  title: string;
  error: string;
  onRetry: () => void;
}) {
  const adminDenied = error.toLowerCase().includes("admin access required");

  return (
    <div className="rounded-2xl border border-red-200 bg-red-50 p-5 text-sm text-red-800">
      <div className="flex items-start gap-3">
        <AlertTriangle className="mt-0.5 h-5 w-5 shrink-0" aria-hidden="true" />
        <div>
          <p className="font-semibold">{adminDenied ? "Admin access required" : title}</p>
          <p className="mt-1">{error}</p>
          <button
            type="button"
            onClick={onRetry}
            className="mt-4 inline-flex items-center gap-2 rounded-xl border border-red-200 bg-white px-4 py-2 font-medium text-red-800 hover:bg-red-100"
          >
            <RefreshCw className="h-4 w-4" aria-hidden="true" />
            Retry
          </button>
        </div>
      </div>
    </div>
  );
}

function QueueSkeleton() {
  return (
    <div className="card overflow-hidden">
      <div className="border-b border-stone-200 p-5">
        <div className="h-5 w-36 rounded bg-stone-200" />
      </div>
      <div className="divide-y divide-stone-200">
        {[0, 1, 2].map((item) => (
          <div key={item} className="animate-pulse p-5">
            <div className="flex items-start justify-between gap-4">
              <div className="space-y-3">
                <div className="h-4 w-32 rounded bg-stone-200" />
                <div className="h-5 w-56 rounded bg-stone-100" />
                <div className="h-4 w-44 rounded bg-stone-100" />
              </div>
              <div className="h-7 w-20 rounded-full bg-stone-200" />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function EmptyStateCard({
  title,
  description,
}: {
  title: string;
  description: string;
}) {
  return (
    <div className="card p-6">
      <div className="flex items-start gap-3">
        <FileWarning className="mt-1 h-5 w-5 text-stone-500" aria-hidden="true" />
        <div>
          <h3 className="text-lg font-semibold text-stone-900">{title}</h3>
          <p className="mt-2 text-sm text-stone-600">{description}</p>
        </div>
      </div>
    </div>
  );
}

function ReportQueueRow({
  report,
  selected,
  onSelect,
}: {
  report: AdminReportListItem;
  selected: boolean;
  onSelect: () => void;
}) {
  return (
    <button
      type="button"
      onClick={onSelect}
      className={`w-full border-l-4 px-5 py-4 text-left transition hover:bg-stone-50 ${
        selected ? "border-stone-900 bg-stone-50" : "border-transparent bg-white"
      }`}
    >
      <div className="flex items-start justify-between gap-4">
        <div className="min-w-0">
          <div className="flex flex-wrap items-center gap-2">
            <p className="text-sm font-semibold text-stone-900">
              {formatModerationLabel(report.reason_code)}
            </p>
            <StatusBadge status={report.status} />
          </div>

          <div className="mt-2 flex flex-wrap items-center gap-2">
            <p className="truncate text-sm text-stone-700">{report.reported_profile.full_name}</p>
            {isHiddenProfile(report.reported_profile.profile_status) ? (
              <ProfileStatusBadge profileStatus={report.reported_profile.profile_status} />
            ) : null}
          </div>
          <p className="mt-1 text-xs text-stone-500">
            Created {formatModerationDate(report.created_at)}
          </p>
        </div>

        <span className="inline-flex h-9 w-9 shrink-0 items-center justify-center rounded-xl border border-stone-200 bg-white text-stone-700">
          <Eye className="h-4 w-4" aria-hidden="true" />
        </span>
      </div>
    </button>
  );
}

function IdentitySummary({
  label,
  email,
  id,
}: {
  label: string;
  email: string;
  id: string;
}) {
  return (
    <div className="rounded-xl border border-stone-200 bg-stone-50 p-4">
      <p className="text-xs uppercase tracking-[0.16em] text-stone-500">{label}</p>
      <p className="mt-2 break-all text-sm font-medium text-stone-900">{email}</p>
      <p className="mt-1 break-all text-xs text-stone-500">{id}</p>
    </div>
  );
}

function DetailPanel({
  report,
  loading,
  error,
  onRetry,
  onUpdated,
}: {
  report: AdminReportDetail | null;
  loading: boolean;
  error: string;
  onRetry: () => void;
  onUpdated: (report: AdminReportDetail) => void;
}) {
  const [draftStatus, setDraftStatus] = useState<ReportStatus>("open");
  const updateStatus = useUpdateAdminReportStatus();

  useEffect(() => {
    if (report) {
      setDraftStatus(report.status);
      updateStatus.reset();
    }
  }, [report?.id, report?.status]);

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!report || draftStatus === report.status) return;

    const updated = await updateStatus.mutate(report.id, draftStatus);
    if (updated) {
      onUpdated(updated);
    }
  }

  if (!report && !loading && !error) {
    return (
      <div className="card p-6">
        <div className="flex items-start gap-3">
          <ShieldCheck className="mt-1 h-5 w-5 text-stone-500" aria-hidden="true" />
          <div>
            <h3 className="text-lg font-semibold text-stone-900">Select a report</h3>
            <p className="mt-2 text-sm text-stone-600">
              Choose a report from the queue to review its details.
            </p>
          </div>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="card p-6">
        <div className="animate-pulse space-y-5">
          <div className="h-5 w-36 rounded bg-stone-200" />
          <div className="h-8 w-64 rounded bg-stone-200" />
          <div className="grid gap-4 sm:grid-cols-2">
            <div className="h-28 rounded-xl bg-stone-100" />
            <div className="h-28 rounded-xl bg-stone-100" />
          </div>
          <div className="h-32 rounded-xl bg-stone-100" />
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="card p-6">
        <ErrorPanel title="Failed to load report detail" error={error} onRetry={onRetry} />
      </div>
    );
  }

  if (!report) {
    return null;
  }

  const statusChanged = draftStatus !== report.status;

  return (
    <div className="card p-6">
      <div className="flex flex-col gap-4 border-b border-stone-200 pb-5 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <p className="text-sm text-stone-500">Report detail</p>
          <h3 className="mt-2 text-xl font-semibold text-stone-900">
            {formatModerationLabel(report.reason_code)}
          </h3>
          <p className="mt-1 text-sm text-stone-600">
            Created {formatModerationDate(report.created_at)}
          </p>
          <p className="mt-1 text-sm text-stone-500">
            Updated {formatModerationDate(report.updated_at)}
          </p>
        </div>
        <StatusBadge status={report.status} />
      </div>

      <div className="mt-5 grid gap-4 sm:grid-cols-2">
        <IdentitySummary
          label="Reporter"
          email={getUserLabel(report.reporter)}
          id={report.reporter.id}
        />
        <IdentitySummary
          label="Reported User"
          email={getUserLabel(report.reported_user)}
          id={report.reported_user.id}
        />
      </div>

      <div className="mt-4 rounded-xl border border-stone-200 bg-stone-50 p-4">
        <p className="text-xs uppercase tracking-[0.16em] text-stone-500">Reported Profile</p>
        <div className="mt-2 flex flex-wrap items-center gap-2">
          <p className="text-sm font-medium text-stone-900">
            {report.reported_profile.full_name}
          </p>
          <ProfileStatusBadge profileStatus={report.reported_profile.profile_status} />
        </div>
        <p className="mt-1 break-all text-xs text-stone-500">
          {report.reported_profile.id}
        </p>
        <p className="mt-2 text-xs text-stone-600">
          {getProfileStatusMeta(report.reported_profile.profile_status).helper}
        </p>
      </div>

      <div className="mt-5">
        <p className="text-sm font-medium text-stone-900">Notes</p>
        <div className="mt-2 rounded-xl border border-stone-200 bg-white p-4 text-sm text-stone-700">
          {report.notes?.trim() ? report.notes : "No notes were submitted with this report."}
        </div>
      </div>

      <form onSubmit={handleSubmit} className="mt-5 rounded-xl border border-stone-200 p-4">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-end">
          <label className="block flex-1 text-sm">
            <span className="mb-2 block font-medium text-stone-700">Status</span>
            <select
              value={draftStatus}
              onChange={(event) => setDraftStatus(event.target.value as ReportStatus)}
              disabled={updateStatus.loading}
              className="w-full rounded-xl border border-stone-300 bg-white px-3 py-2 outline-none focus:border-stone-500 disabled:bg-stone-100"
            >
              {UPDATE_STATUS_OPTIONS.map((status) => (
                <option key={status} value={status}>
                  {getReportStatusMeta(status).label}
                </option>
              ))}
            </select>
          </label>

          <button
            type="submit"
            disabled={!statusChanged || updateStatus.loading}
            className="inline-flex items-center justify-center gap-2 rounded-xl bg-stone-900 px-4 py-2 text-sm font-medium text-white hover:bg-stone-800 disabled:cursor-not-allowed disabled:opacity-60"
          >
            <CheckCircle2 className="h-4 w-4" aria-hidden="true" />
            {updateStatus.loading ? "Updating..." : "Update status"}
          </button>
        </div>

        {updateStatus.error ? (
          <div className="mt-4 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
            {updateStatus.error}
          </div>
        ) : null}
      </form>
    </div>
  );
}

export function AdminReportsQueue({
  onQueueChanged,
}: {
  onQueueChanged?: () => void;
}) {
  const [statusFilter, setStatusFilter] = useState<AdminReportStatusFilter>("open");
  const reportsQuery = useAdminReports(statusFilter);
  const [selectedReportId, setSelectedReportId] = useState<string | null>(null);
  const detailQuery = useAdminReportDetail(selectedReportId);

  useEffect(() => {
    if (!selectedReportId && reportsQuery.reports.length > 0) {
      setSelectedReportId(reportsQuery.reports[0].id);
    }
  }, [reportsQuery.reports, selectedReportId]);

  function handleUpdated(report: AdminReportDetail) {
    if (statusFilter !== "all" && report.status !== statusFilter) {
      setSelectedReportId(null);
      reportsQuery.reload();
      onQueueChanged?.();
      return;
    }

    reportsQuery.replaceReport(report);
    detailQuery.replaceReport(report);
    onQueueChanged?.();
  }

  const listBlockedByAdminAccess =
    reportsQuery.error.toLowerCase().includes("admin access required");
  const detailPending = selectedReportId !== null && detailQuery.report === null && !detailQuery.error;
  const emptyState = useMemo(() => getReportEmptyState(statusFilter), [statusFilter]);

  return (
    <div className="space-y-5">
      <div className="flex flex-col gap-3 rounded-2xl border border-stone-200 bg-white p-4 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex flex-wrap gap-2">
          {STATUS_OPTIONS.map((status) => (
            <button
              key={status}
              type="button"
              onClick={() => {
                setStatusFilter(status);
                setSelectedReportId(null);
              }}
              className={`rounded-xl px-4 py-2 text-sm font-medium ${
                statusFilter === status
                  ? "bg-stone-900 text-white"
                  : "border border-stone-300 bg-white text-stone-800 hover:bg-stone-50"
              }`}
            >
              {status === "all" ? "All" : getReportStatusMeta(status).label}
            </button>
          ))}
        </div>

        <button
          type="button"
          onClick={() => {
            reportsQuery.reload();
            detailQuery.reload();
          }}
          disabled={reportsQuery.refreshing}
          className="inline-flex items-center justify-center gap-2 rounded-xl border border-stone-300 bg-white px-4 py-2 text-sm font-medium text-stone-800 hover:bg-stone-50 disabled:cursor-not-allowed disabled:opacity-60"
        >
          <RefreshCw className="h-4 w-4" aria-hidden="true" />
          {reportsQuery.refreshing ? "Refreshing..." : "Refresh"}
        </button>
      </div>

      {listBlockedByAdminAccess ? (
        <ErrorPanel
          title="Failed to load reports"
          error={reportsQuery.error}
          onRetry={reportsQuery.reload}
        />
      ) : (
        <div className="grid gap-5 xl:grid-cols-[minmax(0,0.95fr)_minmax(420px,1.05fr)]">
          <div>
            {reportsQuery.loading ? (
              <QueueSkeleton />
            ) : reportsQuery.error ? (
              <ErrorPanel
                title="Failed to load reports"
                error={reportsQuery.error}
                onRetry={reportsQuery.reload}
              />
            ) : reportsQuery.reports.length === 0 ? (
              <EmptyStateCard title={emptyState.title} description={emptyState.description} />
            ) : (
              <div className="card overflow-hidden">
                <div className="flex items-center justify-between gap-3 border-b border-stone-200 p-5">
                  <div>
                    <p className="text-sm text-stone-500">Queue</p>
                    <h3 className="mt-1 text-lg font-semibold text-stone-900">
                      {reportsQuery.reports.length} report
                      {reportsQuery.reports.length === 1 ? "" : "s"}
                    </h3>
                  </div>
                  {reportsQuery.refreshing ? (
                    <span className="text-sm text-stone-500">Refreshing...</span>
                  ) : null}
                </div>

                <div className="divide-y divide-stone-200">
                  {reportsQuery.reports.map((report) => (
                    <ReportQueueRow
                      key={report.id}
                      report={report}
                      selected={report.id === selectedReportId}
                      onSelect={() => setSelectedReportId(report.id)}
                    />
                  ))}
                </div>
              </div>
            )}
          </div>

          <DetailPanel
            report={detailQuery.report}
            loading={detailQuery.loading || detailPending}
            error={detailQuery.error}
            onRetry={detailQuery.reload}
            onUpdated={handleUpdated}
          />
        </div>
      )}
    </div>
  );
}
