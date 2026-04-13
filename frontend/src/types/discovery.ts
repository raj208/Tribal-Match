export type DiscoverProfileCard = {
  id: string;
  full_name: string;
  age: number | null;
  community_or_tribe: string | null;
  native_language: string | null;
  location_city: string | null;
  location_state: string | null;
  occupation: string | null;
  bio: string | null;
  verification_status: string;
  primary_photo_url: string | null;
};

export type DiscoverProfileListResponse = {
  items: DiscoverProfileCard[];
  total: number;
  page: number;
  size: number;
};

export type DiscoverProfilePhoto = {
  id: string;
  photo_url: string;
  is_primary: boolean;
  sort_order: number;
};

export type PublicProfile = {
  id: string;
  full_name: string;
  age: number | null;
  gender: string | null;
  community_or_tribe: string | null;
  subgroup_or_clan: string | null;
  native_language: string | null;
  other_languages: string[];
  location_city: string | null;
  location_state: string | null;
  location_country: string | null;
  occupation: string | null;
  education: string | null;
  bio: string | null;
  verification_status: string;
  photos: DiscoverProfilePhoto[];
  intro_video_url: string | null;
};