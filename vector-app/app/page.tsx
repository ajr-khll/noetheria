"use client";

import { useState } from "react";
import ChatInput from "@/components/ChatInput";
import ChatHistory from "@/components/ChatHistory";
import AuthButton from "@/components/AuthButton";
import TypingTitle from "@/components/TypingTitle";
import { useChatStore } from "@/stores/chatStores";
import { FiClock } from "react-icons/fi";

export default function Home() {
  const [messages, setMessages] = useState<string[]>([]);
  const [showHistory, setShowHistory] = useState(false);

  const sendMessage = async (content: string) => {
    setMessages(prev => [...prev, content]);
  };

  return (
    <main className="relative flex flex-col items-center justify-center h-screen bg-zinc-900 text-white">
      {/* Top Navigation */}
      <div className="absolute top-6 left-6 right-6 flex items-center justify-between">
        {/* Left side - Auth Button */}
        <AuthButton />
        
        {/* Right side - Chat History Button */}
        <button
          onClick={() => setShowHistory(true)}
          className="flex items-center gap-2 px-4 py-2 bg-zinc-800 hover:bg-zinc-700 text-zinc-300 hover:text-white rounded-lg transition-colors"
        >
          <FiClock className="w-4 h-4" />
          History
        </button>
      </div>

      {/* 🧠 Animated Title */}
      {messages.length === 0 && <TypingTitle />}

      {/* 💬 Chat input */}
      <ChatInput onSend={sendMessage} hasMessages={messages.length > 0} floating />

      {/* Chat History Modal */}
      <ChatHistory 
        isOpen={showHistory} 
        onClose={() => setShowHistory(false)}
      />
    </main>
  );
}
