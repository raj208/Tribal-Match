import { apiDelete, apiGet, apiPatch, apiPost } from "@/lib/api/client";
import { normalizeMediaContentType, uploadFileToPresignedUrl } from "@/lib/api/presigned-upload";
import type { DirectUploadIntent, Photo } from "@/types/media";

export async function uploadPhoto(file: File, sortOrder: number, isPrimary: boolean) {
  const contentType = normalizeMediaContentType(file, "photo");
  const intent = await apiPost<DirectUploadIntent>("/media/photos/upload-intent", {
    filename: file.name,
    content_type: contentType,
  });

  await uploadFileToPresignedUrl(intent.upload_url, file, contentType);

  return apiPost<Photo>("/media/photos/confirm", {
    object_key: intent.object_key,
    content_type: contentType,
    sort_order: sortOrder,
    make_primary: isPrimary,
  });
}

export function listMyPhotos() {
  return apiGet<Photo[]>("/media/photos/me");
}

export function setPrimaryPhoto(photoId: string) {
  return apiPatch<Photo>(`/media/photos/${photoId}/primary`, {});
}

export function deletePhoto(photoId: string) {
  return apiDelete<{ message: string }>(`/media/photos/${photoId}`);
}
