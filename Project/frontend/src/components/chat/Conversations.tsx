"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import ConversationCard from "../ui/ConversationCard";
import { 
  getAllConversations, 
  createConversation, 
  deleteConversation 
} from "@/lib/api";
import { Conversation } from "@/types/auth";
import { AxiosError } from "axios";

export default function Conversations() {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  useEffect(() => {
    fetchConversations();
  }, []);

  const fetchConversations = async (): Promise<void> => {
    try {
      const response = await getAllConversations();
      setConversations(response.data);
      setError(null);
    } catch (err) {
      const error = err as AxiosError;
      console.error("Error fetching conversations:", error);
      setError("Failed to load conversations");
    } finally {
      setIsLoading(false);
    }
  };

  const handleCreateConversation = async (): Promise<void> => {
    try {
      const response = await createConversation();
      const newConv = response.data;
      router.push(`/chat/${newConv.id}`);
    } catch (err) {
      const error = err as AxiosError;
      console.error("Error creating conversation:", error);
      setError("Failed to create conversation");
    }
  };

  const handleDeleteConversation = async (id: string): Promise<void> => {
    try {
      await deleteConversation(id);
      setConversations(conversations.filter(conv => conv.id !== id));
      setError(null);
    } catch (err) {
      const error = err as AxiosError;
      console.error("Error deleting conversation:", error);
      setError("Failed to delete conversation");
    }
  };

  const handleConversationClick = (id: string): void => {
    router.push(`/chat/${id}`);
  };

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-500"></div>
      </div>
    );
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold">Conversations</h2>
        <button
          onClick={handleCreateConversation}
          className="px-4 py-2 bg-purple-500 text-white rounded-lg hover:bg-purple-600 transition"
        >
          New Chat
        </button>
      </div>

      {error && (
        <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
          {error}
        </div>
      )}
      
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {conversations.length === 0 ? (
          <div className="col-span-full text-center py-12 text-gray-500">
            No conversations yet.
          </div>
        ) : (
          conversations.map((conv) => (
            <ConversationCard
              key={conv.id}
              id={conv.id}
              title={conv.title}
              date={new Date(conv.created_at).toLocaleDateString('en-GB', {
                day: 'numeric',
                month: 'short',
                year: 'numeric'
              })}
              onDelete={handleDeleteConversation}
              onClick={handleConversationClick}
            />
          ))
        )}
      </div>
    </div>
  );
}