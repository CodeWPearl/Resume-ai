import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, THead, TRow, TH, TD, EmptyState } from "@/components/ui/table";
import { Button } from "@/components/ui/button";

export default function RecruiterPage() {
  return (
    <main className="flex flex-col gap-6">
      <div className="max-w-[72ch]">
        <h1 className="text-2xl font-bold tracking-tight">Recruiter dashboard</h1>
        <p className="mt-1 text-[15px] text-slate-600">
          JD upload → bulk resumes → ranked table. Full ranking arrives in Phase 5.
        </p>
      </div>
      <Card>
        <CardHeader>
          <CardTitle>Ranked candidates</CardTitle>
          <CardDescription>Placeholder table shell with shared DataTable component.</CardDescription>
        </CardHeader>
        <CardContent className="flex flex-col gap-4">
          <Table>
            <THead>
              <TRow>
                <TH>Candidate</TH>
                <TH>Score</TH>
                <TH>Match</TH>
              </TRow>
            </THead>
            <tbody>
              <TRow>
                <TD>A. Example</TD>
                <TD numeric>—</TD>
                <TD numeric>—</TD>
              </TRow>
            </tbody>
          </Table>
          <EmptyState
            title="No shortlist yet"
            hint="Upload a job description and resumes in Phase 5 to populate this table."
            action={<Button variant="secondary" size="sm">How shortlisting works</Button>}
          />
        </CardContent>
      </Card>
    </main>
  );
}
