import { ProfileDetailView } from "@/components/browse/profile-detail-view";
import { PageShell } from "@/components/shared/page-shell";

export default async function BrowseProfileDetailPage({
  params,
}: {
  params: Promise<{ profileId: string }>;
}) {
  const { profileId } = await params;

  return (
    <PageShell
      title="Profile Detail"
      description="This is the public profile detail view shown from the browse/discovery flow."
    >
      <ProfileDetailView profileId={profileId} />
    </PageShell>
  );
}
