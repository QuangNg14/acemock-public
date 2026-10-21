import Link from "next/link";

const surfaces = [
  {
    href: "/mock",
    name: "Mock Agent",
    blurb:
      "A live AI interviewer asks real questions for your target company, then grades you against a calibrated mentor rubric with a hint ladder.",
    tag: "SWE / Data",
  },
  {
    href: "/behavioral",
    name: "Behavioral Engine",
    blurb:
      "Turn raw experiences into a STAR story bank auto-mapped to each company's values, then drill them with strict structure and specificity scoring.",
    tag: "Every candidate",
  },
  {
    href: "/quant",
    name: "QuantReady",
    blurb:
      "Brainteaser, probability, mental-math, and market-making drills with firm-specific tracks for Jane Street, Optiver, Citadel, and more.",
    tag: "IB / Quant",
  },
];

export default function Home() {
  return (
    <div>
      <section className="py-10 sm:py-12">
        <p className="chip inline-block" style={{ color: "var(--teal)" }}>
          Graded, not guessed
        </p>
        <h1 className="font-display mt-5 text-4xl font-black leading-[1.0] sm:text-5xl md:text-6xl md:leading-[0.95]">
          Real questions.
          <br />
          A real <span style={{ color: "var(--teal)" }}>answer key</span>.
        </h1>
        <p className="mt-6 max-w-2xl text-base text-black/70 sm:text-lg">
          AceMock runs a live AI interview on actual company questions and scores you against a
          mentor-calibrated rubric, not a generic opinion. Three surfaces, one loop: practice,
          get graded, improve.
        </p>
        <div className="mt-8 flex flex-wrap gap-3 sm:gap-4">
          <Link href="/mock" className="btn">Start a mock interview</Link>
          <Link href="/quant" className="btn" style={{ background: "var(--ink)" }}>
            Try QuantReady
          </Link>
        </div>
      </section>

      <section className="grid gap-6 py-8 md:grid-cols-3">
        {surfaces.map((s) => (
          <Link key={s.href} href={s.href} className="card p-6 transition hover:-translate-y-1">
            <span className="chip" style={{ color: "var(--teal)" }}>{s.tag}</span>
            <h2 className="font-display mt-4 text-2xl font-bold">{s.name}</h2>
            <p className="mt-3 text-sm text-black/70">{s.blurb}</p>
          </Link>
        ))}
      </section>
    </div>
  );
}
