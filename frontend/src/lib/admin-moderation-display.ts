import type { ProfileStatus, ReportStatus, VerificationStatus } from "../types";

export type ModerationBadgeMeta = {
  label: string;
  badgeClass: string;
  helper: string;
};

type ReportEmptyState = {
  title: string;
  description: string;
};

const DEFAULT_BADGE_CLASS = "bg-stone-100 text-stone-700 ring-1 ring-inset ring-stone-200";

const REPORT_STATUS_META: Record<ReportStatus, ModerationBadgeMeta> = {
  open: {
    label: "Open",
    badgeClass: "bg-amber-50 text-amber-800 ring-1 ring-inset ring-amber-200",
    helper: "This report still needs moderator review.",
  },
  reviewed: {
    label: "Reviewed",
    badgeClass: "bg-sky-50 text-sky-800 ring-1 ring-inset ring-sky-200",
    helper: "A moderator has reviewed this report, but it is not fully closed yet.",
  },
  resolved: {
    label: "Resolved",
    badgeClass: "bg-green-50 text-green-800 ring-1 ring-inset ring-green-200",
    helper: "This report is closed for now.",
  },
};

const PROFILE_STATUS_META: Record<ProfileStatus, ModerationBadgeMeta> = {
  draft: {
    label: "Draft",
    badgeClass: "bg-amber-50 text-amber-800 ring-1 ring-inset ring-amber-200",
    helper: "Draft profiles are not visible in normal browse or public profile detail views.",
  },
  published: {
    label: "Published",
    badgeClass: "bg-green-50 text-green-800 ring-1 ring-inset ring-green-200",
    helper: "Published profiles are visible in normal browse and profile detail flows.",
  },
  hidden: {
    label: "Hidden",
    badgeClass: "bg-stone-900 text-white ring-1 ring-inset ring-stone-900",
    helper: "Hidden profiles are removed from browse and public profile detail views.",
  },
  deactivated: {
    label: "Deactivated",
    badgeClass: "bg-orange-50 text-orange-800 ring-1 ring-inset ring-orange-200",
    helper: "Deactivated profiles remain stored, but stay unavailable in normal discovery.",
  },
  deleted: {
    label: "Deleted",
    badgeClass: "bg-red-50 text-red-800 ring-1 ring-inset ring-red-200",
    helper: "Deleted is a soft-delete state and remains unavailable in the app.",
  },
};

const VERIFICATION_STATUS_META: Record<VerificationStatus, ModerationBadgeMeta> = {
  not_started: {
    label: "Not Started",
    badgeClass: DEFAULT_BADGE_CLASS,
    helper: "Verification has not started yet.",
  },
  uploaded: {
    label: "Uploaded",
    badgeClass: "bg-amber-50 text-amber-800 ring-1 ring-inset ring-amber-200",
    helper: "The intro video is uploaded and waiting for the next moderation step.",
  },
  under_review: {
    label: "Under Review",
    badgeClass: "bg-sky-50 text-sky-800 ring-1 ring-inset ring-sky-200",
    helper: "The intro video is currently being reviewed by an admin.",
  },
  approved: {
    label: "Approved",
    badgeClass: "bg-green-50 text-green-800 ring-1 ring-inset ring-green-200",
    helper: "The intro video has passed review.",
  },
  rejected: {
    label: "Rejected",
    badgeClass: "bg-red-50 text-red-800 ring-1 ring-inset ring-red-200",
    helper: "The intro video needs changes before it can be approved.",
  },
};

export function formatModerationLabel(value: string) {
  return value.replace(/_/g, " ").replace(/\b\w/g, (char) => char.toUpperCase());
}

export function formatModerationDate(value: string) {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return "Date unavailable";
  }

  return new Intl.DateTimeFormat(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(date);
}

export function getReportStatusMeta(status: ReportStatus): ModerationBadgeMeta {
  return REPORT_STATUS_META[status];
}

export function getProfileStatusMeta(status: ProfileStatus): ModerationBadgeMeta {
  return PROFILE_STATUS_META[status];
}

export function getVerificationStatusMeta(status: VerificationStatus): ModerationBadgeMeta {
  return VERIFICATION_STATUS_META[status];
}

export function isHiddenProfile(status: ProfileStatus): boolean {
  return status === "hidden";
}

export function getReportEmptyState(status: ReportStatus | "all"): ReportEmptyState {
  if (status === "open") {
    return {
      title: "No open reports",
      description: "New reports that still need moderator attention will appear here.",
    };
  }

  if (status === "reviewed") {
    return {
      title: "No reviewed reports",
      description: "Reports that have been reviewed but not resolved will appear here.",
    };
  }

  if (status === "resolved") {
    return {
      title: "No resolved reports",
      description: "Resolved reports will appear here for reference.",
    };
  }

  return {
    title: "No reports found",
    description: "Reports will appear here as members submit them.",
  };
}
