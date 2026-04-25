import asyncio
import logging
import os
from typing import Any

import boto3

logger = logging.getLogger(__name__)

_KB_ID = os.getenv("BEDROCK_KNOWLEDGE_BASE_ID", "C36YGJVEQP")
_AWS_REGION = os.getenv("AWS_REGION", "eu-central-1")
_AWS_PROFILE = os.getenv("AWS_PROFILE")
_RERANK_MODEL_ARN = f"arn:aws:bedrock:{os.getenv('AWS_REGION', 'eu-central-1')}::foundation-model/amazon.rerank-v1:0"
# Minimum relevance score — passages below this threshold are discarded as noise
_SCORE_THRESHOLD = 0.4
# Candidates pulled before reranking; more candidates improve reranker quality
_NUM_RESULTS = 15
# Maximum number of passages to return after deduplication and scoring
_MAX_UNIQUE_RESULTS = 4

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


def _extract_title_from_text(text: str) -> str | None:
    """Extract a page title embedded in the first chunk of a crawled page.

    Bedrock returns page-header chunks whose text begins with:
        "Page Title | Billy Regnskabsprogram\\n]()![\\n..."

    The title is the substring before the first " | ". Mid-page chunks start
    with body copy and contain no " | " near the start, so they return None.
    """
    pipe_idx = text.find(" | ")
    if pipe_idx == -1 or pipe_idx > 120:
        return None
    candidate = text[:pipe_idx].strip()
    # Reject single words, lowercase starts (body sentences), or overlong strings.
    if not candidate or candidate[0].islower() or len(candidate) > 100:
        return None
    return candidate


def _build_passages(
    retrieval_results: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """
    Convert raw Bedrock `retrieve` results into a list of structured passage dicts.

    Each passage contains its rank, score, source URL, query that produced it,
    optional title, and the raw text excerpt. Passages below _SCORE_THRESHOLD
    are dropped.
    """
    passages: list[dict[str, Any]] = []
    rank = 1

    for result in retrieval_results:
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
            metadata.get("title") or _extract_title_from_text(text) or url
        )

        passages.append(
            {
                "passage": rank,
                "score": round(score, 4),
                "url": url,
                "query": result.get("_query"),
                "title": title,
                "text": text,
            }
        )
        rank += 1

    return passages


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
    """Retrieve raw results from Bedrock KB, tagging each result with its query."""
    logger.info("Querying Bedrock KB with query: %s", query)

    response = bedrock_agent_runtime.retrieve(
        knowledgeBaseId=_KB_ID,
        retrievalQuery={"text": query},
        retrievalConfiguration={
            "vectorSearchConfiguration": {
                "numberOfResults": _NUM_RESULTS,
                "overrideSearchType": "HYBRID",
                "rerankingConfiguration": {
                    "type": "BEDROCK_RERANKING_MODEL",
                    "bedrockRerankingConfiguration": {
                        "numberOfRerankedResults": 5,
                        "modelConfiguration": {"modelArn": _RERANK_MODEL_ARN},
                        "metadataConfiguration": {"selectionMode": "ALL"},
                    },
                },
            }
        },
    )

    results = response.get("retrievalResults", [])
    for r in results:
        r["_query"] = query
    return results


async def fetch_support_knowledge(queries: list[str]) -> list[dict[str, Any]]:
    """
    Search the official Billy support documentation.

    Args:
        queries: A list of 2-3 search terms or phrases (Danish).
                 Example: ["opret faktura", "ny regning"]
    """
    try:
        logger.debug("Starting parallel KB retrieval for: %s", queries)

        # 1. Run all queries in parallel using asyncio.gather
        tasks = [asyncio.to_thread(_retrieve_from_kb_raw, q) for q in queries]
        results_nested = await asyncio.gather(*tasks)

        # 2. Flatten the results (list of lists -> list)
        all_results = [item for sublist in results_nested for item in sublist]

        # 3. Global deduplication across all queries
        unique_results = _get_unique_results(all_results)

        if not unique_results:
            return []

        # 4. Return structured passage dicts — FastMCP will put these in
        #    structuredContent so the caller sees typed objects, not a text blob.
        return _build_passages(unique_results[:_MAX_UNIQUE_RESULTS])

    except Exception as e:
        logger.error("Global KB retrieve error: %s", e, exc_info=True)
        return []
