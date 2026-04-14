import type { InputHTMLAttributes } from "react";

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
}

export default function Input({
  label,
  error,
  id,
  className = "",
  ...rest
}: InputProps) {
  const inputId =
    id || (label ? `input-${label.toLowerCase().replace(/\s+/g, "-")}` : undefined);

  return (
    <div className={`input-group ${error ? "input-error" : ""} ${className}`.trim()}>
      {label && <label htmlFor={inputId}>{label}</label>}
      <input id={inputId} aria-invalid={!!error} {...rest} />
      {error && (
        <span className="input-error-message" role="alert">
          {error}
        </span>
      )}
    </div>
  );
}
