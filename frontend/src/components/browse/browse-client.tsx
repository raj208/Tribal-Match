"use client";

import { useEffect, useState } from "react";

import { getBrowseProfiles } from "@/lib/api/discovery";
import type { DiscoverProfileCard } from "@/types/discovery";
import { ProfileCard } from "@/components/browse/profile-card";

export function BrowseClient() {
  const [items, setItems] = useState<DiscoverProfileCard[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);

  const [q, setQ] = useState("");
  const [minAge, setMinAge] = useState("");
  const [maxAge, setMaxAge] = useState("");
  const [community, setCommunity] = useState("");
  const [nativeLanguage, setNativeLanguage] = useState("");
  const [city, setCity] = useState("");

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  async function loadProfiles(nextPage = 1) {
    try {
      setLoading(true);
      const data = await getBrowseProfiles({
        q,
        min_age: minAge ? Number(minAge) : "",
        max_age: maxAge ? Number(maxAge) : "",
        community,
        native_language: nativeLanguage,
        city,
        page: nextPage,
        size: 12,
      });

      setItems(data.items);
      setTotal(data.total);
      setPage(data.page);
      setError("");
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Failed to load profiles";
      setError(msg);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadProfiles(1);
  }, []);

  function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    loadProfiles(1);
  }

  return (
    <div className="space-y-6">
      <form onSubmit={handleSubmit} className="card p-6">
        <h3 className="text-lg font-semibold text-stone-900">Browse filters</h3>

        <div className="mt-5 grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          <label className="text-sm xl:col-span-3">
            <span className="mb-2 block font-medium text-stone-700">Search</span>
            <input
              value={q}
              onChange={(e) => setQ(e.target.value)}
              className="w-full rounded-xl border border-stone-300 px-3 py-2 outline-none focus:border-stone-500"
              placeholder="Name, community, city, occupation..."
            />
          </label>

          <label className="text-sm">
            <span className="mb-2 block font-medium text-stone-700">Minimum age</span>
            <input
              value={minAge}
              onChange={(e) => setMinAge(e.target.value)}
              type="number"
              className="w-full rounded-xl border border-stone-300 px-3 py-2 outline-none focus:border-stone-500"
            />
          </label>

          <label className="text-sm">
            <span className="mb-2 block font-medium text-stone-700">Maximum age</span>
            <input
              value={maxAge}
              onChange={(e) => setMaxAge(e.target.value)}
              type="number"
              className="w-full rounded-xl border border-stone-300 px-3 py-2 outline-none focus:border-stone-500"
            />
          </label>

          <label className="text-sm">
            <span className="mb-2 block font-medium text-stone-700">Community</span>
            <input
              value={community}
              onChange={(e) => setCommunity(e.target.value)}
              className="w-full rounded-xl border border-stone-300 px-3 py-2 outline-none focus:border-stone-500"
              placeholder="Santhal"
            />
          </label>

          <label className="text-sm">
            <span className="mb-2 block font-medium text-stone-700">Native language</span>
            <input
              value={nativeLanguage}
              onChange={(e) => setNativeLanguage(e.target.value)}
              className="w-full rounded-xl border border-stone-300 px-3 py-2 outline-none focus:border-stone-500"
              placeholder="Santali"
            />
          </label>

          <label className="text-sm">
            <span className="mb-2 block font-medium text-stone-700">City</span>
            <input
              value={city}
              onChange={(e) => setCity(e.target.value)}
              className="w-full rounded-xl border border-stone-300 px-3 py-2 outline-none focus:border-stone-500"
              placeholder="Jamshedpur"
            />
          </label>
        </div>

        <div className="mt-5 flex flex-wrap gap-3">
          <button
            type="submit"
            className="rounded-xl bg-stone-900 px-5 py-3 text-sm font-medium text-white hover:bg-stone-800"
          >
            Apply filters
          </button>

          <button
            type="button"
            onClick={() => {
              setQ("");
              setMinAge("");
              setMaxAge("");
              setCommunity("");
              setNativeLanguage("");
              setCity("");
              setTimeout(() => loadProfiles(1), 0);
            }}
            className="rounded-xl border border-stone-300 bg-white px-5 py-3 text-sm font-medium text-stone-800 hover:bg-stone-100"
          >
            Reset
          </button>
        </div>
      </form>

      {error ? (
        <div className="card border-red-200 p-6">
          <p className="text-sm font-medium text-red-700">Failed to load profiles</p>
          <p className="mt-2 text-sm text-red-600">{error}</p>
        </div>
      ) : loading ? (
        <div className="card p-6 text-sm text-stone-600">Loading profiles...</div>
      ) : items.length === 0 ? (
        <div className="card p-6">
          <h3 className="text-lg font-semibold text-stone-900">No profiles found</h3>
          <p className="mt-2 text-sm text-stone-600">
            This can happen if there are no other published profiles yet, or if your filters are too strict.
          </p>
        </div>
      ) : (
        <>
          <div className="flex items-center justify-between gap-3">
            <p className="text-sm text-stone-600">
              Showing {items.length} of {total} profiles
            </p>
          </div>

          <div className="grid gap-5 md:grid-cols-2 xl:grid-cols-3">
            {items.map((profile) => (
              <ProfileCard key={profile.id} profile={profile} />
            ))}
          </div>

          <div className="flex items-center justify-between gap-3">
            <button
              type="button"
              disabled={page <= 1}
              onClick={() => loadProfiles(page - 1)}
              className="rounded-xl border border-stone-300 bg-white px-4 py-2 text-sm text-stone-800 hover:bg-stone-100 disabled:opacity-50"
            >
              Previous
            </button>

            <span className="text-sm text-stone-600">Page {page}</span>

            <button
              type="button"
              disabled={page * 12 >= total}
              onClick={() => loadProfiles(page + 1)}
              className="rounded-xl border border-stone-300 bg-white px-4 py-2 text-sm text-stone-800 hover:bg-stone-100 disabled:opacity-50"
            >
              Next
            </button>
          </div>
        </>
      )}
    </div>
  );
}