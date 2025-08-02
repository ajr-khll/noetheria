"use client";

import { useParams, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import ChatInput from "@/components/ChatInput";
import ChatHistory from "@/components/ChatHistory";
import AuthButton from "@/components/AuthButton";
import LoadingIcon from "@/components/LoadingIcon";
import { useChatStore } from "@/stores/chatStores";
import ReactMarkdown from "react-markdown";
import { FiClock } from "react-icons/fi";
import { useSession } from "next-auth/react";

type FollowUp = {
  question: string;
  answer: string | null;
};

const getFontSizeClass = (length: number) => {
  if (length < 60) return "text-5xl";
  if (length < 120) return "text-4xl";
  if (length < 180) return "text-3xl";
  return "text-2xl";
};

const createSession = async (initial_question: string, accessToken?: string) => {
  const baseUrl = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8080";
  const headers: Record<string, string> = { "Content-Type": "application/json" };
  if (accessToken) headers['Authorization'] = `Bearer ${accessToken}`;

  const res = await fetch(`${baseUrl}/session`, {
    method: "POST",
    headers,
    body: JSON.stringify({ initial_question }),
  });
  return res.ok ? await res.json() : null;
};

const loadExistingSession = async (sessionId: string, accessToken?: string) => {
  const baseUrl = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8080";
  const headers: Record<string, string> = {};
  if (accessToken) headers['Authorization'] = `Bearer ${accessToken}`;

  const res = await fetch(`${baseUrl}/chat_history/${sessionId}`, { headers });
  return res.ok ? await res.json() : null;
};

export default function ChatThread() {
  const initialQuestion = useChatStore((s) => s.initialQuestion);
  const { isLoading, setIsLoading, loadingMessage, setLoadingMessage } = useChatStore();
  const router = useRouter();
  const params = useParams();
  const { data: session } = useSession();

  const [sessionId, setSessionId] = useState<string | null>(null);
  const [followUpQuestions, setFollowUpQuestions] = useState<string[]>([]);
  const [answers, setAnswers] = useState<(string | null)[]>([]);
  const [shortAnswer, setShortAnswer] = useState<string | null>(null);
  const [currentStep, setCurrentStep] = useState(0);
  const [displayQuestion, setDisplayQuestion] = useState<string>("");
  const [showQuestion, setShowQuestion] = useState(false);
  const [isFollowUp, setIsFollowUp] = useState<boolean | null>(null);
  const [isHistoricalSession, setIsHistoricalSession] = useState(false);
  const [downloadedSites, setDownloadedSites] = useState<string[]>([]);
  const [searchLinks, setSearchLinks] = useState<string[]>([]);
  const [finalResult, setFinalResult] = useState<string>("");
  const [isResearching, setIsResearching] = useState(false);
  const [eventSourceCleanup, setEventSourceCleanup] = useState<(() => void) | null>(null);
  const [showHistory, setShowHistory] = useState(false);

  useEffect(() => {
    const urlSessionId = params.id as string;

    if (urlSessionId && !initialQuestion) {
      setIsLoading(true);
      setLoadingMessage("Loading chat history...");

      loadExistingSession(urlSessionId, session?.accessToken).then((data) => {
        if (!data) {
          router.push("/");
          return;
        }

        setSessionId(data.id);
        setDisplayQuestion(data.initial_question);
        setShowQuestion(true);
        setIsHistoricalSession(true);

        if (data.followups && data.followups.length > 0) {
          const followups = data.followups as FollowUp[];
          setIsFollowUp(true);
          setFollowUpQuestions(followups.map((f) => f.question));
          setAnswers(followups.map((f) => f.answer));
          setCurrentStep(followups.length);
        } else {
          setIsFollowUp(false);
          setShortAnswer(data.short_answer);
        }

        if (data.final_answer) {
          setFinalResult(data.final_answer);
        }

        setIsLoading(false);
      });
      return;
    }

    if (initialQuestion) {
      setDisplayQuestion(initialQuestion);
      setShowQuestion(true);
      setIsLoading(true);
      setLoadingMessage("Creating research session...");

      createSession(initialQuestion, session?.accessToken).then((data) => {
        if (!data) {
          setIsLoading(false);
          return;
        }

        setSessionId(data.session_id);

        if (data.mode === "followup") {
          const followups = data.followups as FollowUp[];
          setIsFollowUp(true);
          setFollowUpQuestions(followups.map((f) => f.question));
          setAnswers([]);
        } else {
          setIsFollowUp(false);
          setShortAnswer(data.short_answer);
        }

        setIsLoading(false);
      });
      return;
    }

    router.push("/");
  }, [initialQuestion, params.id]);

  useEffect(() => {
    return () => {
      if (eventSourceCleanup) eventSourceCleanup();
    };
  }, [eventSourceCleanup]);

  const fetchLinks = async (id: string) => {
    const baseUrl = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:5000";
    setIsLoading(true);
    setLoadingMessage("Finding relevant sources...");

    const res = await fetch(`${baseUrl}/session/${id}/get_links`);
    if (!res.ok) return setIsLoading(false);

    const data = await res.json();
    const links = Array.from(data.links || []) as string[];
    setSearchLinks(links);
    setLoadingMessage("Starting site downloads...");
    const cleanup = startSiteDownload(id, links);
    setEventSourceCleanup(() => cleanup);
  };

  const startSiteDownload = async (id: string, links: string[]) => {
    const baseUrl = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:5000";

    await fetch(`${baseUrl}/session/${id}/download_sites`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ links }),
    });

    const eventSource = new EventSource(`${baseUrl}/session/${id}/progress_stream`);
    eventSource.onmessage = (event) => {
      if (event.data === "__done__") {
        eventSource.close();
        setIsLoading(false);
        startDeepResearch(id);
      } else {
        setDownloadedSites((prev) => [...prev, event.data]);
      }
    };

    return () => {
      eventSource.close();
    };
  };

  const submitAnswer = async (answer: string, idx: number) => {
    if (!sessionId) return;
    const baseUrl = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:5000";

    const res = await fetch(`${baseUrl}/answer`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ session_id: sessionId, question_index: idx, answer }),
    });

    if (res.ok) {
      setAnswers((prev) => [...prev, answer]);
      const nextStep = idx + 1;
      if (nextStep === followUpQuestions.length) {
        fetchLinks(sessionId);
      }
      setCurrentStep(nextStep);
    }
  };

  const startDeepResearch = async (id: string) => {
    const baseUrl = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:5000";
    setIsResearching(true);
    setFinalResult("");

    const res = await fetch(`${baseUrl}/session/${id}/deep_research`, { method: "POST" });
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

    try {
      const formattedRes = await fetch(`${baseUrl}/session/${id}/formatted_response`);
      const data = await formattedRes.json();
      if (data.formatted) setFinalResult(data.formatted);
    } catch (err) {
      console.error("Failed to load formatted response:", err);
    }

    setIsResearching(false);
  };

  return (
    <main className="flex flex-col items-center min-h-screen bg-zinc-900 text-white px-6 pt-6 pb-40 relative">
      {/* Top Navigation */}
      <div className="absolute top-6 left-6 right-6 flex items-center justify-between z-10">
        <AuthButton />
        <button
          onClick={() => setShowHistory(true)}
          className="flex items-center gap-2 px-4 py-2 bg-zinc-800 hover:bg-zinc-700 text-zinc-300 hover:text-white rounded-lg transition-colors"
        >
          <FiClock className="w-4 h-4" />
          History
        </button>
      </div>

      {/* Loading State */}
      {isLoading && (
        <div className="flex flex-col items-center justify-center min-h-screen">
          <LoadingIcon message={loadingMessage || "Loading..."} size="lg" />
        </div>
      )}

      {/* Question Display */}
      {!isLoading && showQuestion && (
        <div className="w-full max-w-4xl mt-20 mb-8">
          <div className="text-center mb-8">
            <h1 className={`font-bold text-white mb-4 ${getFontSizeClass(displayQuestion.length)}`}>
              {displayQuestion}
            </h1>
          </div>

          {/* Short Answer */}
          {!isFollowUp && shortAnswer && (
            <div className="bg-zinc-800 rounded-lg p-6 mb-8">
              <h2 className="text-xl font-semibold mb-4 text-blue-400">Quick Answer:</h2>
              <p className="text-zinc-300 leading-relaxed">{shortAnswer}</p>
            </div>
          )}

          {/* Follow-up Questions */}
          {isFollowUp && followUpQuestions.length > 0 && (
            <div className="space-y-6">
              {followUpQuestions.map((question, idx) => (
                <div key={idx} className="bg-zinc-800 rounded-lg p-6">
                  <h3 className="text-lg font-medium mb-4 text-blue-400">
                    Question {idx + 1}: {question}
                  </h3>
                  
                  {answers[idx] ? (
                    <div className="bg-zinc-700 rounded p-4">
                      <p className="text-zinc-300">{answers[idx]}</p>
                    </div>
                  ) : idx === currentStep ? (
                    <div className="space-y-4">
                      <textarea
                        id={`answer-${idx}`}
                        placeholder="Enter your answer..."
                        className="w-full p-4 bg-zinc-700 border border-zinc-600 rounded-lg text-white placeholder-zinc-400 focus:outline-none focus:border-blue-500"
                        rows={4}
                      />
                      <button
                        onClick={() => {
                          const textarea = document.getElementById(`answer-${idx}`) as HTMLTextAreaElement;
                          if (textarea?.value.trim()) {
                            submitAnswer(textarea.value.trim(), idx);
                          }
                        }}
                        className="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
                      >
                        Submit Answer
                      </button>
                    </div>
                  ) : (
                    <p className="text-zinc-500 italic">Waiting for previous answers...</p>
                  )}
                </div>
              ))}
            </div>
          )}

          {/* Research Progress */}
          {searchLinks.length > 0 && (
            <div className="mt-8 bg-zinc-800 rounded-lg p-6">
              <h3 className="text-lg font-semibold mb-4 text-green-400">Research Sources Found:</h3>
              <p className="text-zinc-300 mb-4">Found {searchLinks.length} relevant sources</p>
              
              {downloadedSites.length > 0 && (
                <div className="space-y-2">
                  <h4 className="font-medium text-zinc-400">Downloaded:</h4>
                  <div className="max-h-40 overflow-y-auto space-y-1">
                    {downloadedSites.map((site, idx) => (
                      <div key={idx} className="text-sm text-zinc-500 font-mono">
                        {site}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Final Result */}
          {isResearching && (
            <div className="mt-8">
              <LoadingIcon message="Analyzing collected content and generating final answer..." size="md" />
            </div>
          )}
          
          {finalResult && (
            <div className="mt-8 bg-zinc-800 rounded-lg p-6">
              <h3 className="text-xl font-semibold mb-4 text-green-400">Research Results:</h3>
              <div className="prose prose-invert max-w-none">
                <ReactMarkdown
                  components={{
                    a: ({ children, ...props }) => (
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
            </div>
          )}
        </div>
      )}

      {/* Chat History Modal */}
      <ChatHistory 
        isOpen={showHistory} 
        onClose={() => setShowHistory(false)}
      />
    </main>
  );
}
