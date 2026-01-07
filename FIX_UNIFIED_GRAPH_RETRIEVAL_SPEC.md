# Fix: Unified Graph Retrieval Not Returning Non-Chunk Nodes

## Problem Statement

When querying via "Ask Your Roadmap", only chunks are being retrieved. Decisions, assessments, roadmap items, and gaps are not being returned even though they exist in the unified graph.

**Symptom:**
```
📊 Retrieval Statistics
Chunks: 20
Decisions: 0
Assessments: 0
Roadmap Items: 0
```

**Expected:**
```
📊 Retrieval Statistics
Chunks: 20
Decisions: 3
Assessments: 2
Roadmap Items: 5
Gaps: 4
```

---

## Diagnosis Steps

### Step 1: Check Graph Contents

First, verify what's actually in the unified graph:

```python
def diagnose_graph_contents():
    """Print diagnostic information about the unified graph."""
    
    graph = load_unified_graph()
    
    if not graph:
        print("❌ ERROR: Unified graph not loaded")
        return
    
    print("=" * 60)
    print("UNIFIED GRAPH DIAGNOSTICS")
    print("=" * 60)
    
    # 1. Check node counts by type
    print("\n1. NODE COUNTS BY TYPE:")
    print("-" * 40)
    
    node_types = {}
    for node_id in graph.graph.nodes():
        node_data = graph.graph.nodes[node_id]
        node_type = node_data.get("node_type", "unknown")
        node_types[node_type] = node_types.get(node_type, 0) + 1
    
    for node_type, count in sorted(node_types.items()):
        status = "✅" if count > 0 else "❌"
        print(f"  {status} {node_type}: {count}")
    
    # 2. Check node_indices
    print("\n2. NODE INDICES:")
    print("-" * 40)
    
    if hasattr(graph, 'node_indices'):
        for node_type, nodes in graph.node_indices.items():
            print(f"  {node_type}: {len(nodes)} indexed")
    else:
        print("  ❌ graph.node_indices not found!")
    
    # 3. Check edge types
    print("\n3. EDGE TYPES:")
    print("-" * 40)
    
    edge_types = {}
    for u, v, data in graph.graph.edges(data=True):
        edge_type = data.get("edge_type", "unknown")
        edge_types[edge_type] = edge_types.get(edge_type, 0) + 1
    
    for edge_type, count in sorted(edge_types.items()):
        print(f"  {edge_type}: {count}")
    
    # 4. Check connectivity from chunks to other types
    print("\n4. CHUNK CONNECTIVITY:")
    print("-" * 40)
    
    chunk_ids = [n for n, d in graph.graph.nodes(data=True) if d.get("node_type") == "chunk"]
    
    connections_to_types = {
        "decision": 0,
        "roadmap_item": 0,
        "assessment": 0,
        "gap": 0,
        "question": 0
    }
    
    for chunk_id in chunk_ids[:100]:  # Sample first 100
        for neighbor in graph.graph.neighbors(chunk_id):
            neighbor_type = graph.graph.nodes[neighbor].get("node_type", "unknown")
            if neighbor_type in connections_to_types:
                connections_to_types[neighbor_type] += 1
        
        for predecessor in graph.graph.predecessors(chunk_id):
            pred_type = graph.graph.nodes[predecessor].get("node_type", "unknown")
            if pred_type in connections_to_types:
                connections_to_types[pred_type] += 1
    
    for target_type, count in connections_to_types.items():
        status = "✅" if count > 0 else "❌"
        print(f"  {status} Chunks connected to {target_type}: {count}")
    
    # 5. Sample some non-chunk nodes
    print("\n5. SAMPLE NON-CHUNK NODES:")
    print("-" * 40)
    
    for node_type in ["decision", "roadmap_item", "assessment", "gap"]:
        nodes = [(n, d) for n, d in graph.graph.nodes(data=True) if d.get("node_type") == node_type]
        if nodes:
            node_id, node_data = nodes[0]
            print(f"\n  Sample {node_type}:")
            print(f"    ID: {node_id}")
            print(f"    Data keys: {list(node_data.keys())}")
            
            # Check edges
            out_edges = list(graph.graph.neighbors(node_id))
            in_edges = list(graph.graph.predecessors(node_id))
            print(f"    Outgoing edges: {len(out_edges)}")
            print(f"    Incoming edges: {len(in_edges)}")
        else:
            print(f"\n  ❌ No {node_type} nodes found!")
    
    print("\n" + "=" * 60)
    
    return node_types, edge_types, connections_to_types


# Run this diagnostic
diagnose_graph_contents()
```

### Step 2: Check Retrieval Pipeline

Add logging to see where retrieval fails:

```python
def retrieve_full_context_debug(
    parsed_query: ParsedQuery,
    max_chunks: int = 30,
    max_per_category: int = 10
) -> RetrievalResult:
    """
    Retrieve context with debug logging.
    """
    
    print("\n" + "=" * 60)
    print("RETRIEVAL DEBUG")
    print("=" * 60)
    
    query_text = parsed_query.original_query
    topics = parsed_query.topics
    
    print(f"\nQuery: {query_text}")
    print(f"Topics filter: {topics}")
    
    # === STAGE 1: LanceDB ===
    print("\n--- STAGE 1: LanceDB Semantic Search ---")
    
    query_embedding = get_embedding(query_text)
    table = get_lancedb_table()
    
    if table:
        semantic_results = table.search(query_embedding).limit(max_chunks).to_list()
        print(f"✅ Found {len(semantic_results)} chunks from LanceDB")
    else:
        semantic_results = []
        print("❌ LanceDB table not available")
    
    initial_chunk_ids = [r.get("id", r.get("chunk_id")) for r in semantic_results]
    print(f"   Chunk IDs: {initial_chunk_ids[:5]}...")
    
    # === STAGE 2: Chunk Context Graph ===
    print("\n--- STAGE 2: Chunk Context Graph Expansion ---")
    
    chunk_graph = load_chunk_context_graph()
    expanded_chunk_ids = set(initial_chunk_ids)
    
    if chunk_graph:
        print(f"✅ Chunk context graph loaded: {chunk_graph.number_of_nodes()} nodes")
        
        for chunk_id in initial_chunk_ids[:10]:
            if chunk_id in chunk_graph:
                neighbors = list(chunk_graph.neighbors(chunk_id))
                expanded_chunk_ids.update(neighbors[:5])
                print(f"   {chunk_id} → {len(neighbors)} neighbors")
            else:
                print(f"   ⚠️ {chunk_id} not in chunk graph")
    else:
        print("❌ Chunk context graph not available")
    
    print(f"   Expanded to {len(expanded_chunk_ids)} chunk IDs")
    
    # === STAGE 3: Unified Knowledge Graph ===
    print("\n--- STAGE 3: Unified Knowledge Graph Traversal ---")
    
    unified_graph = load_unified_graph()
    
    if not unified_graph:
        print("❌ Unified graph not loaded!")
        return empty_result()
    
    print(f"✅ Unified graph loaded")
    
    # Check if graph has the graph attribute
    if not hasattr(unified_graph, 'graph'):
        print("❌ unified_graph.graph not found!")
        return empty_result()
    
    print(f"   Total nodes: {unified_graph.graph.number_of_nodes()}")
    print(f"   Total edges: {unified_graph.graph.number_of_edges()}")
    
    # Check which chunk IDs exist in unified graph
    chunks_in_unified = [cid for cid in expanded_chunk_ids if cid in unified_graph.graph]
    print(f"   Chunks found in unified graph: {len(chunks_in_unified)} / {len(expanded_chunk_ids)}")
    
    if not chunks_in_unified:
        print("   ❌ No chunks from LanceDB found in unified graph!")
        print("   This means chunks are not being added to unified graph during sync")
    
    # Traverse from chunks
    print("\n   Traversing from chunks...")
    
    related_nodes = {}
    nodes_by_type = {"decision": [], "roadmap_item": [], "assessment": [], "gap": [], "question": [], "chunk": []}
    
    for chunk_id in chunks_in_unified[:20]:
        # Get outgoing neighbors
        if chunk_id in unified_graph.graph:
            for neighbor in unified_graph.graph.neighbors(chunk_id):
                neighbor_data = unified_graph.graph.nodes.get(neighbor, {})
                neighbor_type = neighbor_data.get("node_type", "unknown")
                edge_data = unified_graph.graph.edges.get((chunk_id, neighbor), {})
                
                print(f"      {chunk_id} --[{edge_data.get('edge_type', '?')}]--> {neighbor} ({neighbor_type})")
                
                if neighbor not in related_nodes:
                    related_nodes[neighbor] = neighbor_data
                    nodes_by_type.get(neighbor_type, []).append(neighbor)
            
            # Get incoming neighbors (predecessors)
            for predecessor in unified_graph.graph.predecessors(chunk_id):
                pred_data = unified_graph.graph.nodes.get(predecessor, {})
                pred_type = pred_data.get("node_type", "unknown")
                edge_data = unified_graph.graph.edges.get((predecessor, chunk_id), {})
                
                print(f"      {predecessor} ({pred_type}) --[{edge_data.get('edge_type', '?')}]--> {chunk_id}")
                
                if predecessor not in related_nodes:
                    related_nodes[predecessor] = pred_data
                    nodes_by_type.get(pred_type, []).append(predecessor)
    
    print(f"\n   Nodes found by type:")
    for node_type, nodes in nodes_by_type.items():
        status = "✅" if nodes else "❌"
        print(f"      {status} {node_type}: {len(nodes)}")
    
    # === STAGE 4: Direct search of non-chunk nodes ===
    print("\n--- STAGE 4: Direct Search of Non-Chunk Nodes ---")
    
    # If traversal didn't find them, search directly
    for node_type in ["decision", "roadmap_item", "assessment", "gap"]:
        if not nodes_by_type.get(node_type):
            print(f"\n   Searching {node_type} nodes directly...")
            
            type_nodes = [
                (n, d) for n, d in unified_graph.graph.nodes(data=True)
                if d.get("node_type") == node_type
            ]
            print(f"   Found {len(type_nodes)} {node_type} nodes in graph")
            
            # Check if any match query terms
            query_terms = extract_key_terms_simple(query_text)
            matches = []
            
            for node_id, node_data in type_nodes:
                # Get searchable text from node
                searchable = " ".join([
                    str(node_data.get("data", {}).get("name", "")),
                    str(node_data.get("data", {}).get("description", "")),
                    str(node_data.get("data", {}).get("decision", "")),
                    str(node_data.get("data", {}).get("summary", "")),
                ]).lower()
                
                if any(term in searchable for term in query_terms):
                    matches.append((node_id, node_data))
            
            print(f"   Matches for query terms: {len(matches)}")
            for node_id, _ in matches[:3]:
                print(f"      - {node_id}")
    
    print("\n" + "=" * 60)


# Run this before the actual retrieval
retrieve_full_context_debug(parsed_query)
```

---

## Likely Issues and Fixes

### Issue 1: Chunks Not Added to Unified Graph

**Symptom:** Chunks from LanceDB don't exist in unified graph

**Cause:** `sync_all_to_graph()` may not be adding chunks, or chunk IDs don't match between LanceDB and graph

**Fix:**

```python
def sync_chunks_to_unified_graph(graph):
    """Ensure all chunks from LanceDB are in the unified graph."""
    
    table = get_lancedb_table()
    if not table:
        return 0
    
    chunks = table.to_pandas().to_dict('records')
    added = 0
    
    for chunk in chunks:
        chunk_id = chunk.get("id", chunk.get("chunk_id"))
        
        if not chunk_id:
            continue
        
        if chunk_id not in graph.graph:
            # Add chunk node
            graph.graph.add_node(
                chunk_id,
                node_type="chunk",
                data=chunk
            )
            
            # Add to index
            if "chunk" not in graph.node_indices:
                graph.node_indices["chunk"] = {}
            graph.node_indices["chunk"][chunk_id] = chunk
            
            added += 1
    
    print(f"Added {added} chunks to unified graph")
    return added
```

### Issue 2: No Edges Between Chunks and Other Nodes

**Symptom:** Chunks exist but have no edges to decisions/roadmap items/assessments

**Cause:** Edges aren't being created during sync

**Fix:**

```python
def create_chunk_to_roadmap_edges(graph):
    """Create SUPPORTED_BY edges between roadmap items and relevant chunks."""
    
    roadmap_items = graph.node_indices.get("roadmap_item", {})
    chunks = graph.node_indices.get("chunk", {})
    
    edges_created = 0
    
    for item_id, item in roadmap_items.items():
        item_data = item if isinstance(item, dict) else item.__dict__
        item_name = item_data.get("name", "").lower()
        item_desc = item_data.get("description", "").lower()
        item_text = f"{item_name} {item_desc}"
        
        # Extract key terms from roadmap item
        item_terms = extract_key_terms_simple(item_text)
        
        if not item_terms:
            continue
        
        # Find chunks that mention these terms
        for chunk_id, chunk in chunks.items():
            chunk_data = chunk if isinstance(chunk, dict) else chunk.__dict__
            chunk_content = chunk_data.get("content", chunk_data.get("text", "")).lower()
            
            # Check for term overlap
            matches = sum(1 for term in item_terms if term in chunk_content)
            
            if matches >= 2:  # At least 2 term matches
                # Create edge: roadmap_item -[SUPPORTED_BY]-> chunk
                if not graph.graph.has_edge(item_id, chunk_id):
                    graph.graph.add_edge(
                        item_id,
                        chunk_id,
                        edge_type="SUPPORTED_BY",
                        weight=matches / len(item_terms)
                    )
                    edges_created += 1
    
    print(f"Created {edges_created} SUPPORTED_BY edges")
    return edges_created


def create_decision_to_chunk_edges(graph):
    """Create OVERRIDES edges between decisions and relevant chunks."""
    
    decisions = graph.node_indices.get("decision", {})
    chunks = graph.node_indices.get("chunk", {})
    
    edges_created = 0
    
    for dec_id, dec in decisions.items():
        dec_data = dec if isinstance(dec, dict) else dec.__dict__
        dec_text = dec_data.get("decision", "").lower()
        dec_rationale = dec_data.get("rationale", "").lower()
        full_text = f"{dec_text} {dec_rationale}"
        
        # Extract key terms
        dec_terms = extract_key_terms_simple(full_text)
        
        if not dec_terms:
            continue
        
        # Find chunks that might be overridden
        for chunk_id, chunk in chunks.items():
            chunk_data = chunk if isinstance(chunk, dict) else chunk.__dict__
            chunk_content = chunk_data.get("content", chunk_data.get("text", "")).lower()
            
            matches = sum(1 for term in dec_terms if term in chunk_content)
            
            if matches >= 2:
                if not graph.graph.has_edge(dec_id, chunk_id):
                    graph.graph.add_edge(
                        dec_id,
                        chunk_id,
                        edge_type="OVERRIDES",
                        weight=matches / len(dec_terms)
                    )
                    edges_created += 1
    
    print(f"Created {edges_created} OVERRIDES edges")
    return edges_created


def create_assessment_edges(graph):
    """Create edges between assessments and chunks/roadmap items."""
    
    assessments = graph.node_indices.get("assessment", {})
    chunks = graph.node_indices.get("chunk", {})
    roadmap_items = graph.node_indices.get("roadmap_item", {})
    
    edges_created = 0
    
    for assess_id, assess in assessments.items():
        assess_data = assess if isinstance(assess, dict) else assess.__dict__
        assess_summary = assess_data.get("summary", "").lower()
        
        assess_terms = extract_key_terms_simple(assess_summary)
        
        if not assess_terms:
            continue
        
        # Link to roadmap items
        for item_id, item in roadmap_items.items():
            item_data = item if isinstance(item, dict) else item.__dict__
            item_text = f"{item_data.get('name', '')} {item_data.get('description', '')}".lower()
            
            matches = sum(1 for term in assess_terms if term in item_text)
            
            if matches >= 2:
                if not graph.graph.has_edge(assess_id, item_id):
                    graph.graph.add_edge(
                        assess_id,
                        item_id,
                        edge_type="ANALYZES_ITEM"
                    )
                    edges_created += 1
        
        # Link to chunks
        for chunk_id, chunk in list(chunks.items())[:100]:  # Limit for performance
            chunk_data = chunk if isinstance(chunk, dict) else chunk.__dict__
            chunk_content = chunk_data.get("content", chunk_data.get("text", "")).lower()
            
            matches = sum(1 for term in assess_terms if term in chunk_content)
            
            if matches >= 3:
                if not graph.graph.has_edge(assess_id, chunk_id):
                    graph.graph.add_edge(
                        assess_id,
                        chunk_id,
                        edge_type="ANALYZES_CHUNK"
                    )
                    edges_created += 1
    
    print(f"Created {edges_created} assessment edges")
    return edges_created
```

### Issue 3: Traversal Not Following Edges Properly

**Symptom:** Edges exist but traversal doesn't find connected nodes

**Cause:** Traversal only following outgoing edges, not incoming; or only checking immediate neighbors

**Fix:**

```python
def traverse_unified_graph_fixed(
    graph,
    seed_ids: list[str],
    max_hops: int = 2
) -> dict[str, dict]:
    """
    Fixed traversal that follows both directions and all edge types.
    """
    
    results = {}
    visited = set()
    
    # Start with seed IDs that exist in graph
    valid_seeds = [sid for sid in seed_ids if sid in graph.graph]
    
    if not valid_seeds:
        print(f"Warning: None of {len(seed_ids)} seed IDs found in graph")
        return results
    
    queue = [(sid, 0) for sid in valid_seeds]
    
    while queue:
        node_id, hops = queue.pop(0)
        
        if node_id in visited:
            continue
        
        visited.add(node_id)
        
        # Get node data
        node_attrs = graph.graph.nodes.get(node_id, {})
        node_type = node_attrs.get("node_type", "chunk")
        node_data = node_attrs.get("data", node_attrs)
        
        # Store in results
        results[node_id] = {
            "node_type": node_type,
            "id": node_id,
            **node_data
        }
        
        if hops >= max_hops:
            continue
        
        # Follow OUTGOING edges (this node -> neighbors)
        for neighbor in graph.graph.successors(node_id):
            if neighbor not in visited:
                queue.append((neighbor, hops + 1))
        
        # Follow INCOMING edges (predecessors -> this node)
        for predecessor in graph.graph.predecessors(node_id):
            if predecessor not in visited:
                queue.append((predecessor, hops + 1))
    
    return results
```

### Issue 4: Direct Search Fallback

If traversal still doesn't work, add direct search of non-chunk nodes:

```python
def search_non_chunk_nodes_directly(
    graph,
    query: str,
    topics: list[str],
    max_per_type: int = 10
) -> dict[str, list]:
    """
    Directly search non-chunk nodes by keyword matching.
    Fallback when graph traversal doesn't find connections.
    """
    
    query_terms = extract_key_terms_simple(query.lower())
    
    # Add topic terms
    for topic in topics:
        query_terms.extend(KNOWN_TOPICS.get(topic, [topic]))
    
    query_terms = list(set(query_terms))  # Dedupe
    
    results = {
        "decisions": [],
        "roadmap_items": [],
        "assessments": [],
        "gaps": [],
        "questions": []
    }
    
    type_mapping = {
        "decision": "decisions",
        "roadmap_item": "roadmap_items",
        "assessment": "assessments",
        "gap": "gaps",
        "question": "questions"
    }
    
    for node_id, node_attrs in graph.graph.nodes(data=True):
        node_type = node_attrs.get("node_type", "chunk")
        
        if node_type == "chunk":
            continue
        
        result_key = type_mapping.get(node_type)
        if not result_key:
            continue
        
        # Get searchable text
        node_data = node_attrs.get("data", node_attrs)
        
        searchable_fields = [
            node_data.get("name", ""),
            node_data.get("description", ""),
            node_data.get("decision", ""),
            node_data.get("rationale", ""),
            node_data.get("summary", ""),
            node_data.get("question", ""),
            node_data.get("answer", ""),
        ]
        
        searchable_text = " ".join(str(f) for f in searchable_fields).lower()
        
        # Score by term matches
        matches = sum(1 for term in query_terms if term in searchable_text)
        
        if matches >= 1:  # At least one match
            result_item = {
                "id": node_id,
                "node_type": node_type,
                "match_score": matches / len(query_terms) if query_terms else 0,
                **node_data
            }
            results[result_key].append(result_item)
    
    # Sort by match score and limit
    for key in results:
        results[key] = sorted(
            results[key],
            key=lambda x: x.get("match_score", 0),
            reverse=True
        )[:max_per_type]
    
    return results
```

---

## Updated retrieve_full_context Function

```python
def retrieve_full_context(
    parsed_query: ParsedQuery,
    max_chunks: int = 30,
    max_per_category: int = 10
) -> RetrievalResult:
    """
    Retrieve context from all three data stores.
    
    FIXED: Now properly retrieves non-chunk nodes via:
    1. Graph traversal from chunks
    2. Direct search fallback
    """
    
    import time
    start_time = time.time()
    
    query_text = parsed_query.original_query
    topics = parsed_query.topics
    keywords = parsed_query.keywords
    
    # === STAGE 1: LanceDB Semantic Search ===
    
    query_embedding = get_embedding(query_text)
    
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
        for chunk_id in initial_chunk_ids[:10]:
            connected = expand_via_chunk_graph(
                chunk_graph,
                chunk_id,
                max_hops=1,
                edge_types=["SIMILAR_TO", "SAME_SOURCE", "TOPIC_OVERLAP"]
            )
            expanded_chunk_ids.update(connected)
    
    expanded_chunk_ids = list(expanded_chunk_ids)[:max_chunks]
    
    # === STAGE 3: Unified Knowledge Graph ===
    
    unified_graph = load_unified_graph()
    
    # Initialize containers
    decisions = []
    answered_questions = []
    assessments = []
    roadmap_items = []
    gaps = []
    chunks = []
    pending_questions = []
    
    seen_ids = set()
    
    if unified_graph:
        # METHOD 1: Traverse from chunks
        related_nodes = traverse_unified_graph_fixed(
            unified_graph,
            seed_ids=expanded_chunk_ids,
            max_hops=2
        )
        
        # Categorize traversal results
        for node_id, node_data in related_nodes.items():
            if node_id in seen_ids:
                continue
            seen_ids.add(node_id)
            
            node_type = node_data.get("node_type", "chunk")
            
            # Apply topic filter
            if topics and not node_matches_topics(node_data, topics):
                continue
            
            if node_type == "decision":
                if node_data.get("status", "active") == "active":
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
                if not node_data.get("superseded_by"):
                    chunks.append(node_data)
        
        # METHOD 2: Direct search fallback for non-chunk nodes
        # If traversal didn't find enough, search directly
        
        if len(decisions) == 0 or len(roadmap_items) == 0 or len(assessments) == 0:
            direct_results = search_non_chunk_nodes_directly(
                unified_graph,
                query_text,
                topics,
                max_per_type=max_per_category
            )
            
            # Add direct search results (avoid duplicates)
            for dec in direct_results.get("decisions", []):
                if dec.get("id") not in seen_ids:
                    seen_ids.add(dec["id"])
                    if dec.get("status", "active") == "active":
                        decisions.append(dec)
            
            for item in direct_results.get("roadmap_items", []):
                if item.get("id") not in seen_ids:
                    seen_ids.add(item["id"])
                    roadmap_items.append(item)
            
            for assess in direct_results.get("assessments", []):
                if assess.get("id") not in seen_ids:
                    seen_ids.add(assess["id"])
                    assessments.append(assess)
            
            for gap in direct_results.get("gaps", []):
                if gap.get("id") not in seen_ids:
                    seen_ids.add(gap["id"])
                    gaps.append(gap)
            
            for q in direct_results.get("questions", []):
                if q.get("id") not in seen_ids:
                    seen_ids.add(q["id"])
                    if q.get("status") == "pending":
                        pending_questions.append(q)
    
    # Add chunks from semantic results not yet included
    for result in semantic_results:
        chunk_id = result.get("id", result.get("chunk_id"))
        if chunk_id not in seen_ids:
            seen_ids.add(chunk_id)
            chunks.append(result)
    
    # === STAGE 4: Sort and Limit ===
    
    decisions = sorted(decisions, key=lambda x: x.get("created_at", ""), reverse=True)[:max_per_category]
    gaps = sorted(gaps, key=lambda x: gap_severity_score(x), reverse=True)[:max_per_category]
    pending_questions = sorted(pending_questions, key=lambda x: priority_score(x), reverse=True)[:max_per_category]
    roadmap_items = sorted(roadmap_items, key=lambda x: horizon_score(x))[:max_per_category]
    assessments = assessments[:max_per_category]
    answered_questions = answered_questions[:max_per_category]
    chunks = chunks[:max_chunks]
    
    elapsed_ms = int((time.time() - start_time) * 1000)
    
    return RetrievalResult(
        decisions=decisions,
        answered_questions=answered_questions,
        assessments=assessments,
        roadmap_items=roadmap_items,
        gaps=gaps,
        chunks=chunks,
        pending_questions=pending_questions,
        total_sources=len(seen_ids),
        retrieval_time_ms=elapsed_ms,
        topic_filter_applied=topics
    )
```

---

## Updated sync_all_to_graph Function

```python
def sync_all_to_graph() -> UnifiedContextGraph:
    """
    Sync all data sources to unified graph.
    
    FIXED: Now properly adds chunks and creates edges.
    """
    
    graph = load_unified_graph() or UnifiedContextGraph()
    
    print("Syncing all data to unified graph...")
    
    # 1. Sync chunks from LanceDB
    print("\n1. Syncing chunks...")
    sync_chunks_to_unified_graph(graph)
    
    # 2. Sync roadmap items
    print("\n2. Syncing roadmap items...")
    roadmap = load_current_roadmap_structured()
    if roadmap:
        for item in roadmap.get("items", []):
            item_id = f"ri_{item.get('name', 'unknown').lower().replace(' ', '_')}"
            if item_id not in graph.graph:
                graph.graph.add_node(item_id, node_type="roadmap_item", data=item)
                graph.node_indices.setdefault("roadmap_item", {})[item_id] = item
        print(f"   Synced {len(roadmap.get('items', []))} roadmap items")
    
    # 3. Sync decisions
    print("\n3. Syncing decisions...")
    decisions = load_decisions()
    for dec in decisions:
        dec_id = dec.get("id", f"dec_{len(graph.node_indices.get('decision', {}))}")
        if dec_id not in graph.graph:
            graph.graph.add_node(dec_id, node_type="decision", data=dec)
            graph.node_indices.setdefault("decision", {})[dec_id] = dec
    print(f"   Synced {len(decisions)} decisions")
    
    # 4. Sync questions
    print("\n4. Syncing questions...")
    questions = load_questions()
    for q in questions:
        q_id = q.get("id", f"q_{len(graph.node_indices.get('question', {}))}")
        if q_id not in graph.graph:
            graph.graph.add_node(q_id, node_type="question", data=q)
            graph.node_indices.setdefault("question", {})[q_id] = q
    print(f"   Synced {len(questions)} questions")
    
    # 5. Sync assessments
    print("\n5. Syncing assessments...")
    assessments = load_all_assessments()
    for assess in assessments:
        assess_id = assess.get("id", f"assess_{len(graph.node_indices.get('assessment', {}))}")
        if assess_id not in graph.graph:
            graph.graph.add_node(assess_id, node_type="assessment", data=assess)
            graph.node_indices.setdefault("assessment", {})[assess_id] = assess
    print(f"   Synced {len(assessments)} assessments")
    
    # 6. Sync gaps
    print("\n6. Syncing gaps...")
    gaps = load_all_gaps()
    for gap in gaps:
        gap_id = gap.get("id", f"gap_{len(graph.node_indices.get('gap', {}))}")
        if gap_id not in graph.graph:
            graph.graph.add_node(gap_id, node_type="gap", data=gap)
            graph.node_indices.setdefault("gap", {})[gap_id] = gap
    print(f"   Synced {len(gaps)} gaps")
    
    # 7. Create edges between nodes
    print("\n7. Creating edges...")
    create_chunk_to_roadmap_edges(graph)
    create_decision_to_chunk_edges(graph)
    create_assessment_edges(graph)
    
    # 8. Save graph
    print("\n8. Saving graph...")
    save_unified_graph(graph)
    
    # Summary
    print("\n" + "=" * 40)
    print("SYNC COMPLETE")
    print("=" * 40)
    print(f"Total nodes: {graph.graph.number_of_nodes()}")
    print(f"Total edges: {graph.graph.number_of_edges()}")
    
    for node_type, nodes in graph.node_indices.items():
        print(f"  {node_type}: {len(nodes)}")
    
    return graph
```

---

## Testing Checklist

1. [ ] Run `diagnose_graph_contents()` - verify nodes exist for each type
2. [ ] Run `sync_all_to_graph()` - verify it adds chunks and creates edges
3. [ ] Run `diagnose_graph_contents()` again - verify edges now exist
4. [ ] Test query - verify non-chunk nodes appear in results
5. [ ] Verify edge counts: chunks connected to roadmap items, decisions, assessments

---

## Implementation Order

1. **Add diagnostic function** - `diagnose_graph_contents()`
2. **Run diagnostic** - identify which issue(s) exist
3. **Fix sync function** - ensure chunks and edges are created
4. **Fix traversal function** - ensure both directions are followed
5. **Add direct search fallback** - catch anything traversal misses
6. **Update retrieve_full_context** - use fixed functions
7. **Re-run sync** - rebuild graph with edges
8. **Test query** - verify results include all node types

---

## Estimated Time

- Diagnostic functions: 20 min
- Fix sync function: 30 min
- Fix traversal: 20 min
- Direct search fallback: 20 min
- Integration and testing: 30 min

**Total: ~2 hours**
