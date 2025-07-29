import "./globals.css";
import { ReactNode } from "react";

export const metadata = {
  title: "Vector",
  description: "VECTORRRRRRR",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body className="bg-zinc-900 text-white">{children}</body>
    </html>
  );
}