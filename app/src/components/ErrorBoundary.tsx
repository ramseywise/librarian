import { Component, type ErrorInfo, type ReactNode } from "react";

interface Props {
  /** What the boundary guards, for the message ("This page"). */
  what: string;
  /** The boundary forgets its error when this changes (the route), so navigating away recovers. */
  resetKey?: string;
  children: ReactNode;
}

interface State {
  error: Error | null;
}

/**
 * Catches a render error, or a lazy chunk that failed to load, below it and shows it with a
 * Retry button instead of a blank page. The rest of the app (navigation, chat, the map under
 * a course page) keeps running.
 */
export class ErrorBoundary extends Component<Props, State> {
  state: State = { error: null };

  static getDerivedStateFromError(error: Error): State {
    return { error };
  }

  componentDidCatch(error: Error, info: ErrorInfo): void {
    console.error(`${this.props.what} failed to render`, error, info.componentStack);
  }

  componentDidUpdate(prev: Props): void {
    if (this.state.error && prev.resetKey !== this.props.resetKey) this.setState({ error: null });
  }

  render(): ReactNode {
    const { error } = this.state;
    if (!error) return this.props.children;
    return (
      <div className="app-loading" role="alert">
        {this.props.what} failed to load: {error.message}
        <div>
          <button type="button" className="pill-btn" onClick={() => this.setState({ error: null })}>
            Retry
          </button>
        </div>
      </div>
    );
  }
}
