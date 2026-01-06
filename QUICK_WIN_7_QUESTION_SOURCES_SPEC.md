# Quick Win #7: Question Source References & Validation Feedback

## Overview

Add two features to Open Questions:

1. **Source References** — Show the source chunks/assessments that led to each question being generated
2. **Validation Feedback** — Thumbs up/down to log whether the question was accurately generated from the sources

---

## Why This Matters

Currently, questions are generated but you can't see *why* they were generated. This makes it hard to:
- Validate if the question is grounded in real source content
- Trust the question generation process
- Improve prompt quality over time

With source references and feedback:
- You can click through to see exactly what triggered the question
- You can mark questions as accurate or inaccurate
- Over time, you build a dataset of feedback to improve generation

---

## Data Model Changes

### Updated Question Structure

```python
# Existing fields
{
    "id": "q_eng_001",
    "question": "Can Catalog API migration be completed in Q2?",
    "audience": "engineering",
    "category": "feasibility",
    "priority": "high",
    "context": "Multiple roadmap items depend on Catalog.",
    "status": "pending",
    "source": "architecture_assessment",  # Existing - which process generated it
    "created_at": "2025-01-15T10:30:00Z",
    
    # NEW FIELDS
    "source_references": [
        {
            "type": "chunk",                    # chunk, assessment, roadmap_item
            "id": "chunk_123",
            "source_name": "Catalog Roadmap",
            "lens": "team-structured",
            "excerpt": "Q2 timeline is aggressive given current team capacity...",
            "relevance": "Direct mention of Q2 feasibility concern"
        },
        {
            "type": "chunk",
            "id": "chunk_456",
            "source_name": "Engineering Standup Notes",
            "lens": "team-conversational",
            "excerpt": "Sarah mentioned we're already stretched thin...",
            "relevance": "Capacity constraint mentioned"
        },
        {
            "type": "assessment",
            "id": "align_001",
            "source_name": "Architecture Alignment Assessment",
            "excerpt": "Catalog GA has partial architecture support, timing behind...",
            "relevance": "Assessment identified timing risk"
        }
    ],
    
    "validation": {
        "validated": true,                      # Has user validated?
        "is_accurate": true,                    # Thumbs up (true) or down (false)
        "validated_by": "Jonathan",
        "validated_at": "2025-01-15T14:30:00Z",
        "feedback_note": "Good question, sources clearly support this concern"  # Optional
    }
}
```

---

## Implementation

### 1. Update Question Generation to Include Sources

When questions are generated (in synthesis, assessments, etc.), capture the source references.

**Add to question generation prompts:**

```python
QUESTION_GENERATION_ADDENDUM = """
For each question you generate, include source references:

"source_references": [
    {
        "type": "chunk|assessment|roadmap_item",
        "id": "The ID of the source",
        "source_name": "Human-readable name",
        "excerpt": "The specific text (max 200 chars) that led to this question",
        "relevance": "Brief explanation of why this source is relevant"
    }
]

Include 1-3 source references per question. Only include sources that directly support the question being asked.
"""
```

**Modify `add_questions_to_system()` to preserve sources:**

```python
def add_questions_to_system(questions: list[dict], source: str, source_references: list[dict] = None):
    """Add questions with source references."""
    
    existing = load_questions()
    
    for q in questions:
        question_data = {
            "id": f"q_{datetime.now().strftime('%Y%m%d%H%M%S')}_{len(existing)}",
            "question": q["question"],
            "audience": q.get("audience", "product"),
            "category": q.get("category", "direction"),
            "priority": q.get("priority", "medium"),
            "context": q.get("context", ""),
            "status": "pending",
            "source": source,
            "created_at": datetime.now().isoformat(),
            
            # NEW: Include source references
            "source_references": q.get("source_references", source_references or []),
            
            # NEW: Validation placeholder
            "validation": None
        }
        existing.append(question_data)
    
    save_questions(existing)
```

### 2. Render Source References in Questions UI

**Add this function:**

```python
def render_question_source_references(question: dict):
    """Render source references for a question."""
    
    sources = question.get("source_references", [])
    
    if not sources:
        st.caption("No source references available")
        return
    
    st.markdown(f"**📚 Source References** ({len(sources)})")
    
    for i, ref in enumerate(sources):
        ref_type = ref.get("type", "unknown")
        ref_id = ref.get("id", "unknown")
        source_name = ref.get("source_name", "Unknown Source")
        excerpt = ref.get("excerpt", "")
        relevance = ref.get("relevance", "")
        lens = ref.get("lens", "")
        
        # Type icon
        type_icon = {
            "chunk": "📄",
            "assessment": "🔬",
            "roadmap_item": "🗺️"
        }.get(ref_type, "📎")
        
        with st.container(border=True):
            # Header
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown(f"{type_icon} **{source_name}**")
                if lens:
                    st.caption(f"Lens: {lens} | ID: {ref_id}")
            with col2:
                # Link to view full source
                if st.button("View", key=f"view_ref_{question['id']}_{i}"):
                    st.session_state.viewing_source = {
                        "type": ref_type,
                        "id": ref_id
                    }
            
            # Excerpt
            if excerpt:
                st.markdown(f"*\"{excerpt}\"*")
            
            # Relevance explanation
            if relevance:
                st.caption(f"↳ {relevance}")
```

### 3. Render Validation Feedback UI

**Add this function:**

```python
def render_question_validation(question: dict):
    """Render validation feedback UI for a question."""
    
    validation = question.get("validation")
    
    st.markdown("**✅ Validate Question**")
    
    if validation and validation.get("validated"):
        # Already validated - show result
        is_accurate = validation.get("is_accurate")
        validated_by = validation.get("validated_by", "Unknown")
        validated_at = validation.get("validated_at", "")[:10]
        
        if is_accurate:
            st.success(f"👍 Validated as accurate by {validated_by} on {validated_at}")
        else:
            st.error(f"👎 Validated as inaccurate by {validated_by} on {validated_at}")
        
        if validation.get("feedback_note"):
            st.caption(f"Note: {validation['feedback_note']}")
        
        # Option to re-validate
        if st.button("Re-validate", key=f"reval_{question['id']}"):
            st.session_state.revalidating_question = question["id"]
            st.rerun()
    
    else:
        # Not yet validated - show validation UI
        st.caption("Review the source references above, then indicate if this question is well-grounded:")
        
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            thumbs_up = st.button("👍 Accurate", key=f"thumbs_up_{question['id']}", use_container_width=True)
        
        with col2:
            thumbs_down = st.button("👎 Inaccurate", key=f"thumbs_down_{question['id']}", use_container_width=True)
        
        with col3:
            feedback_note = st.text_input(
                "Feedback (optional)",
                key=f"feedback_{question['id']}",
                placeholder="Why accurate/inaccurate?"
            )
        
        validated_by = st.text_input(
            "Your name",
            key=f"validator_{question['id']}",
            value=st.session_state.get("last_validator", "")
        )
        
        if thumbs_up or thumbs_down:
            if not validated_by:
                st.warning("Please enter your name")
            else:
                # Save validation
                save_question_validation(
                    question_id=question["id"],
                    is_accurate=thumbs_up,
                    validated_by=validated_by,
                    feedback_note=feedback_note
                )
                st.session_state.last_validator = validated_by
                st.success("Validation saved!")
                st.rerun()


def save_question_validation(question_id: str, is_accurate: bool, validated_by: str, feedback_note: str = ""):
    """Save validation feedback for a question."""
    
    questions = load_questions()
    
    for q in questions:
        if q["id"] == question_id:
            q["validation"] = {
                "validated": True,
                "is_accurate": is_accurate,
                "validated_by": validated_by,
                "validated_at": datetime.now().isoformat(),
                "feedback_note": feedback_note
            }
            break
    
    save_questions(questions)
```

### 4. Enhanced Question Card with Sources

**Update the question card rendering:**

```python
def render_question_card_with_sources(q: dict):
    """Render a question card with source references and validation."""
    
    priority_icon = {
        "critical": "🔴",
        "high": "🟠", 
        "medium": "🟡",
        "low": "🟢"
    }.get(q.get("priority", "medium"), "⚪")
    
    # Validation status icon
    validation = q.get("validation")
    if validation and validation.get("validated"):
        val_icon = "👍" if validation.get("is_accurate") else "👎"
    else:
        val_icon = "❓"
    
    with st.container(border=True):
        # Header row
        col1, col2, col3 = st.columns([4, 1, 1])
        
        with col1:
            st.markdown(f"{priority_icon} **{q['question'][:80]}{'...' if len(q['question']) > 80 else ''}**")
            st.caption(f"Category: {q.get('category', 'unknown')} | Source: {q.get('source', 'unknown')}")
        
        with col2:
            # Source count badge
            source_count = len(q.get("source_references", []))
            st.caption(f"📚 {source_count}")
        
        with col3:
            st.caption(val_icon)
        
        # Expandable details
        with st.expander("View Details & Validate"):
            # Context
            if q.get("context"):
                st.markdown(f"**Context:** {q['context']}")
            
            st.divider()
            
            # Source references
            render_question_source_references(q)
            
            st.divider()
            
            # Validation
            render_question_validation(q)
            
            st.divider()
            
            # Answer button (if pending)
            if q.get("status") == "pending":
                if st.button("Answer This Question", key=f"answer_{q['id']}", type="primary"):
                    st.session_state.answering_question_id = q["id"]
                    st.rerun()
```

### 5. Validation Statistics

**Add to dashboard or questions page:**

```python
def render_validation_stats():
    """Render validation statistics."""
    
    questions = load_questions()
    
    total = len(questions)
    validated = [q for q in questions if q.get("validation", {}).get("validated")]
    accurate = [q for q in validated if q["validation"].get("is_accurate")]
    inaccurate = [q for q in validated if not q["validation"].get("is_accurate")]
    
    st.subheader("📊 Question Validation Stats")
    
    col1, col2, col3, col4 = st.columns(4)
    
    col1.metric("Total Questions", total)
    col2.metric("Validated", len(validated))
    col3.metric("👍 Accurate", len(accurate))
    col4.metric("👎 Inaccurate", len(inaccurate))
    
    if validated:
        accuracy_rate = len(accurate) / len(validated) * 100
        st.progress(accuracy_rate / 100)
        st.caption(f"Accuracy Rate: {accuracy_rate:.1f}%")
    
    # Recent inaccurate (for review)
    if inaccurate:
        with st.expander(f"⚠️ Review Inaccurate Questions ({len(inaccurate)})"):
            for q in inaccurate[:5]:
                st.markdown(f"- **{q['question'][:60]}...**")
                st.caption(f"  Feedback: {q['validation'].get('feedback_note', 'No feedback')}")
```

---

## Integration Points

### In Questions Page

Replace or enhance the existing question list:

```python
elif page == "❓ Open Questions":
    st.title("❓ Open Questions")
    
    # ADD: Validation stats
    render_validation_stats()
    
    st.divider()
    
    # Existing filters...
    
    # Replace existing question cards with enhanced version
    for q in filtered_questions:
        render_question_card_with_sources(q)
```

### In Question Generation (Synthesis, Assessments)

When generating questions, update the prompt to include source references:

```python
# In synthesis prompt or assessment prompt, add:
QUESTION_OUTPUT_FORMAT = """
For each question, include:
{
    "question": "The question text",
    "audience": "engineering|leadership|product",
    "category": "feasibility|investment|direction|trade-off|alignment|timing|scope|dependency",
    "priority": "critical|high|medium|low",
    "context": "Why this question arose",
    "source_references": [
        {
            "type": "chunk",
            "id": "chunk_id",
            "source_name": "Document name",
            "lens": "lens type",
            "excerpt": "Exact quote (max 200 chars) that triggered this question",
            "relevance": "Why this supports the question"
        }
    ]
}
"""
```

---

## Backfilling Existing Questions

For questions already generated without source references, add a backfill function:

```python
def backfill_question_sources(question_id: str):
    """Attempt to find source references for an existing question."""
    
    questions = load_questions()
    question = next((q for q in questions if q["id"] == question_id), None)
    
    if not question:
        return None
    
    # Search for relevant chunks
    graph = load_unified_graph()
    
    if not graph:
        return None
    
    # Use question text to find similar chunks
    query = question["question"]
    results = retrieve_with_authority(query, graph, include_superseded=False)
    
    source_references = []
    
    # Add top relevant chunks
    for chunk in results.get("chunks", [])[:3]:
        data = chunk.get("data", chunk)
        source_references.append({
            "type": "chunk",
            "id": chunk.get("id", data.get("id", "unknown")),
            "source_name": data.get("source_name", "Unknown"),
            "lens": data.get("lens", "unknown"),
            "excerpt": data.get("content", data.get("text", ""))[:200],
            "relevance": f"Similarity: {chunk.get('similarity', 0):.2f}"
        })
    
    # Add relevant assessments
    for assessment in results.get("assessments", [])[:2]:
        data = assessment.get("data", assessment)
        source_references.append({
            "type": "assessment",
            "id": assessment.get("id", data.get("id", "unknown")),
            "source_name": f"{data.get('assessment_type', 'Unknown').title()} Assessment",
            "excerpt": data.get("summary", "")[:200],
            "relevance": f"Similarity: {assessment.get('similarity', 0):.2f}"
        })
    
    # Update question
    question["source_references"] = source_references
    save_questions(questions)
    
    return source_references


def backfill_all_question_sources():
    """Backfill source references for all questions missing them."""
    
    questions = load_questions()
    backfilled = 0
    
    for q in questions:
        if not q.get("source_references"):
            refs = backfill_question_sources(q["id"])
            if refs:
                backfilled += 1
    
    return backfilled
```

**Add backfill button to Questions page:**

```python
# In questions page
with st.expander("🔧 Maintenance"):
    if st.button("Backfill Source References"):
        with st.spinner("Finding source references for existing questions..."):
            count = backfill_all_question_sources()
        st.success(f"Backfilled {count} questions")
        st.rerun()
```

---

## Testing Checklist

- [ ] Questions display source references
- [ ] Can expand to see full source details
- [ ] Thumbs up/down buttons work
- [ ] Validation saves correctly
- [ ] Validation stats display on page
- [ ] Already-validated questions show their status
- [ ] Re-validate option works
- [ ] Backfill function finds relevant sources
- [ ] New questions generated with source references

---

## Estimated Time

- Source references display: 20 min
- Validation UI: 15 min
- Validation stats: 10 min
- Backfill function: 15 min
- Integration: 15 min

**Total: ~1.25 hours**
