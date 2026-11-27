"""A real Pipecat pipeline with fake speech models and a fake model client: no download, no audio
device, no network. The point is what ends up in the logs while a session runs."""

from __future__ import annotations

import asyncio
import logging
import threading
from collections.abc import AsyncGenerator, Callable, Iterator
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest
from voice_fakes import FakeClient, Reply, grade_call

pytest.importorskip("pipecat")
pytest.importorskip("faster_whisper")

from loguru import logger
from pipecat.frames.frames import (
    EndFrame,
    Frame,
    InputAudioRawFrame,
    InterruptionFrame,
    TTSAudioRawFrame,
    VADUserStartedSpeakingFrame,
    VADUserStoppedSpeakingFrame,
)
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.task import PipelineParams, PipelineWorker
from pipecat.processors.aggregators.llm_context import LLMContext
from pipecat.processors.aggregators.llm_response_universal import (
    LLMUserAggregator,
    LLMUserAggregatorParams,
)
from pipecat.processors.frame_processor import FrameDirection, FrameProcessor
from pipecat.processors.frameworks.rtvi.frames import RTVIClientMessageFrame, RTVIServerMessageFrame
from pipecat.services.tts_service import TTSService
from pipecat.turns.user_start import VADUserTurnStartStrategy
from pipecat.turns.user_stop import SpeechTimeoutUserTurnStopStrategy
from pipecat.turns.user_turn_strategies import UserTurnStrategies
from pipecat.workers.runner import WorkerRunner

from librarian.courses import learning
from librarian.voice import grades, log_policy, pipeline
from librarian.voice.config import VoiceConfig
from librarian.voice.conversation import Conversation
from librarian.voice.latency import LatencyTracker
from librarian.voice.limits import SessionLimits
from librarian.voice.policy import Refusal, SessionPlan

SENTINEL = "zebrafish marmalade"
REPLY_SENTINEL = "quokka lantern"
RATE = 16_000
PLAN = SessionPlan(
    mode="approach",
    title="Invented",
    local_only=False,
    lesson="maths/m/drill",
    prompt="Count the lanterns.",
    reference="Keep a tally.",
)


class FakeWhisper:
    def transcribe(self, _audio: object, **_kw: object) -> tuple[list[Any], None]:
        return [SimpleNamespace(text=f"My answer is {SENTINEL}.", no_speech_prob=0.0)], None


class QuietTTS(TTSService):
    """Says nothing itself, so anything in a log came from Pipecat. Returns a little silence."""

    def __init__(self) -> None:
        super().__init__(sample_rate=24_000, push_stop_frames=True)
        self.texts: list[str] = []

    def can_generate_metrics(self) -> bool:
        return False

    async def run_tts(self, text: str, context_id: str) -> AsyncGenerator[Frame | None, None]:
        self.texts.append(text)
        yield TTSAudioRawFrame(b"\0\0" * 240, 24_000, 1, context_id=context_id)


class Script(FrameProcessor):
    """Sends speech frames as a VAD and microphone would."""

    async def play(self) -> None:
        await self.push_frame(VADUserStartedSpeakingFrame(), FrameDirection.DOWNSTREAM)
        silence = b"\0\0" * 320
        for _ in range(5):
            await self.push_frame(InputAudioRawFrame(silence, RATE, 1), FrameDirection.DOWNSTREAM)
        await self.push_frame(VADUserStoppedSpeakingFrame(), FrameDirection.DOWNSTREAM)

    async def process_frame(self, frame: Frame, direction: FrameDirection) -> None:
        await super().process_frame(frame, direction)
        await self.push_frame(frame, direction)


def _rig(
    client: FakeClient, tail: FrameProcessor | None = None
) -> tuple[Script, QuietTTS, PipelineWorker]:
    limits = SessionLimits(
        started=0.0, idle_timeout_s=60, max_duration_s=600, max_turns=5, max_tokens=1000
    )
    conversation = Conversation(PLAN, client, VoiceConfig(), limits, grades.grade_writer(None))  # type: ignore[arg-type]
    script = Script()
    tts = QuietTTS()
    turn_rules = UserTurnStrategies(
        start=[VADUserTurnStartStrategy()],
        stop=[SpeechTimeoutUserTurnStopStrategy(user_speech_timeout=0.05)],
    )
    users = LLMUserAggregator(
        LLMContext(), params=LLMUserAggregatorParams(user_turn_strategies=turn_rules)
    )
    turns = pipeline.ClaudeTurnProcessor(conversation, LatencyTracker())
    stt = pipeline.LocalWhisperSTT(FakeWhisper())
    worker = PipelineWorker(
        Pipeline([script, stt, users, turns, tts, *([tail] if tail else [])]),
        params=PipelineParams(audio_in_sample_rate=RATE, audio_out_sample_rate=24_000),
        enable_rtvi=False,
        idle_timeout_secs=None,
    )
    return script, tts, worker


async def _start(worker: PipelineWorker) -> asyncio.Task[None]:
    runner = WorkerRunner(handle_sigint=False, handle_sigterm=False)
    await runner.add_workers(worker)
    return asyncio.create_task(runner.run())


async def _session(client: FakeClient, mastery_log: Path) -> QuietTTS:
    script, tts, worker = _rig(client)
    run = await _start(worker)
    await asyncio.sleep(0.1)
    await script.play()
    await asyncio.wait_for(_until(lambda: REPLY_SENTINEL in " ".join(tts.texts)), 5)
    await asyncio.wait_for(_until(mastery_log.exists), 5)
    await worker.queue_frame(EndFrame())
    await asyncio.wait_for(run, 5)
    return tts


async def _until(check: Callable[[], bool]) -> None:
    while not check():
        await asyncio.sleep(0.01)


def _reply() -> Reply:
    return Reply(
        chunks=[f"You said {REPLY_SENTINEL}. "], blocks=[grade_call(0.5)], stop_reason="tool_use"
    )


@pytest.fixture
def restore_logs() -> Iterator[None]:
    yield
    logger.remove()
    logger.add(lambda _message: None, level="DEBUG")
    for name in log_policy.CHATTY_STDLIB_LOGGERS:
        logging.getLogger(name).setLevel(logging.NOTSET)


@pytest.fixture
def mastery_log(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    path = tmp_path / "mastery.jsonl"

    def record(_user_id: str, event: learning.EventIn) -> dict[str, Any]:
        with path.open("a") as out:  # A file, so the tests can see what was written and what not.
            out.write(event.model_dump_json() + "\n")
        return {"logged": True, "concepts": []}

    monkeypatch.setattr(learning, "record_event", record)
    monkeypatch.setattr(grades, "_learner", lambda _user_id: "learner")
    return path


async def test_control_pipecat_at_its_default_level_does_print_the_words(
    restore_logs: None, mastery_log: Path
) -> None:
    """Without this, the test below could pass on a pipeline that logs no words at all."""
    lines: list[str] = []
    logger.remove()
    logger.add(lines.append, level="DEBUG")
    await _session(FakeClient(_reply()), mastery_log)
    assert REPLY_SENTINEL in "".join(lines)  # tts_service logs what it speaks, at debug.


async def test_pinned_logging_keeps_every_word_out_of_every_log(
    restore_logs: None,
    mastery_log: Path,
    capfd: pytest.CaptureFixture[str],
    caplog: pytest.LogCaptureFixture,
    tmp_path: Path,
) -> None:
    lines: list[str] = []
    log_policy.pin_logging(sink=lines.append)
    caplog.set_level(logging.DEBUG)
    client = FakeClient(_reply())
    tts = await _session(client, mastery_log)

    # The words did go through: the model got them, and the voice said them.
    assert SENTINEL in str(client.requests[0]["messages"])
    assert REPLY_SENTINEL in " ".join(tts.texts)

    captured = capfd.readouterr()
    for sink in ("".join(lines), captured.out, captured.err, caplog.text):
        assert SENTINEL not in sink
        assert REPLY_SENTINEL not in sink
    grade_line = mastery_log.read_text()
    assert '"score":0.5' in grade_line.replace(" ", "")
    assert SENTINEL not in grade_line
    assert REPLY_SENTINEL not in grade_line
    written = [p for p in tmp_path.rglob("*") if p.is_file()]
    assert written == [mastery_log]


def test_an_error_prints_where_it_came_from_and_not_its_message(restore_logs: None) -> None:
    lines: list[str] = []
    log_policy.pin_logging(sink=lines.append)
    logger.debug(f"debug {SENTINEL}")
    logger.warning(f"warning {SENTINEL}")
    logger.error(f"boom {SENTINEL}")
    text = "".join(lines)
    assert SENTINEL not in text
    assert "ERROR" in text


def test_loguru_is_pinned_above_warning_where_kokoro_logs_its_text(restore_logs: None) -> None:
    lines: list[str] = []
    log_policy.pin_logging(sink=lines.append)
    logger.warning("anything")
    assert lines == []


# ── Fail closed, at the point the pipeline is built ──────────────────────────


LOCAL_ONLY = SessionPlan(mode="interview", title="t", local_only=True, lesson="interviewing/m/t")


@pytest.mark.parametrize("state", ["failed", "loading"])
def test_build_stt_refuses_without_the_local_model(
    state: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "not-a-real-key")
    models = SimpleNamespace(stt=state, whisper=None)
    with pytest.raises(Refusal):
        pipeline.build_stt(LOCAL_ONLY, models)  # type: ignore[arg-type]


def test_a_local_only_plan_that_says_hosted_is_refused_rather_than_built(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "not-a-real-key")
    plan = SessionPlan(mode="interview", title="t", local_only=True, stt="openai", tts="openai")
    models = SimpleNamespace(stt="ready", tts="ready", whisper=object(), kokoro_paths=None)
    with pytest.raises(Refusal):
        pipeline.build_stt(plan, models)  # type: ignore[arg-type]
    with pytest.raises(Refusal):
        pipeline.build_tts(plan, models, VoiceConfig())  # type: ignore[arg-type]


@pytest.mark.parametrize("state", ["failed", "loading"])
def test_build_tts_refuses_without_the_local_model(state: str) -> None:
    models = SimpleNamespace(tts=state, kokoro_paths=None)
    with pytest.raises(Refusal):
        pipeline.build_tts(LOCAL_ONLY, models, VoiceConfig())  # type: ignore[arg-type]


def test_a_load_failure_ends_as_failed_and_not_as_a_hosted_service(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    import faster_whisper

    def boom(*_a: object, **_kw: object) -> None:
        raise OSError("no model")

    monkeypatch.setattr(faster_whisper, "WhisperModel", boom)
    monkeypatch.setattr(pipeline, "ensure_kokoro", boom)
    models = pipeline.LocalModels(VoiceConfig(cache_dir=tmp_path))
    models.load()
    assert (models.stt, models.tts) == ("failed", "failed")


def test_a_phonemizer_that_will_not_load_fails_the_voice_closed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def no_espeak(_self: object, *_a: object) -> str:
        raise OSError("no espeak")

    monkeypatch.setattr(pipeline, "ensure_kokoro", lambda _dir: (tmp_path / "m", tmp_path / "v"))
    monkeypatch.setattr(pipeline.Tokenizer, "phonemize", no_espeak)
    models = pipeline.LocalModels(VoiceConfig(cache_dir=tmp_path))
    models.load()
    assert models.tts == "failed"


@pytest.mark.parametrize(("tts", "warmed"), [("local", True), ("openai", False)])
async def test_the_offer_warms_the_local_phonemizer_on_the_event_loop_thread(
    tts: str, warmed: bool, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Phonemizer caches per thread, and Kokoro calls it from the event loop's."""
    threads: list[int] = []

    async def no_connection(_request: object, _callback: object) -> None:
        return None

    monkeypatch.setattr(pipeline, "warm_phonemizer", lambda: threads.append(threading.get_ident()))
    cfg = VoiceConfig(cache_dir=tmp_path)
    session = pipeline.PipecatSession(
        SimpleNamespace(tts=tts),  # type: ignore[arg-type]
        cfg,
        pipeline.LocalModels(cfg),
        FakeClient(),  # type: ignore[arg-type]
        lambda: None,
    )
    monkeypatch.setattr(session._handler, "handle_web_request", no_connection)
    with pytest.raises(Refusal):
        await session.offer({"sdp": "v=0", "type": "offer"})
    assert threads == ([threading.get_ident()] if warmed else [])


async def test_a_voice_that_has_gone_silent_for_good_ends_the_session_and_says_so(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Otherwise each later turn is a billed call that nobody hears."""
    tts = QuietTTS()
    monkeypatch.setattr(pipeline, "build_tts", lambda *_a: tts)
    monkeypatch.setattr(pipeline, "build_stt", lambda *_a: pipeline.LocalWhisperSTT(FakeWhisper()))
    assembly = pipeline.assemble(
        PLAN,
        VoiceConfig(cache_dir=tmp_path),
        pipeline.LocalModels(VoiceConfig(cache_dir=tmp_path)),
        FakeClient(),  # type: ignore[arg-type]
        Script(),
        Script(),
    )
    told: list[dict[str, Any]] = []
    queue_frame = assembly.task.queue_frame

    async def spy(frame: Frame) -> None:
        if isinstance(frame, RTVIServerMessageFrame):
            told.append(frame.data)
        await queue_frame(frame)

    monkeypatch.setattr(assembly.task, "queue_frame", spy)
    running = await _start(assembly.task)
    await asyncio.sleep(1)
    assert not running.done()
    await tts.push_error("no audio", force_treat_as_permanent=True)
    # Not wait_for: the runner swallows a cancel and returns, which would look like an ending.
    _done, pending = await asyncio.wait({running}, timeout=10)
    if pending:
        await assembly.task.cancel()
    assert not pending, "the session carried on with no voice"
    assert told == [{"type": "ended", "reason": "speech_lost", "message": pipeline.SPEECH_LOST}]


# ── Barge-in ─────────────────────────────────────────────────────────────────


async def test_an_interruption_closes_the_in_flight_model_call(
    restore_logs: None, mastery_log: Path
) -> None:
    log_policy.pin_logging(sink=lambda _message: None)
    client = FakeClient(Reply(chunks=["First sentence. "], hang_after_chunks=True))
    script, _tts, worker = _rig(client)
    run = await _start(worker)
    await asyncio.sleep(0.1)
    await script.play()
    await asyncio.wait_for(client.hanging.wait(), 5)
    assert client.closed == 0
    await worker.queue_frame(InterruptionFrame())
    await asyncio.wait_for(_until(lambda: client.closed == 1), 5)
    await worker.queue_frame(EndFrame())
    await asyncio.wait_for(run, 5)
    assert not mastery_log.exists()


async def test_the_interrupt_button_closes_the_call_and_stops_output(
    restore_logs: None, mastery_log: Path
) -> None:
    log_policy.pin_logging(sink=lambda _message: None)
    client = FakeClient(Reply(chunks=["First sentence. "], hang_after_chunks=True))
    seen: list[Frame] = []

    class Tail(FrameProcessor):
        async def process_frame(self, frame: Frame, direction: FrameDirection) -> None:
            await super().process_frame(frame, direction)
            if isinstance(frame, InterruptionFrame):
                seen.append(frame)
            await self.push_frame(frame, direction)

    script, _tts, worker = _rig(client, Tail())
    run = await _start(worker)
    await asyncio.sleep(0.1)
    await script.play()
    await asyncio.wait_for(client.hanging.wait(), 5)
    await worker.queue_frame(RTVIClientMessageFrame(msg_id="m", type="other", data=None))
    await asyncio.sleep(0.05)
    assert client.closed == 0  # Only this message type interrupts.
    await worker.queue_frame(RTVIClientMessageFrame(msg_id="m", type="interrupt", data=None))
    await asyncio.wait_for(_until(lambda: client.closed == 1 and bool(seen)), 5)
    await worker.queue_frame(EndFrame())
    await asyncio.wait_for(run, 5)
    assert not mastery_log.exists()


async def test_ending_the_session_also_closes_the_in_flight_model_call(
    restore_logs: None, mastery_log: Path
) -> None:
    log_policy.pin_logging(sink=lambda _message: None)
    client = FakeClient(Reply(hang_after_chunks=True))
    script, _tts, worker = _rig(client)
    run = await _start(worker)
    await asyncio.sleep(0.1)
    await script.play()
    await asyncio.wait_for(client.hanging.wait(), 5)
    await worker.cancel()
    await asyncio.wait_for(run, 5)
    assert client.closed == 1
