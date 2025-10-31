import type { User } from '@/types/auth';

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
    setCookie('access_token', token, 7);
    setCookie('user', encodeURIComponent(JSON.stringify(user)), 7);
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