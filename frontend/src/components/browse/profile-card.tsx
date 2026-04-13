import Link from "next/link";

import type { DiscoverProfileCard } from "@/types/discovery";

export function ProfileCard({ profile }: { profile: DiscoverProfileCard }) {
  return (
    <div className="card overflow-hidden">
      <div className="aspect-[4/3] bg-stone-100">
        {profile.primary_photo_url ? (
          <img
            src={profile.primary_photo_url}
            alt={profile.full_name}
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
            <h3 className="text-lg font-semibold text-stone-900">
              {profile.full_name}
            </h3>
            <p className="mt-1 text-sm text-stone-600">
              {profile.age ?? "—"} • {profile.community_or_tribe ?? "—"}
            </p>
          </div>

          <span className="soft-badge bg-stone-100 text-stone-700">
            {profile.verification_status}
          </span>
        </div>

        <div className="mt-4 space-y-2 text-sm text-stone-700">
          <p>
            <span className="font-medium">Location:</span>{" "}
            {profile.location_city ?? "—"}
            {profile.location_state ? `, ${profile.location_state}` : ""}
          </p>
          <p>
            <span className="font-medium">Language:</span>{" "}
            {profile.native_language ?? "—"}
          </p>
          <p>
            <span className="font-medium">Occupation:</span>{" "}
            {profile.occupation ?? "—"}
          </p>
        </div>

        <p className="mt-4 line-clamp-3 text-sm text-stone-600">
          {profile.bio || "No bio added yet."}
        </p>

        <Link
          href={`/browse/${profile.id}`}
          className="mt-5 inline-flex rounded-xl bg-stone-900 px-4 py-2 text-sm font-medium text-white hover:bg-stone-800"
        >
          View profile
        </Link>
      </div>
    </div>
  );
}