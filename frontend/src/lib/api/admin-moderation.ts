import { apiGet, apiPatch } from "@/lib/api/client";
import type {
  AdminReportDetail,
  AdminReportListItem,
  AdminReportStatusUpdatePayload,
} from "@/types/admin-moderation";
import type { ReportStatus } from "@/types";

type AdminReportListParams = {
  status?: ReportStatus | "all";
  limit?: number;
  offset?: number;
};

function toQueryString(params: AdminReportListParams = {}) {
  const searchParams = new URLSearchParams();

  if (params.status && params.status !== "all") {
    searchParams.set("status", params.status);
  }

  if (typeof params.limit === "number") {
    searchParams.set("limit", String(params.limit));
  }

  if (typeof params.offset === "number") {
    searchParams.set("offset", String(params.offset));
  }

  const queryString = searchParams.toString();
  return queryString ? `?${queryString}` : "";
}

export function listAdminReports(params?: AdminReportListParams) {
  return apiGet<AdminReportListItem[]>(`/admin/reports${toQueryString(params)}`);
}

export function getAdminReport(reportId: string) {
  return apiGet<AdminReportDetail>(`/admin/reports/${reportId}`);
}

export function updateAdminReportStatus(
  reportId: string,
  payload: AdminReportStatusUpdatePayload
) {
  return apiPatch<AdminReportDetail>(`/admin/reports/${reportId}`, payload);
}
