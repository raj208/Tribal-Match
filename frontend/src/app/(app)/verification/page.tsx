import { PhotoManager } from "@/components/media/photo-manager";
import { PageShell } from "@/components/shared/page-shell";
import { VideoVerificationCard } from "@/components/verification/video-verification-card";

export default function VerificationPage() {
  return (
    <PageShell
      title="Media & Verification"
      description="You can now upload real local image and video files. Later we can swap this local storage provider with Cloudflare or a mobile-friendly provider."
    >
      <PhotoManager />
      <VideoVerificationCard />
    </PageShell>
  );
}