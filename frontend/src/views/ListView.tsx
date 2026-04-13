import { useState, useMemo } from "react";
import type { ListViewConfig, Record } from "./types";

interface ListViewProps {
  config: ListViewConfig;
  records: Record[];
  onRowClick?: (record: Record) => void;
  onSearch?: (query: string) => void;
}

type SortDirection = "asc" | "desc";

export default function ListView({
  config,
  records,
  onRowClick,
  onSearch,
}: ListViewProps) {
  const [sortField, setSortField] = useState<string | null>(null);
  const [sortDir, setSortDir] = useState<SortDirection>("asc");
  const [searchQuery, setSearchQuery] = useState("");

  const handleSort = (field: string) => {
    if (sortField === field) {
      setSortDir((prev) => (prev === "asc" ? "desc" : "asc"));
    } else {
      setSortField(field);
      setSortDir("asc");
    }
  };

  const handleSearch = (value: string) => {
    setSearchQuery(value);
    onSearch?.(value);
  };

  const sortedRecords = useMemo(() => {
    if (!sortField) return records;
    return [...records].sort((a, b) => {
      const aVal = a[sortField];
      const bVal = b[sortField];
      if (aVal == null && bVal == null) return 0;
      if (aVal == null) return 1;
      if (bVal == null) return -1;
      const cmp = String(aVal).localeCompare(String(bVal));
      return sortDir === "asc" ? cmp : -cmp;
    });
  }, [records, sortField, sortDir]);

  const filteredRecords = useMemo(() => {
    if (!searchQuery || !config.search_fields?.length) return sortedRecords;
    const q = searchQuery.toLowerCase();
    return sortedRecords.filter((record) =>
      config.search_fields!.some((field) =>
        String(record[field] ?? "")
          .toLowerCase()
          .includes(q),
      ),
    );
  }, [sortedRecords, searchQuery, config.search_fields]);

  return (
    <div className="list-view">
      {config.search_fields && config.search_fields.length > 0 && (
        <div className="list-search">
          <input
            type="search"
            placeholder="Search..."
            value={searchQuery}
            onChange={(e) => handleSearch(e.target.value)}
            aria-label="Search records"
          />
        </div>
      )}

      <table className="list-table">
        <thead>
          <tr>
            {config.columns.map((col) => (
              <th
                key={col.field}
                onClick={col.sortable ? () => handleSort(col.field) : undefined}
                className={col.sortable ? "sortable" : ""}
                style={col.width ? { width: col.width } : undefined}
              >
                {col.label}
                {sortField === col.field && (
                  <span className="sort-indicator" aria-label={`sorted ${sortDir}`}>
                    {sortDir === "asc" ? " \u25B2" : " \u25BC"}
                  </span>
                )}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {filteredRecords.length === 0 ? (
            <tr>
              <td colSpan={config.columns.length} className="empty-state">
                No records found.
              </td>
            </tr>
          ) : (
            filteredRecords.map((record) => (
              <tr
                key={record.id}
                onClick={() => onRowClick?.(record)}
                className={onRowClick ? "clickable" : ""}
              >
                {config.columns.map((col) => (
                  <td key={col.field}>{formatValue(record[col.field])}</td>
                ))}
              </tr>
            ))
          )}
        </tbody>
      </table>

      <div className="list-footer">
        {filteredRecords.length} record{filteredRecords.length !== 1 ? "s" : ""}
      </div>
    </div>
  );
}

function formatValue(value: unknown): string {
  if (value == null) return "";
  if (typeof value === "boolean") return value ? "Yes" : "No";
  return String(value);
}
