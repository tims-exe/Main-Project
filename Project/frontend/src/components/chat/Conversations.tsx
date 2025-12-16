"use client";

import ConversationCard from "../ui/ConversationCard";


const dummyConversations = [
  { id: 1, title: "Convo 1", date: "15 Sep 2025" },
  { id: 2, title: "Convo 2", date: "14 Sep 2025" },
  { id: 3, title: "Convo 3", date: "13 Sep 2025" },
  { id: 4, title: "Convo 4", date: "12 Sep 2025" },
  { id: 5, title: "Convo 5", date: "11 Sep 2025" },
  { id: 6, title: "Convo 6", date: "10 Sep 2025" },
];

export default function Conversations() {
  return (
    <div
      className="
        grid
        grid-cols-1
        sm:grid-cols-2
        lg:grid-cols-3
        gap-4
      "
    >
      {dummyConversations.map((conv) => (
        <ConversationCard
          key={conv.id}
          title={conv.title}
          date={conv.date}
        />
      ))}
    </div>
  );
}
