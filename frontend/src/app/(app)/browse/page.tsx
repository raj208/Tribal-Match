import { BrowseClient } from "@/components/browse/browse-client";
import { PageShell } from "@/components/shared/page-shell";

export default function BrowsePage() {
  return (
    <PageShell
      title="Browse Profiles"
      description="Browse published profiles using basic discovery filters. Your own profile is hidden from this list."
    >
      <BrowseClient />
    </PageShell>
  );
}