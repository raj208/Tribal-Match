import Link from "next/link";

const links = [
  { href: "/", label: "Home" },
  { href: "/login", label: "Login" },
  { href: "/signup", label: "Signup" },
];

export function PublicHeader() {
  return (
    <header className="border-b border-stone-200 bg-white/90 backdrop-blur">
      <div className="container-shell flex items-center justify-between py-4">
        <Link href="/" className="text-lg font-semibold text-stone-900">
          Tribal Match
        </Link>

        <nav className="flex items-center gap-5 text-sm text-stone-600">
          {links.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className="hover:text-stone-900"
            >
              {item.label}
            </Link>
          ))}
        </nav>
      </div>
    </header>
  );
}