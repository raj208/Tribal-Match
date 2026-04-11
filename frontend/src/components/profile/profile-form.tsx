"use client";

import { useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";

import { createProfile, getMyProfile, updateMyProfile } from "@/lib/api/profile";
import type { Profile, ProfilePayload } from "@/types/profile";

type FormState = {
  full_name: string;
  age: string;
  gender: string;
  date_of_birth: string;
  community_or_tribe: string;
  subgroup_or_clan: string;
  native_language: string;
  other_languages: string;
  location_city: string;
  location_state: string;
  location_country: string;
  occupation: string;
  education: string;
  bio: string;
  profile_visibility: string;
  preferred_min_age: string;
  preferred_max_age: string;
  preferred_locations: string;
  preferred_communities: string;
  preferred_languages: string;
};

const EMPTY_FORM: FormState = {
  full_name: "",
  age: "",
  gender: "",
  date_of_birth: "",
  community_or_tribe: "",
  subgroup_or_clan: "",
  native_language: "",
  other_languages: "",
  location_city: "",
  location_state: "",
  location_country: "",
  occupation: "",
  education: "",
  bio: "",
  profile_visibility: "public",
  preferred_min_age: "",
  preferred_max_age: "",
  preferred_locations: "",
  preferred_communities: "",
  preferred_languages: "",
};

function splitCsv(value: string): string[] {
  return value
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean);
}

function joinCsv(values: string[] | null | undefined): string {
  if (!values || values.length === 0) return "";
  return values.join(", ");
}

function toFormState(profile: Profile): FormState {
  return {
    full_name: profile.full_name ?? "",
    age: profile.age?.toString() ?? "",
    gender: profile.gender ?? "",
    date_of_birth: profile.date_of_birth ?? "",
    community_or_tribe: profile.community_or_tribe ?? "",
    subgroup_or_clan: profile.subgroup_or_clan ?? "",
    native_language: profile.native_language ?? "",
    other_languages: joinCsv(profile.other_languages),
    location_city: profile.location_city ?? "",
    location_state: profile.location_state ?? "",
    location_country: profile.location_country ?? "",
    occupation: profile.occupation ?? "",
    education: profile.education ?? "",
    bio: profile.bio ?? "",
    profile_visibility: profile.profile_visibility ?? "public",
    preferred_min_age: profile.preferences?.preferred_min_age?.toString() ?? "",
    preferred_max_age: profile.preferences?.preferred_max_age?.toString() ?? "",
    preferred_locations: joinCsv(profile.preferences?.preferred_locations),
    preferred_communities: joinCsv(profile.preferences?.preferred_communities),
    preferred_languages: joinCsv(profile.preferences?.preferred_languages),
  };
}

function toNullableString(value: string): string | null {
  const trimmed = value.trim();
  return trimmed ? trimmed : null;
}

function toNullableNumber(value: string): number | null {
  const trimmed = value.trim();
  if (!trimmed) return null;

  const parsed = Number(trimmed);
  return Number.isNaN(parsed) ? null : parsed;
}

function buildPayload(form: FormState): ProfilePayload {
  const preferencesFilled =
    form.preferred_min_age.trim() ||
    form.preferred_max_age.trim() ||
    form.preferred_locations.trim() ||
    form.preferred_communities.trim() ||
    form.preferred_languages.trim();

  return {
    full_name: form.full_name.trim(),
    age: toNullableNumber(form.age),
    gender: toNullableString(form.gender),
    date_of_birth: toNullableString(form.date_of_birth),
    community_or_tribe: toNullableString(form.community_or_tribe),
    subgroup_or_clan: toNullableString(form.subgroup_or_clan),
    native_language: toNullableString(form.native_language),
    other_languages: splitCsv(form.other_languages),
    location_city: toNullableString(form.location_city),
    location_state: toNullableString(form.location_state),
    location_country: toNullableString(form.location_country),
    occupation: toNullableString(form.occupation),
    education: toNullableString(form.education),
    bio: toNullableString(form.bio),
    profile_visibility: form.profile_visibility || "public",
    preferences: preferencesFilled
      ? {
          preferred_min_age: toNullableNumber(form.preferred_min_age),
          preferred_max_age: toNullableNumber(form.preferred_max_age),
          preferred_locations: splitCsv(form.preferred_locations),
          preferred_communities: splitCsv(form.preferred_communities),
          preferred_languages: splitCsv(form.preferred_languages),
        }
      : null,
  };
}

export function ProfileForm() {
  const router = useRouter();

  const [form, setForm] = useState<FormState>(EMPTY_FORM);
  const [loading, setLoading] = useState(true);
  const [hasProfile, setHasProfile] = useState(false);
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);
  const [notice, setNotice] = useState("");

  useEffect(() => {
    let active = true;

    getMyProfile()
      .then((profile) => {
        if (!active) return;
        setHasProfile(true);
        setForm(toFormState(profile));
      })
      .catch((err: Error) => {
        if (!active) return;

        if (err.message.includes("404")) {
          setHasProfile(false);
          setForm(EMPTY_FORM);
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

  const title = useMemo(() => {
    return hasProfile ? "Edit your profile" : "Create your profile";
  }, [hasProfile]);

  function updateField<K extends keyof FormState>(key: K, value: FormState[K]) {
    setForm((prev) => ({ ...prev, [key]: value }));
  }

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setError("");
    setNotice("");

    if (!form.full_name.trim()) {
      setError("Full name is required.");
      return;
    }

    try {
      setSaving(true);
      const payload = buildPayload(form);

      if (hasProfile) {
        await updateMyProfile(payload);
        setNotice("Profile updated successfully.");
      } else {
        await createProfile(payload);
        setHasProfile(true);
        setNotice("Profile created successfully.");
      }

      router.push("/profile");
      router.refresh();
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Failed to save profile";
      setError(msg);
    } finally {
      setSaving(false);
    }
  }

  if (loading) {
    return <div className="card p-6 text-sm text-stone-600">Loading form...</div>;
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div className="card p-6">
        <h3 className="text-lg font-semibold text-stone-900">{title}</h3>
        <p className="mt-2 text-sm text-stone-600">
          Fill your basic details first. Later we will connect photos, intro video, and verification.
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
      </div>

      <div className="card p-6">
        <h3 className="text-lg font-semibold text-stone-900">Basic information</h3>

        <div className="mt-5 grid gap-4 md:grid-cols-2">
          <label className="text-sm">
            <span className="mb-2 block font-medium text-stone-700">Full name *</span>
            <input
              value={form.full_name}
              onChange={(e) => updateField("full_name", e.target.value)}
              className="w-full rounded-xl border border-stone-300 px-3 py-2 outline-none focus:border-stone-500"
              placeholder="Enter your full name"
            />
          </label>

          <label className="text-sm">
            <span className="mb-2 block font-medium text-stone-700">Age</span>
            <input
              value={form.age}
              onChange={(e) => updateField("age", e.target.value)}
              type="number"
              className="w-full rounded-xl border border-stone-300 px-3 py-2 outline-none focus:border-stone-500"
              placeholder="22"
            />
          </label>

          <label className="text-sm">
            <span className="mb-2 block font-medium text-stone-700">Gender</span>
            <input
              value={form.gender}
              onChange={(e) => updateField("gender", e.target.value)}
              className="w-full rounded-xl border border-stone-300 px-3 py-2 outline-none focus:border-stone-500"
              placeholder="male / female / other"
            />
          </label>

          <label className="text-sm">
            <span className="mb-2 block font-medium text-stone-700">Date of birth</span>
            <input
              value={form.date_of_birth}
              onChange={(e) => updateField("date_of_birth", e.target.value)}
              type="date"
              className="w-full rounded-xl border border-stone-300 px-3 py-2 outline-none focus:border-stone-500"
            />
          </label>

          <label className="text-sm">
            <span className="mb-2 block font-medium text-stone-700">Community / Tribe</span>
            <input
              value={form.community_or_tribe}
              onChange={(e) => updateField("community_or_tribe", e.target.value)}
              className="w-full rounded-xl border border-stone-300 px-3 py-2 outline-none focus:border-stone-500"
              placeholder="Santhal"
            />
          </label>

          <label className="text-sm">
            <span className="mb-2 block font-medium text-stone-700">Subgroup / Clan</span>
            <input
              value={form.subgroup_or_clan}
              onChange={(e) => updateField("subgroup_or_clan", e.target.value)}
              className="w-full rounded-xl border border-stone-300 px-3 py-2 outline-none focus:border-stone-500"
              placeholder="Optional"
            />
          </label>

          <label className="text-sm">
            <span className="mb-2 block font-medium text-stone-700">Native language</span>
            <input
              value={form.native_language}
              onChange={(e) => updateField("native_language", e.target.value)}
              className="w-full rounded-xl border border-stone-300 px-3 py-2 outline-none focus:border-stone-500"
              placeholder="Santali"
            />
          </label>

          <label className="text-sm">
            <span className="mb-2 block font-medium text-stone-700">Other languages</span>
            <input
              value={form.other_languages}
              onChange={(e) => updateField("other_languages", e.target.value)}
              className="w-full rounded-xl border border-stone-300 px-3 py-2 outline-none focus:border-stone-500"
              placeholder="Hindi, English"
            />
          </label>
        </div>
      </div>

      <div className="card p-6">
        <h3 className="text-lg font-semibold text-stone-900">Location and background</h3>

        <div className="mt-5 grid gap-4 md:grid-cols-2">
          <label className="text-sm">
            <span className="mb-2 block font-medium text-stone-700">City</span>
            <input
              value={form.location_city}
              onChange={(e) => updateField("location_city", e.target.value)}
              className="w-full rounded-xl border border-stone-300 px-3 py-2 outline-none focus:border-stone-500"
            />
          </label>

          <label className="text-sm">
            <span className="mb-2 block font-medium text-stone-700">State</span>
            <input
              value={form.location_state}
              onChange={(e) => updateField("location_state", e.target.value)}
              className="w-full rounded-xl border border-stone-300 px-3 py-2 outline-none focus:border-stone-500"
            />
          </label>

          <label className="text-sm">
            <span className="mb-2 block font-medium text-stone-700">Country</span>
            <input
              value={form.location_country}
              onChange={(e) => updateField("location_country", e.target.value)}
              className="w-full rounded-xl border border-stone-300 px-3 py-2 outline-none focus:border-stone-500"
            />
          </label>

          <label className="text-sm">
            <span className="mb-2 block font-medium text-stone-700">Occupation</span>
            <input
              value={form.occupation}
              onChange={(e) => updateField("occupation", e.target.value)}
              className="w-full rounded-xl border border-stone-300 px-3 py-2 outline-none focus:border-stone-500"
            />
          </label>

          <label className="text-sm">
            <span className="mb-2 block font-medium text-stone-700">Education</span>
            <input
              value={form.education}
              onChange={(e) => updateField("education", e.target.value)}
              className="w-full rounded-xl border border-stone-300 px-3 py-2 outline-none focus:border-stone-500"
            />
          </label>

          <label className="text-sm">
            <span className="mb-2 block font-medium text-stone-700">Profile visibility</span>
            <select
              value={form.profile_visibility}
              onChange={(e) => updateField("profile_visibility", e.target.value)}
              className="w-full rounded-xl border border-stone-300 px-3 py-2 outline-none focus:border-stone-500"
            >
              <option value="public">public</option>
              <option value="private">private</option>
            </select>
          </label>
        </div>

        <label className="mt-4 block text-sm">
          <span className="mb-2 block font-medium text-stone-700">Bio</span>
          <textarea
            value={form.bio}
            onChange={(e) => updateField("bio", e.target.value)}
            rows={5}
            className="w-full rounded-xl border border-stone-300 px-3 py-2 outline-none focus:border-stone-500"
            placeholder="Write a short introduction"
          />
        </label>
      </div>

      <div className="card p-6">
        <h3 className="text-lg font-semibold text-stone-900">Preferences</h3>
        <p className="mt-2 text-sm text-stone-600">
          Use comma-separated values for location, community, and language preferences.
        </p>

        <div className="mt-5 grid gap-4 md:grid-cols-2">
          <label className="text-sm">
            <span className="mb-2 block font-medium text-stone-700">Preferred minimum age</span>
            <input
              value={form.preferred_min_age}
              onChange={(e) => updateField("preferred_min_age", e.target.value)}
              type="number"
              className="w-full rounded-xl border border-stone-300 px-3 py-2 outline-none focus:border-stone-500"
            />
          </label>

          <label className="text-sm">
            <span className="mb-2 block font-medium text-stone-700">Preferred maximum age</span>
            <input
              value={form.preferred_max_age}
              onChange={(e) => updateField("preferred_max_age", e.target.value)}
              type="number"
              className="w-full rounded-xl border border-stone-300 px-3 py-2 outline-none focus:border-stone-500"
            />
          </label>

          <label className="text-sm md:col-span-2">
            <span className="mb-2 block font-medium text-stone-700">Preferred locations</span>
            <input
              value={form.preferred_locations}
              onChange={(e) => updateField("preferred_locations", e.target.value)}
              className="w-full rounded-xl border border-stone-300 px-3 py-2 outline-none focus:border-stone-500"
              placeholder="Ranchi, Jamshedpur, Bhubaneswar"
            />
          </label>

          <label className="text-sm md:col-span-2">
            <span className="mb-2 block font-medium text-stone-700">Preferred communities</span>
            <input
              value={form.preferred_communities}
              onChange={(e) => updateField("preferred_communities", e.target.value)}
              className="w-full rounded-xl border border-stone-300 px-3 py-2 outline-none focus:border-stone-500"
              placeholder="Santhal, Ho"
            />
          </label>

          <label className="text-sm md:col-span-2">
            <span className="mb-2 block font-medium text-stone-700">Preferred languages</span>
            <input
              value={form.preferred_languages}
              onChange={(e) => updateField("preferred_languages", e.target.value)}
              className="w-full rounded-xl border border-stone-300 px-3 py-2 outline-none focus:border-stone-500"
              placeholder="Santali, Hindi"
            />
          </label>
        </div>
      </div>

      <div className="flex justify-end">
        <button
          type="submit"
          disabled={saving}
          className="rounded-xl bg-stone-900 px-5 py-3 text-sm font-medium text-white hover:bg-stone-800 disabled:cursor-not-allowed disabled:opacity-60"
        >
          {saving ? "Saving..." : hasProfile ? "Update profile" : "Create profile"}
        </button>
      </div>
    </form>
  );
}