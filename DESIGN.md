# ResumeIQ — DESIGN.md (Impeccable visual system, v1)

Source of truth for all frontend work. Run `npx impeccable detect frontend/src`
before shipping UI changes.

## Tokens
- Colors (light-first, sober palette):
  - bg: #FFFFFF, surface: #F8FAFC (slate-50), border: #E2E8F0 (slate-200)
  - ink: #0F172A (slate-900), muted: #475569 (slate-600), faint: #94A3B8
  - accent: #1D4ED8 (blue-700, single strategic color), accent-ink: #FFFFFF
  - warn: #B45309 (amber-700), danger: #B91C1C (red-700), ok: #15803D
  - flagged AI content: amber-50 bg (#FFFBEB) + amber-700 border + "Needs review" badge
- Type: Geist Sans (body), Geist Mono (scores/code). Scale: 12 meta / 14 body /
  16 section / 24 page title. Line length <= 72ch for explanations.
- Spacing/rhythm: 4pt base, cards p-6, section gap-8, page max-w-6xl.
- Corners: rounded-lg (8px) cards/buttons, sharp data-table headers. No pill-everything.
- Motion: 150ms ease-out only; no bounce. Skeletons for cold-start waits.

## Components (shadcn/ui + Tailwind)
- Button: variants primary (blue-700)/secondary (outline slate)/ghost/danger.
  Min touch target 40px. Never gradient.
- Input/Label: 14px labels slate-700, inputs border slate-200, focus ring blue-700.
- DataTable: sticky header, numeric right-aligned, row hover slate-50, empty state
  with action (not blank).
- Card: white bg, slate-200 border, rounded-lg, header = 16px semibold + muted desc.
- UploadDropzone: dashed slate-300 border, drag-active = blue-700 border + slate-50 bg,
  file list with per-file status, client-side PDF/DOCX + size validation messaging.
- Badge: match% (blue), critical gap (red-50/red-700), nice-to-have (slate-100),
  flagged (amber-50/amber-700).

## Layout rules
- App shell: top SiteHeader (logo left, role nav center, email + sign-out right) +
  max-w-6xl content. Role dashboards use left section nav on desktop.
- Score dashboard: overall score hero (large numeral + band label) + 8 category rows
  with bars + one-line explanations.
- Never side-tab borders as decoration; never purple/blue gradient text.
- Accessibility: labeled inputs, focus-visible rings, table scope attrs,
  touch targets >= 40px, contrast AA.

## Cold-start / empty / error states
- First backend call after idle: "Waking up the server, this can take up to a
  minute (free tier)…" + progress + retry. Not a bare spinner.
- Empty recruiter table / no resumes: illustration-free empty card + CTA.
- Gemini 429: "AI is busy, try again in a moment." Never raw errors/stack traces.
