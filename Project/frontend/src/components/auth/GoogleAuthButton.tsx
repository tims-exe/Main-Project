"use client";

import { useState } from 'react';
import { initiateGoogleLogin } from '@/lib/api';

export default function GoogleAuthButton() {
    const [loading, setLoading] = useState(false);

    const handleGoogleLogin = async () => {
        try {
            setLoading(true);
            const { auth_url } = await initiateGoogleLogin();
            window.location.href = auth_url;
        } catch (error) {
            console.error('Error initiating Google login:', error);
            // alert('Failed to initiate login. Please try again.');
            setLoading(false);
        }
    };

    return (
        <button 
            onClick={handleGoogleLogin}
            disabled={loading}
            className="bg-neutral-300 px-4 py-2 rounded-2xl my-4 hover:cursor-pointer hover:bg-neutral-400 duration-200 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
        >
            {loading ? 'Redirecting...' : 'Login with Google'}
        </button>
    );
}