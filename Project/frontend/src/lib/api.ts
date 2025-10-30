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

export const authenticateWithGoogle = async (idToken: string) => {
    const response = await fetch(`${API_URL}/auth/google`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            id_token: idToken,
        }),
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Authentication failed');
    }

    return response.json();
};