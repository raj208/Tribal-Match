import { apiDelete, apiGet, apiPost } from "@/lib/api/client";
import type { ShortlistItem } from "@/types/interactions";

export function addToShortlist(profileId: string) {
  return apiPost<ShortlistItem>("/shortlist", {
    profile_id: profileId,
  });
}

export function listMyShortlist() {
  return apiGet<ShortlistItem[]>("/shortlist");
}

export function deleteShortlistItem(shortlistId: string) {
  return apiDelete<void>(`/shortlist/${shortlistId}`);
}