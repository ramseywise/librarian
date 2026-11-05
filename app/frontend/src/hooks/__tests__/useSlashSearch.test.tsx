import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { useSlashSearch, VIEW_SEARCH_ATTR } from "../useSlashSearch";

function Harness({ children }: { children?: React.ReactNode }) {
  useSlashSearch();
  return <>{children}</>;
}

const search = { [VIEW_SEARCH_ATTR]: "", "aria-label": "search", defaultValue: "old" };

/** Dispatch `/` at the focused element; true when the app claimed it. */
function pressSlash(init: KeyboardEventInit = {}): boolean {
  return !fireEvent.keyDown(document.activeElement ?? document.body, { key: "/", ...init });
}

describe("useSlashSearch", () => {
  it("focuses and selects the view's search, and keeps the / out of it", () => {
    render(<Harness><input {...search} /></Harness>);
    expect(pressSlash()).toBe(true);
    const input = screen.getByLabelText("search") as HTMLInputElement;
    expect(document.activeElement).toBe(input);
    expect([input.selectionStart, input.selectionEnd]).toEqual([0, 3]);
  });

  it("works with focus on a button or canvas", () => {
    render(<Harness><button>go</button><input {...search} /></Harness>);
    screen.getByRole("button").focus();
    expect(pressSlash()).toBe(true);
    expect(document.activeElement).toBe(screen.getByLabelText("search"));
  });

  it.each([
    ["input", <input key="x" aria-label="other" />],
    ["textarea", <textarea key="x" aria-label="other" />],
    ["select", <select key="x" aria-label="other" />],
    ["contenteditable", <div key="x" aria-label="other" contentEditable suppressContentEditableWarning tabIndex={0} />],
  ])("leaves the key alone while focus is in a %s", (_name, field) => {
    render(<Harness>{field}<input {...search} /></Harness>);
    const other = screen.getByLabelText("other");
    other.focus();
    expect(pressSlash()).toBe(false);
    expect(document.activeElement).toBe(other);
  });

  it("does nothing with a modifier held", () => {
    render(<Harness><input {...search} /></Harness>);
    for (const mod of [{ ctrlKey: true }, { metaKey: true }, { altKey: true }]) {
      expect(pressSlash(mod)).toBe(false);
    }
    expect(document.activeElement).toBe(document.body);
  });

  it("skips a search on a hidden layer: the graph stays mounted under the course views", () => {
    render(
      <Harness>
        <div style={{ visibility: "hidden" }}><input {...search} aria-label="graph" /></div>
        <div style={{ display: "none" }}><input {...search} aria-label="menu" /></div>
        <input {...search} aria-label="courses" />
      </Harness>,
    );
    pressSlash();
    expect(document.activeElement).toBe(screen.getByLabelText("courses"));
  });

  it("keeps the key for the browser in a view with no search", () => {
    render(<Harness><button>go</button></Harness>);
    expect(pressSlash()).toBe(false);
  });
});
