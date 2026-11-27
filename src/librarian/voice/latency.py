"""Per-turn latency, as numbers only: the ship condition is a gap under about 1.5 s.

The gap runs from when the user stopped speaking to the first audio going out. VAD reports the
stop only after `vad_stop_ms` of silence, so that wait is counted back in, or the figure would
flatter the pipeline by exactly the wait the user sits through.

    vad_stop_ms   silence the VAD waits for before it reports the stop (a setting, not measured)
    stt_ms        VAD stop to final transcript
    turn_ms       VAD stop to the turn being closed and sent to the LLM (includes stt_ms)
    llm_first_ms  LLM request to its first spoken text
    tts_first_ms  first spoken text to the first synthesized audio
    output_ms     first synthesized audio to the transport reporting speech started
    gap_ms        the whole gap, including vad_stop_ms
"""

from __future__ import annotations

from dataclasses import dataclass

Report = dict[str, float | int | None]


def _ms(start: float | None, end: float | None) -> float | None:
    if start is None or end is None or end < start:
        return None
    return round((end - start) * 1000, 1)


@dataclass
class TurnLatency:
    vad_stop_ms: float = 0.0
    stopped: float | None = None
    transcript: float | None = None
    turn_closed: float | None = None
    llm_request: float | None = None
    llm_first: float | None = None
    tts_first: float | None = None
    bot_started: float | None = None

    def report(self, turn: int) -> Report:
        gap = _ms(self.stopped, self.bot_started)
        return {
            "turn": turn,
            "vad_stop_ms": self.vad_stop_ms,
            "stt_ms": _ms(self.stopped, self.transcript),
            "turn_ms": _ms(self.stopped, self.turn_closed),
            "llm_first_ms": _ms(self.llm_request, self.llm_first),
            "tts_first_ms": _ms(self.llm_first, self.tts_first),
            "output_ms": _ms(self.tts_first, self.bot_started),
            "gap_ms": round(gap + self.vad_stop_ms, 1) if gap is not None else None,
        }


class LatencyTracker:
    """Fed timestamps by the pipeline observer. Knows nothing of frames or what they carry.

    The first mark of each kind wins, as the same frame is seen at every processor it crosses.
    """

    def __init__(self, vad_stop_ms: float = 0.0) -> None:
        self._vad_stop_ms = vad_stop_ms
        self._turn = 0
        self._current = TurnLatency(vad_stop_ms=vad_stop_ms)

    def user_started(self) -> None:
        """Speech resumed before the reply, or a barge-in: what was measured is void."""
        self._current = TurnLatency(vad_stop_ms=self._vad_stop_ms)

    def user_stopped(self, now: float) -> None:
        """A pause then more speech passes through `user_started`, so the stop kept is the last
        one before the reply. The same stop is broadcast both ways, so the first of those wins."""
        if self._current.stopped is None:
            self._current = TurnLatency(vad_stop_ms=self._vad_stop_ms, stopped=now)

    def _mark(self, field: str, now: float) -> None:
        if self._current.stopped is not None and getattr(self._current, field) is None:
            setattr(self._current, field, now)

    def transcript(self, now: float) -> None:
        self._mark("transcript", now)

    def turn_closed(self, now: float) -> None:
        self._mark("turn_closed", now)

    def llm_request(self, now: float) -> None:
        self._mark("llm_request", now)

    def llm_first(self, now: float) -> None:
        self._mark("llm_first", now)

    def tts_first(self, now: float) -> None:
        self._mark("tts_first", now)

    def bot_started(self, now: float) -> Report | None:
        """Close the turn and return its report, or None if no user turn was being timed: the
        opening line and the next card have no stop to measure from."""
        if self._current.stopped is None:
            return None
        self._mark("bot_started", now)
        self._turn += 1
        report = self._current.report(self._turn)
        self._current = TurnLatency(vad_stop_ms=self._vad_stop_ms)
        return report
