"use client";

import { useEffect, useRef, useState } from "react";
import Link from "next/link";
import { api, CompanyCount, MockSession, Scorecard, speak } from "@/lib/api";

const TRACKS = ["swe", "data", "quant"];
const ROUNDS = ["coding", "system_design", "behavioral", "oa"];

export default function MockPage() {
  const [companies, setCompanies] = useState<CompanyCount[]>([]);
  const [company, setCompany] = useState("");
  const [track, setTrack] = useState("swe");
  const [round, setRound] = useState("coding");
  const [session, setSession] = useState<MockSession | null>(null);
  const [message, setMessage] = useState("");
  const [card, setCard] = useState<Scorecard | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [limitHit, setLimitHit] = useState(false);
  const [voice, setVoice] = useState(false);
  const [listening, setListening] = useState(false);
  const recognitionRef = useRef<any>(null);
  const lastSpokenRef = useRef<number>(-1);

  useEffect(() => {
    api.companies().then((c) => {
      setCompanies(c);
      if (c[0]) setCompany(c[0].company);
    }).catch((e) => setError(String(e)));
  }, []);

  // Speak each new interviewer turn when voice mode is on.
  useEffect(() => {
    if (!voice || !session) return;
    const turns = session.turns;
    const last = turns[turns.length - 1];
    if (last && last.speaker === "interviewer" && last.position > lastSpokenRef.current) {
      lastSpokenRef.current = last.position;
      speak(last.content);
    }
  }, [session, voice]);

  function handleError(e: unknown) {
    const msg = String(e);
    if (msg.startsWith("Error: 402")) setLimitHit(true);
    else setError(msg);
  }

  async function start() {
    setBusy(true); setError(""); setCard(null); setLimitHit(false); lastSpokenRef.current = -1;
    try {
      setSession(await api.startMock(company, track, round));
    } catch (e) { handleError(e); } finally { setBusy(false); }
  }

  async function send() {
    if (!session || !message.trim()) return;
    setBusy(true);
    try {
      setSession(await api.message(session.id, message));
      setMessage("");
    } catch (e) { handleError(e); } finally { setBusy(false); }
  }

  async function grade() {
    if (!session) return;
    setBusy(true);
    try { setCard(await api.grade(session.id)); }
    catch (e) { handleError(e); } finally { setBusy(false); }
  }

  function toggleMic() {
    const SR = (typeof window !== "undefined" &&
      ((window as any).webkitSpeechRecognition || (window as any).SpeechRecognition)) as any;
    if (!SR) { setError("Speech recognition is not supported in this browser."); return; }
    if (listening) { recognitionRef.current?.stop(); return; }
    const rec = new SR();
    rec.lang = "en-US";
    rec.interimResults = false;
    rec.onresult = (ev: any) => setMessage((m) => (m + " " + ev.results[0][0].transcript).trim());
    rec.onend = () => setListening(false);
    rec.start();
    recognitionRef.current = rec;
    setListening(true);
  }

  return (
    <div>
      <div className="flex flex-wrap items-center justify-between gap-2">
        <h1 className="font-display text-3xl font-black sm:text-4xl">Mock Agent</h1>
        <label className="flex items-center gap-2 text-sm font-semibold">
          <input type="checkbox" checked={voice} onChange={(e) => setVoice(e.target.checked)} />
          Voice mode
        </label>
      </div>
      <p className="mt-2 text-black/70">Live interview on a real question, graded by the mentor rubric.</p>

      {error && <p className="mt-4 text-sm text-red-700">{error}</p>}
      {limitHit && (
        <div className="card mt-4 p-4">
          <p className="text-sm">You hit the free monthly mock limit.{" "}
            <Link href="/pricing" className="font-semibold" style={{ color: "var(--teal)" }}>
              Upgrade to Pro
            </Link>{" "}for unlimited graded mocks.</p>
        </div>
      )}

      <div className="card mt-6 flex flex-wrap items-end gap-4 p-5">
        <label className="text-sm font-semibold">
          Company
          <select className="mt-1 block rounded border border-black/20 bg-white p-2"
            value={company} onChange={(e) => setCompany(e.target.value)}>
            {companies.map((c) => <option key={c.company} value={c.company}>{c.company} ({c.count})</option>)}
          </select>
        </label>
        <label className="text-sm font-semibold">
          Track
          <select className="mt-1 block rounded border border-black/20 bg-white p-2"
            value={track} onChange={(e) => setTrack(e.target.value)}>
            {TRACKS.map((t) => <option key={t}>{t}</option>)}
          </select>
        </label>
        <label className="text-sm font-semibold">
          Round
          <select className="mt-1 block rounded border border-black/20 bg-white p-2"
            value={round} onChange={(e) => setRound(e.target.value)}>
            {ROUNDS.map((r) => <option key={r}>{r}</option>)}
          </select>
        </label>
        <button className="btn" onClick={start} disabled={busy || !company}>Start</button>
      </div>

      {session && (
        <div className="mt-8 grid gap-6 md:grid-cols-3">
          <div className="md:col-span-2">
            <div className="card p-5">
              <p className="text-xs uppercase tracking-wide text-black/50">
                {session.company} - {session.round} - hints used: {session.hints_used}
              </p>
              {session.question && (
                <p className="font-display mt-2 text-lg font-bold">{session.question.title}</p>
              )}
              <div className="mt-4 space-y-3">
                {session.turns.map((t) => (
                  <div key={t.position}
                    className={`whitespace-pre-wrap break-words rounded-lg p-3 text-sm ${t.speaker === "interviewer" ? "bg-teal-50" : "bg-black/5"}`}>
                    <span className="block text-xs font-bold uppercase text-black/40">
                      {t.speaker}{t.is_hint ? " - hint" : ""}
                    </span>
                    {t.content}
                  </div>
                ))}
              </div>
              {session.status === "active" && (
                <div className="mt-4 flex flex-wrap gap-2">
                  <input className="min-w-0 flex-1 basis-full rounded border border-black/20 bg-white p-2 text-sm sm:basis-0"
                    placeholder="Type your response..." value={message}
                    onChange={(e) => setMessage(e.target.value)}
                    onKeyDown={(e) => e.key === "Enter" && send()} />
                  {voice && (
                    <button className="btn" style={{ background: listening ? "var(--amber)" : "var(--ink)" }}
                      onClick={toggleMic}>{listening ? "Stop" : "Speak"}</button>
                  )}
                  <button className="btn" onClick={send} disabled={busy}>Send</button>
                </div>
              )}
              <button className="btn mt-4" style={{ background: "var(--ink)" }}
                onClick={grade} disabled={busy}>Finish & grade</button>
            </div>
          </div>

          <div>
            {card && (
              <div className="card p-5">
                <p className="text-xs uppercase tracking-wide text-black/50">Scorecard</p>
                <p className="font-display text-5xl font-black" style={{ color: "var(--teal)" }}>
                  {card.overall.toFixed(1)}
                </p>
                <p className="text-sm font-bold uppercase">{card.recommendation.replace("_", " ")}</p>
                <ul className="mt-4 space-y-2 text-sm">
                  {card.breakdown.map((b) => (
                    <li key={b.criterion}>
                      <span className="font-semibold">{b.criterion}: {b.score}</span>
                      <span className="block text-black/60">{b.justification}</span>
                    </li>
                  ))}
                </ul>
                {card.improvements && (
                  <p className="mt-4 text-sm"><b>Improve:</b> {card.improvements}</p>
                )}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
