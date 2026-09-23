import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { UploadDropzone } from "@/components/UploadDropzone";

export default function CandidatePage() {
  return (
    <main className="flex flex-col gap-6">
      <div className="max-w-[72ch]">
        <h1 className="text-2xl font-bold tracking-tight">Candidate dashboard</h1>
        <p className="mt-1 text-[15px] text-slate-600">
          Upload → confirm parsed data → ATS score. Full scoring arrives in Phase 1.
        </p>
      </div>
      <Card>
        <CardHeader>
          <CardTitle>Upload resume</CardTitle>
          <CardDescription>PDF or DOCX. Stored in a private bucket, never in git.</CardDescription>
        </CardHeader>
        <CardContent><UploadDropzone /></CardContent>
      </Card>
      <Card>
        <CardHeader>
          <CardTitle>ATS score</CardTitle>
          <CardDescription>Placeholder — overall + 8 categories land in Phase 1.</CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-slate-600">No resume scored yet. Upload above to begin.</p>
        </CardContent>
      </Card>
    </main>
  );
}
