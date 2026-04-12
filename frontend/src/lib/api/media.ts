import { apiDelete, apiGet, apiPatch, apiPost } from "@/lib/api/client";
import type { Photo } from "@/types/media";

export async function uploadPhoto(file: File, sortOrder: number, isPrimary: boolean) {
  const form = new FormData();
  form.append("file", file);
  form.append("sort_order", String(sortOrder));
  form.append("is_primary", String(isPrimary));
  return apiPost<Photo>("/media/photos/upload", form);
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