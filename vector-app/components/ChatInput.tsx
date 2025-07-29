"use client";

import { useState, useRef, useEffect } from "react";
import { FiSend } from "react-icons/fi";
import clsx from "clsx";
import { v4 as uuidv4 } from "uuid";
import { useRouter } from "next/navigation";
import { useChatStore } from "@/stores/chatStores";

const placeholders = [
  "Perform a literature review on...",
  "What are the most cited papers on...",
  "Summarize competing theories around...",
  "What are the open research questions in...",
  "Compare methodologies used in studies on...",
  "Trace the historical evolution of ideas about...",
  "Synthesize current findings in the field of...",
  "Identify key contributors and papers in...",
  "What’s the consensus and controversy around...",
  "Extract common variables from studies on...",
  "Analyze gaps in existing research on...",
  "What datasets are used most often to study...",
  "What frameworks have been proposed for...",
  "List the most influential books written about...",
  "What technical challenges remain in...",
  "What does the latest meta-analysis say about...",
  "Design a multi-step research plan to investigate...",
  "Break down a case study relevant to...",
  "What are the epistemological assumptions behind...",
  "Map out the schools of thought in...",
  "Identify common metrics used to evaluate...",
  "Compare quantitative and qualitative research on...",
  "Extract definitions of key terms from academic sources on...",
  "How do different fields conceptualize...",
  "Review experimental setups commonly used in...",
  "What longitudinal studies exist about...",
  "Generate a timeline of important discoveries in...",
  "What are recent breakthroughs in...",
  "Summarize white papers and reports related to...",
  "Find contradictory findings in research about...",
  "What predictive models are used in studying...",
  "Extract methodological flaws in studies of...",
  "What ethical considerations arise when researching...",
  "Design a research question and hypothesis for...",
  "Summarize working papers or preprints discussing...",
  "What policy recommendations emerge from research on...",
  "What interdisciplinary insights exist on..."
];

export default function ChatInput({
  onSend,
  hasMessages,
  floating = false
}: {
  onSend: (msg: string) => void;
  hasMessages: boolean;
  floating?: boolean;
}) {
  const router = useRouter();
  const [input, setInput] = useState("");
  const [hasAnimated, setHasAnimated] = useState(false);
  const [placeholderIndex, setPlaceholderIndex] = useState(0);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const shuffled = [...placeholders].sort(() => 0.5 - Math.random());

  useEffect(() => {
    const interval = setInterval(() => {
      setPlaceholderIndex(Math.floor(Math.random() * shuffled.length));
    }, 5000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (hasMessages && !hasAnimated) {
      setHasAnimated(true);
    }
  }, [hasMessages]);

  useEffect(() => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = "auto";
      textarea.style.height = `${textarea.scrollHeight}px`;
    }
  }, [input]);

  const setInitialQuestion = useChatStore((s) => s.setInitialQuestion);
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;
    const id = uuidv4();
    setInitialQuestion(input.trim());
    router.push(`/chat/${id}`);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <form
      onSubmit={handleSubmit}
      className={clsx(
        "w-full px-4",
        floating
          ? "max-w-xl absolute top-1/2 left-1/2 z-50 transition-transform duration-700 ease-in-out"
          : "max-w"
      )}
      
      style={
        floating
          ? {
              transform: hasAnimated
                ? "translate(-50%, 200px)"
                : "translate(-50%, -50%)"
            }
          : undefined
      }
      
    >
      <div className="flex items-end bg-zinc-800 p-2 rounded-[24px] shadow-xl w-full">
        <textarea
          ref={textareaRef}
          className="flex-1 bg-transparent resize-none outline-none text-sm text-white px-4 py-2 max-h-48 overflow-y-auto scrollbar-thin scrollbar-thumb-zinc-600 scrollbar-track-transparent"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={placeholders[placeholderIndex]}
          rows={1}
          maxLength={200}
        />
        <p className="text-xs text-zinc-400 text-right mt-1">
          {input.length} / 200
        </p>
        <button type="submit" className="p-2">
          <FiSend className="text-white text-xl" />
        </button>
      </div>
    </form>
  );
}
