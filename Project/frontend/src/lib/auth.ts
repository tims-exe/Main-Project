import type { User } from '@/types/auth';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Client-side functions
export const isAuthenticated = (): boolean => {
    if (typeof window === 'undefined') return false;
    return !!getCookie('access_token');
};

export const getStoredUser = (): User | null => {
    if (typeof window === 'undefined') return null;
    const userStr = getCookie('user');
    return userStr ? JSON.parse(decodeURIComponent(userStr)) : null;
};

export const getAccessToken = (): string | null => {
    if (typeof window === 'undefined') return null;
    return getCookie('access_token');
};

export const setAuthData = (token: string, user: User): void => {
    // Set cookies instead of localStorage
    setCookie('access_token', token, 7); // 7 days expiry
    setCookie('user', JSON.stringify(user), 7);
};

export const clearAuthData = (): void => {
    deleteCookie('access_token');
    deleteCookie('user');
};

export const logout = (): void => {
    clearAuthData();
    window.location.href = '/login';
};

// Cookie helper functions
function setCookie(name: string, value: string, days: number) {
    const expires = new Date();
    expires.setTime(expires.getTime() + days * 24 * 60 * 60 * 1000);
    document.cookie = `${name}=${value};expires=${expires.toUTCString()};path=/;SameSite=Lax`;
}

function getCookie(name: string): string | null {
    const nameEQ = name + "=";
    const ca = document.cookie.split(';');
    for (let i = 0; i < ca.length; i++) {
        let c = ca[i];
        while (c.charAt(0) === ' ') c = c.substring(1, c.length);
        if (c.indexOf(nameEQ) === 0) return c.substring(nameEQ.length, c.length);
    }
    return null;
}

function deleteCookie(name: string) {
    document.cookie = `${name}=;expires=Thu, 01 Jan 1970 00:00:00 UTC;path=/;`;
}

// Server-side function
export async function getServerUser(token: string): Promise<User | null> {
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

        return await response.json();
    } catch (error) {
        console.error('Error fetching user:', error);
        return null;
    }
}