import axios from 'axios';
import { getAccessToken, clearAuthData } from './auth';
import { ChatPostRequestType } from '@/types/auth';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Create Axios instance
const api = axios.create({
    baseURL: API_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Add Authorization header automatically
api.interceptors.request.use((config) => {
    const token = getAccessToken();
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

// Handle unauthorized errors globally
api.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response && error.response.status === 401) {
            clearAuthData();
            window.location.href = '/login';
        }
        return Promise.reject(error);
    }
);

// GET request with auth
export const fetchWithAuth = async (endpoint: string) => {
    return api.get(endpoint);
};

// POST request with auth and payload
export const postChatWithAuth = async (endpoint: string, data: ChatPostRequestType) => {
    return api.post(endpoint, data);
};

export const postFormWithAuth = async (endpoint: string, data: FormData) => {
    return api.post(endpoint, data, {
        headers: { "Content-Type": "multipart/form-data" }
    });
}

// Get current user
export const getCurrentUser = async () => {
    const response = await fetchWithAuth('/auth/me');
    return response.data;
};

// Initiate Google login
export const initiateGoogleLogin = async () => {
    const response = await api.get('/auth/google/login');
    return response.data;
};

export default api;
