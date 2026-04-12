"use client";

import { useEffect, useState } from "react";

import { addPhoto, deletePhoto, listMyPhotos, setPrimaryPhoto } from "@/lib/api/media";
import type { Photo } from "@/types/media";

export function PhotoManager() {
  const [photos, setPhotos] = useState<Photo[]>([]);
  const [photoUrl, setPhotoUrl] = useState("");
  const [sortOrder, setSortOrder] = useState("0");
  const [isPrimary, setIsPrimary] = useState(false);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");

  async function loadPhotos() {
    try {
      const data = await listMyPhotos();
      setPhotos(data);
      setError("");
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Failed to load photos";
      setError(msg);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadPhotos();
  }, []);

  async function handleAddPhoto(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setError("");
    setNotice("");

    if (!photoUrl.trim()) {
      setError("Photo URL is required.");
      return;
    }

    try {
      setSaving(true);
      await addPhoto({
        photo_url: photoUrl.trim(),
        sort_order: Number(sortOrder || 0),
        is_primary: isPrimary,
      });

      setPhotoUrl("");
      setSortOrder("0");
      setIsPrimary(false);
      setNotice("Photo placeholder added.");
      await loadPhotos();
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Failed to add photo";
      setError(msg);
    } finally {
      setSaving(false);
    }
  }

  async function handleSetPrimary(photoId: string) {
    setError("");
    setNotice("");

    try {
      await setPrimaryPhoto(photoId);
      setNotice("Primary photo updated.");
      await loadPhotos();
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Failed to set primary photo";
      setError(msg);
    }
  }

  async function handleDelete(photoId: string) {
    setError("");
    setNotice("");

    try {
      await deletePhoto(photoId);
      setNotice("Photo deleted.");
      await loadPhotos();
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Failed to delete photo";
      setError(msg);
    }
  }

  return (
    <div className="space-y-5">
      <div className="card p-6">
        <h3 className="text-lg font-semibold text-stone-900">Profile photos</h3>
        <p className="mt-2 text-sm text-stone-600">
          This is a placeholder media flow. Paste image URLs for now. Real upload storage comes later.
        </p>

        {error ? (
          <div className="mt-4 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
            {error}
          </div>
        ) : null}

        {notice ? (
          <div className="mt-4 rounded-xl border border-green-200 bg-green-50 px-4 py-3 text-sm text-green-700">
            {notice}
          </div>
        ) : null}

        <form onSubmit={handleAddPhoto} className="mt-5 grid gap-4 md:grid-cols-2">
          <label className="text-sm md:col-span-2">
            <span className="mb-2 block font-medium text-stone-700">Photo URL</span>
            <input
              value={photoUrl}
              onChange={(e) => setPhotoUrl(e.target.value)}
              className="w-full rounded-xl border border-stone-300 px-3 py-2 outline-none focus:border-stone-500"
              placeholder="https://example.com/photo.jpg"
            />
          </label>

          <label className="text-sm">
            <span className="mb-2 block font-medium text-stone-700">Sort order</span>
            <input
              value={sortOrder}
              onChange={(e) => setSortOrder(e.target.value)}
              type="number"
              className="w-full rounded-xl border border-stone-300 px-3 py-2 outline-none focus:border-stone-500"
            />
          </label>

          <label className="flex items-center gap-3 text-sm text-stone-700">
            <input
              checked={isPrimary}
              onChange={(e) => setIsPrimary(e.target.checked)}
              type="checkbox"
            />
            Set as primary
          </label>

          <div className="md:col-span-2">
            <button
              type="submit"
              disabled={saving}
              className="rounded-xl bg-stone-900 px-5 py-3 text-sm font-medium text-white hover:bg-stone-800 disabled:opacity-60"
            >
              {saving ? "Adding..." : "Add photo"}
            </button>
          </div>
        </form>
      </div>

      <div className="card p-6">
        <div className="flex items-center justify-between gap-3">
          <h3 className="text-lg font-semibold text-stone-900">Saved photos</h3>
          <span className="soft-badge bg-stone-100 text-stone-700">
            {photos.length}/6
          </span>
        </div>

        {loading ? (
          <p className="mt-4 text-sm text-stone-600">Loading photos...</p>
        ) : photos.length === 0 ? (
          <p className="mt-4 text-sm text-stone-600">No photos added yet.</p>
        ) : (
          <div className="mt-5 grid gap-4 md:grid-cols-2 xl:grid-cols-3">
            {photos.map((photo) => (
              <div key={photo.id} className="rounded-2xl border border-stone-200 p-4">
                <div className="aspect-[4/3] overflow-hidden rounded-xl bg-stone-100">
                  <img
                    src={photo.photo_url}
                    alt="Profile media"
                    className="h-full w-full object-cover"
                  />
                </div>

                <div className="mt-3 space-y-2 text-sm text-stone-700">
                  <p>
                    <span className="font-medium">Sort:</span> {photo.sort_order}
                  </p>
                  <p>
                    <span className="font-medium">Primary:</span> {photo.is_primary ? "Yes" : "No"}
                  </p>
                </div>

                <div className="mt-4 flex flex-wrap gap-2">
                  {!photo.is_primary ? (
                    <button
                      type="button"
                      onClick={() => handleSetPrimary(photo.id)}
                      className="rounded-xl border border-stone-300 px-3 py-2 text-sm text-stone-700 hover:bg-stone-100"
                    >
                      Set primary
                    </button>
                  ) : (
                    <span className="rounded-xl bg-green-100 px-3 py-2 text-sm font-medium text-green-700">
                      Primary
                    </span>
                  )}

                  <button
                    type="button"
                    onClick={() => handleDelete(photo.id)}
                    className="rounded-xl border border-red-200 px-3 py-2 text-sm text-red-700 hover:bg-red-50"
                  >
                    Delete
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}