import { apiGet, apiPost } from "@/lib/api/client";
import type { InterestItem } from "@/types/interactions";

export function sendInterest(receiverProfileId: string) {
  return apiPost<InterestItem>("/interests", {
    receiver_profile_id: receiverProfileId,
  });
}

export function listSentInterests() {
  return apiGet<InterestItem[]>("/interests/sent");
}

export function listReceivedInterests() {
  return apiGet<InterestItem[]>("/interests/received");
}