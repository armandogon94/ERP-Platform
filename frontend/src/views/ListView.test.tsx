import { fireEvent, render, screen, within } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import ListView from "./ListView";
import type { ListViewConfig, Record } from "./types";

const config: ListViewConfig = {
  columns: [
    { field: "name", label: "Name", sortable: true },
    { field: "department", label: "Department", sortable: true },
    { field: "status", label: "Status" },
  ],
  search_fields: ["name", "department"],
};

const records: Record[] = [
  { id: 1, name: "Alice", department: "Engineering", status: "active" },
  { id: 2, name: "Bob", department: "Sales", status: "active" },
  { id: 3, name: "Charlie", department: "Engineering", status: "inactive" },
];

describe("ListView", () => {
  it("renders column headers", () => {
    render(<ListView config={config} records={records} />);
    expect(screen.getByText("Name")).toBeInTheDocument();
    expect(screen.getByText("Department")).toBeInTheDocument();
    expect(screen.getByText("Status")).toBeInTheDocument();
  });

  it("renders all records", () => {
    render(<ListView config={config} records={records} />);
    expect(screen.getByText("Alice")).toBeInTheDocument();
    expect(screen.getByText("Bob")).toBeInTheDocument();
    expect(screen.getByText("Charlie")).toBeInTheDocument();
  });

  it("shows record count in footer", () => {
    render(<ListView config={config} records={records} />);
    expect(screen.getByText("3 records")).toBeInTheDocument();
  });

  it("shows empty state when no records", () => {
    render(<ListView config={config} records={[]} />);
    expect(screen.getByText("No records found.")).toBeInTheDocument();
  });

  it("sorts by column on header click", () => {
    render(<ListView config={config} records={records} />);
    const nameHeader = screen.getByText("Name");

    // Click to sort ascending
    fireEvent.click(nameHeader);
    const rows = screen.getAllByRole("row");
    // row[0] is header, row[1] is first data row
    expect(within(rows[1]).getByText("Alice")).toBeInTheDocument();

    // Click again to sort descending
    fireEvent.click(nameHeader);
    const rowsDesc = screen.getAllByRole("row");
    expect(within(rowsDesc[1]).getByText("Charlie")).toBeInTheDocument();
  });

  it("filters records via search", () => {
    render(<ListView config={config} records={records} />);
    const searchInput = screen.getByPlaceholderText("Search...");

    fireEvent.change(searchInput, { target: { value: "engineer" } });
    expect(screen.getByText("Alice")).toBeInTheDocument();
    expect(screen.getByText("Charlie")).toBeInTheDocument();
    expect(screen.queryByText("Bob")).not.toBeInTheDocument();
    expect(screen.getByText("2 records")).toBeInTheDocument();
  });

  it("calls onRowClick when row is clicked", () => {
    const onClick = vi.fn();
    render(<ListView config={config} records={records} onRowClick={onClick} />);
    fireEvent.click(screen.getByText("Alice"));
    expect(onClick).toHaveBeenCalledWith(records[0]);
  });

  it("renders search input only when search_fields defined", () => {
    const noSearchConfig = { ...config, search_fields: undefined };
    render(<ListView config={noSearchConfig} records={records} />);
    expect(screen.queryByPlaceholderText("Search...")).not.toBeInTheDocument();
  });

  it("formats boolean values", () => {
    const boolConfig: ListViewConfig = {
      columns: [
        { field: "name", label: "Name" },
        { field: "active", label: "Active" },
      ],
    };
    const boolRecords: Record[] = [
      { id: 1, name: "Item", active: true },
      { id: 2, name: "Other", active: false },
    ];
    render(<ListView config={boolConfig} records={boolRecords} />);
    expect(screen.getByText("Yes")).toBeInTheDocument();
    expect(screen.getByText("No")).toBeInTheDocument();
  });
});
