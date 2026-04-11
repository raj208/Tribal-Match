"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { getMyProfile } from "@/lib/api/profile";
import type { Profile } from "@/types/profile";

function joinList(items: string[] | null | undefined) {
  if (!items || items.length === 0) return "—";
  return items.join(", ");
}

export function ProfileView() {
  const [profile, setProfile] = useState<Profile | null>(null);
  const [loading, setLoading] = useState(true);
  const [missing, setMissing] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;

    getMyProfile()
      .then((data) => {
        if (!active) return;
        setProfile(data);
        setMissing(false);
        setError("");
      })
      .catch((err: Error) => {
        if (!active) return;

        if (err.message.includes("404")) {
          setMissing(true);
          setProfile(null);
          setError("");
          return;
        }

        setError(err.message || "Unable to load profile");
      })
      .finally(() => {
        if (!active) return;
        setLoading(false);
      });

    return () => {
      active = false;
    };
  }, []);

  if (loading) {
    return <div className="card p-6 text-sm text-stone-600">Loading profile...</div>;
  }

  if (error) {
    return (
      <div className="card border-red-200 p-6">
        <p className="text-sm font-medium text-red-700">Failed to load profile</p>
        <p className="mt-2 text-sm text-red-600">{error}</p>
      </div>
    );
  }

  if (missing || !profile) {
    return (
      <div className="card p-6">
        <h3 className="text-lg font-semibold text-stone-900">No profile found</h3>
        <p className="mt-2 text-sm text-stone-600">
          Your profile has not been created yet. Start by filling your basic details and preferences.
        </p>
        <Link
          href="/profile/edit"
          className="mt-4 inline-flex rounded-xl bg-stone-900 px-4 py-2 text-sm font-medium text-white hover:bg-stone-800"
        >
          Create profile
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-5">
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
            <p><span className="font-medium">Other languages:</span> {joinList(profile.other_languages)}</p>
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
            <p><span className="font-medium">Visibility:</span> {profile.profile_visibility}</p>
          </div>
        </div>
      </div>

      <div className="card p-6">
        <h3 className="text-lg font-semibold text-stone-900">About</h3>
        <p className="mt-3 text-sm text-stone-700">{profile.bio || "—"}</p>
      </div>

      <div className="grid gap-5 md:grid-cols-2">
        <div className="card p-6">
          <h3 className="text-lg font-semibold text-stone-900">Profile Status</h3>
          <div className="mt-4 space-y-3 text-sm text-stone-700">
            <p><span className="font-medium">Profile status:</span> {profile.profile_status}</p>
            <p><span className="font-medium">Verification status:</span> {profile.verification_status}</p>
            <p><span className="font-medium">Completion:</span> {profile.completion_percentage}%</p>
          </div>
        </div>

        <div className="card p-6">
          <h3 className="text-lg font-semibold text-stone-900">Preferences</h3>
          <div className="mt-4 space-y-3 text-sm text-stone-700">
            <p>
              <span className="font-medium">Preferred age:</span>{" "}
              {profile.preferences
                ? `${profile.preferences.preferred_min_age ?? "—"} to ${profile.preferences.preferred_max_age ?? "—"}`
                : "—"}
            </p>
            <p>
              <span className="font-medium">Preferred locations:</span>{" "}
              {joinList(profile.preferences?.preferred_locations)}
            </p>
            <p>
              <span className="font-medium">Preferred communities:</span>{" "}
              {joinList(profile.preferences?.preferred_communities)}
            </p>
            <p>
              <span className="font-medium">Preferred languages:</span>{" "}
              {joinList(profile.preferences?.preferred_languages)}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}