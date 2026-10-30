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
  const state = over ? "over" : running ? "running" : started ? "paused" : "idle";
  const label = over ? `Over the ${timeboxMin}-minute timebox by ${clock.slice(1)}` : `${clock} remaining`;

  return (
    <span role="group" aria-label="Drill timer" className={`drill-timer${compact ? " drill-timer--compact" : ""}`}>
      <span role="timer" aria-label={label} title={label} className={`drill-clock drill-clock--${state}`}>
        {clock}
      </span>
      <button onClick={running ? pause : start} className="drill-btn">
        {running ? "Pause" : started ? "Resume" : "Start"}
      </button>
      {started && !compact && (
        <button onClick={reset} className="drill-btn">Reset</button>
      )}
    </span>
  );
}
