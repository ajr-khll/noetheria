"use client";

import { useParams, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import ChatInput from "@/components/ChatInput";
import { useChatStore } from "@/stores/chatStores";

// Font sizing logic
const getFontSizeClass = (length: number) => {
  if (length < 60) return "text-5xl";
  if (length < 120) return "text-4xl";
  if (length < 180) return "text-3xl";
  return "text-2xl";
};

const listOfSites = [
  "arxiv.org",
  "researchgate.net",
  "jstor.org",
  "sciencedirect.com",
  "springer.com",
  "wiley.com",
  "tandfonline.com",
  "cambridge.org",
  "mdpi.com",
  "sagepub.com"
];

const followUpQuestions = [
  "Can you clarify the scope of your research?",
  "Which regions or time periods are you focused on?",
  "Are there specific methodologies you want to prioritize?"
];

export default function ChatThread() {
  const { id } = useParams();
  const initialQuestion = useChatStore((s) => s.initialQuestion);
  const router = useRouter();

  const [showQuestion, setShowQuestion] = useState(false);
  const [visibleSites, setVisibleSites] = useState<string[]>([]);
  const [isFollowUp, setIsFollowUp] = useState<boolean | null>(null);
  const [currentStep, setCurrentStep] = useState(0);
  const [answers, setAnswers] = useState<string[]>([]);
  const [shortAnswer, setShortAnswer] = useState<string | null>(null);

  useEffect(() => {
    if (!initialQuestion) {
      router.push("/");
    } else {
      setTimeout(() => setShowQuestion(true), 50);
      setTimeout(() => {
        const followMode = true; // flip to false to test short answer
        setIsFollowUp(followMode);
        if (!followMode) {
          setShortAnswer("This is a brief direct response to your question.");
        }
      }, 800);
    }
  }, [initialQuestion]);

  useEffect(() => {
    listOfSites.forEach((site, i) => {
      setTimeout(() => {
        setVisibleSites((prev) => [...prev, site]);
      }, i * 150);
    });
  }, []);

  const handleFollowUpSubmit = (e: React.FormEvent<HTMLFormElement>, idx: number) => {
    e.preventDefault();
    const input = (e.currentTarget.elements.namedItem("answer") as HTMLInputElement).value.trim();
    if (!input) return;

    setAnswers((prev) => [...prev, input]);
    setCurrentStep(idx + 1);
  };

  return (
    <main className="flex flex-col items-center min-h-screen bg-zinc-900 text-white px-6 pt-6 pb-40 relative">
      {/* Fade-in animation style block */}
      <style jsx>{`
        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(10px); }
          to { opacity: 1; transform: translateY(0); }
        }
        .fade-in {
          opacity: 0;
          animation: fadeIn 0.6s ease forwards;
        }
      `}</style>

      {/* Initial Question */}
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

      {initialQuestion && showQuestion && (
        <hr className="w-full max-w-screen-lg border-zinc-700 my-2" />
      )}

      {/* Answer area */}
      <div className="w-full max-w-screen-lg text-left mt-4 space-y-4">
        {/* Short answer */}
        {isFollowUp === false && shortAnswer && (
          <p className="text-lg text-zinc-300 whitespace-pre-wrap break-words fade-in">
            {shortAnswer}
          </p>
        )}

        {/* Follow-up logic */}
        {isFollowUp &&
          followUpQuestions.slice(0, currentStep + 1).map((q, idx) => (
            <div
              key={idx}
              className="space-y-2 fade-in"
              style={{ animationDelay: `${idx * 0.3}s`, animationFillMode: "forwards" }}
            >
              <p className="text-zinc-300">{q}</p>
              {idx === currentStep ? (
                <form onSubmit={(e) => handleFollowUpSubmit(e, idx)} className="flex flex-col sm:flex-row gap-2">
                <input
                  name="answer"
                  type="text"
                  autoFocus
                  className="flex-1 bg-zinc-800 px-4 py-2 rounded text-white"
                  placeholder="Type your response..."
                />
                <button
                  type="button"
                  onClick={() => {
                    setAnswers((prev) => [...prev, "Not sure"]);
                    setCurrentStep(idx + 1);
                  }}
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

        {/* Favicon grid */}
        <div className="mt-6 grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
          {listOfSites.map((domain) => (
            <div
              key={domain}
              className={`flex items-center space-x-3 transition-opacity duration-500 ${
                visibleSites.includes(domain) ? "opacity-100" : "opacity-0"
              }`}
            >
              <img
                src={`https://www.google.com/s2/favicons?sz=64&domain=${domain}`}
                alt={`${domain} favicon`}
                className="w-6 h-6"
              />
              <span className="text-sm text-white">{domain}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Chat input at the bottom */}
      <div className="fixed bottom-0 left-0 w-full px-6 py-4 bg-zinc-900 border-t border-zinc-800 shadow-[0_-4px_12px_rgba(0,0,0,0.3)] z-50">
        <div className="max-w-screen-lg mx-auto">
          <ChatInput onSend={() => {}} hasMessages={!!initialQuestion} />
        </div>
      </div>
    </main>
  );
}
