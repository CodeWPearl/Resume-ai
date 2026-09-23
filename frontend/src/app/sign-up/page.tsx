"use client";
import * as React from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { createClient } from "@/lib/supabase/client";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

export default function SignUpPage() {
  const router = useRouter();
  const [email, setEmail] = React.useState("");
  const [password, setPassword] = React.useState("");
  const [role, setRole] = React.useState<"candidate" | "recruiter">("candidate");
  const [error, setError] = React.useState<string | null>(null);
  const [notice, setNotice] = React.useState<string | null>(null);
  const [busy, setBusy] = React.useState(false);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError(null);
    setNotice(null);
    const { data, error } = await createClient().auth.signUp({
      email,
      password,
      options: { data: { role } },
    });
    setBusy(false);
    if (error) {
      setError(error.message);
      return;
    }
    if (data.session) {
      router.push("/?auto=1");
      router.refresh();
    } else {
      setNotice("Account created. Confirm your email (unless confirmation is off), then sign in.");
    }
  }

  return (
    <main className="mx-auto max-w-md py-10">
      <Card>
        <CardHeader>
          <CardTitle>Create an account</CardTitle>
          <CardDescription>Pick the portal you will use. Admins are assigned in the Supabase dashboard.</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={onSubmit} className="flex flex-col gap-4">
            <div className="flex flex-col gap-1.5">
              <Label htmlFor="email">Email</Label>
              <Input id="email" type="email" required autoComplete="email" value={email} onChange={(e) => setEmail(e.target.value)} />
            </div>
            <div className="flex flex-col gap-1.5">
              <Label htmlFor="password">Password</Label>
              <Input id="password" type="password" required autoComplete="new-password" minLength={6} value={password} onChange={(e) => setPassword(e.target.value)} />
            </div>
            <div className="flex flex-col gap-1.5">
              <Label htmlFor="role">I am a…</Label>
              <select
                id="role"
                value={role}
                onChange={(e) => setRole(e.target.value as "candidate" | "recruiter")}
                className="flex min-h-10 w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm text-slate-900 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-700"
              >
                <option value="candidate">Candidate</option>
                <option value="recruiter">Recruiter</option>
              </select>
            </div>
            {error ? <p role="alert" className="text-sm text-red-700">{error}</p> : null}
            {notice ? <p role="status" className="text-sm text-slate-700">{notice}</p> : null}
            <Button type="submit" disabled={busy}>{busy ? "Creating…" : "Create account"}</Button>
            <p className="text-sm text-slate-600">
              Have an account? <Link className="font-medium text-blue-700 hover:underline" href="/sign-in">Sign in</Link>
            </p>
          </form>
        </CardContent>
      </Card>
    </main>
  );
}
