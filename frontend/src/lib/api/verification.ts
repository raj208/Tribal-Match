import { apiGet, apiPatch, apiPost } from "@/lib/api/client";
import type { VerificationState } from "@/types/media";

export async function uploadIntroVideo(file: File, durationSeconds: number) {
  const form = new FormData();
  form.append("file", file);
  form.append("duration_seconds", String(durationSeconds));
  return apiPost<VerificationState>("/verification/video/upload", form);
}

export async function reuploadIntroVideo(file: File, durationSeconds: number) {
  const form = new FormData();
  form.append("file", file);
  form.append("duration_seconds", String(durationSeconds));
  return apiPatch<VerificationState>("/verification/video/reupload", form);
}

export function getMyVerification() {
  return apiGet<VerificationState>("/verification/me");
}