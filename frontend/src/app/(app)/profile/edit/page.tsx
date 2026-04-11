import { ProfileForm } from "@/components/profile/profile-form";
import { PageShell } from "@/components/shared/page-shell";

export default function EditProfilePage() {
  return (
    <PageShell
      title="Create / Edit Profile"
      description="This is the first real connected form in the app. It saves profile data and preferences to the backend."
    >
      <ProfileForm />
    </PageShell>
  );
}