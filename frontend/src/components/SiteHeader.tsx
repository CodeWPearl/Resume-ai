"use client";
import * as React from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { createClient } from "@/lib/supabase/client";
import { Button } from "@/components/ui/button";

export function SiteHeader() {
  const router = useRouter();
  const [email, setEmail] = React.useState<string | null>(null);
  const [ready, setReady] = React.useState(false);

  React.useEffect(() => {
    const supabase = createClient();
    supabase.auth.getUser().then(({ data }) => {
      setEmail(data.user?.email ?? null);
      setReady(true);
    });
    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((_event, session) => {
      setEmail(session?.user?.email ?? null);
    });
    return () => subscription.unsubscribe();
  }, []);

  async function signOut() {
    await createClient().auth.signOut();
    setEmail(null);
    router.push("/");
    router.refresh();
  }

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
          {!ready ? null : email ? (
            <>
              <span className="hidden text-sm text-slate-600 sm:inline">{email}</span>
              <Button variant="secondary" size="sm" onClick={signOut}>Sign out</Button>
            </>
          ) : (
            <Button asChild size="sm"><Link href="/sign-in">Sign in</Link></Button>
          )}
        </div>
      </div>
    </header>
  );
}
