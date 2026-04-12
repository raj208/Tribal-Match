import { apiGet, apiPatch, apiPost } from "@/lib/api/client";
import type { VerificationState } from "@/types/media";

export type IntroVideoPayload = {
  video_url: string;
  duration_seconds: number;
};

export function getMyVerification() {
  return apiGet<VerificationState>("/verification/me");
}

export function uploadIntroVideo(payload: IntroVideoPayload) {
  return apiPost<VerificationState>("/verification/video", payload);
}

export function reuploadIntroVideo(payload: IntroVideoPayload) {
  return apiPatch<VerificationState>("/verification/video/reupload", payload);
}