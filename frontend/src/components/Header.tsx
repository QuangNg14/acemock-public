"use client";

import Link from "next/link";
import { useState } from "react";
import AuthControls from "./AuthControls";

const links = [
  { href: "/mock", label: "Mock Agent" },
  { href: "/behavioral", label: "Behavioral" },
  { href: "/quant", label: "QuantReady" },
  { href: "/pricing", label: "Pricing" },
];

export default function Header() {
  const [open, setOpen] = useState(false);

  return (
    <header className="border-b border-black/10">
      <nav className="mx-auto flex max-w-6xl items-center justify-between px-4 py-4 sm:px-6">
        <Link
          href="/"
          onClick={() => setOpen(false)}
          className="font-display text-2xl font-black tracking-tight"
        >
          Ace<span style={{ color: "var(--teal)" }}>Mock</span>
        </Link>

        <div className="hidden items-center gap-6 text-sm font-semibold md:flex">
          {links.map((l) => (
            <Link key={l.href} href={l.href} className="hover:text-teal-700">
              {l.label}
            </Link>
          ))}
          <AuthControls />
        </div>

        <button
          aria-label="Toggle menu"
          aria-expanded={open}
          className="-mr-2 p-2 md:hidden"
          onClick={() => setOpen((o) => !o)}
        >
          <span className="mb-1.5 block h-0.5 w-6 bg-current" />
          <span className="mb-1.5 block h-0.5 w-6 bg-current" />
          <span className="block h-0.5 w-6 bg-current" />
        </button>
      </nav>

      {open && (
        <div className="border-t border-black/10 px-4 py-3 md:hidden">
          <div className="flex flex-col gap-3 text-base font-semibold">
            {links.map((l) => (
              <Link
                key={l.href}
                href={l.href}
                onClick={() => setOpen(false)}
                className="py-1 hover:text-teal-700"
              >
                {l.label}
              </Link>
            ))}
            <div className="pt-1">
              <AuthControls />
            </div>
          </div>
        </div>
      )}
    </header>
  );
}
