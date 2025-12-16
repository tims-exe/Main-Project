"use client"

import { redirect } from "next/navigation";


export default function BackHomeButton(){
    return (
        <div className="text-center">
          <button
            onClick={() => redirect("/")}
            className="text-purple-600 hover:text-purple-700 font-medium text-sm transition-colors hover:cursor-pointer"
          >
            ← Back to Home
          </button>
        </div>
    )
}