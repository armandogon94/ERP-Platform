interface SkeletonProps {
  lines?: number;
  /** Optional fixed height per bar (default 14px). */
  height?: number;
}

/**
 * A shimmering placeholder that replaces the bare `<div>Loading…</div>`
 * patterns used by list pages. Gives the app a professional "something's
 * about to render" feel during async loads.
 */
export default function Skeleton({ lines = 3, height = 14 }: SkeletonProps) {
  return (
    <div className="skeleton" role="status" aria-label="Loading" aria-busy="true">
      {Array.from({ length: lines }).map((_, i) => (
        <div
          key={i}
          className="skeleton-bar"
          style={{
            height,
            width: `${60 + ((i * 13) % 30)}%`,
          }}
        />
      ))}
    </div>
  );
}
