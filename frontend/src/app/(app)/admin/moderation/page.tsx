import { AdminReportsQueue } from "@/components/admin/admin-reports-queue";
import { PageShell } from "@/components/shared/page-shell";

export default function AdminModerationPage() {
  return (
    <PageShell
      title="Admin Reports"
      description="Review submitted profile reports and update their moderation status."
    >
      <AdminReportsQueue />
    </PageShell>
  );
}
