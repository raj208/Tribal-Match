import { apiDelete, apiPost } from "@/lib/api/client";

export function blockProfile(profileId: string) {
  return apiPost<{ message: string }>("/blocks", {
    profile_id: profileId,
  });
}

export function unblockProfile(profileId: string) {
  return apiDelete<{ message: string }>(`/blocks/${profileId}`);
}

export function reportProfile(profileId: string, reasonCode: string, notes: string) {
  return apiPost<{ message: string }>("/reports", {
    profile_id: profileId,
    reason_code: reasonCode,
    notes: notes.trim() ? notes.trim() : null,
  });
}