import { SettingsClient } from "@/components/settings/settings-client";
import { PageShell } from "@/components/shared/page-shell";

export default function Page() {
  return (
    <PageShell
      title="Settings"
      description="Manage the real backend-backed account summary, privacy visibility, and lifecycle actions for your profile."
    >
      <SettingsClient />
    </PageShell>
  );
}
