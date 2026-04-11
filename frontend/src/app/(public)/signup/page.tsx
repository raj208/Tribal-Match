import { SignupForm } from "@/components/auth/signup-form";
import { PageShell } from "@/components/shared/page-shell";

export default function SignupPage() {
  return (
    <PageShell
      title="Signup"
      description="Create your Tribal Match account before continuing to profile creation."
    >
      <SignupForm />
    </PageShell>
  );
}