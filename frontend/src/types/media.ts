export type Photo = {
  id: string;
  user_id: string;
  profile_id: string;
  photo_url: string;
  sort_order: number;
  is_primary: boolean;
  moderation_status: string;
  created_at: string;
};

export type IntroVideo = {
  id: string;
  user_id: string;
  profile_id: string;
  video_url: string;
  duration_seconds: number | null;
  upload_status: string;
  verification_status: string;
  moderation_notes: string | null;
  created_at: string;
  updated_at: string;
};

export type VerificationState = {
  profile_verification_status: string;
  intro_video: IntroVideo | null;
};