"use client";

import { useEffect, useState } from 'react';
import { authenticateWithGoogle } from '@/lib/api';
import { setAuthData } from '@/lib/auth';
import type { GoogleCredentialResponse, AuthResponse } from '@/types/auth';

export default function GoogleAuthButton() {
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        const script = document.createElement('script');
        script.src = 'https://accounts.google.com/gsi/client';
        script.async = true;
        script.defer = true;
        document.body.appendChild(script);

        script.onload = () => {
            if (window.google) {
                window.google.accounts.id.initialize({
                    client_id: process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID!,
                    callback: handleCredentialResponse,
                });
            }
        };

        return () => {
            if (document.body.contains(script)) {
                document.body.removeChild(script);
            }
        };
    }, []);

    const handleCredentialResponse = async (response: GoogleCredentialResponse) => {
        try {
            setLoading(true);
            const data: AuthResponse = await authenticateWithGoogle(response.credential);
            
            setAuthData(data.access_token, data.user);
            
            window.location.href = '/home';
            
        } catch (error) {
            console.error('Error during authentication:', error);
            alert('Authentication failed. Please try again.');
            setLoading(false);
        }
    };

    const handleGoogleLogin = () => {
        if (window.google) {
            window.google.accounts.id.prompt();
        }
    };

    return (
        <button 
            onClick={handleGoogleLogin}
            disabled={loading}
            className="bg-neutral-300 px-4 py-2 rounded-2xl my-4 hover:cursor-pointer hover:bg-neutral-400 duration-200 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
        >
            {loading ? 'Logging in...' : 'Login with Google'}
        </button>
    );
}