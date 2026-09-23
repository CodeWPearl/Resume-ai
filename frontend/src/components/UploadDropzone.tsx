"use client";
import * as React from "react";
import { UploadCloud, FileText, X } from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";

const ACCEPT = ".pdf,.docx";
const MAX_MB = 10;

type Staged = { name: string; size: number; error?: string };

/** Visual shell only (Phase 0) — no upload logic yet. Phase 1 wires it to the backend. */
export function UploadDropzone({ onFiles }: { onFiles?: (files: File[]) => void }) {
  const [drag, setDrag] = React.useState(false);
  const [staged, setStaged] = React.useState<Staged[]>([]);
  const [message, setMessage] = React.useState<string | null>(null);
  const inputRef = React.useRef<HTMLInputElement>(null);

  function validate(f: File): string | undefined {
    const okExt = /\.(pdf|docx)$/i.test(f.name);
    if (!okExt) return "Only PDF or DOCX files are accepted.";
    if (f.size > MAX_MB * 1024 * 1024) return `File exceeds ${MAX_MB}MB limit.`;
    return undefined;
  }

  function handle(list: FileList | File[]) {
    const files = Array.from(list);
    const next: Staged[] = files.map((f) => ({ name: f.name, size: f.size, error: validate(f) }));
    setStaged((s) => [...s, ...next]);
    const valid = files.filter((f) => !validate(f));
    if (valid.length === 0 && files.length > 0) {
      setMessage("No valid files — check type (PDF/DOCX) and size.");
    } else {
      setMessage(null);
      onFiles?.(valid);
    }
  }

  return (
    <div className="flex flex-col gap-4">
      <div
        role="button"
        tabIndex={0}
        aria-label="Upload resumes (PDF or DOCX)"
        onClick={() => inputRef.current?.click()}
        onKeyDown={(e) => e.key === "Enter" && inputRef.current?.click()}
        onDragOver={(e) => { e.preventDefault(); setDrag(true); }}
        onDragLeave={() => setDrag(false)}
        onDrop={(e) => { e.preventDefault(); setDrag(false); handle(e.dataTransfer.files); }}
        className={cn(
          "flex flex-col items-center gap-2 rounded-lg border border-dashed px-6 py-10 text-center transition-colors",
          drag ? "border-blue-700 bg-slate-50" : "border-slate-300 bg-white"
        )}
      >
        <UploadCloud className="h-8 w-8 text-slate-400" aria-hidden />
        <p className="text-sm font-semibold text-slate-900">Drag & drop resumes here, or click to browse</p>
        <p className="text-[13px] text-slate-600">PDF or DOCX only, up to {MAX_MB}MB each. Parsing wires up in Phase 1.</p>
        <input
          ref={inputRef}
          type="file"
          accept={ACCEPT}
          multiple
          className="hidden"
          onChange={(e) => e.target.files && handle(e.target.files)}
        />
      </div>
      {message ? <p className="text-sm text-amber-700">{message}</p> : null}
      {staged.length > 0 ? (
        <ul className="flex flex-col gap-2">
          {staged.map((f, i) => (
            <li key={i} className="flex items-center gap-3 rounded-lg border border-slate-200 bg-white px-4 py-2">
              <FileText className="h-4 w-4 text-slate-500" aria-hidden />
              <div className="min-w-0 flex-1">
                <p className="truncate text-sm font-medium text-slate-900">{f.name}</p>
                <p className={f.error ? "text-[13px] text-red-700" : "text-[13px] text-slate-600"}>
                  {f.error ?? `${(f.size / 1024).toFixed(0)} KB — ready (upload in Phase 1)`}
                </p>
              </div>
              <Button variant="ghost" size="sm" aria-label={`Remove ${f.name}`} onClick={() => setStaged((s) => s.filter((_, j) => j !== i))}>
                <X className="h-4 w-4" />
              </Button>
            </li>
          ))}
        </ul>
      ) : null}
    </div>
  );
}
