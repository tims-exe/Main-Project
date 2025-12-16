import { redirect } from "next/navigation";
import { getServerSession } from "@/lib/server-auth";
import GoogleAuthButton from "@/components/auth/GoogleAuthButton";
import BackHomeButton from "@/components/ui/button/BackHomeButton";

export default async function Login() {
  const session = await getServerSession();

  if (session) {
    redirect("/home");
  }

  return (
    <div className="min-h-screen bg-white flex flex-col justify-center items-center px-4">
      <div className="max-w-md w-full space-y-8">
        {/* Logo/Brand */}
        <div className="text-center space-y-2">
          <h1 className="text-5xl font-bold text-purple-600">
            SentiCore
          </h1>
          <p className="text-gray-600">
            Welcome back
          </p>
        </div>

        {/* Login Card */}
        <div className="bg-white border border-purple-100 rounded-2xl p-8 shadow-sm">
          <div className="space-y-6">
            <div className="text-center space-y-2">
              <h2 className="text-2xl font-semibold text-gray-800">
                Sign in to continue
              </h2>
              <p className="text-sm text-gray-600">
                Access your conversations and chat history
              </p>
            </div>

            {/* Google Sign In Button */}
            <GoogleAuthButton />

            <div className="text-center">
              <p className="text-xs text-gray-500">
                By signing in, you agree to our Terms of Service and Privacy Policy
              </p>
            </div>
          </div>
        </div>

        {/* Back to Home */}
        <BackHomeButton />
      </div>
    </div>
  );
}
