"use client";

import { logout } from '@/lib/auth';

export default function LogoutButton() {
    return (
        <button
            onClick={logout}
            className="mt-6 bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600 transition-colors"
        >
            Logout
        </button>
    );
}