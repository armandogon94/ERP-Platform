import { fireEvent, render, screen, within } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import KanbanView from "./KanbanView";
import type { KanbanViewConfig, Record } from "./types";

const config: KanbanViewConfig = {
  column_field: "status",
  columns: [
    { value: "todo", label: "To Do", color: "#3B82F6" },
    { value: "in_progress", label: "In Progress", color: "#F59E0B" },
    { value: "done", label: "Done", color: "#10B981" },
  ],
  card_fields: ["title", "assignee"],
};

const records: Record[] = [
  { id: 1, title: "Task A", assignee: "Alice", status: "todo" },
  { id: 2, title: "Task B", assignee: "Bob", status: "in_progress" },
  { id: 3, title: "Task C", assignee: "Charlie", status: "done" },
  { id: 4, title: "Task D", assignee: "Diana", status: "todo" },
];

describe("KanbanView", () => {
  it("renders column headers", () => {
    render(<KanbanView config={config} records={records} />);
    expect(screen.getByText("To Do")).toBeInTheDocument();
    expect(screen.getByText("In Progress")).toBeInTheDocument();
    expect(screen.getByText("Done")).toBeInTheDocument();
  });

  it("groups records into correct columns", () => {
    render(<KanbanView config={config} records={records} />);
    // To Do column should have 2 items
    expect(screen.getByText("Task A")).toBeInTheDocument();
    expect(screen.getByText("Task D")).toBeInTheDocument();
    // In Progress has 1
    expect(screen.getByText("Task B")).toBeInTheDocument();
    // Done has 1
    expect(screen.getByText("Task C")).toBeInTheDocument();
  });

  it("shows record count per column", () => {
    render(<KanbanView config={config} records={records} />);
    // Find count badges — To Do: 2, In Progress: 1, Done: 1
    const counts = screen.getAllByText(/^[0-9]+$/);
    const countValues = counts.map((el) => el.textContent);
    expect(countValues).toContain("2");
    expect(countValues).toContain("1");
  });

  it("renders card fields on each card", () => {
    render(<KanbanView config={config} records={records} />);
    // Each card shows title and assignee
    expect(screen.getByText("Alice")).toBeInTheDocument();
    expect(screen.getByText("Bob")).toBeInTheDocument();
    expect(screen.getByText("Charlie")).toBeInTheDocument();
    expect(screen.getByText("Diana")).toBeInTheDocument();
  });

  it("calls onCardClick when card is clicked", () => {
    const onClick = vi.fn();
    render(<KanbanView config={config} records={records} onCardClick={onClick} />);
    fireEvent.click(screen.getByText("Task A"));
    expect(onClick).toHaveBeenCalledWith(records[0]);
  });

  it("handles drag and drop to move cards", () => {
    const onCardMove = vi.fn();
    render(<KanbanView config={config} records={records} onCardMove={onCardMove} />);

    const card = screen.getByText("Task A").closest("[draggable]")!;
    const columns = document.querySelectorAll(".kanban-column");
    const inProgressColumn = columns[1];

    // Start drag on Task A (id: 1)
    fireEvent.dragStart(card);
    // Drop on In Progress column
    fireEvent.dragOver(inProgressColumn);
    fireEvent.drop(inProgressColumn);

    expect(onCardMove).toHaveBeenCalledWith(1, "in_progress");
  });

  it("renders empty columns without errors", () => {
    const singleRecord: Record[] = [
      { id: 1, title: "Only Task", assignee: "Alice", status: "todo" },
    ];
    render(<KanbanView config={config} records={singleRecord} />);
    // All 3 columns render even though 2 are empty
    expect(screen.getByText("To Do")).toBeInTheDocument();
    expect(screen.getByText("In Progress")).toBeInTheDocument();
    expect(screen.getByText("Done")).toBeInTheDocument();
  });

  it("applies color to column headers", () => {
    render(<KanbanView config={config} records={records} />);
    const headers = document.querySelectorAll(".kanban-column-header");
    expect(headers[0]).toHaveStyle({ borderTopColor: "#3B82F6" });
    expect(headers[1]).toHaveStyle({ borderTopColor: "#F59E0B" });
    expect(headers[2]).toHaveStyle({ borderTopColor: "#10B981" });
  });

  it("makes cards draggable", () => {
    render(<KanbanView config={config} records={records} />);
    const card = screen.getByText("Task A").closest("[draggable]");
    expect(card).toHaveAttribute("draggable", "true");
  });

  it("renders cards as accessible buttons", () => {
    render(<KanbanView config={config} records={records} />);
    const buttons = screen.getAllByRole("button");
    expect(buttons.length).toBe(4); // 4 cards
  });
});
