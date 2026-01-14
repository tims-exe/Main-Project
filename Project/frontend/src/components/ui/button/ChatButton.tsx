"use client";

import { useRouter } from "next/navigation";
import { createConversation } from "@/lib/api";
import { useState } from "react";
import { AxiosError } from "axios";

export default function ChatButton() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);

  const handleNewChat = async () => {
    try {
      setLoading(true);
      const response = await createConversation();
      router.push(`/chat/${response.data.id}`);
    } catch (err) {
      console.error(err as AxiosError);
      alert("Failed to start a new chat");
    } finally {
      setLoading(false);
    }
  };

  return (
    <button
      onClick={handleNewChat}
      disabled={loading}
      className="bg-purple-600 text-white rounded-full hover:bg-purple-700
             transition-all duration-200 py-3 px-8 text-base font-medium
             w-[280px] disabled:opacity-50 shadow-lg hover:shadow-xl
             transform hover:-translate-y-0.5 active:translate-y-0
             cursor-pointer disabled:cursor-not-allowed"
    >
      {loading ? "Starting..." : "New Chat"}
    </button>
  );
}
