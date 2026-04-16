import { apiGet, apiPatch } from "@/lib/api/client";
import type {
  AdminVerificationDetail,
  AdminVerificationQueueItem,
  AdminVerificationReviewPayload,
} from "@/types/admin-verification";

type AdminVerificationListParams = {
  limit?: number;
  offset?: number;
};

function toQueryString(params: AdminVerificationListParams = {}) {
  const searchParams = new URLSearchParams();

  if (typeof params.limit === "number") {
    searchParams.set("limit", String(params.limit));
  }

  if (typeof params.offset === "number") {
    searchParams.set("offset", String(params.offset));
  }

  const queryString = searchParams.toString();
  return queryString ? `?${queryString}` : "";
}

export function listAdminVerifications(params?: AdminVerificationListParams) {
  return apiGet<AdminVerificationQueueItem[]>(
    `/admin/verifications${toQueryString(params)}`
  );
}

export function getAdminVerification(itemId: string) {
  return apiGet<AdminVerificationDetail>(`/admin/verifications/${itemId}`);
}

export function reviewAdminVerification(
  itemId: string,
  payload: AdminVerificationReviewPayload
) {
  return apiPatch<AdminVerificationDetail>(`/admin/verifications/${itemId}`, payload);
}
