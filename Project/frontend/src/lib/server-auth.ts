import { cookies } from 'next/headers';
import type { User } from '@/types/auth';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function getServerSession(): Promise<{ user: User; token: string } | null> {
    const cookieStore = await cookies();
    const token = cookieStore.get('access_token')?.value;

    if (!token) {
        return null;
    }

    try {
        const response = await fetch(`${API_URL}/auth/me`, {
            headers: {
                'Authorization': `Bearer ${token}`,
            },
            cache: 'no-store',
        });

        if (!response.ok) {
            return null;
        }

        const user = await response.json();
        return { user, token };
    } catch (error) {
        console.error('Error fetching user:', error);
        return null;
    }
}