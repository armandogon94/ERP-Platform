import { useState } from "react";
import { type AggregateRow, fetchAggregateApi } from "../../api/reports";
import PivotView from "../../views/PivotView";
import GraphView, { type ChartType } from "../../views/GraphView";

// Curated list of reportable models with their whitelist of group_by /
// measure fields (kept in sync with backend AggregationMixin declarations).
const MODEL_OPTIONS: Array<{
  label: string;
  model: string;
  group_by: string[];
  measures: string[];
}> = [
  {
    label: "Invoices",
    model: "invoicing/invoices",
    group_by: ["status", "invoice_type", "invoice_date"],
    measures: ["total_amount", "subtotal", "tax_amount", "amount_paid"],
  },
  {
    label: "Sales Orders",
    model: "sales/orders",
    group_by: ["status", "order_date"],
    measures: ["total_amount"],
  },
  {
    label: "Sales Quotations",
    model: "sales/quotations",
    group_by: ["status", "valid_until"],
    measures: ["total_amount"],
  },
  {
    label: "Purchase Orders",
    model: "purchasing/purchase-orders",
    group_by: ["status", "order_date"],
    measures: ["total_amount"],
  },
  {
    label: "Journal Entries",
    model: "accounting/entries",
    group_by: ["status", "entry_date"],
    measures: ["id"],
  },
  {
    label: "Tickets",
    model: "helpdesk/tickets",
    group_by: ["status", "priority", "sla_breached"],
    measures: ["id"],
  },
  {
    label: "Work Orders",
    model: "manufacturing/work-orders",
    group_by: ["status"],
    measures: ["quantity_target", "quantity_done"],
  },
  {
    label: "Products",
    model: "inventory/products",
    group_by: ["uom", "is_active"],
    measures: ["sale_price", "cost_price"],
  },
];

const OPERATIONS: Array<{
  value: "sum" | "count" | "avg" | "min" | "max";
  label: string;
}> = [
  { value: "count", label: "Count" },
  { value: "sum", label: "Sum" },
  { value: "avg", label: "Average" },
  { value: "min", label: "Minimum" },
  { value: "max", label: "Maximum" },
];

const VIEW_OPTIONS: Array<{ value: "pivot" | ChartType; label: string }> = [
  { value: "pivot", label: "Pivot table" },
  { value: "bar", label: "Bar chart" },
  { value: "line", label: "Line chart" },
  { value: "pie", label: "Pie chart" },
  { value: "area", label: "Area chart" },
];

export default function ReportBuilderPage() {
  const [modelIndex, setModelIndex] = useState(0);
  const currentModel = MODEL_OPTIONS[modelIndex];
  const [groupBy, setGroupBy] = useState(currentModel.group_by[0]);
  const [measure, setMeasure] = useState(currentModel.measures[0] ?? "id");
  const [op, setOp] = useState<"sum" | "count" | "avg" | "min" | "max">(
    "count",
  );
  const [viewMode, setViewMode] = useState<"pivot" | ChartType>("pivot");
  const [rows, setRows] = useState<AggregateRow[] | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleModelChange = (i: number) => {
    setModelIndex(i);
    setGroupBy(MODEL_OPTIONS[i].group_by[0]);
    setMeasure(MODEL_OPTIONS[i].measures[0] ?? "id");
    setRows(null);
  };

  const handleRun = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await fetchAggregateApi({
        model: currentModel.model,
        group_by: groupBy,
        measure: op === "count" ? undefined : measure,
        op,
      });
      setRows(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Report failed");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div>
      <h1>Report Builder</h1>

      {error && <div role="alert">{error}</div>}

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fill, minmax(180px, 1fr))",
          gap: "12px",
          maxWidth: "900px",
          marginBottom: "16px",
        }}
      >
        <div>
          <label htmlFor="model">Model</label>
          <select
            id="model"
            value={modelIndex}
            onChange={(e) => handleModelChange(Number(e.target.value))}
          >
            {MODEL_OPTIONS.map((m, i) => (
              <option key={m.model} value={i}>
                {m.label}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label htmlFor="group_by">Group by</label>
          <select
            id="group_by"
            value={groupBy}
            onChange={(e) => setGroupBy(e.target.value)}
          >
            {currentModel.group_by.map((g) => (
              <option key={g} value={g}>
                {g}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label htmlFor="op">Operation</label>
          <select
            id="op"
            value={op}
            onChange={(e) =>
              setOp(e.target.value as "sum" | "count" | "avg" | "min" | "max")
            }
          >
            {OPERATIONS.map((o) => (
              <option key={o.value} value={o.value}>
                {o.label}
              </option>
            ))}
          </select>
        </div>

        {op !== "count" && (
          <div>
            <label htmlFor="measure">Measure</label>
            <select
              id="measure"
              value={measure}
              onChange={(e) => setMeasure(e.target.value)}
            >
              {currentModel.measures.map((m) => (
                <option key={m} value={m}>
                  {m}
                </option>
              ))}
            </select>
          </div>
        )}

        <div>
          <label htmlFor="view">View</label>
          <select
            id="view"
            value={viewMode}
            onChange={(e) =>
              setViewMode(e.target.value as "pivot" | ChartType)
            }
          >
            {VIEW_OPTIONS.map((v) => (
              <option key={v.value} value={v.value}>
                {v.label}
              </option>
            ))}
          </select>
        </div>
      </div>

      <button type="button" onClick={handleRun} disabled={isLoading}>
        {isLoading ? "Running..." : "Run report"}
      </button>

      <div style={{ marginTop: "24px" }}>
        {rows !== null && viewMode === "pivot" && (
          <PivotView
            rows={rows}
            rowLabel={groupBy}
            valueLabel={op === "count" ? "Count" : measure}
          />
        )}
        {rows !== null && viewMode !== "pivot" && (
          <GraphView rows={rows} chartType={viewMode} />
        )}
      </div>
    </div>
  );
}
