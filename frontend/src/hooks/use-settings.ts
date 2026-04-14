"use client";

import { useEffect, useState } from "react";

import { useAuth } from "@/hooks/use-auth";
import {
  deactivateMyProfile,
  deleteMyProfile,
  getMySettings,
  updateMySettings,
} from "@/lib/api/settings";
import type {
  SettingsLifecycleResponse,
  SettingsSummary,
  SettingsUpdatePayload,
} from "@/types/settings";

type SettingsQueryResult = {
  settings: SettingsSummary | null;
  loading: boolean;
  error: string;
  reload: () => void;
};

type UpdateSettingsMutationResult = {
  mutate: (payload: SettingsUpdatePayload) => Promise<SettingsSummary | null>;
  loading: boolean;
  error: string;
  reset: () => void;
};

type LifecycleMutationResult = {
  mutate: () => Promise<SettingsLifecycleResponse | null>;
  loading: boolean;
  error: string;
  reset: () => void;
};

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
    // Keep the original message when the backend response is not JSON text.
  }

  return error.message;
}

export function useSettingsSummary(): SettingsQueryResult {
  const { user, loading: authLoading } = useAuth();
  const [settings, setSettings] = useState<SettingsSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [reloadKey, setReloadKey] = useState(0);

  useEffect(() => {
    if (authLoading) {
      return;
    }

    if (!user) {
      setSettings(null);
      setError("");
      setLoading(false);
      return;
    }

    let active = true;
    setLoading(true);

    getMySettings()
      .then((data) => {
        if (!active) return;
        setSettings(data);
        setError("");
      })
      .catch((err: unknown) => {
        if (!active) return;
        setSettings(null);
        setError(toApiErrorMessage(err, "Unable to load settings"));
      })
      .finally(() => {
        if (!active) return;
        setLoading(false);
      });

    return () => {
      active = false;
    };
  }, [authLoading, reloadKey, user]);

  return {
    settings,
    loading,
    error,
    reload: () => setReloadKey((value) => value + 1),
  };
}

export function useUpdateSettings(): UpdateSettingsMutationResult {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function mutate(payload: SettingsUpdatePayload) {
    setLoading(true);
    setError("");

    try {
      return await updateMySettings(payload);
    } catch (err: unknown) {
      setError(toApiErrorMessage(err, "Unable to update settings"));
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

export function useDeactivateProfile(): LifecycleMutationResult {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function mutate() {
    setLoading(true);
    setError("");

    try {
      return await deactivateMyProfile();
    } catch (err: unknown) {
      setError(toApiErrorMessage(err, "Unable to deactivate profile"));
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

export function useDeleteProfile(): LifecycleMutationResult {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function mutate() {
    setLoading(true);
    setError("");

    try {
      return await deleteMyProfile();
    } catch (err: unknown) {
      setError(toApiErrorMessage(err, "Unable to delete profile"));
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
