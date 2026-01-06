# Conversational Content Filtering Specification

## Problem

Transcript ingestion is creating chunks with no substantive content:
- Greetings and small talk ("Good, yeah, that's mine, but it's okay")
- Filler phrases and speaker transitions
- Partial sentences without context
- Content that adds noise to retrieval and synthesis

These low-value chunks:
1. Pollute the vector index
2. Get retrieved when they shouldn't
3. Create false TOPIC_OVERLAP connections (341 connections based on "so", "speaker", "we")
4. Waste tokens in synthesis context

## Solution

Add a content quality filter that evaluates chunks before indexing, with special handling for conversational content.

---

## Implementation

### 1. Content Quality Scoring

```python
def score_chunk_quality(chunk: dict) -> dict:
    """
    Score a chunk's content quality.
    Returns score (0-1) and reasons.
    """
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
    
    if lens == "team-conversational":
        
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
            import re
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
            import re
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
```

### 2. Filter During Ingestion

Update the ingestion flow to filter low-quality chunks:

```python
def ingest_with_quality_filter(
    chunks: list[dict],
    min_quality_score: float = 0.4,
    log_filtered: bool = True
) -> tuple[list[dict], list[dict]]:
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
                print(f"Filtered chunk (score={quality['score']:.2f}): {chunk['content'][:100]}...")
                print(f"  Reasons: {', '.join(quality['reasons'])}")
    
    return accepted, filtered
```

### 3. Update Agentic Chunking Prompt

Add quality guidance to the agentic chunking prompt:

```markdown
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
```
Speaker 1 0:05 Good, yeah, that's mine, but it's okay, good man, yeah. So listen, I appreciate you making the time.
```

**Example — GOOD chunk:**
```
Speaker 1 (Errol) discussing Acquisition roadmap: "The big problem has been Tam's voice being too loud in prioritization. We need to align people to one mental model first. Once the mental model is established, then we can have productive debates about what goes in which quarter."
```
```

### 4. Post-Ingestion Cleanup Command

Add a CLI command to clean existing low-quality chunks:

```python
@app.command()
def cleanup(
    min_score: float = typer.Option(0.4, help="Minimum quality score to keep"),
    dry_run: bool = typer.Option(True, help="Show what would be removed without removing")
):
    """Remove low-quality chunks from the index."""
    
    # Load all chunks
    table = get_table()
    df = table.to_pandas()
    
    to_remove = []
    to_keep = []
    
    for _, row in df.iterrows():
        chunk = row.to_dict()
        quality = score_chunk_quality(chunk)
        
        if quality["score"] < min_score:
            to_remove.append({
                "id": chunk["id"],
                "score": quality["score"],
                "reasons": quality["reasons"],
                "preview": chunk["content"][:100]
            })
        else:
            to_keep.append(chunk["id"])
    
    # Report
    console.print(f"\n[bold]Quality Analysis[/bold]")
    console.print(f"Total chunks: {len(df)}")
    console.print(f"Would keep: {len(to_keep)} ({len(to_keep)/len(df):.0%})")
    console.print(f"Would remove: {len(to_remove)} ({len(to_remove)/len(df):.0%})")
    
    if to_remove:
        console.print(f"\n[bold]Chunks to remove:[/bold]")
        for item in to_remove[:20]:  # Show first 20
            console.print(f"  Score {item['score']:.2f}: {item['preview']}...")
            console.print(f"    Reasons: {', '.join(item['reasons'])}")
        
        if len(to_remove) > 20:
            console.print(f"  ... and {len(to_remove) - 20} more")
    
    if not dry_run:
        # Actually remove
        for item in to_remove:
            table.delete(f"id = '{item['id']}'")
        
        console.print(f"\n[green]Removed {len(to_remove)} low-quality chunks[/green]")
        
        # Rebuild graph
        console.print("Rebuilding context graph...")
        rebuild_context_graph()
        console.print("[green]Graph rebuilt[/green]")
    else:
        console.print(f"\n[yellow]Dry run — no changes made. Use --no-dry-run to apply.[/yellow]")
```

### 5. Update Key Term Extraction

The current key term extraction is finding low-value terms like "so", "speaker", "we". Fix this:

```python
def extract_key_terms(text: str, top_n: int = 10) -> list[str]:
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
```

### 6. Streamlit Quality Dashboard

Add a quality overview to the dashboard:

```python
# In dashboard page

st.subheader("Content Quality")

# Get quality distribution
chunks = get_all_chunks()
scores = [score_chunk_quality(c)["score"] for c in chunks]

col1, col2, col3 = st.columns(3)
col1.metric("Avg Quality Score", f"{sum(scores)/len(scores):.2f}")
col2.metric("Low Quality (<0.4)", len([s for s in scores if s < 0.4]))
col3.metric("High Quality (>0.7)", len([s for s in scores if s > 0.7]))

# Quality by lens
st.write("**Quality by Lens:**")
lens_quality = {}
for chunk in chunks:
    lens = chunk.get("lens", "unknown")
    score = score_chunk_quality(chunk)["score"]
    if lens not in lens_quality:
        lens_quality[lens] = []
    lens_quality[lens].append(score)

for lens, scores in lens_quality.items():
    avg = sum(scores) / len(scores)
    low = len([s for s in scores if s < 0.4])
    st.write(f"- {lens}: avg {avg:.2f}, {low} low-quality chunks")

# Cleanup button
if st.button("🧹 Cleanup Low-Quality Chunks"):
    st.warning("This will remove chunks with quality score < 0.4")
    if st.button("Confirm Cleanup"):
        removed = cleanup_low_quality_chunks(min_score=0.4)
        st.success(f"Removed {removed} chunks")
        st.experimental_rerun()
```

---

## Implementation Order

1. **Add score_chunk_quality function** (15 min)
2. **Update key term extraction** to exclude fillers (10 min)
3. **Add quality filter to ingestion flow** (15 min)
4. **Update agentic chunking prompt** with conversational rules (10 min)
5. **Add cleanup CLI command** (15 min)
6. **Add Streamlit quality dashboard** (15 min)
7. **Test with conversational transcripts** (15 min)
8. **Run cleanup on existing index** (5 min)

---

## After Implementation

Run cleanup on existing data:

```bash
# See what would be removed
uv run python roadmap.py cleanup --dry-run

# Actually remove
uv run python roadmap.py cleanup --no-dry-run
```

Then re-check the View Chunks page — low-value chunks should be gone.

---

## Expected Outcome

| Metric | Before | After |
|--------|--------|-------|
| team-conversational chunks | ~200 | ~120 (40% reduction) |
| Avg TOPIC_OVERLAP connections | 341 | ~50 (based on real topics) |
| Key terms quality | "so, speaker, we" | "roadmap, acquisition, priority" |
| Retrieval relevance | Noisy | Focused on substance |
