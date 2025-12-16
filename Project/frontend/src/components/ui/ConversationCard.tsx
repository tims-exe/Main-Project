type Props = {
  title: string;
  date: string;
};

export default function ConversationCard({ title, date }: Props) {
  return (
    <button
      type="button"
      className="w-full text-left p-4 rounded-xl border hover:bg-muted transition"
    >
      <p className="font-medium text-lg">{title}</p>
      <p className="text-sm text-muted-foreground">{date}</p>
    </button>
  );
}
