import { redirect } from "next/navigation";
import { createClient, roleOf } from "@/lib/supabase/server";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

export default async function AdminPage() {
  try {
    const supabase = await createClient();
    const {
      data: { user },
    } = await supabase.auth.getUser();
    if (user && roleOf(user) !== "admin") redirect("/");
  } catch {
    // Unreachable project (e.g. CI placeholder env) — render placeholder.
  }

  return (
    <main className="flex flex-col gap-6">
      <div className="max-w-[72ch]">
        <h1 className="text-2xl font-bold tracking-tight">Admin dashboard</h1>
        <p className="mt-1 text-[15px] text-slate-600">
          Usage, storage, token-cost, roles, health. Live numbers arrive in Phase 6.
          Admin role is assigned via user_metadata in the Supabase dashboard.
        </p>
      </div>
      <div className="grid gap-4 md:grid-cols-3">
        {(["Usage", "Token cost", "System health"] as const).map((t) => (
          <Card key={t}>
            <CardHeader><CardTitle>{t}</CardTitle><CardDescription>Placeholder</CardDescription></CardHeader>
            <CardContent><p className="text-2xl font-bold tabular-nums">—</p></CardContent>
          </Card>
        ))}
      </div>
    </main>
  );
}
