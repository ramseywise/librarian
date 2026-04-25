"""
PII / secrets detection and redaction.

Design goals
------------
- Pure function: no I/O, no network, no side effects.
- Single-pass: compile all patterns once at import time.
- Tuple return so callers know *whether* any PII was found.
"""

import re
from typing import List, Tuple

# ---------------------------------------------------------------------------
# Pattern registry
# Each entry: (compiled_regex, replacement_token)
#
# Ordering matters: more specific patterns (PEM blocks, prefixed keys) come
# before generic ones (long hex, JWT) to avoid partial matches leaving
# fragments for downstream patterns.
# ---------------------------------------------------------------------------
_RAW_PATTERNS: List[Tuple[str, str]] = [
    # ── E-mail ────────────────────────────────────────────────────────────────
    (r"\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b", "[EMAIL]"),
    # ── Phone numbers ─────────────────────────────────────────────────────────
    # Fix: original \b before '(' is a non-word char so \b never anchors there,
    # leaving a dangling '(' in the output.  Use (?<!\d) lookbehind + explicit
    # (NNN) vs NNN alternation so the opening paren is consumed.
    # US / Canada:  (555) 123-4567 | 555-123-4567 | +1 555.123.4567
    (
        r"(?<!\d)(?:\+?1[\s.\-]?)?(?:\(\d{3}\)|\d{3})[\s.\-]?\d{3}[\s.\-]?\d{4}(?!\d)",
        "[PHONE]",
    ),
    # International E.164-style: +44 20 7946 0958, +33 1 23 45 67 89
    # Requires a + country-code prefix so it doesn't swallow arbitrary numbers.
    (r"\+\d{1,3}[\s.\-]?\d{1,5}(?:[\s.\-]\d{2,6}){1,5}(?!\d)", "[PHONE]"),
    # ── Credit / debit card  (16-digit groups, optional space/dash) ───────────
    # (?<!\d) / (?!\d) prevent partial matches inside longer digit strings.
    (r"(?<!\d)(?:\d{4}[\s\-]?){3}\d{4}(?!\d)", "[CARD]"),
    # ── US Social Security Number ─────────────────────────────────────────────
    # NNN-NN-NNNN.  Known trade-off: also fires on order numbers of the same
    # shape ("Order 123-45-6789").  PII redaction is intentionally conservative.
    (r"\b\d{3}-\d{2}-\d{4}\b", "[SSN]"),
    # ── PEM private / public key blocks ───────────────────────────────────────
    # Must come before the long-hex and JWT patterns to consume the whole block.
    (
        r"-----BEGIN\s+(?:(?:RSA|EC|DSA|OPENSSH|ENCRYPTED)\s+)?"
        r"(?:PRIVATE|PUBLIC)\s+KEY-----[\s\S]*?"
        r"-----END\s+\S[^\n]*?KEY-----",
        "[PEM_KEY]",
    ),
    # X.509 certificate blocks
    (
        r"-----BEGIN\s+CERTIFICATE-----[\s\S]*?-----END\s+CERTIFICATE-----",
        "[CERT]",
    ),
    # ── Prefixed service / platform API keys ──────────────────────────────────
    # Stripe  (sk_live_…, pk_live_…, sk_test_…, pk_test_…)
    (r"\b(?:sk|pk)_(?:live|test)_[A-Za-z0-9]{20,}\b", "[SECRET]"),
    # GitHub  (ghp_, ghs_, gho_, ghc_, ghr_)
    (r"\bgh[poscrhi]_[A-Za-z0-9]{36,}\b", "[SECRET]"),
    # Slack  (xoxb-, xoxp-, xoxa-, xoxs-, xoxr-)
    (r"\bxox[bpars]-\d+-\d+-?[A-Za-z0-9]+\b", "[SECRET]"),
    # SendGrid  (SG.<key_id>.<secret>)
    (r"\bSG\.[A-Za-z0-9.\-_]{20,}\b", "[SECRET]"),
    # AWS IAM access key ID  (always AKIA + 16 uppercase alphanumerics)
    (r"\bAKIA[A-Z0-9]{16}\b", "[SECRET]"),
    # ── Authorization / Bearer header tokens ──────────────────────────────────
    # "Authorization: Bearer <token>" or bare "Bearer <token>"
    (r"\bBearer\s+[A-Za-z0-9\-._~+/]+=*", "[SECRET]"),
    # ── API keys / credentials in key=value or key: value form ───────────────
    # Fixes: (1) removed redundant (?i) — file compiled with IGNORECASE already;
    #        (2) replaced \S+ with [^\s,;'")\]]+ so trailing punctuation isn't
    #            consumed into the token.
    (
        r"(?:api[_\-]?key|token|secret|password|passwd|pwd|auth)"
        r"\s*[=:]\s*[^\s,;'\")\]]+",
        "[SECRET]",
    ),
    # ── IPv4 addresses ────────────────────────────────────────────────────────
    # Lookbehind (?<![./\w]) + lookahead (?![./\d]) prevent firing inside
    # URLs (/192.168.1.1), semver (requires that NO dot or digit directly
    # abuts the match).  Trade-off: "version 1.2.3.4" still fires if it
    # stands alone preceded only by a space — acceptable for a PII guardrail
    # where over-redaction is preferable to under-redaction.
    (r"(?<![./\w])(?:\d{1,3}\.){3}\d{1,3}(?![./\d])", "[IP]"),
    # ── Long hex strings (≥ 32 chars) — hashes, raw secret keys ──────────────
    (r"\b[0-9a-fA-F]{32,}\b", "[HEX_SECRET]"),
    # ── JWTs  (header.payload.signature, each segment ≥ 10 base64url chars) ──
    # Negative lookahead/lookbehind on [.\w] prevents matching 3-part domain
    # names where each label happens to be long alphanumeric.
    (
        r"(?<![.\w])[A-Za-z0-9\-_]{10,}\.[A-Za-z0-9\-_]{10,}\.[A-Za-z0-9\-_]{10,}(?![.\w])",
        "[JWT]",
    ),
]

PII_RE: List[Tuple[re.Pattern, str]] = [
    (re.compile(pattern, re.IGNORECASE), replacement)
    for pattern, replacement in _RAW_PATTERNS
]


def detect_and_redact(text: str) -> Tuple[str, bool]:
    """
    Scan *text* for PII / secrets; replace matches with safe placeholder tokens.

    Returns
    -------
    redacted_text : str
        Copy of *text* with PII replaced by ``[TOKEN]`` placeholders.
    pii_found : bool
        ``True`` when at least one pattern matched.
    """
    pii_found = False
    for pattern, replacement in PII_RE:
        text, n = pattern.subn(replacement, text)
        if n:
            pii_found = True
    return text, pii_found
