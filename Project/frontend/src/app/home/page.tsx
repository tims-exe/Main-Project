import { redirect } from "next/navigation";
import { getServerSession } from "@/lib/server-auth";
import LogoutButton from "@/components/ui/button/LogoutButton";
import ChatButton from "@/components/ui/button/ChatButton";

export default async function Home() {
  const session = await getServerSession();

  if (!session) {
    redirect("/login");
  }

  const { user } = session;

  return (
    <div className="h-screen flex flex-col justify-between p-10">
      <div className="flex justify-between w-full">
        <p className="font-semibold text-2xl">Home Page</p>
        <div className="flex items-center gap-4">
          <div className="text-end">
            <p className="font-semibold text-xl">
              {user.first_name} {user.last_name}
            </p>
            <p>{user.email}</p>
          </div>
          <LogoutButton />
        </div>
      </div>

      <div className="flex justify-center items-center flex-1">
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
