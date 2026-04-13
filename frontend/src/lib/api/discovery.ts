import { apiGet } from "@/lib/api/client";
import type {
  DiscoverProfileListResponse,
  PublicProfile,
} from "@/types/discovery";

type BrowseQuery = {
  q?: string;
  min_age?: number | "";
  max_age?: number | "";
  community?: string;
  native_language?: string;
  city?: string;
  page?: number;
  size?: number;
};

function toQueryString(params: BrowseQuery) {
  const search = new URLSearchParams();

  Object.entries(params).forEach(([key, value]) => {
    if (value === undefined || value === null || value === "") return;
    search.set(key, String(value));
  });

  const query = search.toString();
  return query ? `?${query}` : "";
}

export function getBrowseProfiles(params: BrowseQuery) {
  return apiGet<DiscoverProfileListResponse>(`/profiles${toQueryString(params)}`);
}

export function getPublicProfile(profileId: string) {
  return apiGet<PublicProfile>(`/profiles/${profileId}`);
}