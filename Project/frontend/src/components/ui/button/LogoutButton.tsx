"use client";

import { logout } from '@/lib/auth';

export default function LogoutButton() {
    return (
        <button
            onClick={logout}
            className="border-2 border-red-400 text-red-400 rounded hover:bg-red-400 hover:text-white hover:cursor-pointer transition-colors h-[40px] px-3"
        >
            Logout
        </button>
    );
}