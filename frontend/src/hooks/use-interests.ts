"use client";

import { useEffect, useState } from "react";

import { useAuth } from "@/hooks/use-auth";
import {
  actOnInterest,
  listReceivedInterests,
  listSentInterests,
} from "@/lib/api/interests";
import type {
  InterestAction,
  InterestActionResponse,
  InterestItem,
} from "@/types/interactions";

type InterestListQueryResult = {
  interests: InterestItem[];
  loading: boolean;
  error: string;
  reload: () => void;
};

type InterestActionMutationResult = {
  mutate: (interestId: string, action: InterestAction) => Promise<InterestActionResponse | null>;
  loading: boolean;
  error: string;
  reset: () => void;
};

type InterestListFetcher = () => Promise<InterestItem[]>;

function toApiErrorMessage(error: unknown, fallback: string): string {
  if (!(error instanceof Error) || !error.message) {
    return fallback;
  }

  try {
    const parsed = JSON.parse(error.message) as { detail?: unknown };
    if (typeof parsed.detail === "string" && parsed.detail.trim()) {
      return parsed.detail;
    }
  } catch {
    return error.message;
  }

  return error.message;
}

function useInterestList(
  fetcher: InterestListFetcher,
  fallbackMessage: string
): InterestListQueryResult {
  const { user, loading: authLoading } = useAuth();
  const [interests, setInterests] = useState<InterestItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [reloadKey, setReloadKey] = useState(0);

  useEffect(() => {
    if (authLoading) {
      return;
    }

    if (!user) {
      setInterests([]);
      setError("");
      setLoading(false);
      return;
    }

    let active = true;
    setLoading(true);

    fetcher()
      .then((data) => {
        if (!active) return;
        setInterests(data);
        setError("");
      })
      .catch((err: unknown) => {
        if (!active) return;
        setInterests([]);
        setError(toApiErrorMessage(err, fallbackMessage));
      })
      .finally(() => {
        if (!active) return;
        setLoading(false);
      });

    return () => {
      active = false;
    };
  }, [authLoading, fetcher, fallbackMessage, reloadKey, user]);

  return {
    interests,
    loading,
    error,
    reload: () => setReloadKey((value) => value + 1),
  };
}

export function useSentInterests(): InterestListQueryResult {
  return useInterestList(listSentInterests, "Unable to load sent interests");
}

export function useReceivedInterests(): InterestListQueryResult {
  return useInterestList(listReceivedInterests, "Unable to load received interests");
}

export function useInterestAction(): InterestActionMutationResult {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function mutate(interestId: string, action: InterestAction) {
    setLoading(true);
    setError("");

    try {
      return await actOnInterest(interestId, action);
    } catch (err: unknown) {
      setError(toApiErrorMessage(err, "Unable to update interest"));
      return null;
    } finally {
      setLoading(false);
    }
  }

  return {
    mutate,
    loading,
    error,
    reset: () => setError(""),
  };
}
