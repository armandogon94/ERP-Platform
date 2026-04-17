import type { AggregateRow } from "../api/reports";

interface PivotViewProps {
  rows: AggregateRow[];
  rowLabel: string;
  valueLabel: string;
  formatter?: (value: number) => string;
}

export default function PivotView({
  rows,
  rowLabel,
  valueLabel,
  formatter = (v) => String(v),
}: PivotViewProps) {
  if (rows.length === 0) {
    return <div>No data</div>;
  }
  const total = rows.reduce((sum, r) => sum + r.value, 0);
  return (
    <table>
      <thead>
        <tr>
          <th>{rowLabel}</th>
          <th>{valueLabel}</th>
        </tr>
      </thead>
      <tbody>
        {rows.map((r) => (
          <tr key={String(r.group)}>
            <td>{r.group ?? "—"}</td>
            <td>{formatter(r.value)}</td>
          </tr>
        ))}
        <tr>
          <td>
            <strong>Total</strong>
          </td>
          <td>
            <strong>{formatter(total)}</strong>
          </td>
        </tr>
      </tbody>
    </table>
  );
}
