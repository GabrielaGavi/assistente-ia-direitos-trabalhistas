import type { Metadata } from "next";
import localFont from "next/font/local";
import { SmoothScroll } from "@/components/smooth-scroll";
import { SessionProvider } from "@/components/session-provider";
import "./globals.css";

const geistSans = localFont({ src: "./fonts/geist-latin-variable.woff2", weight: "100 900", variable: "--font-geist-sans", display: "swap" });
const geistMono = localFont({ src: "./fonts/geist-mono-latin-variable.woff2", weight: "100 900", variable: "--font-geist-mono", display: "swap" });

export const metadata: Metadata = { title: "Assistente de Direitos Trabalhistas", description: "Orientação trabalhista clara, com fontes oficiais." };

export default function RootLayout({ children }: LayoutProps<"/">) {
  return <html lang="pt-BR" className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}><body className="min-h-full flex flex-col"><SessionProvider><SmoothScroll />{children}</SessionProvider></body></html>;
}
