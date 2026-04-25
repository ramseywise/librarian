"""Support knowledge base tool for the Billy accounting system."""

# ---------------------------------------------------------------------------
# Mock knowledge base passages
# ---------------------------------------------------------------------------

_MOCK_KB: list[dict] = [
    {
        "url": "https://help.billy.dk/da/articles/create-invoice",
        "title": "Sådan opretter du en faktura",
        "score": 0.92,
        "text": (
            "For at oprette en ny faktura i Billy skal du gå til Fakturaer og klikke på 'Ny faktura'. "
            "Vælg en kunde, tilføj mindst én fakturalinje med produkt, antal og enhedspris, og vælg "
            "fakturadato samt betalingsbetingelser. Klik 'Godkend' for at godkende fakturaen med det "
            "samme, eller gem den som kladde. Fakturaen kan sendes direkte via e-mail fra Billy."
        ),
    },
    {
        "url": "https://help.billy.dk/da/articles/send-invoice-email",
        "title": "Send faktura via e-mail",
        "score": 0.88,
        "text": (
            "Du kan sende en godkendt faktura direkte til din kunde fra Billy. Åbn fakturaen og klik "
            "på 'Send via e-mail'. Udfyld emnelinjen og e-mailens brødtekst. Fakturaen sendes til "
            "kundens primære kontaktpersons e-mailadresse. Systemet registrerer automatisk, at "
            "fakturaen er afsendt."
        ),
    },
    {
        "url": "https://help.billy.dk/da/articles/payment-terms",
        "title": "Betalingsbetingelser",
        "score": 0.85,
        "text": (
            "Billy understøtter netto-betalingsbetingelser. Du kan angive antal dage, fx netto 7 "
            "eller netto 30. Forfaldsdatoen beregnes automatisk ud fra fakturadatoen plus "
            "betalingsfristens antal dage. Du kan ændre betalingsbetingelserne på en kladde-faktura "
            "men ikke på en godkendt faktura."
        ),
    },
    {
        "url": "https://help.billy.dk/da/articles/create-customer",
        "title": "Opret ny kunde",
        "score": 0.83,
        "text": (
            "Gå til Kontakter og klik 'Ny kontakt'. Udfyld minimum firmanavn. Du kan også tilføje "
            "adresse, CVR-nummer, telefon og e-mailadresse. CVR-nummeret bruges til EAN-fakturering "
            "og til automatisk opslag af firmaoplysninger. E-mailadressen gemmes på kontaktpersonen "
            "og bruges ved afsendelse af fakturaer."
        ),
    },
    {
        "url": "https://help.billy.dk/da/articles/products",
        "title": "Produkter og ydelser",
        "score": 0.80,
        "text": (
            "Produkter i Billy er de varer eller ydelser du sælger. Hvert produkt har et navn, "
            "en enhedspris og en salgskonto. Produkter bruges som fakturalinje-skabeloner – når du "
            "vælger et produkt på en faktura, udfyldes beskrivelse og pris automatisk. Du kan "
            "redigere prisen direkte på fakturalinjen."
        ),
    },
    {
        "url": "https://help.billy.dk/da/articles/moms",
        "title": "Moms og momssatser",
        "score": 0.78,
        "text": (
            "Billy beregner moms automatisk baseret på den valgte momssats. Standardmomssatsen i "
            "Danmark er 25 %. Du kan vælge om priser på fakturaen er inkl. eller ekskl. moms "
            "via indstillingen 'Momstilstand'. Momsbeløbet vises separat på fakturaen og i "
            "momsrapporten."
        ),
    },
    {
        "url": "https://help.billy.dk/da/articles/invite-collaborator",
        "title": "Inviter en medarbejder",
        "score": 0.75,
        "text": (
            "Du kan invitere andre brugere til din organisation som samarbejdspartnere. Gå til "
            "Indstillinger > Brugere og klik 'Inviter bruger'. Angiv e-mailadressen på den person "
            "du vil invitere. De modtager en e-mail med et link til at acceptere invitationen og "
            "oprette en adgangskode."
        ),
    },
]


def _search_passages(query: str) -> list[dict]:
    """Simple keyword-based mock search."""
    query_lower = query.lower()
    results = []
    for passage in _MOCK_KB:
        combined = (passage["title"] + " " + passage["text"]).lower()
        # Score boost if query words appear in passage
        words = query_lower.split()
        hits = sum(1 for w in words if w in combined)
        if hits > 0:
            results.append(
                {**passage, "score": min(0.99, passage["score"] + hits * 0.03)}
            )
    return results


def _format_passages(results: list[dict]) -> str:
    parts = []
    for i, r in enumerate(results):
        header = f"[PASSAGE {i + 1}] score={r['score']:.2f} | {r['title']}"
        if r.get("url"):
            header += f"\nURL: {r['url']}"
        parts.append(f"{header}\n{r['text']}")
    return "\n---\n".join(parts)


# ---------------------------------------------------------------------------
# Tool
# ---------------------------------------------------------------------------


def fetch_support_knowledge(queries: list) -> str:
    """Search the official Billy support documentation.

    Args:
        queries: A list of 2-3 search terms or phrases (Danish).
                 Example: ['opret faktura', 'ny regning']

    Returns:
        Formatted string of relevant documentation passages, or a message
        indicating no relevant documentation was found.
    """
    all_results: list[dict] = []
    seen: set[str] = set()

    for query in queries:
        for passage in _search_passages(query):
            url = passage.get("url", "no-url")
            if url not in seen:
                seen.add(url)
                all_results.append(passage)

    if not all_results:
        return "No relevant documentation found."

    all_results.sort(key=lambda r: r["score"], reverse=True)
    return _format_passages(all_results[:5])
