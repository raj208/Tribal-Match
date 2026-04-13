import { InterestsClient } from "@/components/interests/interests-client";
import { PageShell } from "@/components/shared/page-shell";

export default function InterestsPage() {
  return (
    <PageShell
      title="Interests"
      description="Track interests you sent and interests you received."
    >
      <InterestsClient />
    </PageShell>
  );
}