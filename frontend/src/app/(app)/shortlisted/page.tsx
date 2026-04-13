import { ShortlistClient } from "@/components/interests/shortlist-client";
import { PageShell } from "@/components/shared/page-shell";

export default function ShortlistedPage() {
  return (
    <PageShell
      title="Shortlisted Profiles"
      description="Profiles you saved for later appear here."
    >
      <ShortlistClient />
    </PageShell>
  );
}