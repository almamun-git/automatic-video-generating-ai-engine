type Props = { status: 'Pending' | 'Running' | 'Success' | 'Error' }

export default function StatusPill({ status }: Props) {
  const map = {
    Pending: 'bg-white/5 text-muted border-white/10',
    Running: 'bg-cyan-500/10 text-cyan-300 border-cyan-400/20',
    Success: 'bg-emerald-500/10 text-emerald-300 border-emerald-400/20',
    Error: 'bg-rose-500/10 text-rose-300 border-rose-400/20',
  } as const
  return <span className={`badge ${map[status]}`}>{status}</span>
}
