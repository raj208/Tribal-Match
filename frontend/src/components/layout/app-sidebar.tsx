import Link from "next/link";

import { LogoutButton } from "@/components/auth/logout-button";

const links = [
  { href: "/dashboard", label: "Dashboard" },
  { href: "/browse", label: "Browse Profiles" },
  { href: "/shortlisted", label: "Shortlisted" },
  { href: "/interests", label: "Interests" },
  { href: "/profile", label: "My Profile" },
  { href: "/verification", label: "Verification" },
  { href: "/settings", label: "Settings" },
];

export function AppSidebar() {
  return (
    <aside className="card h-fit p-4">
      <div>
        <p className="text-xs uppercase tracking-[0.2em] text-stone-400">
          Navigation
        </p>
        <h2 className="mt-2 text-lg font-semibold text-stone-900">
          Tribal Match
        </h2>
        <p className="mt-1 text-sm text-stone-600">
          Auth-enabled MVP shell
        </p>
      </div>

      <nav className="mt-5 flex flex-col gap-2">
        {links.map((item) => (
          <Link
            key={item.href}
            href={item.href}
            className="rounded-xl px-3 py-2 text-sm text-stone-700 hover:bg-stone-100 hover:text-stone-900"
          >
            {item.label}
          </Link>
        ))}
      </nav>

      <div className="mt-5">
        <LogoutButton />
      </div>
    </aside>
  );
}