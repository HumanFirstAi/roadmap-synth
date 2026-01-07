#!/usr/bin/env python3
"""
Roadmap Synthesis Tool
Single-file CLI for synthesizing strategic documents into roadmaps
"""

import os
import json
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime

import typer
from rich.console import Console
from rich.progress import track
from dotenv import load_dotenv
import tiktoken
import anthropic
import httpx
import voyageai
import lancedb
import networkx as nx
from unstructured.partition.auto import partition

# Configuration
load_dotenv()
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
VOYAGE_API_KEY = os.getenv("VOYAGE_API_KEY")
MATERIALS_DIR = Path("materials")
OUTPUT_DIR = Path("output")
DATA_DIR = Path("data")
PROMPTS_DIR = Path("prompts")

# Constants
CHUNK_SIZE = 1024
CHUNK_OVERLAP = 150
TOP_K = 20
VALID_LENSES = [
    "your-voice",
    "team-structured",
    "team-conversational",
    "sales-conversational",
    "business-framework",
    "engineering",
    "external-analyst"
]

# Initialize clients
console = Console()
app = typer.Typer(help="Roadmap Synthesis Tool - Generate strategic roadmaps from documents")


# ========== SECTION 1: UTILITY FUNCTIONS ==========

def count_tokens(text: str) -> int:
    """Count tokens using tiktoken"""
    encoding = tiktoken.get_encoding("cl100k_base")
    return len(encoding.encode(text))


def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """Calculate cosine similarity between two vectors."""
    import numpy as np

    v1 = np.array(vec1)
    v2 = np.array(vec2)

    # Compute cosine similarity
    dot_product = np.dot(v1, v2)
    norm1 = np.linalg.norm(v1)
    norm2 = np.linalg.norm(v2)

    if norm1 == 0 or norm2 == 0:
        return 0.0

    return float(dot_product / (norm1 * norm2))


def validate_api_keys():
    """Validate that required API keys are set"""
    if not ANTHROPIC_API_KEY:
        console.print("[red]Error: ANTHROPIC_API_KEY not set in .env file")
        raise typer.Exit(1)
    if not VOYAGE_API_KEY:
        console.print("[red]Error: VOYAGE_API_KEY not set in .env file")
        raise typer.Exit(1)


# ========== SECTION 2: DOCUMENT PARSING ==========

def parse_document(file_path: Path) -> str:
    """Parse document using unstructured library"""
    try:
        elements = partition(str(file_path))
        text = "\n\n".join([e.text for e in elements if hasattr(e, 'text')])
        return text
    except Exception as e:
        console.print(f"[red]Error parsing {file_path.name}: {e}")
        raise


# ========== SECTION 3: CHUNKING ==========
# Note: Main chunking functions are in Section 4.5 (agentic chunking)
# This section is kept for reference but chunking now happens via chunk_with_fallback()


# ========== SECTION 4: KEY TERM & TIME EXTRACTION ==========

def extract_key_terms(text: str, top_n: int = 10) -> List[str]:
    """Extract meaningful key terms, excluding common filler words."""
    import re
    from collections import Counter

    # Expanded stop words for conversations
    stop_words = {
        # Standard stops
        "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
        "of", "with", "by", "from", "as", "is", "was", "are", "were", "been",
        "be", "have", "has", "had", "do", "does", "did", "will", "would",
        "could", "should", "may", "might", "must", "shall", "can",
        "this", "that", "these", "those", "it", "its",
        "i", "you", "he", "she", "we", "they", "me", "him", "her", "us", "them",
        "my", "your", "his", "her", "our", "their",
        "what", "which", "who", "whom", "when", "where", "why", "how",

        # Conversational fillers
        "yeah", "yes", "no", "okay", "ok", "so", "well", "like", "just",
        "really", "very", "actually", "basically", "literally", "right",
        "um", "uh", "er", "ah", "hmm", "huh",
        "think", "know", "mean", "see", "look", "got", "get", "going",
        "thing", "things", "stuff", "something", "anything", "nothing",
        "good", "great", "nice", "fine", "cool", "awesome",
        "speaker", "minute", "minutes", "second", "seconds",

        # Common verbs
        "said", "say", "says", "saying", "talk", "talking", "talked",
        "want", "wants", "wanted", "need", "needs", "needed",
        "make", "makes", "made", "making",
    }

    # Extract words
    words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())

    # Filter stop words
    meaningful_words = [w for w in words if w not in stop_words]

    # Also extract capitalized phrases (likely proper nouns, products, teams)
    caps_phrases = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
    caps_lower = [p.lower() for p in caps_phrases if p.lower() not in stop_words]

    # Combine and count
    all_terms = meaningful_words + caps_lower
    counts = Counter(all_terms)

    # Return top N
    return [term for term, _ in counts.most_common(top_n)]


def extract_time_references(text: str) -> List[str]:
    """Extract temporal references from text."""
    import re

    patterns = [
        r'\bQ[1-4]\s*(?:20\d{2})?\b',  # Q1, Q2 2024, etc.
        r'\b20\d{2}\b',  # Years
        r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s*(?:20\d{2})?\b',
        r'\b(?:this|next|last)\s+(?:quarter|month|year)\b',
    ]

    refs = []
    for pattern in patterns:
        refs.extend(re.findall(pattern, text, re.IGNORECASE))

    return list(set(refs))


# ========== SECTION 4.4: QUALITY SCORING ==========

def score_chunk_quality(chunk: dict) -> dict:
    """
    Score a chunk's content quality.
    Returns score (0-1) and reasons.
    """
    import re

    content = chunk.get("content", "")
    lens = chunk.get("lens", "")

    score = 1.0
    reasons = []

    # === Universal checks ===

    # Too short
    word_count = len(content.split())
    if word_count < 20:
        score -= 0.5
        reasons.append(f"Very short ({word_count} words)")
    elif word_count < 50:
        score -= 0.2
        reasons.append(f"Short ({word_count} words)")

    # Low information density (high filler word ratio)
    filler_words = {
        "um", "uh", "like", "you know", "i mean", "sort of", "kind of",
        "basically", "actually", "literally", "right", "okay", "so",
        "yeah", "yes", "no", "well", "but", "and", "the", "a", "an"
    }
    words = content.lower().split()
    if words:
        filler_count = sum(1 for w in words if w.strip(".,!?") in filler_words)
        filler_ratio = filler_count / len(words)
        if filler_ratio > 0.4:
            score -= 0.4
            reasons.append(f"High filler ratio ({filler_ratio:.0%})")
        elif filler_ratio > 0.3:
            score -= 0.2
            reasons.append(f"Moderate filler ratio ({filler_ratio:.0%})")

    # === Conversational-specific checks ===

    if lens in ["team-conversational", "sales-conversational"]:

        # Check for greeting/small talk patterns
        small_talk_patterns = [
            r"^(hi|hey|hello|good morning|good afternoon)",
            r"how are you",
            r"thanks for (making|taking) the time",
            r"appreciate you",
            r"let me share my screen",
            r"can you hear me",
            r"you're on mute",
            r"let's get started",
            r"before we begin",
            r"^speaker \d+\s+\d+:\d+\s*(okay|so|yeah|right|um|uh)",
        ]

        content_lower = content.lower()
        for pattern in small_talk_patterns:
            if re.search(pattern, content_lower):
                score -= 0.3
                reasons.append(f"Small talk pattern: {pattern}")
                break

        # Check for substantive content indicators
        substantive_indicators = [
            r"roadmap", r"priority", r"timeline", r"deadline",
            r"customer", r"revenue", r"cost", r"budget",
            r"architecture", r"integration", r"api", r"platform",
            r"q[1-4]", r"20\d{2}", r"next quarter", r"this year",
            r"decision", r"strategy", r"plan", r"goal",
            r"problem", r"solution", r"risk", r"dependency",
            r"team", r"engineering", r"product", r"sales"
        ]

        substantive_count = 0
        for pattern in substantive_indicators:
            if re.search(pattern, content_lower):
                substantive_count += 1

        if substantive_count == 0:
            score -= 0.4
            reasons.append("No substantive keywords detected")
        elif substantive_count >= 3:
            score += 0.2  # Bonus for high substance
            reasons.append(f"High substance ({substantive_count} indicators)")

        # Check for actionable content
        action_patterns = [
            r"we (need|should|must|will|can|could)",
            r"(action|next step|todo|follow up)",
            r"(agree|disagree|concern|issue|blocker)",
            r"(decision|decided|choosing|choice)",
        ]

        has_action = any(re.search(p, content_lower) for p in action_patterns)
        if has_action:
            score += 0.1
            reasons.append("Contains actionable language")

    # Clamp score
    score = max(0.0, min(1.0, score))

    return {
        "score": score,
        "reasons": reasons,
        "should_index": score >= 0.4,  # Threshold
        "lens": lens
    }


# ========== SECTION 4.5: AGENTIC CHUNKING ==========

# Agentic chunking prompt template
AGENTIC_CHUNKING_PROMPT = """
You are a document segmentation tool. Your ONLY job is to identify logical boundaries and return character positions.

## CRITICAL RULES

1. **POSITIONS ONLY**: Return start_char and end_char positions ONLY
   - DO NOT include the actual content in JSON (it causes escaping issues)
   - I will extract the content using these positions

2. **METADATA FROM DOCUMENT**: All metadata must use ONLY words from the document
   - section_title: Actual heading or null
   - key_entities: Only explicitly named entities
   - time_references: Only explicitly mentioned dates/periods

3. **WHEN UNCERTAIN**: Use null or empty array

## CONVERSATIONAL CONTENT RULES

When chunking transcripts or meeting notes:

1. **SKIP pure small talk**: Greetings, "how are you", "thanks for joining" — do not create chunks for these

2. **SKIP filler transitions**: "So anyway", "Moving on", "Let me think" — unless followed by substantive content

3. **COMBINE speaker turns**: If multiple short turns discuss the same topic, combine into one chunk

4. **REQUIRE substance**: Every chunk must contain at least ONE of:
   - A decision or recommendation
   - A concern, risk, or blocker
   - A timeline or deadline reference
   - A specific plan or action item
   - A strategic insight or priority statement
   - Technical details or constraints

5. **PRESERVE context**: When extracting substantive content, include enough context to understand it:
   - Who is speaking (if relevant)
   - What topic is being discussed
   - What prompted the statement

**Example — BAD chunk (do not create):**
"Speaker 1 0:05 Good, yeah, that's mine, but it's okay, good man, yeah. So listen, I appreciate you making the time."

**Example — GOOD chunk:**
"Speaker 1 (Errol) discussing Acquisition roadmap: The big problem has been Tam's voice being too loud in prioritization. We need to align people to one mental model first. Once the mental model is established, then we can have productive debates about what goes in which quarter."

{document_type_hints}

## OUTPUT FORMAT

Return ONLY valid JSON. No markdown, no explanation.

{{
  "chunks": [
    {{
      "chunk_index": 0,
      "start_char": 0,
      "end_char": 1523,
      "section_title": "Exact heading or null",
      "key_entities": ["Entity1", "Entity2"],
      "time_references": ["Q2", "2024"]
    }}
  ]
}}

## DOCUMENT TO SEGMENT

<document>
{document_text}
</document>

IMPORTANT: Return ONLY the JSON with positions. Do NOT include document content in the JSON.
"""


def get_document_type_hints(source_path: str, content: str) -> str:
    """Generate document-specific chunking hints."""
    path = Path(source_path)
    suffix = path.suffix.lower()

    if suffix in ['.pptx', '.ppt']:
        return """
DOCUMENT TYPE: Presentation
- Each slide should typically be its own chunk
- Slide titles are section_title
- Keep bullet points with their slide
"""
    elif suffix in ['.docx', '.doc', '.pdf']:
        return """
DOCUMENT TYPE: Document
- Split at heading boundaries (look for formatting, numbering, or bold text)
- Keep headings with their content
- Preserve paragraph integrity
"""
    elif suffix in ['.txt', '.md']:
        # Check if it's a transcript
        transcript_markers = ['speaker:', 'q:', 'a:', '[', ']:']
        if any(marker in content.lower()[:2000] for marker in transcript_markers):
            return """
DOCUMENT TYPE: Transcript/Conversation
- Split at speaker changes
- Keep speaker attribution with their statement
- Preserve Q&A pairs together
"""
        else:
            return """
DOCUMENT TYPE: Notes/Text
- Split at heading markers (##, ###, ---, blank lines)
- Keep related bullet points together
- Preserve paragraph integrity
"""
    elif suffix in ['.csv', '.xlsx', '.xls']:
        return """
DOCUMENT TYPE: Structured Data
- Group related rows together
- Keep column headers with data
- Split at logical groupings if apparent
"""

    return """
DOCUMENT TYPE: Unknown
- Use paragraph breaks as primary split points
- Look for topic shifts
- Target 500-1500 tokens per chunk
"""


def verify_chunk_integrity(chunk: Dict, source_document: str) -> Dict:
    """
    Verify that all chunk content exists verbatim in source document.
    Returns verification result with any issues found.
    """
    issues = []

    # 1. Verify content is verbatim
    content = chunk.get("content", "")
    if content not in source_document:
        # Try to find closest match (sometimes whitespace differs)
        normalized_content = " ".join(content.split())
        normalized_source = " ".join(source_document.split())

        if normalized_content not in normalized_source:
            issues.append({
                "type": "CONTENT_NOT_FOUND",
                "severity": "CRITICAL",
                "message": "Chunk content does not exist verbatim in source document",
                "content_preview": content[:200]
            })

    # 2. Verify entities exist in source
    metadata = chunk.get("metadata", {})
    for entity in metadata.get("key_entities", []):
        if entity.lower() not in source_document.lower():
            issues.append({
                "type": "ENTITY_NOT_FOUND",
                "severity": "HIGH",
                "message": f"Entity '{entity}' not found in source document",
            })

    # 3. Verify time references exist
    for time_ref in metadata.get("time_references", []):
        if time_ref.lower() not in source_document.lower():
            issues.append({
                "type": "TIME_REF_NOT_FOUND",
                "severity": "HIGH",
                "message": f"Time reference '{time_ref}' not found in source document",
            })

    # 4. Verify section title exists (if provided)
    section_title = metadata.get("section_title")
    if section_title and section_title.lower() not in source_document.lower():
        issues.append({
            "type": "TITLE_NOT_FOUND",
            "severity": "MEDIUM",
            "message": f"Section title '{section_title}' not found in source document",
        })

    return {
        "chunk_id": chunk.get("chunk_index"),
        "is_valid": len([i for i in issues if i["severity"] == "CRITICAL"]) == 0,
        "issues": issues,
        "issue_count": len(issues)
    }


def verify_all_chunks(chunks: List[Dict], source_document: str) -> Dict:
    """Verify all chunks and return summary."""
    results = []
    critical_failures = 0

    for chunk in chunks:
        result = verify_chunk_integrity(chunk, source_document)
        results.append(result)
        if not result["is_valid"]:
            critical_failures += 1

    return {
        "total_chunks": len(chunks),
        "valid_chunks": len(chunks) - critical_failures,
        "critical_failures": critical_failures,
        "all_valid": critical_failures == 0,
        "results": results
    }


class AgenticChunker:
    """Chunk documents using Claude with strict extraction-only behavior."""

    def __init__(self, api_key: str = None, model: str = "claude-sonnet-4-20250514"):
        import httpx
        self.client = anthropic.Anthropic(
            api_key=api_key or ANTHROPIC_API_KEY,
            http_client=httpx.Client(verify=False)  # Disable SSL verification
        )
        self.model = model
        self.prompt_template = AGENTIC_CHUNKING_PROMPT
        self.max_tokens = 16000  # Increased from 8000 to handle large documents

    def chunk_document(self, document_text: str, source_path: str, lens: str) -> List[Dict]:
        """
        Chunk a document using Claude.
        Returns list of verified chunks with metadata.
        """
        import json

        # Skip very short documents
        if len(document_text.strip()) < 100:
            return [{
                "chunk_index": 0,
                "content": document_text.strip(),
                "lens": lens,
                "source_file": source_path,
                "chunk_index": 0,
                "token_count": count_tokens(document_text.strip()),
                "metadata": {
                    "section_title": None,
                    "key_entities": [],
                    "time_references": []
                }
            }]

        # Get document-specific hints
        hints = get_document_type_hints(source_path, document_text)

        # Call Claude
        prompt = self.prompt_template.format(
            document_text=document_text,
            document_type_hints=hints
        )

        response = self.client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            temperature=0,  # Deterministic for consistency
            messages=[{"role": "user", "content": prompt}]
        )

        # Parse response
        response_text = response.content[0].text

        # Extract JSON from response
        chunks_data = self._parse_json_response(response_text)

        # Extract content using positions and verify each chunk
        verified_chunks = []
        for chunk in chunks_data.get("chunks", []):
            # NEW: Extract actual content using character positions
            start_char = chunk.get("start_char", 0)
            end_char = chunk.get("end_char", len(document_text))

            # Validate positions
            if start_char < 0 or end_char > len(document_text) or start_char >= end_char:
                console.print(f"[yellow]⚠ Chunk {chunk.get('chunk_index')} has invalid positions: {start_char}-{end_char}")
                continue

            # Extract content
            chunk["content"] = document_text[start_char:end_char]

            # Build metadata structure from flat fields returned by Claude
            if "metadata" not in chunk:
                chunk["metadata"] = {
                    "section_title": chunk.get("section_title"),
                    "key_entities": chunk.get("key_entities", []),
                    "time_references": chunk.get("time_references", [])
                }

            # Now verify the chunk
            verification = verify_chunk_integrity(chunk, document_text)

            if verification["is_valid"]:
                # Format chunk for indexing
                formatted_chunk = {
                    "content": chunk["content"],
                    "lens": lens,
                    "chunk_index": chunk["chunk_index"],
                    "token_count": count_tokens(chunk["content"]),
                    "source_file": source_path,
                    "metadata": chunk["metadata"]
                }
                verified_chunks.append(formatted_chunk)
            else:
                # Log but try to salvage
                console.print(f"[yellow]⚠ Chunk {chunk.get('chunk_index')} failed verification")
                salvaged = self._salvage_chunk(chunk, document_text, source_path, lens)
                if salvaged:
                    verified_chunks.append(salvaged)

        return verified_chunks

    def _parse_json_response(self, response_text: str) -> Dict:
        """Extract JSON from Claude's response."""
        import json
        import re

        try:
            # Look for ```json block
            if "```json" in response_text:
                start = response_text.find("```json") + 7
                end = response_text.find("```", start)
                json_str = response_text[start:end].strip()
            elif "```" in response_text:
                start = response_text.find("```") + 3
                end = response_text.find("```", start)
                json_str = response_text[start:end].strip()
            else:
                # Try parsing entire response
                json_str = response_text.strip()

            # Try to parse
            return json.loads(json_str)

        except json.JSONDecodeError as e:
            console.print(f"[yellow]⚠ JSON parse error: {e}")
            console.print(f"[yellow]Attempting to fix malformed JSON...")

            # Try to extract just the chunks array
            try:
                # Find chunks array in response
                chunks_match = re.search(r'"chunks"\s*:\s*\[(.*)\]', response_text, re.DOTALL)
                if chunks_match:
                    console.print(f"[yellow]Found chunks array, attempting manual parse...")
                    # This is complex - just log and return empty
                    console.print(f"[red]Could not recover from JSON error")

                    # Save problematic response for debugging
                    debug_path = DATA_DIR / "debug_response.txt"
                    debug_path.parent.mkdir(exist_ok=True)
                    with open(debug_path, "w") as f:
                        f.write(response_text)
                    console.print(f"[yellow]Response saved to {debug_path} for debugging")

                return {"chunks": []}
            except Exception as e2:
                console.print(f"[red]Recovery failed: {e2}")
                return {"chunks": []}

    def _salvage_chunk(self, chunk: Dict, document_text: str, source_path: str, lens: str) -> Optional[Dict]:
        """
        Try to salvage a chunk that failed verification by finding
        the closest matching text in the document.
        """
        content = chunk.get("content", "")
        if not content:
            return None

        # Try to find content with fuzzy matching
        words = content.split()
        if len(words) < 5:
            return None

        # Try progressively shorter matches
        for length in range(len(words), 4, -1):
            search_phrase = " ".join(words[:length])
            if search_phrase.lower() in document_text.lower():
                # Found match - extract surrounding context
                idx = document_text.lower().find(search_phrase.lower())

                # Extract ~1000 chars around match
                start = max(0, idx - 100)
                end = min(len(document_text), idx + len(search_phrase) + 900)

                # Adjust to word boundaries
                while start > 0 and document_text[start] not in " \n":
                    start -= 1
                while end < len(document_text) and document_text[end] not in " \n":
                    end += 1

                salvaged_content = document_text[start:end].strip()

                return {
                    "chunk_index": chunk.get("chunk_index", 0),
                    "content": salvaged_content,
                    "lens": lens,
                    "source_file": source_path,
                    "token_count": count_tokens(salvaged_content),
                    "metadata": {
                        "section_title": None,
                        "key_entities": extract_key_terms(salvaged_content),
                        "time_references": extract_time_references(salvaged_content)
                    },
                    "salvaged": True
                }

        return None


def structure_aware_chunk(text: str, source_path: str, lens: str) -> List[Dict]:
    """Structure-aware fallback chunking (token-based with overlap)."""
    encoding = tiktoken.get_encoding("cl100k_base")
    tokens = encoding.encode(text)

    if len(tokens) == 0:
        return []

    chunks = []
    start = 0
    chunk_idx = 0

    while start < len(tokens):
        end = min(start + CHUNK_SIZE, len(tokens))
        chunk_tokens = tokens[start:end]
        chunk_content = encoding.decode(chunk_tokens)

        chunks.append({
            "content": chunk_content,
            "lens": lens,
            "chunk_index": chunk_idx,
            "token_count": len(chunk_tokens),
            "source_file": source_path,
            "metadata": {
                "section_title": None,
                "key_entities": extract_key_terms(chunk_content),
                "time_references": extract_time_references(chunk_content)
            }
        })

        # If we've reached the end, break
        if end >= len(tokens):
            break

        start = end - CHUNK_OVERLAP
        chunk_idx += 1

    return chunks


def filter_chunks_by_quality(
    chunks: List[Dict],
    min_quality_score: float = 0.4,
    log_filtered: bool = False
) -> tuple[List[Dict], List[Dict]]:
    """
    Filter chunks by quality score.
    Returns (accepted_chunks, filtered_chunks).
    """
    accepted = []
    filtered = []

    for chunk in chunks:
        quality = score_chunk_quality(chunk)
        chunk["quality_score"] = quality["score"]
        chunk["quality_reasons"] = quality["reasons"]

        if quality["should_index"]:
            accepted.append(chunk)
        else:
            filtered.append(chunk)
            if log_filtered:
                console.print(f"[dim]Filtered chunk (score={quality['score']:.2f}): {chunk['content'][:100]}...")
                console.print(f"[dim]  Reasons: {', '.join(quality['reasons'])}")

    return accepted, filtered


def chunk_with_fallback(
    document_text: str,
    source_path: str,
    lens: str,
    use_agentic: bool = True,
    max_retries: int = 2,
    log_results: bool = True,
    apply_quality_filter: bool = True
) -> List[Dict]:
    """
    Attempt agentic chunking with fallback to structure-aware chunking.
    Optionally filters low-quality chunks.
    """
    # Check if agentic should be used
    if not use_agentic:
        console.print(f"[blue]Using structure-aware chunking for {Path(source_path).name}")
        chunks = structure_aware_chunk(document_text, source_path, lens)

        # Apply quality filter
        if apply_quality_filter:
            chunks, filtered = filter_chunks_by_quality(chunks, log_filtered=False)
            if filtered:
                console.print(f"[dim]Filtered {len(filtered)} low-quality chunks")

        if log_results:
            log_chunking_result(source_path, lens, chunks, None, "structure-aware")
        return chunks

    # Helper function to apply quality filter before returning
    def _finalize_chunks(chunks, method_name):
        if apply_quality_filter:
            chunks, filtered = filter_chunks_by_quality(chunks, log_filtered=False)
            if filtered:
                console.print(f"[dim]Filtered {len(filtered)} low-quality chunks")
        if log_results:
            log_chunking_result(source_path, lens, chunks, None, method_name)
        return chunks

    # Estimate tokens to decide if agentic is worth it
    est_tokens = len(document_text) // 4
    if est_tokens > 30000:
        console.print(f"[yellow]Document too large ({est_tokens} est. tokens), using fallback")
        chunks = structure_aware_chunk(document_text, source_path, lens)
        return _finalize_chunks(chunks, "structure-aware (too large)")

    if est_tokens < 100:
        console.print(f"[yellow]Document too small ({est_tokens} est. tokens), using fallback")
        chunks = structure_aware_chunk(document_text, source_path, lens)
        return _finalize_chunks(chunks, "structure-aware (too small)")

    # Try agentic chunking
    for attempt in range(max_retries):
        try:
            console.print(f"[blue]Attempting agentic chunking (attempt {attempt + 1}/{max_retries})...")
            chunker = AgenticChunker()
            chunks = chunker.chunk_document(document_text, source_path, lens)

            # Verify
            verification = verify_all_chunks(chunks, document_text)

            if verification["all_valid"]:
                console.print(f"[green]✓ Agentic chunking succeeded ({len(chunks)} chunks)")

                # Apply quality filter
                if apply_quality_filter:
                    chunks, filtered = filter_chunks_by_quality(chunks, log_filtered=False)
                    if filtered:
                        console.print(f"[dim]Filtered {len(filtered)} low-quality chunks")

                if log_results:
                    log_chunking_result(source_path, lens, chunks, verification, "agentic")
                return chunks

            # Log issues but continue if mostly valid
            if verification["valid_chunks"] / verification["total_chunks"] > 0.8:
                console.print(f"[yellow]⚠ {verification['critical_failures']} chunks failed, using {verification['valid_chunks']} valid chunks")

                # Apply quality filter
                if apply_quality_filter:
                    chunks, filtered = filter_chunks_by_quality(chunks, log_filtered=False)
                    if filtered:
                        console.print(f"[dim]Filtered {len(filtered)} low-quality chunks")

                if log_results:
                    log_chunking_result(source_path, lens, chunks, verification, "agentic (partial)")
                return chunks

            # Too many failures, retry
            console.print(f"[yellow]Attempt {attempt + 1}: {verification['critical_failures']} chunks failed verification")

        except Exception as e:
            console.print(f"[red]Agentic chunking failed: {e}")

    # Fallback to structure-aware chunking
    console.print(f"[yellow]Falling back to structure-aware chunking for {Path(source_path).name}")
    chunks = structure_aware_chunk(document_text, source_path, lens)
    return _finalize_chunks(chunks, "structure-aware (fallback)")


# Keep original function for backward compatibility
def chunk_text(text: str, lens: str, source_path: str = "") -> List[Dict]:
    """
    Legacy function - wraps structure_aware_chunk for backward compatibility.
    """
    return structure_aware_chunk(text, source_path or "unknown", lens)


def log_chunking_result(
    source_path: str,
    lens: str,
    chunks: List[Dict],
    verification: Optional[Dict],
    method: str
) -> Dict:
    """Log chunking results for auditing."""
    import json
    from datetime import datetime

    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "source_path": source_path,
        "lens": lens,
        "method": method,
        "chunk_count": len(chunks),
        "verification": {
            "all_valid": verification.get("all_valid", True) if verification else True,
            "valid_count": verification.get("valid_chunks", len(chunks)) if verification else len(chunks),
            "issues": [
                {
                    "chunk_index": r["chunk_id"],
                    "issues": r["issues"]
                }
                for r in verification.get("results", []) if verification
                if r.get("issues")
            ] if verification else []
        },
        "chunks_preview": [
            {
                "index": c.get("chunk_index", i),
                "content_length": len(c.get("content", "")),
                "content_preview": c.get("content", "")[:100],
                "entities": c.get("metadata", {}).get("key_entities", []) if isinstance(c.get("metadata"), dict) else [],
            }
            for i, c in enumerate(chunks[:5])
        ]
    }

    # Save to log file
    log_path = DATA_DIR / "chunking_log.jsonl"
    log_path.parent.mkdir(exist_ok=True)

    with open(log_path, "a") as f:
        f.write(json.dumps(log_entry) + "\n")

    return log_entry


class ContextGraph:
    """Graph-based context management for chunk relationships"""

    def __init__(self, graph_path: Path = DATA_DIR / "context_graph.json"):
        import networkx as nx
        self.graph_path = graph_path
        self.graph = nx.Graph()

    def build_from_chunks(self, chunks: List[Dict], embeddings: List[List[float]]):
        """Build graph from chunks and their embeddings."""
        # Add nodes
        for chunk in chunks:
            self.graph.add_node(
                chunk["id"],
                lens=chunk.get("lens", ""),
                source_path=chunk.get("source_file", ""),
                source_name=Path(chunk.get("source_file", "")).name,
                chunk_index=chunk.get("chunk_index", 0),
                token_count=chunk.get("token_count", 0),
                content_preview=chunk.get("content", "")[:200],
                key_terms=extract_key_terms(chunk.get("content", "")),
                time_references=extract_time_references(chunk.get("content", "")),
            )

        # Add edges
        self._add_same_source_edges(chunks)
        self._add_same_lens_edges(chunks)
        self._add_sequential_edges(chunks)
        self._add_topic_overlap_edges(chunks)
        self._add_similarity_edges(chunks, embeddings)
        self._add_temporal_edges(chunks)

    def _add_same_source_edges(self, chunks: List[Dict]):
        """Connect chunks from same source document."""
        by_source = {}
        for chunk in chunks:
            src = chunk.get("source_file", "")
            if src not in by_source:
                by_source[src] = []
            by_source[src].append(chunk["id"])

        for source, chunk_ids in by_source.items():
            for i, id1 in enumerate(chunk_ids):
                for id2 in chunk_ids[i+1:]:
                    self.graph.add_edge(id1, id2, type="SAME_SOURCE", weight=1.0)

    def _add_same_lens_edges(self, chunks: List[Dict]):
        """Connect chunks with same lens (lightweight edges)."""
        by_lens = {}
        for chunk in chunks:
            lens = chunk.get("lens", "")
            if lens not in by_lens:
                by_lens[lens] = []
            by_lens[lens].append(chunk["id"])

        # Only connect if not too many (avoid explosion)
        for lens, chunk_ids in by_lens.items():
            if len(chunk_ids) <= 50:
                for i, id1 in enumerate(chunk_ids):
                    for id2 in chunk_ids[i+1:]:
                        if not self.graph.has_edge(id1, id2):
                            self.graph.add_edge(id1, id2, type="SAME_LENS", weight=0.5)

    def _add_sequential_edges(self, chunks: List[Dict]):
        """Connect adjacent chunks in same document."""
        by_source = {}
        for chunk in chunks:
            src = chunk.get("source_file", "")
            if src not in by_source:
                by_source[src] = []
            by_source[src].append(chunk)

        for source, source_chunks in by_source.items():
            sorted_chunks = sorted(source_chunks, key=lambda x: x.get("chunk_index", 0))
            for i in range(len(sorted_chunks) - 1):
                id1 = sorted_chunks[i]["id"]
                id2 = sorted_chunks[i + 1]["id"]
                self.graph.add_edge(id1, id2, type="SEQUENTIAL", weight=1.0)

    def _add_topic_overlap_edges(self, chunks: List[Dict]):
        """Connect chunks that share key terms."""
        # Get key terms for each chunk
        chunk_terms = {}
        for chunk in chunks:
            terms = set(extract_key_terms(chunk.get("content", "")))
            chunk_terms[chunk["id"]] = terms

        # Find overlaps
        chunk_ids = list(chunk_terms.keys())
        for i, id1 in enumerate(chunk_ids):
            for id2 in chunk_ids[i+1:]:
                overlap = chunk_terms[id1] & chunk_terms[id2]
                if len(overlap) >= 2:  # At least 2 shared terms
                    if not self.graph.has_edge(id1, id2):
                        self.graph.add_edge(
                            id1, id2,
                            type="TOPIC_OVERLAP",
                            weight=len(overlap),
                            shared_terms=list(overlap)
                        )

    def _add_similarity_edges(self, chunks: List[Dict], embeddings: List[List[float]], threshold: float = 0.80):
        """Connect semantically similar chunks."""
        import numpy as np

        # Convert to numpy for efficient computation
        emb_matrix = np.array(embeddings)

        # Normalize for cosine similarity
        norms = np.linalg.norm(emb_matrix, axis=1, keepdims=True)
        normalized = emb_matrix / norms

        # Compute similarities in batches (avoid memory explosion)
        n = len(chunks)
        batch_size = 100

        for i in range(0, n, batch_size):
            batch_end = min(i + batch_size, n)
            batch = normalized[i:batch_end]

            # Compare batch against all chunks
            similarities = np.dot(batch, normalized.T)

            for bi, sim_row in enumerate(similarities):
                chunk_i = i + bi
                for chunk_j in range(chunk_i + 1, n):
                    sim = sim_row[chunk_j]
                    if sim > threshold:
                        id1 = chunks[chunk_i]["id"]
                        id2 = chunks[chunk_j]["id"]
                        if not self.graph.has_edge(id1, id2):
                            self.graph.add_edge(
                                id1, id2,
                                type="SIMILAR_TO",
                                weight=float(sim)
                            )

    def _add_temporal_edges(self, chunks: List[Dict]):
        """Connect chunks referencing same time periods."""
        chunk_times = {}
        for chunk in chunks:
            times = set(extract_time_references(chunk.get("content", "")))
            if times:
                chunk_times[chunk["id"]] = times

        chunk_ids = list(chunk_times.keys())
        for i, id1 in enumerate(chunk_ids):
            for id2 in chunk_ids[i+1:]:
                overlap = chunk_times[id1] & chunk_times[id2]
                if overlap and not self.graph.has_edge(id1, id2):
                    self.graph.add_edge(
                        id1, id2,
                        type="TEMPORAL_OVERLAP",
                        weight=1.0,
                        shared_periods=list(overlap)
                    )

    def save(self):
        """Save graph to JSON."""
        import networkx as nx
        import json
        data = nx.node_link_data(self.graph)
        self.graph_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.graph_path, "w") as f:
            json.dump(data, f, indent=2, default=str)

    def load(self):
        """Load graph from JSON."""
        import networkx as nx
        import json
        if self.graph_path.exists():
            with open(self.graph_path) as f:
                data = json.load(f)
            self.graph = nx.node_link_graph(data)
        return self

    def get_stats(self) -> Dict:
        """Get graph statistics."""
        import networkx as nx
        edge_types = {}
        for _, _, data in self.graph.edges(data=True):
            t = data.get("type", "UNKNOWN")
            edge_types[t] = edge_types.get(t, 0) + 1

        return {
            "nodes": self.graph.number_of_nodes(),
            "edges": self.graph.number_of_edges(),
            "edge_types": edge_types,
            "density": nx.density(self.graph),
            "components": nx.number_connected_components(self.graph),
        }


# ========== SECTION 5: EMBEDDINGS & INDEXING ==========

def generate_embeddings(texts: List[str]) -> List[List[float]]:
    """Generate embeddings using Voyage AI"""
    validate_api_keys()
    import ssl
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    vo = voyageai.Client(api_key=VOYAGE_API_KEY)
    result = vo.embed(texts=texts, model="voyage-3-large", input_type="document")
    return result.embeddings


def init_db():
    """Initialize LanceDB connection"""
    DATA_DIR.mkdir(exist_ok=True)
    return lancedb.connect(str(DATA_DIR))


def index_chunks(chunks: List[Dict], source_file: str):
    """Store chunks in LanceDB"""
    if not chunks:
        return

    db = init_db()

    # Generate embeddings
    texts = [c["content"] for c in chunks]
    embeddings = generate_embeddings(texts)

    # Prepare records
    records = []
    for chunk, embedding in zip(chunks, embeddings):
        records.append({
            "id": f"{source_file}_{chunk['chunk_index']}",
            "content": chunk["content"],
            "vector": embedding,
            "lens": chunk["lens"],
            "source_file": source_file,
            "chunk_index": chunk["chunk_index"],
            "token_count": chunk["token_count"],
            "created_at": datetime.now()
        })

    # Create or append to table
    try:
        table = db.open_table("roadmap_chunks")
        table.add(records)
    except Exception:
        # Table doesn't exist, create it
        db.create_table("roadmap_chunks", records)


# ========== SECTION 6: RETRIEVAL ==========

def retrieve_chunks(query: str, top_k: int = TOP_K) -> List[Dict]:
    """Semantic search over indexed chunks"""
    validate_api_keys()
    db = init_db()

    try:
        table = db.open_table("roadmap_chunks")
    except Exception:
        console.print("[yellow]Warning: No indexed documents found. Run 'ingest' first.")
        return []

    # Generate query embedding
    import ssl
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    vo = voyageai.Client(api_key=VOYAGE_API_KEY)
    query_embedding = vo.embed(
        texts=[query],
        model="voyage-3-large",
        input_type="query"
    ).embeddings[0]

    # Search
    results = table.search(query_embedding).limit(top_k).to_list()

    # Sort by lens priority (your-voice highest, external-analyst lowest)
    lens_priority = {lens: i for i, lens in enumerate(VALID_LENSES)}
    results.sort(key=lambda x: lens_priority.get(x["lens"], 999))

    return results


def retrieve_balanced(query: str, chunks_per_lens: int = 8) -> List[Dict]:
    """Retrieve chunks with guaranteed representation from each lens."""
    validate_api_keys()
    db = init_db()

    try:
        table = db.open_table("roadmap_chunks")
    except Exception:
        console.print("[yellow]Warning: No indexed documents found. Run 'ingest' first.")
        return []

    # Generate query embedding
    import ssl
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    vo = voyageai.Client(api_key=VOYAGE_API_KEY)
    query_embedding = vo.embed(
        texts=[query],
        model="voyage-3-large",
        input_type="query"
    ).embeddings[0]

    all_results = []
    for lens in VALID_LENSES:
        try:
            results = (
                table.search(query_embedding)
                .where(f"lens = '{lens}'")
                .limit(chunks_per_lens)
                .to_list()
            )
            all_results.extend(results)
        except Exception:
            # Lens may have no chunks
            pass

    return all_results


def retrieve_with_graph_expansion(
    query: str,
    graph: ContextGraph,
    initial_limit: int = 20,
    expansion_hops: int = 1,
    final_limit: int = 50
) -> List[Dict]:
    """Retrieve chunks and expand via graph relationships."""
    import networkx as nx
    validate_api_keys()
    db = init_db()

    try:
        table = db.open_table("roadmap_chunks")
    except Exception:
        return []

    # Generate query embedding
    import ssl
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    vo = voyageai.Client(api_key=VOYAGE_API_KEY)
    query_embedding = vo.embed(
        texts=[query],
        model="voyage-3-large",
        input_type="query"
    ).embeddings[0]

    # Step 1: Initial vector search
    initial_results = table.search(query_embedding).limit(initial_limit).to_list()
    seed_ids = {r["id"] for r in initial_results}

    # Step 2: Expand via graph
    expanded_ids = set(seed_ids)
    for chunk_id in seed_ids:
        if chunk_id in graph.graph:
            # Get neighbors within N hops
            neighbors = nx.single_source_shortest_path_length(
                graph.graph, chunk_id, cutoff=expansion_hops
            )
            expanded_ids.update(neighbors.keys())

    # Step 3: Fetch expanded chunks
    new_ids = expanded_ids - seed_ids

    expanded_results = []
    if new_ids:
        # Fetch from table by ID
        for chunk_id in new_ids:
            try:
                result = table.search(query_embedding).where(f"id = '{chunk_id}'").limit(1).to_list()
                if result:
                    expanded_results.extend(result)
            except Exception:
                pass

    # Step 4: Combine and deduplicate
    all_results = initial_results + expanded_results
    seen = set()
    unique_results = []
    for r in all_results:
        if r["id"] not in seen:
            seen.add(r["id"])
            unique_results.append(r)

    return unique_results[:final_limit]


def detect_potential_contradictions(chunks: List[Dict], graph: ContextGraph) -> List[Dict]:
    """Find chunks that may contradict each other."""
    contradictions = []

    # Group by topic
    topic_groups = {}
    for chunk in chunks:
        chunk_id = chunk.get("id", "")
        if chunk_id in graph.graph.nodes:
            terms = graph.graph.nodes[chunk_id].get("key_terms", [])
            for term in terms:
                if term not in topic_groups:
                    topic_groups[term] = []
                topic_groups[term].append(chunk)

    # Find cross-lens disagreements on same topic
    for topic, topic_chunks in topic_groups.items():
        if len(topic_chunks) < 2:
            continue

        # Check for different lenses discussing same topic
        lenses_present = set(c.get("lens", "") for c in topic_chunks)

        # Flag if conversational disagrees with structured
        if "team-conversational" in lenses_present and "team-structured" in lenses_present:
            contradictions.append({
                "topic": topic,
                "type": "conversational_vs_structured",
                "chunks": [c for c in topic_chunks if c.get("lens") in ["team-conversational", "team-structured"]],
                "note": "Team discussions may reveal concerns not in formal docs"
            })

        # Flag if engineering contradicts product plans
        if "engineering" in lenses_present and "team-structured" in lenses_present:
            contradictions.append({
                "topic": topic,
                "type": "engineering_vs_product",
                "chunks": [c for c in topic_chunks if c.get("lens") in ["engineering", "team-structured"]],
                "note": "Engineering feasibility may conflict with product plans"
            })

    return contradictions


# ========== SECTION 7: SYNTHESIS ==========

def load_prompt(name: str) -> str:
    """Load prompt from file"""
    prompt_path = PROMPTS_DIR / name
    if not prompt_path.exists():
        console.print(f"[red]Error: Prompt file not found: {prompt_path}")
        raise typer.Exit(1)
    return prompt_path.read_text()


def format_decisions_for_synthesis(decisions: List[Dict]) -> str:
    """
    Format decision log for inclusion in synthesis context.
    Only includes active decisions that should inform the roadmap.
    """
    active = [d for d in decisions if d.get("status", "active") == "active"]

    if not active:
        return ""

    output = ["## PREVIOUS DECISIONS", ""]
    output.append("The following decisions have been made by stakeholders and should be reflected in the roadmap:")
    output.append("")

    for dec in sorted(active, key=lambda x: x.get("created_at", ""), reverse=True):
        output.append(f"### Decision {dec['id']} ({dec.get('created_at', 'Unknown')[:10]})")
        output.append(f"**Decision:** {dec['decision']}")

        if dec.get("rationale"):
            output.append(f"**Rationale:** {dec['rationale']}")

        if dec.get("implications"):
            output.append("**Implications:**")
            for imp in dec["implications"]:
                output.append(f"  - {imp}")

        output.append(f"**Owner:** {dec.get('owner', 'Unassigned')}")

        # Link to original question
        question_id = dec.get("question_id")
        if question_id:
            output.append(f"**Original Question ID:** {question_id}")

        output.append("")

    # Add integration instructions
    output.append("### How to Use These Decisions")
    output.append("")
    output.append("1. **Respect active decisions** — These are resolved questions; incorporate their implications into the roadmap")
    output.append("2. **Note decision impacts** — Show how decisions affected roadmap items in your synthesis")
    output.append("3. **Flag conflicts** — If new information contradicts a decision, surface this explicitly")
    output.append("4. **Don't re-open decided questions** — Unless new evidence makes them obsolete")
    output.append("")

    return "\n".join(output)


def generate_roadmap(query: str = "Generate a comprehensive product roadmap") -> str:
    """Generate master roadmap using Claude with graph-enhanced retrieval"""
    validate_api_keys()

    console.print("[blue]Loading context graph...")
    graph = ContextGraph().load()

    # Multiple queries for comprehensive retrieval
    console.print("[blue]Retrieving relevant context...")
    queries = [
        "product strategy and vision",
        "roadmap priorities and timeline",
        "technical architecture and dependencies",
        "customer needs and outcomes",
        "resource constraints and trade-offs",
        "risks and concerns",
    ]

    # Retrieve with balanced lens representation
    all_chunks = []
    for q in queries:
        chunks = retrieve_balanced(q, chunks_per_lens=5)
        all_chunks.extend(chunks)

    # Expand via graph if graph is loaded
    if graph.graph.number_of_nodes() > 0:
        console.print("[blue]Expanding context via graph relationships...")
        expanded = retrieve_with_graph_expansion(
            queries[0],  # Primary query
            graph,
            initial_limit=30,
            expansion_hops=1,
            final_limit=60
        )
        all_chunks.extend(expanded)

    # Deduplicate
    seen = set()
    final_chunks = []
    for chunk in all_chunks:
        if chunk["id"] not in seen:
            seen.add(chunk["id"])
            final_chunks.append(chunk)

    if not final_chunks:
        console.print("[red]Error: No chunks found. Please ingest documents first.")
        raise typer.Exit(1)

    console.print(f"[blue]Retrieved {len(final_chunks)} chunks from {len(set(c['lens'] for c in final_chunks))} lenses")

    # Detect contradictions
    contradictions = []
    if graph.graph.number_of_nodes() > 0:
        console.print("[blue]Detecting potential contradictions...")
        contradictions = detect_potential_contradictions(final_chunks, graph)
        if contradictions:
            console.print(f"[yellow]Found {len(contradictions)} potential contradictions to consider")

    # Build context organized by lens
    context_by_lens = {}
    for chunk in final_chunks:
        lens = chunk["lens"]
        if lens not in context_by_lens:
            context_by_lens[lens] = []
        context_by_lens[lens].append(chunk["content"])

    # Format context
    context_str = ""
    for lens in VALID_LENSES:
        if lens in context_by_lens:
            context_str += f"\n## {lens.upper().replace('-', ' ')} SOURCES:\n"
            context_str += "\n\n".join(context_by_lens[lens])

    # Add contradiction warnings
    if contradictions:
        context_str += "\n\n## Potential Contradictions Detected\n"
        for c in contradictions[:5]:  # Top 5
            context_str += f"\n### {c['topic']} ({c['type']})\n"
            context_str += f"Note: {c['note']}\n"

    # Load and add decision log
    decisions = load_decisions()
    if decisions:
        decision_context = format_decisions_for_synthesis(decisions)
        if decision_context:
            context_str += f"\n\n{decision_context}"
            console.print(f"[blue]Including {len([d for d in decisions if d.get('status') == 'active'])} active decisions in context")

    # Load synthesis prompt
    synthesis_prompt = load_prompt("synthesis.md")

    # Call Claude
    console.print("[blue]Generating roadmap with Claude...")
    import httpx
    client = anthropic.Anthropic(
        api_key=ANTHROPIC_API_KEY,
        http_client=httpx.Client(verify=False)  # Disable SSL verification
    )
    message = client.messages.create(
        model="claude-opus-4-5-20251101",
        max_tokens=8000,
        system=synthesis_prompt,
        messages=[
            {"role": "user", "content": f"Context from source materials:\n{context_str}\n\nGenerate the product roadmap."}
        ]
    )

    roadmap = message.content[0].text

    # Save
    OUTPUT_DIR.mkdir(exist_ok=True)
    (OUTPUT_DIR / "master_roadmap.md").write_text(roadmap)

    return roadmap


def format_for_persona(persona: str, master_roadmap: Optional[str] = None) -> str:
    """Format roadmap for specific persona"""
    validate_api_keys()

    if not master_roadmap:
        roadmap_path = OUTPUT_DIR / "master_roadmap.md"
        if not roadmap_path.exists():
            console.print("[red]Error: Master roadmap not found. Run 'generate' first.")
            raise typer.Exit(1)
        master_roadmap = roadmap_path.read_text()

    # Load persona prompt
    persona_prompt = load_prompt(f"personas/{persona}.md")

    # Call Claude
    import httpx
    client = anthropic.Anthropic(
        api_key=ANTHROPIC_API_KEY,
        http_client=httpx.Client(verify=False)  # Disable SSL verification
    )
    message = client.messages.create(
        model="claude-opus-4-5-20251101",
        max_tokens=8000,
        system=persona_prompt,
        messages=[
            {"role": "user", "content": f"Master Roadmap:\n\n{master_roadmap}\n\nReformat this roadmap for the {persona} audience."}
        ]
    )

    formatted = message.content[0].text
    (OUTPUT_DIR / f"{persona}_roadmap.md").write_text(formatted)

    return formatted


# ========== SECTION 7.5: QUESTIONS & DECISIONS STORAGE ==========

def load_questions() -> List[Dict]:
    """Load all questions from storage."""
    questions_file = DATA_DIR / "questions" / "questions.json"
    if not questions_file.exists():
        return []

    with open(questions_file, 'r') as f:
        data = json.load(f)
    return data.get("questions", [])


def save_questions(questions: List[Dict]):
    """Save questions to storage."""
    questions_file = DATA_DIR / "questions" / "questions.json"
    questions_file.parent.mkdir(parents=True, exist_ok=True)

    # Update metadata
    from collections import Counter
    status_counts = Counter(q["status"] for q in questions)

    data = {
        "questions": questions,
        "metadata": {
            "last_updated": datetime.now().isoformat(),
            "total_pending": status_counts.get("pending", 0),
            "total_answered": status_counts.get("answered", 0),
            "total_deferred": status_counts.get("deferred", 0),
            "total_obsolete": status_counts.get("obsolete", 0)
        }
    }

    with open(questions_file, 'w') as f:
        json.dump(data, f, indent=2)


def load_answers() -> List[Dict]:
    """Load all answers from storage."""
    answers_file = DATA_DIR / "questions" / "answers.json"
    if not answers_file.exists():
        return []

    with open(answers_file, 'r') as f:
        data = json.load(f)
    return data.get("answers", [])


def save_answers(answers: List[Dict]):
    """Save answers to storage."""
    answers_file = DATA_DIR / "questions" / "answers.json"
    answers_file.parent.mkdir(parents=True, exist_ok=True)

    data = {
        "answers": answers,
        "metadata": {
            "last_updated": datetime.now().isoformat(),
            "total_answers": len(answers)
        }
    }

    with open(answers_file, 'w') as f:
        json.dump(data, f, indent=2)


def load_decisions() -> List[Dict]:
    """Load all decisions from storage."""
    decisions_file = DATA_DIR / "questions" / "decisions.json"
    if not decisions_file.exists():
        return []

    with open(decisions_file, 'r') as f:
        data = json.load(f)
    return data.get("decisions", [])


def save_decisions(decisions: List[Dict]):
    """Save decisions to storage."""
    decisions_file = DATA_DIR / "questions" / "decisions.json"
    decisions_file.parent.mkdir(parents=True, exist_ok=True)

    # Update metadata
    from collections import Counter
    status_counts = Counter(d["status"] for d in decisions)

    data = {
        "decisions": decisions,
        "metadata": {
            "last_updated": datetime.now().isoformat(),
            "total_decisions": len(decisions),
            "active_decisions": status_counts.get("active", 0),
            "superseded_decisions": status_counts.get("superseded", 0),
            "revisiting_decisions": status_counts.get("revisiting", 0)
        }
    }

    with open(decisions_file, 'w') as f:
        json.dump(data, f, indent=2)


# ========== SECTION 7.6: ARCHITECTURE ALIGNMENT ==========

# Architecture document paths
ARCHITECTURE_PATHS = [
    "materials/engineering/architecture",
    "materials/engineering/tech-specs",
]

MAX_TOKENS_PER_DOC = 200000  # Increased to handle large enterprise architecture docs
MAX_TOTAL_TOKENS = 200000    # Claude Opus 4.5 has 200K context window


def load_architecture_documents(selected_files: Optional[List[str]] = None) -> tuple[List[Dict], Dict]:
    """
    Load full architecture documents (not chunked) for alignment analysis.

    Args:
        selected_files: Optional list of file paths to load. If None, loads all files within budget.

    Returns:
        Tuple of (loaded_documents, metadata) where metadata includes skipped files info
    """
    import os

    enc = tiktoken.get_encoding("cl100k_base")
    documents = []
    skipped = []
    total_tokens = 0

    for base_path in ARCHITECTURE_PATHS:
        path = Path(base_path)
        if not path.exists():
            continue

        for file_path in path.rglob("*"):
            if file_path.suffix not in [".md", ".txt", ".rst"]:
                continue

            # Skip if not in selected files
            if selected_files is not None and str(file_path) not in selected_files:
                continue

            try:
                content = file_path.read_text(encoding='utf-8')
            except Exception as e:
                console.print(f"[yellow]Could not read {file_path}: {e}")
                skipped.append({
                    "path": str(file_path),
                    "name": file_path.name,
                    "reason": f"Read error: {e}",
                    "token_count": 0
                })
                continue

            token_count = len(enc.encode(content))

            # Skip very large docs
            if token_count > MAX_TOKENS_PER_DOC:
                console.print(f"[yellow]Skipping {file_path.name} ({token_count} tokens > {MAX_TOKENS_PER_DOC})")
                skipped.append({
                    "path": str(file_path),
                    "name": file_path.name,
                    "reason": f"Too large ({token_count:,} tokens > {MAX_TOKENS_PER_DOC:,})",
                    "token_count": token_count
                })
                continue

            # Check total budget
            if total_tokens + token_count > MAX_TOTAL_TOKENS:
                console.print(f"[yellow]Token budget reached at {total_tokens} tokens, stopping")
                skipped.append({
                    "path": str(file_path),
                    "name": file_path.name,
                    "reason": f"Budget exceeded (would be {total_tokens + token_count:,} > {MAX_TOTAL_TOKENS:,})",
                    "token_count": token_count
                })
                continue

            # Extract key components
            key_components = extract_components_from_doc(content)

            # Determine doc type
            if "architecture" in str(file_path).lower():
                doc_type = "architecture"
            elif "spec" in str(file_path).lower():
                doc_type = "tech-spec"
            else:
                doc_type = "design-doc"

            # Extract title
            title = extract_doc_title(content, file_path)

            # Get file modification date
            modified_time = os.path.getmtime(file_path)
            last_updated = datetime.fromtimestamp(modified_time).isoformat()

            documents.append({
                "id": f"doc_arch_{len(documents):03d}",
                "path": str(file_path),
                "title": title,
                "doc_type": doc_type,
                "content": content,
                "token_count": token_count,
                "key_components": key_components,
                "last_updated": last_updated,
                "loaded_at": datetime.now().isoformat()
            })

            total_tokens += token_count

    metadata = {
        "total_tokens": total_tokens,
        "loaded_count": len(documents),
        "skipped_count": len(skipped),
        "skipped_files": skipped
    }

    return documents, metadata


def scan_architecture_documents() -> List[Dict]:
    """
    Scan all architecture documents and return metadata without loading full content.
    Useful for document selection UI.
    """
    import os

    enc = tiktoken.get_encoding("cl100k_base")
    available_docs = []

    for base_path in ARCHITECTURE_PATHS:
        path = Path(base_path)
        if not path.exists():
            continue

        for file_path in path.rglob("*"):
            if file_path.suffix not in [".md", ".txt", ".rst"]:
                continue

            try:
                content = file_path.read_text(encoding='utf-8')
                token_count = len(enc.encode(content))

                # Extract title
                title = extract_doc_title(content, file_path)

                # Get file info
                file_size = file_path.stat().st_size
                modified_time = os.path.getmtime(file_path)

                available_docs.append({
                    "path": str(file_path),
                    "name": file_path.name,
                    "title": title,
                    "token_count": token_count,
                    "file_size": file_size,
                    "last_modified": datetime.fromtimestamp(modified_time).isoformat(),
                    "too_large": token_count > MAX_TOKENS_PER_DOC,
                })
            except Exception as e:
                console.print(f"[yellow]Could not scan {file_path}: {e}")
                continue

    # Sort by token count (smaller first)
    available_docs.sort(key=lambda x: x["token_count"])

    return available_docs


def extract_components_from_doc(content: str) -> List[str]:
    """Extract key component names from architecture document."""
    import re

    components = set()

    # Look for common patterns
    patterns = [
        r'##\s+([A-Z][a-zA-Z\s]+(?:Service|Engine|API|System|Module|Component))',
        r'\*\*([A-Z][a-zA-Z\s]+(?:Service|Engine|API|System|Module|Component))\*\*',
        r'`([A-Z][a-zA-Z]+(?:Service|Engine|API))`',
    ]

    for pattern in patterns:
        matches = re.findall(pattern, content)
        components.update(m.strip() for m in matches)

    return sorted(list(components))[:20]  # Limit to top 20


def extract_doc_title(content: str, file_path: Path) -> str:
    """Extract document title from content or filename."""
    # Try to find # Title
    lines = content.split('\n')
    for line in lines[:10]:
        if line.startswith('# '):
            return line[2:].strip()

    # Fall back to filename
    return file_path.stem.replace('-', ' ').replace('_', ' ').title()


def format_architecture_docs(arch_docs: List[Dict]) -> str:
    """Format architecture documents for Claude prompt."""
    output = []

    for doc in arch_docs:
        output.append(f"### {doc['title']}")
        output.append(f"**Type:** {doc['doc_type']}")
        output.append(f"**Path:** {doc['path']}")

        if doc.get('key_components'):
            output.append(f"**Key Components:** {', '.join(doc['key_components'][:10])}")

        output.append("\n**Content:**\n")
        output.append(doc['content'])
        output.append("\n---\n")

    return "\n".join(output)


def parse_roadmap_for_analysis(roadmap_content: str) -> Dict:
    """
    Parse roadmap markdown to extract items for analysis.
    Returns structured roadmap data.
    """
    import re

    items = []

    # Simple heuristic: Look for items in roadmap sections
    # This is a basic implementation - adjust based on actual roadmap format

    lines = roadmap_content.split('\n')
    current_horizon = "unknown"
    current_item = None

    for line in lines:
        # Detect horizon sections
        if re.match(r'^##\s+(Now|Next|Later|Future)', line, re.IGNORECASE):
            match = re.match(r'^##\s+(Now|Next|Later|Future)', line, re.IGNORECASE)
            current_horizon = match.group(1).lower()
            continue

        # Detect items (lines starting with ###, ####, or bullet points with bold)
        if line.startswith('### ') or line.startswith('#### '):
            if current_item:
                items.append(current_item)

            title = line.lstrip('#').strip()
            current_item = {
                "name": title,
                "description": "",
                "horizon": current_horizon
            }
        elif current_item and line.strip():
            # Accumulate description
            current_item["description"] += line + " "

    # Add last item
    if current_item:
        items.append(current_item)

    return {
        "items": items,
        "total_items": len(items)
    }


def generate_architecture_alignment(
    roadmap: Dict,
    architecture_docs: List[Dict],
    use_opus: bool = True
) -> Dict:
    """
    Generate architecture alignment analysis.
    Returns analysis with assessments, risks, and engineering questions.
    """
    validate_api_keys()

    # Format architecture docs
    arch_context = format_architecture_docs(architecture_docs)

    # Format roadmap items
    roadmap_items = []
    for item in roadmap.get("items", []):
        roadmap_items.append(
            f"- **{item['name']}** ({item['horizon']})\n"
            f"  Description: {item['description'][:200]}..."
        )
    roadmap_str = "\n".join(roadmap_items)

    # Build prompt
    prompt = f"""You are a technical architect analyzing alignment between a product roadmap and system architecture.

## Your Task

For each roadmap item, assess whether the current architecture supports it and identify gaps, risks, and required changes.

## Architecture Context

The following are the FULL architecture and technical design documents for the system:

{arch_context}

## Roadmap Items to Analyze

{roadmap_str}

## Analysis Instructions

For EACH roadmap item, provide:

### 1. Alignment Assessment

- **Architecture Supports**: Does the current architecture support this item?
  - `full` — Architecture fully supports, no changes needed
  - `partial` — Some support exists, but changes required
  - `no` — Architecture does not support, significant work needed
  - `unknown` — Cannot determine from available docs

- **Confidence**: How confident is this assessment?
  - `high` — Clear documentation exists
  - `medium` — Some inference required
  - `low` — Significant gaps in documentation

### 2. Supporting Components

List the existing components/services that enable this roadmap item.

### 3. Required Changes

For each change needed:
- **Component**: Which component needs to change
- **Change Type**: `new` (build new), `modify` (change existing), `deprecate` (remove), `migrate` (move/transform)
- **Description**: What specifically needs to change
- **Effort**: T-shirt size (S/M/L/XL)
- **Risk Level**: low/medium/high
- **Blocking**: Does this block the roadmap item from starting?

### 4. Technical Risks

For each risk:
- **Risk**: Description of the technical risk
- **Severity**: critical/high/medium/low
- **Likelihood**: high/medium/low
- **Mitigation**: How could this be mitigated
- **Owner**: Who should address this

### 5. Dependencies

Technical dependencies:
- **Prerequisite Work**: What must be done first (technically)
- **Enables**: What does completing this unblock (technically)
- **External Dependencies**: Third-party or cross-team dependencies

### 6. Engineering Questions

Generate 2-5 specific questions for engineering about this roadmap item. Questions should:
- Be specific and actionable
- Reference specific components or systems when relevant
- Help clarify feasibility, approach, or risk
- Be answerable by engineering leadership or architects

Question format:
```json
{{
  "question": "Specific question text",
  "category": "feasibility|architecture|capacity|timeline|dependency|risk",
  "priority": "critical|high|medium|low",
  "context": "Why this question matters",
  "component": "Relevant component if applicable"
}}
```

## Output Format

Return JSON:

```json
{{
  "assessments": [
    {{
      "roadmap_item": "Item name",
      "roadmap_item_description": "Full description",
      "horizon": "now|next|later|future",

      "architecture_supports": "full|partial|no|unknown",
      "confidence": "high|medium|low",
      "summary": "2-3 sentence summary of alignment status",

      "supporting_components": ["Component1", "Component2"],

      "required_changes": [
        {{
          "component": "Component name",
          "change_type": "new|modify|deprecate|migrate",
          "description": "What needs to change",
          "effort": "S|M|L|XL",
          "risk_level": "low|medium|high",
          "blocking": true|false
        }}
      ],

      "technical_risks": [
        {{
          "risk": "Risk description",
          "severity": "critical|high|medium|low",
          "likelihood": "high|medium|low",
          "mitigation": "Mitigation approach",
          "owner": "Team or role"
        }}
      ],

      "dependencies": {{
        "prerequisite_work": ["Item1", "Item2"],
        "enables": ["Item3", "Item4"],
        "external": ["External dependency 1"]
      }},

      "questions": [
        {{
          "question": "Question text",
          "category": "feasibility",
          "priority": "high",
          "context": "Why this matters",
          "component": "Relevant component"
        }}
      ]
    }}
  ],

  "cross_cutting_concerns": {{
    "architectural_gaps": ["Gap 1", "Gap 2"],
    "systemic_risks": ["Risk 1", "Risk 2"],
    "recommended_adrs": ["ADR topic 1", "ADR topic 2"],
    "sequencing_recommendations": "Narrative about technical sequencing"
  }}
}}
```

## Important Notes

1. **Be specific** — Reference actual components, APIs, and systems from the docs
2. **Surface unknowns** — If docs don't cover something, say so
3. **Think dependencies** — Technical work often has ordering constraints
4. **Consider scale** — What works for MVP may not work at scale
5. **Flag debt** — Note if roadmap items will create or require addressing tech debt

Now analyze the alignment between the roadmap and architecture."""

    # Call Claude
    import httpx
    model = "claude-opus-4-20250514" if use_opus else "claude-sonnet-4-20250514"

    client = anthropic.Anthropic(
        api_key=ANTHROPIC_API_KEY,
        http_client=httpx.Client(verify=False)
    )

    message = client.messages.create(
        model=model,
        max_tokens=8000,
        messages=[{"role": "user", "content": prompt}]
    )

    # Parse JSON response
    response_text = message.content[0].text

    # Extract JSON from response (may be wrapped in ```json```)
    if "```json" in response_text:
        json_start = response_text.find("```json") + 7
        json_end = response_text.rfind("```")
        response_text = response_text[json_start:json_end].strip()

    try:
        analysis = json.loads(response_text)
    except json.JSONDecodeError as e:
        console.print(f"[red]Failed to parse Claude response as JSON: {e}")
        console.print(f"[dim]Response:\n{response_text[:500]}...")
        raise

    return analysis


def extract_engineering_questions_from_alignment(analysis: Dict) -> List[Dict]:
    """Extract engineering questions from alignment analysis."""
    questions = []

    for assessment in analysis.get("assessments", []):
        roadmap_item = assessment.get("roadmap_item", "Unknown")

        for q in assessment.get("questions", []):
            question_id = f"q_eng_arch_{len(questions):03d}"
            questions.append({
                "id": question_id,
                "question": q["question"],
                "audience": "engineering",
                "category": q.get("category", "architecture"),
                "priority": q.get("priority", "medium"),
                "context": f"From architecture alignment analysis for: {roadmap_item}. {q.get('context', '')}",
                "source": "architecture_alignment",
                "source_type": "architecture_alignment",
                "related_roadmap_items": [roadmap_item],
                "related_component": q.get("component"),
                "status": "pending",
                "created_at": datetime.now().isoformat(),
                "created_from_synthesis": None
            })

    return questions


def add_architecture_questions_to_system(questions: List[Dict]) -> int:
    """Add architecture-generated questions to the Open Questions system."""
    existing = load_questions()

    # Avoid duplicates (simple check on question text similarity)
    existing_texts = {q["question"].lower() for q in existing}

    new_questions = []
    for q in questions:
        if q["question"].lower() not in existing_texts:
            new_questions.append(q)

    if new_questions:
        save_questions(existing + new_questions)

    return len(new_questions)


def save_alignment_analysis(analysis: Dict, output_path: Path = None):
    """Save alignment analysis to JSON file."""
    if output_path is None:
        output_path = OUTPUT_DIR / "architecture-alignment.json"

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w') as f:
        json.dump(analysis, f, indent=2)


def load_alignment_analysis(analysis_path: Path = None) -> Dict:
    """Load alignment analysis from JSON file."""
    if analysis_path is None:
        analysis_path = OUTPUT_DIR / "architecture-alignment.json"

    if not analysis_path.exists():
        return {}

    with open(analysis_path, 'r') as f:
        return json.load(f)


def format_alignment_report(analysis: Dict) -> str:
    """Format alignment analysis as markdown report."""
    lines = [
        "# Architecture Alignment Report",
        f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
        "## Executive Summary\n"
    ]

    assessments = analysis.get("assessments", [])
    full_support = len([a for a in assessments if a.get("architecture_supports") == "full"])
    partial_support = len([a for a in assessments if a.get("architecture_supports") == "partial"])
    no_support = len([a for a in assessments if a.get("architecture_supports") == "no"])

    lines.append(f"- **Items Analyzed:** {len(assessments)}")
    lines.append(f"- **Full Support:** {full_support} ({full_support/len(assessments)*100:.0f}%)" if assessments else "")
    lines.append(f"- **Partial Support:** {partial_support} ({partial_support/len(assessments)*100:.0f}%)" if assessments else "")
    lines.append(f"- **No Support:** {no_support} ({no_support/len(assessments)*100:.0f}%)" if assessments else "")
    lines.append("\n---\n")

    # Group by support level
    for support_level, icon in [("full", "🟢"), ("partial", "⚠️"), ("no", "❌")]:
        level_assessments = [a for a in assessments if a.get("architecture_supports") == support_level]

        if not level_assessments:
            continue

        lines.append(f"## {icon} {support_level.title()} Support\n")

        for assessment in level_assessments:
            lines.append(f"### {assessment['roadmap_item']}")
            lines.append(f"- **Horizon:** {assessment.get('horizon', 'N/A')}")
            lines.append(f"- **Confidence:** {assessment.get('confidence', 'N/A')}")
            lines.append(f"- **Summary:** {assessment.get('summary', 'N/A')}\n")

            if assessment.get("supporting_components"):
                lines.append("**Supporting Components:**")
                for comp in assessment["supporting_components"]:
                    lines.append(f"- {comp}")
                lines.append("")

            if assessment.get("required_changes"):
                lines.append("**Required Changes:**")
                for change in assessment["required_changes"]:
                    blocking = "🚫 BLOCKING" if change.get("blocking") else ""
                    lines.append(f"- **{change['component']}** ({change['change_type']}, {change['effort']}) — {change['description']} {blocking}")
                lines.append("")

            if assessment.get("technical_risks"):
                lines.append("**Technical Risks:**")
                for risk in assessment["technical_risks"]:
                    lines.append(f"- [{risk['severity']}] {risk['risk']}")
                    lines.append(f"  - Mitigation: {risk['mitigation']}")
                lines.append("")

            lines.append("---\n")

    # Cross-cutting concerns
    cross_cutting = analysis.get("cross_cutting_concerns", {})
    if cross_cutting:
        lines.append("## Cross-Cutting Concerns\n")

        if cross_cutting.get("architectural_gaps"):
            lines.append("### Architectural Gaps")
            for gap in cross_cutting["architectural_gaps"]:
                lines.append(f"- {gap}")
            lines.append("")

        if cross_cutting.get("systemic_risks"):
            lines.append("### Systemic Risks")
            for risk in cross_cutting["systemic_risks"]:
                lines.append(f"- {risk}")
            lines.append("")

        if cross_cutting.get("recommended_adrs"):
            lines.append("### Recommended ADRs")
            for adr in cross_cutting["recommended_adrs"]:
                lines.append(f"- {adr}")
            lines.append("")

        if cross_cutting.get("sequencing_recommendations"):
            lines.append("### Sequencing Recommendations")
            lines.append(cross_cutting["sequencing_recommendations"])
            lines.append("")

    return "\n".join(lines)


# ========== SECTION 7.7: COMPETITIVE INTELLIGENCE ==========

# Storage paths
COMPETITIVE_DIR = OUTPUT_DIR / "competitive"
COMPETITOR_DEVELOPMENTS_FILE = COMPETITIVE_DIR / "developments.json"
ANALYST_ASSESSMENTS_FILE = COMPETITIVE_DIR / "assessments.json"
ANALYST_DOCS_PATH = Path("materials/external-analyst")


def load_competitor_developments() -> List[Dict]:
    """Load all competitor developments."""
    if not COMPETITOR_DEVELOPMENTS_FILE.exists():
        return []
    return json.loads(COMPETITOR_DEVELOPMENTS_FILE.read_text())


def save_competitor_developments(developments: List[Dict]) -> None:
    """Save competitor developments."""
    COMPETITIVE_DIR.mkdir(parents=True, exist_ok=True)
    COMPETITOR_DEVELOPMENTS_FILE.write_text(json.dumps(developments, indent=2))


def add_competitor_development(
    competitor: str,
    development_type: str,
    title: str,
    description: str,
    source_url: str,
    announced_date: str
) -> Dict:
    """Add a new competitor development."""
    developments = load_competitor_developments()

    dev_id = f"comp_{datetime.now().strftime('%Y%m%d%H%M%S')}"

    development = {
        "id": dev_id,
        "competitor": competitor,
        "development_type": development_type,
        "title": title,
        "description": description,
        "source_url": source_url,
        "announced_date": announced_date,
        "created_at": datetime.now().isoformat()
    }

    developments.append(development)
    save_competitor_developments(developments)

    return development


def get_competitor_development(dev_id: str) -> Optional[Dict]:
    """Get a specific competitor development by ID."""
    developments = load_competitor_developments()
    for dev in developments:
        if dev["id"] == dev_id:
            return dev
    return None


def load_analyst_assessments() -> List[Dict]:
    """Load all analyst assessments."""
    if not ANALYST_ASSESSMENTS_FILE.exists():
        return []
    return json.loads(ANALYST_ASSESSMENTS_FILE.read_text())


def save_analyst_assessment(assessment: Dict) -> None:
    """Save an analyst assessment."""
    assessments = load_analyst_assessments()
    assessments.append(assessment)
    COMPETITIVE_DIR.mkdir(parents=True, exist_ok=True)
    ANALYST_ASSESSMENTS_FILE.write_text(json.dumps(assessments, indent=2))


def load_analyst_documents() -> List[Dict]:
    """
    Load external analyst research documents for market context.
    These provide the analytical lens for competitive assessments.
    """
    import os

    if not ANALYST_DOCS_PATH.exists():
        return []

    enc = tiktoken.get_encoding("cl100k_base")
    documents = []

    for file_path in ANALYST_DOCS_PATH.rglob("*"):
        if file_path.suffix not in [".md", ".txt", ".rst", ".pdf"]:
            continue

        try:
            content = file_path.read_text(encoding='utf-8')
            token_count = len(enc.encode(content))

            documents.append({
                "path": str(file_path),
                "name": file_path.name,
                "content": content,
                "token_count": token_count
            })
        except Exception as e:
            console.print(f"[yellow]Could not read {file_path}: {e}")
            continue

    return documents


def format_analyst_documents_for_assessment(docs: List[Dict]) -> str:
    """Format analyst documents for inclusion in assessment prompt."""
    if not docs:
        return "No analyst research documents available."

    formatted = []
    for doc in docs:
        formatted.append(f"## {doc['name']}\n\n{doc['content']}\n")

    return "\n".join(formatted)


def extract_roadmap_item_names(roadmap_content: str) -> List[str]:
    """Extract all roadmap item names from roadmap markdown."""
    import re

    # Look for markdown headings and bullet points that look like roadmap items
    patterns = [
        r'###\s+(.+)',  # H3 headings
        r'##\s+(.+)',   # H2 headings
        r'\*\*(.+?)\*\*',  # Bold text
        r'^\s*[-•]\s*\*\*(.+?)\*\*',  # Bullet with bold
    ]

    items = set()
    for pattern in patterns:
        matches = re.findall(pattern, roadmap_content, re.MULTILINE)
        items.update(m.strip() for m in matches)

    return list(items)


def validate_no_novel_concepts(analysis: Dict, roadmap_content: str) -> List[str]:
    """
    Validate that the analysis doesn't introduce concepts not in the roadmap.
    Returns list of warnings if potential novel concepts detected.
    """
    warnings = []
    roadmap_lower = roadmap_content.lower()

    # Check strengths reference real roadmap items
    for strength in analysis.get("roadmap_strengths", []):
        item = strength.get("roadmap_item", "")
        if item and item.lower() not in roadmap_lower:
            warnings.append(f"Strength references unknown roadmap item: {item}")

    # Check timing assessments reference real items
    for timing in analysis.get("timing_assessments", []):
        item = timing.get("roadmap_item", "")
        if item and item.lower() not in roadmap_lower:
            warnings.append(f"Timing assessment references unknown roadmap item: {item}")

    # Check gaps don't suggest new concepts
    for gap in analysis.get("roadmap_gaps", []):
        gap_desc = gap.get("gap_description", "").lower()
        # Flag if gap description contains suggestive language
        suggestive_phrases = ["should add", "could implement", "needs to", "must build"]
        for phrase in suggestive_phrases:
            if phrase in gap_desc:
                warnings.append(f"Gap description may suggest new concepts: {gap_desc[:50]}...")

    return warnings


def add_strategic_questions_to_system(questions: List[Dict], development: Dict) -> int:
    """
    Add strategic questions from analyst assessment to Open Questions system.
    These are questions raised by the assessment, NOT recommendations.
    """
    existing = load_questions()
    added_count = 0

    for q in questions:
        question_obj = {
            "id": f"q_competitive_{datetime.now().strftime('%Y%m%d%H%M%S')}_{added_count:03d}",
            "question": q.get("question", ""),
            "audience": "leadership",  # Strategic questions go to leadership
            "category": q.get("question_type", "positioning"),
            "priority": "high",  # Competitive questions are high priority
            "context": f"Raised by analyst assessment of: {development.get('competitor')} - {development.get('title')}. {q.get('context', '')}",
            "source": f"competitive_analysis_{development.get('id')}",
            "related_roadmap_items": q.get("relevant_roadmap_items", []),
            "status": "pending",
            "created_at": datetime.now().isoformat(),
        }
        existing.append(question_obj)
        added_count += 1

    if added_count > 0:
        save_questions(existing)

    return added_count


def generate_analyst_assessment(
    development: Dict,
    use_opus: bool = True
) -> Dict:
    """
    Generate an analyst assessment of competitor development against roadmap.

    CRITICAL: This is an ASSESSMENT, not a strategy document.
    - The roadmap is the source of truth
    - No novel concepts are introduced
    - Claude acts as an industry analyst, not a strategist
    """
    validate_api_keys()

    # 1. Load analyst documents for market context
    analyst_docs = load_analyst_documents()
    analyst_context = format_analyst_documents_for_assessment(analyst_docs)

    # 2. Load current roadmap (source of truth)
    roadmap_file = OUTPUT_DIR / "master_roadmap.md"
    if not roadmap_file.exists():
        raise FileNotFoundError("Roadmap not found. Generate a roadmap first.")

    roadmap_content = roadmap_file.read_text()

    # 3. Build prompt with CRITICAL constraints
    prompt = f"""You are a senior industry analyst at a research firm covering this market.

## Your Role

You have been asked to write an objective analyst assessment of how a competitor's development impacts a company's roadmap.

## CRITICAL CONSTRAINTS

1. **The roadmap is fixed** — You are assessing impact on the roadmap AS IT EXISTS
2. **No recommendations** — You do NOT suggest changes, new features, or strategy
3. **No novel concepts** — You do NOT introduce ideas not already in the roadmap
4. **Analyst objectivity** — You write as an external analyst, not an employee
5. **Evidence-based** — Every claim must reference a specific roadmap item or analyst research
6. **Questions, not answers** — You raise strategic questions but do not answer them

## What You MUST Do

- Reference specific roadmap items by name
- Quote or cite analyst research for market context
- Identify what the roadmap addresses and what it doesn't
- Assess timing implications for existing roadmap items
- Raise questions for decision-makers to consider

## What You MUST NOT Do

- Suggest new features or capabilities
- Recommend roadmap changes
- Propose technical approaches not in the roadmap
- Create strategy or action plans
- Speculate beyond the evidence

---

## ANALYST RESEARCH CONTEXT

Use this analyst research to understand market dynamics, customer expectations, and competitive landscape. Quote directly when relevant.

{analyst_context}

---

## THE ROADMAP (Source of Truth)

This is what the company IS building. Your assessment must be grounded in this.

{roadmap_content}

---

## COMPETITOR DEVELOPMENT TO ASSESS

**Competitor:** {development.get('competitor')}
**Development Type:** {development.get('development_type')}
**Title:** {development.get('title')}
**Announced:** {development.get('announced_date')}

**Description:**
{development.get('description')}

**Source:** {development.get('source_url')}

---

## OUTPUT FORMAT

Return JSON with this structure:

{{
  "headline": "IMPACT_LEVEL: One-line headline",
  "executive_summary": "3-5 sentence summary",

  "market_context": {{
    "relevant_trends": ["Trend 1", "Trend 2"],
    "market_direction": "Where market is heading",
    "customer_expectations": "What customers expect",
    "competitive_landscape": "Current dynamics",
    "analyst_quotes": ["Direct quote from analyst research 1", "Direct quote 2"]
  }},

  "overall_impact": "significant|moderate|minimal|none",
  "impact_timeline": "immediate|near_term|medium_term|long_term",
  "confidence": "high|medium|low",

  "roadmap_strengths": [
    {{
      "roadmap_item": "Exact item name from roadmap",
      "horizon": "now|next|later|future",
      "how_it_addresses": "How this addresses the development",
      "coverage_level": "full|partial|tangential",
      "timing_adequacy": "ahead|on_pace|behind|unclear",
      "source_quote": "Quote from roadmap about this item"
    }}
  ],

  "roadmap_gaps": [
    {{
      "gap_description": "What the gap is (descriptive, not prescriptive)",
      "severity": "critical|significant|moderate|minor",
      "competitor_capability": "What competitor has",
      "roadmap_coverage": "What roadmap says or doesn't say",
      "is_acknowledged": true|false,
      "relevant_roadmap_items": ["Items that partially address"],
      "analyst_perspective": "What analyst research says about importance"
    }}
  ],

  "timing_assessments": [
    {{
      "roadmap_item": "Item name",
      "current_horizon": "now|next|later|future",
      "timing_implication": "more_urgent|less_relevant|unchanged|uncertain",
      "rationale": "Why this implication"
    }}
  ],

  "segment_implications": [
    {{
      "segment": "Segment name",
      "implication": "What this means",
      "roadmap_relevance": "How roadmap addresses",
      "risk_level": "high|medium|low"
    }}
  ],

  "competitive_position_assessment": "Narrative assessment grounded in roadmap and research",

  "strategic_questions": [
    {{
      "question": "The question raised",
      "question_type": "timing|investment|priority|scope|positioning",
      "context": "Why this question is raised",
      "relevant_roadmap_items": ["Related items"]
    }}
  ],

  "analyst_conclusion": "2-3 paragraph objective conclusion"
}}

Now write your analyst assessment."""

    # 4. Call Claude
    model = "claude-opus-4-20250514" if use_opus else "claude-sonnet-4-20250514"
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY, http_client=httpx.Client(verify=False))

    message = client.messages.create(
        model=model,
        max_tokens=6000,
        messages=[{"role": "user", "content": prompt}]
    )

    # 5. Parse response
    response_text = message.content[0].text

    # Extract JSON
    if "```json" in response_text:
        json_start = response_text.find("```json") + 7
        json_end = response_text.rfind("```")
        response_text = response_text[json_start:json_end].strip()

    try:
        analysis = json.loads(response_text)
    except json.JSONDecodeError as e:
        console.print(f"[red]Failed to parse Claude response as JSON: {e}")
        console.print(f"[dim]Response:\n{response_text[:500]}...")
        raise

    # 6. Validate no novel concepts
    warnings = validate_no_novel_concepts(analysis, roadmap_content)
    if warnings:
        console.print("[yellow]⚠️ Validation warnings:")
        for w in warnings:
            console.print(f"  - {w}")

    # 7. Build assessment object
    assessment = {
        "id": f"analysis_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "development_id": development["id"],
        "assessed_at": datetime.now().isoformat(),
        "roadmap_version": roadmap_file.stat().st_mtime,
        "analyst_docs_used": [d["path"] for d in analyst_docs],
        "development": development,  # Store reference to the development
        "analysis": analysis,
        "validation_warnings": warnings
    }

    # 8. Save assessment
    save_analyst_assessment(assessment)

    # 9. Add strategic questions to Open Questions
    strategic_questions = analysis.get("strategic_questions", [])
    added_count = add_strategic_questions_to_system(strategic_questions, development)

    console.print(f"[dim]Added {added_count} strategic questions to Open Questions[/dim]")

    return assessment


def format_analyst_assessment_markdown(assessment: Dict) -> str:
    """Format analyst assessment as markdown research note."""
    analysis = assessment["analysis"]
    development = assessment["development"]

    lines = [
        f"# Competitive Assessment: {development['competitor']} - {development['title']}",
        "",
        f"**Date:** {assessment['assessed_at'][:10]}",
        f"**Analyst:** Roadmap Synth Analyst Assessment",
        f"**Development Date:** {development['announced_date']}",
        f"**Source:** {development['source_url']}",
        "",
        "---",
        "",
        f"## {analysis['headline']}",
        "",
        "**Executive Summary**",
        "",
        analysis['executive_summary'],
        "",
        "---",
        "",
        "## Market Context",
        ""
    ]

    # Market context
    mc = analysis.get("market_context", {})
    if mc.get("market_direction"):
        lines.append(f"**Market Direction:** {mc['market_direction']}")
        lines.append("")

    if mc.get("customer_expectations"):
        lines.append(f"**Customer Expectations:** {mc['customer_expectations']}")
        lines.append("")

    if mc.get("analyst_quotes"):
        lines.append("**Analyst Research:**")
        lines.append("")
        for quote in mc["analyst_quotes"]:
            lines.append(f"> {quote}")
            lines.append("")

    # Roadmap strengths
    lines.append("---")
    lines.append("")
    lines.append("## Roadmap Strengths")
    lines.append("")

    for strength in analysis.get("roadmap_strengths", []):
        lines.append(f"### {strength['roadmap_item']} ({strength['horizon']} horizon)")
        lines.append(f"- **Coverage:** {strength['coverage_level']}")
        lines.append(f"- **Timing:** {strength['timing_adequacy']}")
        lines.append(f"- **Assessment:** {strength['how_it_addresses']}")
        if strength.get('source_quote'):
            lines.append(f"- **Roadmap:** \"{strength['source_quote']}\"")
        lines.append("")

    # Roadmap gaps
    lines.append("---")
    lines.append("")
    lines.append("## Roadmap Gaps")
    lines.append("")

    for gap in analysis.get("roadmap_gaps", []):
        lines.append(f"### {gap['gap_description']}")
        lines.append(f"- **Severity:** {gap['severity']}")
        lines.append(f"- **Competitor Capability:** {gap['competitor_capability']}")
        lines.append(f"- **Roadmap Coverage:** {gap['roadmap_coverage']}")
        if gap.get('analyst_perspective'):
            lines.append(f"- **Analyst Perspective:** {gap['analyst_perspective']}")
        lines.append("")

    # Timing assessments
    if analysis.get("timing_assessments"):
        lines.append("---")
        lines.append("")
        lines.append("## Timing Implications")
        lines.append("")
        lines.append("| Roadmap Item | Current Horizon | Implication | Rationale |")
        lines.append("|--------------|-----------------|-------------|-----------|")
        for timing in analysis["timing_assessments"]:
            lines.append(f"| {timing['roadmap_item']} | {timing['current_horizon']} | {timing['timing_implication']} | {timing['rationale']} |")
        lines.append("")

    # Competitive position
    lines.append("---")
    lines.append("")
    lines.append("## Competitive Position Assessment")
    lines.append("")
    lines.append(analysis.get('competitive_position_assessment', 'Not provided'))
    lines.append("")

    # Strategic questions
    lines.append("---")
    lines.append("")
    lines.append("## Strategic Questions Raised")
    lines.append("")
    lines.append("This assessment raises the following questions for leadership consideration:")
    lines.append("")

    for i, q in enumerate(analysis.get("strategic_questions", []), 1):
        lines.append(f"{i}. **[{q['question_type'].upper()}]** {q['question']}")
        lines.append(f"   - *Context:* {q['context']}")
        if q.get('relevant_roadmap_items'):
            lines.append(f"   - *Relevant items:* {', '.join(q['relevant_roadmap_items'])}")
        lines.append("")

    lines.append("**Note:** These questions are raised for leadership consideration. This assessment does not recommend specific answers.")
    lines.append("")

    # Analyst conclusion
    lines.append("---")
    lines.append("")
    lines.append("## Analyst Conclusion")
    lines.append("")
    lines.append(analysis.get('analyst_conclusion', 'Not provided'))
    lines.append("")

    # Footer
    lines.append("---")
    lines.append("")
    lines.append("*This assessment is an objective external analyst perspective based on the provided roadmap and analyst research. It does not recommend strategic actions.*")

    return "\n".join(lines)


# ========== SECTION 7.8: UNIFIED CONTEXT GRAPH ==========

# Graph storage path
GRAPH_PATH = DATA_DIR / "unified_graph"

# Authority hierarchy (lower number = higher authority)
AUTHORITY_LEVELS = {
    "decision": 1,        # Highest - overrides everything
    "answered_question": 2,
    "assessment": 3,
    "roadmap_item": 4,
    "gap": 5,
    "chunk": 6,
    "pending_question": 7  # Lowest
}


class UnifiedContextGraph:
    """
    Unified graph containing all knowledge types with authority hierarchy.
    """

    def __init__(self):
        self.graph = nx.DiGraph()
        self.node_indices = {
            "chunk": {},
            "decision": {},
            "question": {},
            "assessment": {},
            "roadmap_item": {},
            "gap": {},
        }

    def add_node(self, node_id: str, node_type: str, data: dict, embedding: Optional[List[float]] = None) -> None:
        """Add a node to the graph."""
        self.graph.add_node(
            node_id,
            node_type=node_type,
            data=data,
            embedding=embedding
        )
        self.node_indices[node_type][node_id] = data

    def add_edge(self, from_id: str, to_id: str, edge_type: str, weight: float = 1.0, metadata: dict = None) -> None:
        """Add an edge between nodes."""
        self.graph.add_edge(
            from_id,
            to_id,
            edge_type=edge_type,
            weight=weight,
            metadata=metadata or {}
        )

    def get_nodes_by_type(self, node_type: str) -> dict:
        """Get all nodes of a specific type."""
        return self.node_indices.get(node_type, {})

    def get_superseding_decision(self, chunk_id: str) -> Optional[dict]:
        """Get decision that supersedes a chunk, if any."""
        for neighbor in self.graph.predecessors(chunk_id):
            edge = self.graph.edges.get((neighbor, chunk_id))
            if edge and edge.get("edge_type") == "OVERRIDES":
                return self.node_indices["decision"].get(neighbor)
        return None

    def save(self) -> None:
        """Save graph to disk."""
        GRAPH_PATH.mkdir(parents=True, exist_ok=True)

        # Save graph structure
        graph_data = nx.node_link_data(self.graph)
        (GRAPH_PATH / "graph.json").write_text(json.dumps(graph_data, indent=2, default=str))

        # Save node indices
        for node_type, nodes in self.node_indices.items():
            (GRAPH_PATH / f"{node_type}_nodes.json").write_text(
                json.dumps(nodes, indent=2, default=str)
            )

    @classmethod
    def load(cls) -> 'UnifiedContextGraph':
        """Load graph from disk."""
        graph = cls()

        if not GRAPH_PATH.exists():
            return graph

        # Load graph structure
        graph_file = GRAPH_PATH / "graph.json"
        if graph_file.exists():
            graph_data = json.loads(graph_file.read_text())
            graph.graph = nx.node_link_graph(graph_data)

        # Load node indices
        for node_type in ["chunk", "decision", "question", "assessment", "roadmap_item", "gap"]:
            node_file = GRAPH_PATH / f"{node_type}_nodes.json"
            if node_file.exists():
                nodes = json.loads(node_file.read_text())
                graph.node_indices[node_type] = nodes

        return graph


def integrate_decision_to_graph(graph: UnifiedContextGraph, decision: dict) -> None:
    """Integrate a decision into the graph with embedding for semantic matching."""

    # Generate embedding for decision
    decision_text = f"{decision.get('decision', '')}. {decision.get('rationale', '')}"

    if decision_text.strip():
        embedding = generate_embeddings([decision_text])[0]
    else:
        embedding = None

    # Add decision node
    graph.add_node(
        decision["id"],
        "decision",
        decision,
        embedding=embedding
    )

    # Link to resolved question
    if decision.get("question_id"):
        graph.add_edge(
            decision["id"],
            decision["question_id"],
            edge_type="RESOLVES",
            weight=1.0
        )

        # Update question status if it exists
        if decision["question_id"] in graph.node_indices["question"]:
            question = graph.node_indices["question"][decision["question_id"]]
            question["status"] = "answered"
            question["answered_by_decision"] = decision["id"]

    # Find and mark conflicting chunks (simplified - based on related_roadmap_items)
    if decision.get("related_roadmap_items"):
        for item_name in decision["related_roadmap_items"]:
            # Find roadmap item
            for ri_id, ri_data in graph.node_indices["roadmap_item"].items():
                if ri_data.get("name", "").lower() == item_name.lower():
                    # Link decision to roadmap item
                    graph.add_edge(
                        decision["id"],
                        ri_id,
                        edge_type="IMPACTS",
                        weight=1.0
                    )


def integrate_assessment_to_graph(graph: UnifiedContextGraph, assessment: dict, assessment_type: str) -> None:
    """Integrate an assessment into the graph with gaps and questions."""

    # Add assessment node
    summary = assessment.get("analysis", {}).get("executive_summary", "")[:200] if assessment_type == "competitive" else str(assessment)[:200]

    graph.add_node(
        assessment["id"],
        "assessment",
        {
            "id": assessment["id"],
            "type": assessment_type,
            "summary": summary,
            "data": assessment
        },
        embedding=None
    )

    # Extract and link gaps
    gaps = []
    if assessment_type == "architecture":
        gaps = assessment.get("analysis", {}).get("roadmap_gaps", [])
    elif assessment_type == "competitive":
        gaps = assessment.get("analysis", {}).get("roadmap_gaps", [])

    for i, gap_data in enumerate(gaps):
        gap_id = f"gap_{assessment['id']}_{i}"
        gap_desc = gap_data.get("gap_description", gap_data.get("gap", gap_data.get("description", "")))

        graph.add_node(
            gap_id,
            "gap",
            {
                "id": gap_id,
                "description": gap_desc,
                "severity": gap_data.get("severity", "medium"),
                "type": assessment_type,
                "identified_by": assessment["id"]
            },
            embedding=None
        )

        graph.add_edge(
            assessment["id"],
            gap_id,
            edge_type="IDENTIFIES_GAP",
            weight=0.9
        )


def integrate_question_to_graph(graph: UnifiedContextGraph, question: dict) -> None:
    """Integrate a question into the graph."""

    graph.add_node(
        question["id"],
        "question",
        question,
        embedding=None
    )

    # Link to related roadmap items
    if question.get("related_roadmap_items"):
        for item_name in question["related_roadmap_items"]:
            for ri_id, ri_data in graph.node_indices["roadmap_item"].items():
                if ri_data.get("name", "").lower() == item_name.lower():
                    graph.add_edge(
                        question["id"],
                        ri_id,
                        edge_type="ABOUT_ITEM",
                        weight=0.8
                    )


def integrate_roadmap_to_graph(graph: UnifiedContextGraph, roadmap_content: str) -> None:
    """Integrate roadmap items into the graph with embeddings."""

    # Parse roadmap
    roadmap = parse_roadmap_for_analysis(roadmap_content)

    # Batch generate embeddings for all roadmap items
    items_to_embed = []
    item_data_list = []

    for item in roadmap.get("items", []):
        item_id = f"ri_{item['name'].lower().replace(' ', '_')[:50]}"

        # Skip if already in graph
        if item_id in graph.node_indices["roadmap_item"]:
            continue

        # Create text for embedding (name + description for better semantic matching)
        embed_text = f"{item['name']}. {item.get('description', '')}"
        items_to_embed.append(embed_text)

        item_data_list.append({
            "id": item_id,
            "name": item["name"],
            "description": item.get("description", ""),
            "horizon": item.get("horizon", "future")
        })

    # Generate embeddings in batch
    if items_to_embed:
        console.print(f"[blue]Generating embeddings for {len(items_to_embed)} roadmap items...")
        embeddings = generate_embeddings(items_to_embed)

        # Add nodes with embeddings
        for item_data, embedding in zip(item_data_list, embeddings):
            graph.add_node(
                item_data["id"],
                "roadmap_item",
                item_data,
                embedding=embedding
            )


def sync_all_to_graph() -> UnifiedContextGraph:
    """
    Sync all data sources to the unified graph.
    Call this after any updates to decisions, assessments, etc.
    """

    console.print("[blue]Syncing unified context graph...")

    graph = UnifiedContextGraph.load()

    # 1. Sync roadmap items
    roadmap_file = OUTPUT_DIR / "master_roadmap.md"
    if roadmap_file.exists():
        roadmap_content = roadmap_file.read_text()
        integrate_roadmap_to_graph(graph, roadmap_content)

    # 2. Sync questions
    questions = load_questions()
    for question in questions:
        if question["id"] not in graph.node_indices["question"]:
            integrate_question_to_graph(graph, question)

    # 3. Sync decisions (highest authority)
    decisions = load_decisions()
    for decision in decisions:
        if decision["id"] not in graph.node_indices["decision"]:
            integrate_decision_to_graph(graph, decision)

    # 4. Sync assessments
    try:
        # Architecture assessments
        if (OUTPUT_DIR / "architecture-alignment.json").exists():
            alignment_data = json.loads((OUTPUT_DIR / "architecture-alignment.json").read_text())
            if alignment_data:
                # Add ID if missing
                if "id" not in alignment_data:
                    alignment_data["id"] = "arch_alignment_001"

                if alignment_data["id"] not in graph.node_indices["assessment"]:
                    integrate_assessment_to_graph(graph, alignment_data, "architecture")
    except Exception as e:
        console.print(f"[yellow]Warning: Could not sync architecture assessments: {e}")

    try:
        # Competitive assessments
        assessments = load_analyst_assessments()
        for assessment in assessments:
            if "id" in assessment and assessment["id"] not in graph.node_indices["assessment"]:
                integrate_assessment_to_graph(graph, assessment, "competitive")
    except Exception as e:
        console.print(f"[yellow]Warning: Could not sync competitive assessments: {e}")

    # 5. Sync chunks from LanceDB
    console.print("[blue]Syncing chunks from LanceDB...")
    try:
        db = init_db()
        table = db.open_table("roadmap_chunks")
        chunks_df = table.to_pandas()

        chunk_count = 0
        for _, row in chunks_df.iterrows():
            chunk_id = row.get("id")
            if chunk_id and chunk_id not in graph.node_indices["chunk"]:
                chunk_data = {
                    "id": chunk_id,
                    "content": row.get("content", ""),
                    "lens": row.get("lens", "unknown"),
                    "source_name": row.get("source_name", ""),
                    "source_file": row.get("source_file", ""),
                    "chunk_index": row.get("chunk_index", 0),
                    "token_count": row.get("token_count", 0)
                }

                graph.add_node(
                    chunk_id,
                    "chunk",
                    chunk_data,
                    embedding=row.get("vector")
                )
                chunk_count += 1

        console.print(f"[green]✓ Synced {chunk_count} chunks")
    except Exception as e:
        console.print(f"[yellow]Warning: Could not sync chunks: {e}")

    # 6. Create edges between chunks and other nodes using semantic similarity
    total_chunks = len(graph.node_indices["chunk"])
    console.print(f"[blue]Creating semantic edges for {total_chunks} chunks...")

    try:
        import numpy as np

        edges_created = 0
        chunk_items = list(graph.node_indices["chunk"].items())

        # Thresholds for different edge types
        SUPPORTED_BY_THRESHOLD = 0.75  # High relevance
        MENTIONED_IN_THRESHOLD = 0.65  # Moderate relevance
        OVERRIDES_THRESHOLD = 0.70     # Decision relevance

        # Cache for roadmap item embeddings (avoid repeated lookups)
        roadmap_embeddings = {}
        for ri_id, ri_data in graph.node_indices["roadmap_item"].items():
            # Get embedding from node
            ri_node = graph.graph.nodes[ri_id]
            ri_embedding = ri_node.get("embedding")
            if ri_embedding is not None:
                roadmap_embeddings[ri_id] = (ri_data, ri_embedding)

        # Cache for decision embeddings
        decision_embeddings = {}
        for dec_id, dec_data in graph.node_indices["decision"].items():
            dec_node = graph.graph.nodes[dec_id]
            dec_embedding = dec_node.get("embedding")
            if dec_embedding is not None:
                decision_embeddings[dec_id] = (dec_data, dec_embedding)

        console.print(f"[blue]Using semantic similarity with {len(roadmap_embeddings)} roadmap items, {len(decision_embeddings)} decisions")

        # Process all chunks with progress tracking
        for chunk_id, chunk_data in track(chunk_items, description="Creating semantic edges"):
            # Get chunk embedding
            chunk_node = graph.graph.nodes[chunk_id]
            chunk_embedding = chunk_node.get("embedding")

            if chunk_embedding is None:
                continue  # Skip chunks without embeddings

            # Link to roadmap items based on embedding similarity
            for ri_id, (ri_data, ri_embedding) in roadmap_embeddings.items():
                similarity = cosine_similarity(chunk_embedding, ri_embedding)

                # Create SUPPORTED_BY edge for high similarity
                if similarity >= SUPPORTED_BY_THRESHOLD:
                    if not graph.graph.has_edge(ri_id, chunk_id):
                        graph.add_edge(ri_id, chunk_id, edge_type="SUPPORTED_BY", weight=similarity)
                        edges_created += 1

                # Create MENTIONED_IN edge for moderate similarity
                elif similarity >= MENTIONED_IN_THRESHOLD:
                    if not graph.graph.has_edge(ri_id, chunk_id):
                        graph.add_edge(ri_id, chunk_id, edge_type="MENTIONED_IN", weight=similarity)
                        edges_created += 1

            # Link to decisions based on embedding similarity
            for dec_id, (dec_data, dec_embedding) in decision_embeddings.items():
                similarity = cosine_similarity(chunk_embedding, dec_embedding)

                # Create OVERRIDES edge for relevant decisions
                if similarity >= OVERRIDES_THRESHOLD:
                    if not graph.graph.has_edge(dec_id, chunk_id):
                        graph.add_edge(dec_id, chunk_id, edge_type="OVERRIDES", weight=similarity)
                        edges_created += 1

        console.print(f"[green]✓ Created {edges_created} semantic edges across {total_chunks} chunks")
        console.print(f"[blue]Edge thresholds: SUPPORTED_BY≥{SUPPORTED_BY_THRESHOLD}, MENTIONED_IN≥{MENTIONED_IN_THRESHOLD}, OVERRIDES≥{OVERRIDES_THRESHOLD}")
    except Exception as e:
        console.print(f"[yellow]Warning: Could not create semantic edges: {e}")
        import traceback
        console.print(f"[yellow]{traceback.format_exc()}")

    # Save
    graph.save()

    console.print(f"[green]✓ Graph synced: {graph.graph.number_of_nodes()} nodes, {graph.graph.number_of_edges()} edges")

    return graph


def retrieve_with_authority(query: str, graph: UnifiedContextGraph, top_k: int = 20) -> dict:
    """
    Retrieve relevant content respecting authority hierarchy.
    Returns content grouped by authority level.
    """

    # For now, return nodes grouped by type
    # In a full implementation, this would use embeddings for similarity search

    result = {
        "decisions": [],
        "answered_questions": [],
        "assessments": [],
        "roadmap_items": [],
        "gaps": [],
        "chunks": [],
        "pending_questions": []
    }

    query_lower = query.lower()

    # Search decisions
    for dec_id, dec_data in graph.node_indices["decision"].items():
        if query_lower in str(dec_data).lower():
            result["decisions"].append({"id": dec_id, "data": dec_data, "similarity": 0.9})

    # Search questions
    for q_id, q_data in graph.node_indices["question"].items():
        if query_lower in str(q_data).lower():
            if q_data.get("status") == "answered":
                result["answered_questions"].append({"id": q_id, "data": q_data, "similarity": 0.8})
            else:
                result["pending_questions"].append({"id": q_id, "data": q_data, "similarity": 0.7})

    # Search assessments
    for assess_id, assess_data in graph.node_indices["assessment"].items():
        if query_lower in str(assess_data).lower():
            result["assessments"].append({"id": assess_id, "data": assess_data, "similarity": 0.8})

    # Search roadmap items
    for ri_id, ri_data in graph.node_indices["roadmap_item"].items():
        if query_lower in str(ri_data).lower():
            result["roadmap_items"].append({"id": ri_id, "data": ri_data, "similarity": 0.7})

    # Search gaps
    for gap_id, gap_data in graph.node_indices["gap"].items():
        if query_lower in str(gap_data).lower():
            result["gaps"].append({"id": gap_id, "data": gap_data, "similarity": 0.7})

    # Limit results
    for category in result:
        result[category] = result[category][:top_k]

    return result


def format_context_with_authority(retrieved: dict) -> str:
    """Format retrieved content for synthesis prompt, separated by authority level."""

    sections = []

    # Level 1: Decisions
    if retrieved["decisions"]:
        sections.append("## RESOLVED DECISIONS (Highest Authority)")
        sections.append("These decisions override conflicting content.\n")
        for item in retrieved["decisions"][:5]:
            d = item["data"]
            sections.append(f"### {d.get('id', 'Decision')}")
            sections.append(f"**Decision:** {d.get('decision', 'N/A')}")
            sections.append(f"**Rationale:** {d.get('rationale', 'N/A')}\n")

    # Level 2: Answered Questions
    if retrieved["answered_questions"]:
        sections.append("## ANSWERED QUESTIONS")
        for item in retrieved["answered_questions"][:5]:
            q = item["data"]
            sections.append(f"- {q.get('question', 'N/A')} (Answered)\n")

    # Level 3: Assessments
    if retrieved["assessments"]:
        sections.append("## ASSESSMENTS")
        for item in retrieved["assessments"][:5]:
            a = item["data"]
            sections.append(f"- {a.get('type', 'Assessment')}: {a.get('summary', 'N/A')[:200]}\n")

    # Level 4: Roadmap Items
    if retrieved["roadmap_items"]:
        sections.append("## ROADMAP ITEMS")
        for item in retrieved["roadmap_items"][:10]:
            ri = item["data"]
            sections.append(f"- **{ri.get('name', 'Item')}** ({ri.get('horizon', 'future')}): {ri.get('description', 'N/A')[:150]}\n")

    # Level 5: Gaps
    if retrieved["gaps"]:
        sections.append("## IDENTIFIED GAPS")
        for item in retrieved["gaps"][:10]:
            g = item["data"]
            sections.append(f"- [{g.get('severity', 'N/A')}] {g.get('description', 'N/A')[:150]}\n")

    # Level 7: Pending Questions
    if retrieved["pending_questions"]:
        sections.append("## OPEN QUESTIONS")
        for item in retrieved["pending_questions"][:10]:
            q = item["data"]
            sections.append(f"- [{q.get('priority', 'N/A')}] {q.get('question', 'N/A')}\n")

    return "\n".join(sections)


# ========== SECTION 8: CLI COMMANDS ==========

@app.command()
def ingest(
    path: str = typer.Argument(..., help="Path to file or directory to ingest"),
    lens: str = typer.Option(..., "--lens", "-l", help="Source lens (authority level)")
):
    """
    Ingest documents with specified lens (authority level).

    Lens options: your-voice, team-structured, team-conversational,
    business-framework, engineering, external-analyst
    """
    if lens not in VALID_LENSES:
        console.print(f"[red]Invalid lens. Must be one of: {', '.join(VALID_LENSES)}")
        raise typer.Exit(1)

    path_obj = Path(path)
    if not path_obj.exists():
        console.print(f"[red]Error: Path not found: {path}")
        raise typer.Exit(1)

    # Get list of files
    if path_obj.is_dir():
        files = [f for f in path_obj.rglob("*") if f.is_file() and not f.name.startswith('.')]
    else:
        files = [path_obj]

    if not files:
        console.print("[yellow]No files found to ingest.")
        return

    console.print(f"[blue]Ingesting {len(files)} file(s) with lens: [bold]{lens}[/bold]")

    # Process files
    success_count = 0
    for file in track(files, description=f"Processing..."):
        try:
            text = parse_document(file)
            if not text.strip():
                console.print(f"[yellow]⚠ {file.name}: Empty document, skipping")
                continue

            # Use agentic chunking with fallback
            chunks = chunk_with_fallback(text, str(file), lens, use_agentic=True)
            if not chunks:
                console.print(f"[yellow]⚠ {file.name}: No chunks generated, skipping")
                continue

            index_chunks(chunks, str(file))
            console.print(f"[green]✓ {file.name} ({len(chunks)} chunks)")
            success_count += 1
        except Exception as e:
            console.print(f"[red]✗ {file.name}: {str(e)}")

    console.print(f"\n[green]Successfully ingested {success_count}/{len(files)} files")

    # Rebuild context graph
    if success_count > 0:
        console.print("[blue]Rebuilding context graph...")
        try:
            db = init_db()
            table = db.open_table("roadmap_chunks")

            # Get all chunks and embeddings from store
            all_data = table.to_pandas()
            all_chunks = []
            all_embeddings = []

            for _, row in all_data.iterrows():
                all_chunks.append({
                    "id": row["id"],
                    "content": row["content"],
                    "lens": row["lens"],
                    "source_file": row["source_file"],
                    "chunk_index": row["chunk_index"],
                    "token_count": row["token_count"],
                })
                all_embeddings.append(row["vector"])

            # Build graph
            graph = ContextGraph()
            graph.build_from_chunks(all_chunks, all_embeddings)
            graph.save()

            stats = graph.get_stats()
            console.print(f"[green]✓ Context graph updated: {stats['nodes']} nodes, {stats['edges']} edges")
        except Exception as e:
            console.print(f"[yellow]⚠ Could not build graph: {e}")


@app.command()
def generate():
    """Generate master roadmap from indexed materials."""
    console.print("[blue]Starting roadmap generation...")

    try:
        roadmap = generate_roadmap()
        console.print(f"\n[green]✓ Master roadmap generated successfully!")
        console.print(f"[green]  Saved to: {OUTPUT_DIR / 'master_roadmap.md'}")
    except Exception as e:
        console.print(f"[red]Error generating roadmap: {e}")
        raise typer.Exit(1)


@app.command()
def format(
    persona: str = typer.Argument(..., help="Persona to format for (executive/product/engineering)")
):
    """Format master roadmap for specific persona (executive, product, or engineering)."""
    valid_personas = ["executive", "product", "engineering"]
    if persona not in valid_personas:
        console.print(f"[red]Persona must be one of: {', '.join(valid_personas)}")
        raise typer.Exit(1)

    console.print(f"[blue]Formatting roadmap for [bold]{persona}[/bold] audience...")

    try:
        formatted = format_for_persona(persona)
        console.print(f"\n[green]✓ {persona.capitalize()} roadmap generated successfully!")
        console.print(f"[green]  Saved to: {OUTPUT_DIR / f'{persona}_roadmap.md'}")
    except Exception as e:
        console.print(f"[red]Error formatting roadmap: {e}")
        raise typer.Exit(1)


@app.command()
def ask(question: str = typer.Argument(..., help="Question to ask about your materials")):
    """Ask questions about your indexed materials."""
    validate_api_keys()

    console.print(f"[blue]Searching for: [italic]{question}[/italic]")

    chunks = retrieve_chunks(question, top_k=10)

    if not chunks:
        console.print("[yellow]No relevant content found. Please ingest documents first.")
        return

    # Build context
    context = "\n\n".join([f"[{c['lens']}] {c['content']}" for c in chunks])

    # Ask Claude
    console.print("[blue]Generating answer...")
    import httpx
    client = anthropic.Anthropic(
        api_key=ANTHROPIC_API_KEY,
        http_client=httpx.Client(verify=False)  # Disable SSL verification
    )
    message = client.messages.create(
        model="claude-opus-4-5-20251101",
        max_tokens=2000,
        messages=[
            {"role": "user", "content": f"Context from documents:\n{context}\n\nQuestion: {question}"}
        ]
    )

    console.print(f"\n[green]{message.content[0].text}")


@app.command()
def clear():
    """Clear the entire vector index and context graph."""
    console.print("[yellow]⚠️  This will delete all indexed chunks and the context graph.")

    confirm = typer.confirm("Are you sure you want to continue?")
    if not confirm:
        console.print("[blue]Aborted.")
        return

    try:
        # Clear vector database
        db = init_db()
        try:
            db.drop_table("roadmap_chunks")
            console.print("[green]✓ Cleared vector index")
        except Exception:
            console.print("[yellow]⚠ No vector index found")

        # Clear context graph
        graph_path = DATA_DIR / "context_graph.json"
        if graph_path.exists():
            graph_path.unlink()
            console.print("[green]✓ Cleared context graph")
        else:
            console.print("[yellow]⚠ No context graph found")

        # Clear chunking log
        log_path = DATA_DIR / "chunking_log.jsonl"
        if log_path.exists():
            log_path.unlink()
            console.print("[green]✓ Cleared chunking log")
        else:
            console.print("[yellow]⚠ No chunking log found")

        console.print("\n[green]✓ All data cleared successfully!")

    except Exception as e:
        console.print(f"[red]Error clearing data: {e}")
        raise typer.Exit(1)


@app.command()
def status():
    """Show status of indexed materials."""
    console.print("[blue]Checking index status...\n")

    try:
        db = init_db()
        table = db.open_table("roadmap_chunks")
        chunks = table.to_pandas()

        if chunks.empty:
            console.print("[yellow]No materials indexed yet.")
            return

        # Overall stats
        total_chunks = len(chunks)
        total_tokens = chunks['token_count'].sum()
        unique_sources = chunks['source_file'].nunique()

        console.print(f"[green]📊 Index Statistics")
        console.print(f"  Total Chunks: {total_chunks:,}")
        console.print(f"  Total Tokens: {total_tokens:,}")
        console.print(f"  Unique Sources: {unique_sources}")

        # Breakdown by lens
        console.print(f"\n[blue]📋 Breakdown by Lens")
        lens_stats = chunks.groupby('lens').agg({
            'source_file': 'nunique',
            'chunk_index': 'count',
            'token_count': 'sum'
        }).rename(columns={
            'source_file': 'files',
            'chunk_index': 'chunks',
            'token_count': 'tokens'
        })

        for lens in VALID_LENSES:
            if lens in lens_stats.index:
                stats = lens_stats.loc[lens]
                console.print(f"  {lens:25s} {int(stats['files']):3d} files, {int(stats['chunks']):5d} chunks, {int(stats['tokens']):8,d} tokens")
            else:
                console.print(f"  {lens:25s}   0 files,     0 chunks,        0 tokens")

        # Context graph
        console.print(f"\n[blue]🕸️  Context Graph")
        graph_path = DATA_DIR / "context_graph.json"
        if graph_path.exists():
            graph = ContextGraph().load()
            stats = graph.get_stats()
            console.print(f"  Nodes: {stats['nodes']:,}")
            console.print(f"  Edges: {stats['edges']:,}")
            console.print(f"  Components: {stats['components']}")
            console.print(f"  Density: {stats['density']:.4f}")

            if stats['edge_types']:
                console.print(f"\n  Edge Types:")
                for edge_type, count in stats['edge_types'].items():
                    console.print(f"    {edge_type:20s} {count:5,d}")
        else:
            console.print(f"  [yellow]No context graph found")

        # Chunking log
        console.print(f"\n[blue]📝 Chunking Log")
        log_path = DATA_DIR / "chunking_log.jsonl"
        if log_path.exists():
            import json
            logs = []
            with open(log_path) as f:
                for line in f:
                    logs.append(json.loads(line))

            agentic_count = len([l for l in logs if l['method'].startswith('agentic')])
            fallback_count = len([l for l in logs if 'fallback' in l['method'] or l['method'].startswith('structure')])
            issues_count = len([l for l in logs if not l['verification']['all_valid']])

            console.print(f"  Total Documents: {len(logs)}")
            console.print(f"  Agentic Chunking: {agentic_count}")
            console.print(f"  Fallback Used: {fallback_count}")
            console.print(f"  With Issues: {issues_count}")
        else:
            console.print(f"  [yellow]No chunking log found")

    except Exception as e:
        console.print(f"[yellow]No materials indexed yet.")


@app.command()
def cleanup(
    min_score: float = typer.Option(0.4, help="Minimum quality score to keep"),
    dry_run: bool = typer.Option(True, help="Show what would be removed without removing")
):
    """Remove low-quality chunks from the index."""
    console.print(f"[blue]Analyzing chunk quality (min_score={min_score})...\n")

    try:
        db = init_db()
        table = db.open_table("roadmap_chunks")
        df = table.to_pandas()

        if df.empty:
            console.print("[yellow]No chunks to analyze.")
            return

        to_remove = []
        to_keep = []

        # Score all chunks
        for _, row in df.iterrows():
            chunk = {
                "content": row.get("content", ""),
                "lens": row.get("lens", "")
            }
            quality = score_chunk_quality(chunk)

            if quality["score"] < min_score:
                to_remove.append({
                    "id": row.get("id"),
                    "score": quality["score"],
                    "reasons": quality["reasons"],
                    "preview": chunk["content"][:100] if chunk["content"] else "",
                    "lens": chunk["lens"]
                })
            else:
                to_keep.append(row.get("id"))

        # Report
        console.print(f"[bold]Quality Analysis[/bold]")
        console.print(f"Total chunks: {len(df)}")
        console.print(f"Would keep: {len(to_keep)} ({len(to_keep)/len(df)*100:.0%})")
        console.print(f"Would remove: {len(to_remove)} ({len(to_remove)/len(df)*100:.0%})")

        if to_remove:
            console.print(f"\n[bold]Chunks to remove:[/bold]")
            for item in to_remove[:20]:  # Show first 20
                console.print(f"  Score {item['score']:.2f} [{item['lens']}]: {item['preview']}...")
                console.print(f"    Reasons: {', '.join(item['reasons'])}")

            if len(to_remove) > 20:
                console.print(f"  ... and {len(to_remove) - 20} more")

        if not dry_run:
            if not typer.confirm("\n⚠️  This will permanently remove these chunks. Continue?"):
                console.print("[yellow]Cleanup cancelled.")
                return

            # Actually remove
            console.print(f"\n[blue]Removing {len(to_remove)} chunks...")
            for item in to_remove:
                # Escape single quotes in ID for SQL
                escaped_id = item['id'].replace("'", "''")
                table.delete(f"id = '{escaped_id}'")

            console.print(f"[green]✓ Removed {len(to_remove)} low-quality chunks[/green]")

            # Rebuild graph
            console.print("[blue]Rebuilding context graph...")
            graph = ContextGraph()
            # Reload remaining chunks
            df_remaining = table.to_pandas()
            remaining_chunks = []
            remaining_embeddings = []
            for _, row in df_remaining.iterrows():
                remaining_chunks.append({
                    "id": row["id"],
                    "content": row["content"],
                    "lens": row["lens"],
                    "source_file": row["source_file"],
                    "chunk_index": row["chunk_index"],
                    "token_count": row["token_count"],
                })
                remaining_embeddings.append(row["vector"])

            if remaining_chunks:
                graph.build_from_chunks(remaining_chunks, remaining_embeddings)
                graph.save()
                console.print("[green]✓ Graph rebuilt[/green]")
            else:
                console.print("[yellow]No chunks remaining, graph cleared[/yellow]")
        else:
            console.print(f"\n[yellow]Dry run — no changes made. Use --no-dry-run to apply.[/yellow]")

    except Exception as e:
        console.print(f"[red]Error during cleanup: {e}")


# ========== SECTION 9.5: QUESTIONS & DECISIONS CLI ==========

@app.command()
def questions_list(
    audience: str = typer.Option(None, help="Filter by audience (engineering/leadership/product)"),
    status: str = typer.Option("pending", help="Filter by status (pending/answered/deferred/obsolete)"),
    priority: str = typer.Option(None, help="Filter by priority (critical/high/medium/low)"),
    show_all: bool = typer.Option(False, help="Show all questions regardless of status")
):
    """List open questions."""

    questions = load_questions()

    if not questions:
        console.print("[yellow]No questions found. Generate questions from synthesis first.")
        return

    # Apply filters
    filtered = questions
    if not show_all:
        filtered = [q for q in filtered if q.get("status", "pending") == status]
    if audience:
        filtered = [q for q in filtered if q.get("audience", "") == audience]
    if priority:
        filtered = [q for q in filtered if q.get("priority", "") == priority]

    if not filtered:
        console.print(f"[yellow]No questions match filters (audience={audience}, status={status}, priority={priority})")
        return

    # Group by audience
    by_audience = {}
    for q in filtered:
        aud = q.get("audience", "unknown")
        if aud not in by_audience:
            by_audience[aud] = []
        by_audience[aud].append(q)

    # Display summary
    console.print(f"\n[bold]Open Questions[/bold] ({len(filtered)} questions)")
    console.print(f"Filters: audience={audience or 'all'}, status={status if not show_all else 'all'}, priority={priority or 'all'}\n")

    # Display by audience
    for aud in ["engineering", "leadership", "product"]:
        if aud not in by_audience:
            continue

        console.print(f"[bold cyan]{aud.upper()}[/bold cyan] ({len(by_audience[aud])} questions)\n")

        # Sort by priority
        priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        sorted_qs = sorted(by_audience[aud], key=lambda x: priority_order.get(x.get("priority", "low"), 4))

        for q in sorted_qs:
            priority_color = {"critical": "red", "high": "yellow", "medium": "white", "low": "dim"}.get(q.get("priority", "medium"), "white")
            status_icon = {"pending": "⏳", "answered": "✅", "deferred": "⏸️", "obsolete": "❌"}.get(q.get("status", "pending"), "?")

            console.print(f"  {status_icon} [{priority_color}]{q['id']}[/{priority_color}]")
            console.print(f"     {q['question']}")
            console.print(f"     [dim]Category: {q.get('category', 'N/A')} | Priority: {q.get('priority', 'medium')} | Created: {q.get('created_at', 'N/A')[:10]}[/dim]")

            if q.get("context"):
                context_preview = q['context'][:120] + "..." if len(q['context']) > 120 else q['context']
                console.print(f"     [dim]Context: {context_preview}[/dim]")

            if q.get("related_roadmap_items"):
                console.print(f"     [dim]Affects: {', '.join(q['related_roadmap_items'][:3])}[/dim]")

            console.print()


@app.command()
def questions_answer(
    question_id: str = typer.Argument(..., help="Question ID to answer (e.g., q_eng_001)"),
    answer: str = typer.Option(None, help="The answer (will prompt interactively if not provided)"),
    answered_by: str = typer.Option(None, help="Who provided the answer"),
    confidence: str = typer.Option("medium", help="Confidence level: high, medium, low"),
    create_decision: bool = typer.Option(True, help="Create decision entry from answer")
):
    """Submit an answer to an open question."""

    questions = load_questions()
    question = next((q for q in questions if q["id"] == question_id), None)

    if not question:
        console.print(f"[red]Question {question_id} not found[/red]")
        console.print(f"[dim]Use 'questions-list' to see available questions[/dim]")
        raise typer.Exit(1)

    # Display question
    console.print(f"\n[bold]Question:[/bold] {question['question']}")
    console.print(f"[dim]Context: {question.get('context', 'None')}[/dim]")
    console.print(f"[dim]Category: {question.get('category', 'N/A')} | Audience: {question.get('audience', 'N/A')}[/dim]")

    if question.get("related_roadmap_items"):
        console.print(f"[dim]Affects: {', '.join(question['related_roadmap_items'])}[/dim]")

    console.print()

    # Get answer interactively if not provided
    if not answer:
        console.print("[bold]Enter your answer:[/bold]")
        answer = typer.prompt("Answer")

    if not answered_by:
        answered_by = typer.prompt("Answered by")

    # Validate confidence
    if confidence not in ["high", "medium", "low"]:
        console.print(f"[yellow]Invalid confidence '{confidence}', using 'medium'[/yellow]")
        confidence = "medium"

    # Create answer record
    answer_record = {
        "id": f"ans_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "question_id": question_id,
        "answer": answer,
        "answered_by": answered_by,
        "answered_at": datetime.now().isoformat(),
        "confidence": confidence,
        "follow_up_needed": False,
        "notes": ""
    }

    # Save answer
    answers = load_answers()
    answers.append(answer_record)
    save_answers(answers)

    # Update question status
    question["status"] = "answered"
    save_questions(questions)

    console.print(f"\n[green]✓ Answer recorded: {answer_record['id']}[/green]")

    # Create decision if requested
    if create_decision:
        console.print("\n[bold]Create decision record:[/bold]")

        decision_text = typer.prompt("Decision (press Enter to use answer)", default=answer, show_default=False)
        rationale = typer.prompt("Rationale (optional)", default="", show_default=False)
        implications_str = typer.prompt("Implications (comma-separated, optional)", default="", show_default=False)
        owner = typer.prompt("Owner", default=answered_by, show_default=False)

        implications = [i.strip() for i in implications_str.split(",") if i.strip()]

        decision_record = {
            "id": f"dec_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "question_id": question_id,
            "answer_id": answer_record["id"],
            "decision": decision_text or answer,
            "rationale": rationale,
            "implications": implications,
            "owner": owner or answered_by,
            "review_date": None,
            "status": "active",
            "created_at": datetime.now().isoformat()
        }

        decisions = load_decisions()
        decisions.append(decision_record)
        save_decisions(decisions)

        console.print(f"[green]✓ Decision recorded: {decision_record['id']}[/green]")
        console.print(f"\n[bold]Summary:[/bold]")
        console.print(f"  Question: {question['question'][:80]}...")
        console.print(f"  Decision: {decision_record['decision'][:80]}...")
        console.print(f"  Owner: {decision_record['owner']}")
        if implications:
            console.print(f"  Implications: {len(implications)} noted")


@app.command()
def decisions_log(
    show_all: bool = typer.Option(False, help="Include superseded and revisiting decisions"),
    since: str = typer.Option(None, help="Show decisions since date (YYYY-MM-DD)"),
    export: Path = typer.Option(None, help="Export to markdown file")
):
    """View the decision log."""

    decisions = load_decisions()

    if not decisions:
        console.print("[yellow]No decisions recorded yet.")
        console.print("[dim]Answer questions with 'questions-answer' to create decisions.[/dim]")
        return

    # Filter
    filtered = decisions
    if not show_all:
        filtered = [d for d in filtered if d.get("status", "active") == "active"]

    if since:
        try:
            since_date = datetime.fromisoformat(since)
            filtered = [d for d in filtered if datetime.fromisoformat(d.get("created_at", "")) >= since_date]
        except ValueError:
            console.print(f"[red]Invalid date format: {since}. Use YYYY-MM-DD[/red]")
            raise typer.Exit(1)

    # Sort by date descending
    filtered = sorted(filtered, key=lambda x: x.get("created_at", ""), reverse=True)

    # Display
    console.print(f"\n[bold]Decision Log[/bold] ({len(filtered)} decisions)")
    console.print(f"Filters: status={'all' if show_all else 'active'}, since={since or 'all time'}\n")

    for dec in filtered:
        status_icon = {"active": "✅", "superseded": "🔄", "revisiting": "🔍"}.get(dec.get("status", "active"), "?")
        created = dec.get("created_at", "Unknown")[:10]

        console.print(f"{status_icon} [bold cyan]{dec['id']}[/bold cyan] — {created}")
        console.print(f"   [bold]Decision:[/bold] {dec['decision']}")

        if dec.get("rationale"):
            console.print(f"   [dim]Rationale: {dec['rationale']}[/dim]")

        if dec.get("implications"):
            console.print(f"   [yellow]Implications:[/yellow]")
            for imp in dec["implications"]:
                console.print(f"      • {imp}")

        console.print(f"   [dim]Owner: {dec.get('owner', 'Unassigned')} | Status: {dec.get('status', 'active')}[/dim]")

        # Link to question
        question_id = dec.get("question_id")
        if question_id:
            console.print(f"   [dim]Question ID: {question_id}[/dim]")

        console.print()

    # Export if requested
    if export:
        md_lines = [
            "# Decision Log",
            f"\nGenerated: {datetime.now().isoformat()}",
            f"Total Decisions: {len(filtered)}\n",
            "---\n"
        ]

        for dec in filtered:
            status_emoji = {"active": "✅", "superseded": "🔄", "revisiting": "🔍"}.get(dec.get("status", "active"), "?")
            created = dec.get("created_at", "Unknown")[:10]

            md_lines.append(f"## {status_emoji} {dec['id']} ({created})\n")
            md_lines.append(f"**Decision:** {dec['decision']}\n")

            if dec.get("rationale"):
                md_lines.append(f"**Rationale:** {dec['rationale']}\n")

            if dec.get("implications"):
                md_lines.append("**Implications:**")
                for imp in dec["implications"]:
                    md_lines.append(f"- {imp}")
                md_lines.append("")

            md_lines.append(f"**Owner:** {dec.get('owner', 'Unassigned')}")
            md_lines.append(f"**Status:** {dec.get('status', 'active')}")

            question_id = dec.get("question_id")
            if question_id:
                md_lines.append(f"**Question ID:** {question_id}")

            md_lines.append("\n---\n")

        md_content = "\n".join(md_lines)
        export.write_text(md_content)
        console.print(f"[green]✓ Exported to {export}[/green]")


@app.command()
def architecture_alignment(
    roadmap_file: Path = typer.Option(OUTPUT_DIR / "master_roadmap.md", help="Roadmap file to analyze"),
    output: Path = typer.Option(OUTPUT_DIR / "architecture-alignment.md", help="Output markdown file"),
    add_questions: bool = typer.Option(True, help="Add generated questions to Open Questions"),
    use_opus: bool = typer.Option(True, help="Use Opus for higher quality analysis")
):
    """Analyze alignment between roadmap and architecture documents."""

    console.print("[bold]Architecture Alignment Analysis[/bold]\n")

    # Load architecture documents
    console.print("[blue]Loading architecture documents...")
    arch_docs, metadata = load_architecture_documents()

    if not arch_docs:
        console.print("[yellow]No architecture documents found in:")
        for path in ARCHITECTURE_PATHS:
            console.print(f"  - {path}")
        console.print("\n[dim]Add architecture documents to these directories to enable analysis.")

        if metadata['skipped_count'] > 0:
            console.print(f"\n[yellow]{metadata['skipped_count']} documents were skipped:")
            for skipped in metadata['skipped_files']:
                console.print(f"  • {skipped['name']}: {skipped['reason']}")
        return

    console.print(f"[green]Loaded {len(arch_docs)} architecture documents:[/green]")
    for doc in arch_docs:
        console.print(f"  • {doc['title']} ({doc['token_count']:,} tokens)")

    console.print(f"[bold]Total: {metadata['total_tokens']:,} tokens[/bold]")

    if metadata['skipped_count'] > 0:
        console.print(f"[yellow]\n{metadata['skipped_count']} documents were skipped:")
        for skipped in metadata['skipped_files']:
            console.print(f"  • {skipped['name']}: {skipped['reason']}")
    console.print()

    # Load roadmap
    if not roadmap_file.exists():
        console.print(f"[red]Roadmap file not found: {roadmap_file}[/red]")
        console.print("[dim]Run 'generate' first to create a roadmap.")
        raise typer.Exit(1)

    roadmap_content = roadmap_file.read_text()
    roadmap = parse_roadmap_for_analysis(roadmap_content)

    console.print(f"[blue]Found {len(roadmap['items'])} roadmap items to analyze[/blue]\n")

    if not roadmap['items']:
        console.print("[yellow]No roadmap items found to analyze.")
        return

    # Run analysis
    console.print("[blue]Analyzing architecture alignment (this may take 1-2 minutes)...[/blue]")
    try:
        analysis = generate_architecture_alignment(
            roadmap=roadmap,
            architecture_docs=arch_docs,
            use_opus=use_opus
        )
    except Exception as e:
        console.print(f"[red]Analysis failed: {e}")
        raise typer.Exit(1)

    # Save results
    save_alignment_analysis(analysis)

    output_content = format_alignment_report(analysis)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(output_content)

    console.print(f"[green]✓ Analysis saved to {output}[/green]\n")

    # Summary
    console.print("[bold]Summary[/bold]")

    assessments = analysis.get("assessments", [])
    full_support = len([a for a in assessments if a.get("architecture_supports") == "full"])
    partial_support = len([a for a in assessments if a.get("architecture_supports") == "partial"])
    no_support = len([a for a in assessments if a.get("architecture_supports") == "no"])

    console.print(f"  [green]Full support: {full_support}[/green]")
    console.print(f"  [yellow]Partial support: {partial_support}[/yellow]")
    console.print(f"  [red]No support: {no_support}[/red]")

    # Count questions
    total_questions = sum(len(a.get("questions", [])) for a in assessments)
    console.print(f"\n  [blue]Engineering questions generated: {total_questions}[/blue]")

    # Add questions
    if add_questions and total_questions > 0:
        questions = extract_engineering_questions_from_alignment(analysis)
        added = add_architecture_questions_to_system(questions)
        console.print(f"  [green]Questions added to Open Questions: {added}[/green]")

    # Cross-cutting concerns
    cross_cutting = analysis.get("cross_cutting_concerns", {})
    if cross_cutting.get("architectural_gaps"):
        console.print("\n[yellow]Architectural Gaps Identified:[/yellow]")
        for gap in cross_cutting["architectural_gaps"]:
            console.print(f"  • {gap}")

    if cross_cutting.get("recommended_adrs"):
        console.print("\n[cyan]Recommended ADRs:[/cyan]")
        for adr in cross_cutting["recommended_adrs"]:
            console.print(f"  • {adr}")

    console.print(f"\n[dim]View detailed analysis: {output}")


@app.command()
def architecture_docs(
    show_components: bool = typer.Option(False, help="Show extracted components")
):
    """List available architecture documents."""

    docs, metadata = load_architecture_documents()

    if not docs:
        console.print("[yellow]No architecture documents found in:")
        for path in ARCHITECTURE_PATHS:
            console.print(f"  - {path}")

        if metadata['skipped_count'] > 0:
            console.print(f"\n[yellow]{metadata['skipped_count']} documents were skipped:")
            for skipped in metadata['skipped_files']:
                console.print(f"  • {skipped['name']}: {skipped['reason']}")
        return

    console.print(f"\n[bold]Architecture Documents[/bold] ({len(docs)} loaded)\n")

    for doc in docs:
        console.print(f"[cyan]{doc['title']}[/cyan]")
        console.print(f"  Path: {doc['path']}")
        console.print(f"  Type: {doc['doc_type']}")
        console.print(f"  Tokens: {doc['token_count']:,}")
        console.print(f"  Last Updated: {doc['last_updated'][:10]}")

        if show_components and doc.get('key_components'):
            console.print(f"  Components: {', '.join(doc['key_components'][:5])}")

        console.print()

    console.print(f"[bold]Total tokens: {metadata['total_tokens']:,}[/bold]")

    if metadata['skipped_count'] > 0:
        console.print(f"\n[yellow]{metadata['skipped_count']} documents were skipped:")
        for skipped in metadata['skipped_files']:
            console.print(f"  • {skipped['name']}: {skipped['reason']}")
    console.print(f"[dim]Token budget: {MAX_TOTAL_TOKENS}")


# ========== COMPETITIVE INTELLIGENCE CLI ==========

@app.command()
def competitive_add(
    competitor: str = typer.Option(..., help="Competitor name"),
    dev_type: str = typer.Option(..., help="Development type (product_launch, feature, acquisition, partnership, funding, strategy_shift)"),
    title: str = typer.Option(..., help="Title of the development"),
    description: str = typer.Option(..., help="Full description"),
    source_url: str = typer.Option(..., help="Source URL"),
    announced_date: str = typer.Option(..., help="Announced date (YYYY-MM-DD)")
):
    """Add a competitor development to track."""
    console.print("[bold]Adding Competitor Development[/bold]\n")

    development = add_competitor_development(
        competitor=competitor,
        development_type=dev_type,
        title=title,
        description=description,
        source_url=source_url,
        announced_date=announced_date
    )

    console.print(f"[green]✓ Added competitor development: {development['id']}")
    console.print(f"  Competitor: {competitor}")
    console.print(f"  Title: {title}")
    console.print(f"  Type: {dev_type}")
    console.print("\n[dim]Run 'competitive-assess {development['id']}' to generate analyst assessment")


@app.command()
def competitive_list():
    """List all competitor developments."""
    developments = load_competitor_developments()

    if not developments:
        console.print("[yellow]No competitor developments tracked yet.")
        console.print("[dim]Use 'competitive-add' to add a development.")
        return

    console.print(f"\n[bold]Competitor Developments[/bold] ({len(developments)} total)\n")

    for dev in developments:
        console.print(f"[cyan]{dev['id']}[/cyan] — {dev['competitor']}")
        console.print(f"  {dev['title']}")
        console.print(f"  Type: {dev['development_type']} | Announced: {dev['announced_date']}")

        # Check if assessed
        assessments = load_analyst_assessments()
        assessed = any(a['development_id'] == dev['id'] for a in assessments)
        if assessed:
            console.print("  [green]✓ Assessed")
        else:
            console.print("  [yellow]⧗ Not yet assessed")

        console.print()


@app.command()
def competitive_assess(
    development_id: str = typer.Argument(..., help="Development ID to assess"),
    use_opus: bool = typer.Option(True, help="Use Opus for higher quality")
):
    """
    Generate analyst assessment of competitor development.

    IMPORTANT: This produces an objective analyst research note, not a strategy document.
    The roadmap is the source of truth. No new features or recommendations are suggested.
    """
    console.print("[bold]Analyst Assessment[/bold]")
    console.print("[dim]Note: This is an objective assessment, not a strategy document[/dim]\n")

    # Load development
    development = get_competitor_development(development_id)
    if not development:
        console.print(f"[red]Development not found: {development_id}")
        console.print("[dim]Use 'competitive-list' to see available developments")
        raise typer.Exit(1)

    console.print(f"Competitor: [cyan]{development['competitor']}[/cyan]")
    console.print(f"Development: {development['title']}")
    console.print(f"Type: {development['development_type']}")
    console.print()

    # Load context
    analyst_docs = load_analyst_documents()
    if analyst_docs:
        console.print(f"[blue]Analyst research context: {len(analyst_docs)} documents")
    else:
        console.print("[yellow]No analyst research documents found in materials/external-analyst/")
        console.print("[dim]Proceeding without analyst context...")

    roadmap_file = OUTPUT_DIR / "master_roadmap.md"
    if not roadmap_file.exists():
        console.print("[red]Roadmap not found. Generate a roadmap first.")
        raise typer.Exit(1)

    console.print(f"[blue]Roadmap: Using current version as source of truth\n")

    try:
        with console.status("[blue]Generating analyst assessment... (this may take 1-2 minutes)"):
            assessment = generate_analyst_assessment(development, use_opus=use_opus)

        analysis = assessment['analysis']

        # Display summary
        console.print(f"\n[bold green]✓ Assessment Complete[/bold green]\n")
        console.print(f"[bold]{analysis['headline']}[/bold]\n")
        console.print(f"Impact: {analysis['overall_impact']} ({analysis['confidence']} confidence)")
        console.print(f"Timeline: {analysis['impact_timeline']}\n")

        console.print(f"Roadmap Strengths Identified: {len(analysis.get('roadmap_strengths', []))}")
        console.print(f"Roadmap Gaps Identified: {len(analysis.get('roadmap_gaps', []))}")
        console.print(f"Strategic Questions Raised: {len(analysis.get('strategic_questions', []))}\n")

        # Save markdown
        markdown_content = format_analyst_assessment_markdown(assessment)
        output_file = COMPETITIVE_DIR / f"assessment_{assessment['id']}.md"
        output_file.write_text(markdown_content)

        console.print(f"[green]✓ Saved: {output_file}")
        console.print(f"[dim]Strategic questions added to Open Questions for leadership review")

        if assessment.get('validation_warnings'):
            console.print(f"\n[yellow]⚠️ {len(assessment['validation_warnings'])} validation warnings — see above")

    except Exception as e:
        console.print(f"[red]Assessment failed: {e}")
        import traceback
        console.print(f"[dim]{traceback.format_exc()}")
        raise typer.Exit(1)


@app.command()
def competitive_view(
    assessment_id: str = typer.Argument(..., help="Assessment ID to view")
):
    """View a specific analyst assessment."""
    assessments = load_analyst_assessments()
    assessment = next((a for a in assessments if a['id'] == assessment_id), None)

    if not assessment:
        console.print(f"[red]Assessment not found: {assessment_id}")
        raise typer.Exit(1)

    analysis = assessment['analysis']
    development = assessment['development']

    console.print(f"\n[bold]{analysis['headline']}[/bold]\n")
    console.print(f"Competitor: {development['competitor']}")
    console.print(f"Development: {development['title']}")
    console.print(f"Assessed: {assessment['assessed_at'][:10]}\n")

    console.print(f"[bold]Executive Summary[/bold]")
    console.print(analysis['executive_summary'])
    console.print()

    console.print(f"[bold]Impact Assessment[/bold]")
    console.print(f"Overall Impact: {analysis['overall_impact']}")
    console.print(f"Timeline: {analysis['impact_timeline']}")
    console.print(f"Confidence: {analysis['confidence']}\n")

    console.print(f"[bold]Roadmap Strengths:[/bold] {len(analysis.get('roadmap_strengths', []))}")
    for strength in analysis.get('roadmap_strengths', []):
        console.print(f"  • {strength['roadmap_item']} ({strength['horizon']}) — {strength['coverage_level']} coverage")

    console.print(f"\n[bold]Roadmap Gaps:[/bold] {len(analysis.get('roadmap_gaps', []))}")
    for gap in analysis.get('roadmap_gaps', []):
        console.print(f"  • [{gap['severity']}] {gap['gap_description']}")

    console.print(f"\n[bold]Strategic Questions:[/bold] {len(analysis.get('strategic_questions', []))}")
    for q in analysis.get('strategic_questions', []):
        console.print(f"  • [{q['question_type']}] {q['question']}")

    markdown_file = COMPETITIVE_DIR / f"assessment_{assessment_id}.md"
    if markdown_file.exists():
        console.print(f"\n[dim]Full report: {markdown_file}")


# ========== GRAPH MANAGEMENT CLI ==========

@app.command()
def graph_sync():
    """Sync all data sources to the unified context graph."""

    console.print("[bold]Syncing Unified Context Graph[/bold]\n")

    try:
        graph = sync_all_to_graph()

        # Report stats
        console.print("\n[bold]Graph Statistics:[/bold]")
        console.print(f"  Total nodes: {graph.graph.number_of_nodes()}")
        console.print(f"  Total edges: {graph.graph.number_of_edges()}")

        for node_type, nodes in graph.node_indices.items():
            console.print(f"  {node_type}: {len(nodes)}")

        console.print("\n[green]✓ Graph sync complete!")

    except Exception as e:
        console.print(f"[red]Sync failed: {e}")
        import traceback
        console.print(f"[dim]{traceback.format_exc()}")


@app.command()
def graph_query(
    query: str = typer.Argument(..., help="Query to search"),
    top_k: int = typer.Option(20, help="Max results per category")
):
    """Query the unified context graph with authority hierarchy."""

    graph = UnifiedContextGraph.load()

    if graph.graph.number_of_nodes() == 0:
        console.print("[yellow]Graph is empty. Run 'graph-sync' first.")
        return

    console.print(f"[bold]Querying:[/bold] {query}\n")

    results = retrieve_with_authority(query, graph, top_k)

    # Display results by authority level
    total_results = sum(len(items) for items in results.values())

    if total_results == 0:
        console.print("[yellow]No results found.")
        return

    console.print(f"[green]Found {total_results} results\n")

    for category, items in results.items():
        if items:
            console.print(f"\n[bold cyan]{category.upper().replace('_', ' ')}[/bold cyan] ({len(items)} results)")
            for item in items[:5]:
                data_str = str(item['data'])[:150]
                console.print(f"  • {item['id']}: {data_str}...")


@app.command()
def graph_stats():
    """Show unified graph statistics and authority coverage."""

    graph = UnifiedContextGraph.load()

    if graph.graph.number_of_nodes() == 0:
        console.print("[yellow]Graph is empty. Run 'graph-sync' first.")
        return

    console.print("[bold]Unified Context Graph Statistics[/bold]\n")

    console.print(f"Total nodes: {graph.graph.number_of_nodes()}")
    console.print(f"Total edges: {graph.graph.number_of_edges()}")

    console.print("\n[bold]Nodes by Type:[/bold]")
    for node_type, nodes in graph.node_indices.items():
        console.print(f"  {node_type}: {len(nodes)}")

    console.print("\n[bold]Edges by Type:[/bold]")
    edge_counts = {}
    for u, v, data in graph.graph.edges(data=True):
        edge_type = data.get("edge_type", "unknown")
        edge_counts[edge_type] = edge_counts.get(edge_type, 0) + 1

    if edge_counts:
        for edge_type, count in sorted(edge_counts.items()):
            console.print(f"  {edge_type}: {count}")
    else:
        console.print("  (no edges)")

    # Authority coverage
    console.print("\n[bold]Authority Coverage:[/bold]")

    active_decisions = len([
        d for d in graph.node_indices["decision"].values()
        if d.get("status") == "active"
    ])
    console.print(f"  Active decisions (L1): {active_decisions}")

    answered_questions = len([
        q for q in graph.node_indices["question"].values()
        if q.get("status") == "answered"
    ])
    pending_questions = len([
        q for q in graph.node_indices["question"].values()
        if q.get("status") == "pending"
    ])
    console.print(f"  Answered questions (L2): {answered_questions}")
    console.print(f"  Assessments (L3): {len(graph.node_indices['assessment'])}")
    console.print(f"  Roadmap items (L4): {len(graph.node_indices['roadmap_item'])}")
    console.print(f"  Gaps (L5): {len(graph.node_indices['gap'])}")
    console.print(f"  Pending questions (L7): {pending_questions}")


if __name__ == "__main__":
    app()
