"use client";

import { useSession, signIn, signOut } from "next-auth/react";
import { FiUser, FiLogOut } from "react-icons/fi";
import { FcGoogle } from "react-icons/fc";

export default function AuthButton() {
  const { data: session, status } = useSession();

  if (status === "loading") {
    return (
      <div className="flex items-center gap-2 px-4 py-2 bg-zinc-800 text-zinc-400 rounded-lg">
        <div className="w-4 h-4 animate-spin rounded-full border-2 border-zinc-600 border-t-zinc-400"></div>
        <span className="text-sm">Loading...</span>
      </div>
    );
  }

  if (session) {
    return (
      <div className="flex items-center gap-3">
        {/* User Profile */}
        <div className="flex items-center gap-2 px-3 py-2 bg-zinc-800 rounded-lg">
          {session.user?.image ? (
            <img
              src={session.user.image}
              alt={session.user.name || "User"}
              className="w-6 h-6 rounded-full"
            />
          ) : (
            <FiUser className="w-4 h-4 text-zinc-400" />
          )}
          <span className="text-sm text-white max-w-[120px] truncate">
            {session.user?.name}
          </span>
        </div>

        {/* Sign Out Button */}
        <button
          onClick={() => signOut()}
          className="flex items-center gap-2 px-3 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors"
          title="Sign out"
        >
          <FiLogOut className="w-4 h-4" />
          <span className="text-sm">Sign Out</span>
        </button>
      </div>
    );
  }

  return (
    <button
      onClick={() => signIn("google")}
      className="flex items-center gap-2 px-4 py-2 bg-white hover:bg-gray-50 text-gray-800 rounded-lg transition-colors border border-gray-300 shadow-sm"
    >
      <FcGoogle className="w-5 h-5" />
      <span className="text-sm font-medium">Sign in with Google</span>
    </button>
  );
}