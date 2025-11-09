import ChatClient from "@/components/chat/ChatClient";
import Navbar from "@/components/ui/Navbar";
import { getServerSession } from "@/lib/server-auth";
import { redirect } from "next/navigation";

export default async function Chat() {
  const session = await getServerSession()

  if (!session) {
    redirect("/login")
  }

  return (
    <div className="h-screen flex flex-col bg-gradient-to-br from-gray-50 via-blue-100/10 to-gray-100">
      <Navbar />

      <main className="flex-1 overflow-hidden px-4 sm:px-6 lg:px-8 py-6">
        <div className="h-full max-w-7xl mx-auto">
          <div className="h-full bg-white rounded-3xl shadow-xl overflow-hidden border border-gray-100">
            <div className="h-full grid lg:grid-cols-4">
              <ChatClient />
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}