"use client";

import { useState } from "react";
import { api } from "@/lib/api";

export default function UpgradeButton({ plan = "pro", label }: { plan?: string; label?: string }) {
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  async function go() {
    setBusy(true);
    setError("");
    try {
      const { url } = await api.checkout(plan);
      window.location.href = url;
    } catch (e) {
      setError(String(e));
      setBusy(false);
    }
  }

  return (
    <span>
      <button className="btn" onClick={go} disabled={busy}>
        {label ?? (busy ? "Redirecting..." : "Upgrade to Pro")}
      </button>
      {error && <span className="ml-2 text-xs text-red-700">{error}</span>}
    </span>
  );
}
