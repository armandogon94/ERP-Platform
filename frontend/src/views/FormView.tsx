import { type FormEvent, useState } from "react";
import type { FormViewConfig, Record } from "./types";

interface FormViewProps {
  config: FormViewConfig;
  record?: Record;
  onSave?: (data: Partial<Record>) => void;
  onCancel?: () => void;
  readonly?: boolean;
}

export default function FormView({
  config,
  record,
  onSave,
  onCancel,
  readonly = false,
}: FormViewProps) {
  const [formData, setFormData] = useState<Partial<Record>>(() => {
    if (record) return { ...record };
    const defaults: Partial<Record> = {};
    for (const section of config.sections) {
      for (const field of section.fields) {
        if (field.type === "boolean") defaults[field.field] = false;
        else defaults[field.field] = "";
      }
    }
    return defaults;
  });

  const handleChange = (field: string, value: unknown) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    onSave?.(formData);
  };

  return (
    <form className="form-view" onSubmit={handleSubmit} aria-label="Record form">
      {config.sections.map((section) => (
        <fieldset key={section.title} className="form-section">
          <legend>{section.title}</legend>
          {section.fields.map((field) => {
            const isReadonly = readonly || field.readonly;
            const value = formData[field.field];

            return (
              <div key={field.field} className="form-field">
                <label htmlFor={`field-${field.field}`}>
                  {field.label}
                  {field.required && <span className="required"> *</span>}
                </label>
                {renderInput(field, value, isReadonly, (v) =>
                  handleChange(field.field, v),
                )}
              </div>
            );
          })}
        </fieldset>
      ))}

      {!readonly && (
        <div className="form-actions">
          <button type="submit" className="btn-primary">
            Save
          </button>
          {onCancel && (
            <button type="button" className="btn-secondary" onClick={onCancel}>
              Cancel
            </button>
          )}
        </div>
      )}
    </form>
  );
}

function renderInput(
  field: {
    field: string;
    type: string;
    placeholder?: string;
    options?: { value: string; label: string }[];
    required?: boolean;
  },
  value: unknown,
  readonly: boolean,
  onChange: (v: unknown) => void,
) {
  const id = `field-${field.field}`;
  const commonProps = {
    id,
    disabled: readonly,
    required: field.required,
  };

  switch (field.type) {
    case "text":
      return (
        <textarea
          {...commonProps}
          value={String(value ?? "")}
          onChange={(e) => onChange(e.target.value)}
          placeholder={field.placeholder}
        />
      );

    case "boolean":
      return (
        <input
          {...commonProps}
          type="checkbox"
          checked={Boolean(value)}
          onChange={(e) => onChange(e.target.checked)}
        />
      );

    case "integer":
    case "float":
    case "decimal":
      return (
        <input
          {...commonProps}
          type="number"
          step={field.type === "integer" ? "1" : "0.01"}
          value={value != null ? String(value) : ""}
          onChange={(e) => onChange(Number(e.target.value))}
          placeholder={field.placeholder}
        />
      );

    case "date":
      return (
        <input
          {...commonProps}
          type="date"
          value={String(value ?? "")}
          onChange={(e) => onChange(e.target.value)}
        />
      );

    case "datetime":
      return (
        <input
          {...commonProps}
          type="datetime-local"
          value={String(value ?? "")}
          onChange={(e) => onChange(e.target.value)}
        />
      );

    case "selection":
      return (
        <select
          {...commonProps}
          value={String(value ?? "")}
          onChange={(e) => onChange(e.target.value)}
        >
          <option value="">-- Select --</option>
          {field.options?.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>
      );

    default:
      return (
        <input
          {...commonProps}
          type="text"
          value={String(value ?? "")}
          onChange={(e) => onChange(e.target.value)}
          placeholder={field.placeholder}
        />
      );
  }
}
