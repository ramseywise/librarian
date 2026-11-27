import { act, cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { useDictation, type DictationEnd } from "../../../hooks/useSpeech";
import { FakeRecognition, installFakeRecognition } from "../../../test/fakeSpeech";
import { DICTATION_NOTICE } from "../../../voice/policy";
import { MicButton } from "../MicButton";

const results: [string, DictationEnd][] = [];
function Harness({ disabled }: { disabled?: boolean }) {
  const dictation = useDictation((text, how) => results.push([text, how]));
  return <MicButton dictation={dictation} disabled={disabled} label="Hold to talk" />;
}
const button = () => screen.getByRole("button");
const setup = (disabled?: boolean) => {
  results.length = 0;
  installFakeRecognition();
  return render(<Harness disabled={disabled} />);
};
const live = () => button().getAttribute("aria-pressed") === "true";
/** Advance performance.now() past or within the tap limit. */
const wait = (ms: number) => vi.spyOn(performance, "now").mockReturnValue(performance.now() + ms);

afterEach(() => {
  cleanup();
  vi.restoreAllMocks();
  vi.unstubAllGlobals();
});

describe("MicButton", () => {
  it("names itself, and always shows and titles the cloud notice", () => {
    setup();
    expect(button()).toHaveAccessibleName("Hold to talk");
    expect(button().getAttribute("title")).toContain(DICTATION_NOTICE);
    expect(screen.getByText(DICTATION_NOTICE)).toBeVisible();
    expect(button()).toHaveAccessibleDescription(DICTATION_NOTICE);
  });

  it("hold and release with a pointer delivers as released", () => {
    setup();
    fireEvent.pointerDown(button(), { button: 0 });
    expect(live()).toBe(true);
    expect(button()).toHaveAccessibleName(/release to finish/);
    FakeRecognition.last.hear("spoken words");
    wait(1000);
    fireEvent.pointerUp(button());
    expect(FakeRecognition.last.stopped).toBe(true);
    FakeRecognition.last.end();
    expect(results).toEqual([["spoken words", "released"]]);
    expect(live()).toBe(false);
  });

  it("a right-click does not start it", () => {
    setup();
    fireEvent.pointerDown(button(), { button: 2 });
    expect(FakeRecognition.instances).toHaveLength(0);
  });

  it("a quick tap latches until the next press", () => {
    setup();
    fireEvent.pointerDown(button(), { button: 0 });
    fireEvent.pointerUp(button());
    expect(FakeRecognition.last.stopped).toBe(false);
    expect(button()).toHaveAccessibleName(/press to finish/);
    FakeRecognition.last.hear("latched words");
    fireEvent.pointerDown(button(), { button: 0 });
    expect(FakeRecognition.last.stopped).toBe(true);
    fireEvent.pointerUp(button());
    FakeRecognition.last.end();
    expect(results).toEqual([["latched words", "released"]]);
  });

  it.each([[" "], ["Enter"]])("holds with the key %j, ignoring auto-repeat", (key) => {
    setup();
    fireEvent.keyDown(button(), { key });
    fireEvent.keyDown(button(), { key, repeat: true });
    expect(FakeRecognition.instances).toHaveLength(1);
    FakeRecognition.last.hear("keyed words");
    wait(1000);
    fireEvent.keyUp(button(), { key });
    FakeRecognition.last.end();
    expect(results).toEqual([["keyed words", "released"]]);
  });

  it("a click with no pointer, as from a screen reader, toggles", () => {
    setup();
    fireEvent.click(button(), { detail: 0 });
    expect(live()).toBe(true);
    FakeRecognition.last.hear("assistive words");
    fireEvent.click(button(), { detail: 0 });
    FakeRecognition.last.end();
    expect(results).toEqual([["assistive words", "released"]]);
  });

  it("the click that follows a key lift is not a second toggle", () => {
    setup();
    fireEvent.keyDown(button(), { key: " " });
    wait(1000);
    fireEvent.keyUp(button(), { key: " " });
    fireEvent.click(button(), { detail: 0 });
    expect(FakeRecognition.instances).toHaveLength(1);
  });

  it("Escape discards", () => {
    setup();
    fireEvent.keyDown(button(), { key: " " });
    FakeRecognition.last.hear("unwanted");
    fireEvent.keyDown(button(), { key: "Escape" });
    expect(FakeRecognition.last.aborted).toBe(true);
    expect(live()).toBe(false);
    expect(results).toEqual([]);
  });

  it.each([
    ["pointer cancel", () => fireEvent.pointerCancel(button())],
    ["focus leaving", () => fireEvent.blur(button())],
  ])("%s finishes without counting as a release", (_name, leave) => {
    setup();
    fireEvent.pointerDown(button(), { button: 0 });
    FakeRecognition.last.hear("half said");
    leave();
    FakeRecognition.last.end();
    expect(results).toEqual([["half said", "ended"]]);
  });

  it("does nothing while disabled, and becoming disabled ends a live session", () => {
    const { rerender } = setup(true);
    fireEvent.pointerDown(button(), { button: 0 });
    expect(FakeRecognition.instances).toHaveLength(0);
    rerender(<Harness />);
    fireEvent.pointerDown(button(), { button: 0 });
    FakeRecognition.last.hear("words");
    act(() => rerender(<Harness disabled />));
    expect(FakeRecognition.last.stopped).toBe(true);
    FakeRecognition.last.end();
    expect(results).toEqual([["words", "ended"]]);
  });
});
