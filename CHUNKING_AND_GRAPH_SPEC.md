# Chunking & Context Graph Improvements

## Overview

This spec covers two related improvements to the Roadmap Synthesis tool:

1. **Improved Chunking** — Larger chunks with more overlap to preserve context
2. **Context Graph** — A chunk-level graph to capture relationships and improve retrieval

---

## Part 1: Improved Chunking

### Current Problems
- 512 token chunks are too small for strategic documents
- 50 token overlap (~10%) loses continuity between chunks
- Context is fragmented, synthesis becomes reductive

### New Parameters

| Parameter | Old Value | New Value | Rationale |
|-----------|-----------|-----------|-----------|
| `CHUNK_SIZE` | 512 | 1024 | Preserve more context per chunk |
| `CHUNK_OVERLAP` | 50 | 150 | ~15% overlap maintains continuity |

### Implementation

Find the chunking configuration and update:

```python
# Configuration
CHUNK_SIZE = 1024  # tokens (~750 words)
CHUNK_OVERLAP = 150  # tokens (~15% overlap)
```

### Migration

After updating, users must re-ingest all materials:

```bash
uv run python roadmap.py clear
uv run python roadmap.py ingest ./materials/your-voice/ --lens your-voice
uv run python roadmap.py ingest ./materials/team-structured/ --lens team-structured
# ... etc
```

Add a warning in the UI when chunk parameters change.

---

## Part 2: Context Graph

### Purpose

Build a graph that captures relationships between chunks to:
- Improve retrieval by following relationships
- Surface contradictions between sources
- Ensure balanced representation across lenses
- Provide explainability for synthesis decisions

### Dependencies

```bash
uv add networkx
```

### Data Model

#### Nodes
Each chunk becomes a node with attributes:

```python
{
    "id": "chunk_123",  # Unique chunk ID
    "lens": "team-structured",
    "source_path": "materials/team-structured/cpq/roadmap.pdf",
    "source_name": "roadmap.pdf",  # Short name for display
    "chunk_index": 3,
    "total_chunks": 12,
    "token_count": 987,
    "content_preview": "First 200 chars...",  # For UI display
    "key_terms": ["catalog", "Q2", "integration"],  # Extracted terms
    "time_references": ["Q2", "2024"],  # Temporal mentions
    "created_at": "2024-01-15T10:30:00Z"
}
```

#### Edges
Relationships between chunks:

| Edge Type | Condition | Weight |
|-----------|-----------|--------|
| `SIMILAR_TO` | Cosine similarity > 0.80 | similarity score |
| `SAME_SOURCE` | Same source_path | 1.0 |
| `SAME_LENS` | Same lens | 0.5 |
| `TOPIC_OVERLAP` | Share 2+ key terms | count of shared terms |
| `TEMPORAL_OVERLAP` | Reference same time period | 1.0 |
| `SEQUENTIAL` | Adjacent chunks in same doc | 1.0 |

Edge attributes:
```python
{
    "type": "SIMILAR_TO",
    "weight": 0.87,
    "created_at": "2024-01-15T10:30:00Z"
}
```

### Graph Construction

#### Step 1: Extract Key Terms

For each chunk, extract key terms using simple NLP:

```python
import re
from collections import Counter

def extract_key_terms(text: str, top_n: int = 10) -> list[str]:
    """Extract key terms from chunk text."""
    # Simple approach: extract capitalized phrases and repeated nouns
    
    # Find capitalized words/phrases (likely proper nouns, products, teams)
    caps = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
    
    # Find common business terms
    business_terms = re.findall(
        r'\b(roadmap|priority|Q[1-4]|integration|platform|API|'
        r'customer|revenue|churn|acquisition|catalog|experience|'
        r'engineering|architecture|dependency|milestone)\b',
        text.lower()
    )
    
    # Count and return top terms
    all_terms = [t.lower() for t in caps] + business_terms
    counts = Counter(all_terms)
    return [term for term, _ in counts.most_common(top_n)]
```

#### Step 2: Extract Time References

```python
def extract_time_references(text: str) -> list[str]:
    """Extract temporal references from text."""
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
```

#### Step 3: Build Graph

```python
import networkx as nx
from pathlib import Path
import json

class ContextGraph:
    def __init__(self, graph_path: Path = Path("data/context_graph.json")):
        self.graph_path = graph_path
        self.graph = nx.Graph()
    
    def build_from_chunks(self, chunks: list[dict], embeddings: list[list[float]]):
        """Build graph from chunks and their embeddings."""
        
        # Add nodes
        for chunk in chunks:
            self.graph.add_node(
                chunk["id"],
                lens=chunk["lens"],
                source_path=chunk["source_path"],
                source_name=Path(chunk["source_path"]).name,
                chunk_index=chunk["chunk_index"],
                token_count=chunk["token_count"],
                content_preview=chunk["text"][:200],
                key_terms=extract_key_terms(chunk["text"]),
                time_references=extract_time_references(chunk["text"]),
            )
        
        # Add edges
        self._add_same_source_edges(chunks)
        self._add_same_lens_edges(chunks)
        self._add_sequential_edges(chunks)
        self._add_topic_overlap_edges(chunks)
        self._add_similarity_edges(chunks, embeddings)
        self._add_temporal_edges(chunks)
    
    def _add_same_source_edges(self, chunks):
        """Connect chunks from same source document."""
        by_source = {}
        for chunk in chunks:
            src = chunk["source_path"]
            if src not in by_source:
                by_source[src] = []
            by_source[src].append(chunk["id"])
        
        for source, chunk_ids in by_source.items():
            for i, id1 in enumerate(chunk_ids):
                for id2 in chunk_ids[i+1:]:
                    self.graph.add_edge(id1, id2, type="SAME_SOURCE", weight=1.0)
    
    def _add_same_lens_edges(self, chunks):
        """Connect chunks with same lens (lightweight edges)."""
        by_lens = {}
        for chunk in chunks:
            lens = chunk["lens"]
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
    
    def _add_sequential_edges(self, chunks):
        """Connect adjacent chunks in same document."""
        by_source = {}
        for chunk in chunks:
            src = chunk["source_path"]
            if src not in by_source:
                by_source[src] = []
            by_source[src].append(chunk)
        
        for source, source_chunks in by_source.items():
            sorted_chunks = sorted(source_chunks, key=lambda x: x["chunk_index"])
            for i in range(len(sorted_chunks) - 1):
                id1 = sorted_chunks[i]["id"]
                id2 = sorted_chunks[i + 1]["id"]
                self.graph.add_edge(id1, id2, type="SEQUENTIAL", weight=1.0)
    
    def _add_topic_overlap_edges(self, chunks):
        """Connect chunks that share key terms."""
        # Get key terms for each chunk
        chunk_terms = {}
        for chunk in chunks:
            terms = set(extract_key_terms(chunk["text"]))
            chunk_terms[chunk["id"]] = terms
        
        # Find overlaps (only check pairs with potential overlap)
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
    
    def _add_similarity_edges(self, chunks: list, embeddings: list, threshold: float = 0.80):
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
    
    def _add_temporal_edges(self, chunks):
        """Connect chunks referencing same time periods."""
        chunk_times = {}
        for chunk in chunks:
            times = set(extract_time_references(chunk["text"]))
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
        data = nx.node_link_data(self.graph)
        self.graph_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.graph_path, "w") as f:
            json.dump(data, f, indent=2, default=str)
    
    def load(self):
        """Load graph from JSON."""
        if self.graph_path.exists():
            with open(self.graph_path) as f:
                data = json.load(f)
            self.graph = nx.node_link_graph(data)
        return self
    
    def get_stats(self) -> dict:
        """Get graph statistics."""
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
```

### Enhanced Retrieval

#### Balanced Retrieval by Lens

```python
def retrieve_balanced(
    query: str,
    table,  # LanceDB table
    embedder,  # Embedding function
    chunks_per_lens: int = 8
) -> list[dict]:
    """Retrieve chunks with guaranteed representation from each lens."""
    
    query_embedding = embedder.embed_query(query)
    
    lenses = [
        "your-voice",
        "team-structured",
        "team-conversational",
        "business-framework",
        "engineering",
        "external-analyst"
    ]
    
    all_results = []
    for lens in lenses:
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
```

#### Graph-Expanded Retrieval

```python
def retrieve_with_graph_expansion(
    query: str,
    table,
    embedder,
    graph: ContextGraph,
    initial_limit: int = 20,
    expansion_hops: int = 1,
    final_limit: int = 50
) -> list[dict]:
    """Retrieve chunks and expand via graph relationships."""
    
    query_embedding = embedder.embed_query(query)
    
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
    # Filter to only new IDs
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
    
    # Step 5: Re-rank by relevance and lens diversity
    # ... (optional: implement re-ranking logic)
    
    return unique_results[:final_limit]
```

### Contradiction Detection

```python
def detect_potential_contradictions(
    chunks: list[dict],
    graph: ContextGraph
) -> list[dict]:
    """Find chunks that may contradict each other."""
    
    contradictions = []
    
    # Group by topic
    topic_groups = {}
    for chunk in chunks:
        terms = graph.graph.nodes[chunk["id"]].get("key_terms", [])
        for term in terms:
            if term not in topic_groups:
                topic_groups[term] = []
            topic_groups[term].append(chunk)
    
    # Find cross-lens disagreements on same topic
    authority_order = {
        "your-voice": 1,
        "business-framework": 2,
        "team-structured": 3,
        "team-conversational": 4,
        "engineering": 5,
        "external-analyst": 6,
    }
    
    for topic, topic_chunks in topic_groups.items():
        if len(topic_chunks) < 2:
            continue
        
        # Check for different lenses discussing same topic
        lenses_present = set(c["lens"] for c in topic_chunks)
        
        # Flag if conversational disagrees with structured
        if "team-conversational" in lenses_present and "team-structured" in lenses_present:
            contradictions.append({
                "topic": topic,
                "type": "conversational_vs_structured",
                "chunks": [c for c in topic_chunks if c["lens"] in ["team-conversational", "team-structured"]],
                "note": "Team discussions may reveal concerns not in formal docs"
            })
        
        # Flag if engineering contradicts product plans
        if "engineering" in lenses_present and "team-structured" in lenses_present:
            contradictions.append({
                "topic": topic,
                "type": "engineering_vs_product",
                "chunks": [c for c in topic_chunks if c["lens"] in ["engineering", "team-structured"]],
                "note": "Engineering feasibility may conflict with product plans"
            })
    
    return contradictions
```

### Integration with Synthesis

Update the `generate` command to use enhanced retrieval:

```python
def generate_roadmap(context: str = "", use_opus: bool = False):
    """Generate master roadmap with graph-enhanced retrieval."""
    
    # Load graph
    graph = ContextGraph().load()
    
    # Queries for comprehensive retrieval
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
    for query in queries:
        chunks = retrieve_balanced(query, table, embedder, chunks_per_lens=5)
        all_chunks.extend(chunks)
    
    # Expand via graph
    expanded = retrieve_with_graph_expansion(
        queries[0],  # Primary query
        table,
        embedder,
        graph,
        initial_limit=30,
        expansion_hops=1,
        final_limit=60
    )
    
    # Deduplicate
    seen = set()
    final_chunks = []
    for chunk in all_chunks + expanded:
        if chunk["id"] not in seen:
            seen.add(chunk["id"])
            final_chunks.append(chunk)
    
    # Detect contradictions
    contradictions = detect_potential_contradictions(final_chunks, graph)
    
    # Format context for synthesis
    context_text = format_chunks_by_lens(final_chunks)
    
    # Add contradiction warnings
    if contradictions:
        context_text += "\n\n## Potential Contradictions Detected\n"
        for c in contradictions[:5]:  # Top 5
            context_text += f"\n### {c['topic']} ({c['type']})\n"
            context_text += f"Note: {c['note']}\n"
    
    # Call Claude for synthesis
    # ... rest of generation logic
```

---

## Part 3: Streamlit Integration

### New Page: Context Graph Visualization

Add a page to visualize and explore the graph.

```python
# In app.py, add new page

elif page == "🕸️ Context Graph":
    st.title("Context Graph")
    
    graph = ContextGraph().load()
    stats = graph.get_stats()
    
    # Stats
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Nodes", stats["nodes"])
    col2.metric("Edges", stats["edges"])
    col3.metric("Components", stats["components"])
    col4.metric("Density", f"{stats['density']:.3f}")
    
    # Edge type breakdown
    st.subheader("Edge Types")
    st.bar_chart(stats["edge_types"])
    
    # Interactive exploration
    st.subheader("Explore Connections")
    
    # Select a chunk to explore
    chunk_ids = list(graph.graph.nodes())
    selected = st.selectbox("Select a chunk", chunk_ids)
    
    if selected:
        node_data = graph.graph.nodes[selected]
        st.write("**Chunk Info:**")
        st.json(node_data)
        
        # Show connections
        neighbors = list(graph.graph.neighbors(selected))
        st.write(f"**Connected to {len(neighbors)} other chunks:**")
        
        for neighbor in neighbors[:10]:
            edge_data = graph.graph.edges[selected, neighbor]
            neighbor_data = graph.graph.nodes[neighbor]
            
            with st.expander(f"{edge_data['type']} → {neighbor_data.get('source_name', neighbor)}"):
                st.write(f"**Weight:** {edge_data.get('weight', 'N/A')}")
                st.write(f"**Lens:** {neighbor_data.get('lens', 'N/A')}")
                st.write(f"**Preview:** {neighbor_data.get('content_preview', 'N/A')}")
```

### Update Dashboard

Add graph stats to dashboard:

```python
# In dashboard page
st.subheader("Context Graph")
try:
    graph = ContextGraph().load()
    stats = graph.get_stats()
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Graph Nodes", stats["nodes"])
    col2.metric("Graph Edges", stats["edges"])
    col3.metric("Components", stats["components"])
except Exception:
    st.info("No context graph built yet. Ingest materials to build.")
```

### Update Ingest Flow

Rebuild graph after ingestion:

```python
def ingest_with_graph_update(path, lens):
    """Ingest documents and update context graph."""
    
    # ... existing ingestion logic ...
    
    # After adding to vector store, rebuild graph
    st.info("Rebuilding context graph...")
    
    # Get all chunks and embeddings from store
    all_chunks = table.to_pandas().to_dict('records')
    all_embeddings = [chunk["vector"] for chunk in all_chunks]
    
    # Build graph
    graph = ContextGraph()
    graph.build_from_chunks(all_chunks, all_embeddings)
    graph.save()
    
    st.success(f"Context graph updated: {graph.get_stats()['edges']} relationships found")
```

---

## Part 4: Updated Settings

Add chunk configuration to settings page:

```python
st.subheader("Chunking Configuration")

chunk_size = st.number_input(
    "Chunk Size (tokens)",
    min_value=256,
    max_value=4096,
    value=1024,
    help="Larger chunks preserve more context but reduce granularity"
)

chunk_overlap = st.number_input(
    "Chunk Overlap (tokens)",
    min_value=0,
    max_value=500,
    value=150,
    help="Overlap between adjacent chunks to maintain continuity"
)

similarity_threshold = st.slider(
    "Similarity Edge Threshold",
    min_value=0.5,
    max_value=0.95,
    value=0.80,
    help="Minimum similarity to create SIMILAR_TO edges in graph"
)

if st.button("Save Chunking Settings"):
    # Save to config
    save_config({
        "chunk_size": chunk_size,
        "chunk_overlap": chunk_overlap,
        "similarity_threshold": similarity_threshold
    })
    st.success("Settings saved. Re-ingest materials to apply.")
```

---

## Implementation Order

1. **Update chunking parameters** (5 min)
   - Change CHUNK_SIZE to 1024
   - Change CHUNK_OVERLAP to 150

2. **Add NetworkX dependency** (1 min)
   - `uv add networkx`

3. **Implement ContextGraph class** (30 min)
   - Node/edge creation
   - Save/load JSON
   - Statistics

4. **Implement key term extraction** (15 min)
   - Simple regex-based extraction
   - Time reference detection

5. **Implement enhanced retrieval** (20 min)
   - Balanced retrieval by lens
   - Graph expansion

6. **Implement contradiction detection** (15 min)
   - Cross-lens comparison
   - Warning generation

7. **Integrate with generate command** (15 min)
   - Use new retrieval
   - Add contradictions to context

8. **Add Streamlit pages** (30 min)
   - Context Graph visualization
   - Update dashboard
   - Update ingest flow

9. **Test end-to-end** (20 min)
   - Clear and re-ingest
   - Generate roadmap
   - Verify improvements

---

## Success Criteria

- [ ] Chunks are 1024 tokens with 150 overlap
- [ ] Context graph builds after ingestion
- [ ] Graph has SIMILAR_TO, SAME_SOURCE, TOPIC_OVERLAP, SEQUENTIAL, TEMPORAL_OVERLAP edges
- [ ] Retrieval pulls from all lenses proportionally
- [ ] Contradictions are detected and surfaced
- [ ] Synthesis output is more comprehensive (less reductive)
- [ ] Streamlit shows graph stats and exploration

---

## Expected Outcomes

After implementation:

| Metric | Before | After (Expected) |
|--------|--------|------------------|
| Avg tokens/chunk | 491 | ~950 |
| Total chunks | 669 | ~350 |
| Lens balance in retrieval | Skewed to your-voice | Even across lenses |
| Context in synthesis | Fragmented | Coherent with relationships |
| Contradictions surfaced | None | Explicit warnings |
