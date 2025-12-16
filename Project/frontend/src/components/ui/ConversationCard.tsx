interface ConversationCardProps {
  id: string;
  title: string;
  date: string;
  onDelete: (id: string) => void;
  onClick: (id: string) => void;
}

export default function ConversationCard({
  id,
  title,
  date,
  onDelete,
  onClick,
}: ConversationCardProps) {
  const handleDelete = (e: React.MouseEvent<HTMLButtonElement>) => {
    e.stopPropagation();
    if (confirm("Delete this conversation?")) {
      onDelete(id);
    }
  };

  return (
    <div
      onClick={() => onClick(id)}
      className="group relative bg-white border border-zinc-900/50 rounded-xl p-5
                 hover:border-zinc-900 hover:shadow-md transition-all duration-200
                 cursor-pointer"
    >
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1 min-w-0">
          <h3 className="font-semibold text-gray-800 text-base mb-1 truncate">
            {title}
          </h3>
          <p className="text-sm text-gray-500">{date}</p>
        </div>

        <button
          onClick={handleDelete}
          className="opacity-0 group-hover:opacity-100 p-2 rounded-full
                     hover:bg-red-50 text-gray-400 hover:text-red-500
                     transition-all cursor-pointer"
        >
          <svg
            className="w-5 h-5"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
            />
          </svg>
        </button>
      </div>

      <div className="mt-3 flex items-center text-purple-600 text-sm font-medium opacity-0 group-hover:opacity-100 transition-opacity">
        <span>Open conversation</span>
        <svg className="w-4 h-4 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
        </svg>
      </div>
    </div>
  );
}
