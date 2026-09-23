import Link from "next/link";
import { redirect } from "next/navigation";
import { createClient, roleOf } from "@/lib/supabase/server";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { UploadDropzone } from "@/components/UploadDropzone";

function roleHome(role: string): string | null {
  if (role === "recruiter") return "/recruiter";
  if (role === "admin") return "/admin";
  if (role === "candidate") return "/candidate";
  return null;
}

export default async function Home({ searchParams }: { searchParams: Promise<{ auto?: string }> }) {
  const params = await searchParams;
  // Role-aware redirect after login: ?auto=1 triggers it without trapping logged-out users.
  if (params.auto) {
    try {
      const supabase = await createClient();
      const {
        data: { user },
      } = await supabase.auth.getUser();
      const dest = user ? roleHome(roleOf(user)) : null;
      if (dest) redirect(dest);
    } catch {
      // Unreachable Supabase project (e.g. CI placeholder env) — render logged-out view.
    }
  }

  return (
    <main className="flex flex-col gap-8">
      <section className="max-w-[72ch]">
        <p className="text-[13px] font-semibold uppercase tracking-wide text-blue-700">ResumeIQ · Phase 0</p>
        <h1 className="mt-2 text-2xl font-bold tracking-tight">One score, three portals.</h1>
        <p className="mt-2 text-[15px] leading-7 text-slate-600">
          Candidates see the same ATS score recruiters rank on. Upload a resume to get a
          plain-language breakdown, match it against a job description, and improve it
          with AI that never invents achievements.
        </p>
        <div className="mt-4 flex gap-3">
          <Button asChild><Link href="/candidate">Candidate portal</Link></Button>
          <Button asChild variant="secondary"><Link href="/recruiter">Recruiter portal</Link></Button>
          <Button asChild variant="ghost"><Link href="/?auto=1">Go to my dashboard</Link></Button>
        </div>
      </section>

      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Try the uploader shell</CardTitle>
            <CardDescription>Visual only in Phase 0 — parsing and scoring arrive in Phase 1.</CardDescription>
          </CardHeader>
          <CardContent><UploadDropzone /></CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>How it works</CardTitle>
            <CardDescription>Same engine everywhere, guarded generation.</CardDescription>
          </CardHeader>
          <CardContent>
            <ol className="flex list-decimal flex-col gap-2 pl-5 text-sm leading-6 text-slate-700">
              <li>Upload a resume (PDF/DOCX) — stored privately, parsed into skills, experience, education.</li>
              <li>Get an ATS score across 8 categories with one-line explanations.</li>
              <li>Paste a job description for match % and missing skills (critical vs. nice-to-have).</li>
              <li>Generate rewrites, summaries, cover letters — every output fact-checked against your resume.</li>
            </ol>
          </CardContent>
        </Card>
      </div>
    </main>
  );
}
