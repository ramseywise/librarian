/** The done mark beside a lesson. */
export function Check({ on, small }: { on: boolean; small?: boolean }) {
  const s = small ? 12 : 14;
  return (
    <span className={`check${on ? " is-on" : ""}`} style={{ width: s, height: s, fontSize: s - 4 }}>{on ? "✓" : ""}</span>
  );
}
