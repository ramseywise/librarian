import { useEffect, useState } from "react";
import { apiFetch } from "../utils/api";

interface Metric {
  value: number;
  status: string;
}

interface Snapshot {
  date: string | null;
  metrics: Record<string, Metric>;
}

const LABELS: Record<string, string> = {
  orphan_rate: "orphans",
  average_degree: "links per page",
  main_component: "connected",
  stale_rate: "stale",
  typed_link_rate: "typed links",
  stub_rate: "stubs",
};

/** Statuses come from data/telemetry/metrics.jsonl as written; one this doesn't know stays neutral. */
const STATUS_CLASS: Record<string, string> = {
  healthy: "health-chip--healthy",
  watch: "health-chip--watch",
  broken: "health-chip--broken",
};

const label = (name: string) => LABELS[name] ?? name.replace(/_/g, " ");

/** The wiki's latest telemetry row. It shows the file's statuses and no page count: size isn't health. */
export function HealthStrip() {
  const [snapshot, setSnapshot] = useState<Snapshot | null>(null);
  const [failed, setFailed] = useState(false);

  useEffect(() => {
    let cancelled = false;
    apiFetch("/api/wiki/health")
      .then((r) => (r.ok ? (r.json() as Promise<Snapshot>) : Promise.reject(new Error(`HTTP ${r.status}`))))
      .then((body) => {
        if (!cancelled) setSnapshot(body);
      })
      .catch(() => {
        if (!cancelled) setFailed(true);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  if (!snapshot && !failed) return null;
  const metrics = Object.entries(snapshot?.metrics ?? {});
  return (
    <section className="health-strip" aria-label="Wiki health">
      {failed ? (
        <span className="health-note">Wiki health unavailable</span>
      ) : !snapshot?.date || !metrics.length ? (
        <span className="health-note">No wiki health snapshot yet</span>
      ) : (
        <>
          <span className="health-note">Health {snapshot.date}</span>
          {metrics.map(([name, metric]) => (
            <span key={name} className={`health-chip ${STATUS_CLASS[metric.status] ?? ""}`} title={`${name}: ${metric.value}`}>
              {label(name)} <strong>{metric.status}</strong>
            </span>
          ))}
        </>
      )}
    </section>
  );
}
