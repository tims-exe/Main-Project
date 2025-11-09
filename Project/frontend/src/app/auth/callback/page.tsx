"use client";

import { useEffect, Suspense } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import { setAuthData } from '@/lib/auth';

function CallbackContent() {
    const searchParams = useSearchParams();
    const router = useRouter();

    useEffect(() => {
        const handleCallback = async () => {
            const token = searchParams.get('token');
            const userParam = searchParams.get('user');
            const error = searchParams.get('error');

            if (error) {
                console.error('Authentication error:', error);
                // alert('Authentication failed. Please try again.');
                router.push('/login');
                return;
            }
            // console.log(searchParams)
            // console.log(token)
            // console.log(userParam)
            if (token && userParam) {
                try {
                    const user = JSON.parse(decodeURIComponent(userParam));
                    setAuthData(token, user);
                    router.replace('/home');
                } catch (error) {
                    console.error('Error parsing user data:', error);
                    router.push('/login');
                }
            } else {
                router.push('/login');
            }
        };

        handleCallback();
    }, [searchParams, router]);

    return (
        <div className="flex items-center justify-center min-h-screen">
            <div className="text-center">
                {/* <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900 mx-auto"></div> */}
                <p className="mt-4 text-gray-600">Authenticating...</p>
            </div>
        </div>
    );
}

export default function CallbackPage() {
    return (
        <Suspense fallback={
            <div className="flex items-center justify-center min-h-screen">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900"></div>
            </div>
        }>
            <CallbackContent />
        </Suspense>
    );
}