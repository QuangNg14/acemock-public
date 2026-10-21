import type { Metadata } from "next";
import AuthProvider from "@/components/AuthProvider";
import Header from "@/components/Header";
import "./globals.css";

export const metadata: Metadata = {
  title: "AceMock - Graded AI Mock Interviews",
  description:
    "Live AI interviews on real company questions, graded by a calibrated mentor rubric. Plus a behavioral story engine and QuantReady.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="surface min-h-screen">
        <AuthProvider>
          <Header />
          <main className="mx-auto max-w-6xl px-4 py-8 sm:px-6 sm:py-10">{children}</main>
          <footer className="mx-auto max-w-6xl px-4 py-8 text-xs text-black/50 sm:px-6 sm:py-10">
            AceMock - real banks, mentor-calibrated grading. Built on the Pathwise knowledge base.
          </footer>
        </AuthProvider>
      </body>
    </html>
  );
}
