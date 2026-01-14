"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import ConversationCard from "../ui/ConversationCard";
import { getAllConversations, deleteConversation } from "@/lib/api";
import { Conversation } from "@/types/auth";

export default function Conversations() {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  useEffect(() => {
    fetchConversations();
  }, []);

  const fetchConversations = async () => {
    try {
      const response = await getAllConversations();
      setConversations(response.data);
    } catch {
      setError("Failed to load conversations");
    } finally {
      setIsLoading(false);
    }
  };

  const handleDeleteConversation = async (id: string) => {
    try {
      await deleteConversation(id);
      setConversations(prev => prev.filter(c => c.id !== id));
    } catch {
      setError("Failed to delete conversation");
    }
  };

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-500" />
      </div>
    );
  }

  return (
    <>
      {error && (
        <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {conversations.length === 0 ? (
          <div className="col-span-full text-center py-16">
            <p className="text-gray-500 text-lg">No conversations yet</p>
            <p className="text-gray-400 text-sm mt-1">
              Start a new chat to get going
            </p>
          </div>
        ) : (
          conversations.map(conv => (
            <ConversationCard
              key={conv.id}
              id={conv.id}
              title={conv.title}
              date={new Date(conv.created_at).toLocaleDateString("en-GB", {
                day: "numeric",
                month: "short",
                year: "numeric",
              })}
              onDelete={handleDeleteConversation}
              onClick={id => router.push(`/chat/${id}`)}
            />
          ))
        )}
      </div>
    </>
  );
}
