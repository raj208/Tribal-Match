import { apiDelete, apiGet, apiPatch, apiPost } from "@/lib/api/client";
import type { Photo } from "@/types/media";

export type PhotoPayload = {
  photo_url: string;
  sort_order: number;
  is_primary: boolean;
};

export function listMyPhotos() {
  return apiGet<Photo[]>("/media/photos/me");
}

export function addPhoto(payload: PhotoPayload) {
  return apiPost<Photo>("/media/photos", payload);
}

export function setPrimaryPhoto(photoId: string) {
  return apiPatch<Photo>(`/media/photos/${photoId}/primary`, {});
}

export function deletePhoto(photoId: string) {
  return apiDelete<{ message: string }>(`/media/photos/${photoId}`);
}