import { ReactNode, isValidElement } from 'react'

type Props = {
  title: string
  value: ReactNode
  delta?: string
  icon?: ReactNode
}

export default function StatCard({ title, value, delta, icon }: Props) {
  return (
    <div className="card">
      <div className="flex items-center justify-between">
        <div className="text-sm text-muted">{title}</div>
        {isValidElement(icon) ? icon : null}
      </div>
      <div className="mt-2 text-2xl font-semibold">{value}</div>
      {delta && <div className="mt-1 text-xs text-muted">{delta}</div>}
    </div>
  )
}
