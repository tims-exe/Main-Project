import { getAccessToken, clearAuthData } from './auth';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface FetchOptions extends RequestInit {
    headers?: Record<string, string>;
}

export const fetchWithAuth = async (endpoint: string, options: FetchOptions = {}) => {
    const token = getAccessToken();
    
    const headers: Record<string, string> = {
        'Content-Type': 'application/json',
        ...options.headers,
    };

    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(`${API_URL}${endpoint}`, {
        ...options,
        headers,
    });

    if (response.status === 401) {
        clearAuthData();
        window.location.href = '/login';
        throw new Error('Unauthorized');
    }

    return response;
};

export const getCurrentUser = async () => {
    const response = await fetchWithAuth('/auth/me');
    if (!response.ok) {
        throw new Error('Failed to fetch user');
    }
    return response.json();
};

export const initiateGoogleLogin = async () => {
    const response = await fetch(`${API_URL}/auth/google/login`);
    
    if (!response.ok) {
        throw new Error('Failed to initiate Google login');
    }
    
    return response.json();
};