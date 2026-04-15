import type { InterestDirection, InterestStatus } from "@/types";

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
  status: InterestStatus;
  direction: InterestDirection;
  created_at: string;
};

export type InterestAction = "accept" | "decline";

export type InterestActionPayload = {
  action: InterestAction;
};

export type InterestActionResponse = {
  id: string;
  status: InterestStatus;
};
