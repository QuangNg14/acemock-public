import { getAuthToken } from "./auth-bridge";

const API = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

async function req<T>(path: string, init?: RequestInit): Promise<T> {
  const token = await getAuthToken();
  const res = await fetch(`${API}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...(init?.headers ?? {}),
    },
  });
  if (!res.ok) {
    const detail = await res.text();
    throw new Error(`${res.status}: ${detail}`);
  }
  return res.json() as Promise<T>;
}

export interface CompanyCount {
  company: string;
  count: number;
}

export interface Turn {
  position: number;
  speaker: string;
  content: string;
  is_hint: boolean;
}

export interface MockSession {
  id: string;
  company: string;
  track: string;
  round: string;
  status: string;
  hints_used: number;
  question: { title: string; prompt: string } | null;
  turns: Turn[];
}

export interface Scorecard {
  overall: number;
  recommendation: string;
  breakdown: { criterion: string; score: number; weight: number; justification: string }[];
  strengths: string | null;
  improvements: string | null;
}

export interface QuantDrill {
  id: string;
  category: string;
  difficulty: string;
  firm_tracks: string | null;
  prompt: string;
  time_limit_seconds: number | null;
}

export interface BillingMe {
  authenticated: boolean;
  is_pro: boolean;
  email: string | null;
}

export const api = {
  companies: () => req<CompanyCount[]>("/questions/companies"),
  startMock: (company: string, track = "swe", round = "coding") =>
    req<MockSession>("/mock/start", {
      method: "POST",
      body: JSON.stringify({ company, track, round }),
    }),
  message: (id: string, content: string) =>
    req<MockSession>(`/mock/${id}/message`, {
      method: "POST",
      body: JSON.stringify({ content }),
    }),
  grade: (id: string) => req<Scorecard>(`/mock/${id}/grade`, { method: "POST" }),
  quantDrills: (firm?: string) =>
    req<QuantDrill[]>(`/quant/drills${firm ? `?firm=${encodeURIComponent(firm)}` : ""}`),
  quantAttempt: (drill_id: string, response: string, elapsed_seconds?: number) =>
    req<{ correct: boolean; feedback: string | null; reasoning_quality: number | null }>(
      "/quant/attempts",
      { method: "POST", body: JSON.stringify({ drill_id, response, elapsed_seconds }) },
    ),
  createStory: (body: {
    title: string;
    situation: string;
    task: string;
    action: string;
    result: string;
    target_companies: string[];
  }) => req<{ id: string; title: string; mapped_values: { value: string; evidence: string }[] }>(
    "/behavioral/stories",
    { method: "POST", body: JSON.stringify(body) },
  ),
  gradeDrill: (body: { story_id: string; company: string; value_probed: string; answer: string }) =>
    req<{
      score: number | null;
      structure_score: number | null;
      specificity_score: number | null;
      feedback: string | null;
      followups: string[];
    }>("/behavioral/drills", { method: "POST", body: JSON.stringify(body) }),

  billingMe: () => req<BillingMe>("/billing/me"),
  checkout: (plan = "pro") =>
    req<{ url: string }>("/billing/checkout", {
      method: "POST",
      body: JSON.stringify({ plan }),
    }),
  portal: () => req<{ url: string }>("/billing/portal", { method: "POST" }),
  voiceStatus: () => req<{ tts: boolean; stt: boolean }>("/voice/status"),
};

// Speak text using server-side ElevenLabs TTS when configured, falling back to
// the free browser speechSynthesis API otherwise.
export async function speak(text: string): Promise<void> {
  const token = await getAuthToken();
  try {
    const res = await fetch(`${API}/voice/tts`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      body: JSON.stringify({ text }),
    });
    if (res.ok) {
      const blob = await res.blob();
      const audio = new Audio(URL.createObjectURL(blob));
      await audio.play();
      return;
    }
  } catch {
    // fall through to browser TTS
  }
  if (typeof window !== "undefined" && "speechSynthesis" in window) {
    window.speechSynthesis.cancel();
    window.speechSynthesis.speak(new SpeechSynthesisUtterance(text));
  }
}
