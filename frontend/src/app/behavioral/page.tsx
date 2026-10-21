"use client";

import { useState } from "react";
import { api } from "@/lib/api";

export default function BehavioralPage() {
  const [form, setForm] = useState({
    title: "", situation: "", task: "", action: "", result: "", company: "Amazon",
  });
  const [storyId, setStoryId] = useState<string | null>(null);
  const [mapped, setMapped] = useState<{ value: string; evidence: string }[]>([]);
  const [value, setValue] = useState("Ownership");
  const [answer, setAnswer] = useState("");
  const [grade, setGrade] = useState<Awaited<ReturnType<typeof api.gradeDrill>> | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  function set(k: keyof typeof form, v: string) {
    setForm((f) => ({ ...f, [k]: v }));
  }

  async function createStory() {
    setBusy(true); setError("");
    try {
      const s = await api.createStory({
        title: form.title, situation: form.situation, task: form.task,
        action: form.action, result: form.result, target_companies: [form.company],
      });
      setStoryId(s.id); setMapped(s.mapped_values ?? []);
    } catch (e) { setError(String(e)); } finally { setBusy(false); }
  }

  async function drill() {
    if (!storyId) return;
    setBusy(true); setError("");
    try {
      setGrade(await api.gradeDrill({ story_id: storyId, company: form.company, value_probed: value, answer }));
    } catch (e) { setError(String(e)); } finally { setBusy(false); }
  }

  return (
    <div>
      <h1 className="font-display text-3xl font-black sm:text-4xl">Behavioral Engine</h1>
      <p className="mt-2 text-black/70">Build a STAR story, map it to company values, then drill it under strict scoring.</p>
      {error && <p className="mt-4 text-sm text-red-700">{error}</p>}

      <div className="mt-6 grid gap-6 md:grid-cols-2">
        <div className="card p-5">
          <h2 className="font-display text-xl font-bold">1. Your story</h2>
          <input className="mt-3 w-full rounded border border-black/20 p-2 text-sm" placeholder="Title"
            value={form.title} onChange={(e) => set("title", e.target.value)} />
          {(["situation", "task", "action", "result"] as const).map((k) => (
            <textarea key={k} className="mt-2 w-full rounded border border-black/20 p-2 text-sm"
              placeholder={k[0].toUpperCase() + k.slice(1)} rows={2}
              value={form[k]} onChange={(e) => set(k, e.target.value)} />
          ))}
          <input className="mt-2 w-full rounded border border-black/20 p-2 text-sm" placeholder="Target company"
            value={form.company} onChange={(e) => set("company", e.target.value)} />
          <button className="btn mt-3" onClick={createStory} disabled={busy}>Map to values</button>

          {mapped.length > 0 && (
            <ul className="mt-4 space-y-2 text-sm">
              {mapped.map((m, i) => (
                <li key={i}><span className="chip" style={{ color: "var(--teal)" }}>{m.value}</span>
                  <span className="ml-2 text-black/60">{m.evidence}</span></li>
              ))}
            </ul>
          )}
        </div>

        <div className="card p-5">
          <h2 className="font-display text-xl font-bold">2. Drill</h2>
          <p className="mt-1 text-sm text-black/60">Answer the probe; get structure + specificity scores.</p>
          <input className="mt-3 w-full rounded border border-black/20 p-2 text-sm" placeholder="Value probed (e.g. Ownership)"
            value={value} onChange={(e) => setValue(e.target.value)} />
          <textarea className="mt-2 w-full rounded border border-black/20 p-2 text-sm" rows={6}
            placeholder="Tell me about a time you..." value={answer} onChange={(e) => setAnswer(e.target.value)} />
          <button className="btn mt-3" onClick={drill} disabled={busy || !storyId}>Grade answer</button>

          {grade && (
            <div className="mt-4 text-sm">
              <p className="font-display text-3xl font-black" style={{ color: "var(--teal)" }}>
                {grade.score?.toFixed(1)}
              </p>
              <p>Structure {grade.structure_score} - Specificity {grade.specificity_score}</p>
              <p className="mt-2"><b>Feedback:</b> {grade.feedback}</p>
              {grade.followups?.length > 0 && (
                <ul className="mt-2 list-disc pl-5 text-black/70">
                  {grade.followups.map((f, i) => <li key={i}>{f}</li>)}
                </ul>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
