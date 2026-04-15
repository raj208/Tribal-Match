"use client";

import Link from "next/link";
import { useState } from "react";

import {
  useInterestAction,
  useReceivedInterests,
  useSentInterests,
} from "@/hooks/use-interests";
import type { InterestAction } from "@/types/interactions";

type PendingAction = {
  interestId: string;
  action: InterestAction;
} | null;

export function InterestsClient() {
  const [tab, setTab] = useState<"received" | "sent">("received");
  const [pendingAction, setPendingAction] = useState<PendingAction>(null);
  const sentQuery = useSentInterests();
  const receivedQuery = useReceivedInterests();
  const interestAction = useInterestAction();

  async function handleInterestAction(interestId: string, action: InterestAction) {
    setPendingAction({ interestId, action });

    try {
      const result = await interestAction.mutate(interestId, action);
      if (result) {
        receivedQuery.reload();
        sentQuery.reload();
      }
    } finally {
      setPendingAction(null);
    }
  }

  const sent = sentQuery.interests;
  const received = receivedQuery.interests;
  const items = tab === "received" ? received : sent;
  const loading = sentQuery.loading || receivedQuery.loading;
  const listError = tab === "received" ? receivedQuery.error : sentQuery.error;
  const error = interestAction.error || listError;

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
                  <div className="flex flex-wrap gap-3">
                    <Link
                      href={`/browse/${item.profile_id}`}
                      className="rounded-xl bg-stone-900 px-4 py-2 text-sm font-medium text-white hover:bg-stone-800"
                    >
                      View profile
                    </Link>

                    {tab === "received" && item.status === "sent" ? (
                      <>
                        <button
                          type="button"
                          onClick={() => handleInterestAction(item.id, "accept")}
                          disabled={interestAction.loading}
                          className="rounded-xl bg-green-700 px-4 py-2 text-sm font-medium text-white hover:bg-green-800 disabled:cursor-not-allowed disabled:opacity-60"
                        >
                          {pendingAction?.interestId === item.id && pendingAction.action === "accept"
                            ? "Accepting..."
                            : "Accept"}
                        </button>

                        <button
                          type="button"
                          onClick={() => handleInterestAction(item.id, "decline")}
                          disabled={interestAction.loading}
                          className="rounded-xl border border-stone-300 bg-white px-4 py-2 text-sm font-medium text-stone-800 hover:bg-stone-50 disabled:cursor-not-allowed disabled:opacity-60"
                        >
                          {pendingAction?.interestId === item.id && pendingAction.action === "decline"
                            ? "Declining..."
                            : "Decline"}
                        </button>
                      </>
                    ) : null}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
