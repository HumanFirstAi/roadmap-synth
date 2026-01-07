# Ask Your Roadmap - Conversational Q&A Specification

## Overview

Add a conversational interface to query your roadmap knowledge base. Users can ask natural language questions and receive synthesized answers with source citations.

**Examples:**
- "What's my biggest gap for CPQ?"
- "What questions need answers before Catalog GA?"
- "Summarize competitive threats to Experiences"
- "What did we decide about pricing timeline?"
- "Give me a status update on Acquisition"

---

## Architecture

### Data Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│  User Query: "What's my biggest gap for CPQ?"                              │
│                                                                             │
│         │                                                                   │
│         ▼                                                                   │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  STEP 1: Query Analysis                                              │   │
│  │                                                                      │   │
│  │  Extract:                                                            │   │
│  │  - Topic/Team: CPQ                                                   │   │
│  │  - Intent: find gaps                                                 │   │
│  │  - Modifier: biggest/most critical                                   │   │
│  │  - Keywords: ["CPQ", "gap", "priority"]                             │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│         │                                                                   │
│         ▼                                                                   │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  STEP 2: Multi-Source Retrieval                                      │   │
│  │                                                                      │   │
│  │  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐                │   │
│  │  │   LanceDB   │   │   Chunk     │   │  Unified    │                │   │
│  │  │   Vector    │ → │   Context   │ → │  Knowledge  │                │   │
│  │  │   Search    │   │   Graph     │   │  Graph      │                │   │
│  │  └─────────────┘   └─────────────┘   └─────────────┘                │   │
│  │        │                 │                 │                         │   │
│  │        ▼                 ▼                 ▼                         │   │
│  │   Similar chunks    Expanded chunks    Decisions, Gaps,             │   │
│  │   by embedding      via relationships  Questions, Items             │   │
│  │                                                                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│         │                                                                   │
│         ▼                                                                   │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  STEP 3: Context Assembly                                            │   │
│  │                                                                      │   │
│  │  Organize by authority:                                              │   │
│  │  1. Active Decisions (highest)                                       │   │
│  │  2. Answered Questions                                               │   │
│  │  3. Assessments                                                      │   │
│  │  4. Roadmap Items                                                    │   │
│  │  5. Gaps                                                             │   │
│  │  6. Source Chunks                                                    │   │
│  │  7. Pending Questions (lowest)                                       │   │
│  │                                                                      │   │
│  │  Filter out superseded content                                       │   │
│  │  Prioritize topic-relevant content                                   │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│         │                                                                   │
│         ▼                                                                   │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  STEP 4: Synthesis via Claude                                        │   │
│  │                                                                      │   │
│  │  Prompt includes:                                                    │   │
│  │  - User's question                                                   │   │
│  │  - Retrieved context (structured)                                    │   │
│  │  - Instructions to cite sources                                      │   │
│  │  - Instruction to be direct and actionable                          │   │
│  │                                                                      │   │
│  │  Output:                                                             │   │
│  │  - Direct answer                                                     │   │
│  │  - Supporting evidence                                               │   │
│  │  - Source citations                                                  │   │
│  │  - Related questions/next steps                                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│         │                                                                   │
│         ▼                                                                   │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  STEP 5: Response Display                                            │   │
│  │                                                                      │   │
│  │  - Formatted answer                                                  │   │
│  │  - Expandable source citations                                       │   │
│  │  - Related pending questions                                         │   │
│  │  - Suggested follow-up queries                                       │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Implementation

### Step 1: Query Analysis

```python
from dataclasses import dataclass
from enum import Enum

class QueryIntent(Enum):
    FIND_GAPS = "find_gaps"
    FIND_QUESTIONS = "find_questions"
    FIND_DECISIONS = "find_decisions"
    STATUS_UPDATE = "status_update"
    COMPETITIVE_ANALYSIS = "competitive_analysis"
    TIMELINE_QUERY = "timeline_query"
    DEPENDENCY_QUERY = "dependency_query"
    BLOCKER_QUERY = "blocker_query"
    RECOMMENDATION = "recommendation"
    GENERAL = "general"


@dataclass
class ParsedQuery:
    original_query: str
    intent: QueryIntent
    topics: list[str]          # CPQ, Catalog, Experiences, Acquisition, etc.
    keywords: list[str]        # Extracted search terms
    modifiers: list[str]       # biggest, latest, critical, etc.
    time_context: str | None   # today, this quarter, before GA, etc.


# Known topics/teams for filtering
KNOWN_TOPICS = {
    "cpq": ["cpq", "configure price quote", "pricing", "quoting"],
    "catalog": ["catalog", "catalogue", "product catalog"],
    "experiences": ["experiences", "experience builder", "cx"],
    "acquisition": ["acquisition", "customer acquisition", "onboarding"],
    "platform": ["platform", "infrastructure", "core"],
}


def parse_query(query: str) -> ParsedQuery:
    """
    Parse a natural language query to extract intent and filters.
    """
    
    query_lower = query.lower()
    
    # Detect intent
    intent = detect_intent(query_lower)
    
    # Extract topics
    topics = extract_topics(query_lower)
    
    # Extract keywords
    keywords = extract_key_terms_simple(query)
    
    # Extract modifiers
    modifiers = extract_modifiers(query_lower)
    
    # Extract time context
    time_context = extract_time_context(query_lower)
    
    return ParsedQuery(
        original_query=query,
        intent=intent,
        topics=topics,
        keywords=keywords,
        modifiers=modifiers,
        time_context=time_context
    )


def detect_intent(query: str) -> QueryIntent:
    """Detect the intent of the query."""
    
    intent_patterns = {
        QueryIntent.FIND_GAPS: ["gap", "gaps", "missing", "lack", "need", "don't have"],
        QueryIntent.FIND_QUESTIONS: ["question", "questions", "unanswered", "pending", "need to answer", "need answers"],
        QueryIntent.FIND_DECISIONS: ["decide", "decided", "decision", "decisions", "chose", "chosen"],
        QueryIntent.STATUS_UPDATE: ["status", "update", "progress", "where are we", "how is", "how's"],
        QueryIntent.COMPETITIVE_ANALYSIS: ["competitor", "competitive", "competition", "threat", "market"],
        QueryIntent.TIMELINE_QUERY: ["when", "timeline", "schedule", "deadline", "date", "timing"],
        QueryIntent.DEPENDENCY_QUERY: ["depend", "dependency", "dependencies", "blocked by", "waiting for", "prerequisite"],
        QueryIntent.BLOCKER_QUERY: ["blocker", "blocking", "blocked", "obstacle", "impediment", "risk"],
        QueryIntent.RECOMMENDATION: ["should", "recommend", "suggestion", "advice", "best", "priority", "prioritize"],
    }
    
    for intent, patterns in intent_patterns.items():
        if any(pattern in query for pattern in patterns):
            return intent
    
    return QueryIntent.GENERAL


def extract_topics(query: str) -> list[str]:
    """Extract known topics/teams from query."""
    
    found_topics = []
    
    for topic, aliases in KNOWN_TOPICS.items():
        if any(alias in query for alias in aliases):
            found_topics.append(topic)
    
    return found_topics


def extract_modifiers(query: str) -> list[str]:
    """Extract modifiers that affect ranking/filtering."""
    
    modifiers = []
    
    modifier_patterns = {
        "priority": ["biggest", "most important", "critical", "top", "main", "primary"],
        "recency": ["latest", "recent", "new", "newest", "current"],
        "severity": ["worst", "severe", "serious", "major"],
        "scope": ["all", "every", "complete", "full"],
    }
    
    for modifier_type, patterns in modifier_patterns.items():
        if any(pattern in query for pattern in patterns):
            modifiers.append(modifier_type)
    
    return modifiers


def extract_time_context(query: str) -> str | None:
    """Extract time context from query."""
    
    time_patterns = {
        "today": ["today", "right now", "currently"],
        "this_week": ["this week"],
        "this_quarter": ["this quarter", "q1", "q2", "q3", "q4"],
        "before_ga": ["before ga", "before launch", "pre-launch"],
        "next_quarter": ["next quarter"],
    }
    
    for time_context, patterns in time_patterns.items():
        if any(pattern in query.lower() for pattern in patterns):
            return time_context
    
    return None
```

### Step 2: Multi-Source Retrieval

```python
@dataclass
class RetrievalResult:
    """Results from multi-source retrieval."""
    
    # By authority level
    decisions: list[dict]
    answered_questions: list[dict]
    assessments: list[dict]
    roadmap_items: list[dict]
    gaps: list[dict]
    chunks: list[dict]
    pending_questions: list[dict]
    
    # Metadata
    total_sources: int
    retrieval_time_ms: int
    topic_filter_applied: list[str]


def retrieve_full_context(
    parsed_query: ParsedQuery,
    max_chunks: int = 30,
    max_per_category: int = 10
) -> RetrievalResult:
    """
    Retrieve context from all three data stores.
    
    Flow: LanceDB → Chunk Context Graph → Unified Knowledge Graph
    """
    
    import time
    start_time = time.time()
    
    query_text = parsed_query.original_query
    topics = parsed_query.topics
    keywords = parsed_query.keywords
    
    # === STAGE 1: LanceDB Semantic Search ===
    
    query_embedding = get_embedding(query_text)
    
    # Search LanceDB
    table = get_lancedb_table()
    if table:
        semantic_results = table.search(query_embedding).limit(max_chunks).to_list()
    else:
        semantic_results = []
    
    # Filter by topic if specified
    if topics:
        semantic_results = filter_by_topic(semantic_results, topics)
    
    initial_chunk_ids = [r.get("id", r.get("chunk_id")) for r in semantic_results]
    
    # === STAGE 2: Expand via Chunk Context Graph ===
    
    chunk_graph = load_chunk_context_graph()
    expanded_chunk_ids = set(initial_chunk_ids)
    
    if chunk_graph:
        for chunk_id in initial_chunk_ids[:10]:  # Expand top 10
            # Get connected chunks
            connected = expand_via_chunk_graph(
                chunk_graph, 
                chunk_id, 
                max_hops=1,
                edge_types=["SIMILAR_TO", "SAME_SOURCE", "TOPIC_OVERLAP"]
            )
            expanded_chunk_ids.update(connected)
    
    # Limit expanded set
    expanded_chunk_ids = list(expanded_chunk_ids)[:max_chunks]
    
    # === STAGE 3: Traverse Unified Knowledge Graph ===
    
    unified_graph = load_unified_graph()
    
    # Initialize result containers
    decisions = []
    answered_questions = []
    assessments = []
    roadmap_items = []
    gaps = []
    chunks = []
    pending_questions = []
    
    seen_ids = set()
    
    if unified_graph:
        # Get all related nodes via traversal
        related_nodes = traverse_unified_graph(
            unified_graph,
            seed_ids=expanded_chunk_ids,
            max_hops=2
        )
        
        # Categorize by type
        for node_id, node_data in related_nodes.items():
            if node_id in seen_ids:
                continue
            seen_ids.add(node_id)
            
            node_type = node_data.get("node_type", "chunk")
            
            # Apply topic filter
            if topics and not node_matches_topics(node_data, topics):
                continue
            
            if node_type == "decision":
                if node_data.get("status") == "active":
                    decisions.append(node_data)
            
            elif node_type == "question":
                if node_data.get("status") == "answered":
                    answered_questions.append(node_data)
                elif node_data.get("status") == "pending":
                    pending_questions.append(node_data)
            
            elif node_type == "assessment":
                assessments.append(node_data)
            
            elif node_type == "roadmap_item":
                roadmap_items.append(node_data)
            
            elif node_type == "gap":
                gaps.append(node_data)
            
            elif node_type == "chunk":
                # Check if superseded
                if not node_data.get("superseded_by"):
                    chunks.append(node_data)
    
    # Also get chunks from semantic results not yet included
    for result in semantic_results:
        chunk_id = result.get("id", result.get("chunk_id"))
        if chunk_id not in seen_ids:
            seen_ids.add(chunk_id)
            chunks.append(result)
    
    # === STAGE 4: Rank and Limit ===
    
    # Sort by relevance/severity/priority
    decisions = sorted(decisions, key=lambda x: x.get("created_at", ""), reverse=True)[:max_per_category]
    gaps = sorted(gaps, key=lambda x: gap_severity_score(x), reverse=True)[:max_per_category]
    pending_questions = sorted(pending_questions, key=lambda x: priority_score(x), reverse=True)[:max_per_category]
    roadmap_items = sorted(roadmap_items, key=lambda x: horizon_score(x))[:max_per_category]
    
    elapsed_ms = int((time.time() - start_time) * 1000)
    
    return RetrievalResult(
        decisions=decisions,
        answered_questions=answered_questions[:max_per_category],
        assessments=assessments[:max_per_category],
        roadmap_items=roadmap_items,
        gaps=gaps,
        chunks=chunks[:max_chunks],
        pending_questions=pending_questions,
        total_sources=len(seen_ids),
        retrieval_time_ms=elapsed_ms,
        topic_filter_applied=topics
    )


def expand_via_chunk_graph(
    graph,
    chunk_id: str,
    max_hops: int = 1,
    edge_types: list[str] = None
) -> set[str]:
    """
    Expand from a chunk via the chunk context graph.
    Returns set of connected chunk IDs.
    """
    
    connected = set()
    
    if chunk_id not in graph:
        return connected
    
    # BFS expansion
    queue = [(chunk_id, 0)]
    visited = {chunk_id}
    
    while queue:
        current_id, hops = queue.pop(0)
        
        if hops >= max_hops:
            continue
        
        # Get neighbors
        for neighbor in graph.neighbors(current_id):
            if neighbor in visited:
                continue
            
            # Check edge type if filter specified
            if edge_types:
                edge_data = graph.edges.get((current_id, neighbor), {})
                if edge_data.get("edge_type") not in edge_types:
                    continue
            
            visited.add(neighbor)
            connected.add(neighbor)
            queue.append((neighbor, hops + 1))
    
    return connected


def traverse_unified_graph(
    graph,
    seed_ids: list[str],
    max_hops: int = 2
) -> dict[str, dict]:
    """
    Traverse unified knowledge graph from seed nodes.
    Returns dict of node_id -> node_data.
    """
    
    results = {}
    visited = set()
    queue = [(id, 0) for id in seed_ids if id in graph.graph]
    
    while queue:
        node_id, hops = queue.pop(0)
        
        if node_id in visited:
            continue
        
        visited.add(node_id)
        
        if node_id not in graph.graph:
            continue
        
        # Get node data
        node = graph.graph.nodes[node_id]
        node_data = node.get("data", {})
        node_data["node_type"] = node.get("node_type", "chunk")
        node_data["id"] = node_id
        
        results[node_id] = node_data
        
        if hops >= max_hops:
            continue
        
        # Add neighbors
        for neighbor in graph.graph.neighbors(node_id):
            if neighbor not in visited:
                queue.append((neighbor, hops + 1))
        
        for neighbor in graph.graph.predecessors(node_id):
            if neighbor not in visited:
                queue.append((neighbor, hops + 1))
    
    return results


def filter_by_topic(results: list[dict], topics: list[str]) -> list[dict]:
    """Filter results to those matching specified topics."""
    
    filtered = []
    topic_terms = []
    
    for topic in topics:
        topic_terms.extend(KNOWN_TOPICS.get(topic, [topic]))
    
    for result in results:
        content = result.get("content", result.get("text", "")).lower()
        source_name = result.get("source_name", "").lower()
        
        if any(term in content or term in source_name for term in topic_terms):
            filtered.append(result)
    
    return filtered if filtered else results  # Fall back to all if no matches


def node_matches_topics(node_data: dict, topics: list[str]) -> bool:
    """Check if a node matches the specified topics."""
    
    topic_terms = []
    for topic in topics:
        topic_terms.extend(KNOWN_TOPICS.get(topic, [topic]))
    
    # Check various fields
    searchable_text = " ".join([
        str(node_data.get("name", "")),
        str(node_data.get("description", "")),
        str(node_data.get("content", "")),
        str(node_data.get("text", "")),
        str(node_data.get("question", "")),
        str(node_data.get("decision", "")),
        str(node_data.get("summary", "")),
    ]).lower()
    
    return any(term in searchable_text for term in topic_terms)


def gap_severity_score(gap: dict) -> int:
    """Score a gap by severity for sorting."""
    severity_scores = {"critical": 4, "significant": 3, "moderate": 2, "minor": 1}
    return severity_scores.get(gap.get("severity", ""), 0)


def priority_score(item: dict) -> int:
    """Score by priority for sorting."""
    priority_scores = {"critical": 4, "high": 3, "medium": 2, "low": 1}
    return priority_scores.get(item.get("priority", ""), 0)


def horizon_score(item: dict) -> int:
    """Score by horizon for sorting (lower = sooner)."""
    horizon_scores = {"now": 1, "next": 2, "later": 3, "future": 4}
    return horizon_scores.get(item.get("horizon", ""), 5)
```

### Step 3: Context Assembly

```python
def assemble_context_for_synthesis(
    parsed_query: ParsedQuery,
    retrieval: RetrievalResult
) -> str:
    """
    Assemble retrieved context into a structured prompt for Claude.
    Organized by authority level.
    """
    
    sections = []
    
    # Header
    sections.append(f"## CONTEXT FOR QUERY: \"{parsed_query.original_query}\"")
    sections.append("")
    
    if parsed_query.topics:
        sections.append(f"**Topic Filter Applied:** {', '.join(parsed_query.topics)}")
        sections.append("")
    
    # === LEVEL 1: Decisions (Highest Authority) ===
    if retrieval.decisions:
        sections.append("### ACTIVE DECISIONS (Highest Authority)")
        sections.append("These are resolved decisions that override other content.")
        sections.append("")
        
        for dec in retrieval.decisions:
            sections.append(f"**{dec.get('id', 'Unknown')}:** {dec.get('decision', '')}")
            if dec.get('rationale'):
                sections.append(f"  Rationale: {dec['rationale'][:200]}")
            if dec.get('implications'):
                sections.append(f"  Implications: {', '.join(dec['implications'][:3])}")
            sections.append("")
    
    # === LEVEL 2: Answered Questions ===
    if retrieval.answered_questions:
        sections.append("### ANSWERED QUESTIONS")
        sections.append("")
        
        for q in retrieval.answered_questions:
            sections.append(f"**Q:** {q.get('question', '')}")
            sections.append(f"**A:** {q.get('answer', 'Answered')[:200]}")
            sections.append("")
    
    # === LEVEL 3: Assessments ===
    if retrieval.assessments:
        sections.append("### ASSESSMENTS")
        sections.append("")
        
        for assess in retrieval.assessments:
            assess_type = assess.get('assessment_type', 'Unknown')
            sections.append(f"**{assess_type.title()} Assessment ({assess.get('id', '')}):**")
            sections.append(f"  {assess.get('summary', 'No summary')[:300]}")
            sections.append("")
    
    # === LEVEL 4: Roadmap Items ===
    if retrieval.roadmap_items:
        sections.append("### ROADMAP ITEMS")
        sections.append("")
        
        for item in retrieval.roadmap_items:
            horizon = item.get('horizon', 'unknown')
            sections.append(f"**{item.get('name', 'Unknown')}** [{horizon}]")
            sections.append(f"  {item.get('description', '')[:200]}")
            if item.get('owner'):
                sections.append(f"  Owner: {item['owner']}")
            sections.append("")
    
    # === LEVEL 5: Gaps ===
    if retrieval.gaps:
        sections.append("### IDENTIFIED GAPS")
        sections.append("")
        
        for gap in retrieval.gaps:
            severity = gap.get('severity', 'unknown')
            sections.append(f"**[{severity.upper()}]** {gap.get('description', '')[:200]}")
            if gap.get('identified_by_assessment'):
                sections.append(f"  Source: {gap['identified_by_assessment']}")
            sections.append("")
    
    # === LEVEL 6: Source Chunks ===
    if retrieval.chunks:
        sections.append("### SOURCE DOCUMENTS")
        sections.append("")
        
        for chunk in retrieval.chunks[:15]:  # Limit for token budget
            source_name = chunk.get('source_name', 'Unknown')
            lens = chunk.get('lens', 'unknown')
            content = chunk.get('content', chunk.get('text', ''))[:300]
            
            sections.append(f"**{source_name}** ({lens}) [ID: {chunk.get('id', 'unknown')}]")
            sections.append(f"  \"{content}\"")
            sections.append("")
    
    # === LEVEL 7: Pending Questions ===
    if retrieval.pending_questions:
        sections.append("### PENDING QUESTIONS (Unresolved)")
        sections.append("")
        
        for q in retrieval.pending_questions:
            priority = q.get('priority', 'medium')
            sections.append(f"**[{priority}]** {q.get('question', '')}")
            sections.append("")
    
    return "\n".join(sections)
```

### Step 4: Synthesis via Claude

```python
@dataclass
class SynthesizedAnswer:
    """The final synthesized answer."""
    
    answer: str
    confidence: str  # high, medium, low
    sources_cited: list[dict]
    related_questions: list[dict]
    suggested_followups: list[str]
    retrieval_stats: dict


def synthesize_answer(
    parsed_query: ParsedQuery,
    retrieval: RetrievalResult,
    context: str
) -> SynthesizedAnswer:
    """
    Use Claude to synthesize an answer from the retrieved context.
    """
    
    # Build the synthesis prompt
    prompt = f"""You are an expert analyst helping a product leader understand their roadmap.

The user asked: "{parsed_query.original_query}"

{context}

---

## YOUR TASK

Provide a direct, actionable answer to the user's question based ONLY on the context provided above.

Guidelines:
1. Be direct and specific - answer the question first, then provide supporting details
2. Cite sources using [Source: ID] format (e.g., [Source: chunk_123] or [Source: dec_001])
3. Respect the authority hierarchy - decisions override older source content
4. If there are gaps or uncertainties, acknowledge them
5. If there are pending questions related to the user's query, mention them
6. Suggest 2-3 follow-up questions the user might want to ask

## RESPONSE FORMAT

Respond in this JSON format:
```json
{{
    "answer": "Your direct answer to the question. Use markdown formatting. Cite sources inline.",
    "confidence": "high|medium|low",
    "key_sources": [
        {{"id": "source_id", "type": "decision|chunk|assessment|gap", "relevance": "Why this source is important"}}
    ],
    "related_pending_questions": [
        {{"id": "q_001", "question": "The pending question text"}}
    ],
    "suggested_followups": [
        "Follow-up question 1",
        "Follow-up question 2"
    ]
}}
```

Be concise but comprehensive. Focus on what the user needs to know.
"""

    # Call Claude
    response = call_claude_api(prompt, model="claude-sonnet-4-20250514")
    
    # Parse response
    try:
        result = parse_json_from_response(response)
    except:
        # Fallback if JSON parsing fails
        result = {
            "answer": response,
            "confidence": "medium",
            "key_sources": [],
            "related_pending_questions": [],
            "suggested_followups": []
        }
    
    # Match cited sources to full source data
    sources_cited = []
    for source in result.get("key_sources", []):
        source_id = source.get("id")
        full_source = find_source_in_retrieval(source_id, retrieval)
        if full_source:
            sources_cited.append({
                **source,
                "full_data": full_source
            })
    
    # Match related questions
    related_questions = []
    for q in result.get("related_pending_questions", []):
        q_id = q.get("id")
        full_q = next((pq for pq in retrieval.pending_questions if pq.get("id") == q_id), None)
        if full_q:
            related_questions.append(full_q)
        else:
            related_questions.append(q)
    
    return SynthesizedAnswer(
        answer=result.get("answer", "Unable to generate answer"),
        confidence=result.get("confidence", "medium"),
        sources_cited=sources_cited,
        related_questions=related_questions,
        suggested_followups=result.get("suggested_followups", []),
        retrieval_stats={
            "total_sources": retrieval.total_sources,
            "retrieval_time_ms": retrieval.retrieval_time_ms,
            "decisions": len(retrieval.decisions),
            "gaps": len(retrieval.gaps),
            "chunks": len(retrieval.chunks),
            "pending_questions": len(retrieval.pending_questions)
        }
    )


def find_source_in_retrieval(source_id: str, retrieval: RetrievalResult) -> dict | None:
    """Find a source by ID in the retrieval results."""
    
    for dec in retrieval.decisions:
        if dec.get("id") == source_id:
            return {**dec, "type": "decision"}
    
    for gap in retrieval.gaps:
        if gap.get("id") == source_id:
            return {**gap, "type": "gap"}
    
    for assess in retrieval.assessments:
        if assess.get("id") == source_id:
            return {**assess, "type": "assessment"}
    
    for chunk in retrieval.chunks:
        if chunk.get("id") == source_id:
            return {**chunk, "type": "chunk"}
    
    for q in retrieval.pending_questions:
        if q.get("id") == source_id:
            return {**q, "type": "question"}
    
    return None
```

### Step 5: Main Query Function

```python
def ask_roadmap(query: str) -> SynthesizedAnswer:
    """
    Main entry point for asking questions about the roadmap.
    
    Args:
        query: Natural language question
    
    Returns:
        SynthesizedAnswer with answer, sources, and follow-ups
    """
    
    # Step 1: Parse the query
    parsed = parse_query(query)
    
    # Step 2: Retrieve from all sources
    retrieval = retrieve_full_context(parsed)
    
    # Step 3: Assemble context
    context = assemble_context_for_synthesis(parsed, retrieval)
    
    # Step 4: Synthesize answer
    answer = synthesize_answer(parsed, retrieval, context)
    
    return answer
```

---

## UI Integration

### New Page: Ask Your Roadmap

```python
def render_ask_roadmap_page():
    """Render the Ask Your Roadmap conversational interface."""
    
    st.title("💬 Ask Your Roadmap")
    
    st.markdown("""
    Ask natural language questions about your roadmap, gaps, decisions, and more.
    
    **Example questions:**
    - "What's my biggest gap for CPQ?"
    - "What questions need answers before Catalog GA?"
    - "Give me a status update on Acquisition"
    - "What did we decide about pricing timeline?"
    """)
    
    st.divider()
    
    # Topic filter (optional)
    col1, col2 = st.columns([3, 1])
    
    with col1:
        query = st.text_input(
            "Ask a question",
            placeholder="What's my biggest gap for CPQ?",
            key="roadmap_query"
        )
    
    with col2:
        topic_filter = st.selectbox(
            "Focus on",
            ["All Topics", "CPQ", "Catalog", "Experiences", "Acquisition", "Platform"],
            key="topic_filter"
        )
    
    # Submit button
    if st.button("Ask", type="primary", disabled=not query):
        # Append topic filter to query if specified
        full_query = query
        if topic_filter != "All Topics":
            full_query = f"{query} (focus on {topic_filter})"
        
        with st.spinner("Searching and synthesizing answer..."):
            answer = ask_roadmap(full_query)
        
        # Store in session for display
        st.session_state.last_answer = answer
        st.session_state.last_query = query
    
    # Display answer if available
    if "last_answer" in st.session_state:
        render_answer_display(st.session_state.last_answer, st.session_state.last_query)


def render_answer_display(answer: SynthesizedAnswer, query: str):
    """Render the synthesized answer with sources."""
    
    st.divider()
    
    # Query echo
    st.markdown(f"**You asked:** {query}")
    
    # Confidence badge
    confidence_colors = {
        "high": "🟢",
        "medium": "🟡",
        "low": "🟠"
    }
    st.caption(f"Confidence: {confidence_colors.get(answer.confidence, '⚪')} {answer.confidence}")
    
    st.divider()
    
    # Main answer
    st.markdown("### Answer")
    st.markdown(answer.answer)
    
    # Retrieval stats
    stats = answer.retrieval_stats
    st.caption(
        f"Retrieved from {stats['total_sources']} sources in {stats['retrieval_time_ms']}ms | "
        f"Decisions: {stats['decisions']} | Gaps: {stats['gaps']} | Chunks: {stats['chunks']}"
    )
    
    st.divider()
    
    # Sources cited
    if answer.sources_cited:
        with st.expander(f"📚 Sources Cited ({len(answer.sources_cited)})", expanded=False):
            for source in answer.sources_cited:
                source_type = source.get("type", "unknown")
                source_id = source.get("id", "unknown")
                relevance = source.get("relevance", "")
                
                type_icons = {
                    "decision": "✅",
                    "chunk": "📄",
                    "assessment": "🔬",
                    "gap": "⚠️",
                    "question": "❓"
                }
                icon = type_icons.get(source_type, "📎")
                
                with st.container(border=True):
                    st.markdown(f"{icon} **{source_id}** ({source_type})")
                    st.caption(relevance)
                    
                    # Show content preview
                    full_data = source.get("full_data", {})
                    if source_type == "decision":
                        st.write(full_data.get("decision", ""))
                    elif source_type == "chunk":
                        st.text(full_data.get("content", full_data.get("text", ""))[:200])
                    elif source_type == "gap":
                        st.write(full_data.get("description", ""))
                    elif source_type == "assessment":
                        st.write(full_data.get("summary", "")[:200])
    
    # Related pending questions
    if answer.related_questions:
        with st.expander(f"❓ Related Pending Questions ({len(answer.related_questions)})", expanded=False):
            for q in answer.related_questions:
                priority = q.get("priority", "medium")
                priority_icons = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}
                icon = priority_icons.get(priority, "⚪")
                
                st.markdown(f"{icon} {q.get('question', 'Unknown question')}")
                
                if st.button("Answer This", key=f"answer_{q.get('id', 'unknown')}"):
                    st.session_state.answering_question_id = q.get("id")
                    st.session_state.current_page = "❓ Open Questions"
                    st.rerun()
    
    # Suggested follow-ups
    if answer.suggested_followups:
        st.markdown("### 💡 You might also want to ask:")
        
        for followup in answer.suggested_followups:
            col1, col2 = st.columns([5, 1])
            col1.markdown(f"- {followup}")
            if col2.button("Ask", key=f"followup_{followup[:20]}"):
                st.session_state.roadmap_query = followup
                st.rerun()


def render_conversation_history():
    """Render conversation history for context."""
    
    if "conversation_history" not in st.session_state:
        st.session_state.conversation_history = []
    
    if st.session_state.conversation_history:
        with st.expander("📜 Previous Questions", expanded=False):
            for i, item in enumerate(reversed(st.session_state.conversation_history[-5:])):
                st.markdown(f"**Q:** {item['query']}")
                st.caption(f"A: {item['answer'][:100]}...")
                st.divider()
```

### Add to Navigation

```python
# In sidebar navigation, add:
st.sidebar.page_link("💬 Ask Your Roadmap")

# Or in radio navigation:
pages = [
    "📊 Dashboard",
    "💬 Ask Your Roadmap",  # NEW
    "📁 Sources",
    "🗺️ Roadmap",
    "❓ Open Questions",
    # ...
]
```

---

## Example Interactions

### Example 1: Gap Query

**User:** "What's my biggest gap for CPQ?"

**Answer:**
```
Based on the available context, the biggest gap for CPQ is **real-time competitive 
price monitoring** [Source: gap_007].

This gap was identified in the competitive assessment [Source: analysis_001] when 
Competitor X launched AI-powered dynamic pricing. The architecture assessment 
[Source: align_001] confirms there is currently no infrastructure to support 
real-time price feeds.

**Severity:** Significant

**Impact:** Without this capability, the Dynamic Pricing Engine roadmap item 
[Source: ri_dynamic_pricing] cannot achieve full competitive parity.

**Related Decision:** The pricing timeline has been set to Q3 [Source: dec_003], 
which provides some runway but may need acceleration given competitive pressure.

📚 Sources: gap_007, analysis_001, align_001, ri_dynamic_pricing, dec_003
```

### Example 2: Status Query

**User:** "Give me a status update on Catalog"

**Answer:**
```
**Catalog Status Update:**

**Timeline:** Catalog GA is targeted for Q3 (moved from Q2 per decision dec_008) 
[Source: dec_008]

**Current State:**
- Architecture assessment shows partial support, with API migration as the key 
  dependency [Source: align_001]
- 8 source documents discuss Catalog, primarily from team-structured lens

**Gaps:**
- No real-time sync capability identified [Source: gap_012]
- Schema migration tooling needed [Source: gap_015]

**Pending Questions:**
- 🟠 "Can we parallelize API migration with Catalog development?" [q_eng_012]
- 🟡 "What's the customer communication plan for timeline change?" [q_prod_003]

**Dependencies:** Acquisition Integration is waiting on Catalog GA.
```

### Example 3: Decision Query

**User:** "What did we decide about pricing?"

**Answer:**
```
**Pricing Decisions:**

1. **Pricing Engine targets Q3, not Q2** [Source: dec_003]
   - Rationale: Depends on Catalog API migration completing first
   - Owner: Sarah Chen
   - Implications: Set customer expectations, Experience Builder uses mocks

2. **Platform investment takes priority in Q1** [Source: dec_007]
   - This indirectly affects pricing by focusing resources on infrastructure

No decisions have been made yet regarding:
- Real-time competitive pricing approach
- AI/ML pricing models

**Related pending questions:**
- 🔴 "Should we accelerate Dynamic Pricing given competitive pressure?" [q_lead_003]
```

---

## Testing Checklist

- [ ] Query parsing extracts topics correctly
- [ ] Query parsing detects intent correctly
- [ ] LanceDB semantic search returns relevant chunks
- [ ] Chunk context graph expansion works
- [ ] Unified graph traversal finds related nodes
- [ ] Topic filtering works across all node types
- [ ] Context assembly respects authority hierarchy
- [ ] Claude synthesis produces structured response
- [ ] Sources are correctly cited and linkable
- [ ] Related pending questions are shown
- [ ] Follow-up suggestions work
- [ ] UI displays answer with formatting
- [ ] Conversation history is preserved

---

## Estimated Time

- Query parsing: 30 min
- Multi-source retrieval: 45 min
- Chunk graph expansion: 20 min
- Context assembly: 20 min
- Claude synthesis: 30 min
- UI implementation: 45 min
- Testing: 30 min

**Total: ~4 hours**
