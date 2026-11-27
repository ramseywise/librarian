"""Settings for the voice process, from the environment. The defaults are all local and free."""

from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path

# Not configurable: this process serves one person on this machine (D9).
HOST = "127.0.0.1"
DEFAULT_ORIGINS = "http://localhost:5173,http://127.0.0.1:5173"
ALLOWED_HOSTS = frozenset({"localhost", "127.0.0.1"})


def _chat_model() -> str:
    from librarian.config import get_settings

    return get_settings().chat_model


def _number(env: Mapping[str, str], key: str, default: float) -> float:
    raw = env.get(key, "").strip()
    if not raw:
        return default
    try:
        value = float(raw)
    except ValueError as e:
        raise ValueError(f"{key} must be a number") from e
    if value <= 0:
        raise ValueError(f"{key} must be above zero")
    return value


def allowed_origins(env: Mapping[str, str] = os.environ) -> frozenset[str]:
    raw = env.get("VOICE_ALLOWED_ORIGINS", "") or DEFAULT_ORIGINS
    return frozenset(o.strip().rstrip("/") for o in raw.split(",") if o.strip())


@dataclass(frozen=True)
class VoiceConfig:
    port: int = 8200
    # Follows the chat agent's model (`librarian.agent.loop.default_model`). A faster model may
    # suit voice; that is a setting (VOICE_MODEL).
    model: str = ""
    # Covers thinking as well as speech on models that always think, so not as small as the
    # reply alone would need. A reply cut off here is spoken as far as it got and left ungraded.
    max_tokens: int = 1200
    effort: str = "low"  # empty sends no effort setting, for a model that doesn't take one
    llm_timeout_s: float = 30.0
    idle_timeout_s: float = 300.0
    max_duration_s: float = 1800.0
    max_turns: int = 60
    max_session_tokens: int = 60_000
    offer_timeout_s: float = 30.0
    whisper_model: str = "tiny.en"
    whisper_compute_type: str = "int8"
    kokoro_voice: str = "af_heart"
    cache_dir: Path = Path.home() / ".cache" / "librarian-voice"
    stt_provider: str = "local"
    tts_provider: str = "local"
    allowed_origins: frozenset[str] = field(
        default_factory=lambda: frozenset(DEFAULT_ORIGINS.split(","))
    )
    hosted_key_set: bool = False


def load_config(env: Mapping[str, str] = os.environ) -> VoiceConfig:
    d = VoiceConfig()
    return VoiceConfig(
        port=int(_number(env, "VOICE_PORT", d.port)),
        model=env.get("VOICE_MODEL") or _chat_model(),
        max_tokens=int(_number(env, "VOICE_MAX_TOKENS", d.max_tokens)),
        effort=env.get("VOICE_EFFORT", d.effort).strip(),
        llm_timeout_s=_number(env, "VOICE_LLM_TIMEOUT_S", d.llm_timeout_s),
        idle_timeout_s=_number(env, "VOICE_IDLE_TIMEOUT_S", d.idle_timeout_s),
        max_duration_s=_number(env, "VOICE_MAX_DURATION_S", d.max_duration_s),
        max_turns=int(_number(env, "VOICE_MAX_TURNS", d.max_turns)),
        max_session_tokens=int(_number(env, "VOICE_MAX_SESSION_TOKENS", d.max_session_tokens)),
        whisper_model=env.get("VOICE_WHISPER_MODEL") or d.whisper_model,
        whisper_compute_type=env.get("VOICE_WHISPER_COMPUTE_TYPE") or d.whisper_compute_type,
        kokoro_voice=env.get("VOICE_KOKORO_VOICE") or d.kokoro_voice,
        cache_dir=Path(env["VOICE_CACHE_DIR"]) if env.get("VOICE_CACHE_DIR") else d.cache_dir,
        stt_provider=(env.get("VOICE_STT_PROVIDER") or d.stt_provider).strip().lower(),
        tts_provider=(env.get("VOICE_TTS_PROVIDER") or d.tts_provider).strip().lower(),
        allowed_origins=allowed_origins(env),
        hosted_key_set=bool(env.get("OPENAI_API_KEY", "").strip()),
    )
