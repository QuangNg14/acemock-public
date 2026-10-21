"use client";

import { useEffect, useState } from "react";
import { api, QuantDrill } from "@/lib/api";

const FIRMS = ["", "jane-street", "optiver", "citadel", "sig", "imc", "two-sigma", "hrt", "drw"];

export default function QuantPage() {
  const [firm, setFirm] = useState("");
  const [drills, setDrills] = useState<QuantDrill[]>([]);
  const [idx, setIdx] = useState(0);
  const [response, setResponse] = useState("");
  const [result, setResult] = useState<{ correct: boolean; feedback: string | null } | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  function load(f: string) {
    setBusy(true); setError(""); setResult(null); setResponse(""); setIdx(0);
    api.quantDrills(f || undefined)
      .then(setDrills)
      .catch((e) => setError(String(e)))
      .finally(() => setBusy(false));
  }

  useEffect(() => { load(""); }, []);

  const drill = drills[idx];

  async function submit() {
    if (!drill) return;
    setBusy(true);
    try { setResult(await api.quantAttempt(drill.id, response)); }
    catch (e) { setError(String(e)); } finally { setBusy(false); }
  }

  function next() {
    setResult(null); setResponse("");
    setIdx((i) => (i + 1) % Math.max(drills.length, 1));
  }

  return (
    <div>
      <h1 className="font-display text-3xl font-black sm:text-4xl">QuantReady</h1>
      <p className="mt-2 text-black/70">Firm-specific brainteaser, probability, mental-math, and market-making drills.</p>
      {error && <p className="mt-4 text-sm text-red-700">{error}</p>}

      <div className="mt-6 flex flex-wrap gap-2">
        {FIRMS.map((f) => (
          <button key={f || "all"}
            className="chip"
            style={{ background: firm === f ? "var(--teal)" : "transparent", color: firm === f ? "#fff" : "var(--teal)" }}
            onClick={() => { setFirm(f); load(f); }}>
            {f || "all firms"}
          </button>
        ))}
      </div>

      {drill ? (
        <div className="card mt-6 p-6">
          <div className="flex flex-wrap gap-2 text-xs">
            <span className="chip" style={{ color: "var(--teal)" }}>{drill.category}</span>
            <span className="chip" style={{ color: "var(--teal)" }}>{drill.difficulty}</span>
            {drill.time_limit_seconds && (
              <span className="chip" style={{ color: "var(--amber)" }}>{drill.time_limit_seconds}s</span>
            )}
          </div>
          <p className="font-display mt-4 break-words text-lg sm:text-xl">{drill.prompt}</p>
          <div className="mt-4 flex flex-wrap gap-2">
            <input className="min-w-0 flex-1 basis-full rounded border border-black/20 p-2 text-sm sm:basis-0" placeholder="Your answer"
              value={response} onChange={(e) => setResponse(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && submit()} />
            <button className="btn" onClick={submit} disabled={busy}>Check</button>
            <button className="btn" style={{ background: "var(--ink)" }} onClick={next}>Next</button>
          </div>
          {result && (
            <p className={`mt-4 font-semibold ${result.correct ? "text-teal-700" : "text-red-700"}`}>
              {result.correct ? "Correct" : "Not quite"} - {result.feedback}
            </p>
          )}
        </div>
      ) : (
        <p className="mt-6 text-black/60">{busy ? "Loading..." : "No drills found."}</p>
      )}
    </div>
  );
}
