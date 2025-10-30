"use client";

import { useEffect } from 'react';
import { isAuthenticated } from '@/lib/auth';
import { redirect } from 'next/navigation';

interface ProtectedRouteProps {
    children: React.ReactNode;
}

export default function ProtectedRoute({ children }: ProtectedRouteProps) {
    useEffect(() => {
        if (!isAuthenticated()) {
            redirect('/login');
        }
    }, []);

    return <>{children}</>;
}