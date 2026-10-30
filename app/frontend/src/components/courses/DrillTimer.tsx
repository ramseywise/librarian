import { formatCountdown, useDrillTimer } from "../../hooks/useDrillTimer";

interface Props {
  lessonId: string;
  timeboxMin: number;
  /** Compact form for the practice list row. */
  compact?: boolean;
}

/** Countdown from the drill's timebox; turns red at zero and keeps counting overtime. */
export function DrillTimer({ lessonId, timeboxMin, compact }: Props) {
  const { remainingMs, running, started, start, pause, reset } = useDrillTimer(lessonId, timeboxMin);
  const over = remainingMs <= 0;
  const clock = formatCountdown(remainingMs);
  const color = over ? "#EF5350" : running ? "#90caf9" : started ? "#bbb" : "#888";
  const label = over ? `Over the ${timeboxMin}-minute timebox by ${clock.slice(1)}` : `${clock} remaining`;

  return (
    <span role="group" aria-label="Drill timer" style={{ display: "inline-flex", alignItems: "center", gap: 6 }}>
      <span role="timer" aria-label={label} title={label}
        style={{ fontFamily: "ui-monospace, Menlo, monospace", fontSize: compact ? 12 : 15, color, minWidth: compact ? 44 : 56 }}>
        {clock}
      </span>
      <button onClick={running ? pause : start} style={btnStyle(compact)}>
        {running ? "Pause" : started ? "Resume" : "Start"}
      </button>
      {started && !compact && (
        <button onClick={reset} style={btnStyle(compact)}>Reset</button>
      )}
    </span>
  );
}

const btnStyle = (compact?: boolean): React.CSSProperties => ({
  background: "transparent", border: "1px solid #333", borderRadius: 12, color: "#bbb",
  fontSize: compact ? 11 : 12, padding: compact ? "1px 8px" : "3px 12px", cursor: "pointer", fontFamily: "inherit",
});
