export type Preference = {
  id: string;
  user_id: string;
  profile_id: string;
  preferred_min_age: number | null;
  preferred_max_age: number | null;
  preferred_locations: string[];
  preferred_communities: string[];
  preferred_languages: string[];
  created_at: string;
  updated_at: string;
};

export type Profile = {
  id: string;
  user_id: string;
  full_name: string;
  age: number | null;
  gender: string | null;
  date_of_birth: string | null;
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
  profile_visibility: string;
  profile_status: string;
  verification_status: string;
  completion_percentage: number;
  created_at: string;
  updated_at: string;
  preferences: Preference | null;
};

export type ProfilePayload = {
  full_name: string;
  age: number | null;
  gender: string | null;
  date_of_birth: string | null;
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
  profile_visibility: string;
  preferences: {
    preferred_min_age: number | null;
    preferred_max_age: number | null;
    preferred_locations: string[];
    preferred_communities: string[];
    preferred_languages: string[];
  } | null;
};