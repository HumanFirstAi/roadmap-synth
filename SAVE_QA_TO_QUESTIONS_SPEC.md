# Add Q&A to Open Questions Specification

## Overview

After asking a question in "Ask Your Roadmap" and receiving an answer, the user can save that Q&A to the Open Questions list for follow-up and decision-making.

This creates a feedback loop:
```
Ask Question → Get Answer → Save to Open Questions → Review → Make Decision
```

---

## User Flow

```
┌─────────────────────────────────────────────────────────────┐
│  💬 Ask Your Roadmap                                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  **You asked:** What's my biggest gap for CPQ?             │
│                                                             │
│  ### Answer                                                 │
│  The biggest gap for CPQ is **real-time competitive        │
│  price monitoring**...                                      │
│                                                             │
│  ─────────────────────────────────────────────────────────  │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  📌 Save to Open Questions                          │   │
│  │                                                      │   │
│  │  This will add the Q&A to your Open Questions list  │   │
│  │  for follow-up and decision-making.                 │   │
│  │                                                      │   │
│  │  Audience: [Leadership ▼]                           │   │
│  │  Category: [Direction ▼]                            │   │
│  │  Priority: [High ▼]                                 │   │
│  │                                                      │   │
│  │  ☑️ Include synthesized answer as context           │   │
│  │  ☑️ Link source references                          │   │
│  │                                                      │   │
│  │  [Save to Open Questions]                           │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ✅ Saved as q_20250115_143022                             │
│  [View in Open Questions →]                                │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Data Model

### Question Created from Q&A

```python
{
    "id": "q_20250115_143022",
    "question": "What's my biggest gap for CPQ?",  # Original query
    "audience": "leadership",
    "category": "direction",
    "priority": "high",
    "status": "pending",
    "created_at": "2025-01-15T14:30:22Z",
    
    # === Q&A SPECIFIC FIELDS ===
    
    "generation": {
        "type": "user_query",  # New type: user asked this directly
        "source": "ask_roadmap",
        "generated_at": "2025-01-15T14:30:22Z",
    },
    
    # The synthesized answer becomes context
    "context": "Based on analysis: The biggest gap for CPQ is real-time competitive price monitoring. This was identified in competitive assessment when Competitor X launched AI-powered pricing. Architecture assessment confirms no infrastructure exists. Related decision: Pricing timeline set to Q3.",
    
    # Link to the full synthesized answer
    "synthesized_answer": {
        "answer": "The biggest gap for CPQ is **real-time competitive price monitoring**...",
        "confidence": "high",
        "generated_at": "2025-01-15T14:30:22Z",
        "retrieval_stats": {
            "total_sources": 47,
            "decisions": 3,
            "gaps": 5,
            "chunks": 30
        }
    },
    
    # Source references from the answer
    "source_references": [
        {
            "type": "gap",
            "id": "gap_007",
            "source_name": "Real-time competitive pricing gap",
            "relevance": "Primary gap identified"
        },
        {
            "type": "assessment",
            "id": "analysis_001",
            "source_name": "Competitive Assessment",
            "relevance": "Identified the competitive threat"
        },
        {
            "type": "decision",
            "id": "dec_003",
            "source_name": "Pricing timeline Q3",
            "relevance": "Current timeline decision"
        }
    ],
    
    # Track that this came from a Q&A session
    "qa_session": {
        "query": "What's my biggest gap for CPQ?",
        "topic_filter": "CPQ",
        "session_timestamp": "2025-01-15T14:30:00Z"
    },
    
    # Validation (starts empty)
    "validation": null
}
```

---

## Implementation

### Save Q&A to Open Questions Function

```python
def save_qa_to_open_questions(
    query: str,
    answer: SynthesizedAnswer,
    audience: str,
    category: str,
    priority: str,
    include_answer_as_context: bool = True,
    link_sources: bool = True,
    topic_filter: str = None
) -> dict:
    """
    Save a Q&A from Ask Your Roadmap to Open Questions.
    
    Args:
        query: The original question asked
        answer: The synthesized answer object
        audience: engineering | leadership | product
        category: Question category
        priority: critical | high | medium | low
        include_answer_as_context: Whether to include the answer as context
        link_sources: Whether to link the source references
        topic_filter: The topic filter that was applied (if any)
    
    Returns:
        The created question dict
    """
    
    question_id = f"q_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # Build context from answer
    context = ""
    if include_answer_as_context:
        # Summarize the answer for context (strip markdown, limit length)
        context = summarize_answer_for_context(answer.answer, max_length=500)
    
    # Build source references
    source_references = []
    if link_sources:
        for source in answer.sources_cited:
            source_references.append({
                "type": source.get("type", "chunk"),
                "id": source.get("id", "unknown"),
                "source_name": get_source_display_name(source),
                "relevance": source.get("relevance", ""),
                "source_path": source.get("full_data", {}).get("source_path", "")
            })
    
    # Create the question
    question = {
        "id": question_id,
        "question": query,
        "audience": audience,
        "category": category,
        "priority": priority,
        "status": "pending",
        "created_at": datetime.now().isoformat(),
        
        "generation": {
            "type": "user_query",
            "source": "ask_roadmap",
            "generated_at": datetime.now().isoformat(),
        },
        
        "context": context,
        
        "synthesized_answer": {
            "answer": answer.answer,
            "confidence": answer.confidence,
            "generated_at": datetime.now().isoformat(),
            "retrieval_stats": answer.retrieval_stats
        },
        
        "source_references": source_references,
        
        "qa_session": {
            "query": query,
            "topic_filter": topic_filter,
            "session_timestamp": datetime.now().isoformat()
        },
        
        "validation": None
    }
    
    # Save to questions list
    questions = load_questions()
    questions.append(question)
    save_questions(questions)
    
    return question


def summarize_answer_for_context(answer: str, max_length: int = 500) -> str:
    """
    Summarize the synthesized answer for use as question context.
    Strips markdown and limits length.
    """
    
    import re
    
    # Remove markdown formatting
    text = answer
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)  # Bold
    text = re.sub(r'\*([^*]+)\*', r'\1', text)      # Italic
    text = re.sub(r'\[Source:[^\]]+\]', '', text)   # Source citations
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)  # Links
    text = re.sub(r'#{1,6}\s*', '', text)           # Headers
    text = re.sub(r'\n{2,}', ' ', text)             # Multiple newlines
    text = re.sub(r'\s{2,}', ' ', text)             # Multiple spaces
    
    text = text.strip()
    
    # Truncate if needed
    if len(text) > max_length:
        text = text[:max_length - 3] + "..."
    
    return f"Based on analysis: {text}"


def get_source_display_name(source: dict) -> str:
    """Get a display name for a source reference."""
    
    full_data = source.get("full_data", {})
    source_type = source.get("type", "chunk")
    
    if source_type == "decision":
        return full_data.get("decision", "Decision")[:50]
    elif source_type == "gap":
        return full_data.get("description", "Gap")[:50]
    elif source_type == "assessment":
        return f"{full_data.get('assessment_type', 'Unknown').title()} Assessment"
    elif source_type == "chunk":
        return full_data.get("source_name", "Source document")
    else:
        return source.get("id", "Unknown source")
```

### UI Component: Save to Open Questions

```python
def render_save_to_questions_ui(query: str, answer: SynthesizedAnswer, topic_filter: str = None):
    """
    Render the UI for saving a Q&A to Open Questions.
    """
    
    st.divider()
    
    with st.container(border=True):
        st.markdown("### 📌 Save to Open Questions")
        st.caption("Add this Q&A to your Open Questions list for follow-up and decision-making.")
        
        # Check if already saved
        existing = find_existing_qa_question(query)
        if existing:
            st.info(f"This question was already saved as **{existing['id']}**")
            if st.button("View in Open Questions →"):
                st.session_state.current_page = "❓ Open Questions"
                st.session_state.highlight_question = existing['id']
                st.rerun()
            return
        
        # Options
        col1, col2, col3 = st.columns(3)
        
        with col1:
            audience = st.selectbox(
                "Audience",
                ["leadership", "engineering", "product"],
                index=0,
                key="save_qa_audience"
            )
        
        with col2:
            category = st.selectbox(
                "Category",
                ["direction", "investment", "feasibility", "trade-off", 
                 "alignment", "timing", "scope", "dependency"],
                index=0,
                key="save_qa_category"
            )
        
        with col3:
            priority = st.selectbox(
                "Priority",
                ["high", "critical", "medium", "low"],
                index=0,
                key="save_qa_priority"
            )
        
        # Include options
        col1, col2 = st.columns(2)
        
        with col1:
            include_answer = st.checkbox(
                "Include synthesized answer as context",
                value=True,
                key="save_qa_include_answer",
                help="The answer will be saved as context for the question"
            )
        
        with col2:
            link_sources = st.checkbox(
                "Link source references",
                value=True,
                key="save_qa_link_sources",
                help="Source citations will be linked to the question"
            )
        
        # Save button
        if st.button("📌 Save to Open Questions", type="primary"):
            saved_question = save_qa_to_open_questions(
                query=query,
                answer=answer,
                audience=audience,
                category=category,
                priority=priority,
                include_answer_as_context=include_answer,
                link_sources=link_sources,
                topic_filter=topic_filter
            )
            
            st.success(f"✅ Saved as **{saved_question['id']}**")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("View in Open Questions →"):
                    st.session_state.current_page = "❓ Open Questions"
                    st.session_state.highlight_question = saved_question['id']
                    st.rerun()
            with col2:
                if st.button("Make Decision Now →"):
                    st.session_state.current_page = "❓ Open Questions"
                    st.session_state.answering_question_id = saved_question['id']
                    st.rerun()


def find_existing_qa_question(query: str) -> dict | None:
    """Check if this query was already saved as a question."""
    
    questions = load_questions()
    
    for q in questions:
        # Check if it came from ask_roadmap
        if q.get("generation", {}).get("source") == "ask_roadmap":
            # Check if query matches
            if q.get("qa_session", {}).get("query", "").lower() == query.lower():
                return q
    
    return None
```

### Update Ask Your Roadmap Page

```python
def render_ask_roadmap_page():
    """Render the Ask Your Roadmap conversational interface."""
    
    st.title("💬 Ask Your Roadmap")
    
    # ... existing query input UI ...
    
    # Display answer if available
    if "last_answer" in st.session_state:
        answer = st.session_state.last_answer
        query = st.session_state.last_query
        topic = st.session_state.get("last_topic_filter", None)
        
        render_answer_display(answer, query)
        
        # ADD THIS: Save to Open Questions UI
        render_save_to_questions_ui(query, answer, topic)
```

### Display Q&A Questions Differently in Open Questions

```python
def render_question_card_enhanced(q: dict):
    """Render question card with special handling for Q&A questions."""
    
    generation = q.get("generation", {})
    gen_type = generation.get("type", "unknown")
    gen_source = generation.get("source", "unknown")
    
    # Determine badge
    if gen_type == "user_query" and gen_source == "ask_roadmap":
        type_badge = "💬 From Q&A"
        has_synthesized_answer = True
    elif gen_type == "llm":
        type_badge = "🤖 LLM"
        has_synthesized_answer = False
    elif gen_type == "derived":
        type_badge = f"🔍 Derived"
        has_synthesized_answer = False
    else:
        type_badge = "❓ Unknown"
        has_synthesized_answer = False
    
    # ... existing card rendering ...
    
    with st.container(border=True):
        # Header
        col1, col2, col3 = st.columns([4, 2, 1])
        
        with col1:
            priority_icons = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}
            icon = priority_icons.get(q.get("priority", "medium"), "⚪")
            st.markdown(f"{icon} **{q['question']}**")
        
        with col2:
            if gen_type == "user_query":
                st.success(type_badge)
            elif gen_type == "derived":
                st.warning(type_badge)
            else:
                st.info(type_badge)
        
        with col3:
            # Validation status
            validation = q.get("validation")
            if validation and validation.get("validated"):
                st.markdown("👍" if validation.get("is_accurate") else "👎")
            else:
                st.markdown("⬜")
        
        st.caption(f"{q.get('audience', 'unknown')} | {q.get('category', 'unknown')}")
        
        # Expandable details
        with st.expander("View Details"):
            # Context
            if q.get("context"):
                st.info(f"**Context:** {q['context']}")
            
            # === NEW: Show synthesized answer for Q&A questions ===
            if has_synthesized_answer and q.get("synthesized_answer"):
                st.divider()
                render_qa_synthesized_answer(q["synthesized_answer"])
            
            st.divider()
            
            # Source references
            render_question_source_references(q)
            
            st.divider()
            
            # Validation
            render_question_validation(q)
        
        # Actions
        if q.get("status") == "pending":
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✏️ Answer & Decide", key=f"ans_{q['id']}"):
                    st.session_state.answering_question_id = q["id"]
                    st.rerun()
            with col2:
                # For Q&A questions, offer to re-ask
                if has_synthesized_answer:
                    if st.button("🔄 Re-Ask", key=f"reask_{q['id']}"):
                        st.session_state.roadmap_query = q["question"]
                        st.session_state.current_page = "💬 Ask Your Roadmap"
                        st.rerun()


def render_qa_synthesized_answer(synthesized_answer: dict):
    """Render the synthesized answer from a Q&A session."""
    
    st.markdown("**📝 Synthesized Answer (from Q&A)**")
    
    confidence = synthesized_answer.get("confidence", "medium")
    confidence_icons = {"high": "🟢", "medium": "🟡", "low": "🟠"}
    st.caption(f"Confidence: {confidence_icons.get(confidence, '⚪')} {confidence}")
    
    # Show answer (collapsed for space)
    answer_text = synthesized_answer.get("answer", "No answer recorded")
    
    # Truncate for display
    if len(answer_text) > 500:
        st.markdown(answer_text[:500] + "...")
        with st.expander("Show full answer"):
            st.markdown(answer_text)
    else:
        st.markdown(answer_text)
    
    # Stats
    stats = synthesized_answer.get("retrieval_stats", {})
    if stats:
        st.caption(
            f"Generated from {stats.get('total_sources', 0)} sources | "
            f"Decisions: {stats.get('decisions', 0)} | "
            f"Gaps: {stats.get('gaps', 0)}"
        )
```

### Filter by Generation Source

Add a filter to show only Q&A questions:

```python
def render_question_filters():
    """Render question filters including Q&A filter."""
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        status_filter = st.selectbox(
            "Status",
            ["pending", "answered", "obsolete", "all"],
            index=0
        )
    
    with col2:
        audience_filter = st.selectbox(
            "Audience",
            ["all", "engineering", "leadership", "product"],
            index=0
        )
    
    with col3:
        # Updated to include Q&A
        type_filter = st.selectbox(
            "Source",
            ["all", "user_query", "llm", "derived"],  # user_query = Q&A
            index=0,
            format_func=lambda x: {
                "all": "All Sources",
                "user_query": "💬 From Q&A",
                "llm": "🤖 LLM Generated",
                "derived": "🔍 Derived"
            }.get(x, x)
        )
    
    with col4:
        priority_filter = st.selectbox(
            "Priority",
            ["all", "critical", "high", "medium", "low"],
            index=0
        )
    
    return {
        "status": status_filter,
        "audience": audience_filter,
        "type": type_filter,
        "priority": priority_filter
    }
```

---

## Full Workflow

```
┌─────────────────────────────────────────────────────────────┐
│  1. USER ASKS QUESTION                                      │
│                                                             │
│  💬 Ask Your Roadmap                                        │
│  "What's my biggest gap for CPQ?"                          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────┐
│  2. SYSTEM GENERATES ANSWER                                 │
│                                                             │
│  Retrieves from LanceDB → Chunk Graph → Unified Graph      │
│  Synthesizes answer via Claude                              │
│  Shows sources, related questions, follow-ups              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────┐
│  3. USER SAVES TO OPEN QUESTIONS                            │
│                                                             │
│  📌 Save to Open Questions                                  │
│  - Sets audience: Leadership                                │
│  - Sets priority: High                                      │
│  - Includes synthesized answer as context                  │
│  - Links source references                                  │
│                                                             │
│  [Save to Open Questions]                                   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────┐
│  4. QUESTION APPEARS IN OPEN QUESTIONS                      │
│                                                             │
│  ❓ Open Questions                                          │
│                                                             │
│  🟠 What's my biggest gap for CPQ?          💬 From Q&A    │
│     leadership | direction                                  │
│                                                             │
│     📝 Synthesized Answer:                                  │
│     The biggest gap is real-time competitive pricing...    │
│                                                             │
│     📚 Sources: gap_007, analysis_001, dec_003             │
│                                                             │
│     [✏️ Answer & Decide]  [🔄 Re-Ask]                      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────┐
│  5. USER MAKES DECISION                                     │
│                                                             │
│  Answer: "We will accelerate the pricing engine to Q2      │
│  and add contractor support"                                │
│                                                             │
│  ☑️ Create decision from this answer                       │
│                                                             │
│  Decision: Accelerate pricing engine to Q2                  │
│  Owner: Jonathan                                            │
│                                                             │
│  [Submit Answer]                                            │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────┐
│  6. DECISION LOGGED & GRAPH UPDATED                         │
│                                                             │
│  ✅ Decision Log                                            │
│                                                             │
│  dec_009: Accelerate pricing engine to Q2                  │
│  Resolves: q_20250115_143022                               │
│  Overrides: dec_003 (previous Q3 timeline)                 │
│                                                             │
│  [🔄 Sync Graph] to update knowledge base                  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Testing Checklist

- [ ] "Save to Open Questions" UI appears after answer
- [ ] Audience/category/priority selectors work
- [ ] Include answer checkbox works
- [ ] Link sources checkbox works
- [ ] Save button creates question with correct fields
- [ ] Question appears in Open Questions list
- [ ] Q&A questions show "💬 From Q&A" badge
- [ ] Synthesized answer displays in question detail
- [ ] Source references are linked
- [ ] "Re-Ask" button navigates back to Ask Your Roadmap
- [ ] Filter by source "From Q&A" works
- [ ] Duplicate detection prevents saving same query twice
- [ ] Making decision from Q&A question works
- [ ] Decision links back to original question

---

## Estimated Time

- save_qa_to_open_questions function: 20 min
- UI component: 20 min
- Question card updates: 15 min
- Filter updates: 10 min
- Testing: 15 min

**Total: ~1.5 hours**
