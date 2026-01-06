# Agentic Chunking Specification

## Critical Constraint: EXTRACTION ONLY

**Claude must NEVER synthesize, infer, or generate new ideas during chunking.**

The chunking process is strictly extractive:
- ✅ Identify where to split the document
- ✅ Extract exact text from the document
- ✅ Label sections with titles FROM the document
- ✅ Summarize using ONLY words/phrases from the document
- ✅ Extract entities that are EXPLICITLY mentioned
- ❌ NEVER add interpretation
- ❌ NEVER infer meaning not stated
- ❌ NEVER generate new phrasing
- ❌ NEVER fill gaps with assumptions

---

## Verification Strategy

### 1. Verbatim Extraction
All chunk content must be **exact quotes** from the source document. No paraphrasing.

### 2. Grounded Summaries
Summaries must be **extractive** — composed only of words/phrases that appear in the chunk.

### 3. Citation Requirements
Every metadata field must reference specific text from the document.

### 4. Hallucination Check
Post-processing step verifies all extracted content exists in source.

---

## Implementation

### Dependencies

```bash
uv add anthropic
```

Uses existing Anthropic SDK.

---

## Chunking Prompt

This is the core prompt sent to Claude for each document:

```python
AGENTIC_CHUNKING_PROMPT = """
You are a document segmentation tool. Your ONLY job is to identify logical boundaries in this document and extract sections VERBATIM.

## CRITICAL RULES — READ CAREFULLY

1. **EXTRACTION ONLY**: You must ONLY extract text that exists in the document. 
   - DO NOT paraphrase
   - DO NOT summarize in your own words
   - DO NOT infer or interpret meaning
   - DO NOT add any information not explicitly stated

2. **VERBATIM QUOTES**: The "content" field must be an EXACT copy-paste from the document.

3. **GROUNDED METADATA**: All metadata must use ONLY words that appear in the document.
   - section_title: Use the actual heading from the document, or first phrase if no heading
   - key_entities: Only entities EXPLICITLY named in the text
   - time_references: Only dates/periods EXPLICITLY mentioned
   
4. **NO SYNTHESIS**: Do not connect ideas across sections. Each chunk stands alone.

5. **PRESERVE ORIGINAL**: Include typos, formatting, exact phrasing — do not "fix" anything.

## YOUR TASK

Analyze this document and segment it into logical chunks.

For each chunk, provide:
- Exact start and end character positions
- The verbatim text content
- Metadata extracted ONLY from that chunk's text

## OUTPUT FORMAT

Return a JSON array of chunks:

```json
{
  "chunks": [
    {
      "chunk_index": 0,
      "start_char": 0,
      "end_char": 1523,
      "content": "EXACT VERBATIM TEXT FROM DOCUMENT — COPY PASTE ONLY",
      "metadata": {
        "section_title": "Exact heading from document or null",
        "key_entities": ["Entity1", "Entity2"],
        "time_references": ["Q2", "2024"],
        "source_quotes_for_metadata": {
          "section_title_source": "The exact text where title appears",
          "entities_sources": ["Quote mentioning Entity1", "Quote mentioning Entity2"]
        }
      }
    }
  ],
  "document_stats": {
    "total_characters": 15234,
    "total_chunks": 8,
    "detected_structure": "headings|paragraphs|slides|speaker_turns"
  }
}
```

## SEGMENTATION GUIDELINES

Split documents at:
- Heading boundaries (##, ###, bold titles)
- Topic shifts (new subject introduced)
- Speaker changes (in transcripts)
- Slide boundaries (in presentations)
- Paragraph breaks when topics change

Target chunk size: 500-1500 tokens. Prefer logical boundaries over size limits.

Keep together:
- A heading with its content
- A question with its answer
- A claim with its supporting points
- A speaker's complete turn

## DOCUMENT TO SEGMENT

<document>
{document_text}
</document>

Now segment this document following ALL rules above. Remember: EXTRACTION ONLY, NO SYNTHESIS.
"""
```

---

## Verification Function

Post-processing to catch any hallucinations:

```python
def verify_chunk_integrity(chunk: dict, source_document: str) -> dict:
    """
    Verify that all chunk content exists verbatim in source document.
    Returns verification result with any issues found.
    """
    issues = []
    
    # 1. Verify content is verbatim
    content = chunk.get("content", "")
    if content not in source_document:
        # Try to find closest match
        # Sometimes whitespace differs
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


def verify_all_chunks(chunks: list[dict], source_document: str) -> dict:
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
```

---

## Fallback Strategy

If Claude's chunking fails verification, fall back to structure-aware chunking:

```python
def chunk_with_fallback(
    document_text: str,
    source_path: str,
    lens: str,
    max_retries: int = 2
) -> list[dict]:
    """
    Attempt agentic chunking with fallback to deterministic chunking.
    """
    
    # Try agentic chunking
    for attempt in range(max_retries):
        try:
            chunks = agentic_chunk(document_text, source_path, lens)
            
            # Verify
            verification = verify_all_chunks(chunks, document_text)
            
            if verification["all_valid"]:
                return chunks
            
            # Log issues but continue if mostly valid
            if verification["valid_chunks"] / verification["total_chunks"] > 0.8:
                # Filter out invalid chunks
                valid_chunks = [
                    c for c, v in zip(chunks, verification["results"]) 
                    if v["is_valid"]
                ]
                return valid_chunks
            
            # Too many failures, retry
            print(f"Attempt {attempt + 1}: {verification['critical_failures']} chunks failed verification")
            
        except Exception as e:
            print(f"Agentic chunking failed: {e}")
    
    # Fallback to deterministic chunking
    print(f"Falling back to structure-aware chunking for {source_path}")
    return structure_aware_chunk(document_text, source_path, lens)
```

---

## Agentic Chunking Implementation

```python
import json
import anthropic
from pathlib import Path

class AgenticChunker:
    """Chunk documents using Claude with strict extraction-only behavior."""
    
    def __init__(self, api_key: str = None, model: str = "claude-sonnet-4-20250514"):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model
        self.prompt_template = AGENTIC_CHUNKING_PROMPT
    
    def chunk_document(
        self,
        document_text: str,
        source_path: str,
        lens: str
    ) -> list[dict]:
        """
        Chunk a document using Claude.
        
        Returns list of verified chunks with metadata.
        """
        
        # Skip very short documents
        if len(document_text.strip()) < 100:
            return [{
                "chunk_index": 0,
                "content": document_text.strip(),
                "source_path": source_path,
                "lens": lens,
                "metadata": {
                    "section_title": None,
                    "key_entities": [],
                    "time_references": []
                }
            }]
        
        # Call Claude
        prompt = self.prompt_template.format(document_text=document_text)
        
        response = self.client.messages.create(
            model=self.model,
            max_tokens=8000,
            temperature=0,  # Deterministic for consistency
            messages=[{"role": "user", "content": prompt}]
        )
        
        # Parse response
        response_text = response.content[0].text
        
        # Extract JSON from response
        chunks_data = self._parse_json_response(response_text)
        
        # Verify each chunk
        verified_chunks = []
        for chunk in chunks_data.get("chunks", []):
            verification = verify_chunk_integrity(chunk, document_text)
            
            if verification["is_valid"]:
                # Add source info
                chunk["source_path"] = source_path
                chunk["lens"] = lens
                chunk["verified"] = True
                verified_chunks.append(chunk)
            else:
                # Log but don't include
                print(f"Chunk {chunk.get('chunk_index')} failed verification: {verification['issues']}")
                
                # Try to salvage by extracting content directly
                salvaged = self._salvage_chunk(chunk, document_text, source_path, lens)
                if salvaged:
                    verified_chunks.append(salvaged)
        
        return verified_chunks
    
    def _parse_json_response(self, response_text: str) -> dict:
        """Extract JSON from Claude's response."""
        # Try to find JSON block
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
            
            return json.loads(json_str)
        
        except json.JSONDecodeError as e:
            print(f"Failed to parse JSON: {e}")
            return {"chunks": []}
    
    def _salvage_chunk(
        self,
        chunk: dict,
        document_text: str,
        source_path: str,
        lens: str
    ) -> dict | None:
        """
        Try to salvage a chunk that failed verification by finding
        the closest matching text in the document.
        """
        content = chunk.get("content", "")
        if not content:
            return None
        
        # Try to find content with fuzzy matching
        # Look for longest substring match
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
                    "source_path": source_path,
                    "lens": lens,
                    "metadata": {
                        "section_title": None,
                        "key_entities": self._extract_entities_simple(salvaged_content),
                        "time_references": self._extract_times_simple(salvaged_content)
                    },
                    "verified": True,
                    "salvaged": True
                }
        
        return None
    
    def _extract_entities_simple(self, text: str) -> list[str]:
        """Simple entity extraction without LLM."""
        import re
        
        # Find capitalized phrases
        caps = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
        
        # Deduplicate and limit
        seen = set()
        entities = []
        for cap in caps:
            if cap.lower() not in seen and len(cap) > 2:
                seen.add(cap.lower())
                entities.append(cap)
        
        return entities[:10]
    
    def _extract_times_simple(self, text: str) -> list[str]:
        """Simple time extraction without LLM."""
        import re
        
        patterns = [
            r'\bQ[1-4]\s*(?:20\d{2})?\b',
            r'\b20\d{2}\b',
            r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s*(?:20\d{2})?\b',
        ]
        
        refs = []
        for pattern in patterns:
            refs.extend(re.findall(pattern, text, re.IGNORECASE))
        
        return list(set(refs))[:5]
```

---

## Document-Type Specific Handling

Different document types need different chunking hints:

```python
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
```

---

## Updated Chunking Prompt with Type Hints

```python
AGENTIC_CHUNKING_PROMPT_V2 = """
You are a document segmentation tool. Your ONLY job is to identify logical boundaries in this document and extract sections VERBATIM.

## CRITICAL RULES — YOU MUST FOLLOW THESE EXACTLY

1. **EXTRACTION ONLY**: You must ONLY extract text that exists in the document. 
   - DO NOT paraphrase — use exact quotes only
   - DO NOT summarize in your own words
   - DO NOT infer or interpret meaning
   - DO NOT add any information not explicitly stated
   - DO NOT "improve" or "fix" the text
   - DO NOT fill in gaps or add context

2. **VERBATIM CONTENT**: The "content" field must be an EXACT copy-paste from the document.
   - Include all original punctuation
   - Include any typos from the original
   - Include original formatting markers
   - Do not fix grammar or spelling

3. **GROUNDED METADATA**: All metadata must use ONLY words that appear in the document.
   - section_title: Use the actual heading from the document, or null if none
   - key_entities: Only entities EXPLICITLY named in the text
   - time_references: Only dates/periods EXPLICITLY mentioned

4. **CITE YOUR SOURCES**: For each metadata field, include the exact quote from the document that supports it.

5. **WHEN UNCERTAIN, LEAVE EMPTY**: If you're not 100% sure something is explicitly stated, use null or empty array.

{document_type_hints}

## OUTPUT FORMAT

Return valid JSON only. No explanation before or after.

```json
{{
  "chunks": [
    {{
      "chunk_index": 0,
      "start_char": 0,
      "end_char": 1523,
      "content": "EXACT VERBATIM TEXT — COPY PASTE ONLY — DO NOT MODIFY",
      "metadata": {{
        "section_title": "Exact heading or null",
        "key_entities": ["Only", "Explicitly", "Named", "Entities"],
        "time_references": ["Q2", "2024"],
        "source_citations": {{
          "title_found_at": "Quote where title appears",
          "entities_found_at": ["Quote for entity 1", "Quote for entity 2"]
        }}
      }}
    }}
  ]
}}
```

## DOCUMENT TO SEGMENT

<document>
{document_text}
</document>

Return ONLY valid JSON. Extract ONLY what exists. DO NOT add anything.
"""
```

---

## Integration with Existing System

### Update Ingest Flow

```python
def ingest_document(
    file_path: Path,
    lens: str,
    use_agentic: bool = True
) -> list[dict]:
    """
    Ingest a document with optional agentic chunking.
    """
    
    # Parse document
    content = parse_document(file_path)
    
    if use_agentic:
        # Use Claude for intelligent chunking
        chunker = AgenticChunker()
        
        # Get document-specific hints
        hints = get_document_type_hints(str(file_path), content)
        
        # Chunk with verification
        chunks = chunk_with_fallback(
            document_text=content,
            source_path=str(file_path),
            lens=lens
        )
    else:
        # Fall back to token-based chunking
        chunks = token_based_chunk(content, str(file_path), lens)
    
    return chunks
```

### Streamlit Integration

Add chunking method selection to ingest page:

```python
# In Streamlit ingest page

st.subheader("Chunking Method")

chunking_method = st.radio(
    "Select chunking strategy",
    ["Agentic (Claude-powered)", "Structure-aware", "Fixed token"],
    index=0,
    help="""
    - Agentic: Highest quality, uses Claude to find logical boundaries (~$0.01-0.05 per document)
    - Structure-aware: Uses document structure (headings, slides), no LLM cost
    - Fixed token: Simple split every N tokens, fastest but lowest quality
    """
)

if chunking_method == "Agentic (Claude-powered)":
    st.info("⚠️ Agentic chunking calls Claude API. Estimated cost: ~$0.02-0.05 per document.")
    
    verify_chunks = st.checkbox(
        "Verify chunk integrity",
        value=True,
        help="Double-check that all extracted content exists in source document"
    )
```

---

## Logging and Transparency

Add detailed logging so you can audit chunking decisions:

```python
def log_chunking_result(
    source_path: str,
    lens: str,
    chunks: list[dict],
    verification: dict,
    method: str
) -> dict:
    """Log chunking results for auditing."""
    
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "source_path": source_path,
        "lens": lens,
        "method": method,
        "chunk_count": len(chunks),
        "verification": {
            "all_valid": verification["all_valid"],
            "valid_count": verification["valid_chunks"],
            "issues": [
                {
                    "chunk_index": r["chunk_id"],
                    "issues": r["issues"]
                }
                for r in verification["results"]
                if r["issues"]
            ]
        },
        "chunks_preview": [
            {
                "index": c["chunk_index"],
                "content_length": len(c.get("content", "")),
                "content_preview": c.get("content", "")[:100],
                "entities": c.get("metadata", {}).get("key_entities", []),
            }
            for c in chunks[:5]
        ]
    }
    
    # Save to log file
    log_path = Path("data/chunking_log.jsonl")
    log_path.parent.mkdir(exist_ok=True)
    
    with open(log_path, "a") as f:
        f.write(json.dumps(log_entry) + "\n")
    
    return log_entry
```

---

## Streamlit Audit Page

Add a page to review chunking quality:

```python
elif page == "🔍 Chunking Audit":
    st.title("Chunking Audit Log")
    
    log_path = Path("data/chunking_log.jsonl")
    
    if not log_path.exists():
        st.info("No chunking logs yet. Ingest some documents first.")
    else:
        # Load logs
        logs = []
        with open(log_path) as f:
            for line in f:
                logs.append(json.loads(line))
        
        st.metric("Total Documents Processed", len(logs))
        
        # Filter by verification status
        show_only_issues = st.checkbox("Show only documents with issues")
        
        for log in reversed(logs):  # Most recent first
            if show_only_issues and log["verification"]["all_valid"]:
                continue
            
            status = "✅" if log["verification"]["all_valid"] else "⚠️"
            
            with st.expander(f"{status} {log['source_path']} — {log['chunk_count']} chunks"):
                st.write(f"**Lens:** {log['lens']}")
                st.write(f"**Method:** {log['method']}")
                st.write(f"**Time:** {log['timestamp']}")
                
                if not log["verification"]["all_valid"]:
                    st.error(f"Issues in {len(log['verification']['issues'])} chunks:")
                    for issue in log["verification"]["issues"]:
                        st.write(f"Chunk {issue['chunk_index']}: {issue['issues']}")
                
                st.write("**Sample Chunks:**")
                for chunk in log["chunks_preview"]:
                    st.code(chunk["content_preview"])
```

---

## Cost Controls

```python
# Configuration
AGENTIC_CHUNKING_CONFIG = {
    "enabled": True,
    "model": "claude-sonnet-4-20250514",  # Good balance of quality/cost
    "max_document_tokens": 50000,  # Skip agentic for very large docs
    "min_document_tokens": 100,  # Skip agentic for tiny docs
    "verify_chunks": True,
    "fallback_on_failure": True,
    "log_all_results": True,
}

def should_use_agentic(document_text: str, config: dict = AGENTIC_CHUNKING_CONFIG) -> bool:
    """Determine if agentic chunking is appropriate for this document."""
    
    if not config.get("enabled", True):
        return False
    
    # Estimate tokens (rough)
    est_tokens = len(document_text) // 4
    
    if est_tokens > config.get("max_document_tokens", 50000):
        return False  # Too large, use fallback
    
    if est_tokens < config.get("min_document_tokens", 100):
        return False  # Too small, not worth it
    
    return True
```

---

## Implementation Order

1. **Add AgenticChunker class** (30 min)
   - Prompt template
   - Claude API call
   - JSON parsing

2. **Add verification functions** (20 min)
   - verify_chunk_integrity
   - verify_all_chunks

3. **Add fallback logic** (15 min)
   - chunk_with_fallback
   - Structure-aware fallback

4. **Add document type detection** (15 min)
   - get_document_type_hints

5. **Integrate with ingest flow** (20 min)
   - Update ingest command
   - Add method selection

6. **Add logging** (15 min)
   - log_chunking_result
   - Audit log file

7. **Streamlit integration** (30 min)
   - Chunking method selection
   - Audit page

8. **Test end-to-end** (30 min)
   - Test with different document types
   - Verify no hallucinations
   - Check verification catches issues

---

## Success Criteria

- [ ] Claude extracts ONLY verbatim content from documents
- [ ] Verification catches any hallucinated content
- [ ] Fallback works when agentic chunking fails
- [ ] Different document types chunked appropriately
- [ ] All chunking decisions logged for audit
- [ ] Streamlit shows chunking method and quality
- [ ] Cost stays under $5 for full re-index

---

## Testing Checklist

Before deploying, verify with these tests:

### Test 1: Verbatim Extraction
- Ingest a document with unique phrases
- Verify every chunk's content exists exactly in source
- Check no words were added or changed

### Test 2: Entity Grounding
- Check all extracted entities appear in source document
- Verify no inferred entities were added

### Test 3: Hallucination Detection
- Manually introduce a "hallucinated" chunk
- Verify verification function catches it

### Test 4: Fallback Works
- Test with a document that causes parsing failure
- Verify fallback produces valid chunks

### Test 5: Document Types
- Test with: PDF, PPTX, DOCX, transcript, markdown
- Verify appropriate splitting for each type
