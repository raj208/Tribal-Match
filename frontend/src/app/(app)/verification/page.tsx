import { PhotoManager } from "@/components/media/photo-manager";
import { PageShell } from "@/components/shared/page-shell";
import { VideoVerificationCard } from "@/components/verification/video-verification-card";

export default function VerificationPage() {
  return (
    <PageShell
      title="Media & Verification"
      description="Manage private profile photos and intro video verification. Existing local media still works while new uploads move through protected storage."
    >
      <PhotoManager />
      <VideoVerificationCard />
    </PageShell>
  );
}
