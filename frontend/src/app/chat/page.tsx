import { Suspense } from "react";
import { ChatEntry } from "@/components/chat-entry";

export default function ChatPage() {
  return <Suspense fallback={<main className="chatLoading" role="status">Abrindo sua conversa…</main>}><ChatEntry /></Suspense>;
}
