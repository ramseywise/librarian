import re

INJECTION_PATTERNS = [
    # ── 1. Direct instruction overrides ────────────────────────────────────────
    # Bounded .{0,60} prevents the greedy DOTALL wildcard spanning the full text.
    r"(ignore|disregard|forget|overwrite|bypass|circumvent|skip)"
    r".{0,60}(previous|prior|initial|system|all)\s*(instructions?|directives?|rules?|prompts?)?",
    # "new instructions:" / "updated instructions:" prefix attack
    r"\b(new|updated|revised|changed)\s+instructions?\s*[:\-]",
    # "from now on …" override
    r"\bfrom\s+now\s+on\b",
    # ── 2. Prompt / system-message extraction ──────────────────────────────────
    r"(reveal|show|print|output|display|repeat|summarize|leak|dump)"
    r".{0,60}(prompt|instructions?|directives?|system\s*message|context|guidelines?)",
    r"\brepeat\s+(after\s+me|the\s+above|your\s+(prompt|instructions?|rules?))\b",
    r"\btranslate\s+(the\s+above|your\s+(prompt|instructions?|system\s*message))\b",
    r"\bwhat\s+(are\s+)?your\s+(instructions?|rules?|directives?|guidelines?|prompt)\b",
    # ── 3. Goal / task / role hijacking ────────────────────────────────────────
    # 'act' omitted — too broad for a wine agent ("act as my sommelier" is legitimate).
    r"\b(operate|behave|roleplay|pretend|simulate|masquerade)\s+as\b",
    r"\byou\s+are\s+(now|currently|henceforth|actually)\b",
    r"\b(identity|personality|persona)\s+is\b",
    r"\byour\s+(real|true|actual|new|updated)\s+(goal|task|objective|purpose|mission|instructions?)\b",
    r"\b(your\s+)?(new\s+)?(goal|task|objective|purpose)\s+is\s+(now|to)\b",
    r"\bstop\s+(being|acting\s+as|playing|pretending)\b",
    # ── 4. Jailbreak lexicon ────────────────────────────────────────────────────
    # Removed 'raw' and 'binary' — both appear in legitimate wine/general language.
    r"\b(jailbreak|gpt-?4chan|unfiltered|unrestricted|uncensored|do-anything-now)\b",
    r"\bdan\s+mode\b",
    r"\b(developer|sudo|god|admin|super|privileged)\s+mode\b",
    r"\bdo\s+anything\s+now\b",
    r"\bno\s+restrictions\b",
    r"without\s+(any\s+)?(restrictions?|filters?|guidelines?|rules?|safety|censorship)",
    # Optional interstitial word: "remove your safety guidelines", "remove all content filters"
    r"remove\s+(your\s+)?(\w+\s+)?(restrictions?|filters?|guidelines?|rules?|limitations?|constraints?)",
    # ── 5. Sensitive internals extraction ─────────────────────────────────────
    # a) Verb + hidden/secret/internal + sensitive noun
    #    Catches: "show hidden rules", "reveal internal config", "dump secret prompt"
    r"\b(show|reveal|print|output|display|dump|leak|share)\s+"
    r"(the\s+)?(hidden|secret|internal|private|real)\s+"
    r"(rules?|instructions?|config(?:uration)?|settings?|prompt|directives?|context)\b",
    # b) "what is (in) the system prompt / hidden rules" — uses 'what is' not action verbs
    r"\bwhat\s+(is|are)\s+(in\s+)?(the\s+)?"
    r"(system\s+(prompt|message|instructions?)|hidden\s+rules?|your\s+secrets?|real\s+instructions?)\b",
    # c) Chain-of-thought / internal reasoning extraction
    #    Catches: "print your chain-of-thought", "reveal your reasoning process"
    # Optional interstitial word handles "show me your reasoning", "show us your thinking"
    r"\b(print|show|reveal|output|display|dump|share)\s+(\w+\s+)?(your\s+)?"
    r"(chain[\s\-]of[\s\-]thought|reasoning|thought\s+process|internal\s+monologue|thinking)\b",
    # ── 6 (new). Secrets / credentials / environment probing ───────────────────
    # These terms have no plausible legitimate use in a wine-assistant conversation.
    # Catches: "reveal your API key", "show environment variables", "what secrets do you have"
    r"\b(api[_\s\-]?key|secret[_\s\-]?key|access[_\s\-]?token|auth[_\s\-]?token)\b",
    r"\b(internal|system|app)\s+config(?:uration)?\b",
    r"\benvironment\s+variables?\b",
    r"\b\.env\b",
    r"\bwhat\s+secrets?\s+(do\s+you|have\s+you|are\s+you\s+keeping)\b",
    # ── 7 (new). Tool / agent hijacking ────────────────────────────────────────
    # Catches attempts to force tool calls or re-route to privileged agents.
    # a) "call / invoke X no matter what" — unconditional tool-call coercion
    r"\b(call|invoke|trigger|run|execute|use)\s+\w[\w\s]{0,30}"
    r"(no\s+matter\s+what|regardless|unconditionally|at\s+all\s+costs)\b",
    # b) "always call/invoke the tool/agent/function" — persistent override
    r"\balways\s+(call|invoke|use|run|execute)\s+(the\s+)?(tool|agent|function|expert)\b",
    # c) "send / forward / route to admin/root/system agent"
    r"\b(send|forward|route|escalate|redirect)\s+.{0,40}"
    r"(to\s+)?(the\s+)?(admin|root|system|master|super)\s*(agent|user|level|handler)?\b",
    # d) "force / make the agent/model to call X"
    r"\b(force|make|compel|require)\s+(the\s+)?(agent|system|model|ai|bot)\s+to\s+"
    r"(call|invoke|use|run|execute)\b",
    # ── 8. Encoding / obfuscation ──────────────────────────────────────────────
    # 'hex' and 'binary' dropped — too common in unrelated text.
    r"\b(base64|rot13|caesar\s+cipher|ascii\s+code)\b",
    r"\b(encode|decode)\s+(this|the\s+(following|above|message|text))\b",
    # ── 9. LLM template / control tokens ──────────────────────────────────────
    # These are direct injections targeting specific model prompt formats.
    r"<\|?\s*(system|im_start|im_end|endoftext|user|assistant|stop|end)\s*\|?>",
    r"\[\s*(INST|SYSTEM)\s*\]",
    r"<<\s*SYS\s*>>",
    # ── 10. Structural delimiters ──────────────────────────────────────────────
    # Anchored to a full standalone line to avoid firing on normal prose.
    # (Evaluated with re.MULTILINE; ^ / $ match line boundaries.)
    r"^\s*---+\s*$",  # YAML front-matter or markdown HR on its own line
    r"^\s*#{3,}\s*$",  # bare ### / #### with nothing after
    r"^\s*#{1,6}\s*(system|override|instruction|directive|admin|root)\b",
    # ── 11 (new). Advisory & Input Control Tags ────────────────────────────────
    # Catches opening/closing tags and handles optional attributes like priority.
    # Matches: <USER_INPUT_BLOCK>, </SCOPE_ADVISORY>, <SECURITY_ADVISORY priority='high'>
    r"</?\s*(USER_INPUT_BLOCK|DATA_PRIVACY_NOTICE|SCOPE_ADVISORY)\s*>",
    r"</?\s*(INPUT_CONSTRAINT|SECURITY_ADVISORY)(\s+[^>]+)?\s*>",
]

# Pre-compile into one single efficient regex object.
# re.IGNORECASE : no need to .lower() the input manually.
# re.DOTALL     : '.' matches newlines (multi-line injection payloads).
# re.MULTILINE  : ^ / $ anchors match individual line boundaries (needed for
#                 the structural-delimiter group above).
INJECTION_RE = re.compile(
    "|".join(INJECTION_PATTERNS),
    re.IGNORECASE | re.DOTALL | re.MULTILINE,
)


def looks_like_injection(text: str) -> bool:
    if not text:
        return False
    return bool(INJECTION_RE.search(text))
