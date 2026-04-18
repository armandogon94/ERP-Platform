import type { ReactNode } from "react";
import EmptyState from "./EmptyState";
import Skeleton from "./Skeleton";

interface ListPageShellProps {
  /** Page heading — rendered as h1. */
  title: ReactNode;
  /** Optional toolbar / action buttons rendered next to the heading. */
  actions?: ReactNode;
  /** True while the list is loading. Shows a Skeleton placeholder. */
  isLoading: boolean;
  /** Error message. If set, shown via role=alert, content hidden. */
  error?: string | null;
  /** When `true`, render the empty-state block instead of children. */
  isEmpty?: boolean;
  /** Configuration for the empty state (shown when isEmpty is true). */
  empty?: { title: string; description?: string; action?: ReactNode };
  /** The main content — typically a table or grid. */
  children: ReactNode;
}

/**
 * REVIEW S-4: consolidates the loading/error/empty/content pattern that
 * was copy-pasted into 28 list pages. Use as::
 *
 *     <ListPageShell
 *       title={`${label}s`}
 *       actions={<Link to="new">New</Link>}
 *       isLoading={isLoading}
 *       error={error}
 *       isEmpty={rows.length === 0}
 *       empty={{ title: "No records yet" }}
 *     >
 *       <table>…</table>
 *     </ListPageShell>
 */
export default function ListPageShell({
  title,
  actions,
  isLoading,
  error,
  isEmpty,
  empty,
  children,
}: ListPageShellProps): JSX.Element {
  return (
    <div className="list-page-shell">
      <div className="list-page-header">
        <h1>{title}</h1>
        {actions && <div className="list-page-actions">{actions}</div>}
      </div>

      {error && <div role="alert">{error}</div>}

      {isLoading && <Skeleton />}

      {!isLoading && !error && isEmpty && empty && (
        <EmptyState
          title={empty.title}
          description={empty.description}
          action={empty.action}
        />
      )}

      {!isLoading && !error && !isEmpty && children}
    </div>
  );
}
