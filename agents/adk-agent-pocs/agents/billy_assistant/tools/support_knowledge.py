import asyncio
import logging
import os
from typing import Any

import boto3

logger = logging.getLogger(__name__)

_KB_ID = os.getenv("BEDROCK_KNOWLEDGE_BASE_ID", "4SUAFKZBE8")
_AWS_REGION = os.getenv("AWS_REGION", "eu-north-1")
_AWS_PROFILE = os.getenv("AWS_PROFILE")

# Minimum relevance score — passages below this threshold are discarded as noise
_SCORE_THRESHOLD = 0.4
# Number of passages to retrieve; more coverage improves synthesis quality
_NUM_RESULTS = 5

# Initialize client outside the function for Lambda/Container reuse
aws_session = boto3.Session(profile_name=_AWS_PROFILE, region_name=_AWS_REGION)
bedrock_agent_runtime = aws_session.client("bedrock-agent-runtime")


def _extract_url(location: dict[str, Any]) -> str | None:
    """Extract the source URL from a retrievalResult location dict."""
    if "webLocation" in location:
        return location["webLocation"].get("url")
    if "s3Location" in location:
        return location["s3Location"].get("uri")
    if "confluenceLocation" in location:
        return location["confluenceLocation"].get("url")
    if "sharePointLocation" in location:
        return location["sharePointLocation"].get("url")
    if "salesforceLocation" in location:
        return location["salesforceLocation"].get("url")
    if "kendraDocumentLocation" in location:
        return location["kendraDocumentLocation"].get("uri")
    return None


def _format_passages(retrieval_results: list[dict[str, Any]]) -> str:
    """
    Convert raw Bedrock `retrieve` results into a structured string for Gemini.

    Each passage block contains its rank, relevance score, source URL, optional
    title, and the raw text excerpt. Passages below _SCORE_THRESHOLD are dropped.
    """
    parts: list[str] = []

    for i, result in enumerate(retrieval_results, start=1):
        score: float = result.get("score", 0.0)
        if score < _SCORE_THRESHOLD:
            continue

        text: str = result.get("content", {}).get("text", "").strip()
        if not text:
            continue

        location: dict = result.get("location", {})
        url: str | None = _extract_url(location)
        metadata: dict = result.get("metadata", {})
        title: str | None = (
            metadata.get("title") or metadata.get("x-amz-bedrock-kb-source-uri") or url
        )

        header = f"[PASSAGE {i}] score={score:.2f}"
        if title:
            header += f" | {title}"
        if url:
            header += f"\nURL: {url}"

        parts.append(f"{header}\n{text}")

    return "\n---\n".join(parts)


def _get_unique_results(results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Deduplicates results based on source URL and content fingerprint.
    Prioritizes higher scores.
    """
    # 1. Sort by score descending so we keep the most relevant version
    sorted_results = sorted(results, key=lambda x: x.get("score", 0.0), reverse=True)

    unique_results = []
    seen_fingerprints = set()

    for res in sorted_results:
        # Extract location to identify the source
        location = res.get("location", {})
        url = _extract_url(location) or "no-url"

        # Create a normalized content fingerprint (first 200 chars, whitespace removed)
        # This catches near-duplicate chunks that might differ by a single newline
        content = res.get("content", {}).get("text", "")
        content_snippet = "".join(content[:200].split()).lower()

        fingerprint = f"{url}|{content_snippet}"

        if fingerprint not in seen_fingerprints:
            unique_results.append(res)
            seen_fingerprints.add(fingerprint)

    return unique_results


def _retrieve_from_kb_raw(query: str) -> list[dict]:
    """
    Same as your original retrieval, but returns the LIST of dicts
    instead of a formatted string.
    """
    logger.info("Querying Bedrock KB with query: %s", query)

    response = bedrock_agent_runtime.retrieve(
        knowledgeBaseId=_KB_ID,
        retrievalQuery={"text": query},
        retrievalConfiguration={
            "vectorSearchConfiguration": {
                "numberOfResults": _NUM_RESULTS,
                "overrideSearchType": "HYBRID",
            }
        },
    )

    # We return the raw list of results here
    return response.get("retrievalResults", [])


async def fetch_support_knowledge(queries: list[str]) -> str:
    """
    Search the official Billy support documentation.

    Args:
        queries: A list of 2-3 search terms or phrases (Danish).
                 Example: ["opret faktura", "ny regning"]
    """
    try:
        print(f"DEBUG: Starting parallel KB retrieval for: {queries}")

        # return "No relevant documentation found."
        # return "[PASSAGE 1] score=0.49 | https://www.billy.dk/support/article/opret-forste-faktura/ URL: https://www.billy.dk/support/article/opret-forste-faktura/ Opret din første faktura i Billy ]()![ Produkt Priser Ressourcer For bogholdere & revisorer Log ind Opret gratis bruger ]()![ SupportartiklerFaktureringOpret din første faktura i Billy # Opret din første faktura i Billy Forfatter:Cecilie Topp Udgivet:12. september 2025 Læsetid:2 minutter Når du skal oprette en faktura, er der flere ting du skal være opmærksom på. I denne supportartikel vil jeg vise dig, hvor nemt det er at oprette og sende en faktura i Billy. Og hvis du hellere vil se det i en video, kan du se her, hvordan du opretter en faktura. Der er to ting at være opmærksom på når at man skal oprette en faktura i Billy. 1. Det valgte land på kontakten som man opretter fakturaen til. --- [PASSAGE 2] score=0.49 | https://www.billy.dk/support/article/rykker/ URL: https://www.billy.dk/support/article/rykker/ Oprettelse af rykker ved forfalden faktura ]()![ Produkt Priser Ressourcer For bogholdere & revisorer Log ind Opret gratis bruger ]()![ SupportartiklerFaktureringOprettelse af rykker ved forfalden faktura # Oprettelse af rykker ved forfalden faktura Forfatter:Hannibal Blytt Udgivet:16. oktober 2024 Læsetid:3 minutter Når en kunde ikke betaler til tiden sætter det virksomheden i en besværlig situation. Virksomheden har brug for at kunden betaler for at de selv kan betale deres regninger](https://www.billy.dk/billypedia/regning/). --- [PASSAGE 3] score=0.49 | https://www.billy.dk/support/article/opret-faktura-pa-engelsk/ URL: https://www.billy.dk/support/article/opret-faktura-pa-engelsk/ Konverter faktura – Fra dansk til engelsk med Billy ]()![ Produkt Priser Ressourcer For bogholdere & revisorer Log ind Opret gratis bruger ]()![ SupportartiklerFaktureringOpret faktura på engelsk # Opret faktura på engelsk Forfatter:Peter Flemming Askov Jensen Udgivet:15. september 2025 Læsetid:1 minut Hvis du skal oprette en faktura, som du gerne vil have på engelsk, kan du nemt gøre med nogle få klik. Det hele kan gøres i Billy. Du skal blot følge denne guide. ## Sådan oprettes en faktura på engelsk * Vælg **Kontakter** i menuen til venstre * Find den kunde hvor du vil ændre sproget på fakturaen til at være på engelsk * Tryk derefter på kontakten og vælg **Ret** * Vælg **Tilføj felt** nede i højre hjørne af kontaktboksen * Vælg **Sprog** * Tryk nu på Sprog boksen og vælg **Engelsk** * Fremtidige fakturaer vil nu blive på Engelsk i stedet. Har du spørgsmål til, er du altid velkommen til at kontakte os på **billy@billy.dk**, pr. telefon på **89 87 87 00** eller skrive til os på chatten. ]()! --- [PASSAGE 4] score=0.49 | https://www.billy.dk/support/article/aendre-faktura-sprog-pr-kunde/ URL: https://www.billy.dk/support/article/aendre-faktura-sprog-pr-kunde/ Konverter faktura – Fra dansk til engelsk med Billy ]()![ Produkt Priser Ressourcer For bogholdere & revisorer Log ind Opret gratis bruger ]()![ SupportartiklerFaktureringOpret faktura på engelsk # Opret faktura på engelsk Forfatter:Peter Flemming Askov Jensen Udgivet:15. september 2025 Læsetid:1 minut Hvis du skal oprette en faktura, som du gerne vil have på engelsk, kan du nemt gøre med nogle få klik. Det hele kan gøres i Billy. Du skal blot følge denne guide. ## Sådan oprettes en faktura på engelsk * Vælg **Kontakter** i menuen til venstre * Find den kunde hvor du vil ændre sproget på fakturaen til at være på engelsk * Tryk derefter på kontakten og vælg **Ret** * Vælg **Tilføj felt** nede i højre hjørne af kontaktboksen * Vælg **Sprog** * Tryk nu på Sprog boksen og vælg **Engelsk** * Fremtidige fakturaer vil nu blive på Engelsk i stedet. Har du spørgsmål til, er du altid velkommen til at kontakte os på **billy@billy.dk**, pr. telefon på **89 87 87 00** eller skrive til os på chatten. ]()! --- [PASSAGE 5] score=0.48 | https://www.billy.dk/support/article/haandter-debitorer-og-kreditorer-naar-du-skifter-til-billy/ URL: https://www.billy.dk/support/article/haandter-debitorer-og-kreditorer-naar-du-skifter-til-billy/ For at kunne holde styr på dine debitorer oprettes der én salgsfaktura pr. debitor. Start med at oprette et produkt via.: * Salg * Produkter * Opret produkt Fokusområder: * Giv produktet et valgfrit navn (navnet bør indikerer, at produktet kan anvendes til korrektion af debitorer) * Vælg 1110 -- Salg under Indtægtskategori * Vælg Momsfrit under Moms Dernæst oprettes én faktura pr. debitor. Først skal fakuranummereringen indstilles til manuel indtastning via.: * Indstillinger * Faktura * Vælg Fortløbende under Fakturanummerering * Gem Opret dernæst en faktura, som illustreret nedenfor: Fokusområder: * Opret en kunde * Vælg produktet * Indtast en passende beskrivelse (i dette tilfælde Indtast D1 under Fakturanr. (indikerer, at det er debitor nr. 1) * Indtast skæringsdatoen under Dato (i dette tilfælde 30-06-2021) * Indtast beløb under Enhedspris (i dette tilfælde 1.500 kr.) * Afslut med Godkend Du har nu oprettet en debitorsaldo på kunden Hans Jensen og din salgs- og tilgodehavende-konto er ajourført for denne kunde. ### **Håndtering af kreditorer** Når du skal ajourføre dine kreditorer skal du bruge en kreditorliste. Den viser alle gældsposter til dine leverandører pr. en given dato. --- [PASSAGE 6] score=0.46 | https://www.billy.dk/support/article/kom-nemt-i-gang-med-billy-4-trin/ URL: https://www.billy.dk/support/article/kom-nemt-i-gang-med-billy-4-trin/ Hvis du er momsfritaget, så er det underordnet, hvad du vælger, da det ikke har påvirkning på regnskabet. Som udgangspunkt indberetter alle nystartede virksomheder moms **kvartalsvist**. Herefter kan du finde dine fakturaindstillinger under **Faktura** i menuen Herunder kan du udfylde dine betalingsoplysninger, så dine kunder ved, hvordan de kan betale din faktura. Det gør du sådan her: * Tryk på **Opret Betalingsmetode** * Vælg **Bankoverførsel** * Vælg **5710 - Bank** som konto * Udfyld Bankens navn * Udfyld Reg og Kontonummer og tryk **Gem** ## ## **2. Lav din første faktura** Når du skal oprette en faktura så er der flere ting du skal være opmærksom på. Her vil vi vise hvor nemt det er at oprette og sende en faktura i Billy. * Klik på **Salg.** * Klik på **Fakturaer** * Klik på **Opret faktura** Derefter skal du vælge kunden den er til, vælg eksisterende kunde eller opret en ny ved at gøre følgende. * Klik på **Vælg kunde** * Klik på **Opret ny** Derefter skal du vælge om det er en **Virksomhed** eller en **Privatperson**. Hvis der er tale om en virksomhed så kan du skrive virksomhedens CVR-nummer og herefter kan du trykke på virksomheden, så vil alle relevante oplysninger blive udfyldt. --- [PASSAGE 7] score=0.46 | https://www.billy.dk/billypedia/udestaaende/ URL: https://www.billy.dk/billypedia/udestaaende/ Fra sælgers perspektiv er det kaldt en faktura. Fra købers perspektiv er det kaldt en regning. Når virksomheden sender en faktura, så der en række formelle krav til fakturaens indhold. Den skal nemlig indeholde mere end det skyldige beløb og en betalingsfrist ... ### Hvad indeholder en faktura? En faktura beskriver... * Hvem køber/ debitor ](https://www.billy.dk/billypedia/debitor/)og sælger/ [kreditor er med navn, adresse, CVR nummer m.m. * Hvornår produktet eller ydelsen er solgt. * Hvornår fakturaen er sendt til kunden. * Hvilket produkt eller ydelse der er leveret * Hvor mange produkter/ ydelser i antal * Hvad prisen er for produkterne/ ydelserne. * Hvor meget moms der er på købet. * Hvor stort et beløb kunden i alt skylder. * Hvornår betalingsfristen lyder. Når kunden har betalt det fulde beløb inden for betalingsfristen, så er der ikke længere et udestående mellem kunden og virksomheden. --- [PASSAGE 8] score=0.44 | https://www.billy.dk/billypedia/faktura/ URL: https://www.billy.dk/billypedia/faktura/ Faktura | Hvad er en faktura? | Læs mere her ]()![ Produkt Priser Ressourcer For bogholdere & revisorer Log ind Opret gratis bruger ]()![ BillypediaFaktura - Hvad er en faktura? # Faktura - Hvad er en faktura? En faktura, også kaldet en regning, er et dokument der specificerer salget af en vare eller ydelse, som sælger udsteder til køber som en anmodning om betaling. Fakturaen beskriver de forskellige omstændigheder omkring købet herunder pris, salgsdato og betalingsbetingelser. Med Billys fakturasevice kan du sende din første faktura med få klik. Prøv Billy gratis. --- [PASSAGE 9] score=0.44 | https://www.billy.dk/billypedia/tilbud/ URL: https://www.billy.dk/billypedia/tilbud/ Fakturaen er en essentiel del i at få betaling for den vare eller ydelse, som du har tilbudt til kunden. --- [PASSAGE 10] score=0.44 | https://www.billy.dk/support/article/5-tips-til-momsindberetning/ URL: https://www.billy.dk/support/article/5-tips-til-momsindberetning/ Vi har lavet en artikel som vil hjælpe dig med at forstå din skattekonto hos SKAT så du nemt kan afstemme skattekontoen. Hvis ikke man sørger for at betale de opkrævninger som SKAT har indregnet på din skattekonto, kan det hurtigt løbe op med de tillagte renter. ## Tip 5: Lav eventuelle efterindberetninger Det sker til tider at man har glemt en regning eller faktura efter man har afregnet sin moms til SKAT. Hvis dette er tilfældet, vil man skulle lave en efterindberetning når man har opdaget fejlen."

        # 1. Run all queries in parallel using asyncio.gather
        # This calls your existing _retrieve_from_kb logic for each string
        tasks = [asyncio.to_thread(_retrieve_from_kb_raw, q) for q in queries]
        results_nested = await asyncio.gather(*tasks)

        # 2. Flatten the results (list of lists -> list)
        all_results = [item for sublist in results_nested for item in sublist]

        # 3. Global Deduplication: This is the "Magic Sauce"
        # It removes duplicates across ALL queries at once
        unique_results = _get_unique_results(all_results)

        if not unique_results:
            return "No relevant documentation found."

        # 4. Format the final unique set into one clean string for Gemini
        return _format_passages(unique_results)

    except Exception as e:
        logger.error("Global KB retrieve error: %s", e)
        return "System error: I'm having trouble accessing the documentation."
