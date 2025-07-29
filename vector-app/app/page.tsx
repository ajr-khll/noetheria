"use client";

import { useState } from "react";
import ChatInput from "@/components/ChatInput";
import TypingTitle from "@/components/TypingTitle";
import { useChatStore } from "@/stores/chatStores";

export default function Home() {
  const [messages, setMessages] = useState<string[]>([]);

  const sendMessage = async (content: string) => {
    setMessages(prev => [...prev, content]);
  };

  return (
    <main className="relative flex flex-col items-center justify-center h-screen bg-zinc-900 text-white">
      {/* 🧠 Animated Title */}
      {messages.length === 0 && <TypingTitle />}

      {/* 💬 Chat input */}
      <ChatInput onSend={sendMessage} hasMessages={messages.length > 0} floating />
    </main>
  );
}
