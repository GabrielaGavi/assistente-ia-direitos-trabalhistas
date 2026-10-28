"use client";

import { useState, type ReactNode } from "react";

const items = [
  ["About Us", "#principios"], ["Insights", "#recursos"],
  ["Case Studies", "#depoimentos"], ["Case Studies Details", "#depoimentos"],
  ["Contact", "#comecar"],
];

export function MobileNavigation({ variant, children }: { variant: "phone" | "tablet"; children: ReactNode }) {
  const [open, setOpen] = useState(false);
  const closedVariant = variant === "phone" ? "1ohqsr3" : "1mrntuk";
  const openVariant = variant === "phone" ? "27hnyu" : "1wn8ysw";
  return <div className={`framer-WYfR8 framer-185sxef framer-v-${open ? openVariant : closedVariant}${open ? " landingMobileOpen" : ""}`}
    data-framer-name={variant === "phone" ? "Phone" : "Tablet Closed"}
    style={{ width: "100%", opacity: 1, transform: "none", backgroundColor: open ? "rgb(248,248,243)" : "transparent" }}
    onClick={event => {
      const target = event.target as Element;
      if (target.closest(".framer-5tvets")) setOpen(value => !value);
      else if (target.closest("a")) setOpen(false);
    }}
    onKeyDown={event => {
      if (event.key === "Escape") setOpen(false);
      if ((event.key === "Enter" || event.key === " ") && (event.target as Element).closest(".framer-5tvets")) {
        event.preventDefault(); setOpen(value => !value);
      }
    }}>
    {children}
    {open ? <nav className="framer-fwilei" aria-label="Menu principal" style={{ backgroundColor: "rgb(248,248,243)" }}>
      {items.map(([label, href]) => <div key={label} className="framer-6x5h2g landingMobileLinks">
        <a href={href}>{label}</a>
      </div>)}
    </nav> : null}
  </div>;
}
