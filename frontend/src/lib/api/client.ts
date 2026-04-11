import { getSupabaseBrowserClient } from "@/lib/supabase/client";

const API_BASE_URL = (
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api/v1"
).replace(/\/$/, "");

type RequestOptions = {
  method?: "GET" | "POST" | "PATCH" | "DELETE";
  body?: unknown;
};

async function buildHeaders() {
  const headers = new Headers();
  headers.set("Content-Type", "application/json");

  if (typeof window === "undefined") {
    return headers;
  }

  const supabase = getSupabaseBrowserClient();
  const {
    data: { session },
  } = await supabase.auth.getSession();

  if (session?.access_token) {
    headers.set("Authorization", `Bearer ${session.access_token}`);
  }

  if (session?.user?.email) {
    headers.set("X-User-Email", session.user.email);
  }

  return headers;
}

async function apiRequest<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const { method = "GET", body } = options;
  const headers = await buildHeaders();

  const res = await fetch(`${API_BASE_URL}${path}`, {
    method,
    cache: "no-store",
    headers,
    body: body !== undefined ? JSON.stringify(body) : undefined,
  });

  if (!res.ok) {
    const txt = await res.text();
    throw new Error(txt || `Request failed with status ${res.status}`);
  }

  return res.json() as Promise<T>;
}

export function apiGet<T>(path: string) {
  return apiRequest<T>(path, { method: "GET" });
}

export function apiPost<T>(path: string, body: unknown) {
  return apiRequest<T>(path, { method: "POST", body });
}

export function apiPatch<T>(path: string, body: unknown) {
  return apiRequest<T>(path, { method: "PATCH", body });
}