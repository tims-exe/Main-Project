import { redirect } from 'next/navigation';
import { getServerSession } from '@/lib/server-auth';
import LogoutButton from '@/components/ui/button/LogoutButton';

export default async function Home() {
    const session = await getServerSession();

    if (!session) {
        redirect('/login');
    }

    const { user } = session;

    return (
        <div className="p-8">
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
                    {/* {user.profile_picture && (
                        <Image 
                            src={user.profile_picture} 
                            alt="Profile" 
                            className="w-20 h-20 rounded-full mt-4"
                        />
                    )} */}
                </div>
                <LogoutButton />
            </div>
        </div>
    );
}