"use client"

import { redirect } from "next/navigation"

export default function ChatButton() {
    return (
        <button onClick={() => {
            redirect("/chat")
        }}
        className="bg-purple-800/80 text-white rounded-2xl hover:bg-purple-900 hover:text-white hover:cursor-pointer transition-colors py-3 px-6 text-xl w-[300px]">
            Chat
        </button>
    )
}