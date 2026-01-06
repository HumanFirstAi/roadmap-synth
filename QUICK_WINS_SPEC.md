# Quick Wins Specification (No Restructure)

## Approach

Add features directly to the existing `app.py` without restructuring. Zero risk to current functionality.

**Principle:** Small, additive changes. Each change is independent and can be reverted.

---

## Quick Win #1: Dashboard Attention Needed

**What:** Add an "Attention Needed" section to Dashboard showing items requiring action.

**Where:** Add to existing Dashboard page section in `app.py`

**Code to Add:**

```python
def render_attention_needed():
    """Render attention needed section on dashboard."""
    
    attention_items = []
    
    # Check for critical questions
    questions = load_questions()
    critical_pending = [q for q in questions if q.get("status") == "pending" and q.get("priority") == "critical"]
    if critical_pending:
        attention_items.append({
            "icon": "🔴",
            "message": f"{len(critical_pending)} critical question(s) pending",
            "action": "Go to Questions"
        })
    
    # Check for high priority pending questions
    high_pending = [q for q in questions if q.get("status") == "pending" and q.get("priority") == "high"]
    if high_pending:
        attention_items.append({
            "icon": "🟠",
            "message": f"{len(high_pending)} high priority question(s) pending",
            "action": "Go to Questions"
        })
    
    # Check for gaps without decisions
    graph = load_unified_graph()
    if graph:
        unaddressed_gaps = [
            g for g in graph.node_indices.get("gap", {}).values()
            if not g.addressed_by_decision
        ]
        critical_gaps = [g for g in unaddressed_gaps if g.severity in ["critical", "significant"]]
        if critical_gaps:
            attention_items.append({
                "icon": "⚠️",
                "message": f"{len(critical_gaps)} significant gap(s) without decisions",
                "action": "View Gaps"
            })
    
    # Check for graph sync needed
    # (Compare last sync time to last decision/assessment time)
    if needs_graph_sync():
        attention_items.append({
            "icon": "🔄",
            "message": "Knowledge graph needs sync",
            "action": "Sync Now"
        })
    
    # Render
    if attention_items:
        st.subheader("⚡ Attention Needed")
        for item in attention_items:
            col1, col2 = st.columns([4, 1])
            col1.markdown(f"{item['icon']} {item['message']}")
            col2.button(item['action'], key=f"attn_{item['message'][:10]}")
    else:
        st.success("✅ No items need attention")


def needs_graph_sync() -> bool:
    """Check if graph needs syncing based on file modification times."""
    try:
        graph_file = Path("data/unified_graph/graph.json")
        decisions_file = Path("data/questions/decisions.json")
        assessments_dir = Path("output/competitive")
        
        if not graph_file.exists():
            return True
        
        graph_mtime = graph_file.stat().st_mtime
        
        # Check if decisions are newer
        if decisions_file.exists() and decisions_file.stat().st_mtime > graph_mtime:
            return True
        
        # Check if any assessment is newer
        if assessments_dir.exists():
            for f in assessments_dir.glob("*.json"):
                if f.stat().st_mtime > graph_mtime:
                    return True
        
        return False
    except:
        return False
```

**Where to Insert in app.py:**

Find the Dashboard section and add after the metrics:

```python
elif page == "📊 Dashboard":
    st.title("📊 Dashboard")
    
    # ... existing metrics code ...
    
    st.divider()
    
    # ADD THIS:
    render_attention_needed()
    
    # ... rest of dashboard ...
```

---

## Quick Win #2: Question → Decision Flow

**What:** When answering a question, option to immediately create a decision from the answer.

**Where:** Modify the question answering section in `app.py`

**Code to Add/Modify:**

```python
def render_answer_question_form(question: dict):
    """Enhanced answer form with decision creation option."""
    
    st.subheader(f"Answer Question")
    
    # Display question
    st.info(f"**{question['question']}**")
    if question.get("context"):
        st.caption(f"Context: {question['context']}")
    
    # Related items
    if question.get("related_roadmap_items"):
        st.caption(f"Related: {', '.join(question['related_roadmap_items'])}")
    
    st.divider()
    
    # Answer fields
    answer_text = st.text_area(
        "Your Answer",
        height=120,
        key="answer_text",
        placeholder="Provide your answer to this question..."
    )
    
    col1, col2 = st.columns(2)
    with col1:
        answered_by = st.text_input("Answered By", key="answered_by")
    with col2:
        confidence = st.selectbox(
            "Confidence",
            ["high", "medium", "low"],
            key="answer_confidence"
        )
    
    st.divider()
    
    # Decision creation option
    create_decision = st.checkbox(
        "✅ Create decision from this answer",
        value=True,
        help="Automatically create a decision record that will be tracked in the Decision Log and override conflicting source content"
    )
    
    if create_decision:
        st.markdown("**Decision Details**")
        
        # Pre-populate decision from answer
        default_decision = answer_text[:150] if answer_text else ""
        
        decision_statement = st.text_input(
            "Decision Statement",
            value=default_decision,
            key="decision_statement",
            help="Concise statement of what was decided (will appear in Decision Log)"
        )
        
        decision_rationale = st.text_area(
            "Rationale",
            value=answer_text,
            height=80,
            key="decision_rationale",
            help="Why this decision was made"
        )
        
        decision_implications = st.text_input(
            "Implications (comma-separated)",
            key="decision_implications",
            placeholder="e.g., Timeline shifts to Q3, Need to inform customers"
        )
        
        decision_owner = st.text_input(
            "Decision Owner",
            value=answered_by,
            key="decision_owner",
            help="Who is responsible for executing this decision"
        )
    
    st.divider()
    
    # Submit button
    can_submit = bool(answer_text and answered_by)
    if create_decision:
        can_submit = can_submit and bool(decision_statement)
    
    if st.button("Submit Answer", type="primary", disabled=not can_submit):
        # Save answer
        answer_data = {
            "id": f"ans_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "question_id": question["id"],
            "answer": answer_text,
            "answered_by": answered_by,
            "confidence": confidence,
            "timestamp": datetime.now().isoformat()
        }
        
        # Update question status
        questions = load_questions()
        for q in questions:
            if q["id"] == question["id"]:
                q["status"] = "answered"
                q["answer"] = answer_text
                q["answered_by"] = answered_by
                q["answered_at"] = datetime.now().isoformat()
                break
        save_questions(questions)
        
        # Create decision if requested
        if create_decision:
            decision_data = {
                "id": f"dec_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "question_id": question["id"],
                "answer_id": answer_data["id"],
                "decision": decision_statement,
                "rationale": decision_rationale,
                "implications": [i.strip() for i in decision_implications.split(",") if i.strip()],
                "owner": decision_owner,
                "status": "active",
                "created_at": datetime.now().isoformat()
            }
            
            decisions = load_decisions()
            decisions.append(decision_data)
            save_decisions(decisions)
            
            st.success(f"✅ Answer submitted and decision **{decision_data['id']}** created!")
            
            # Prompt to sync graph
            st.info("💡 Run 'Sync Graph' to integrate this decision into the knowledge graph")
        else:
            st.success("✅ Answer submitted!")
        
        # Clear selection
        st.session_state.answering_question_id = None
        st.rerun()
```

**Integration Point:**

In the Questions page section, replace or enhance the existing answer form with this function.

---

## Quick Win #3: Decision Override Display

**What:** Show which source chunks a decision overrides in the Decision Log view.

**Where:** Enhance the Decisions display section in `app.py`

**Code to Add:**

```python
def render_decision_with_overrides(decision: dict):
    """Render a decision card showing what it overrides."""
    
    with st.container(border=True):
        # Header
        col1, col2 = st.columns([4, 1])
        with col1:
            status_icon = "✅" if decision.get("status") == "active" else "⏸️"
            st.markdown(f"### {status_icon} {decision['id']}")
        with col2:
            st.caption(decision.get("created_at", "")[:10])
        
        # Decision statement
        st.markdown(f"**Decision:** {decision['decision']}")
        
        # Rationale
        if decision.get("rationale"):
            with st.expander("Rationale"):
                st.write(decision["rationale"])
        
        # Implications
        if decision.get("implications"):
            st.markdown("**Implications:**")
            for imp in decision["implications"]:
                st.markdown(f"- {imp}")
        
        # Resolved question
        if decision.get("question_id"):
            st.caption(f"Resolves: {decision['question_id']}")
        
        # Owner
        if decision.get("owner"):
            st.caption(f"Owner: {decision['owner']}")
        
        st.divider()
        
        # OVERRIDES SECTION - This is the new part
        overrides = get_decision_overrides(decision["id"])
        
        if overrides:
            with st.expander(f"⚡ Overrides {len(overrides)} source chunk(s)", expanded=False):
                st.caption("This decision supersedes the following source content:")
                
                for chunk in overrides:
                    st.markdown(f"**{chunk.get('source_name', 'Unknown')}** ({chunk.get('lens', 'unknown')})")
                    st.text(chunk.get("content", chunk.get("text", ""))[:200] + "...")
                    st.divider()
        else:
            st.caption("No conflicting source chunks identified")
        
        # Actions
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("Mark for Review", key=f"review_{decision['id']}"):
                decision["status"] = "reviewing"
                save_decision_update(decision)
                st.rerun()
        with col2:
            if st.button("Supersede", key=f"supersede_{decision['id']}"):
                st.session_state.superseding_decision = decision["id"]
        with col3:
            if decision.get("status") != "active":
                if st.button("Reactivate", key=f"reactivate_{decision['id']}"):
                    decision["status"] = "active"
                    save_decision_update(decision)
                    st.rerun()


def get_decision_overrides(decision_id: str) -> list:
    """Get chunks that a decision overrides from the graph."""
    
    try:
        graph = load_unified_graph()
        if not graph or not graph.graph:
            return []
        
        overrides = []
        
        # Find OVERRIDES edges from this decision
        if decision_id in graph.graph:
            for neighbor in graph.graph.successors(decision_id):
                edge = graph.graph.edges.get((decision_id, neighbor), {})
                if edge.get("edge_type") == "OVERRIDES":
                    # Get chunk data
                    chunk = graph.node_indices.get("chunk", {}).get(neighbor)
                    if chunk:
                        overrides.append(chunk.__dict__ if hasattr(chunk, '__dict__') else chunk)
        
        return overrides
    except Exception as e:
        print(f"Error getting overrides: {e}")
        return []


def save_decision_update(decision: dict):
    """Update a single decision in the decisions file."""
    decisions = load_decisions()
    for i, d in enumerate(decisions):
        if d["id"] == decision["id"]:
            decisions[i] = decision
            break
    save_decisions(decisions)
```

---

## Quick Win #4: Authority-Aware Graph Query Display

**What:** When querying the knowledge graph, show results grouped by authority level with clear superseded indicators.

**Where:** Enhance the Knowledge Graph page section in `app.py`

**Code to Add:**

```python
def render_graph_query_results(results: dict):
    """Render graph query results grouped by authority level."""
    
    st.subheader("Results by Authority Level")
    
    st.caption("""
    Results are ordered by authority. Decisions (Level 1) override conflicting 
    chunks (Level 6). Content marked as superseded should be treated as outdated.
    """)
    
    # Level 1: Decisions
    decisions = results.get("decisions", [])
    if decisions:
        with st.expander(f"🔴 **LEVEL 1: DECISIONS** ({len(decisions)}) — Highest Authority", expanded=True):
            st.caption("These decisions are final and override conflicting source content.")
            for item in decisions[:10]:
                render_authority_result_card(item, "decision")
    
    # Level 2: Answered Questions
    answered = results.get("answered_questions", [])
    if answered:
        with st.expander(f"🟠 **LEVEL 2: ANSWERED QUESTIONS** ({len(answered)})", expanded=False):
            st.caption("Questions that have been resolved by decisions.")
            for item in answered[:10]:
                render_authority_result_card(item, "answered_question")
    
    # Level 3: Assessments
    assessments = results.get("assessments", [])
    if assessments:
        with st.expander(f"🟡 **LEVEL 3: ASSESSMENTS** ({len(assessments)})", expanded=False):
            st.caption("Analyzed intelligence from architecture, competitive, and impact assessments.")
            for item in assessments[:10]:
                render_authority_result_card(item, "assessment")
    
    # Level 4: Roadmap Items
    roadmap_items = results.get("roadmap_items", [])
    if roadmap_items:
        with st.expander(f"🟢 **LEVEL 4: ROADMAP ITEMS** ({len(roadmap_items)})", expanded=False):
            st.caption("Current roadmap items.")
            for item in roadmap_items[:10]:
                render_authority_result_card(item, "roadmap_item")
    
    # Level 5: Gaps
    gaps = results.get("gaps", [])
    if gaps:
        with st.expander(f"🔵 **LEVEL 5: GAPS** ({len(gaps)})", expanded=False):
            st.caption("Identified gaps from assessments, not yet addressed by decisions.")
            for item in gaps[:10]:
                render_authority_result_card(item, "gap")
    
    # Level 6: Chunks
    chunks = results.get("chunks", [])
    if chunks:
        superseded_count = len([c for c in chunks if c.get("superseded")])
        with st.expander(f"⚪ **LEVEL 6: SOURCE CHUNKS** ({len(chunks)}, {superseded_count} superseded)", expanded=False):
            st.caption("Raw source content. Superseded chunks have been overridden by decisions.")
            for item in chunks[:15]:
                render_authority_result_card(item, "chunk")
    
    # Level 7: Pending Questions
    pending = results.get("pending_questions", [])
    if pending:
        with st.expander(f"⬜ **LEVEL 7: PENDING QUESTIONS** ({len(pending)}) — Lowest Authority", expanded=False):
            st.caption("Open questions not yet resolved.")
            for item in pending[:10]:
                render_authority_result_card(item, "pending_question")


def render_authority_result_card(item: dict, item_type: str):
    """Render a single result card based on type."""
    
    data = item.get("data", item)
    similarity = item.get("similarity", 0)
    
    # Check if superseded
    is_superseded = item.get("superseded", False) or data.get("superseded_by")
    
    # Card styling
    if is_superseded:
        st.markdown(
            f"""<div style="opacity: 0.6; border-left: 3px solid #ff6b6b; padding-left: 10px;">""",
            unsafe_allow_html=True
        )
    
    with st.container(border=True):
        # Header with similarity score
        col1, col2 = st.columns([4, 1])
        
        with col1:
            if item_type == "decision":
                st.markdown(f"**{data.get('id', 'Unknown')}**")
                st.write(data.get("decision", ""))
            
            elif item_type == "chunk":
                source = data.get("source_name", "Unknown")
                lens = data.get("lens", "unknown")
                st.markdown(f"**{source}** ({lens})")
                content = data.get("content", data.get("text", ""))[:200]
                st.text(content + "..." if len(content) >= 200 else content)
            
            elif item_type == "roadmap_item":
                st.markdown(f"**{data.get('name', 'Unknown')}** ({data.get('horizon', '')})")
                st.write(data.get("description", "")[:150])
            
            elif item_type == "gap":
                severity = data.get("severity", "unknown")
                severity_icon = {"critical": "🔴", "significant": "🟠", "moderate": "🟡", "minor": "🟢"}.get(severity, "⚪")
                st.markdown(f"{severity_icon} **{data.get('description', '')[:100]}**")
            
            elif item_type == "assessment":
                st.markdown(f"**{data.get('assessment_type', '').title()} Assessment**")
                st.write(data.get("summary", "")[:150])
            
            elif item_type in ["answered_question", "pending_question"]:
                st.markdown(f"**{data.get('question', '')[:100]}**")
                if data.get("answer"):
                    st.caption(f"Answer: {data['answer'][:100]}...")
        
        with col2:
            st.caption(f"Score: {similarity:.2f}")
        
        # Superseded indicator
        if is_superseded:
            superseded_by = data.get("superseded_by") or item.get("superseded_by")
            st.warning(f"⚠️ SUPERSEDED by {superseded_by}")
    
    if is_superseded:
        st.markdown("</div>", unsafe_allow_html=True)
```

**Integration Point:**

In the Knowledge Graph page section, after calling `retrieve_with_authority()`, use this function to display results:

```python
elif page == "🕸️ Knowledge Graph":
    # ... existing code ...
    
    if query and st.button("Search"):
        graph = load_unified_graph()
        results = retrieve_with_authority(query, graph, include_superseded)
        
        # ADD THIS:
        render_graph_query_results(results)
```

---

## Quick Win #5: Source Lens Distribution

**What:** Visual bar showing distribution of sources by lens on the Sources page.

**Where:** Add to Sources page section in `app.py`

**Code to Add:**

```python
def render_lens_distribution():
    """Render visual distribution of sources by lens."""
    
    st.subheader("📊 Source Distribution by Lens")
    
    # Get counts by lens
    lens_counts = get_chunks_by_lens_count()
    
    if not lens_counts:
        st.info("No sources ingested yet")
        return
    
    # Define lens colors and order
    lens_order = [
        "your-voice",
        "team-structured", 
        "team-conversational",
        "business-framework",
        "engineering",
        "sales",
        "external-analyst"
    ]
    
    lens_colors = {
        "your-voice": "#e74c3c",
        "team-structured": "#3498db",
        "team-conversational": "#2ecc71",
        "business-framework": "#9b59b6",
        "engineering": "#f39c12",
        "sales": "#1abc9c",
        "external-analyst": "#34495e"
    }
    
    max_count = max(lens_counts.values()) if lens_counts else 1
    
    for lens in lens_order:
        count = lens_counts.get(lens, 0)
        if count == 0:
            continue
        
        pct = count / max_count
        color = lens_colors.get(lens, "#95a5a6")
        
        col1, col2, col3 = st.columns([2, 4, 1])
        
        with col1:
            st.markdown(f"**{lens}**")
        
        with col2:
            # Create a simple progress bar
            st.progress(pct)
        
        with col3:
            st.caption(f"{count} chunks")


def get_chunks_by_lens_count() -> dict:
    """Get count of chunks grouped by lens."""
    
    try:
        # If you have LanceDB table access
        table = get_lancedb_table()
        if table:
            df = table.to_pandas()
            return df.groupby("lens").size().to_dict()
    except:
        pass
    
    # Fallback: count from graph
    try:
        graph = load_unified_graph()
        if graph:
            lens_counts = {}
            for chunk in graph.node_indices.get("chunk", {}).values():
                lens = chunk.lens if hasattr(chunk, 'lens') else chunk.get("lens", "unknown")
                lens_counts[lens] = lens_counts.get(lens, 0) + 1
            return lens_counts
    except:
        pass
    
    return {}
```

**Integration Point:**

Add to the Sources page section:

```python
elif page == "📁 Sources":
    st.title("📁 Sources")
    
    # ADD THIS at the top:
    render_lens_distribution()
    
    st.divider()
    
    # ... rest of existing sources code ...
```

---

## Quick Win #6: Quick Actions on Dashboard

**What:** Add prominent quick action buttons for common workflows.

**Where:** Add to Dashboard page section in `app.py`

**Code to Add:**

```python
def render_quick_actions():
    """Render quick action buttons for common workflows."""
    
    st.subheader("⚡ Quick Actions")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("🔄 Generate Roadmap", use_container_width=True):
            with st.spinner("Generating roadmap..."):
                try:
                    result = generate_roadmap()
                    st.success("Roadmap generated!")
                    st.session_state.last_action = "roadmap_generated"
                except Exception as e:
                    st.error(f"Error: {e}")
    
    with col2:
        if st.button("🔄 Sync Graph", use_container_width=True):
            with st.spinner("Syncing knowledge graph..."):
                try:
                    graph = sync_all_to_graph()
                    node_count = graph.graph.number_of_nodes() if graph.graph else 0
                    st.success(f"Graph synced! {node_count} nodes")
                except Exception as e:
                    st.error(f"Error: {e}")
    
    with col3:
        pending_count = len([q for q in load_questions() if q.get("status") == "pending"])
        if st.button(f"❓ Answer Questions ({pending_count})", use_container_width=True):
            st.session_state.current_page = "❓ Open Questions"
            st.rerun()
    
    with col4:
        if st.button("📄 Ingest Document", use_container_width=True):
            st.session_state.current_page = "📁 Sources"
            st.session_state.show_ingest_form = True
            st.rerun()
```

**Integration Point:**

Add to Dashboard after title:

```python
elif page == "📊 Dashboard":
    st.title("📊 Dashboard")
    
    # ADD THIS:
    render_quick_actions()
    
    st.divider()
    
    # ... rest of dashboard ...
```

---

## Implementation Order

1. **Quick Win #6: Quick Actions** (5 min) — Easiest, high visibility
2. **Quick Win #1: Attention Needed** (15 min) — High value for power users
3. **Quick Win #5: Lens Distribution** (10 min) — Simple, visual improvement
4. **Quick Win #2: Question → Decision Flow** (20 min) — Core workflow improvement
5. **Quick Win #3: Decision Override Display** (15 min) — Shows authority system value
6. **Quick Win #4: Authority-Aware Results** (20 min) — Makes graph query useful

**Total estimated time: ~1.5 hours**

---

## Testing Checklist

After each quick win, verify:

- [ ] App still loads without errors
- [ ] Existing functionality unchanged
- [ ] New feature works as expected
- [ ] No Python exceptions in console
- [ ] UI renders correctly

---

## Rollback Plan

Each quick win is a single function or small code block. To rollback:

1. Delete the added function
2. Remove the function call from the page section
3. App returns to previous state

No database changes, no file structure changes, no risk to data.
