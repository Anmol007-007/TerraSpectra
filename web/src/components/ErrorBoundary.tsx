import { Component, type ErrorInfo, type ReactNode } from "react";

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
  public override state: State = {
    hasError: false,
    error: null,
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public override componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error("ErrorBoundary caught an error:", error, errorInfo);
  }

  private handleReset = () => {
    this.setState({ hasError: false, error: null });
  };

  public override render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }
      return (
        <div
          data-testid="error-boundary-fallback"
          className="p-6 bg-red-950/80 border border-red-700/60 rounded-xl text-red-200 m-4 space-y-3"
        >
          <div className="flex items-center space-x-2">
            <span className="text-xl">⚠️</span>
            <h3 className="font-bold text-sm text-red-100 uppercase tracking-wider">
              Visualization Component Error
            </h3>
          </div>
          <p className="text-xs text-red-300 font-mono">
            {this.state.error?.message || "An unexpected error occurred in GIS rendering."}
          </p>
          <button
            onClick={this.handleReset}
            className="px-3 py-1.5 bg-red-800 hover:bg-red-700 text-white rounded text-xs font-semibold uppercase tracking-wider transition-colors"
          >
            Retry Render
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}
