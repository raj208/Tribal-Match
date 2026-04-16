import type { ProfileStatus, VerificationStatus } from "@/types";

export type AdminVerificationUserSummary = {
  id: string;
  email: string;
};

export type AdminVerificationProfileSummary = {
  id: string;
  user_id: string;
  full_name: string;
  profile_status: ProfileStatus;
  verification_status: VerificationStatus;
};

export type AdminVerificationQueueItem = {
  id: string;
  user: AdminVerificationUserSummary;
  profile: AdminVerificationProfileSummary;
  verification_status: VerificationStatus;
  video_url: string;
  duration_seconds: number | null;
  created_at: string;
};

export type AdminVerificationDetail = AdminVerificationQueueItem & {
  upload_status: string;
  moderation_notes: string | null;
  updated_at: string;
};

export type AdminVerificationReviewPayload = {
  status: "approved" | "rejected";
  reason?: string | null;
};
