import { redirect } from 'next/navigation';
import { getServerSession } from '@/lib/server-auth';
import GoogleAuthButton from "@/components/auth/GoogleAuthButton";

export default async function Login() {
    const session = await getServerSession();

    if (session) {
        redirect('/home');
    }

    return (
        <div className="flex flex-col justify-center items-center h-screen">
            <GoogleAuthButton />
        </div>
    );
}