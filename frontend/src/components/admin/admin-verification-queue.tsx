"use client";

import { useEffect, useState } from "react";
import {
  AlertTriangle,
  CheckCircle2,
  ExternalLink,
  Eye,
  ShieldAlert,
  RefreshCw,
  ShieldCheck,
  XCircle,
} from "lucide-react";

import {
  useAdminVerificationDetail,
  useAdminVerificationQueue,
  useReviewAdminVerification,
} from "@/hooks/use-admin-verifications";
import {
  formatModerationDate,
  formatModerationLabel,
  getProfileStatusMeta,
  getVerificationStatusMeta,
  isHiddenProfile,
} from "@/lib/admin-moderation-display";
import type { VerificationStatus } from "@/types";
import type {
  AdminVerificationDetail,
  AdminVerificationProfileSummary,
  AdminVerificationQueueItem,
  AdminVerificationUserSummary,
} from "@/types/admin-verification";

function getUserLabel(user: AdminVerificationUserSummary) {
  return user.email || user.id;
}

function VerificationStatusBadge({
  status,
}: {
  status: VerificationStatus;
}) {
  const meta = getVerificationStatusMeta(status);
  return <span className={`soft-badge ${meta.badgeClass}`}>{meta.label}</span>;
}

function ProfileStatusBadge({
  profileStatus,
}: {
  profileStatus: AdminVerificationProfileSummary["profile_status"];
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
        <div className="h-5 w-44 rounded bg-stone-200" />
      </div>
      <div className="divide-y divide-stone-200">
        {[0, 1, 2].map((item) => (
          <div key={item} className="animate-pulse p-5">
            <div className="flex items-start justify-between gap-4">
              <div className="space-y-3">
                <div className="h-4 w-36 rounded bg-stone-200" />
                <div className="h-5 w-52 rounded bg-stone-100" />
                <div className="h-4 w-44 rounded bg-stone-100" />
              </div>
              <div className="h-7 w-24 rounded-full bg-stone-200" />
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
        <ShieldAlert className="mt-1 h-5 w-5 text-stone-500" aria-hidden="true" />
        <div>
          <h3 className="text-lg font-semibold text-stone-900">{title}</h3>
          <p className="mt-2 text-sm text-stone-600">{description}</p>
        </div>
      </div>
    </div>
  );
}

function VerificationQueueRow({
  item,
  selected,
  onSelect,
}: {
  item: AdminVerificationQueueItem;
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
              {item.profile.full_name}
            </p>
            <VerificationStatusBadge status={item.verification_status} />
            {isHiddenProfile(item.profile.profile_status) ? (
              <ProfileStatusBadge profileStatus={item.profile.profile_status} />
            ) : null}
          </div>
          <p className="mt-2 truncate text-sm text-stone-700">
            {item.user.email}
          </p>
          <p className="mt-1 text-xs text-stone-500">
            Uploaded {formatModerationDate(item.created_at)}
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
  primary,
  secondary,
}: {
  label: string;
  primary: string;
  secondary: string;
}) {
  return (
    <div className="rounded-xl border border-stone-200 bg-stone-50 p-4">
      <p className="text-xs uppercase tracking-[0.16em] text-stone-500">{label}</p>
      <p className="mt-2 break-all text-sm font-medium text-stone-900">{primary}</p>
      <p className="mt-1 break-all text-xs text-stone-500">{secondary}</p>
    </div>
  );
}

function VerificationDetailPanel({
  item,
  loading,
  error,
  onRetry,
  onReviewed,
}: {
  item: AdminVerificationDetail | null;
  loading: boolean;
  error: string;
  onRetry: () => void;
  onReviewed: () => void;
}) {
  const [rejectReason, setRejectReason] = useState("");
  const reviewMutation = useReviewAdminVerification();

  useEffect(() => {
    setRejectReason(item?.moderation_notes ?? "");
    reviewMutation.reset();
  }, [item?.id]);

  async function handleApprove() {
    if (!item) return;
    const updated = await reviewMutation.mutate(item.id, "approved");
    if (updated) {
      onReviewed();
    }
  }

  async function handleReject() {
    if (!item) return;
    const updated = await reviewMutation.mutate(item.id, "rejected", rejectReason);
    if (updated) {
      onReviewed();
    }
  }

  if (!item && !loading && !error) {
    return (
      <div className="card p-6">
        <div className="flex items-start gap-3">
          <ShieldCheck className="mt-1 h-5 w-5 text-stone-500" aria-hidden="true" />
          <div>
            <h3 className="text-lg font-semibold text-stone-900">
              Select a verification item
            </h3>
            <p className="mt-2 text-sm text-stone-600">
              Choose a pending verification to review the uploaded intro video.
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
          <div className="h-5 w-44 rounded bg-stone-200" />
          <div className="h-8 w-72 rounded bg-stone-200" />
          <div className="h-56 rounded-2xl bg-stone-100" />
          <div className="grid gap-4 sm:grid-cols-2">
            <div className="h-28 rounded-xl bg-stone-100" />
            <div className="h-28 rounded-xl bg-stone-100" />
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="card p-6">
        <ErrorPanel
          title="Failed to load verification detail"
          error={error}
          onRetry={onRetry}
        />
      </div>
    );
  }

  if (!item) {
    return null;
  }

  return (
    <div className="card p-6">
      <div className="flex flex-col gap-4 border-b border-stone-200 pb-5 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <p className="text-sm text-stone-500">Verification detail</p>
          <h3 className="mt-2 text-xl font-semibold text-stone-900">
            {item.profile.full_name}
          </h3>
          <p className="mt-1 text-sm text-stone-600">
            Uploaded {formatModerationDate(item.created_at)}
          </p>
          <p className="mt-1 text-sm text-stone-500">
            Updated {formatModerationDate(item.updated_at)}
          </p>
        </div>
        <VerificationStatusBadge status={item.verification_status} />
      </div>

      <div className="mt-5 overflow-hidden rounded-2xl border border-stone-200 bg-stone-950">
        <video
          key={item.video_url}
          controls
          preload="metadata"
          className="h-[320px] w-full bg-stone-950 object-contain"
          src={item.video_url}
        >
          Your browser does not support embedded video playback.
        </video>
      </div>

      <div className="mt-4 flex flex-wrap items-center gap-3">
        <a
          href={item.video_url}
          target="_blank"
          rel="noreferrer"
          className="inline-flex items-center gap-2 rounded-xl border border-stone-300 bg-white px-4 py-2 text-sm font-medium text-stone-800 hover:bg-stone-50"
        >
          <ExternalLink className="h-4 w-4" aria-hidden="true" />
          Open Video
        </a>
        <span className="soft-badge bg-stone-100 text-stone-700">
          Duration {item.duration_seconds ? `${item.duration_seconds}s` : "Unknown"}
        </span>
        <span className="soft-badge bg-stone-100 text-stone-700">
          Upload {formatModerationLabel(item.upload_status)}
        </span>
      </div>

      <div className="mt-5 grid gap-4 sm:grid-cols-2">
        <IdentitySummary
          label="User"
          primary={getUserLabel(item.user)}
          secondary={item.user.id}
        />
        <IdentitySummary
          label="Profile"
          primary={item.profile.full_name}
          secondary={item.profile.id}
        />
      </div>

      <div className="mt-4 rounded-xl border border-stone-200 bg-stone-50 p-4">
        <div className="flex flex-wrap items-center gap-2">
          <VerificationStatusBadge status={item.profile.verification_status} />
          <ProfileStatusBadge profileStatus={item.profile.profile_status} />
        </div>
        <p className="mt-2 text-sm text-stone-600">
          {getProfileStatusMeta(item.profile.profile_status).helper}
        </p>
        <p className="mt-1 text-sm text-stone-500">
          Profile verification state mirrors the intro video review decision.
        </p>
      </div>

      <div className="mt-5 rounded-xl border border-stone-200 p-4">
        <label className="block text-sm">
          <span className="mb-2 block font-medium text-stone-700">
            Rejection note
          </span>
          <textarea
            value={rejectReason}
            onChange={(event) => setRejectReason(event.target.value)}
            rows={4}
            disabled={reviewMutation.loading}
            className="w-full resize-none rounded-xl border border-stone-300 bg-white px-3 py-2 outline-none focus:border-stone-500 disabled:bg-stone-100"
            placeholder="Explain why this video should be rejected"
          />
        </label>

        {reviewMutation.error ? (
          <div className="mt-4 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
            {reviewMutation.error}
          </div>
        ) : null}

        <div className="mt-4 flex flex-wrap gap-3">
          <button
            type="button"
            onClick={handleApprove}
            disabled={reviewMutation.loading}
            className="inline-flex items-center gap-2 rounded-xl bg-green-700 px-4 py-2 text-sm font-medium text-white hover:bg-green-800 disabled:cursor-not-allowed disabled:opacity-60"
          >
            <CheckCircle2 className="h-4 w-4" aria-hidden="true" />
            {reviewMutation.loading ? "Saving..." : "Approve"}
          </button>

          <button
            type="button"
            onClick={handleReject}
            disabled={reviewMutation.loading}
            className="inline-flex items-center gap-2 rounded-xl border border-red-300 bg-white px-4 py-2 text-sm font-medium text-red-800 hover:bg-red-50 disabled:cursor-not-allowed disabled:opacity-60"
          >
            <XCircle className="h-4 w-4" aria-hidden="true" />
            {reviewMutation.loading ? "Saving..." : "Reject"}
          </button>
        </div>
      </div>
    </div>
  );
}

export function AdminVerificationQueue({
  onQueueChanged,
}: {
  onQueueChanged?: () => void;
}) {
  const queueQuery = useAdminVerificationQueue();
  const [selectedItemId, setSelectedItemId] = useState<string | null>(null);
  const detailQuery = useAdminVerificationDetail(selectedItemId);

  useEffect(() => {
    if (!selectedItemId && queueQuery.items.length > 0) {
      setSelectedItemId(queueQuery.items[0].id);
    }
  }, [queueQuery.items, selectedItemId]);

  const queueBlockedByAdminAccess =
    queueQuery.error.toLowerCase().includes("admin access required");
  const detailPending =
    selectedItemId !== null && detailQuery.item === null && !detailQuery.error;

  return (
    <div className="space-y-5">
      <div className="flex flex-col gap-3 rounded-2xl border border-stone-200 bg-white p-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <p className="text-sm text-stone-500">Pending verification</p>
          <h3 className="mt-1 text-lg font-semibold text-stone-900">
            {queueQuery.items.length} item{queueQuery.items.length === 1 ? "" : "s"}
          </h3>
        </div>

        <button
          type="button"
          onClick={() => {
            queueQuery.reload();
            detailQuery.reload();
          }}
          disabled={queueQuery.refreshing}
          className="inline-flex items-center justify-center gap-2 rounded-xl border border-stone-300 bg-white px-4 py-2 text-sm font-medium text-stone-800 hover:bg-stone-50 disabled:cursor-not-allowed disabled:opacity-60"
        >
          <RefreshCw className="h-4 w-4" aria-hidden="true" />
          {queueQuery.refreshing ? "Refreshing..." : "Refresh"}
        </button>
      </div>

      {queueBlockedByAdminAccess ? (
        <ErrorPanel
          title="Failed to load verification queue"
          error={queueQuery.error}
          onRetry={queueQuery.reload}
        />
      ) : (
        <div className="grid gap-5 xl:grid-cols-[minmax(0,0.95fr)_minmax(420px,1.05fr)]">
          <div>
            {queueQuery.loading ? (
              <QueueSkeleton />
            ) : queueQuery.error ? (
              <ErrorPanel
                title="Failed to load verification queue"
                error={queueQuery.error}
                onRetry={queueQuery.reload}
              />
            ) : queueQuery.items.length === 0 ? (
              <EmptyStateCard
                title="No pending verification items"
                description="Uploaded or under-review intro videos will appear here when they need moderation."
              />
            ) : (
              <div className="card overflow-hidden">
                <div className="flex items-center justify-between gap-3 border-b border-stone-200 p-5">
                  <div>
                    <p className="text-sm text-stone-500">Queue</p>
                    <h3 className="mt-1 text-lg font-semibold text-stone-900">
                      Verification review
                    </h3>
                  </div>
                  {queueQuery.refreshing ? (
                    <span className="text-sm text-stone-500">Refreshing...</span>
                  ) : null}
                </div>

                <div className="divide-y divide-stone-200">
                  {queueQuery.items.map((item) => (
                    <VerificationQueueRow
                      key={item.id}
                      item={item}
                      selected={item.id === selectedItemId}
                      onSelect={() => setSelectedItemId(item.id)}
                    />
                  ))}
                </div>
              </div>
            )}
          </div>

          <VerificationDetailPanel
            item={detailQuery.item}
            loading={detailQuery.loading || detailPending}
            error={detailQuery.error}
            onRetry={detailQuery.reload}
            onReviewed={() => {
              setSelectedItemId(null);
              queueQuery.reload();
              onQueueChanged?.();
            }}
          />
        </div>
      )}
    </div>
  );
}
