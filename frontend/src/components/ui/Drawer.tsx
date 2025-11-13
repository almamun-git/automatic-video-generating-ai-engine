import { ReactNode } from 'react'

type Props = { open: boolean; onClose: () => void; title?: string; children: ReactNode }

export default function Drawer({ open, onClose, title, children }: Props) {
  return (
    <div className={`fixed inset-0 z-50 ${open ? '' : 'pointer-events-none'}`}>
      <div className={`absolute inset-0 bg-black/40 transition-opacity ${open ? 'opacity-100' : 'opacity-0'}`} onClick={onClose} />
      <div className={`absolute right-0 top-0 h-full w-full max-w-xl glass translate-x-0 transition-transform ${open ? '' : 'translate-x-full'}`}>
        <div className="flex items-center justify-between px-4 py-3 border-b border-white/10">
          <h3 className="text-lg font-semibold">{title}</h3>
          <button className="btn-secondary" onClick={onClose}>Close</button>
        </div>
        <div className="p-4 overflow-auto h-[calc(100%-56px)]">{children}</div>
      </div>
    </div>
  )
}
