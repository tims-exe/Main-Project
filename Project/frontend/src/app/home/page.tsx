import { redirect } from "next/navigation";
import { getServerSession } from "@/lib/server-auth";
import Navbar from "@/components/ui/Navbar";
import ChatButton from "@/components/ui/button/ChatButton";
import Conversations from "@/components/chat/Conversations";

export default async function Home() {
  const session = await getServerSession();

  if (!session) redirect("/login");

  return (
    <div className="h-screen flex flex-col bg-gray-50">
      <Navbar user={session.user} />

      <main className="flex-1 overflow-y-auto px-8 py-6">
        <h1 className="text-2xl font-bold text-gray-800 mb-6">
          Conversations
        </h1>
        <Conversations />
      </main>

      <div className="pb-6 flex justify-center bg-gray-50">
        <ChatButton />
      </div>
    </div>
  );
}
