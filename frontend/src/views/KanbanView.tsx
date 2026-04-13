import { useState } from "react";
import type { KanbanViewConfig, Record } from "./types";

interface KanbanViewProps {
  config: KanbanViewConfig;
  records: Record[];
  onCardClick?: (record: Record) => void;
  onCardMove?: (recordId: number, newColumnValue: string) => void;
}

export default function KanbanView({
  config,
  records,
  onCardClick,
  onCardMove,
}: KanbanViewProps) {
  const [draggedId, setDraggedId] = useState<number | null>(null);

  const recordsByColumn = new Map<string, Record[]>();
  for (const col of config.columns) {
    recordsByColumn.set(col.value, []);
  }
  for (const record of records) {
    const colValue = String(record[config.column_field] ?? "");
    const arr = recordsByColumn.get(colValue);
    if (arr) arr.push(record);
  }

  const handleDragStart = (recordId: number) => {
    setDraggedId(recordId);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
  };

  const handleDrop = (columnValue: string) => {
    if (draggedId != null) {
      onCardMove?.(draggedId, columnValue);
      setDraggedId(null);
    }
  };

  return (
    <div className="kanban-view" role="region" aria-label="Kanban board">
      {config.columns.map((col) => (
        <div
          key={col.value}
          className="kanban-column"
          onDragOver={handleDragOver}
          onDrop={() => handleDrop(col.value)}
        >
          <div
            className="kanban-column-header"
            style={{ borderTopColor: col.color || "#6B7280" }}
          >
            <span className="kanban-column-title">{col.label}</span>
            <span className="kanban-column-count">
              {recordsByColumn.get(col.value)?.length ?? 0}
            </span>
          </div>
          <div className="kanban-column-body">
            {(recordsByColumn.get(col.value) ?? []).map((record) => (
              <div
                key={record.id}
                className={`kanban-card ${draggedId === record.id ? "dragging" : ""}`}
                draggable
                onDragStart={() => handleDragStart(record.id)}
                onClick={() => onCardClick?.(record)}
                role="button"
                tabIndex={0}
              >
                {config.card_fields.map((field) => (
                  <div key={field} className="kanban-card-field">
                    {String(record[field] ?? "")}
                  </div>
                ))}
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}
