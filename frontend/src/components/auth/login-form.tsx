"use client";

import { useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";

import { getSupabaseBrowserClient } from "@/lib/supabase/client";
import { useAuth } from "@/hooks/use-auth";

export function LoginForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { user, loading } = useAuth();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  const next = searchParams.get("next") || "/dashboard";

  useEffect(() => {
    if (!loading && user) {
      router.replace(next);
    }
  }, [loading, next, router, user]);

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setError("");

    try {
      setSubmitting(true);

      const supabase = getSupabaseBrowserClient();
      const { error: signInError } = await supabase.auth.signInWithPassword({
        email: email.trim(),
        password,
      });

      if (signInError) {
        setError(signInError.message);
        return;
      }

      router.replace(next);
      router.refresh();
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="card max-w-xl p-6">
      <h2 className="text-xl font-semibold text-stone-900">Login</h2>
      <p className="mt-2 text-sm text-stone-600">
        Sign in with your email and password.
      </p>

      {error ? (
        <div className="mt-4 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          {error}
        </div>
      ) : null}

      <div className="mt-5 space-y-4">
        <label className="block text-sm">
          <span className="mb-2 block font-medium text-stone-700">Email</span>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            className="w-full rounded-xl border border-stone-300 px-3 py-2 outline-none focus:border-stone-500"
            placeholder="you@example.com"
          />
        </label>

        <label className="block text-sm">
          <span className="mb-2 block font-medium text-stone-700">Password</span>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            className="w-full rounded-xl border border-stone-300 px-3 py-2 outline-none focus:border-stone-500"
            placeholder="Enter your password"
          />
        </label>
      </div>

      <button
        type="submit"
        disabled={submitting}
        className="mt-6 rounded-xl bg-stone-900 px-5 py-3 text-sm font-medium text-white hover:bg-stone-800 disabled:opacity-60"
      >
        {submitting ? "Logging in..." : "Login"}
      </button>
    </form>
  );
}