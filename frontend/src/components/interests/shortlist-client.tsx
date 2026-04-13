"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { deleteShortlistItem, listMyShortlist } from "@/lib/api/shortlist";
import type { ShortlistItem } from "@/types/interactions";

export function ShortlistClient() {
  const [items, setItems] = useState<ShortlistItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");

  async function loadData() {
    try {
      const data = await listMyShortlist();
      setItems(data);
      setError("");
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Failed to load shortlist";
      setError(msg);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadData();
  }, []);

  async function handleRemove(shortlistId: string) {
    setError("");
    setNotice("");

    try {
      await deleteShortlistItem(shortlistId);
      setNotice("Removed from shortlist.");
      await loadData();
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Failed to remove item";
      setError(msg);
    }
  }

  if (loading) {
    return <div className="card p-6 text-sm text-stone-600">Loading shortlist...</div>;
  }

  return (
    <div className="space-y-5">
      {error ? (
        <div className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          {error}
        </div>
      ) : null}

      {notice ? (
        <div className="rounded-xl border border-green-200 bg-green-50 px-4 py-3 text-sm text-green-700">
          {notice}
        </div>
      ) : null}

      {items.length === 0 ? (
        <div className="card p-6">
          <h3 className="text-lg font-semibold text-stone-900">No shortlisted profiles</h3>
          <p className="mt-2 text-sm text-stone-600">
            Save profiles from the browse detail page to see them here.
          </p>
        </div>
      ) : (
        <div className="grid gap-5 md:grid-cols-2 xl:grid-cols-3">
          {items.map((item) => (
            <div key={item.id} className="card overflow-hidden">
              <div className="aspect-[4/3] bg-stone-100">
                {item.primary_photo_url ? (
                  <img
                    src={item.primary_photo_url}
                    alt={item.full_name}
                    className="h-full w-full object-cover"
                  />
                ) : (
                  <div className="flex h-full items-center justify-center text-sm text-stone-500">
                    No photo
                  </div>
                )}
              </div>

              <div className="p-5">
                <h3 className="text-lg font-semibold text-stone-900">{item.full_name}</h3>
                <p className="mt-1 text-sm text-stone-600">
                  {item.age ?? "—"} • {item.community_or_tribe ?? "—"}
                </p>

                <div className="mt-4 space-y-2 text-sm text-stone-700">
                  <p><span className="font-medium">Language:</span> {item.native_language ?? "—"}</p>
                  <p><span className="font-medium">City:</span> {item.location_city ?? "—"}</p>
                  <p><span className="font-medium">Occupation:</span> {item.occupation ?? "—"}</p>
                </div>

                <p className="mt-4 line-clamp-3 text-sm text-stone-600">
                  {item.bio || "No bio added yet."}
                </p>

                <div className="mt-5 flex flex-wrap gap-2">
                  <Link
                    href={`/browse/${item.profile_id}`}
                    className="rounded-xl bg-stone-900 px-4 py-2 text-sm font-medium text-white hover:bg-stone-800"
                  >
                    View profile
                  </Link>

                  <button
                    type="button"
                    onClick={() => handleRemove(item.id)}
                    className="rounded-xl border border-red-200 px-4 py-2 text-sm font-medium text-red-700 hover:bg-red-50"
                  >
                    Remove
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}