type Item = { id: string; title: string; time: string; status: 'Pending'|'Running'|'Success'|'Error' }

export default function ActivityTimeline({ items }: { items: Item[] }) {
  return (
    <ol className="relative border-l border-white/10 pl-4">
      {items.map((i) => (
        <li key={i.id} className="mb-4">
          <div className="absolute -left-1.5 w-3 h-3 rounded-full border border-white/20 bg-white/10" />
          <div className="flex items-center gap-2 text-xs text-muted">
            <span>{i.time}</span>
            <span className={`badge ${i.status==='Success' ? 'text-emerald-300 border-emerald-400/20 bg-emerald-500/10' : i.status==='Error' ? 'text-rose-300 border-rose-400/20 bg-rose-500/10' : i.status==='Running' ? 'text-cyan-300 border-cyan-400/20 bg-cyan-500/10' : 'text-muted'}`}>{i.status}</span>
          </div>
          <div className="text-sm mt-1">{i.title}</div>
        </li>
      ))}
    </ol>
  )
}
