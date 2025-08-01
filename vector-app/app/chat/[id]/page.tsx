"use client";

import { useParams, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import ChatInput from "@/components/ChatInput";
import { useChatStore } from "@/stores/chatStores";
import ReactMarkdown from "react-markdown";

const getFontSizeClass = (length: number) => {
  if (length < 60) return "text-5xl";
  if (length < 120) return "text-4xl";
  if (length < 180) return "text-3xl";
  return "text-2xl";
};

const createSession = async (initial_question: string) => {
  const res = await fetch("http://localhost:5000/session", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ initial_question }),
  });
  return res.ok ? await res.json() : null;
};

export default function ChatThread() {
  const initialQuestion = useChatStore((s) => s.initialQuestion);
  const router = useRouter();

  const [sessionId, setSessionId] = useState<string | null>(null);
  const [followUpQuestions, setFollowUpQuestions] = useState<string[]>([]);
  const [showQuestion, setShowQuestion] = useState(false);
  const [isFollowUp, setIsFollowUp] = useState<boolean | null>(null);
  const [currentStep, setCurrentStep] = useState(0);
  const [answers, setAnswers] = useState<string[]>([]);
  const [shortAnswer, setShortAnswer] = useState<string | null>(null);
  const [downloadedSites, setDownloadedSites] = useState<string[]>([]);
  const [searchLinks, setSearchLinks] = useState<string[]>([]);
  const [finalResult, setFinalResult] = useState<string>("");
  const [isResearching, setIsResearching] = useState(false);
  const [eventSourceCleanup, setEventSourceCleanup] = useState<(() => void) | null>(null);

  // On mount, create session
  useEffect(() => {
    if (!initialQuestion) {
      router.push("/");
      return;
    }

    setShowQuestion(true);

    createSession(initialQuestion).then((data) => {
      if (!data) return;
      setSessionId(data.session_id);

      if (data.mode === "followup") {
        setIsFollowUp(true);
        setFollowUpQuestions(data.followups || []);
      } else {
        setIsFollowUp(false);
        setShortAnswer(data.short_answer);
      }
    });
  }, [initialQuestion]);

  // Cleanup EventSource on component unmount
  useEffect(() => {
    return () => {
      if (eventSourceCleanup) {
        eventSourceCleanup();
      }
    };
  }, [eventSourceCleanup]);

  const fetchLinks = async (id: string) => {
    const res = await fetch(`http://localhost:5000/session/${id}/get_links`);
    
    if (!res.ok) return;

    const data = await res.json();
    const links = Array.from(data.links || []) as string[];
    console.log(links)
    setSearchLinks(links); // still useful if UI uses it
    const cleanup = startSiteDownload(id, links); // ✅ pass directly
    setEventSourceCleanup(() => cleanup);
  };

  const startSiteDownload = async (id: string, links: string[]) => {
    console.log("📦 Sending links:", links);
  
    await fetch(`http://localhost:5000/session/${id}/download_sites`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ links }),
    });
  
    const eventSource = new EventSource(`http://localhost:5000/session/${id}/progress_stream`);
    eventSource.onmessage = (event) => {
      if (event.data === "__done__") {
        eventSource.close();
        startDeepResearch(id); // 🧠 Begin deep research now
      } else {
        setDownloadedSites((prev) => [...prev, event.data]);
      }
    };

    // Cleanup function for EventSource
    return () => {
      eventSource.close();
    };
  };
  
  const submitAnswer = async (answer: string, idx: number) => {
    if (!sessionId) return;

    const res = await fetch("http://localhost:5000/answer", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        session_id: sessionId,
        question_index: idx,
        answer,
      }),
    });

    if (res.ok) {
      setAnswers((prev) => [...prev, answer]);
      const nextStep = idx + 1;

      if (nextStep === followUpQuestions.length && sessionId) {
        fetchLinks(sessionId); // 🎯 Start full process once follow-ups are complete
      }

      setCurrentStep(nextStep);
    }
  };

  const startDeepResearch = async (id: string) => {
    setIsResearching(true);
    setFinalResult(""); // clear any previous results
  
    const res = await fetch(`http://localhost:5000/session/${id}/deep_research`, {
      method: "POST",
    });
  
    if (!res.body) {
      setFinalResult("[Error: No response body]");
      setIsResearching(false);
      return;
    }
  
    const reader = res.body.getReader();
    const decoder = new TextDecoder("utf-8");
  
    while (true) {
      const { value, done } = await reader.read();
      if (done) break;
      const chunk = decoder.decode(value, { stream: true });
      setFinalResult((prev) => prev + chunk);
    }
  
    // ✅ Step 2: After stream finishes, fetch the formatted result
    try {
      const formattedRes = await fetch(`http://localhost:5000/session/${id}/formatted_response`);
      const data = await formattedRes.json();
  
      if (data.formatted) {
        setFinalResult(data.formatted); // 🔄 Replace with formatted output
      }
    } catch (err) {
      console.error("Failed to load formatted response:", err);
    }
  
    setIsResearching(false);
  };
  

  return (
    <main className="flex flex-col items-center min-h-screen bg-zinc-900 text-white px-6 pt-6 pb-40 relative">
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
        .fade-in {
          opacity: 0;
          animation: fadeIn 0.6s ease forwards;
        }
      `}</style>

      {/* Initial question display */}
      {initialQuestion && (
        <div className="w-full max-w-screen-lg text-right mb-4">
          <div
            className={`font-semibold leading-tight whitespace-pre-wrap break-words transition-opacity duration-700 ${
              showQuestion ? "opacity-100" : "opacity-0"
            } ${getFontSizeClass(initialQuestion.length)}`}
          >
            {initialQuestion}
          </div>
        </div>
      )}

      <hr className="w-full max-w-screen-lg border-zinc-700 my-2" />

      <div className="w-full max-w-screen-lg text-left mt-4 space-y-4">
        {isFollowUp === false && shortAnswer && (
          <p className="text-lg text-zinc-300 whitespace-pre-wrap break-words fade-in">
            {shortAnswer}
          </p>
        )}

        {isFollowUp &&
          followUpQuestions.slice(0, currentStep + 1).map((q, idx) => (
            <div
              key={idx}
              className="space-y-2 fade-in"
              style={{ animationDelay: `${idx * 0.3}s`, animationFillMode: "forwards" }}
            >
              <p className="text-zinc-300">{q}</p>
              {idx === currentStep ? (
                <form
                  onSubmit={(e) => {
                    e.preventDefault();
                    const input = (e.currentTarget.elements.namedItem("answer") as HTMLInputElement).value.trim();
                    if (input) submitAnswer(input, idx);
                  }}
                  className="flex flex-col sm:flex-row gap-2"
                >
                  <input
                    name="answer"
                    type="text"
                    autoFocus
                    className="flex-1 bg-zinc-800 px-4 py-2 rounded text-white"
                    placeholder="Type your response..."
                  />
                  <button
                    type="button"
                    onClick={() => submitAnswer("Not sure", idx)}
                    className="bg-zinc-700 hover:bg-zinc-600 text-sm text-white px-4 py-2 rounded"
                  >
                    Not sure
                  </button>
                </form>
              ) : (
                <p className="text-green-400">{answers[idx]}</p>
              )}
            </div>
          ))}

        {/* Progress List */}
        {downloadedSites.length > 0 && (
  <div className="mt-8">
  <h3 className="text-white mb-2">Download Progress:</h3>
  <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
    {downloadedSites.map((msg, i) => {
      const [status, urlRaw] = msg.split(/:\s(.+)/);
      const url = urlRaw?.trim() || "";
      let domain = "";

      try {
        domain = new URL(url).hostname;
      } catch {
        domain = "Invalid URL";
      }

      const getStatusColor = () => {
        if (status.includes("loaded")) return "text-green-400";
        if (status.includes("skipped")) return "text-yellow-400";
        if (status.includes("error")) return "text-red-400";
        return "text-zinc-400";
      };

      return (
        <div
          key={i}
          className="flex items-center gap-3 p-3 rounded bg-zinc-800 border border-zinc-700 shadow"
        >
          <img
            src={`https://www.google.com/s2/favicons?domain=${domain}&sz=32`}
            alt="favicon"
            className="w-6 h-6 rounded"
          />
          <div className="flex-1 min-w-0">
            <a
              href={url}
              target="_blank"
              rel="noopener noreferrer"
              className={`truncate block ${getStatusColor()} hover:underline`}
              title={url}
            >
              {domain}
            </a>
            <span className="text-xs text-zinc-500">{status}</span>
          </div>
        </div>
      );
    })}
  </div>
</div>

)}

{downloadedSites.length > 0 && (
  <div className="mt-12 fade-in">
    <div className="bg-zinc-800 border border-zinc-700 rounded-lg p-6 shadow-lg text-zinc-300 whitespace-pre-wrap leading-relaxed min-h-[120px]">
      {isResearching && (
        <p className="text-zinc-500 italic animate-pulse">Analyzing collected content...</p>
      )}
      {!isResearching && finalResult.trim() === "" && (
        <p className="text-zinc-400 italic">No final result available.</p>
      )}
      {finalResult && (
        <div className="prose prose-invert max-w-none">
          <ReactMarkdown
            components={{
              a: ({ node, children, ...props }) => (
                <a
                  {...props}
                  className="ml-1 inline-block text-xs font-medium px-2 py-0.5 bg-zinc-700 text-blue-300 rounded-full hover:bg-zinc-600 transition-colors"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  {children}
                </a>
              ),
            }}
          >
            {finalResult}
          </ReactMarkdown>
        </div>
      )}
    </div>
  </div>
)}
      </div>

      <div className="fixed bottom-0 left-0 w-full px-6 py-4 bg-zinc-900 border-t border-zinc-800 shadow-[0_-4px_12px_rgba(0,0,0,0.3)] z-50">
        <div className="max-w-screen-lg mx-auto">
          <ChatInput onSend={() => {}} hasMessages={!!initialQuestion} />
        </div>
      </div>
    </main>
  );
}

