"use client";

import { useSearchParams } from "next/navigation";
import { chatTopics } from "@/lib/chat-topics";
import { ChatShell } from "./chat-shell";

export function ChatEntry() {
  const query = useSearchParams();
  const topic = chatTopics.find(item => item.id === query.get("tema"));
  const preset = (query.get("q") ?? topic?.prompt ?? "").slice(0, 4000);
  return <ChatShell key={`${topic?.id ?? ""}:${preset}`} initialDraft={preset} initialTopic={topic?.id} />;
}
