"use client";

import { useEffect, useState } from "react";

import { useAuth } from "@/hooks/use-auth";
import {
  getAdminVerification,
  listAdminVerifications,
  reviewAdminVerification,
} from "@/lib/api/admin-verification";
import type {
  AdminVerificationDetail,
  AdminVerificationQueueItem,
} from "@/types/admin-verification";

type AdminVerificationQueueResult = {
  items: AdminVerificationQueueItem[];
  loading: boolean;
  refreshing: boolean;
  error: string;
  reload: () => void;
};

type AdminVerificationDetailResult = {
  item: AdminVerificationDetail | null;
  loading: boolean;
  error: string;
  reload: () => void;
  replaceItem: (item: AdminVerificationDetail) => void;
};

type ReviewAdminVerificationMutationResult = {
  mutate: (
    itemId: string,
    decision: "approved" | "rejected",
    reason?: string | null
  ) => Promise<AdminVerificationDetail | null>;
  loading: boolean;
  error: string;
  reset: () => void;
};

function toApiErrorMessage(error: unknown, fallback: string): string {
  if (!(error instanceof Error) || !error.message) {
    return fallback;
  }

  return error.message;
}

export function useAdminVerificationQueue(): AdminVerificationQueueResult {
  const { user, loading: authLoading } = useAuth();
  const [items, setItems] = useState<AdminVerificationQueueItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState("");
  const [reloadKey, setReloadKey] = useState(0);

  useEffect(() => {
    if (authLoading) {
      return;
    }

    if (!user) {
      setItems([]);
      setError("");
      setLoading(false);
      setRefreshing(false);
      return;
    }

    let active = true;
    const hasExistingItems = items.length > 0;

    if (hasExistingItems) {
      setRefreshing(true);
    } else {
      setLoading(true);
    }
    setError("");

    listAdminVerifications({ limit: 100 })
      .then((data) => {
        if (!active) return;
        setItems(data);
        setError("");
      })
      .catch((err: unknown) => {
        if (!active) return;
        if (!hasExistingItems) {
          setItems([]);
        }
        setError(toApiErrorMessage(err, "Unable to load verification queue"));
      })
      .finally(() => {
        if (!active) return;
        setLoading(false);
        setRefreshing(false);
      });

    return () => {
      active = false;
    };
  }, [authLoading, reloadKey, user]);

  return {
    items,
    loading,
    refreshing,
    error,
    reload: () => setReloadKey((value) => value + 1),
  };
}

export function useAdminVerificationDetail(
  itemId: string | null
): AdminVerificationDetailResult {
  const { user, loading: authLoading } = useAuth();
  const [item, setItem] = useState<AdminVerificationDetail | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [reloadKey, setReloadKey] = useState(0);

  useEffect(() => {
    if (authLoading) {
      return;
    }

    if (!user || !itemId) {
      setItem(null);
      setError("");
      setLoading(false);
      return;
    }

    let active = true;
    setLoading(true);
    setError("");

    getAdminVerification(itemId)
      .then((data) => {
        if (!active) return;
        setItem(data);
        setError("");
      })
      .catch((err: unknown) => {
        if (!active) return;
        setItem(null);
        setError(toApiErrorMessage(err, "Unable to load verification detail"));
      })
      .finally(() => {
        if (!active) return;
        setLoading(false);
      });

    return () => {
      active = false;
    };
  }, [authLoading, itemId, reloadKey, user]);

  return {
    item,
    loading,
    error,
    reload: () => setReloadKey((value) => value + 1),
    replaceItem: (nextItem) => {
      setItem(nextItem);
      setError("");
    },
  };
}

export function useReviewAdminVerification(): ReviewAdminVerificationMutationResult {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function mutate(
    itemId: string,
    decision: "approved" | "rejected",
    reason?: string | null
  ) {
    setLoading(true);
    setError("");

    try {
      return await reviewAdminVerification(itemId, {
        status: decision,
        reason: reason?.trim() ? reason.trim() : null,
      });
    } catch (err: unknown) {
      setError(toApiErrorMessage(err, "Unable to review verification"));
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
