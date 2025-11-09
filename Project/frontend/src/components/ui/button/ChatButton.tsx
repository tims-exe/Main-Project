"use client"

import { redirect } from "next/navigation"

export default function ChatButton() {
    return (
        <button onClick={() => {
            redirect("/chat")
        }}
        className="bg-purple-500 text-white rounded-2xl hover:bg-indigo-800 hover:text-white hover:cursor-pointer transition-colors py-4 px-6 text-2xl">
            Chat
        </button>
    )
}