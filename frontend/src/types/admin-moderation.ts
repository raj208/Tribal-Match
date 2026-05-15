import type { ProfileStatus, ReportStatus } from "@/types";

export type AdminReportUserSummary = {
  id: string;
  email: string;
};

export type AdminReportProfileSummary = {
  id: string;
  user_id: string;
  full_name: string;
  profile_status: ProfileStatus;
  instagram_url: string | null;
  facebook_url: string | null;
  linkedin_url: string | null;
};

export type AdminReportListItem = {
  id: string;
  reporter: AdminReportUserSummary;
  reported_user: AdminReportUserSummary;
  reported_profile: AdminReportProfileSummary;
  reason_code: string;
  status: ReportStatus;
  created_at: string;
};

export type AdminReportDetail = AdminReportListItem & {
  notes: string | null;
  updated_at: string;
};

export type AdminReportStatusUpdatePayload = {
  status: ReportStatus;
};
