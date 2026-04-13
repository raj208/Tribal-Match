import type { ProfileStatus, VerificationStatus } from "./index";

export interface DashboardSummary {
  profile_exists: boolean;
  profile_status: ProfileStatus | null;
  completion_percentage: number;
  verification_status: VerificationStatus | null;
  photo_count: number;
  has_intro_video: boolean;
  shortlist_count: number;
  sent_interests_count: number;
  received_interests_count: number;
}
