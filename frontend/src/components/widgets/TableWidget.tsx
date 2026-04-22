import type { TableRow } from "../../api/dashboards";

interface TableWidgetProps {
  title: string;
  subtitle?: string;
  data: TableRow[] | undefined;
}

/**
 * Ranked-list / plain-table widget. Infers columns from the first row's
 * keys. Renders nothing if the payload is an error envelope.
 */
export default function TableWidget({
  title,
  subtitle,
  data,
}: TableWidgetProps) {
  const rows: TableRow[] = Array.isArray(data) ? data : [];
  const columns = rows[0] ? Object.keys(rows[0]) : [];

  return (
    <div className="widget widget-table">
      <div className="widget-title">{title}</div>
      {subtitle && <div className="widget-subtitle">{subtitle}</div>}
      {rows.length === 0 ? (
        <div className="widget-empty">No data</div>
      ) : (
        <table>
          <thead>
            <tr>
              {columns.map((c) => (
                <th key={c}>{c.replace(/_/g, " ")}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((row, i) => (
              <tr key={i}>
                {columns.map((c) => (
                  <td key={c}>{row[c] as string | number | null}</td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
