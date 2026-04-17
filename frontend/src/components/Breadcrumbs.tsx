import { Link, useLocation } from "react-router-dom";

/**
 * Derives breadcrumbs from the current route path.
 *
 * "/hr/employees/42/edit" → Home › hr › employees › 42 › edit
 *
 * Numeric segments render as plain text (not links) since they are
 * usually IDs with no stable landing page.
 */
export default function Breadcrumbs() {
  const location = useLocation();
  const parts = location.pathname.split("/").filter(Boolean);

  return (
    <nav aria-label="Breadcrumb" className="breadcrumbs">
      <ol>
        <li>
          <Link to="/">Home</Link>
        </li>
        {parts.map((segment, i) => {
          const href = "/" + parts.slice(0, i + 1).join("/");
          const isLast = i === parts.length - 1;
          const isNumeric = /^\d+$/.test(segment);
          return (
            <li key={href}>
              <span className="breadcrumb-sep" aria-hidden="true">
                ›
              </span>
              {isLast || isNumeric ? (
                <span>{segment}</span>
              ) : (
                <Link to={href}>{segment}</Link>
              )}
            </li>
          );
        })}
      </ol>
    </nav>
  );
}
