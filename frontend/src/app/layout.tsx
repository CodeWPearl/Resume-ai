import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { SiteHeader } from "@/components/SiteHeader";

const geistSans = Geist({ variable: "--font-geist-sans", subsets: ["latin"] });
const geistMono = Geist_Mono({ variable: "--font-geist-mono", subsets: ["latin"] });

export const metadata: Metadata = {
  title: "ResumeIQ — AI resume intelligence",
  description: "ATS scoring, JD matching, and guarded AI rewrites for candidates and recruiters.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}>
      <body className="flex min-h-full flex-col bg-white text-slate-900">
        <SiteHeader />
        <div className="mx-auto w-full max-w-6xl flex-1 px-4 py-8">{children}</div>
        <footer className="border-t border-slate-200 py-4 text-center text-[13px] text-slate-500">
          ResumeIQ Phase 0 — backend: {process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"}
        </footer>
      </body>
    </html>
  );
}
