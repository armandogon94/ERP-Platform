import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import Badge from "./Badge";
import Button from "./Button";
import Input from "./Input";
import Modal from "./Modal";
import Select from "./Select";

describe("Button", () => {
  it("renders children text", () => {
    render(<Button>Click me</Button>);
    expect(screen.getByText("Click me")).toBeInTheDocument();
  });

  it("applies variant class", () => {
    render(<Button variant="danger">Delete</Button>);
    expect(screen.getByText("Delete")).toHaveClass("btn-danger");
  });

  it("applies size class", () => {
    render(<Button size="sm">Small</Button>);
    expect(screen.getByText("Small")).toHaveClass("btn-sm");
  });

  it("disables button when loading", () => {
    render(<Button loading>Submit</Button>);
    const btn = screen.getByRole("button");
    expect(btn).toBeDisabled();
  });

  it("shows spinner when loading", () => {
    render(<Button loading>Submit</Button>);
    expect(screen.getByLabelText("Loading")).toBeInTheDocument();
  });

  it("disables button when disabled prop set", () => {
    render(<Button disabled>Submit</Button>);
    expect(screen.getByRole("button")).toBeDisabled();
  });

  it("calls onClick handler", () => {
    const onClick = vi.fn();
    render(<Button onClick={onClick}>Click</Button>);
    fireEvent.click(screen.getByText("Click"));
    expect(onClick).toHaveBeenCalled();
  });
});

describe("Input", () => {
  it("renders label when provided", () => {
    render(<Input label="Email" />);
    expect(screen.getByText("Email")).toBeInTheDocument();
  });

  it("links label to input via id", () => {
    render(<Input label="Email" />);
    const input = screen.getByLabelText("Email");
    expect(input).toBeInTheDocument();
  });

  it("shows error message", () => {
    render(<Input label="Email" error="Required field" />);
    expect(screen.getByText("Required field")).toBeInTheDocument();
    expect(screen.getByRole("alert")).toBeInTheDocument();
  });

  it("sets aria-invalid when error exists", () => {
    render(<Input label="Email" error="Bad" />);
    expect(screen.getByLabelText("Email")).toHaveAttribute("aria-invalid", "true");
  });

  it("renders without label", () => {
    render(<Input placeholder="Type here" />);
    expect(screen.getByPlaceholderText("Type here")).toBeInTheDocument();
  });
});

describe("Select", () => {
  const options = [
    { value: "a", label: "Option A" },
    { value: "b", label: "Option B" },
  ];

  it("renders options", () => {
    render(<Select options={options} />);
    expect(screen.getByText("Option A")).toBeInTheDocument();
    expect(screen.getByText("Option B")).toBeInTheDocument();
  });

  it("renders placeholder option", () => {
    render(<Select options={options} placeholder="Choose..." />);
    expect(screen.getByText("Choose...")).toBeInTheDocument();
  });

  it("renders label", () => {
    render(<Select label="Role" options={options} />);
    expect(screen.getByText("Role")).toBeInTheDocument();
  });

  it("shows error message", () => {
    render(<Select options={options} error="Pick one" />);
    expect(screen.getByText("Pick one")).toBeInTheDocument();
    expect(screen.getByRole("alert")).toBeInTheDocument();
  });

  it("calls onChange", () => {
    const onChange = vi.fn();
    render(<Select label="Role" options={options} onChange={onChange} />);
    fireEvent.change(screen.getByLabelText("Role"), { target: { value: "b" } });
    expect(onChange).toHaveBeenCalled();
  });
});

describe("Modal", () => {
  it("renders nothing when closed", () => {
    render(<Modal open={false} onClose={() => {}}>Content</Modal>);
    expect(screen.queryByText("Content")).not.toBeInTheDocument();
  });

  it("renders children when open", () => {
    render(<Modal open onClose={() => {}}>Content</Modal>);
    expect(screen.getByText("Content")).toBeInTheDocument();
  });

  it("renders title", () => {
    render(<Modal open onClose={() => {}} title="Confirm">Body</Modal>);
    expect(screen.getByText("Confirm")).toBeInTheDocument();
  });

  it("has dialog role with aria-modal", () => {
    render(<Modal open onClose={() => {}}>Body</Modal>);
    const dialog = screen.getByRole("dialog");
    expect(dialog).toHaveAttribute("aria-modal", "true");
  });

  it("calls onClose when close button clicked", () => {
    const onClose = vi.fn();
    render(<Modal open onClose={onClose}>Body</Modal>);
    fireEvent.click(screen.getByLabelText("Close"));
    expect(onClose).toHaveBeenCalled();
  });

  it("calls onClose when overlay clicked", () => {
    const onClose = vi.fn();
    render(<Modal open onClose={onClose}>Body</Modal>);
    fireEvent.click(screen.getByRole("presentation"));
    expect(onClose).toHaveBeenCalled();
  });

  it("does not close when modal content clicked", () => {
    const onClose = vi.fn();
    render(<Modal open onClose={onClose}>Body</Modal>);
    fireEvent.click(screen.getByText("Body"));
    expect(onClose).not.toHaveBeenCalled();
  });

  it("closes on Escape key", () => {
    const onClose = vi.fn();
    render(<Modal open onClose={onClose}>Body</Modal>);
    fireEvent.keyDown(document, { key: "Escape" });
    expect(onClose).toHaveBeenCalled();
  });
});

describe("Badge", () => {
  it("renders children text", () => {
    render(<Badge>Active</Badge>);
    expect(screen.getByText("Active")).toBeInTheDocument();
  });

  it("applies default variant class", () => {
    render(<Badge>Tag</Badge>);
    expect(screen.getByText("Tag")).toHaveClass("badge-default");
  });

  it("applies variant class", () => {
    render(<Badge variant="success">Done</Badge>);
    expect(screen.getByText("Done")).toHaveClass("badge-success");
  });

  it("applies custom className", () => {
    render(<Badge className="extra">Tag</Badge>);
    expect(screen.getByText("Tag")).toHaveClass("extra");
  });
});
