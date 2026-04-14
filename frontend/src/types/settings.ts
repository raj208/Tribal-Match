import type { ProfileStatus, VerificationStatus } from "@/types";

export type ProfileVisibility = "public" | "private";

export interface SettingsSummary {
  email: string;
  profile_exists: boolean;
  profile_visibility: ProfileVisibility | null;
  profile_status: ProfileStatus | null;
  verification_status: VerificationStatus | null;
  completion_percentage: number;
}

export interface SettingsUpdatePayload {
  profile_visibility?: ProfileVisibility | null;
}

export interface SettingsLifecycleResponse {
  success: boolean;
  profile_status: ProfileStatus;
  message: string;
}
