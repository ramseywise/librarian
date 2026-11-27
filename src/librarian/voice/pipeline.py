"""The Pipecat side: audio in, turn detection, speech to text, the conversation, speech out.

The only module here that imports Pipecat or a speech model, and only `__main__` imports it. Call
`log_policy.pin_logging` before importing this: importing Pipecat logs, and its default sink would
otherwise print everything said in the session.

Audio stays in memory: Whisper reads a turn's PCM buffer and Kokoro's output goes to the transport.
Nothing in this pipeline records it. The live transcript travels to the browser as RTVI messages
and is not kept at either end.
"""

from __future__ import annotations

import asyncio
import hashlib
import os
import threading
import time
from collections.abc import AsyncGenerator, Callable
from contextlib import aclosing
from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast

import anthropic
import httpx
import numpy as np
from kokoro_onnx.tokenizer import Tokenizer
from pipecat.audio.vad.silero import SileroVADAnalyzer
from pipecat.audio.vad.vad_analyzer import VADParams
from pipecat.frames.frames import (
    BotStartedSpeakingFrame,
    BotStoppedSpeakingFrame,
    CancelFrame,
    EndFrame,
    EndWorkerFrame,
    Frame,
    InterruptionFrame,
    LLMContextFrame,
    TranscriptionFrame,
    TTSAudioRawFrame,
    TTSSpeakFrame,
    UserStartedSpeakingFrame,
    UserStoppedSpeakingFrame,
    VADUserStartedSpeakingFrame,
    VADUserStoppedSpeakingFrame,
)
from pipecat.observers.base_observer import BaseObserver, FramePushed
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.worker import PipelineParams, PipelineWorker, ProcessorUnusablePolicy
from pipecat.processors.aggregators.llm_context import LLMContext
from pipecat.processors.aggregators.llm_response_universal import (
    LLMUserAggregator,
    LLMUserAggregatorParams,
)
from pipecat.processors.frame_processor import FrameDirection, FrameProcessor
from pipecat.processors.frameworks.rtvi.frames import (
    RTVIClientMessageFrame,
    RTVIServerMessageFrame,
)
from pipecat.processors.frameworks.rtvi.observer import RTVIObserverParams
from pipecat.services.kokoro.tts import KokoroTTSService
from pipecat.services.settings import STTSettings
from pipecat.services.stt_service import SegmentedSTTService
from pipecat.transcriptions.language import Language
from pipecat.transports.base_transport import TransportParams
from pipecat.transports.smallwebrtc.request_handler import (
    ConnectionMode,
    IceCandidate,
    SmallWebRTCPatchRequest,
    SmallWebRTCRequest,
    SmallWebRTCRequestHandler,
)
from pipecat.transports.smallwebrtc.transport import SmallWebRTCTransport
from pipecat.utils.time import time_now_iso8601
from pipecat.workers.runner import WorkerRunner

from librarian.log_config import get_logger

from .config import VoiceConfig
from .conversation import Conversation, Finished, Graded, Say, Ungraded
from .grades import grade_writer
from .latency import LatencyTracker
from .limits import END_MESSAGES, SessionLimits
from .policy import HOSTED_PROVIDER, LOCAL_PROVIDER, Refusal, SessionPlan

log = get_logger(__name__)

KOKORO_BASE_URL = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0"
KOKORO_FILES = {
    "kokoro-v1.0.int8.onnx": "6e742170d309016e5891a994e1ce1559c702a2ccd0075e67ef7157974f6406cb",
    "voices-v1.0.bin": "bca610b8308e8d99f32e6fe4197e7ec01679264efed0cac9140fe9c29f1fbf7d",
}
VAD_STOP_SECS = 0.2  # Pipecat's value when a smart-turn model decides the end of the turn.
NO_SPEECH_THRESHOLD = 0.6
# How long a closed turn waits for Whisper's transcript of its last segment. It ends sooner once
# that arrives, so this only costs time when the segment holds no speech. Too short and, on a busy
# machine, the turn goes off with the words before a pause and the rest starts a new turn: seen.
STT_WAIT_S = 2.5
WATCHDOG_INTERVAL_S = 1.0
IN_SAMPLE_RATE = 16_000
OUT_SAMPLE_RATE = 24_000

Notify = Callable[[dict[str, Any]], Any]


def ensure_kokoro(cache_dir: Path) -> tuple[Path, Path]:
    """The small int8 model with its voices. Pipecat's own default would fetch the larger one."""
    directory = cache_dir / "kokoro"
    directory.mkdir(parents=True, exist_ok=True)
    for name, digest in KOKORO_FILES.items():
        target = directory / name
        if target.exists():
            continue
        partial = target.with_suffix(target.suffix + ".part")
        hasher = hashlib.sha256()
        with (
            httpx.Client(follow_redirects=True, timeout=60.0) as client,
            client.stream("GET", f"{KOKORO_BASE_URL}/{name}") as response,
            partial.open("wb") as f,
        ):
            response.raise_for_status()
            for chunk in response.iter_bytes():
                hasher.update(chunk)
                f.write(chunk)
        if hasher.hexdigest() != digest:
            partial.unlink(missing_ok=True)
            raise ValueError(f"checksum mismatch for {name}")
        partial.rename(target)
    return tuple(directory / name for name in KOKORO_FILES)  # type: ignore[return-value]


class LocalModels:
    """Local speech models, loaded once in the background so startup doesn't wait on a download.
    A session waits for `ready` and a failure refuses it: the voice never falls back to hosted."""

    def __init__(self, cfg: VoiceConfig) -> None:
        self._cfg = cfg
        self.stt = "loading"
        self.tts = "loading"
        self.whisper: Any = None
        self.kokoro_paths: tuple[Path, Path] | None = None

    def start_loading(self) -> None:
        threading.Thread(target=self.load, name="voice-model-load", daemon=True).start()

    def load(self) -> None:
        cfg = self._cfg
        os.environ.setdefault("HF_HUB_DISABLE_TELEMETRY", "1")
        try:
            from faster_whisper import WhisperModel

            self.whisper = WhisperModel(
                cfg.whisper_model,
                device="cpu",
                compute_type=cfg.whisper_compute_type,
                download_root=str(cfg.cache_dir / "whisper"),
            )
            self.stt = "ready"
        except Exception as e:
            self.stt = "failed"
            log.error("voice.models.stt_failed", error=type(e).__name__)
        try:
            self.kokoro_paths = ensure_kokoro(cfg.cache_dir)
            warm_phonemizer()
            self.tts = "ready"
        except Exception as e:
            self.tts = "failed"
            log.error("voice.models.tts_failed", error=type(e).__name__)


def warm_phonemizer() -> None:
    """Loads espeak, about a second, for the calling thread: phonemizer's cache is per thread."""
    Tokenizer().phonemize("Ready.", "en-us")


class LocalWhisperSTT(SegmentedSTTService):
    """faster-whisper in process. Pipecat's own Whisper service won't import on Apple Silicon
    without `mlx_whisper`, which is an install we don't need for the small models."""

    def __init__(self, model: Any, **kwargs: Any) -> None:
        settings = STTSettings(model="local", language=Language.EN)
        super().__init__(settings=settings, ttfs_p99_latency=STT_WAIT_S, **kwargs)
        self._model = model

    @property
    def wants_wav_segments(self) -> bool:
        return False

    def _transcribe(self, audio: np.ndarray) -> str:
        segments, _info = self._model.transcribe(audio, language="en", beam_size=1)
        return " ".join(
            s.text.strip() for s in segments if s.no_speech_prob < NO_SPEECH_THRESHOLD
        ).strip()

    async def run_stt(self, audio: bytes) -> AsyncGenerator[Frame | None, None]:
        samples = np.frombuffer(audio, dtype=np.int16).astype(np.float32) / 32768.0
        text = await asyncio.to_thread(self._transcribe, samples)
        if text:
            yield TranscriptionFrame(text, self._user_id, time_now_iso8601(), Language.EN)


def build_stt(plan: SessionPlan, models: LocalModels) -> FrameProcessor:
    if plan.local_only and plan.stt != LOCAL_PROVIDER:
        raise Refusal(500, "This session must stay local, and its plan says otherwise.")
    if plan.stt == HOSTED_PROVIDER:
        from pipecat.services.openai.stt import OpenAISTTService

        return OpenAISTTService(api_key=os.environ["OPENAI_API_KEY"])
    if models.stt != "ready" or models.whisper is None:
        raise Refusal(503, "Local speech recognition is not available, so voice is refused here.")
    return LocalWhisperSTT(models.whisper)


def build_tts(plan: SessionPlan, models: LocalModels, cfg: VoiceConfig) -> FrameProcessor:
    if plan.local_only and plan.tts != LOCAL_PROVIDER:
        raise Refusal(500, "This session must stay local, and its plan says otherwise.")
    if plan.tts == HOSTED_PROVIDER:
        from pipecat.services.openai.tts import OpenAITTSService

        return OpenAITTSService(api_key=os.environ["OPENAI_API_KEY"])
    if models.tts != "ready" or models.kokoro_paths is None:
        raise Refusal(503, "The local voice is not available, so voice is refused here.")
    model_path, voices_path = models.kokoro_paths
    return KokoroTTSService(
        settings=KokoroTTSService.Settings(voice=cfg.kokoro_voice),
        model_path=str(model_path),
        voices_path=str(voices_path),
    )


INTERRUPT_MESSAGE = "interrupt"
SPEECH_LOST = "Speech stopped working on this machine, so the session ended."


class ClaudeTurnProcessor(FrameProcessor):
    """Runs each closed user turn through the conversation, in a task of its own, so an interruption
    can cancel the model call while audio keeps flowing."""

    def __init__(self, conversation: Conversation, tracker: LatencyTracker, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._conversation = conversation
        self._tracker = tracker
        self._turn: asyncio.Task[None] | None = None

    async def _notify(self, data: dict[str, Any]) -> None:
        await self.push_frame(RTVIServerMessageFrame(data=data))

    async def _run_turn(self, text: str) -> None:
        first = True
        self._tracker.llm_request(time.monotonic())
        async with aclosing(self._conversation.respond(text)) as events:
            async for event in events:
                if isinstance(event, Say):
                    if first:
                        first = False
                        self._tracker.llm_first(time.monotonic())
                    await self.push_frame(TTSSpeakFrame(event.text))
                elif isinstance(event, Graded):
                    await self._notify({"type": "grade", "score": event.score})
                elif isinstance(event, Ungraded):
                    await self._notify({"type": "ungraded", "reason": event.reason})
                elif isinstance(event, Finished):
                    await self._notify({"type": "ended", "reason": event.reason})
                    await self.push_frame(EndWorkerFrame(), FrameDirection.UPSTREAM)

    async def _cancel_turn(self) -> bool:
        turn, self._turn = self._turn, None
        if turn is None or turn.done():
            return False
        await self.cancel_task(turn)
        return True

    async def process_frame(self, frame: Frame, direction: FrameDirection) -> None:
        await super().process_frame(frame, direction)
        if isinstance(frame, LLMContextFrame):
            if getattr(frame, "speculation", False):
                return
            parts: list[str] = []
            for m in frame.context.messages:
                msg: dict[str, Any] = cast("dict[str, Any]", m)
                if msg.get("role") == "user" and isinstance(msg.get("content"), str):
                    parts.append(msg["content"])
            frame.context.set_messages([])  # The conversation keeps its own history.
            if text := " ".join(parts).strip():
                if await self._cancel_turn():
                    await self._notify({"type": "ungraded", "reason": "interrupted"})
                self._turn = self.create_task(self._run_turn(text), name="voice_turn")
            return
        if isinstance(frame, RTVIClientMessageFrame):
            if frame.type == INTERRUPT_MESSAGE:  # The drawer's button, for a noisy room.
                if await self._cancel_turn():
                    await self._notify({"type": "ungraded", "reason": "interrupted"})
                await self.broadcast_interruption()
            return
        if isinstance(frame, InterruptionFrame):
            if await self._cancel_turn():
                await self._notify({"type": "ungraded", "reason": "interrupted"})
        elif isinstance(frame, CancelFrame | EndFrame):
            await self._cancel_turn()
        await self.push_frame(frame, direction)


class StageObserver(BaseObserver):
    """Reads frame types and clocks, never their text, and turns them into timings and activity."""

    def __init__(self, tracker: LatencyTracker, limits: SessionLimits, notify: Notify) -> None:
        super().__init__(observe_every_push=False)
        self._tracker = tracker
        self._limits = limits
        self._notify = notify

    async def on_push_frame(self, data: FramePushed) -> None:
        frame = data.frame
        now = time.monotonic()
        tracker = self._tracker
        if isinstance(frame, VADUserStartedSpeakingFrame):
            tracker.user_started()
            self._limits.touch(now)
        elif isinstance(frame, VADUserStoppedSpeakingFrame):
            tracker.user_stopped(now)
            self._limits.touch(now)
        elif isinstance(frame, TranscriptionFrame):
            tracker.transcript(now)
            self._limits.touch(now)
        elif isinstance(frame, UserStoppedSpeakingFrame):
            tracker.turn_closed(now)
        elif isinstance(frame, UserStartedSpeakingFrame | BotStoppedSpeakingFrame):
            self._limits.touch(now)
        elif isinstance(frame, TTSAudioRawFrame):
            tracker.tts_first(now)
        elif isinstance(frame, BotStartedSpeakingFrame):
            self._limits.touch(now)
            if (report := tracker.bot_started(now)) is not None:
                log.info("voice.turn.latency", **report)
                await self._notify({"type": "latency", **report})


@dataclass
class Assembly:
    """The parts of a session without a transport, so a test can feed in a file instead."""

    task: PipelineWorker
    conversation: Conversation
    limits: SessionLimits
    tracker: LatencyTracker


def assemble(
    plan: SessionPlan,
    cfg: VoiceConfig,
    models: LocalModels,
    client: anthropic.AsyncAnthropic,
    audio_in: FrameProcessor,
    audio_out: FrameProcessor,
) -> Assembly:
    """Refuses, by way of `build_stt` and `build_tts`, before anything has been connected."""
    limits = SessionLimits(
        started=time.monotonic(),
        idle_timeout_s=cfg.idle_timeout_s,
        max_duration_s=cfg.max_duration_s,
        max_turns=cfg.max_turns,
        max_tokens=cfg.max_session_tokens,
    )
    tracker = LatencyTracker(vad_stop_ms=VAD_STOP_SECS * 1000)
    conversation = Conversation(plan, client, cfg, limits, grade_writer(plan.user_id))
    stt = build_stt(plan, models)
    tts = build_tts(plan, models, cfg)
    user_turns = LLMUserAggregator(
        LLMContext(),
        params=LLMUserAggregatorParams(
            vad_analyzer=SileroVADAnalyzer(params=VADParams(stop_secs=VAD_STOP_SECS)),
            # A silent turn isn't a question, and it must not make a billed call.
            empty_user_turn=None,
        ),
    )
    turns = ClaudeTurnProcessor(conversation, tracker)
    pipeline = Pipeline([audio_in, stt, user_turns, turns, tts, audio_out])

    holder: list[PipelineWorker] = []

    async def notify(data: dict[str, Any]) -> None:
        await holder[0].queue_frame(RTVIServerMessageFrame(data=data))

    task = PipelineWorker(
        pipeline,
        params=PipelineParams(
            audio_in_sample_rate=IN_SAMPLE_RATE, audio_out_sample_rate=OUT_SAMPLE_RATE
        ),
        observers=[StageObserver(tracker, limits, notify)],
        # The watchdog below owns idle: Pipecat's would count spoken output as activity forever.
        idle_timeout_secs=None,
        # Pipecat's default carries on, and a coach nobody can hear would still bill each turn.
        processor_unusable_policy=ProcessorUnusablePolicy.END,
        enable_rtvi=True,
        rtvi_observer_params=RTVIObserverParams(
            system_logs_enabled=False, metrics_enabled=False, user_llm_enabled=False
        ),
    )
    holder.append(task)

    async def speech_lost(_processor: FrameProcessor, is_usable: bool) -> None:
        if not is_usable:
            log.error("voice.session.speech_lost")
            await notify({"type": "ended", "reason": "speech_lost", "message": SPEECH_LOST})

    stt.add_event_handler("on_usable_changed", speech_lost)
    tts.add_event_handler("on_usable_changed", speech_lost)
    return Assembly(task, conversation, limits, tracker)


async def _watchdog(assembly: Assembly) -> None:
    while True:
        await asyncio.sleep(WATCHDOG_INTERVAL_S)
        reason = assembly.limits.expired(time.monotonic())
        if reason is not None:
            log.info("voice.session.limit", reason=reason)
            await assembly.task.queue_frame(
                RTVIServerMessageFrame(
                    data={"type": "ended", "reason": reason, "message": END_MESSAGES[reason]}
                )
            )
            await assembly.task.cancel()
            return


class PipecatSession:
    """One browser connection. Built before the answer goes back, so a refusal is still possible."""

    def __init__(
        self,
        plan: SessionPlan,
        cfg: VoiceConfig,
        models: LocalModels,
        client: anthropic.AsyncAnthropic,
        on_end: Callable[[], None],
    ) -> None:
        self._plan = plan
        self._cfg = cfg
        self._models = models
        self._client = client
        self._on_end = on_end
        self._handler = SmallWebRTCRequestHandler(connection_mode=ConnectionMode.SINGLE)
        self._run: asyncio.Task[None] | None = None
        self._assembly: Assembly | None = None

    async def _on_connection(self, connection: Any) -> None:
        transport = SmallWebRTCTransport(
            webrtc_connection=connection,
            params=TransportParams(audio_in_enabled=True, audio_out_enabled=True),
        )
        assembly = await asyncio.to_thread(
            assemble,
            self._plan,
            self._cfg,
            self._models,
            self._client,
            transport.input(),
            transport.output(),
        )
        self._assembly = assembly

        @transport.event_handler("on_client_connected")
        async def _connected(_transport: Any, _client: Any) -> None:
            await assembly.task.queue_frame(TTSSpeakFrame(assembly.conversation.opening()))

        @transport.event_handler("on_client_disconnected")
        async def _disconnected(_transport: Any, _client: Any) -> None:
            await assembly.task.cancel()

        self._run = asyncio.create_task(self._drive(assembly, connection))

    async def _drive(self, assembly: Assembly, connection: Any) -> None:
        watchdog = asyncio.create_task(_watchdog(assembly))
        try:
            runner = WorkerRunner(handle_sigint=False, handle_sigterm=False)
            await runner.add_workers(assembly.task)
            await runner.run()
        finally:
            watchdog.cancel()
            await connection.disconnect()
            self._on_end()

    async def offer(self, body: dict[str, Any]) -> dict[str, Any]:
        if self._plan.tts == LOCAL_PROVIDER:
            # Kokoro phonemizes on the event loop, so its stall lands here, before any audio flows,
            # rather than on the first sentence the coach speaks.
            warm_phonemizer()
        request = SmallWebRTCRequest(
            sdp=str(body.get("sdp", "")),
            type=str(body.get("type", "")),
            pc_id=body.get("pc_id"),
            restart_pc=body.get("restart_pc"),
        )
        answer = await self._handler.handle_web_request(request, self._on_connection)
        if answer is None:
            raise Refusal(503, "The voice connection could not be set up.")
        if self._assembly is None:
            raise Refusal(503, "Voice could not start, as the speech models did not load.")
        return dict(answer)

    async def ice(self, body: dict[str, Any]) -> None:
        candidates = [
            IceCandidate(
                candidate=str(c.get("candidate", "")),
                sdp_mid=c.get("sdp_mid"),
                sdp_mline_index=c.get("sdp_mline_index"),
            )
            for c in body.get("candidates", [])
        ]
        await self._handler.handle_patch_request(
            SmallWebRTCPatchRequest(pc_id=str(body.get("pc_id", "")), candidates=candidates)
        )

    async def close(self) -> None:
        if self._assembly is not None:
            await self._assembly.task.cancel()
        if self._run is not None:
            await asyncio.gather(self._run, return_exceptions=True)
        await self._handler.close()
