"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";

import {
  useDeactivateProfile,
  useDeleteProfile,
  useSettingsSummary,
  useUpdateSettings,
} from "@/hooks/use-settings";
import type { ProfileStatus, VerificationStatus } from "@/types";
import type { ProfileVisibility } from "@/types/settings";

type ConfirmAction = "deactivate" | "delete" | null;

function formatLabel(value: string | null | undefined) {
  if (!value) return "Not available";
  return value
    .replace(/_/g, " ")
    .replace(/\b\w/g, (char) => char.toUpperCase());
}

function toSafePercent(value: number | null | undefined) {
  return typeof value === "number" && Number.isFinite(value)
    ? Math.max(0, Math.min(100, Math.round(value)))
    : 0;
}

function normalizeVisibility(value: string | null | undefined): ProfileVisibility {
  return value === "private" ? "private" : "public";
}

function getProfileStatusBadgeClass(status: ProfileStatus | null) {
  if (!status) return "bg-stone-100 text-stone-700";
  if (status === "published") return "bg-green-100 text-green-700";
  if (status === "draft") return "bg-amber-100 text-amber-700";
  if (status === "deactivated") return "bg-amber-100 text-amber-800";
  if (status === "deleted") return "bg-red-100 text-red-700";
  return "bg-stone-100 text-stone-700";
}

function getVerificationBadgeClass(status: VerificationStatus | null) {
  if (!status || status === "not_started") return "bg-stone-100 text-stone-700";
  if (status === "approved") return "bg-green-100 text-green-700";
  if (status === "rejected") return "bg-red-100 text-red-700";
  return "bg-amber-100 text-amber-700";
}

function getLifecycleNotice(status: ProfileStatus | null) {
  if (status === "deactivated") {
    return "Your profile is deactivated. It stays signed in to your account, but it no longer appears in browse or interest flows because discovery only includes published profiles.";
  }

  if (status === "deleted") {
    return "Your profile is soft-deleted. It remains stored on the backend, but it no longer appears in browse or interest flows because discovery only includes published profiles.";
  }

  return "Active lifecycle changes are soft actions only. Deactivate hides your profile without marking it deleted. Delete marks the profile as deleted without hard-removing related data.";
}

export function SettingsClient() {
  const { settings, loading, error, reload } = useSettingsSummary();
  const updateSettings = useUpdateSettings();
  const deactivateProfile = useDeactivateProfile();
  const deleteProfile = useDeleteProfile();

  const [profileVisibility, setProfileVisibility] = useState<ProfileVisibility>("public");
  const [notice, setNotice] = useState("");
  const [confirmAction, setConfirmAction] = useState<ConfirmAction>(null);

  useEffect(() => {
    setProfileVisibility(normalizeVisibility(settings?.profile_visibility));
  }, [settings?.profile_visibility]);

  const profileExists = settings?.profile_exists === true;
  const profileStatus = settings?.profile_status ?? null;
  const verificationStatus = settings?.verification_status ?? null;
  const completionPercentage = toSafePercent(settings?.completion_percentage);
  const completionWidth = `${completionPercentage}%`;
  const isDeactivated = profileStatus === "deactivated";
  const isDeleted = profileStatus === "deleted";
  const anyLifecycleLoading = deactivateProfile.loading || deleteProfile.loading;

  const lifecycleError = deactivateProfile.error || deleteProfile.error;

  const currentVisibilityLabel = useMemo(() => formatLabel(settings?.profile_visibility ?? "public"), [settings?.profile_visibility]);

  function clearFeedback() {
    setNotice("");
    updateSettings.reset();
    deactivateProfile.reset();
    deleteProfile.reset();
  }

  async function handleSaveVisibility(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    clearFeedback();

    const result = await updateSettings.mutate({ profile_visibility: profileVisibility });
    if (!result) return;

    setNotice("Profile visibility updated successfully.");
    reload();
  }

  async function handleDeactivate() {
    clearFeedback();

    const result = await deactivateProfile.mutate();
    if (!result) return;

    setConfirmAction(null);
    setNotice(`${result.message} Your profile is now hidden from browse and interest flows.`);
    reload();
  }

  async function handleDelete() {
    clearFeedback();

    const result = await deleteProfile.mutate();
    if (!result) return;

    setConfirmAction(null);
    setNotice(`${result.message} Your profile is now hidden from browse and interest flows.`);
    reload();
  }

  if (loading) {
    return (
      <div className="grid gap-5 lg:grid-cols-2">
        <div className="card p-6">
          <div className="animate-pulse space-y-4">
            <div className="h-4 w-32 rounded bg-stone-200" />
            <div className="grid gap-4 sm:grid-cols-2">
              <div className="h-24 rounded-2xl bg-stone-100" />
              <div className="h-24 rounded-2xl bg-stone-100" />
              <div className="h-24 rounded-2xl bg-stone-100" />
              <div className="h-24 rounded-2xl bg-stone-100" />
            </div>
          </div>
        </div>

        <div className="card p-6">
          <div className="animate-pulse space-y-4">
            <div className="h-4 w-24 rounded bg-stone-200" />
            <div className="h-10 rounded-xl bg-stone-100" />
            <div className="h-10 w-40 rounded-xl bg-stone-200" />
          </div>
        </div>

        <div className="card p-6 lg:col-span-2">
          <div className="animate-pulse space-y-4">
            <div className="h-4 w-40 rounded bg-stone-200" />
            <div className="grid gap-4 md:grid-cols-2">
              <div className="h-48 rounded-2xl bg-stone-100" />
              <div className="h-48 rounded-2xl bg-stone-100" />
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (error || !settings) {
    return (
      <div className="card border-red-200 p-6">
        <p className="text-sm font-medium text-red-700">Failed to load settings</p>
        <p className="mt-2 text-sm text-red-600">{error || "Settings data is unavailable."}</p>
        <button
          type="button"
          onClick={reload}
          className="mt-4 rounded-xl bg-stone-900 px-4 py-2 text-sm font-medium text-white hover:bg-stone-800"
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-5">
      {notice ? (
        <div className="rounded-xl border border-green-200 bg-green-50 px-4 py-3 text-sm text-green-700">
          {notice}
        </div>
      ) : null}

      <div className="grid gap-5 lg:grid-cols-2">
        <div className="card p-6">
          <div className="flex items-start justify-between gap-4">
            <div>
              <p className="text-sm text-stone-500">Account summary</p>
              <h3 className="mt-2 text-lg font-semibold text-stone-900">Current backend-backed settings status</h3>
            </div>

            <span className={`soft-badge ${profileExists ? "bg-green-100 text-green-700" : "bg-stone-100 text-stone-700"}`}>
              {profileExists ? "Profile found" : "No profile yet"}
            </span>
          </div>

          <div className="mt-5 grid gap-4 sm:grid-cols-2">
            <div className="rounded-2xl border border-stone-200 p-4">
              <p className="text-sm text-stone-500">Email</p>
              <p className="mt-2 break-all text-sm font-medium text-stone-900">{settings.email}</p>
            </div>

            <div className="rounded-2xl border border-stone-200 p-4">
              <p className="text-sm text-stone-500">Profile status</p>
              <div className="mt-2">
                <span className={`soft-badge ${getProfileStatusBadgeClass(profileStatus)}`}>
                  {formatLabel(profileStatus)}
                </span>
              </div>
            </div>

            <div className="rounded-2xl border border-stone-200 p-4">
              <p className="text-sm text-stone-500">Verification status</p>
              <div className="mt-2">
                <span className={`soft-badge ${getVerificationBadgeClass(verificationStatus)}`}>
                  {formatLabel(verificationStatus)}
                </span>
              </div>
            </div>

            <div className="rounded-2xl border border-stone-200 p-4">
              <p className="text-sm text-stone-500">Completion</p>
              <p className="mt-2 text-2xl font-semibold text-stone-900">{completionPercentage}%</p>
            </div>
          </div>

          <div className="mt-5">
            <div className="h-2 rounded-full bg-stone-200">
              <div
                className="h-2 rounded-full bg-stone-900 transition-all"
                style={{ width: completionWidth }}
              />
            </div>
          </div>

          <p className="mt-4 text-sm text-stone-600">{getLifecycleNotice(profileStatus)}</p>
        </div>

        <div className="card p-6">
          <div className="flex items-start justify-between gap-4">
            <div>
              <p className="text-sm text-stone-500">Privacy</p>
              <h3 className="mt-2 text-lg font-semibold text-stone-900">Control how your profile is exposed</h3>
            </div>

            <span className="soft-badge bg-stone-100 text-stone-700">{currentVisibilityLabel}</span>
          </div>

          {!profileExists ? (
            <div className="mt-5 rounded-2xl border border-amber-200 bg-amber-50 p-4">
              <p className="text-sm font-medium text-amber-900">Create a profile to manage privacy.</p>
              <p className="mt-2 text-sm text-amber-800">
                The backend only stores settings against an existing profile, so visibility can be updated after your profile is created.
              </p>
              <Link
                href="/profile/edit"
                className="mt-4 inline-flex rounded-xl bg-stone-900 px-4 py-2 text-sm font-medium text-white hover:bg-stone-800"
              >
                Create profile
              </Link>
            </div>
          ) : (
            <form onSubmit={handleSaveVisibility} className="mt-5 space-y-4">
              {updateSettings.error ? (
                <div className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
                  {updateSettings.error}
                </div>
              ) : null}

              <label className="block text-sm">
                <span className="mb-2 block font-medium text-stone-700">Profile visibility</span>
                <select
                  value={profileVisibility}
                  onChange={(event) => setProfileVisibility(normalizeVisibility(event.target.value))}
                  disabled={updateSettings.loading || anyLifecycleLoading}
                  className="w-full rounded-xl border border-stone-300 px-3 py-2 outline-none focus:border-stone-500 disabled:bg-stone-100 disabled:text-stone-500"
                >
                  <option value="public">public</option>
                  <option value="private">private</option>
                </select>
              </label>

              <p className="text-sm text-stone-600">
                Visibility only affects a live profile. Deactivated or deleted profiles stay hidden from browse and interest flows regardless of this setting.
              </p>

              <button
                type="submit"
                disabled={updateSettings.loading || anyLifecycleLoading}
                className="rounded-xl bg-stone-900 px-4 py-2 text-sm font-medium text-white hover:bg-stone-800 disabled:opacity-60"
              >
                {updateSettings.loading ? "Saving..." : "Save visibility"}
              </button>
            </form>
          )}
        </div>
      </div>

      <div className="card p-6">
        <div>
          <p className="text-sm text-stone-500">Account lifecycle</p>
          <h3 className="mt-2 text-lg font-semibold text-stone-900">Deactivate or soft-delete your profile</h3>
          <p className="mt-2 text-sm text-stone-600">
            These actions do not sign you out. They change the stored profile status so the backend treats your profile as inactive.
          </p>
        </div>

        {lifecycleError ? (
          <div className="mt-4 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
            {lifecycleError}
          </div>
        ) : null}

        {!profileExists ? (
          <div className="mt-5 rounded-2xl border border-stone-200 bg-stone-50 p-4 text-sm text-stone-700">
            Lifecycle actions become available after a profile exists.
          </div>
        ) : (
          <div className="mt-5 grid gap-4 md:grid-cols-2">
            <div className="rounded-2xl border border-amber-200 bg-amber-50 p-5">
              <h4 className="text-base font-semibold text-amber-950">Deactivate profile</h4>
              <p className="mt-2 text-sm text-amber-900">
                Deactivation keeps your profile record in place but changes its status to <span className="font-medium">deactivated</span>. Because discovery only includes published profiles, your profile stops appearing in browse and interaction flows.
              </p>

              {isDeactivated ? (
                <div className="mt-4 rounded-xl border border-amber-300 bg-white px-4 py-3 text-sm text-amber-900">
                  This profile is already deactivated.
                </div>
              ) : isDeleted ? (
                <div className="mt-4 rounded-xl border border-stone-300 bg-white px-4 py-3 text-sm text-stone-700">
                  This profile is already deleted, so deactivation is no longer applicable.
                </div>
              ) : confirmAction === "deactivate" ? (
                <div className="mt-4 rounded-2xl border border-amber-300 bg-white p-4">
                  <p className="text-sm font-medium text-amber-950">Confirm deactivation</p>
                  <p className="mt-2 text-sm text-amber-900">
                    After this, the current profile stays on the backend but will no longer be discoverable in browse or interest flows.
                  </p>
                  <div className="mt-4 flex flex-wrap gap-3">
                    <button
                      type="button"
                      onClick={handleDeactivate}
                      disabled={anyLifecycleLoading}
                      className="rounded-xl bg-amber-700 px-4 py-2 text-sm font-medium text-white hover:bg-amber-800 disabled:opacity-60"
                    >
                      {deactivateProfile.loading ? "Deactivating..." : "Confirm deactivate"}
                    </button>
                    <button
                      type="button"
                      onClick={() => setConfirmAction(null)}
                      disabled={anyLifecycleLoading}
                      className="rounded-xl border border-stone-300 bg-white px-4 py-2 text-sm font-medium text-stone-800 hover:bg-stone-100 disabled:opacity-60"
                    >
                      Cancel
                    </button>
                  </div>
                </div>
              ) : (
                <button
                  type="button"
                  onClick={() => {
                    clearFeedback();
                    setConfirmAction("deactivate");
                  }}
                  disabled={anyLifecycleLoading}
                  className="mt-4 rounded-xl border border-amber-300 bg-white px-4 py-2 text-sm font-medium text-amber-900 hover:bg-amber-100 disabled:opacity-60"
                >
                  Deactivate profile
                </button>
              )}
            </div>

            <div className="rounded-2xl border border-red-200 bg-red-50 p-5">
              <h4 className="text-base font-semibold text-red-950">Soft delete profile</h4>
              <p className="mt-2 text-sm text-red-900">
                Soft delete changes the profile status to <span className="font-medium">deleted</span>. Data is not hard-removed, but the profile becomes inactive and stays hidden from browse and interest flows.
              </p>

              {isDeleted ? (
                <div className="mt-4 rounded-xl border border-red-300 bg-white px-4 py-3 text-sm text-red-900">
                  This profile is already marked as deleted.
                </div>
              ) : confirmAction === "delete" ? (
                <div className="mt-4 rounded-2xl border border-red-300 bg-white p-4">
                  <p className="text-sm font-medium text-red-950">Confirm soft delete</p>
                  <p className="mt-2 text-sm text-red-900">
                    This marks the profile as deleted and makes it effectively inactive in the app. It will no longer appear in browse or interest flows.
                  </p>
                  <div className="mt-4 flex flex-wrap gap-3">
                    <button
                      type="button"
                      onClick={handleDelete}
                      disabled={anyLifecycleLoading}
                      className="rounded-xl bg-red-700 px-4 py-2 text-sm font-medium text-white hover:bg-red-800 disabled:opacity-60"
                    >
                      {deleteProfile.loading ? "Deleting..." : "Confirm delete"}
                    </button>
                    <button
                      type="button"
                      onClick={() => setConfirmAction(null)}
                      disabled={anyLifecycleLoading}
                      className="rounded-xl border border-stone-300 bg-white px-4 py-2 text-sm font-medium text-stone-800 hover:bg-stone-100 disabled:opacity-60"
                    >
                      Cancel
                    </button>
                  </div>
                </div>
              ) : (
                <button
                  type="button"
                  onClick={() => {
                    clearFeedback();
                    setConfirmAction("delete");
                  }}
                  disabled={anyLifecycleLoading}
                  className="mt-4 rounded-xl border border-red-300 bg-white px-4 py-2 text-sm font-medium text-red-900 hover:bg-red-100 disabled:opacity-60"
                >
                  Delete profile
                </button>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
