# oos_detection.py
# Out-of-scope keyword detection — extracted from callbacks.py so the OOS
# vocabulary and matching logic can be maintained and tested independently of
# the routing callback chain.
#
# Usage:
#   from .oos_detection import detect_out_of_scope, apply_out_of_scope_instruction

from __future__ import annotations

from google.adk.models import LlmRequest

# Topics this system does not cover, organised by language.
# Checked as substrings of the lowercased message.
# Extend a language group when new out-of-scope domains are identified.
OOS_BY_LANG: dict[str, frozenset[str]] = {
    "en": frozenset(
        {
            "expense",
            "expenses",
            "payslip",
            "payslips",
            "payroll",
            "salary",
            "salaries",
            "timesheet",
            "timesheets",
            "purchase order",
            "purchase orders",
            "contract",
            "contracts",
            "budget",
            "budgets",
            "receipt",
            "receipts",
            "reimbursement",
            "reimbursements",
        }
    ),
    # ── Danish ───────────────────────────────────────────────────────────────
    "da": frozenset(
        {
            "udgift",
            "udgifter",
            "lønseddel",
            "lønsedler",
            "lønudbetaling",
            "løn",
            "timeseddel",
            "timesedler",
            "indkøbsordre",
            "indkøbsordrer",
            "kontrakt",
            "kontrakter",
            "budget",
            "budgetter",
            "kvittering",
            "kvitteringer",
            "refusion",
            "godtgørelse",
        }
    ),
    # ── German ────────────────────────────────────────────────────────────────
    "de": frozenset(
        {
            "ausgabe",
            "ausgaben",
            "spesen",
            "gehaltsabrechnung",
            "lohnabrechnung",
            "gehalt",
            "lohn",
            "stundenzettel",
            "arbeitszeiterfassung",
            "bestellung",
            "bestellungen",
            "vertrag",
            "verträge",
            "quittung",
            "quittungen",
            "kassenbon",
            "erstattung",
            "kostenerstattung",
        }
    ),
    # ── French ────────────────────────────────────────────────────────────────
    "fr": frozenset(
        {
            "dépense",
            "dépenses",
            "note de frais",
            "fiche de paie",
            "bulletin de salaire",
            "salaire",
            "rémunération",
            "feuille de temps",
            "bon de commande",
            "contrat",
            "contrats",
            "reçu",
            "reçus",
            "remboursement",
            "remboursements",
        }
    ),
}

# Flat union — kept for any code that only needs a True/False membership check.
OUT_OF_SCOPE_KEYWORDS: frozenset[str] = frozenset(
    kw for kws in OOS_BY_LANG.values() for kw in kws
)

# System instruction injected when an out-of-scope keyword is detected.
# The LLM generates the actual response, matching the user's language naturally.
_OUT_OF_SCOPE_INSTRUCTION = (
    'The user\'s message mentions "{topic}", which is outside your scope. '
    "Respond with ONLY the following message (translate to the user's language if not English): "
    "\"I'm sorry, but I cannot assist with {topic} requests. "
    'I can only help with invoice management and product support."'
)


def detect_out_of_scope(msg: str) -> str | None:
    """Return the matched keyword if the message is out of scope, else None.

    Checks all supported languages; English is tried last so language-specific
    terms win when a keyword appears in multiple lists (e.g. "budget").
    """
    text = msg.lower()
    for lang in ("da", "de", "fr", "en"):
        for kw in OOS_BY_LANG[lang]:
            if kw in text:
                return kw
    return None


def apply_out_of_scope_instruction(matched: str, llm_request: LlmRequest) -> None:
    """Override the LlmRequest so the model generates a decline response.

    Replaces the system instruction with a focused decline prompt and clears
    tools so the LLM returns plain text without routing or tool calls.
    """
    instruction = _OUT_OF_SCOPE_INSTRUCTION.format(topic=matched)
    if llm_request.config is None:
        from google.genai import types as _gtypes

        llm_request.config = _gtypes.GenerateContentConfig(
            system_instruction=instruction,
        )
    else:
        llm_request.config.system_instruction = instruction
        llm_request.config.tools = None
        llm_request.config.tool_config = None
