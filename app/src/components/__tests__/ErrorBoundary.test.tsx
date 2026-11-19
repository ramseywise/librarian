import { fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { ErrorBoundary } from "../ErrorBoundary";
import { ResourceNotice } from "../ResourceNotice";

let broken = true;
function Bomb() {
  if (broken) throw new Error("chunk failed");
  return <p>fine</p>;
}

afterEach(() => {
  broken = true;
  vi.restoreAllMocks();
});

describe("ErrorBoundary", () => {
  it("shows the failure and recovers on Retry", () => {
    vi.spyOn(console, "error").mockImplementation(() => {});
    render(<ErrorBoundary what="This page"><Bomb /></ErrorBoundary>);
    expect(screen.getByRole("alert").textContent).toContain("This page failed to load: chunk failed");
    broken = false;
    fireEvent.click(screen.getByRole("button", { name: "Retry" }));
    expect(screen.getByText("fine")).toBeTruthy();
  });

  it("forgets the error when the route key changes", () => {
    vi.spyOn(console, "error").mockImplementation(() => {});
    const { rerender } = render(<ErrorBoundary what="This page" resetKey="a"><Bomb /></ErrorBoundary>);
    expect(screen.getByRole("alert")).toBeTruthy();
    broken = false;
    rerender(<ErrorBoundary what="This page" resetKey="b"><Bomb /></ErrorBoundary>);
    expect(screen.getByText("fine")).toBeTruthy();
  });
});

describe("ResourceNotice", () => {
  it("names what failed and retries", () => {
    const onRetry = vi.fn();
    render(<ResourceNotice what="The glossary" error="HTTP 500" onRetry={onRetry} />);
    expect(screen.getByRole("alert").textContent).toContain("The glossary did not load: HTTP 500");
    fireEvent.click(screen.getByRole("button", { name: "Retry" }));
    expect(onRetry).toHaveBeenCalledTimes(1);
  });
});
