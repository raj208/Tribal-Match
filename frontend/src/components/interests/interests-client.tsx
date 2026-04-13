"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { listReceivedInterests, listSentInterests } from "@/lib/api/interests";
import type { InterestItem } from "@/types/interactions";

export function InterestsClient() {
  const [tab, setTab] = useState<"received" | "sent">("received");
  const [sent, setSent] = useState<InterestItem[]>([]);
  const [received, setReceived] = useState<InterestItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  async function loadData() {
    try {
      const [sentData, receivedData] = await Promise.all([
        listSentInterests(),
        listReceivedInterests(),
      ]);

      setSent(sentData);
      setReceived(receivedData);
      setError("");
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Failed to load interests";
      setError(msg);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadData();
  }, []);

  const items = tab === "received" ? received : sent;

  if (loading) {
    return <div className="card p-6 text-sm text-stone-600">Loading interests...</div>;
  }

  return (
    <div className="space-y-5">
      {error ? (
        <div className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          {error}
        </div>
      ) : null}

      <div className="card p-4">
        <div className="flex flex-wrap gap-3">
          <button
            type="button"
            onClick={() => setTab("received")}
            className={`rounded-xl px-4 py-2 text-sm font-medium ${
              tab === "received"
                ? "bg-stone-900 text-white"
                : "border border-stone-300 bg-white text-stone-800"
            }`}
          >
            Received ({received.length})
          </button>

          <button
            type="button"
            onClick={() => setTab("sent")}
            className={`rounded-xl px-4 py-2 text-sm font-medium ${
              tab === "sent"
                ? "bg-stone-900 text-white"
                : "border border-stone-300 bg-white text-stone-800"
            }`}
          >
            Sent ({sent.length})
          </button>
        </div>
      </div>

      {items.length === 0 ? (
        <div className="card p-6">
          <h3 className="text-lg font-semibold text-stone-900">
            No {tab} interests yet
          </h3>
          <p className="mt-2 text-sm text-stone-600">
            {tab === "received"
              ? "When someone expresses interest in your profile, it will appear here."
              : "Send interest from a public profile detail page to see it here."}
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
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <h3 className="text-lg font-semibold text-stone-900">{item.full_name}</h3>
                    <p className="mt-1 text-sm text-stone-600">
                      {item.age ?? "—"} • {item.community_or_tribe ?? "—"}
                    </p>
                  </div>

                  <span className="soft-badge bg-stone-100 text-stone-700">
                    {item.status}
                  </span>
                </div>

                <div className="mt-4 space-y-2 text-sm text-stone-700">
                  <p><span className="font-medium">Language:</span> {item.native_language ?? "—"}</p>
                  <p><span className="font-medium">City:</span> {item.location_city ?? "—"}</p>
                  <p><span className="font-medium">Occupation:</span> {item.occupation ?? "—"}</p>
                </div>

                <p className="mt-4 line-clamp-3 text-sm text-stone-600">
                  {item.bio || "No bio added yet."}
                </p>

                <div className="mt-5">
                  <Link
                    href={`/browse/${item.profile_id}`}
                    className="rounded-xl bg-stone-900 px-4 py-2 text-sm font-medium text-white hover:bg-stone-800"
                  >
                    View profile
                  </Link>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}