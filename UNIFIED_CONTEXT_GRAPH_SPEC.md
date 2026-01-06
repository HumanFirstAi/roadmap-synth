# Unified Context Graph Integration Specification

## Overview

This specification defines how to integrate all decision intelligence back into the context graph, creating a unified knowledge system that connects:

- Source documents (chunks)
- Architecture assessments
- Competitive assessments
- Document impact assessments
- Open questions
- Decision log
- Roadmap items
- Identified gaps

The goal is to enable intelligent retrieval that respects the authority hierarchy and surfaces relevant decisions, assessments, and resolved questions when synthesizing or querying.

---

## The Problem

Currently, knowledge is fragmented:

```
┌─────────────────────────────────────────────────────────────┐
│  FRAGMENTED KNOWLEDGE                                       │
│                                                             │
│  Context Graph          Decision Log         Assessments    │
│  (chunks only)          (separate JSON)      (separate JSON)│
│       │                      │                    │         │
│       │                      │                    │         │
│       ▼                      ▼                    ▼         │
│  ┌─────────┐           ┌─────────┐          ┌─────────┐    │
│  │ Vector  │           │ JSON    │          │ JSON    │    │
│  │ Search  │           │ Lookup  │          │ Lookup  │    │
│  └─────────┘           └─────────┘          └─────────┘    │
│       │                      │                    │         │
│       └──────────────────────┼────────────────────┘         │
│                              │                              │
│                              ▼                              │
│                    Manual Integration                       │
│                    (in prompts only)                        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Problems:**
1. Decisions don't override conflicting source content
2. Assessments aren't connected to relevant chunks
3. Answered questions don't update the knowledge state
4. No way to traverse from a chunk to related decisions
5. Gaps identified in assessments aren't linked to roadmap items
6. Retrieval doesn't respect authority hierarchy

---

## The Solution: Unified Context Graph

```
┌─────────────────────────────────────────────────────────────┐
│  UNIFIED CONTEXT GRAPH                                      │
│                                                             │
│                    ┌─────────────────┐                     │
│                    │   DECISIONS     │ ◄── Highest Authority│
│                    │   (resolved)    │                     │
│                    └────────┬────────┘                     │
│                             │                              │
│              ┌──────────────┼──────────────┐               │
│              │ RESOLVES     │ SUPERSEDES   │ IMPACTS       │
│              ▼              ▼              ▼               │
│    ┌─────────────┐  ┌─────────────┐  ┌─────────────┐      │
│    │  ANSWERED   │  │  PREVIOUS   │  │  ROADMAP    │      │
│    │  QUESTIONS  │  │  DECISIONS  │  │  ITEMS      │      │
│    └──────┬──────┘  └─────────────┘  └──────┬──────┘      │
│           │                                  │             │
│           │ RAISED_BY                        │ HAS_GAP     │
│           ▼                                  ▼             │
│    ┌─────────────────────────────────────────────┐        │
│    │              ASSESSMENTS                     │        │
│    │  ┌─────────┐ ┌─────────┐ ┌─────────┐       │        │
│    │  │  Arch   │ │ Compet. │ │  Doc    │       │        │
│    │  │ Align   │ │ Analyst │ │ Impact  │       │        │
│    │  └────┬────┘ └────┬────┘ └────┬────┘       │        │
│    └───────┼───────────┼───────────┼─────────────┘        │
│            │ ANALYZES  │ ANALYZES  │ ASSESSES             │
│            ▼           ▼           ▼                      │
│    ┌─────────────────────────────────────────────┐        │
│    │              SOURCE CHUNKS                   │        │
│    │  ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐  │        │
│    │  │your │ │team │ │team │ │eng  │ │ext  │  │        │
│    │  │voice│ │struc│ │conv │ │     │ │anlst│  │        │
│    │  └─────┘ └─────┘ └─────┘ └─────┘ └─────┘  │        │
│    └─────────────────────────────────────────────┘        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Node Types

### 1. Source Chunks (Existing)

```python
@dataclass
class ChunkNode:
    id: str                      # chunk_001
    node_type: str = "chunk"
    
    # Existing fields
    content: str
    lens: str
    source_path: str
    source_name: str
    embedding: list[float]
    
    # New fields for graph integration
    superseded_by: str | None = None      # Decision ID if superseded
    superseded_note: str | None = None    # Why it was superseded
    related_roadmap_items: list[str] = [] # Linked roadmap items
    related_decisions: list[str] = []     # Decisions that reference this
    related_assessments: list[str] = []   # Assessments that analyzed this
```

### 2. Decision Nodes (New)

```python
@dataclass
class DecisionNode:
    id: str                      # dec_001
    node_type: str = "decision"
    
    # From Decision Log
    question_id: str             # Question this resolves
    decision: str                # The decision made
    rationale: str               # Why this decision
    implications: list[str]      # What this affects
    owner: str                   # Who owns execution
    status: str                  # active, superseded, revisiting
    created_at: str
    
    # Graph connections
    resolves_question: str       # Question ID
    supersedes_decision: str | None  # Previous decision if any
    impacts_roadmap_items: list[str] # Roadmap items affected
    related_chunks: list[str]    # Source chunks this relates to
    
    # For retrieval
    embedding: list[float]       # Embedded decision text
    key_terms: list[str]         # Extracted key terms
```

### 3. Question Nodes (New)

```python
@dataclass
class QuestionNode:
    id: str                      # q_eng_001
    node_type: str = "question"
    
    # From Open Questions
    question: str
    audience: str                # engineering, leadership, product
    category: str                # feasibility, investment, direction, etc.
    priority: str
    context: str
    status: str                  # pending, answered, deferred, obsolete
    created_at: str
    
    # Graph connections
    raised_by_assessment: str | None  # Assessment that raised this
    answered_by_decision: str | None  # Decision that resolved this
    related_chunks: list[str]         # Source chunks this relates to
    related_roadmap_items: list[str]  # Roadmap items this affects
    
    # For retrieval
    embedding: list[float]
    key_terms: list[str]
```

### 4. Assessment Nodes (New)

```python
@dataclass
class AssessmentNode:
    id: str                      # assess_001, analysis_001, align_001
    node_type: str = "assessment"
    assessment_type: str         # architecture, competitive, document_impact
    
    # Common fields
    created_at: str
    summary: str
    confidence: str
    
    # Graph connections
    analyzes_roadmap_items: list[str]  # Roadmap items analyzed
    analyzes_chunks: list[str]         # Source chunks analyzed
    identifies_gaps: list[str]         # Gap IDs identified
    raises_questions: list[str]        # Question IDs raised
    
    # Type-specific data (stored as JSON)
    assessment_data: dict        # Full assessment details
    
    # For retrieval
    embedding: list[float]
    key_terms: list[str]
```

### 5. Roadmap Item Nodes (New)

```python
@dataclass
class RoadmapItemNode:
    id: str                      # ri_001
    node_type: str = "roadmap_item"
    
    # From synthesized roadmap
    name: str
    description: str
    horizon: str                 # now, next, later, future
    theme: str
    owner: str
    
    # Graph connections
    supported_by_chunks: list[str]     # Source chunks that support this
    impacted_by_decisions: list[str]   # Decisions affecting this
    analyzed_by_assessments: list[str] # Assessments that analyzed this
    has_gaps: list[str]                # Gap IDs for this item
    has_questions: list[str]           # Open questions about this
    
    # For retrieval
    embedding: list[float]
    key_terms: list[str]
```

### 6. Gap Nodes (New)

```python
@dataclass
class GapNode:
    id: str                      # gap_001
    node_type: str = "gap"
    
    # Gap details
    description: str
    severity: str                # critical, significant, moderate, minor
    gap_type: str                # architecture, competitive, coverage
    
    # Source
    identified_by_assessment: str  # Assessment that found this
    
    # Graph connections
    relates_to_roadmap_item: str | None  # Roadmap item this is a gap for
    relates_to_chunks: list[str]         # Related source chunks
    addressed_by_decision: str | None    # Decision that addressed this
    
    # For retrieval
    embedding: list[float]
    key_terms: list[str]
```

---

## Edge Types

```python
EDGE_TYPES = {
    # === DECISION EDGES (Highest Authority) ===
    "RESOLVES": {
        "from_type": "decision",
        "to_type": "question",
        "weight": 1.0,
        "description": "Decision resolves a question"
    },
    "SUPERSEDES": {
        "from_type": "decision",
        "to_type": "decision",
        "weight": 1.0,
        "description": "New decision supersedes old decision"
    },
    "IMPACTS": {
        "from_type": "decision",
        "to_type": "roadmap_item",
        "weight": 1.0,
        "description": "Decision impacts a roadmap item"
    },
    "OVERRIDES": {
        "from_type": "decision",
        "to_type": "chunk",
        "weight": 1.0,
        "description": "Decision overrides conflicting chunk content"
    },
    
    # === QUESTION EDGES ===
    "RAISED_BY": {
        "from_type": "question",
        "to_type": "assessment",
        "weight": 0.9,
        "description": "Question was raised by an assessment"
    },
    "ANSWERED_BY": {
        "from_type": "question",
        "to_type": "decision",
        "weight": 1.0,
        "description": "Question was answered by a decision"
    },
    "ABOUT_ITEM": {
        "from_type": "question",
        "to_type": "roadmap_item",
        "weight": 0.8,
        "description": "Question is about a roadmap item"
    },
    "RELATES_TO_CHUNK": {
        "from_type": "question",
        "to_type": "chunk",
        "weight": 0.7,
        "description": "Question relates to source chunk"
    },
    
    # === ASSESSMENT EDGES ===
    "ANALYZES_ITEM": {
        "from_type": "assessment",
        "to_type": "roadmap_item",
        "weight": 0.9,
        "description": "Assessment analyzes a roadmap item"
    },
    "ANALYZES_CHUNK": {
        "from_type": "assessment",
        "to_type": "chunk",
        "weight": 0.8,
        "description": "Assessment analyzes source chunks"
    },
    "IDENTIFIES_GAP": {
        "from_type": "assessment",
        "to_type": "gap",
        "weight": 0.9,
        "description": "Assessment identifies a gap"
    },
    "RAISES_QUESTION": {
        "from_type": "assessment",
        "to_type": "question",
        "weight": 0.8,
        "description": "Assessment raises a question"
    },
    
    # === ROADMAP ITEM EDGES ===
    "SUPPORTED_BY": {
        "from_type": "roadmap_item",
        "to_type": "chunk",
        "weight": 0.8,
        "description": "Roadmap item is supported by source chunk"
    },
    "HAS_GAP": {
        "from_type": "roadmap_item",
        "to_type": "gap",
        "weight": 0.8,
        "description": "Roadmap item has an identified gap"
    },
    "DEPENDS_ON": {
        "from_type": "roadmap_item",
        "to_type": "roadmap_item",
        "weight": 0.9,
        "description": "Roadmap item depends on another item"
    },
    
    # === GAP EDGES ===
    "GAP_FOR": {
        "from_type": "gap",
        "to_type": "roadmap_item",
        "weight": 0.9,
        "description": "Gap is for a roadmap item"
    },
    "ADDRESSED_BY": {
        "from_type": "gap",
        "to_type": "decision",
        "weight": 1.0,
        "description": "Gap is addressed by a decision"
    },
    
    # === EXISTING CHUNK EDGES (preserved) ===
    "SIMILAR_TO": {
        "from_type": "chunk",
        "to_type": "chunk",
        "weight": "dynamic",  # Based on similarity score
        "description": "Chunks are semantically similar"
    },
    "SAME_SOURCE": {
        "from_type": "chunk",
        "to_type": "chunk",
        "weight": 1.0,
        "description": "Chunks from same document"
    },
    "SAME_LENS": {
        "from_type": "chunk",
        "to_type": "chunk",
        "weight": 0.5,
        "description": "Chunks from same lens"
    },
    "TOPIC_OVERLAP": {
        "from_type": "chunk",
        "to_type": "chunk",
        "weight": "dynamic",  # Based on shared terms
        "description": "Chunks share key topics"
    },
    "SEQUENTIAL": {
        "from_type": "chunk",
        "to_type": "chunk",
        "weight": 1.0,
        "description": "Chunks are sequential in document"
    },
}
```

---

## Authority Hierarchy

When retrieving and synthesizing, nodes have different authority levels:

```python
AUTHORITY_HIERARCHY = {
    # Level 1: Resolved decisions (highest)
    "decision": {
        "level": 1,
        "behavior": "Overrides conflicting content at lower levels",
        "note": "Active decisions are source of truth"
    },
    
    # Level 2: Answered questions
    "answered_question": {
        "level": 2,
        "behavior": "Resolved questions inform context",
        "note": "Questions answered by decisions"
    },
    
    # Level 3: Assessments (analyzed intelligence)
    "assessment": {
        "level": 3,
        "behavior": "Provides analyzed context, identifies gaps",
        "note": "Architecture, competitive, impact assessments"
    },
    
    # Level 4: Roadmap items (synthesized state)
    "roadmap_item": {
        "level": 4,
        "behavior": "Current roadmap as reference",
        "note": "Output of synthesis, input to assessments"
    },
    
    # Level 5: Gaps (identified issues)
    "gap": {
        "level": 5,
        "behavior": "Identified but not yet resolved",
        "note": "From assessments, awaiting decisions"
    },
    
    # Level 6: Source chunks (base content)
    "chunk": {
        "level": 6,
        "behavior": "Raw source content, may be superseded",
        "note": "Can be overridden by decisions"
    },
    
    # Level 7: Pending questions (unresolved)
    "pending_question": {
        "level": 7,
        "behavior": "Open items requiring resolution",
        "note": "Not yet answered"
    },
}
```

---

## Graph Storage

### Extended NetworkX Graph

```python
import networkx as nx
from typing import Any

class UnifiedContextGraph:
    """
    Unified graph containing all knowledge types.
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
    
    def add_node(self, node: Any) -> None:
        """Add a node of any type to the graph."""
        
        node_type = node.node_type
        node_id = node.id
        
        # Add to graph
        self.graph.add_node(
            node_id,
            node_type=node_type,
            data=node.__dict__,
            embedding=node.embedding if hasattr(node, 'embedding') else None
        )
        
        # Add to type index
        self.node_indices[node_type][node_id] = node
    
    def add_edge(
        self,
        from_id: str,
        to_id: str,
        edge_type: str,
        weight: float = 1.0,
        metadata: dict = None
    ) -> None:
        """Add an edge between nodes."""
        
        self.graph.add_edge(
            from_id,
            to_id,
            edge_type=edge_type,
            weight=weight,
            metadata=metadata or {}
        )
    
    def get_nodes_by_type(self, node_type: str) -> list:
        """Get all nodes of a specific type."""
        return list(self.node_indices.get(node_type, {}).values())
    
    def get_related_decisions(self, node_id: str) -> list[DecisionNode]:
        """Get decisions related to a node."""
        
        decisions = []
        
        # Find all paths to decision nodes
        for decision_id in self.node_indices["decision"]:
            if nx.has_path(self.graph, node_id, decision_id):
                decisions.append(self.node_indices["decision"][decision_id])
            elif nx.has_path(self.graph, decision_id, node_id):
                decisions.append(self.node_indices["decision"][decision_id])
        
        return decisions
    
    def get_superseding_decision(self, chunk_id: str) -> DecisionNode | None:
        """Get decision that supersedes a chunk, if any."""
        
        for neighbor in self.graph.predecessors(chunk_id):
            edge = self.graph.edges[neighbor, chunk_id]
            if edge.get("edge_type") == "OVERRIDES":
                return self.node_indices["decision"].get(neighbor)
        
        return None
    
    def get_gaps_for_roadmap_item(self, item_id: str) -> list[GapNode]:
        """Get gaps identified for a roadmap item."""
        
        gaps = []
        for neighbor in self.graph.successors(item_id):
            edge = self.graph.edges[item_id, neighbor]
            if edge.get("edge_type") == "HAS_GAP":
                gaps.append(self.node_indices["gap"].get(neighbor))
        
        return [g for g in gaps if g is not None]
    
    def get_open_questions_for_item(self, item_id: str) -> list[QuestionNode]:
        """Get pending questions about a roadmap item."""
        
        questions = []
        for neighbor in self.graph.predecessors(item_id):
            node = self.graph.nodes[neighbor]
            if node.get("node_type") == "question":
                q = self.node_indices["question"].get(neighbor)
                if q and q.status == "pending":
                    questions.append(q)
        
        return questions
    
    def traverse_with_authority(
        self,
        start_ids: list[str],
        max_hops: int = 2
    ) -> dict:
        """
        Traverse graph from start nodes, respecting authority hierarchy.
        Returns nodes grouped by type and authority level.
        """
        
        visited = set()
        result = {level: [] for level in range(1, 8)}
        
        def get_authority_level(node_type: str) -> int:
            return AUTHORITY_HIERARCHY.get(node_type, {}).get("level", 6)
        
        queue = [(id, 0) for id in start_ids]
        
        while queue:
            node_id, hops = queue.pop(0)
            
            if node_id in visited or hops > max_hops:
                continue
            
            visited.add(node_id)
            
            if node_id not in self.graph:
                continue
            
            node = self.graph.nodes[node_id]
            node_type = node.get("node_type", "chunk")
            authority = get_authority_level(node_type)
            
            result[authority].append({
                "id": node_id,
                "type": node_type,
                "data": node.get("data", {})
            })
            
            # Add neighbors to queue
            for neighbor in self.graph.neighbors(node_id):
                queue.append((neighbor, hops + 1))
            for neighbor in self.graph.predecessors(node_id):
                queue.append((neighbor, hops + 1))
        
        return result
```

### Persistence

```python
import json
from pathlib import Path

GRAPH_PATH = Path("data/unified_graph")

def save_unified_graph(graph: UnifiedContextGraph) -> None:
    """Save graph to disk."""
    
    GRAPH_PATH.mkdir(parents=True, exist_ok=True)
    
    # Save graph structure
    graph_data = nx.node_link_data(graph.graph)
    (GRAPH_PATH / "graph.json").write_text(json.dumps(graph_data, indent=2))
    
    # Save node indices by type
    for node_type, nodes in graph.node_indices.items():
        node_data = {k: v.__dict__ for k, v in nodes.items()}
        (GRAPH_PATH / f"{node_type}_nodes.json").write_text(
            json.dumps(node_data, indent=2)
        )


def load_unified_graph() -> UnifiedContextGraph:
    """Load graph from disk."""
    
    graph = UnifiedContextGraph()
    
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
            node_data = json.loads(node_file.read_text())
            # Reconstruct node objects
            for node_id, data in node_data.items():
                graph.node_indices[node_type][node_id] = reconstruct_node(node_type, data)
    
    return graph
```

---

## Integration Functions

### 1. Integrate Decisions

```python
def integrate_decision(graph: UnifiedContextGraph, decision: dict) -> None:
    """
    Integrate a new decision into the graph.
    - Creates decision node
    - Links to resolved question
    - Links to impacted roadmap items
    - Creates OVERRIDES edges to conflicting chunks
    """
    
    # Create decision node
    decision_node = DecisionNode(
        id=decision["id"],
        question_id=decision["question_id"],
        decision=decision["decision"],
        rationale=decision.get("rationale", ""),
        implications=decision.get("implications", []),
        owner=decision.get("owner", ""),
        status=decision.get("status", "active"),
        created_at=decision["created_at"],
        resolves_question=decision["question_id"],
        supersedes_decision=None,
        impacts_roadmap_items=[],
        related_chunks=[],
        embedding=embed_text(decision["decision"]),
        key_terms=extract_key_terms(decision["decision"])
    )
    
    graph.add_node(decision_node)
    
    # Link to resolved question
    graph.add_edge(
        decision["id"],
        decision["question_id"],
        edge_type="RESOLVES",
        weight=1.0
    )
    
    # Update question status
    if decision["question_id"] in graph.node_indices["question"]:
        question = graph.node_indices["question"][decision["question_id"]]
        question.status = "answered"
        question.answered_by_decision = decision["id"]
    
    # Find and link impacted roadmap items
    roadmap_items = find_related_roadmap_items(graph, decision["decision"])
    for item_id in roadmap_items:
        graph.add_edge(
            decision["id"],
            item_id,
            edge_type="IMPACTS",
            weight=1.0
        )
        decision_node.impacts_roadmap_items.append(item_id)
    
    # Find conflicting chunks and create OVERRIDES edges
    conflicting_chunks = find_conflicting_chunks(graph, decision)
    for chunk_id in conflicting_chunks:
        graph.add_edge(
            decision["id"],
            chunk_id,
            edge_type="OVERRIDES",
            weight=1.0,
            metadata={"reason": "Decision supersedes this content"}
        )
        decision_node.related_chunks.append(chunk_id)
        
        # Update chunk
        if chunk_id in graph.node_indices["chunk"]:
            chunk = graph.node_indices["chunk"][chunk_id]
            chunk.superseded_by = decision["id"]
            chunk.superseded_note = f"Superseded by decision: {decision['decision'][:100]}"


def find_conflicting_chunks(graph: UnifiedContextGraph, decision: dict) -> list[str]:
    """
    Find chunks that conflict with a decision.
    Uses semantic similarity + keyword matching.
    """
    
    conflicting = []
    decision_embedding = embed_text(decision["decision"])
    decision_terms = set(extract_key_terms(decision["decision"]))
    
    # Get the original question
    question_id = decision["question_id"]
    question = graph.node_indices["question"].get(question_id)
    
    if not question:
        return conflicting
    
    # Find chunks related to the question's topic
    question_terms = set(extract_key_terms(question.question))
    all_terms = decision_terms | question_terms
    
    for chunk_id, chunk in graph.node_indices["chunk"].items():
        chunk_terms = set(chunk.key_terms if hasattr(chunk, 'key_terms') else [])
        
        # Check for topic overlap
        if len(all_terms & chunk_terms) >= 2:
            # Check semantic similarity
            if hasattr(chunk, 'embedding') and chunk.embedding:
                similarity = cosine_similarity(decision_embedding, chunk.embedding)
                if similarity > 0.7:
                    conflicting.append(chunk_id)
    
    return conflicting
```

### 2. Integrate Assessments

```python
def integrate_assessment(
    graph: UnifiedContextGraph,
    assessment: dict,
    assessment_type: str  # architecture, competitive, document_impact
) -> None:
    """
    Integrate an assessment into the graph.
    - Creates assessment node
    - Links to analyzed roadmap items
    - Creates gap nodes
    - Links to raised questions
    """
    
    # Create assessment node
    assessment_node = AssessmentNode(
        id=assessment["id"],
        assessment_type=assessment_type,
        created_at=assessment.get("assessed_at", datetime.now().isoformat()),
        summary=get_assessment_summary(assessment, assessment_type),
        confidence=assessment.get("confidence", "medium"),
        analyzes_roadmap_items=[],
        analyzes_chunks=[],
        identifies_gaps=[],
        raises_questions=[],
        assessment_data=assessment,
        embedding=embed_text(get_assessment_summary(assessment, assessment_type)),
        key_terms=extract_assessment_terms(assessment, assessment_type)
    )
    
    graph.add_node(assessment_node)
    
    # Link to analyzed roadmap items
    roadmap_items = extract_roadmap_items_from_assessment(assessment, assessment_type)
    for item_name in roadmap_items:
        item_id = find_roadmap_item_id(graph, item_name)
        if item_id:
            graph.add_edge(
                assessment["id"],
                item_id,
                edge_type="ANALYZES_ITEM",
                weight=0.9
            )
            assessment_node.analyzes_roadmap_items.append(item_id)
    
    # Create and link gap nodes
    gaps = extract_gaps_from_assessment(assessment, assessment_type)
    for gap_data in gaps:
        gap_node = GapNode(
            id=f"gap_{assessment['id']}_{len(assessment_node.identifies_gaps)}",
            description=gap_data["description"],
            severity=gap_data.get("severity", "medium"),
            gap_type=assessment_type,
            identified_by_assessment=assessment["id"],
            relates_to_roadmap_item=gap_data.get("roadmap_item"),
            relates_to_chunks=[],
            addressed_by_decision=None,
            embedding=embed_text(gap_data["description"]),
            key_terms=extract_key_terms(gap_data["description"])
        )
        
        graph.add_node(gap_node)
        graph.add_edge(
            assessment["id"],
            gap_node.id,
            edge_type="IDENTIFIES_GAP",
            weight=0.9
        )
        assessment_node.identifies_gaps.append(gap_node.id)
        
        # Link gap to roadmap item if specified
        if gap_data.get("roadmap_item"):
            item_id = find_roadmap_item_id(graph, gap_data["roadmap_item"])
            if item_id:
                graph.add_edge(
                    item_id,
                    gap_node.id,
                    edge_type="HAS_GAP",
                    weight=0.8
                )
    
    # Link to raised questions
    questions = extract_questions_from_assessment(assessment, assessment_type)
    for q_id in questions:
        if q_id in graph.node_indices["question"]:
            graph.add_edge(
                assessment["id"],
                q_id,
                edge_type="RAISES_QUESTION",
                weight=0.8
            )
            assessment_node.raises_questions.append(q_id)
            
            # Update question with raised_by
            question = graph.node_indices["question"][q_id]
            question.raised_by_assessment = assessment["id"]


def extract_gaps_from_assessment(assessment: dict, assessment_type: str) -> list[dict]:
    """Extract gaps from different assessment types."""
    
    gaps = []
    
    if assessment_type == "architecture":
        # From architecture alignment
        for gap in assessment.get("gaps_exposed", []):
            gaps.append({
                "description": gap.get("gap", gap.get("description", "")),
                "severity": gap.get("severity", "medium"),
                "roadmap_item": gap.get("roadmap_item")
            })
    
    elif assessment_type == "competitive":
        # From competitive analysis
        for gap in assessment.get("roadmap_gaps", []):
            gaps.append({
                "description": gap.get("gap_description", ""),
                "severity": gap.get("severity", "medium"),
                "roadmap_item": None  # May need to infer
            })
    
    elif assessment_type == "document_impact":
        # From document impact assessment
        for concept in assessment.get("novel_concepts", []):
            if concept.get("relevance") == "high":
                gaps.append({
                    "description": f"Novel concept not in roadmap: {concept.get('concept', '')}",
                    "severity": "moderate",
                    "roadmap_item": None
                })
    
    return gaps
```

### 3. Integrate Roadmap Items

```python
def integrate_roadmap(graph: UnifiedContextGraph, roadmap: dict) -> None:
    """
    Integrate synthesized roadmap into graph.
    - Creates roadmap item nodes
    - Links to supporting chunks
    - Links to existing assessments and gaps
    """
    
    for item in roadmap.get("items", []):
        # Create roadmap item node
        item_node = RoadmapItemNode(
            id=f"ri_{sanitize_id(item['name'])}",
            name=item["name"],
            description=item.get("description", ""),
            horizon=item.get("horizon", "future"),
            theme=item.get("theme", ""),
            owner=item.get("owner", ""),
            supported_by_chunks=[],
            impacted_by_decisions=[],
            analyzed_by_assessments=[],
            has_gaps=[],
            has_questions=[],
            embedding=embed_text(f"{item['name']} {item.get('description', '')}"),
            key_terms=extract_key_terms(f"{item['name']} {item.get('description', '')}")
        )
        
        graph.add_node(item_node)
        
        # Find and link supporting chunks
        supporting_chunks = find_supporting_chunks(graph, item)
        for chunk_id in supporting_chunks:
            graph.add_edge(
                item_node.id,
                chunk_id,
                edge_type="SUPPORTED_BY",
                weight=0.8
            )
            item_node.supported_by_chunks.append(chunk_id)
        
        # Link to existing relevant decisions
        relevant_decisions = find_relevant_decisions(graph, item)
        for decision_id in relevant_decisions:
            if not graph.graph.has_edge(decision_id, item_node.id):
                graph.add_edge(
                    decision_id,
                    item_node.id,
                    edge_type="IMPACTS",
                    weight=1.0
                )
            item_node.impacted_by_decisions.append(decision_id)
        
        # Link to existing relevant questions
        relevant_questions = find_relevant_questions(graph, item)
        for q_id in relevant_questions:
            graph.add_edge(
                q_id,
                item_node.id,
                edge_type="ABOUT_ITEM",
                weight=0.8
            )
            item_node.has_questions.append(q_id)
```

### 4. Sync Function

```python
def sync_all_to_graph() -> UnifiedContextGraph:
    """
    Sync all data sources to the unified graph.
    Call this after any updates to decisions, assessments, etc.
    """
    
    graph = load_unified_graph()
    
    # 1. Sync chunks (base layer)
    chunks = load_all_chunks()
    for chunk in chunks:
        if chunk["id"] not in graph.node_indices["chunk"]:
            integrate_chunk(graph, chunk)
    
    # 2. Sync roadmap items
    roadmap = load_latest_roadmap_structured()
    if roadmap:
        integrate_roadmap(graph, roadmap)
    
    # 3. Sync questions
    questions = load_questions()
    for question in questions:
        if question["id"] not in graph.node_indices["question"]:
            integrate_question(graph, question)
    
    # 4. Sync decisions (highest authority)
    decisions = load_decisions()
    for decision in decisions:
        if decision["id"] not in graph.node_indices["decision"]:
            integrate_decision(graph, decision)
    
    # 5. Sync assessments
    for assessment_type, loader in [
        ("architecture", load_architecture_assessments),
        ("competitive", load_competitive_assessments),
        ("document_impact", load_impact_assessments),
    ]:
        assessments = loader()
        for assessment in assessments:
            if assessment["id"] not in graph.node_indices["assessment"]:
                integrate_assessment(graph, assessment, assessment_type)
    
    # 6. Rebuild cross-references
    rebuild_cross_references(graph)
    
    # 7. Save
    save_unified_graph(graph)
    
    return graph
```

---

## Retrieval with Authority

### Authority-Aware Retrieval

```python
def retrieve_with_authority(
    query: str,
    graph: UnifiedContextGraph,
    include_superseded: bool = False
) -> dict:
    """
    Retrieve relevant content respecting authority hierarchy.
    
    Returns content grouped by authority level, with decisions
    overriding conflicting chunks.
    """
    
    # 1. Embed query
    query_embedding = embed_text(query)
    query_terms = set(extract_key_terms(query))
    
    # 2. Find relevant nodes across all types
    relevant_nodes = {
        "decisions": [],
        "answered_questions": [],
        "assessments": [],
        "roadmap_items": [],
        "gaps": [],
        "chunks": [],
        "pending_questions": [],
    }
    
    # Search each node type
    for node_type, nodes in graph.node_indices.items():
        for node_id, node in nodes.items():
            if not hasattr(node, 'embedding') or not node.embedding:
                continue
            
            similarity = cosine_similarity(query_embedding, node.embedding)
            
            if similarity > 0.6:  # Threshold
                categorize_node(relevant_nodes, node, similarity)
    
    # 3. Apply authority rules
    
    # Get active decisions
    active_decisions = [
        d for d in relevant_nodes["decisions"]
        if d["data"].get("status") == "active"
    ]
    
    # Mark superseded chunks
    superseded_chunk_ids = set()
    for decision in active_decisions:
        # Find chunks this decision overrides
        decision_id = decision["id"]
        for neighbor in graph.graph.successors(decision_id):
            edge = graph.graph.edges[decision_id, neighbor]
            if edge.get("edge_type") == "OVERRIDES":
                superseded_chunk_ids.add(neighbor)
    
    # Filter or mark superseded chunks
    if not include_superseded:
        relevant_nodes["chunks"] = [
            c for c in relevant_nodes["chunks"]
            if c["id"] not in superseded_chunk_ids
        ]
    else:
        for chunk in relevant_nodes["chunks"]:
            if chunk["id"] in superseded_chunk_ids:
                chunk["superseded"] = True
                chunk["superseded_by"] = find_superseding_decision(
                    graph, chunk["id"]
                )
    
    # 4. Expand via graph traversal
    seed_ids = [n["id"] for nodes in relevant_nodes.values() for n in nodes[:5]]
    expanded = graph.traverse_with_authority(seed_ids, max_hops=1)
    
    # Merge expanded nodes
    merge_expanded_nodes(relevant_nodes, expanded, graph)
    
    # 5. Sort by relevance within each category
    for category in relevant_nodes:
        relevant_nodes[category].sort(
            key=lambda x: x.get("similarity", 0),
            reverse=True
        )
    
    return relevant_nodes


def categorize_node(relevant_nodes: dict, node: Any, similarity: float) -> None:
    """Categorize a node into the appropriate bucket."""
    
    node_data = {
        "id": node.id,
        "data": node.__dict__,
        "similarity": similarity
    }
    
    if node.node_type == "decision":
        relevant_nodes["decisions"].append(node_data)
    elif node.node_type == "question":
        if node.status == "answered":
            relevant_nodes["answered_questions"].append(node_data)
        else:
            relevant_nodes["pending_questions"].append(node_data)
    elif node.node_type == "assessment":
        relevant_nodes["assessments"].append(node_data)
    elif node.node_type == "roadmap_item":
        relevant_nodes["roadmap_items"].append(node_data)
    elif node.node_type == "gap":
        relevant_nodes["gaps"].append(node_data)
    elif node.node_type == "chunk":
        relevant_nodes["chunks"].append(node_data)
```

### Format for Synthesis

```python
def format_context_with_authority(retrieved: dict) -> str:
    """
    Format retrieved content for synthesis prompt.
    Clearly separates by authority level.
    """
    
    sections = []
    
    # Level 1: Decisions (Highest Authority)
    if retrieved["decisions"]:
        sections.append("## RESOLVED DECISIONS (Highest Authority)")
        sections.append("These decisions are final and override conflicting source content.\n")
        
        for decision in retrieved["decisions"][:10]:
            d = decision["data"]
            sections.append(f"### Decision: {d['id']}")
            sections.append(f"**Decision:** {d['decision']}")
            sections.append(f"**Rationale:** {d.get('rationale', 'N/A')}")
            if d.get("implications"):
                sections.append(f"**Implications:** {', '.join(d['implications'])}")
            sections.append("")
    
    # Level 2: Answered Questions
    if retrieved["answered_questions"]:
        sections.append("## ANSWERED QUESTIONS")
        sections.append("These questions have been resolved.\n")
        
        for q in retrieved["answered_questions"][:10]:
            qd = q["data"]
            sections.append(f"**Q:** {qd['question']}")
            sections.append(f"**Status:** Answered by {qd.get('answered_by_decision', 'decision')}")
            sections.append("")
    
    # Level 3: Assessments
    if retrieved["assessments"]:
        sections.append("## ASSESSMENTS")
        sections.append("Analyzed intelligence from architecture, competitive, and impact assessments.\n")
        
        for assessment in retrieved["assessments"][:5]:
            a = assessment["data"]
            sections.append(f"### {a['assessment_type'].title()} Assessment: {a['id']}")
            sections.append(f"**Summary:** {a.get('summary', 'N/A')}")
            sections.append(f"**Confidence:** {a.get('confidence', 'medium')}")
            sections.append("")
    
    # Level 4: Roadmap Items
    if retrieved["roadmap_items"]:
        sections.append("## RELEVANT ROADMAP ITEMS")
        sections.append("Current roadmap items related to this query.\n")
        
        for item in retrieved["roadmap_items"][:10]:
            i = item["data"]
            sections.append(f"### {i['name']} ({i['horizon']})")
            sections.append(f"{i.get('description', 'N/A')}")
            sections.append("")
    
    # Level 5: Gaps
    if retrieved["gaps"]:
        sections.append("## IDENTIFIED GAPS")
        sections.append("Gaps identified in assessments, not yet addressed.\n")
        
        for gap in retrieved["gaps"][:10]:
            g = gap["data"]
            sections.append(f"- [{g['severity']}] {g['description']}")
        sections.append("")
    
    # Level 6: Source Chunks
    if retrieved["chunks"]:
        sections.append("## SOURCE CONTENT")
        sections.append("Raw source material. Note: Some may be superseded by decisions above.\n")
        
        for chunk in retrieved["chunks"][:15]:
            c = chunk["data"]
            superseded_note = ""
            if chunk.get("superseded"):
                superseded_note = f" [SUPERSEDED by {chunk['superseded_by']}]"
            
            sections.append(f"### {c.get('source_name', 'Unknown')} ({c.get('lens', 'unknown')}){superseded_note}")
            sections.append(c.get("content", c.get("text", ""))[:500])
            sections.append("")
    
    # Level 7: Pending Questions
    if retrieved["pending_questions"]:
        sections.append("## OPEN QUESTIONS (Unresolved)")
        sections.append("These questions are still pending resolution.\n")
        
        for q in retrieved["pending_questions"][:10]:
            qd = q["data"]
            sections.append(f"- [{qd['priority']}] {qd['question']}")
        sections.append("")
    
    return "\n".join(sections)
```

---

## CLI Commands

### Sync Graph

```python
@app.command()
def graph_sync():
    """Sync all data to the unified context graph."""
    
    console.print("[bold]Syncing Unified Context Graph[/bold]\n")
    
    with console.status("Loading and syncing data..."):
        graph = sync_all_to_graph()
    
    # Report stats
    console.print("[green]Sync complete![/green]\n")
    
    console.print("[bold]Graph Statistics:[/bold]")
    console.print(f"  Total nodes: {graph.graph.number_of_nodes()}")
    console.print(f"  Total edges: {graph.graph.number_of_edges()}")
    
    for node_type, nodes in graph.node_indices.items():
        console.print(f"  {node_type}: {len(nodes)}")


@app.command()
def graph_query(
    query: str = typer.Argument(..., help="Query to search"),
    include_superseded: bool = typer.Option(False, help="Include superseded chunks")
):
    """Query the unified context graph with authority hierarchy."""
    
    graph = load_unified_graph()
    
    console.print(f"[bold]Querying:[/bold] {query}\n")
    
    results = retrieve_with_authority(query, graph, include_superseded)
    
    # Display results by authority level
    for category, items in results.items():
        if items:
            console.print(f"\n[bold]{category.upper()}[/bold] ({len(items)} results)")
            for item in items[:3]:
                console.print(f"  • {item['id']}: {str(item['data'])[:100]}...")


@app.command()
def graph_stats():
    """Show unified graph statistics."""
    
    graph = load_unified_graph()
    
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
    
    for edge_type, count in sorted(edge_counts.items()):
        console.print(f"  {edge_type}: {count}")
    
    # Authority coverage
    console.print("\n[bold]Authority Coverage:[/bold]")
    
    active_decisions = len([
        d for d in graph.node_indices["decision"].values()
        if d.status == "active"
    ])
    console.print(f"  Active decisions: {active_decisions}")
    
    answered_questions = len([
        q for q in graph.node_indices["question"].values()
        if q.status == "answered"
    ])
    pending_questions = len([
        q for q in graph.node_indices["question"].values()
        if q.status == "pending"
    ])
    console.print(f"  Answered questions: {answered_questions}")
    console.print(f"  Pending questions: {pending_questions}")
    
    superseded_chunks = len([
        c for c in graph.node_indices["chunk"].values()
        if c.superseded_by
    ])
    console.print(f"  Superseded chunks: {superseded_chunks}")
```

---

## Streamlit Integration

### Updated Dashboard

```python
# Add to dashboard page

st.subheader("Knowledge Graph Overview")

graph = load_unified_graph()

# Node counts
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Nodes", graph.graph.number_of_nodes())
col2.metric("Total Edges", graph.graph.number_of_edges())
col3.metric("Active Decisions", len([d for d in graph.node_indices["decision"].values() if d.status == "active"]))
col4.metric("Pending Questions", len([q for q in graph.node_indices["question"].values() if q.status == "pending"]))

# Authority breakdown
st.write("**Knowledge by Authority Level:**")

authority_data = {
    "Decisions (L1)": len(graph.node_indices["decision"]),
    "Answered Qs (L2)": len([q for q in graph.node_indices["question"].values() if q.status == "answered"]),
    "Assessments (L3)": len(graph.node_indices["assessment"]),
    "Roadmap Items (L4)": len(graph.node_indices["roadmap_item"]),
    "Gaps (L5)": len(graph.node_indices["gap"]),
    "Chunks (L6)": len(graph.node_indices["chunk"]),
    "Pending Qs (L7)": len([q for q in graph.node_indices["question"].values() if q.status == "pending"]),
}

st.bar_chart(authority_data)

# Sync button
if st.button("🔄 Sync Graph"):
    with st.spinner("Syncing all data to graph..."):
        graph = sync_all_to_graph()
    st.success("Graph synced!")
    st.experimental_rerun()
```

### New Page: Knowledge Graph Explorer

```python
elif page == "🕸️ Knowledge Graph":
    st.title("Unified Knowledge Graph")
    
    graph = load_unified_graph()
    
    tab1, tab2, tab3 = st.tabs(["🔍 Query", "📊 Statistics", "🗺️ Visualize"])
    
    with tab1:
        st.subheader("Query with Authority")
        
        query = st.text_input("Enter your query")
        include_superseded = st.checkbox("Include superseded content")
        
        if query and st.button("Search"):
            results = retrieve_with_authority(query, graph, include_superseded)
            
            for category, items in results.items():
                if items:
                    with st.expander(f"{category.upper()} ({len(items)} results)", expanded=category=="decisions"):
                        for item in items[:10]:
                            st.write(f"**{item['id']}** (similarity: {item['similarity']:.2f})")
                            st.write(str(item['data'])[:300])
                            st.markdown("---")
    
    with tab2:
        # Stats display
        ...
    
    with tab3:
        # Graph visualization using pyvis or similar
        ...
```

---

## Implementation Order

1. **Data models** (20 min)
   - New node types
   - Edge type definitions

2. **UnifiedContextGraph class** (30 min)
   - Core graph operations
   - Node indices
   - Traversal methods

3. **Integration functions** (45 min)
   - integrate_decision
   - integrate_assessment
   - integrate_roadmap
   - integrate_question

4. **Sync function** (20 min)
   - sync_all_to_graph
   - Persistence (save/load)

5. **Authority-aware retrieval** (30 min)
   - retrieve_with_authority
   - format_context_with_authority

6. **CLI commands** (20 min)
   - graph-sync
   - graph-query
   - graph-stats

7. **Streamlit integration** (30 min)
   - Dashboard updates
   - Knowledge Graph explorer page

8. **Testing** (30 min)
   - Test decision override
   - Test assessment integration
   - Test retrieval with authority

---

## Success Criteria

- [ ] All knowledge types integrated into single graph
- [ ] Decisions override conflicting chunks
- [ ] Assessments linked to roadmap items and gaps
- [ ] Questions linked to decisions that answer them
- [ ] Authority hierarchy respected in retrieval
- [ ] Graph syncs automatically after updates
- [ ] Retrieval returns content grouped by authority
- [ ] Superseded content clearly marked
- [ ] Streamlit shows graph overview
- [ ] CLI commands for graph management
