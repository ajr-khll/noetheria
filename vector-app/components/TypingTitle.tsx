"use client";

import { Typewriter } from "react-simple-typewriter";

export default function TypingTitle() {
  return (
    <h1 className="text-center text-2xl md:text-3xl text-white font-medium mb-8 -mt-25">
      <Typewriter
        words={["Deep research, now."]}
        loop={1}
        cursor
        cursorStyle="_"
        typeSpeed={100}
        deleteSpeed={0}
        delaySpeed={1000}
      />
    </h1>
  );
}