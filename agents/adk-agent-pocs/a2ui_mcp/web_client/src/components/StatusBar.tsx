interface Props {
  connected: boolean;
}

export function StatusBar({ connected }: Props) {
  return (
    <div className="flex items-center justify-between px-4 py-2 bg-white border-b border-slate-200 shadow-sm">
      <span className="font-bold text-lg text-slate-800">Shine</span>
      <div className="flex items-center gap-2 text-sm">
        <span
          className={`w-2 h-2 rounded-full ${connected ? "bg-green-500" : "bg-red-400"}`}
        />
        <span className="text-slate-500">{connected ? "connected" : "disconnected"}</span>
      </div>
    </div>
  );
}
