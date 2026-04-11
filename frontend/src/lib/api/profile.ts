import { apiGet, apiPatch, apiPost } from "@/lib/api/client";
import type { Profile, ProfilePayload } from "@/types/profile";

export function getMyProfile() {
  return apiGet<Profile>("/profile/me");
}

export function createProfile(payload: ProfilePayload) {
  return apiPost<Profile>("/profile", payload);
}

export function updateMyProfile(payload: Partial<ProfilePayload>) {
  return apiPatch<Profile>("/profile/me", payload);
}