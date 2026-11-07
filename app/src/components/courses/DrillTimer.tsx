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
  // formatCountdown only prefixes "+" once overtime is a whole second; at exactly the
  // limit the clock reads 00:00 with nothing to strip.
  const label = !over
    ? `${clock} remaining`
    : clock.startsWith("+")
      ? `Over the ${timeboxMin}-minute timebox by ${clock.slice(1)}`
      : `${timeboxMin}-minute timebox reached`;

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
