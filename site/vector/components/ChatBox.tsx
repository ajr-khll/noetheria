"use client";

import { useState, useEffect, useRef } from "react";

export default function ChatBox() {
  const [messages, setMessages] = useState<{ role: string; content: string }[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [hasStarted, setHasStarted] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto scroll to bottom when messages change
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    // Mark that chat has started for the layout transition
    if (!hasStarted) {
      setHasStarted(true);
    }

    const newMessages = [...messages, { role: "user", content: input }];
    setMessages(newMessages);
    setInput("");
    setLoading(true);

    try {
      const res = await fetch("http://localhost:3000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt: input }),
      });

      const data = await res.json();
      setMessages([...newMessages, { role: "assistant", content: data.reply }]);
    } catch (err) {
      setMessages([...newMessages, { role: "assistant", content: "Error getting response." }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 transition-all duration-700">
      {/* Initial centered layout - before first message */}
      {!hasStarted && (
        <div className="flex flex-col items-center justify-center min-h-screen p-4 transition-all duration-700">
          <h1 className="text-2xl font-semibold mb-6 text-white">How can I help?</h1>
          
          <form onSubmit={handleSubmit} className="w-full max-w-xl flex">
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Type your message..."
              className="flex-grow border border-gray-600 bg-gray-700 text-white placeholder-gray-400 rounded-l px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              autoFocus
            />
            <button
              type="submit"
              disabled={!input.trim()}
              className="bg-blue-600 text-white px-4 py-2 rounded-r hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed transition-colors duration-200"
            >
              Send
            </button>
          </form>
        </div>
      )}

      {/* Chat layout - after first message */}
      {hasStarted && (
        <>
          {/* Header */}
          <div className="border-b border-gray-700 p-4 pt-12 bg-gray-900">
            <div className="w-full text-center">
              <h1 className="text-2xl font-semibold text-white">Vector</h1>
            </div>
          </div>

          {/* Messages area - scrollable with bottom padding for input */}
          <div className="overflow-y-auto bg-gray-900" style={{height: 'calc(100vh - 200px)', paddingBottom: '20px'}}>
            <div className="w-full max-w-5xl mx-auto p-4 space-y-4">
              {messages.map((msg, i) => (
                <div 
                  key={i} 
                  className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"} animate-fadeIn`}
                  style={{
                    animation: `fadeIn 0.5s ease-out ${i * 0.1}s both`
                  }}
                >
                  <div
                    className={`p-3 rounded-lg max-w-xs lg:max-w-2xl ${
                      msg.role === "user" 
                        ? "bg-blue-600 text-white" 
                        : "bg-gray-700 text-gray-100 border border-gray-600"
                    }`}
                  >
                    {msg.content}
                  </div>
                </div>
              ))}
              
              {loading && (
                <div className="flex justify-start animate-pulse">
                  <div className="bg-gray-700 border border-gray-600 px-4 py-3 rounded-lg">
                    <div className="text-gray-400 italic">Thinking...</div>
                  </div>
                </div>
              )}
              
              {/* Invisible div to scroll to */}
              <div ref={messagesEndRef} />
            </div>
          </div>
        </>
      )}

      {/* Input box - ALWAYS fixed at bottom when hasStarted is true */}
      {hasStarted && (
        <div className="fixed bottom-0 left-0 right-0 z-50 border-t border-gray-700 p-4 bg-gray-900">
          <form onSubmit={handleSubmit} className="w-full mx-auto flex" style={{paddingLeft: '10%', paddingRight: '10%'}}>
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Type your message..."
              className="flex-grow border border-gray-600 bg-gray-700 text-white placeholder-gray-400 rounded-l px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none"
              style={{height: '120px'}}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleSubmit(e);
                }
              }}
            />
            <button
              type="submit"
              disabled={!input.trim() || loading}
              className="bg-blue-600 text-white px-4 py-2 rounded-r hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed transition-colors duration-200 self-end"
            >
              Send
            </button>
          </form>
        </div>
      )}

      <style jsx>{`
        @keyframes fadeIn {
          from {
            opacity: 0;
            transform: translateY(10px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
        .animate-fadeIn {
          animation: fadeIn 0.5s ease-out forwards;
        }
      `}</style>
    </div>
  );
}