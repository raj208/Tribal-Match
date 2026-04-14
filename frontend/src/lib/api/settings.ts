import { apiDelete, apiGet, apiPatch, apiPost } from "@/lib/api/client";
import type {
  SettingsLifecycleResponse,
  SettingsSummary,
  SettingsUpdatePayload,
} from "@/types/settings";

export function getMySettings() {
  return apiGet<SettingsSummary>("/settings/me");
}

export function updateMySettings(payload: SettingsUpdatePayload) {
  return apiPatch<SettingsSummary>("/settings/me", payload);
}

export function deactivateMyProfile() {
  return apiPost<SettingsLifecycleResponse>("/settings/deactivate", {});
}

export function deleteMyProfile() {
  return apiDelete<SettingsLifecycleResponse>("/settings/me");
}
