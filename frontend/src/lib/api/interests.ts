import { apiGet, apiPatch, apiPost } from "@/lib/api/client";
import type {
  InterestAction,
  InterestActionPayload,
  InterestActionResponse,
  InterestItem,
} from "@/types/interactions";

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

export function actOnInterest(interestId: string, action: InterestAction) {
  const payload: InterestActionPayload = { action };
  return apiPatch<InterestActionResponse>(`/interests/${interestId}`, payload);
}
