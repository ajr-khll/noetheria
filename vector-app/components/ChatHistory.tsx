"use client";

import { useState, useEffect } from "react";
import { FiClock, FiTrash2, FiSearch } from "react-icons/fi";
import { useRouter } from "next/navigation";
import { useSession } from "next-auth/react";

interface ChatHistoryItem {
  id: string;
  initial_question: string;
  created_at: string;
  completed_at: string;
  short_answer?: string;
  preview?: string;
}

interface ChatHistoryProps {
  onSelectChat?: (sessionId: string) => void;
  isOpen: boolean;
  onClose: () => void;
}

export default function ChatHistory({ onSelectChat, isOpen, onClose }: ChatHistoryProps) {
  const [history, setHistory] = useState<ChatHistoryItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");
  const router = useRouter();
  const { data: session, status } = useSession();

  const fetchHistory = async () => {
    // Don't fetch if not authenticated
    if (status !== "authenticated" || !session?.accessToken) {
      setHistory([]);
      return;
    }

    setLoading(true);
    try {
      const baseUrl = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8080";
      const res = await fetch(`${baseUrl}/chat_history`, {
        headers: {
          'Authorization': `Bearer ${session.accessToken}`,
        },
      });
      if (res.ok) {
        const data = await res.json();
        setHistory(data.history || []);
      } else if (res.status === 401) {
        console.log("User not authenticated");
        setHistory([]);
      }
    } catch (error) {
      console.error("Failed to fetch chat history:", error);
    } finally {
      setLoading(false);
    }
  };

  const deleteChat = async (sessionId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!confirm("Are you sure you want to delete this chat?")) return;
    if (!session?.accessToken) return;

    try {
      const baseUrl = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8080";
      const res = await fetch(`${baseUrl}/chat_history/${sessionId}`, {
        method: "DELETE",
        headers: {
          'Authorization': `Bearer ${session.accessToken}`,
        },
      });
      if (res.ok) {
        setHistory(prev => prev.filter(item => item.id !== sessionId));
      }
    } catch (error) {
      console.error("Failed to delete chat:", error);
    }
  };

  const handleChatSelect = (sessionId: string) => {
    if (onSelectChat) {
      onSelectChat(sessionId);
    } else {
      router.push(`/chat/${sessionId}`);
    }
    onClose();
  };

  useEffect(() => {
    if (isOpen) {
      fetchHistory();
    }
  }, [isOpen, session, status]);

  const filteredHistory = history.filter(item =>
    item.initial_question.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

    if (diffDays === 0) {
      return "Today";
    } else if (diffDays === 1) {
      return "Yesterday";
    } else if (diffDays < 7) {
      return `${diffDays} days ago`;
    } else {
      return date.toLocaleDateString();
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div className="bg-zinc-800 rounded-lg max-w-4xl w-full max-h-[80vh] overflow-hidden">
        {/* Header */}
        <div className="p-6 border-b border-zinc-700">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold text-white">Chat History</h2>
            <button
              onClick={onClose}
              className="text-zinc-400 hover:text-white transition-colors"
            >
              ✕
            </button>
          </div>
          
          {/* Search */}
          <div className="relative">
            <FiSearch className="absolute left-3 top-1/2 transform -translate-y-1/2 text-zinc-400" />
            <input
              type="text"
              placeholder="Search chat history..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full bg-zinc-700 text-white pl-10 pr-4 py-2 rounded border border-zinc-600 focus:border-blue-500 focus:outline-none"
            />
          </div>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto max-h-[60vh]">
          {status === "loading" ? (
            <div className="text-center text-zinc-400 py-8">Loading...</div>
          ) : status !== "authenticated" ? (
            <div className="text-center text-zinc-400 py-8">
              <p className="mb-4">Please sign in to view your chat history.</p>
              <p className="text-sm text-zinc-500">Your conversations will be saved and private to your account.</p>
            </div>
          ) : loading ? (
            <div className="text-center text-zinc-400 py-8">Loading...</div>
          ) : filteredHistory.length === 0 ? (
            <div className="text-center text-zinc-400 py-8">
              {searchTerm ? "No chats found matching your search." : "No chat history yet."}
            </div>
          ) : (
            <div className="space-y-4">
              {filteredHistory.map((item) => (
                <div
                  key={item.id}
                  onClick={() => handleChatSelect(item.id)}
                  className="bg-zinc-700 rounded-lg p-4 cursor-pointer hover:bg-zinc-600 transition-colors group"
                >
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1 min-w-0">
                      <h3 className="text-white font-medium mb-2 line-clamp-2">
                        {item.initial_question}
                      </h3>
                      
                      {item.preview && (
                        <p className="text-zinc-300 text-sm mb-2 line-clamp-2">
                          {item.preview}
                        </p>
                      )}
                      
                      <div className="flex items-center gap-2 text-xs text-zinc-400">
                        <FiClock className="w-3 h-3" />
                        <span>{formatDate(item.completed_at || item.created_at)}</span>
                      </div>
                    </div>
                    
                    <button
                      onClick={(e) => deleteChat(item.id, e)}
                      className="opacity-0 group-hover:opacity-100 text-zinc-400 hover:text-red-400 transition-all p-2"
                      title="Delete chat"
                    >
                      <FiTrash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}