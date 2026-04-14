"use client";

import { useEffect, useState } from "react";

import { getDashboardSummary } from "@/lib/api/dashboard";
import { useAuth } from "@/hooks/use-auth";
import type { DashboardSummary } from "@/types/dashboard";

type UseDashboardSummaryResult = {
  summary: DashboardSummary | null;
  loading: boolean;
  error: string;
  reload: () => void;
};

export function useDashboardSummary(): UseDashboardSummaryResult {
  const { user, loading: authLoading } = useAuth();
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [reloadKey, setReloadKey] = useState(0);

  useEffect(() => {
    if (authLoading) {
      return;
    }

    if (!user) {
      setSummary(null);
      setError("");
      setLoading(false);
      return;
    }

    let active = true;
    setLoading(true);

    getDashboardSummary()
      .then((data) => {
        if (!active) return;
        setSummary(data);
        setError("");
      })
      .catch((err: Error) => {
        if (!active) return;
        setSummary(null);
        setError(err.message || "Unable to load dashboard summary");
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
    summary,
    loading,
    error,
    reload: () => setReloadKey((value) => value + 1),
  };
}
