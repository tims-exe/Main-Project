import { redirect } from "next/navigation";
import { getServerSession } from "@/lib/server-auth";
import LogoutButton from "@/components/ui/button/LogoutButton";
import ChatButton from "@/components/ui/button/ChatButton";
import Conversations from "@/components/chat/Conversations";

export default async function Home() {
  const session = await getServerSession();

  if (!session) {
    redirect("/login");
  }

  const { user } = session;

  return (
    <div className="h-screen flex flex-col">
      {/* Header */}
      <header className="flex justify-between items-center px-8 py-6 border-b">
        <h1 className="text-2xl font-semibold">Conversations</h1>

        <div className="flex items-center gap-4">
          <div className="text-right">
            <p className="font-semibold">
              {user.first_name} {user.last_name}
            </p>
            <p className="text-sm text-muted-foreground">{user.email}</p>
          </div>
          <LogoutButton />
        </div>
      </header>

      {/* Conversations list */}
      <main className="flex-1 overflow-y-auto px-8 py-6">
        <Conversations />
      </main>

      {/* Bottom center chat button */}
      <div className="pb-6 flex justify-center">
        <ChatButton />
      </div>
    </div>
  );
}


{
  /* <div className="p-8">
            <h1 className="text-3xl font-bold mb-4">
                Welcome, {user.first_name || 'User'}!
            </h1>
            <div className="bg-white shadow rounded-lg p-6 max-w-md">
                <div className="space-y-3">
                    <p>
                        <strong>Email:</strong> {user.email}
                    </p>
                    <p>
                        <strong>Name:</strong> {user.first_name} {user.last_name}
                    </p>
                </div>
                <LogoutButton />
            </div>
        </div> */
}
