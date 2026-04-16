"use client";

import { useEffect, useState } from "react";

import { useAuth } from "@/hooks/use-auth";
import {
  getAdminReport,
  listAdminReports,
  updateAdminReportStatus,
} from "@/lib/api/admin-moderation";
import type { ReportStatus } from "@/types";
import type {
  AdminReportDetail,
  AdminReportListItem,
} from "@/types/admin-moderation";

export type AdminReportStatusFilter = ReportStatus | "all";

type AdminReportsQueryResult = {
  reports: AdminReportListItem[];
  loading: boolean;
  refreshing: boolean;
  error: string;
  reload: () => void;
  replaceReport: (report: AdminReportDetail) => void;
};

type AdminReportDetailQueryResult = {
  report: AdminReportDetail | null;
  loading: boolean;
  error: string;
  reload: () => void;
  replaceReport: (report: AdminReportDetail) => void;
};

type AdminReportStatusMutationResult = {
  mutate: (reportId: string, status: ReportStatus) => Promise<AdminReportDetail | null>;
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

export function useAdminReports(statusFilter: AdminReportStatusFilter): AdminReportsQueryResult {
  const { user, loading: authLoading } = useAuth();
  const [reports, setReports] = useState<AdminReportListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState("");
  const [reloadKey, setReloadKey] = useState(0);

  useEffect(() => {
    if (authLoading) {
      return;
    }

    if (!user) {
      setReports([]);
      setError("");
      setLoading(false);
      setRefreshing(false);
      return;
    }

    let active = true;
    const hasExistingReports = reports.length > 0;

    if (hasExistingReports) {
      setRefreshing(true);
    } else {
      setLoading(true);
    }
    setError("");

    listAdminReports({ status: statusFilter, limit: 100 })
      .then((data) => {
        if (!active) return;
        setReports(data);
        setError("");
      })
      .catch((err: unknown) => {
        if (!active) return;
        if (!hasExistingReports) {
          setReports([]);
        }
        setError(toApiErrorMessage(err, "Unable to load reports"));
      })
      .finally(() => {
        if (!active) return;
        setLoading(false);
        setRefreshing(false);
      });

    return () => {
      active = false;
    };
  }, [authLoading, reloadKey, statusFilter, user]);

  return {
    reports,
    loading,
    refreshing,
    error,
    reload: () => setReloadKey((value) => value + 1),
    replaceReport: (report) => {
      setReports((current) =>
        current.map((item) => (item.id === report.id ? report : item))
      );
      setError("");
    },
  };
}

export function useAdminReportDetail(reportId: string | null): AdminReportDetailQueryResult {
  const { user, loading: authLoading } = useAuth();
  const [report, setReport] = useState<AdminReportDetail | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [reloadKey, setReloadKey] = useState(0);

  useEffect(() => {
    if (authLoading) {
      return;
    }

    if (!user || !reportId) {
      setReport(null);
      setError("");
      setLoading(false);
      return;
    }

    let active = true;
    setLoading(true);
    setError("");

    getAdminReport(reportId)
      .then((data) => {
        if (!active) return;
        setReport(data);
        setError("");
      })
      .catch((err: unknown) => {
        if (!active) return;
        setReport(null);
        setError(toApiErrorMessage(err, "Unable to load report detail"));
      })
      .finally(() => {
        if (!active) return;
        setLoading(false);
      });

    return () => {
      active = false;
    };
  }, [authLoading, reloadKey, reportId, user]);

  return {
    report,
    loading,
    error,
    reload: () => setReloadKey((value) => value + 1),
    replaceReport: (nextReport) => {
      setReport(nextReport);
      setError("");
    },
  };
}

export function useUpdateAdminReportStatus(): AdminReportStatusMutationResult {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function mutate(reportId: string, status: ReportStatus) {
    setLoading(true);
    setError("");

    try {
      return await updateAdminReportStatus(reportId, { status });
    } catch (err: unknown) {
      setError(toApiErrorMessage(err, "Unable to update report status"));
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
