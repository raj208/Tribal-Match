import { ProfileDetailView } from "@/components/browse/profile-detail-view";
import { PageShell } from "@/components/shared/page-shell";

export default function BrowseProfileDetailPage({
  params,
}: {
  params: { profileId: string };
}) {
  return (
    <PageShell
      title="Profile Detail"
      description="This is the public profile detail view shown from the browse/discovery flow."
    >
      <ProfileDetailView profileId={params.profileId} />
    </PageShell>
  );
}