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
  onClick 
}: ConversationCardProps) {
  const handleDelete = (e: React.MouseEvent<HTMLButtonElement>): void => {
    e.stopPropagation();
    if (confirm('Are you sure you want to delete this conversation?')) {
      onDelete(id);
    }
  };

  const handleClick = (): void => {
    onClick(id);
  };

  return (
    <div className="relative group">
      <button
        type="button"
        onClick={handleClick}
        className="w-full text-left p-4 rounded-xl border hover:bg-muted transition"
      >
        <p className="font-medium text-lg">{title}</p>
        <p className="text-sm text-muted-foreground">{date}</p>
      </button>
      <button
        onClick={handleDelete}
        className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity bg-red-500 text-white rounded-full p-2 hover:bg-red-600"
        title="Delete conversation"
      >
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
    </div>
  );
}