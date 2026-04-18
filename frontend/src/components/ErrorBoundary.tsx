import { Component, type ErrorInfo, type ReactNode } from "react";

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  message: string;
}

/**
 * Class-based ErrorBoundary — React's `componentDidCatch` only works on
 * class components. Wraps the route outlet so a render-time crash in one
 * page doesn't take down the shell.
 */
export default class ErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false, message: "" };

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, message: error.message };
  }

  componentDidCatch(error: Error, info: ErrorInfo): void {
    // Log to console for dev; production error reporting would hook in here.
    console.error("ErrorBoundary caught:", error, info);
  }

  render() {
    if (this.state.hasError) {
      return (
        this.props.fallback ?? (
          <div className="error-boundary">
            <h1>Something went wrong</h1>
            <p>
              The application hit an unexpected error. Try reloading; if this keeps
              happening, contact your administrator.
            </p>
            <details>
              <summary>Error details</summary>
              <pre>{this.state.message}</pre>
            </details>
            <button
              type="button"
              onClick={() => this.setState({ hasError: false, message: "" })}
            >
              Try again
            </button>
          </div>
        )
      );
    }
    return this.props.children;
  }
}
