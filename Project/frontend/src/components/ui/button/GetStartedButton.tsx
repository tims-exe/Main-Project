"use client";

import { redirect } from "next/navigation";

export default function GetStartedButton() {
    return (
        <button onClick={() => {redirect('/login')}}
        className="bg-neutral-300 px-4 py-2 rounded-2xl my-4 hover:cursor-pointer hover:bg-neutral-400 duration-200 transition-all">
            Get Started
        </button>
  );
}
