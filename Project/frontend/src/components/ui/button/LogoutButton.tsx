"use client";

import { logout } from '@/lib/auth';

export default function LogoutButton() {
    return (
        <button
            onClick={logout}
            className="rounded bg-red-400 text-white hover:cursor-pointer transition-colors h-[40px] px-3 hover:bg-red-700"
        >
            Logout
        </button>
    );
}