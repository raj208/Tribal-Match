import { apiGet, apiPost } from "@/lib/api/client";
import { normalizeMediaContentType, uploadFileToPresignedUrl } from "@/lib/api/presigned-upload";
import type { DirectUploadIntent, VerificationState } from "@/types/media";

export async function uploadIntroVideo(file: File, durationSeconds: number) {
  const contentType = normalizeMediaContentType(file, "video");
  const intent = await apiPost<DirectUploadIntent>("/verification/video/upload-intent", {
    filename: file.name,
    content_type: contentType,
  });

  await uploadFileToPresignedUrl(intent.upload_url, file, contentType);

  return apiPost<VerificationState>("/verification/video/confirm", {
    object_key: intent.object_key,
    content_type: contentType,
    duration_seconds: durationSeconds,
  });
}

export async function reuploadIntroVideo(file: File, durationSeconds: number) {
  return uploadIntroVideo(file, durationSeconds);
}

export function getMyVerification() {
  return apiGet<VerificationState>("/verification/me");
}
