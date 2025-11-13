import { ReactNode, InputHTMLAttributes, SelectHTMLAttributes } from 'react'

export function Label({ children }: { children: ReactNode }) {
  return <label className="block text-sm font-medium mb-1 text-muted">{children}</label>
}

export function Input(props: InputHTMLAttributes<HTMLInputElement>) {
  return <input {...props} className={`w-full rounded-lg bg-white/5 border border-white/10 px-3 py-2 outline-none focus:ring-2 focus:ring-primary/50 ${props.className ?? ''}`} />
}

export function Select(props: SelectHTMLAttributes<HTMLSelectElement>) {
  return (
    <select {...props} className={`w-full rounded-lg bg-white/5 border border-white/10 px-3 py-2 outline-none focus:ring-2 focus:ring-primary/50 ${props.className ?? ''}`} />
  )
}

export function Range({ label, value, onChange, min = 0, max = 100, step = 1 }: { label: string; value: number; onChange: (v: number) => void; min?: number; max?: number; step?: number }) {
  return (
    <div>
      <div className="flex items-center justify-between text-sm text-muted mb-1">
        <span>{label}</span>
        <span className="text-foreground font-medium">{value}</span>
      </div>
      <input type="range" min={min} max={max} step={step} value={value} onChange={(e) => onChange(Number(e.target.value))} className="w-full accent-cyan-400" />
    </div>
  )
}
