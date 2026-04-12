import { PhotoManager } from "@/components/media/photo-manager";
import { PageShell } from "@/components/shared/page-shell";
import { VideoVerificationCard } from "@/components/verification/video-verification-card";

export default function VerificationPage() {
  return (
    <PageShell
      title="Media & Verification"
      description="This step uses placeholder media URLs. Later, we will replace this with real image and video upload flows."
    >
      <PhotoManager />
      <VideoVerificationCard />
    </PageShell>
  );
}