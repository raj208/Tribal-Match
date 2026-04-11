"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import { getSupabaseBrowserClient } from "@/lib/supabase/client";
import { useAuth } from "@/hooks/use-auth";

export function SignupForm() {
  const router = useRouter();
  const { user, loading } = useAuth();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");

  useEffect(() => {
    if (!loading && user) {
      router.replace("/dashboard");
    }
  }, [loading, router, user]);

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setError("");
    setNotice("");

    if (password !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    if (password.length < 6) {
      setError("Password should be at least 6 characters.");
      return;
    }

    try {
      setSubmitting(true);

      const supabase = getSupabaseBrowserClient();
      const redirectTo =
        typeof window !== "undefined"
          ? `${window.location.origin}/login`
          : undefined;

      const { data, error: signUpError } = await supabase.auth.signUp({
        email: email.trim(),
        password,
        options: redirectTo ? { emailRedirectTo: redirectTo } : undefined,
      });

      if (signUpError) {
        setError(signUpError.message);
        return;
      }

      if (data.session) {
        router.replace("/dashboard");
        router.refresh();
        return;
      }

      setNotice(
        "Signup successful. Check your email and confirm your account before logging in."
      );
      setEmail("");
      setPassword("");
      setConfirmPassword("");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="card max-w-xl p-6">
      <h2 className="text-xl font-semibold text-stone-900">Signup</h2>
      <p className="mt-2 text-sm text-stone-600">
        Create your Tribal Match account with email and password.
      </p>

      {error ? (
        <div className="mt-4 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          {error}
        </div>
      ) : null}

      {notice ? (
        <div className="mt-4 rounded-xl border border-green-200 bg-green-50 px-4 py-3 text-sm text-green-700">
          {notice}
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
            placeholder="Create a password"
          />
        </label>

        <label className="block text-sm">
          <span className="mb-2 block font-medium text-stone-700">
            Confirm password
          </span>
          <input
            type="password"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            required
            className="w-full rounded-xl border border-stone-300 px-3 py-2 outline-none focus:border-stone-500"
            placeholder="Re-enter your password"
          />
        </label>
      </div>

      <button
        type="submit"
        disabled={submitting}
        className="mt-6 rounded-xl bg-stone-900 px-5 py-3 text-sm font-medium text-white hover:bg-stone-800 disabled:opacity-60"
      >
        {submitting ? "Creating account..." : "Create account"}
      </button>
    </form>
  );
}