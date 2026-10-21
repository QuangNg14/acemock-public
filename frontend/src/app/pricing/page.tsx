"use client";

import { useEffect, useState } from "react";
import { api, BillingMe } from "@/lib/api";
import UpgradeButton from "@/components/UpgradeButton";

const FREE = [
  "3 graded mocks / month",
  "Browse all company question banks",
  "Behavioral value mapping",
  "Basic quant drills",
];
const PRO = [
  "Unlimited graded mocks",
  "Full per-criterion scorecard deep dive",
  "Solutions for questions and quant drills",
  "Voice mode (ElevenLabs)",
];
const QUANT = [
  "All firm-specific tracks",
  "Timed mental-math and market-making",
  "Full solution walkthroughs",
  "Probability and brainteaser sets",
];

export default function PricingPage() {
  const [me, setMe] = useState<BillingMe | null>(null);

  useEffect(() => {
    api.billingMe().then(setMe).catch(() => setMe(null));
  }, []);

  return (
    <div>
      <h1 className="font-display text-3xl font-black sm:text-4xl">Pricing</h1>
      <p className="mt-2 text-black/70">
        {me?.is_pro ? "You are on Pro. Thank you." : "Start free. Upgrade when you want the answer key."}
      </p>

      <div className="mt-8 grid gap-6 md:grid-cols-3">
        <Plan name="Free" price="$0" features={FREE} />
        <Plan name="Pro" price="$18/mo" features={PRO} highlight
          cta={me?.is_pro ? <span className="chip" style={{ color: "var(--teal)" }}>Active</span> : <UpgradeButton plan="pro" />} />
        <Plan name="QuantReady" price="$39/mo" features={QUANT}
          cta={<UpgradeButton plan="quant" label="Get QuantReady" />} />
      </div>
    </div>
  );
}

function Plan({
  name, price, features, highlight, cta,
}: {
  name: string; price: string; features: string[]; highlight?: boolean; cta?: React.ReactNode;
}) {
  return (
    <div className="card p-6" style={highlight ? { borderColor: "var(--teal)" } : undefined}>
      <h2 className="font-display text-2xl font-bold">{name}</h2>
      <p className="font-display mt-1 text-4xl font-black" style={{ color: "var(--teal)" }}>{price}</p>
      <ul className="mt-4 space-y-2 text-sm text-black/70">
        {features.map((f) => <li key={f}>- {f}</li>)}
      </ul>
      <div className="mt-6">{cta}</div>
    </div>
  );
}
