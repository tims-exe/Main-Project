"use client";

import { redirect } from "next/navigation";

export default function GetStartedButton() {
  return (
    <button
      onClick={() => {
        redirect("/login");
      }}
      className="hover:cursor-pointer px-8 py-4 bg-purple-600 hover:bg-purple-700 text-white font-semibold rounded-full text-lg transition-all duration-200 shadow-lg hover:shadow-xl transform hover:-translate-y-0.5"
    >
      Get Started
    </button>
  );
}
