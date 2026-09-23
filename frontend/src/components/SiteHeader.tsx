import Link from "next/link";
import { Show, SignInButton, UserButton } from "@clerk/nextjs";

export function SiteHeader() {
  return (
    <header className="border-b border-slate-200 bg-white">
      <div className="mx-auto flex h-14 max-w-6xl items-center gap-6 px-4">
        <Link href="/" className="text-[15px] font-bold tracking-tight text-slate-900">
          ResumeIQ
        </Link>
        <nav className="flex items-center gap-4 text-sm text-slate-600" aria-label="Primary">
          <Link className="hover:text-slate-900" href="/candidate">Candidate</Link>
          <Link className="hover:text-slate-900" href="/recruiter">Recruiter</Link>
          <Link className="hover:text-slate-900" href="/admin">Admin</Link>
        </nav>
        <div className="ml-auto flex items-center gap-3">
          <Show when="signed-out">
            <SignInButton mode="modal">
              <button className="inline-flex min-h-10 items-center rounded-lg bg-blue-700 px-4 text-sm font-medium text-white hover:bg-blue-800">
                Sign in
              </button>
            </SignInButton>
          </Show>
          <Show when="signed-in">
            <UserButton />
          </Show>
        </div>
      </div>
    </header>
  );
}
