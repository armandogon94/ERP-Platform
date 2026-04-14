import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import FormView from "./FormView";
import type { FormViewConfig, Record } from "./types";

const config: FormViewConfig = {
  sections: [
    {
      title: "General",
      fields: [
        { field: "name", label: "Name", type: "char", required: true },
        {
          field: "email",
          label: "Email",
          type: "char",
          placeholder: "user@example.com",
        },
        { field: "notes", label: "Notes", type: "text" },
      ],
    },
    {
      title: "Settings",
      fields: [
        { field: "active", label: "Active", type: "boolean" },
        { field: "age", label: "Age", type: "integer" },
        {
          field: "role",
          label: "Role",
          type: "selection",
          options: [
            { value: "admin", label: "Admin" },
            { value: "user", label: "User" },
          ],
        },
      ],
    },
  ],
};

const record: Record = {
  id: 1,
  name: "Alice",
  email: "alice@example.com",
  notes: "Some notes",
  active: true,
  age: 30,
  role: "admin",
};

describe("FormView", () => {
  it("renders section titles as legends", () => {
    render(<FormView config={config} />);
    expect(screen.getByText("General")).toBeInTheDocument();
    expect(screen.getByText("Settings")).toBeInTheDocument();
  });

  it("renders field labels", () => {
    render(<FormView config={config} />);
    expect(screen.getByText("Name")).toBeInTheDocument();
    expect(screen.getByText("Email")).toBeInTheDocument();
    expect(screen.getByText("Active")).toBeInTheDocument();
  });

  it("shows required indicator on required fields", () => {
    render(<FormView config={config} />);
    expect(screen.getByText("*")).toBeInTheDocument();
  });

  it("populates form with existing record data", () => {
    render(<FormView config={config} record={record} />);
    const nameInput = screen.getByLabelText(/Name/) as HTMLInputElement;
    expect(nameInput.value).toBe("Alice");

    const activeCheckbox = screen.getByLabelText(/Active/) as HTMLInputElement;
    expect(activeCheckbox.checked).toBe(true);

    const ageInput = screen.getByLabelText(/Age/) as HTMLInputElement;
    expect(ageInput.value).toBe("30");
  });

  it("renders text field as textarea", () => {
    render(<FormView config={config} />);
    const notesField = document.querySelector("#field-notes");
    expect(notesField?.tagName).toBe("TEXTAREA");
  });

  it("renders boolean field as checkbox", () => {
    render(<FormView config={config} />);
    const checkbox = screen.getByLabelText(/Active/) as HTMLInputElement;
    expect(checkbox.type).toBe("checkbox");
  });

  it("renders integer field as number input with step=1", () => {
    render(<FormView config={config} />);
    const ageInput = screen.getByLabelText(/Age/) as HTMLInputElement;
    expect(ageInput.type).toBe("number");
    expect(ageInput.step).toBe("1");
  });

  it("renders selection field as select with options", () => {
    render(<FormView config={config} />);
    const select = screen.getByLabelText(/Role/) as HTMLSelectElement;
    expect(select.tagName).toBe("SELECT");
    expect(screen.getByText("Admin")).toBeInTheDocument();
    expect(screen.getByText("User")).toBeInTheDocument();
    expect(screen.getByText("-- Select --")).toBeInTheDocument();
  });

  it("calls onSave with form data on submit", () => {
    const onSave = vi.fn();
    render(<FormView config={config} record={record} onSave={onSave} />);
    fireEvent.submit(screen.getByRole("form"));
    expect(onSave).toHaveBeenCalledWith(
      expect.objectContaining({
        name: "Alice",
        email: "alice@example.com",
        active: true,
      }),
    );
  });

  it("calls onCancel when cancel button clicked", () => {
    const onCancel = vi.fn();
    render(<FormView config={config} onCancel={onCancel} />);
    fireEvent.click(screen.getByText("Cancel"));
    expect(onCancel).toHaveBeenCalled();
  });

  it("hides save/cancel buttons in readonly mode", () => {
    render(<FormView config={config} record={record} readonly />);
    expect(screen.queryByText("Save")).not.toBeInTheDocument();
    expect(screen.queryByText("Cancel")).not.toBeInTheDocument();
  });

  it("disables inputs in readonly mode", () => {
    render(<FormView config={config} record={record} readonly />);
    const nameInput = screen.getByLabelText(/Name/) as HTMLInputElement;
    expect(nameInput.disabled).toBe(true);
  });

  it("updates form data on input change", () => {
    const onSave = vi.fn();
    render(<FormView config={config} onSave={onSave} />);
    const nameInput = screen.getByLabelText(/Name/) as HTMLInputElement;
    fireEvent.change(nameInput, { target: { value: "Bob" } });
    fireEvent.submit(screen.getByRole("form"));
    expect(onSave).toHaveBeenCalledWith(expect.objectContaining({ name: "Bob" }));
  });

  it("renders placeholder text on inputs", () => {
    render(<FormView config={config} />);
    const emailInput = screen.getByPlaceholderText("user@example.com");
    expect(emailInput).toBeInTheDocument();
  });
});
