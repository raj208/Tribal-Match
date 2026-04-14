"use client";

import Link from "next/link";

import { PageShell } from "@/components/shared/page-shell";
import { useAuth } from "@/hooks/use-auth";
import { useDashboardSummary } from "@/hooks/use-dashboard-summary";
import { appRoutes } from "@/lib/constants/routes";

type GuidanceItem = {
  title: string;
  body: string;
  href: string;
  label: string;
  tone: string;
};

function normalizeName(value: string | null | undefined) {
  if (!value) return "there";
  return value.replace(/[._-]+/g, " ").replace(/\b\w/g, (char) => char.toUpperCase());
}

function formatLabel(value: string | null | undefined) {
  if (!value) return "Not started";
  return value
    .replace(/_/g, " ")
    .replace(/\b\w/g, (char) => char.toUpperCase());
}

function formatPercent(value: number) {
  return `${Math.max(0, Math.min(100, value))}%`;
}

function toSafeCount(value: number | null | undefined, max?: number) {
  const count = typeof value === "number" && Number.isFinite(value) ? Math.max(0, Math.floor(value)) : 0;
  return typeof max === "number" ? Math.min(max, count) : count;
}

function toSafePercent(value: number | null | undefined) {
  return typeof value === "number" && Number.isFinite(value)
    ? Math.max(0, Math.min(100, Math.round(value)))
    : 0;
}

function toSafeBoolean(value: boolean | null | undefined) {
  return value === true;
}

function safeHref(href: string) {
  return appRoutes.includes(href) ? href : "/dashboard";
}

function getProfileStatusBadgeClass(status: string | null) {
  if (!status) return "bg-stone-100 text-stone-700";
  if (status === "published") return "bg-green-100 text-green-700";
  if (status === "draft") return "bg-amber-100 text-amber-700";
  return "bg-stone-100 text-stone-700";
}

function getVerificationBadgeClass(status: string | null) {
  if (!status || status === "not_started") return "bg-stone-100 text-stone-700";
  if (status === "approved") return "bg-green-100 text-green-700";
  if (status === "rejected") return "bg-red-100 text-red-700";
  return "bg-amber-100 text-amber-700";
}

export default function DashboardPage() {
  const { user } = useAuth();
  const { summary, loading, error, reload } = useDashboardSummary();

  const welcomeName = normalizeName(user?.email?.split("@")[0]);

  if (loading) {
    return (
      <PageShell
        title="Dashboard"
        description="Track your profile readiness, verification progress, and recent activity from one place."
      >
        <div className="grid gap-5 lg:grid-cols-2">
          <div className="card p-6">
            <div className="animate-pulse space-y-4">
              <div className="h-4 w-28 rounded bg-stone-200" />
              <div className="h-8 w-3/4 rounded bg-stone-200" />
              <div className="grid gap-4 sm:grid-cols-2">
                <div className="h-24 rounded-2xl bg-stone-100" />
                <div className="h-24 rounded-2xl bg-stone-100" />
              </div>
              <div className="h-2 rounded-full bg-stone-100" />
              <div className="h-10 w-32 rounded-xl bg-stone-200" />
            </div>
          </div>

          <div className="card p-6">
            <div className="animate-pulse space-y-4">
              <div className="h-4 w-36 rounded bg-stone-200" />
              <div className="h-8 w-2/3 rounded bg-stone-200" />
              <div className="grid gap-4 sm:grid-cols-2">
                <div className="h-24 rounded-2xl bg-stone-100" />
                <div className="h-24 rounded-2xl bg-stone-100" />
              </div>
              <div className="h-10 w-48 rounded-xl bg-stone-200" />
            </div>
          </div>
        </div>

        <div className="card p-6">
          <div className="animate-pulse space-y-4">
            <div className="h-4 w-28 rounded bg-stone-200" />
            <div className="grid gap-4 md:grid-cols-3">
              <div className="h-24 rounded-2xl bg-stone-100" />
              <div className="h-24 rounded-2xl bg-stone-100" />
              <div className="h-24 rounded-2xl bg-stone-100" />
            </div>
          </div>
        </div>
      </PageShell>
    );
  }

  if (error || !summary) {
    return (
      <PageShell
        title="Dashboard"
        description="Track your profile readiness, verification progress, and recent activity from one place."
      >
        <div className="card border-red-200 p-6">
          <p className="text-sm font-medium text-red-700">Failed to load dashboard</p>
          <p className="mt-2 text-sm text-red-600">{error || "Dashboard data is unavailable."}</p>
          <div className="mt-4 flex flex-wrap gap-3">
            <button
              type="button"
              onClick={reload}
              className="rounded-xl bg-stone-900 px-4 py-2 text-sm font-medium text-white hover:bg-stone-800"
            >
              Retry
            </button>
            <Link
              href={safeHref("/browse")}
              className="rounded-xl border border-stone-300 bg-white px-4 py-2 text-sm font-medium text-stone-800 hover:bg-stone-100"
            >
              Browse Profiles
            </Link>
          </div>
        </div>
      </PageShell>
    );
  }

  const profileExists = summary.profile_exists === true;
  const profileStatus = profileExists ? summary.profile_status : null;
  const verificationStatus = profileExists ? summary.verification_status : (summary.verification_status ?? "not_started");
  const completionPercentage = toSafePercent(summary.completion_percentage);
  const photoCount = toSafeCount(summary.photo_count, 6);
  const hasIntroVideo = toSafeBoolean(summary.has_intro_video);
  const shortlistCount = toSafeCount(summary.shortlist_count);
  const sentInterestsCount = toSafeCount(summary.sent_interests_count);
  const receivedInterestsCount = toSafeCount(summary.received_interests_count);
  const profileActionLabel = profileExists ? "Edit Profile" : "Create Profile";
  const completionWidth = `${completionPercentage}%`;

  const guidanceItems: GuidanceItem[] = [];

  if (!profileExists) {
    guidanceItems.push({
      title: "Create your profile to get started",
      body: "Add your basic details and preferences so your dashboard and matching journey can begin.",
      href: safeHref("/profile/edit"),
      label: "Create Profile",
      tone: "border-amber-200 bg-amber-50 text-amber-900",
    });
  }

  if (profileExists && (profileStatus === "draft" || completionPercentage < 100)) {
    guidanceItems.push({
      title: "Complete your profile for better visibility",
      body: `Your profile is ${formatPercent(completionPercentage)} complete. Add the missing details and publish when ready.`,
      href: safeHref("/profile/edit"),
      label: "Continue Profile",
      tone: "border-stone-200 bg-stone-50 text-stone-900",
    });
  }

  if (photoCount === 0) {
    guidanceItems.push({
      title: "Add profile photos",
      body: "Profiles with photos are easier to review. You can upload up to 6 photos.",
      href: safeHref("/verification"),
      label: "Manage Photos",
      tone: "border-stone-200 bg-stone-50 text-stone-900",
    });
  }

  if (!hasIntroVideo) {
    guidanceItems.push({
      title: "Upload your intro video",
      body: "A short intro video supports verification and makes your profile more complete.",
      href: safeHref("/verification"),
      label: "Upload Video",
      tone: "border-stone-200 bg-stone-50 text-stone-900",
    });
  }

  const quickActions = [
    {
      href: safeHref("/browse"),
      title: "Browse Profiles",
      description: "Explore published profiles available in discovery.",
    },
    {
      href: safeHref("/shortlisted"),
      title: "View Shortlisted",
      description: "Review the profiles you have already saved.",
    },
    {
      href: safeHref("/interests"),
      title: "View Interests",
      description: "See the interests you sent and the ones you received.",
    },
    {
      href: safeHref("/profile/edit"),
      title: "Edit Profile",
      description: "Update your details, preferences, and profile completion.",
    },
    {
      href: safeHref("/verification"),
      title: "Manage Verification",
      description: "Upload photos and manage your intro video verification.",
    },
  ];

  return (
    <PageShell
      title="Dashboard"
      description={`Welcome back, ${welcomeName}. Keep track of your profile, verification progress, and recent activity here.`}
      action={
        <Link
          href={safeHref("/browse")}
          className="rounded-xl bg-stone-900 px-4 py-2 text-sm font-medium text-white hover:bg-stone-800"
        >
          Browse Profiles
        </Link>
      }
    >
      {!profileExists ? (
        <div className="rounded-2xl border border-amber-200 bg-amber-50 p-5">
          <p className="text-sm font-semibold text-amber-900">Your profile has not been created yet</p>
          <p className="mt-2 text-sm text-amber-800">
            Create your profile first so you can upload media, appear in discovery, and manage your matchmaking activity.
          </p>
          <Link
            href={safeHref("/profile/edit")}
            className="mt-4 inline-flex rounded-xl bg-stone-900 px-4 py-2 text-sm font-medium text-white hover:bg-stone-800"
          >
            Create Profile
          </Link>
        </div>
      ) : null}

      <div className="grid gap-5 lg:grid-cols-2">
        <div className="card p-6">
          <div className="flex items-start justify-between gap-4">
            <div>
              <p className="text-sm text-stone-500">Profile summary</p>
              <h3 className="mt-2 text-lg font-semibold text-stone-900">
                {profileExists ? "Your profile is active in the app" : "Profile setup pending"}
              </h3>
            </div>

            <span
              className={`soft-badge ${profileExists ? "bg-green-100 text-green-700" : "bg-stone-100 text-stone-700"}`}
            >
              {profileExists ? "Profile created" : "No profile yet"}
            </span>
          </div>

          <div className="mt-5 grid gap-4 sm:grid-cols-2">
            <div className="rounded-2xl border border-stone-200 p-4">
              <p className="text-sm text-stone-500">Profile status</p>
              <div className="mt-2 flex items-center gap-2">
                <span className={`soft-badge ${getProfileStatusBadgeClass(profileStatus)}`}>
                  {profileStatus ? formatLabel(profileStatus) : "Not created"}
                </span>
              </div>
            </div>

            <div className="rounded-2xl border border-stone-200 p-4">
              <p className="text-sm text-stone-500">Completion</p>
              <p className="mt-2 text-2xl font-semibold text-stone-900">
                {formatPercent(completionPercentage)}
              </p>
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

          <div className="mt-5">
            <Link
              href={safeHref("/profile/edit")}
              className="inline-flex rounded-xl bg-stone-900 px-4 py-2 text-sm font-medium text-white hover:bg-stone-800"
            >
              {profileActionLabel}
            </Link>
          </div>
        </div>

        <div className="card p-6">
          <div className="flex items-start justify-between gap-4">
            <div>
              <p className="text-sm text-stone-500">Verification & media</p>
              <h3 className="mt-2 text-lg font-semibold text-stone-900">
                Keep your profile trusted and complete
              </h3>
            </div>

            <span className={`soft-badge ${getVerificationBadgeClass(verificationStatus)}`}>
              {formatLabel(verificationStatus)}
            </span>
          </div>

          <div className="mt-5 grid gap-4 sm:grid-cols-2">
            <div className="rounded-2xl border border-stone-200 p-4">
              <p className="text-sm text-stone-500">Photos</p>
              <p className="mt-2 text-2xl font-semibold text-stone-900">
                {photoCount}/6
              </p>
              <p className="mt-1 text-sm text-stone-600">
                {photoCount > 0 ? "Photos uploaded" : "No photos uploaded yet"}
              </p>
            </div>

            <div className="rounded-2xl border border-stone-200 p-4">
              <p className="text-sm text-stone-500">Intro video</p>
              <p className="mt-2 text-2xl font-semibold text-stone-900">
                {hasIntroVideo ? "Uploaded" : "Missing"}
              </p>
              <p className="mt-1 text-sm text-stone-600">
                {hasIntroVideo
                  ? "Your intro video is on file."
                  : "Upload a video to strengthen your profile."}
              </p>
            </div>
          </div>

          <div className="mt-5">
            <Link
              href={safeHref("/verification")}
              className="inline-flex rounded-xl border border-stone-300 bg-white px-4 py-2 text-sm font-medium text-stone-800 hover:bg-stone-100"
            >
              Manage Verification & Media
            </Link>
          </div>
        </div>
      </div>

      <div className="card p-6">
        <div className="flex items-center justify-between gap-4">
          <div>
            <p className="text-sm text-stone-500">Activity stats</p>
            <h3 className="mt-2 text-lg font-semibold text-stone-900">Your recent activity at a glance</h3>
          </div>
        </div>

        <div className="mt-5 grid gap-4 md:grid-cols-3">
          <div className="rounded-2xl border border-stone-200 p-5">
            <p className="text-sm text-stone-500">Shortlisted</p>
            <p className="mt-2 text-3xl font-semibold text-stone-900">{shortlistCount}</p>
          </div>

          <div className="rounded-2xl border border-stone-200 p-5">
            <p className="text-sm text-stone-500">Sent interests</p>
            <p className="mt-2 text-3xl font-semibold text-stone-900">{sentInterestsCount}</p>
          </div>

          <div className="rounded-2xl border border-stone-200 p-5">
            <p className="text-sm text-stone-500">Received interests</p>
            <p className="mt-2 text-3xl font-semibold text-stone-900">{receivedInterestsCount}</p>
          </div>
        </div>
      </div>

      <div className="card p-6">
        <div>
          <p className="text-sm text-stone-500">Quick actions</p>
          <h3 className="mt-2 text-lg font-semibold text-stone-900">Move to the next important task</h3>
        </div>

        <div className="mt-5 grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {quickActions.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className="rounded-2xl border border-stone-200 p-4 transition hover:border-stone-300 hover:bg-stone-50"
            >
              <p className="text-base font-semibold text-stone-900">{item.title}</p>
              <p className="mt-2 text-sm text-stone-600">{item.description}</p>
            </Link>
          ))}
        </div>
      </div>

      {guidanceItems.length > 0 ? (
        <div className="card p-6">
          <div>
            <p className="text-sm text-stone-500">Helpful next steps</p>
            <h3 className="mt-2 text-lg font-semibold text-stone-900">
              A few things will improve your dashboard readiness
            </h3>
          </div>

          <div className="mt-5 grid gap-4 lg:grid-cols-2">
            {guidanceItems.map((item) => (
              <div key={item.title} className={`rounded-2xl border p-5 ${item.tone}`}>
                <h4 className="text-base font-semibold">{item.title}</h4>
                <p className="mt-2 text-sm opacity-90">{item.body}</p>
                <Link
                  href={item.href}
                  className="mt-4 inline-flex rounded-xl bg-stone-900 px-4 py-2 text-sm font-medium text-white hover:bg-stone-800"
                >
                  {item.label}
                </Link>
              </div>
            ))}
          </div>
        </div>
      ) : null}
    </PageShell>
  );
}
