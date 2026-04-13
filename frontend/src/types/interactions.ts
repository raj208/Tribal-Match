export type ShortlistItem = {
  id: string;
  profile_id: string;
  full_name: string;
  age: number | null;
  community_or_tribe: string | null;
  native_language: string | null;
  location_city: string | null;
  occupation: string | null;
  bio: string | null;
  verification_status: string;
  primary_photo_url: string | null;
  created_at: string;
};

export type InterestItem = {
  id: string;
  profile_id: string;
  full_name: string;
  age: number | null;
  community_or_tribe: string | null;
  native_language: string | null;
  location_city: string | null;
  occupation: string | null;
  bio: string | null;
  verification_status: string;
  primary_photo_url: string | null;
  status: string;
  direction: string;
  created_at: string;
};