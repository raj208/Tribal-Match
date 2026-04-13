import { apiGet } from "@/lib/api/client";
import type { DashboardSummary } from "@/types/dashboard";

export function getDashboardSummary() {
  return apiGet<DashboardSummary>("/dashboard/summary");
}
