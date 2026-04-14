import type { SelectHTMLAttributes } from "react";

export interface SelectOption {
  value: string;
  label: string;
}

interface SelectProps extends SelectHTMLAttributes<HTMLSelectElement> {
  label?: string;
  error?: string;
  options: SelectOption[];
  placeholder?: string;
}

export default function Select({
  label,
  error,
  options,
  placeholder,
  id,
  className = "",
  ...rest
}: SelectProps) {
  const selectId =
    id || (label ? `select-${label.toLowerCase().replace(/\s+/g, "-")}` : undefined);

  return (
    <div className={`select-group ${error ? "select-error" : ""} ${className}`.trim()}>
      {label && <label htmlFor={selectId}>{label}</label>}
      <select id={selectId} aria-invalid={!!error} {...rest}>
        {placeholder && <option value="">{placeholder}</option>}
        {options.map((opt) => (
          <option key={opt.value} value={opt.value}>
            {opt.label}
          </option>
        ))}
      </select>
      {error && (
        <span className="select-error-message" role="alert">
          {error}
        </span>
      )}
    </div>
  );
}
