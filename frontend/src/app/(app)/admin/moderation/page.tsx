import { AdminModerationDashboard } from "@/components/admin/admin-moderation-dashboard";
import { PageShell } from "@/components/shared/page-shell";

export default function AdminModerationPage() {
  return (
    <PageShell
      title="Moderation Dashboard"
      description="Review reports and intro video verification items from one admin workspace."
    >
      <AdminModerationDashboard />
    </PageShell>
  );
}
