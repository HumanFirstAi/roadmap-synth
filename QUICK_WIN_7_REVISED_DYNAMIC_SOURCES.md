# Quick Win #7 (Revised): Dynamic Source Reference Lookup

## Changed Approach

**Before:** Rely on LLM to output source references at question generation time
**After:** Dynamically search graph + chunks when displaying a question

This is more reliable because:
- Works for existing questions immediately
- Doesn't depend on LLM following instructions perfectly
- Always shows the most relevant current sources
- Sources update if you ingest new documents

---

## How It Works

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  Question: "Can Catalog API migration be done in Q2?"       │
│                                                             │
│                           │                                 │
│                           ▼                                 │
│              ┌─────────────────────────┐                   │
│              │   Search Pipeline       │                   │
│              └─────────────────────────┘                   │
│                           │                                 │
│          ┌────────────────┼────────────────┐               │
│          ▼                ▼                ▼               │
│   ┌────────────┐  ┌────────────┐  ┌────────────┐          │
│   │  Semantic  │  │  Keyword   │  │   Graph    │          │
│   │  Search    │  │  Match     │  │  Traverse  │          │
│   │ (embeddings)│  │ (terms)   │  │ (related)  │          │
│   └────────────┘  └────────────┘  └────────────┘          │
│          │                │                │               │
│          └────────────────┼────────────────┘               │
│                           ▼                                 │
│              ┌─────────────────────────┐                   │
│              │   Rank & Deduplicate    │                   │
│              └─────────────────────────┘                   │
│                           │                                 │
│                           ▼                                 │
│              ┌─────────────────────────┐                   │
│              │   Top 5 Sources         │                   │
│              │   with relevance scores │                   │
│              └─────────────────────────┘                   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Implementation

### Core Function: Find Sources for Question

```python
def find_sources_for_question(question: dict, max_sources: int = 5) -> list[dict]:
    """
    Dynamically find source references for a question by searching
    the graph and chunks.
    
    Returns list of source references ranked by relevance.
    """
    
    question_text = question.get("question", "")
    context = question.get("context", "")
    query = f"{question_text} {context}".strip()
    
    if not query:
        return []
    
    sources = []
    seen_ids = set()
    
    # === METHOD 1: Semantic search on chunks (LanceDB) ===
    try:
        chunk_results = search_chunks_semantic(query, limit=10)
        
        for chunk in chunk_results:
            chunk_id = chunk.get("id", chunk.get("chunk_id", ""))
            if chunk_id in seen_ids:
                continue
            seen_ids.add(chunk_id)
            
            sources.append({
                "type": "chunk",
                "id": chunk_id,
                "source_name": chunk.get("source_name", chunk.get("source_path", "Unknown")),
                "lens": chunk.get("lens", "unknown"),
                "content": chunk.get("content", chunk.get("text", ""))[:300],
                "similarity": chunk.get("_distance", chunk.get("similarity", 0)),
                "search_method": "semantic"
            })
    except Exception as e:
        print(f"Semantic search error: {e}")
    
    # === METHOD 2: Keyword extraction and search ===
    try:
        keywords = extract_key_terms_simple(question_text)
        
        if keywords:
            keyword_results = search_chunks_keyword(keywords, limit=10)
            
            for chunk in keyword_results:
                chunk_id = chunk.get("id", chunk.get("chunk_id", ""))
                if chunk_id in seen_ids:
                    continue
                seen_ids.add(chunk_id)
                
                # Calculate keyword match score
                content = chunk.get("content", chunk.get("text", "")).lower()
                matches = sum(1 for kw in keywords if kw.lower() in content)
                match_score = matches / len(keywords) if keywords else 0
                
                sources.append({
                    "type": "chunk",
                    "id": chunk_id,
                    "source_name": chunk.get("source_name", chunk.get("source_path", "Unknown")),
                    "lens": chunk.get("lens", "unknown"),
                    "content": chunk.get("content", chunk.get("text", ""))[:300],
                    "similarity": match_score,
                    "search_method": "keyword",
                    "matched_terms": [kw for kw in keywords if kw.lower() in content]
                })
    except Exception as e:
        print(f"Keyword search error: {e}")
    
    # === METHOD 3: Graph traversal (if question linked to roadmap items) ===
    try:
        graph = load_unified_graph()
        
        if graph:
            # Search assessments
            for assess_id, assessment in graph.node_indices.get("assessment", {}).items():
                if assess_id in seen_ids:
                    continue
                
                # Check if assessment summary relates to question
                summary = assessment.summary if hasattr(assessment, 'summary') else assessment.get("summary", "")
                if any(kw.lower() in summary.lower() for kw in extract_key_terms_simple(question_text)):
                    seen_ids.add(assess_id)
                    sources.append({
                        "type": "assessment",
                        "id": assess_id,
                        "source_name": f"{assessment.assessment_type.title() if hasattr(assessment, 'assessment_type') else 'Unknown'} Assessment",
                        "lens": "assessment",
                        "content": summary[:300],
                        "similarity": 0.7,  # Base relevance for keyword match
                        "search_method": "graph"
                    })
            
            # Search gaps
            for gap_id, gap in graph.node_indices.get("gap", {}).items():
                if gap_id in seen_ids:
                    continue
                
                description = gap.description if hasattr(gap, 'description') else gap.get("description", "")
                if any(kw.lower() in description.lower() for kw in extract_key_terms_simple(question_text)):
                    seen_ids.add(gap_id)
                    sources.append({
                        "type": "gap",
                        "id": gap_id,
                        "source_name": f"Gap: {description[:50]}",
                        "lens": "gap",
                        "content": description[:300],
                        "similarity": 0.6,
                        "search_method": "graph"
                    })
            
            # Search roadmap items
            for item_id, item in graph.node_indices.get("roadmap_item", {}).items():
                if item_id in seen_ids:
                    continue
                
                name = item.name if hasattr(item, 'name') else item.get("name", "")
                description = item.description if hasattr(item, 'description') else item.get("description", "")
                combined = f"{name} {description}"
                
                if any(kw.lower() in combined.lower() for kw in extract_key_terms_simple(question_text)):
                    seen_ids.add(item_id)
                    sources.append({
                        "type": "roadmap_item",
                        "id": item_id,
                        "source_name": f"Roadmap: {name}",
                        "lens": "roadmap",
                        "content": description[:300],
                        "similarity": 0.65,
                        "search_method": "graph"
                    })
    except Exception as e:
        print(f"Graph search error: {e}")
    
    # === RANK AND RETURN TOP SOURCES ===
    
    # Sort by similarity/relevance score
    sources.sort(key=lambda x: x.get("similarity", 0), reverse=True)
    
    # Return top N
    return sources[:max_sources]


def extract_key_terms_simple(text: str) -> list[str]:
    """
    Simple keyword extraction without external dependencies.
    Extracts nouns and important terms.
    """
    
    # Common stop words to filter out
    stop_words = {
        "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
        "have", "has", "had", "do", "does", "did", "will", "would", "could",
        "should", "may", "might", "can", "this", "that", "these", "those",
        "i", "you", "he", "she", "it", "we", "they", "what", "which", "who",
        "when", "where", "why", "how", "all", "each", "every", "both", "few",
        "more", "most", "other", "some", "such", "no", "not", "only", "own",
        "same", "so", "than", "too", "very", "just", "also", "now", "here",
        "there", "then", "once", "and", "or", "but", "if", "because", "as",
        "until", "while", "of", "at", "by", "for", "with", "about", "against",
        "between", "into", "through", "during", "before", "after", "above",
        "below", "to", "from", "up", "down", "in", "out", "on", "off", "over",
        "under", "again", "further", "our", "your", "their", "its"
    }
    
    # Tokenize (simple split, remove punctuation)
    import re
    words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
    
    # Filter stop words and short words
    keywords = [w for w in words if w not in stop_words and len(w) > 2]
    
    # Count frequency and return top terms
    from collections import Counter
    counts = Counter(keywords)
    
    # Return top 8 most frequent terms
    return [word for word, count in counts.most_common(8)]


def search_chunks_semantic(query: str, limit: int = 10) -> list[dict]:
    """
    Semantic search on chunks using embeddings.
    Uses LanceDB if available.
    """
    
    try:
        # Get embedding for query
        query_embedding = get_embedding(query)
        
        # Search LanceDB
        table = get_lancedb_table()
        if table is None:
            return []
        
        results = table.search(query_embedding).limit(limit).to_list()
        
        return results
    except Exception as e:
        print(f"Semantic search error: {e}")
        return []


def search_chunks_keyword(keywords: list[str], limit: int = 10) -> list[dict]:
    """
    Keyword-based search on chunks.
    Falls back to scanning if no full-text index.
    """
    
    try:
        table = get_lancedb_table()
        if table is None:
            return []
        
        # Get all chunks and filter (not efficient but works)
        df = table.to_pandas()
        
        results = []
        for _, row in df.iterrows():
            content = str(row.get("content", row.get("text", ""))).lower()
            matches = sum(1 for kw in keywords if kw.lower() in content)
            
            if matches > 0:
                results.append({
                    "id": row.get("id", row.get("chunk_id", "")),
                    "source_name": row.get("source_name", row.get("source_path", "")),
                    "lens": row.get("lens", ""),
                    "content": row.get("content", row.get("text", "")),
                    "similarity": matches / len(keywords),
                    "matched_count": matches
                })
        
        # Sort by match count
        results.sort(key=lambda x: x["matched_count"], reverse=True)
        
        return results[:limit]
    except Exception as e:
        print(f"Keyword search error: {e}")
        return []
```

### Updated UI: Render Sources for Question

```python
def render_question_source_references(question: dict):
    """
    Render source references for a question.
    Dynamically finds sources if not cached.
    """
    
    # Check for cached sources (to avoid re-searching on every render)
    cache_key = f"sources_{question['id']}"
    
    if cache_key in st.session_state:
        sources = st.session_state[cache_key]
    else:
        # Find sources dynamically
        with st.spinner("Finding source references..."):
            sources = find_sources_for_question(question, max_sources=5)
            st.session_state[cache_key] = sources
    
    if not sources:
        st.caption("No relevant sources found")
        
        # Offer to refresh
        if st.button("🔄 Search Again", key=f"refresh_sources_{question['id']}"):
            if cache_key in st.session_state:
                del st.session_state[cache_key]
            st.rerun()
        return
    
    st.markdown(f"**📚 Source References** ({len(sources)} found)")
    
    for i, source in enumerate(sources):
        source_type = source.get("type", "chunk")
        source_id = source.get("id", "unknown")
        source_name = source.get("source_name", "Unknown Source")
        lens = source.get("lens", "")
        content = source.get("content", "")
        similarity = source.get("similarity", 0)
        search_method = source.get("search_method", "unknown")
        matched_terms = source.get("matched_terms", [])
        
        # Type icon
        type_icons = {
            "chunk": "📄",
            "assessment": "🔬",
            "roadmap_item": "🗺️",
            "gap": "⚠️",
            "decision": "✅"
        }
        icon = type_icons.get(source_type, "📎")
        
        # Method badge
        method_badges = {
            "semantic": "🎯",
            "keyword": "🔤",
            "graph": "🕸️"
        }
        method_badge = method_badges.get(search_method, "")
        
        with st.container(border=True):
            # Header row
            col1, col2 = st.columns([4, 1])
            
            with col1:
                st.markdown(f"{icon} **{source_name}**")
                
                meta_parts = []
                if lens and lens not in ["assessment", "gap", "roadmap"]:
                    meta_parts.append(f"Lens: {lens}")
                meta_parts.append(f"ID: {source_id[:20]}...")
                meta_parts.append(f"{method_badge} {search_method}")
                
                st.caption(" | ".join(meta_parts))
            
            with col2:
                # Relevance score
                score_pct = min(similarity * 100, 100)
                if score_pct >= 70:
                    st.success(f"{score_pct:.0f}%")
                elif score_pct >= 40:
                    st.warning(f"{score_pct:.0f}%")
                else:
                    st.caption(f"{score_pct:.0f}%")
            
            # Content excerpt
            if content:
                # Highlight matched terms if available
                display_content = content[:250]
                if len(content) > 250:
                    display_content += "..."
                
                st.markdown(f"*\"{display_content}\"*")
            
            # Matched keywords (for keyword search)
            if matched_terms:
                st.caption(f"Matched: {', '.join(matched_terms)}")
    
    # Refresh button
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("🔄 Refresh", key=f"refresh_sources_{question['id']}"):
            if cache_key in st.session_state:
                del st.session_state[cache_key]
            st.rerun()
```

### Full Question Card with Dynamic Sources

```python
def render_question_card_enhanced(q: dict):
    """
    Render a question card with dynamic source lookup and validation.
    """
    
    priority_icons = {
        "critical": "🔴",
        "high": "🟠",
        "medium": "🟡",
        "low": "🟢"
    }
    priority_icon = priority_icons.get(q.get("priority", "medium"), "⚪")
    
    # Validation status
    validation = q.get("validation")
    if validation and validation.get("validated"):
        val_icon = "👍" if validation.get("is_accurate") else "👎"
        val_status = "validated"
    else:
        val_icon = "⬜"
        val_status = "pending"
    
    with st.container(border=True):
        # Header
        col1, col2, col3 = st.columns([5, 1, 1])
        
        with col1:
            st.markdown(f"{priority_icon} **{q['question']}**")
            
            meta_parts = [
                q.get("audience", "unknown"),
                q.get("category", "unknown"),
                f"from: {q.get('source', 'synthesis')}"
            ]
            st.caption(" | ".join(meta_parts))
        
        with col2:
            st.caption(f"Status: {q.get('status', 'pending')}")
        
        with col3:
            st.markdown(f"### {val_icon}")
        
        # Expandable details
        with st.expander("📚 View Sources & Validate"):
            
            # Context (if any)
            if q.get("context"):
                st.info(f"**Context:** {q['context']}")
            
            st.divider()
            
            # Dynamic source references
            render_question_source_references(q)
            
            st.divider()
            
            # Validation UI
            render_question_validation(q)
        
        # Quick actions row
        if q.get("status") == "pending":
            col1, col2, col3 = st.columns([2, 2, 2])
            
            with col1:
                if st.button("✏️ Answer", key=f"ans_{q['id']}"):
                    st.session_state.answering_question_id = q["id"]
                    st.rerun()
            
            with col2:
                # Quick validate buttons
                if not (validation and validation.get("validated")):
                    if st.button("👍", key=f"quick_up_{q['id']}"):
                        save_question_validation(q["id"], True, "Quick validation", "")
                        st.rerun()
            
            with col3:
                if not (validation and validation.get("validated")):
                    if st.button("👎", key=f"quick_down_{q['id']}"):
                        save_question_validation(q["id"], False, "Quick validation", "")
                        st.rerun()
```

---

## Integration

Replace the existing question card rendering in the Questions page with `render_question_card_enhanced()`.

```python
elif page == "❓ Open Questions":
    st.title("❓ Open Questions")
    
    # Validation stats
    render_validation_stats()
    
    st.divider()
    
    # Filters
    # ... existing filter code ...
    
    # Question list - use enhanced cards
    for q in filtered_questions:
        render_question_card_enhanced(q)
```

---

## Caching Strategy

To avoid re-searching on every page render:

1. **Session state cache**: Store found sources in `st.session_state[f"sources_{question_id}"]`
2. **Refresh button**: Allow user to re-search if sources seem wrong
3. **Cache invalidation**: Clear cache when graph is synced or documents ingested

```python
def invalidate_source_cache():
    """Clear all cached source references."""
    keys_to_delete = [k for k in st.session_state.keys() if k.startswith("sources_")]
    for key in keys_to_delete:
        del st.session_state[key]
```

Call this after:
- Graph sync
- Document ingestion
- Roadmap generation

---

## Testing Checklist

- [ ] Questions with no prior sources now show dynamically found sources
- [ ] Semantic search returns relevant chunks
- [ ] Keyword search finds matches
- [ ] Graph search finds related assessments/gaps/roadmap items
- [ ] Relevance scores display correctly
- [ ] Refresh button re-searches
- [ ] Cache prevents redundant searches
- [ ] Validation still works
- [ ] Quick validate buttons work

---

## Estimated Time

- Core search function: 25 min
- Keyword extraction: 10 min
- UI updates: 15 min
- Cache handling: 10 min
- Integration: 10 min

**Total: ~1 hour**
