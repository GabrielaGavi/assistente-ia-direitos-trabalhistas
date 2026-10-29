import { LandingPage } from "@/components/landing/landing-page";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Direito em claro | Informação trabalhista com fontes",
  description: "Orientação trabalhista clara, fundamentada e acompanhada de fontes que você pode conferir.",
};

export default function Home() { return <LandingPage />; }
