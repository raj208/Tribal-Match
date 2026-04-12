import Link from "next/link";

import { ProfileView } from "@/components/profile/profile-view";
import { PageShell } from "@/components/shared/page-shell";

export default function ProfilePage() {
  return (
    <PageShell
      title="My Profile"
      description="This page shows your current backend profile data, including your saved preferences."
      action={
        <div className="flex flex-wrap gap-2">
          <Link
            href="/profile/edit"
            className="rounded-xl bg-stone-900 px-4 py-2 text-sm font-medium text-white hover:bg-stone-800"
          >
            Edit profile
          </Link>

          <Link
            href="/verification"
            className="rounded-xl border border-stone-300 bg-white px-4 py-2 text-sm font-medium text-stone-800 hover:bg-stone-100"
          >
            Manage media
          </Link>
        </div>
      }
    >
      <ProfileView />
    </PageShell>
  );
}