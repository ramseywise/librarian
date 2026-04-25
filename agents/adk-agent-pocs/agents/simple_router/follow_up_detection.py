# follow_up_detection.py
# Fast, LLM-free classifier that decides whether a user message is a direct
# answer to a clarifying question (follow-up) or the start of a new request.
#
# Usage:
#   from .follow_up_detection import is_follow_up_answer, NEW_REQUEST_STARTS

from __future__ import annotations

# First words that signal the user is making a NEW request, not answering a
# clarifying question. If the message starts with any of these the LLM should
# classify it rather than blindly routing to the follow-up agent.
# Covers: English, Danish, German, French.
NEW_REQUEST_STARTS: frozenset[str] = frozenset(
    {
        # ── English ───────────────────────────────────────────────────────────────
        # Question words
        "how",
        "what",
        "where",
        "when",
        "why",
        "who",
        "which",
        # Action verbs
        "show",
        "update",
        "get",
        "list",
        "find",
        "display",
        "validate",
        "give",
        "fetch",
        "check",
        "set",
        "change",
        "fix",
        # Modal / auxiliary openers
        "can",
        "could",
        "is",
        "are",
        "do",
        "does",
        "will",
        "would",
        # Generic
        "i",
        "help",
        # ── Danish ────────────────────────────────────────────────────────────────
        # Spørgsmålsord
        "hvordan",
        "hvad",
        "hvor",
        "hvornår",
        "hvorfor",
        "hvem",
        "hvilken",
        "hvilket",
        "hvilke",
        # Hjælpeverber / modalverber
        "kan",
        "kunne",
        "er",
        "vil",
        "ville",
        "gør",
        # Handlingsverber (bydeform)
        "vis",
        "opdater",
        "hent",
        "find",
        "valider",
        "giv",
        "tjek",
        "sæt",
        "skift",
        "ret",
        "få",
        "liste",
        # Generisk
        "jeg",
        "hjælp",
        # ── German ────────────────────────────────────────────────────────────────
        # Fragewörter
        "wie",
        "was",
        "wo",
        "wann",
        "warum",
        "wer",
        "welcher",
        "welche",
        "welches",
        "welchen",
        # Modalverben / Hilfsverben
        "kann",
        "könnte",
        "ist",
        "sind",
        "wird",
        "würde",
        "mach",
        "mache",
        # Imperativ-Handlungsverben
        "zeig",
        "zeige",
        "hol",
        "hole",
        "liste",
        "finde",
        "anzeige",
        "validiere",
        "gib",
        "abruf",
        "prüf",
        "prüfe",
        "setz",
        "setze",
        "ändere",
        "behebe",
        "aktualisiere",
        # Generisch
        "ich",
        "hilfe",
        "hilf",
        # ── French ────────────────────────────────────────────────────────────────
        # Mots interrogatifs
        "comment",
        "quoi",
        "où",
        "quand",
        "pourquoi",
        "qui",
        "quel",
        "quelle",
        "quels",
        "quelles",
        # Verbes modaux / auxiliaires
        "peut",
        "pourrait",
        "est",
        "sont",
        # Verbes d'action (impératif)
        "montre",
        "montrez",
        "mets",
        "mettez",
        "obtiens",
        "obtenez",
        "liste",
        "listez",
        "trouve",
        "trouvez",
        "affiche",
        "affichez",
        "valide",
        "validez",
        "donne",
        "donnez",
        "récupère",
        "récupérez",
        "vérifie",
        "vérifiez",
        "définis",
        "définissez",
        "change",
        "changez",
        "corrige",
        "corrigez",
        # Générique
        "je",
        "aide",
        "aidez",
    }
)

# Messages above this word count are unlikely to be bare follow-up answers.
MAX_FOLLOW_UP_WORDS: int = 5


def is_follow_up_answer(msg: str) -> bool:
    """Return True when the message looks like a direct answer to a clarifying question.

    Conservative: only returns True for short messages that don't start with a
    known new-request word. Anything question-shaped or command-shaped falls
    through to the LLM for proper classification.
    """
    if not msg:
        return False
    words = msg.lower().split()
    if words[0] in NEW_REQUEST_STARTS:
        return False
    return len(words) <= MAX_FOLLOW_UP_WORDS
