import Link from "next/link";

export default function LandingPage() {
  return (
    <main className="space-y-10">
      <section className="card overflow-hidden">
        <div className="grid gap-8 p-8 md:grid-cols-[1.25fr_0.75fr] md:p-10">
          <div>
            <span className="soft-badge bg-amber-100 text-amber-800">
              Trust-first MVP
            </span>

            <h1 className="mt-4 text-4xl font-semibold leading-tight text-stone-900 md:text-5xl">
              A respectful, community-oriented profile discovery platform
            </h1>

            <p className="mt-4 max-w-2xl text-base text-stone-600">
              Tribal Match is being built as a profile-first experience with
              identity, authenticity, onboarding, verification, and safe browsing
              as the foundation.
            </p>

            <div className="mt-6 flex flex-wrap gap-3">
              <Link
                href="/signup"
                className="rounded-xl bg-stone-900 px-5 py-3 text-sm font-medium text-white hover:bg-stone-800"
              >
                Start signup
              </Link>

              <Link
                href="/login"
                className="rounded-xl border border-stone-300 bg-white px-5 py-3 text-sm font-medium text-stone-800 hover:bg-stone-100"
              >
                Go to login
              </Link>
            </div>
          </div>

          <div className="card p-6">
            <p className="text-sm font-medium text-stone-500">MVP focus</p>
            <ul className="mt-4 space-y-3 text-sm text-stone-700">
              <li>• signup and login foundation</li>
              <li>• onboarding-ready structure</li>
              <li>• profile creation and browsing flow</li>
              <li>• intro video verification support later</li>
              <li>• shortlist, interest, report, and block readiness</li>
            </ul>
          </div>
        </div>
      </section>

      <section className="grid gap-4 md:grid-cols-3">
        <div className="card p-6">
          <h2 className="text-lg font-semibold text-stone-900">
            Trust-led design
          </h2>
          <p className="mt-2 text-sm text-stone-600">
            The product avoids swipe-first behavior and focuses on respectful,
            profile-based browsing.
          </p>
        </div>

        <div className="card p-6">
          <h2 className="text-lg font-semibold text-stone-900">
            Modular monolith
          </h2>
          <p className="mt-2 text-sm text-stone-600">
            Frontend and backend remain simple now, but their internal module
            boundaries are ready for growth later.
          </p>
        </div>

        <div className="card p-6">
          <h2 className="text-lg font-semibold text-stone-900">
            Future-ready flow
          </h2>
          <p className="mt-2 text-sm text-stone-600">
            We are keeping room for auth, media, verification, moderation,
            recommendations, and mobile support later.
          </p>
        </div>
      </section>
    </main>
  );
}