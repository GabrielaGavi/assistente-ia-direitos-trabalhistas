"use client";

export function LandingPrice({ monthly, yearly, annual }: { monthly: string; yearly: string; annual: boolean }) {
  const amount = annual ? yearly : monthly;
  const period = annual ? "/yr" : "/mo";
  return <div className="framer-fk9wqm-container">
    <span aria-label={`$${amount}${period}`} style={{ position: "relative", display: "inline-flex", alignItems: "baseline", whiteSpace: "nowrap", color: "rgb(26,26,28)", fontVariantNumeric: "tabular-nums", fontFamily: '"Inter Tight", "Inter Tight Placeholder", sans-serif', fontSize: 20, fontStyle: "normal", fontWeight: 400, letterSpacing: "0em", lineHeight: "1.2em" }}>
      <span aria-hidden="true">$</span>
      <span key={amount} className="landingPriceAmount" aria-hidden="true" style={{ display: "inline-block", whiteSpace: "nowrap" }}>{amount}</span>
      <span aria-hidden="true" style={{ position: "relative", display: "inline-block", whiteSpace: "nowrap" }}>{period}</span>
    </span>
  </div>;
}
