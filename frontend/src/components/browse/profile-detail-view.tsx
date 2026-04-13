"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { getPublicProfile } from "@/lib/api/discovery";
import { sendInterest } from "@/lib/api/interests";
import { addToShortlist } from "@/lib/api/shortlist";
import type { PublicProfile } from "@/types/discovery";

export function ProfileDetailView({ profileId }: { profileId: string }) {
  const [profile, setProfile] = useState<PublicProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [actionLoading, setActionLoading] = useState<"shortlist" | "interest" | "">("");

  useEffect(() => {
    let active = true;

    getPublicProfile(profileId)
      .then((data) => {
        if (!active) return;
        setProfile(data);
      })
      .catch((err: Error) => {
        if (!active) return;
        setError(err.message || "Failed to load profile");
      })
      .finally(() => {
        if (!active) return;
        setLoading(false);
      });

    return () => {
      active = false;
    };
  }, [profileId]);

  async function handleShortlist() {
    if (!profile) return;

    setError("");
    setNotice("");
    setActionLoading("shortlist");

    try {
      await addToShortlist(profile.id);
      setNotice("Profile saved to shortlist.");
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Failed to shortlist profile";
      setError(msg);
    } finally {
      setActionLoading("");
    }
  }

  async function handleInterest() {
    if (!profile) return;

    setError("");
    setNotice("");
    setActionLoading("interest");

    try {
      await sendInterest(profile.id);
      setNotice("Interest sent successfully.");
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Failed to send interest";
      setError(msg);
    } finally {
      setActionLoading("");
    }
  }

  if (loading) {
    return <div className="card p-6 text-sm text-stone-600">Loading profile...</div>;
  }

  if (error && !profile) {
    return (
      <div className="card border-red-200 p-6">
        <p className="text-sm font-medium text-red-700">Unable to load profile</p>
        <p className="mt-2 text-sm text-red-600">{error || "Profile not found"}</p>
      </div>
    );
  }

  if (!profile) {
    return (
      <div className="card p-6 text-sm text-stone-600">
        Profile not found.
      </div>
    );
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

      <div className="card p-6">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <h2 className="text-2xl font-semibold text-stone-900">{profile.full_name}</h2>
            <p className="mt-2 text-sm text-stone-600">
              {profile.age ?? "—"} • {profile.community_or_tribe ?? "—"} • {profile.location_city ?? "—"}
            </p>
          </div>

          <div className="flex flex-wrap gap-3">
            <button
              type="button"
              onClick={handleShortlist}
              disabled={actionLoading !== ""}
              className="rounded-xl border border-stone-300 bg-white px-4 py-2 text-sm font-medium text-stone-800 hover:bg-stone-100 disabled:opacity-60"
            >
              {actionLoading === "shortlist" ? "Saving..." : "Save profile"}
            </button>

            <button
              type="button"
              onClick={handleInterest}
              disabled={actionLoading !== ""}
              className="rounded-xl bg-stone-900 px-4 py-2 text-sm font-medium text-white hover:bg-stone-800 disabled:opacity-60"
            >
              {actionLoading === "interest" ? "Sending..." : "Express interest"}
            </button>
          </div>
        </div>
      </div>

      <div className="grid gap-5 md:grid-cols-2">
        <div className="card p-6">
          <h3 className="text-lg font-semibold text-stone-900">Basic Information</h3>
          <div className="mt-4 space-y-3 text-sm text-stone-700">
            <p><span className="font-medium">Name:</span> {profile.full_name}</p>
            <p><span className="font-medium">Age:</span> {profile.age ?? "—"}</p>
            <p><span className="font-medium">Gender:</span> {profile.gender ?? "—"}</p>
            <p><span className="font-medium">Community:</span> {profile.community_or_tribe ?? "—"}</p>
            <p><span className="font-medium">Clan:</span> {profile.subgroup_or_clan ?? "—"}</p>
            <p><span className="font-medium">Native language:</span> {profile.native_language ?? "—"}</p>
            <p>
              <span className="font-medium">Other languages:</span>{" "}
              {profile.other_languages.length ? profile.other_languages.join(", ") : "—"}
            </p>
          </div>
        </div>

        <div className="card p-6">
          <h3 className="text-lg font-semibold text-stone-900">Location & Background</h3>
          <div className="mt-4 space-y-3 text-sm text-stone-700">
            <p><span className="font-medium">City:</span> {profile.location_city ?? "—"}</p>
            <p><span className="font-medium">State:</span> {profile.location_state ?? "—"}</p>
            <p><span className="font-medium">Country:</span> {profile.location_country ?? "—"}</p>
            <p><span className="font-medium">Occupation:</span> {profile.occupation ?? "—"}</p>
            <p><span className="font-medium">Education:</span> {profile.education ?? "—"}</p>
            <p><span className="font-medium">Verification:</span> {profile.verification_status}</p>
          </div>
        </div>
      </div>

      <div className="card p-6">
        <h3 className="text-lg font-semibold text-stone-900">About</h3>
        <p className="mt-3 text-sm text-stone-700">{profile.bio || "—"}</p>
      </div>

      <div className="card p-6">
        <div className="flex items-center justify-between gap-3">
          <h3 className="text-lg font-semibold text-stone-900">Photos</h3>
          <Link
            href="/shortlisted"
            className="rounded-xl border border-stone-300 bg-white px-4 py-2 text-sm font-medium text-stone-800 hover:bg-stone-100"
          >
            View shortlist
          </Link>
        </div>

        {profile.photos.length === 0 ? (
          <p className="mt-4 text-sm text-stone-600">No photos available.</p>
        ) : (
          <div className="mt-5 grid gap-4 md:grid-cols-2 xl:grid-cols-3">
            {profile.photos.map((photo) => (
              <div key={photo.id} className="overflow-hidden rounded-2xl border border-stone-200">
                <div className="aspect-[4/3] bg-stone-100">
                  <img
                    src={photo.photo_url}
                    alt={profile.full_name}
                    className="h-full w-full object-cover"
                  />
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {profile.intro_video_url ? (
        <div className="card p-6">
          <h3 className="text-lg font-semibold text-stone-900">Intro Video</h3>
          <video
            controls
            className="mt-4 w-full rounded-xl border border-stone-200"
            src={profile.intro_video_url}
          />
        </div>
      ) : null}
    </div>
  );
}