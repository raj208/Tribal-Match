import { Suspense } from "react";

import { LoginForm } from "@/components/auth/login-form";
import { PageShell } from "@/components/shared/page-shell";

export default function LoginPage() {
  return (
    <PageShell
      title="Login"
      description="Use your Tribal Match account to access the app."
    >
      <Suspense fallback={null}>
        <LoginForm />
      </Suspense>
    </PageShell>
  );
}
