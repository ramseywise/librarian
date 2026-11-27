

export function SourceList({ label, items, count }: {
  label: string; items: { title: string; source: string; url?: string }[]; count?: number;
}) {
  // Without the local private overlay only the count is public.
  if (!items?.length) {
    return count ? <p className="course-sources">{label}: {count} (the list is kept locally)</p> : null;
  }
  return (
    <div className="course-sources">
      <h3 className="course-sources-label">{label}</h3>
      <ul>
        {items.map((it) => (
          <li key={it.source}>
            {it.url ? <a href={it.url} target="_blank" rel="noreferrer">{it.title}</a>
              : <span title={it.source}>{it.title}</span>}
          </li>
        ))}
      </ul>
    </div>
  );
}


export function Centered({ children }: { children: React.ReactNode }) {
  return (
    <div className="course-centered">
      <div>{children}</div>
    </div>
  );
}

export function SearchBox({ value, onChange, placeholder }: {
  value: string; onChange: (v: string) => void; placeholder: string;
}) {
  return (
    <input
      value={value}
      onChange={(e) => onChange(e.target.value)}
      placeholder={placeholder}
      data-view-search
      className="search-box"
    />
  );
}

export function ProgressBar({ value }: { value: number }) {
  return (
    <div className="progress-bar">
      <div className="progress-bar-fill" style={{ width: `${Math.round(value * 100)}%` }} />
    </div>
  );
}

/**
 * How well the learner knows a module, from the learning API (`null` strength: no concept of it has
 * direct evidence yet). Drawn as an outline, never as 0%, so "no data" cannot read as "failing".
 */
export function MasteryBar({ mastery }: { mastery: { strength: number | null; concepts: number; withEvidence: number } | undefined }) {
  if (!mastery || mastery.concepts === 0) return null;
  const { strength, concepts, withEvidence } = mastery;
  const pct = strength === null ? null : Math.round(strength * 100);
  return (
    <div className="mastery" data-testid="mastery">
      <div className="mastery-track" role="img" aria-label={pct === null ? "Mastery: no data yet" : `Mastery ${pct}%`}>
        <div className={`mastery-seg${pct === null ? " is-empty" : ""}`}>
          {pct !== null && <div className="mastery-fill" style={{ width: `${pct}%` }} />}
        </div>
      </div>
      <div className="mastery-label">
        {pct === null ? "Mastery: no data yet" : `Mastery ${pct}%`} · {withEvidence} of {concepts} concepts practised
      </div>
    </div>
  );
}
