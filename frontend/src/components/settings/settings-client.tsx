"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import {
  useDeactivateProfile,
  useDeleteProfile,
  useSettingsSummary,
  useUpdateSettings,
} from "@/hooks/use-settings";
import type { ProfileStatus, VerificationStatus } from "@/types";
import type { ProfileVisibility } from "@/types/settings";

type ConfirmAction = "deactivate" | "delete" | null;

type StatusMeta = {
  label: string;
  badgeClass: string;
  helper: string;
};

const DEFAULT_BADGE_CLASS = "bg-stone-100 text-stone-700";

const PROFILE_STATUS_META: Record<ProfileStatus, StatusMeta> = {
  draft: {
    label: "Draft",
    badgeClass: "bg-amber-100 text-amber-700",
    helper: "Your profile exists, but it is not fully live in the app yet.",
  },
  published: {
    label: "Published",
    badgeClass: "bg-green-100 text-green-700",
    helper: "Published profiles can appear in discovery and accept profile-based interactions.",
  },
  hidden: {
    label: "Hidden",
    badgeClass: DEFAULT_BADGE_CLASS,
    helper: "This profile is hidden from normal browse visibility.",
  },
  deactivated: {
    label: "Deactivated",
    badgeClass: "bg-amber-100 text-amber-800",
    helper: "The profile remains stored, but it no longer appears in browse or interest flows.",
  },
  deleted: {
    label: "Deleted",
    badgeClass: "bg-red-100 text-red-700",
    helper: "This is a soft-deleted state. Data stays stored, but the profile is inactive in the app.",
  },
};

const VERIFICATION_STATUS_META: Record<VerificationStatus, StatusMeta> = {
  not_started: {
    label: "Not Started",
    badgeClass: DEFAULT_BADGE_CLASS,
    helper: "Verification has not started yet.",
  },
  uploaded: {
    label: "Uploaded",
    badgeClass: "bg-amber-100 text-amber-700",
    helper: "Verification assets are uploaded and awaiting the next review step.",
  },
  under_review: {
    label: "Under Review",
    badgeClass: "bg-amber-100 text-amber-700",
    helper: "Verification is currently being reviewed.",
  },
  approved: {
    label: "Approved",
    badgeClass: "bg-green-100 text-green-700",
    helper: "Verification is approved.",
  },
  rejected: {
    label: "Rejected",
    badgeClass: "bg-red-100 text-red-700",
    helper: "Verification needs attention before it can be approved.",
  },
};

function toSafePercent(value: number | null | undefined) {
  return typeof value === "number" && Number.isFinite(value)
    ? Math.max(0, Math.min(100, Math.round(value)))
    : 0;
}

function normalizeVisibility(value: string | null | undefined): ProfileVisibility {
  return value === "private" ? "private" : "public";
}

function getProfileStatusMeta(profileExists: boolean, status: ProfileStatus | null): StatusMeta {
  if (!profileExists) {
    return {
      label: "Not Created",
      badgeClass: DEFAULT_BADGE_CLASS,
      helper: "Create a profile first to unlock privacy controls and lifecycle actions.",
    };
  }

  if (status) {
    return PROFILE_STATUS_META[status];
  }

  return {
    label: "Unknown",
    badgeClass: DEFAULT_BADGE_CLASS,
    helper: "Profile status is currently unavailable.",
  };
}

function getVerificationStatusMeta(
  profileExists: boolean,
  status: VerificationStatus | null
): StatusMeta {
  if (!profileExists) {
    return {
      label: "Pending Profile",
      badgeClass: DEFAULT_BADGE_CLASS,
      helper: "Verification becomes relevant after your profile exists.",
    };
  }

  if (status) {
    return VERIFICATION_STATUS_META[status];
  }

  return {
    label: "Unknown",
    badgeClass: DEFAULT_BADGE_CLASS,
    helper: "Verification status is currently unavailable.",
  };
}

function getVisibilityLabel(profileExists: boolean, visibility: string | null | undefined) {
  if (!profileExists || !visibility) {
    return "Not Set";
  }

  return visibility === "private" ? "Private" : "Public";
}

function getLifecycleSummary(profileExists: boolean, status: ProfileStatus | null) {
  if (!profileExists) {
    return "No profile exists yet, so there is nothing to deactivate or delete.";
  }

  if (status === "deactivated") {
    return "You remain signed in, but the profile is hidden from browse and profile-based interactions because discovery only includes published profiles.";
  }

  if (status === "deleted") {
    return "You remain signed in, but the profile is soft-deleted and inactive in the app because discovery only includes published profiles.";
  }

  return "Deactivate hides the profile without deleting it. Delete marks it as deleted without hard-removing stored data.";
}

export function SettingsClient() {
  const {
    settings,
    loading,
    refreshing,
    error,
    reload,
    replaceSettings,
    mergeSettings,
  } = useSettingsSummary();
  const updateSettings = useUpdateSettings();
  const deactivateProfile = useDeactivateProfile();
  const deleteProfile = useDeleteProfile();

  const [profileVisibility, setProfileVisibility] = useState<ProfileVisibility>("public");
  const [notice, setNotice] = useState("");
  const [confirmAction, setConfirmAction] = useState<ConfirmAction>(null);
  const [deleteConfirmationText, setDeleteConfirmationText] = useState("");

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
  const visibilityDisabled =
    !profileExists || updateSettings.loading || anyLifecycleLoading || isDeactivated || isDeleted;
  const deleteConfirmationReady = deleteConfirmationText.trim().toUpperCase() === "DELETE";
  const profileStatusMeta = getProfileStatusMeta(profileExists, profileStatus);
  const verificationStatusMeta = getVerificationStatusMeta(profileExists, verificationStatus);
  const lifecycleError = deactivateProfile.error || deleteProfile.error;
  const refreshError = settings ? error : "";
  const loadError = !settings ? error : "";
  const currentVisibilityLabel = getVisibilityLabel(profileExists, settings?.profile_visibility);

  useEffect(() => {
    if (!profileExists || isDeleted || isDeactivated) {
      setConfirmAction(null);
      setDeleteConfirmationText("");
    }
  }, [isDeactivated, isDeleted, profileExists]);

  function clearFeedback() {
    setNotice("");
    updateSettings.reset();
    deactivateProfile.reset();
    deleteProfile.reset();
  }

  function openConfirmation(action: ConfirmAction) {
    clearFeedback();
    setConfirmAction(action);
    if (action !== "delete") {
      setDeleteConfirmationText("");
    }
  }

  async function handleSaveVisibility(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    clearFeedback();

    const currentVisibility = normalizeVisibility(settings?.profile_visibility);
    if (profileVisibility === currentVisibility) {
      setNotice(`Profile visibility is already set to ${currentVisibilityLabel.toLowerCase()}.`);
      return;
    }

    const result = await updateSettings.mutate({ profile_visibility: profileVisibility });
    if (!result) return;

    replaceSettings(result);
    setProfileVisibility(normalizeVisibility(result.profile_visibility));
    setNotice("Profile visibility updated successfully.");
  }

  async function handleDeactivate() {
    clearFeedback();

    const result = await deactivateProfile.mutate();
    if (!result) return;

    mergeSettings({ profile_status: result.profile_status });
    setConfirmAction(null);
    setNotice(
      `${result.message} You remain signed in, and your profile is now hidden from browse and profile-based interaction flows.`
    );
  }

  async function handleDelete() {
    clearFeedback();

    const result = await deleteProfile.mutate();
    if (!result) return;

    mergeSettings({ profile_status: result.profile_status });
    setConfirmAction(null);
    setDeleteConfirmationText("");
    setNotice(
      `${result.message} You remain signed in, and your profile is now inactive in the app until a future lifecycle change is supported.`
    );
  }

  if (loading && !settings) {
    return (
      <div className="space-y-5">
        <div className="card p-6">
          <div className="animate-pulse space-y-4">
            <div className="h-4 w-32 rounded bg-stone-200" />
            <div className="h-8 w-72 rounded bg-stone-200" />
            <div className="h-4 w-full rounded bg-stone-100" />
          </div>
        </div>

        <div className="grid gap-5 lg:grid-cols-2">
          <div className="card p-6">
            <div className="animate-pulse space-y-4">
              <div className="h-4 w-28 rounded bg-stone-200" />
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
              <div className="h-4 w-full rounded bg-stone-100" />
              <div className="h-10 w-40 rounded-xl bg-stone-200" />
            </div>
          </div>
        </div>

        <div className="card p-6">
          <div className="animate-pulse space-y-4">
            <div className="h-4 w-40 rounded bg-stone-200" />
            <div className="grid gap-4 md:grid-cols-2">
              <div className="h-48 rounded-2xl bg-stone-100" />
              <div className="h-56 rounded-2xl bg-stone-100" />
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (!settings) {
    const likelyAuthIssue = loadError.toLowerCase().includes("authentication required");

    return (
      <div className="card border-red-200 p-6">
        <p className="text-sm font-medium text-red-700">Failed to load settings</p>
        <p className="mt-2 text-sm text-red-600">
          {loadError || "Settings data is unavailable."}
        </p>
        <p className="mt-3 text-sm text-stone-600">
          {likelyAuthIssue
            ? "Your session may need refreshing. If retry does not help, use the existing logout flow and sign in again."
            : "The page could not reach the backend-backed settings summary right now."}
        </p>
        <div className="mt-4 flex flex-wrap gap-3">
          <button
            type="button"
            onClick={reload}
            className="rounded-xl bg-stone-900 px-4 py-2 text-sm font-medium text-white hover:bg-stone-800"
          >
            Retry
          </button>
          <Link
            href="/dashboard"
            className="rounded-xl border border-stone-300 bg-white px-4 py-2 text-sm font-medium text-stone-800 hover:bg-stone-100"
          >
            Return to dashboard
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-5">
      {refreshing ? (
        <div className="rounded-xl border border-stone-200 bg-stone-100 px-4 py-3 text-sm text-stone-700">
          Refreshing the latest settings state...
        </div>
      ) : null}

      {refreshError ? (
        <div className="rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900">
          <p className="font-medium">Showing the last known settings state</p>
          <p className="mt-1">{refreshError}</p>
          <button
            type="button"
            onClick={reload}
            className="mt-3 rounded-xl border border-amber-300 bg-white px-4 py-2 text-sm font-medium text-amber-900 hover:bg-amber-100"
          >
            Try again
          </button>
        </div>
      ) : null}

      {notice ? (
        <div className="rounded-xl border border-green-200 bg-green-50 px-4 py-3 text-sm text-green-700">
          {notice}
        </div>
      ) : null}

      {!profileExists ? (
        <div className="rounded-2xl border border-amber-200 bg-amber-50 p-5">
          <p className="text-sm font-semibold text-amber-950">No profile created yet</p>
          <p className="mt-2 text-sm text-amber-900">
            Backend-backed settings are intentionally minimal right now. Create your profile first to manage privacy and lifecycle actions from this page.
          </p>
          <div className="mt-4 flex flex-wrap gap-3">
            <Link
              href="/profile/edit"
              className="rounded-xl bg-stone-900 px-4 py-2 text-sm font-medium text-white hover:bg-stone-800"
            >
              Create profile
            </Link>
            <Link
              href="/dashboard"
              className="rounded-xl border border-stone-300 bg-white px-4 py-2 text-sm font-medium text-stone-800 hover:bg-stone-100"
            >
              Return to dashboard
            </Link>
          </div>
        </div>
      ) : null}

      {(isDeactivated || isDeleted) && profileExists ? (
        <div className="rounded-2xl border border-stone-200 bg-stone-50 p-5">
          <p className="text-sm font-semibold text-stone-900">
            {isDeleted ? "Profile deleted" : "Profile deactivated"}
          </p>
          <p className="mt-2 text-sm text-stone-700">
            You remain signed in because authentication is separate from profile lifecycle in the current app. Your profile is hidden from browse and profile-based interaction flows, but the rest of the authenticated shell still works normally.
          </p>
          <div className="mt-4 flex flex-wrap gap-3">
            <Link
              href="/dashboard"
              className="rounded-xl bg-stone-900 px-4 py-2 text-sm font-medium text-white hover:bg-stone-800"
            >
              Go to dashboard
            </Link>
            <button
              type="button"
              onClick={reload}
              disabled={refreshing}
              className="rounded-xl border border-stone-300 bg-white px-4 py-2 text-sm font-medium text-stone-800 hover:bg-stone-100 disabled:opacity-60"
            >
              {refreshing ? "Refreshing..." : "Refresh status"}
            </button>
          </div>
        </div>
      ) : null}

      <div className="grid gap-5 lg:grid-cols-2">
        <div className="card p-6">
          <div className="flex items-start justify-between gap-4">
            <div>
              <p className="text-sm text-stone-500">Account summary</p>
              <h3 className="mt-2 text-lg font-semibold text-stone-900">
                {profileExists ? "Current backend-backed settings status" : "Profile setup pending"}
              </h3>
            </div>

            <span
              className={`soft-badge ${
                profileExists ? "bg-green-100 text-green-700" : "bg-stone-100 text-stone-700"
              }`}
            >
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
                <span className={`soft-badge ${profileStatusMeta.badgeClass}`}>
                  {profileStatusMeta.label}
                </span>
              </div>
              <p className="mt-2 text-xs text-stone-600">{profileStatusMeta.helper}</p>
            </div>

            <div className="rounded-2xl border border-stone-200 p-4">
              <p className="text-sm text-stone-500">Verification status</p>
              <div className="mt-2">
                <span className={`soft-badge ${verificationStatusMeta.badgeClass}`}>
                  {verificationStatusMeta.label}
                </span>
              </div>
              <p className="mt-2 text-xs text-stone-600">{verificationStatusMeta.helper}</p>
            </div>

            <div className="rounded-2xl border border-stone-200 p-4">
              <p className="text-sm text-stone-500">Completion</p>
              <p className="mt-2 text-2xl font-semibold text-stone-900">
                {profileExists ? `${completionPercentage}%` : "Not started"}
              </p>
              <p className="mt-2 text-xs text-stone-600">
                {profileExists
                  ? "This percentage comes directly from the backend profile summary."
                  : "Completion becomes available after your profile is created."}
              </p>
            </div>
          </div>

          {profileExists ? (
            <div className="mt-5">
              <div className="h-2 rounded-full bg-stone-200">
                <div
                  className="h-2 rounded-full bg-stone-900 transition-all"
                  style={{ width: completionWidth }}
                />
              </div>
            </div>
          ) : null}

          <p className="mt-4 text-sm text-stone-600">
            {getLifecycleSummary(profileExists, profileStatus)}
          </p>
        </div>

        <div className="card p-6">
          <div className="flex items-start justify-between gap-4">
            <div>
              <p className="text-sm text-stone-500">Privacy</p>
              <h3 className="mt-2 text-lg font-semibold text-stone-900">
                Control how your profile is exposed
              </h3>
            </div>

            <span className="soft-badge bg-stone-100 text-stone-700">{currentVisibilityLabel}</span>
          </div>

          {!profileExists ? (
            <div className="mt-5 rounded-2xl border border-amber-200 bg-amber-50 p-4">
              <p className="text-sm font-medium text-amber-900">Create a profile to manage privacy.</p>
              <p className="mt-2 text-sm text-amber-800">
                The backend only stores settings against an existing profile, so profile visibility becomes available after creation.
              </p>
            </div>
          ) : isDeleted || isDeactivated ? (
            <div className="mt-5 rounded-2xl border border-stone-200 bg-stone-50 p-4">
              <p className="text-sm font-medium text-stone-900">Visibility is currently read-only</p>
              <p className="mt-2 text-sm text-stone-700">
                This profile is already {isDeleted ? "deleted" : "deactivated"}, so visibility no longer affects browse. The stored value remains <span className="font-medium">{currentVisibilityLabel.toLowerCase()}</span>.
              </p>
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
                  disabled={visibilityDisabled}
                  className="w-full rounded-xl border border-stone-300 px-3 py-2 outline-none focus:border-stone-500 disabled:bg-stone-100 disabled:text-stone-500"
                >
                  <option value="public">public</option>
                  <option value="private">private</option>
                </select>
              </label>

              <p className="text-sm text-stone-600">
                Choose whether the stored profile visibility is public or private. This setting only matters while the profile is active in the app.
              </p>

              <button
                type="submit"
                disabled={visibilityDisabled || profileVisibility === normalizeVisibility(settings.profile_visibility)}
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
          <h3 className="mt-2 text-lg font-semibold text-stone-900">
            Deactivate or soft-delete your profile
          </h3>
          <p className="mt-2 text-sm text-stone-600">
            These actions do not log you out. They only change the backend lifecycle status stored for your current profile.
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
                Deactivation keeps the profile record in place but changes its status to <span className="font-medium">deactivated</span>. Discovery only includes published profiles, so this hides the profile from browse and profile-based interactions.
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
                    You will stay signed in. Your profile will stop appearing in browse and will no longer be a valid target for profile-based interactions.
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
                  onClick={() => openConfirmation("deactivate")}
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
                Soft delete changes the profile status to <span className="font-medium">deleted</span>. It does not hard-remove related rows, but it makes the profile effectively inactive in the app.
              </p>

              {isDeleted ? (
                <div className="mt-4 rounded-xl border border-red-300 bg-white px-4 py-3 text-sm text-red-900">
                  This profile is already marked as deleted.
                </div>
              ) : confirmAction === "delete" ? (
                <div className="mt-4 rounded-2xl border border-red-300 bg-white p-4">
                  <p className="text-sm font-medium text-red-950">Confirm soft delete</p>
                  <p className="mt-2 text-sm text-red-900">
                    You will stay signed in, but the profile will become inactive in the app and hidden from browse. Type <span className="font-medium">DELETE</span> below to enable the final action.
                  </p>

                  <label className="mt-4 block text-sm">
                    <span className="mb-2 block font-medium text-red-950">Type DELETE to confirm</span>
                    <input
                      value={deleteConfirmationText}
                      onChange={(event) => setDeleteConfirmationText(event.target.value)}
                      disabled={anyLifecycleLoading}
                      className="w-full rounded-xl border border-red-200 px-3 py-2 outline-none focus:border-red-400 disabled:bg-stone-100 disabled:text-stone-500"
                      placeholder="DELETE"
                    />
                  </label>

                  <div className="mt-4 flex flex-wrap gap-3">
                    <button
                      type="button"
                      onClick={handleDelete}
                      disabled={anyLifecycleLoading || !deleteConfirmationReady}
                      className="rounded-xl bg-red-700 px-4 py-2 text-sm font-medium text-white hover:bg-red-800 disabled:opacity-60"
                    >
                      {deleteProfile.loading ? "Deleting..." : "Confirm delete"}
                    </button>
                    <button
                      type="button"
                      onClick={() => {
                        setConfirmAction(null);
                        setDeleteConfirmationText("");
                      }}
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
                  onClick={() => openConfirmation("delete")}
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
