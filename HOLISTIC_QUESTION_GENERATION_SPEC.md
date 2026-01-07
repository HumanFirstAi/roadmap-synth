# Holistic Question Generation Specification

## Overview

Replace inline question generation (during synthesis/assessments) with a dedicated **"Generate Questions"** action that:

1. Analyzes current state holistically
2. Generates LLM questions aware of what's already resolved
3. Derives questions automatically from graph analysis
4. Deduplicates against existing questions
5. Marks stale questions as obsolete
6. Preserves validation feedback on unchanged questions

---

## Current vs Proposed

### Current: Inline Generation (Problems)

```
Synthesis → generates questions (doesn't know about assessments)
     ↓
Arch Assessment → generates questions (doesn't know about competitive)
     ↓
Competitive Assessment → generates questions (may duplicate)
     ↓
RESULT: Duplicate, stale, uncoordinated questions
```

### Proposed: On-Demand Holistic Generation

```
Synthesis → creates roadmap (no questions)
     ↓
Arch Assessment → creates assessment (no questions)
     ↓
Competitive Assessment → creates assessment (no questions)
     ↓
User clicks "Generate Questions"
     ↓
System analyzes EVERYTHING holistically
     ↓
RESULT: Clean, deduplicated, current questions
```

---

## Question Sources

### 1. LLM-Generated Questions

Claude analyzes the full context and generates questions:

| Source | What It Looks At | Question Types |
|--------|------------------|----------------|
| Roadmap | Items, timelines, dependencies | Feasibility, timing, scope |
| Architecture Assessment | Gaps, blockers, effort | Technical feasibility, investment |
| Competitive Assessment | Threats, gaps, timing | Strategic response, prioritization |
| Source Tensions | Conflicting statements | Clarification, resolution |

### 2. Derived Questions (Automatic)

System analyzes the graph and derives questions algorithmically:

| Detection | Pattern | Generated Question |
|-----------|---------|-------------------|
| Contradiction | your-voice says X, team says Y | "Conflicting information: [X] vs [Y]. Which is correct?" |
| Missing Coverage | Roadmap item has no engineering sources | "Has engineering validated feasibility of [item]?" |
| Missing Owner | Item mentioned, no team assigned | "Who owns delivery of [item]?" |
| Dependency Conflict | A depends on B, but B is later | "How can [A] ship in [horizon] if [B] is in [later horizon]?" |
| Stale Source | Source >90 days, no updates | "Is the plan for [topic] still current?" |
| Unaddressed Gap | Gap identified, no decision | "How should we address [gap]?" |
| Timeline Uncertainty | Multiple dates mentioned | "What is the committed date for [item]?" |

---

## Data Model

### Question Structure (Updated)

```python
{
    "id": "q_001",
    "question": "Can Catalog API migration be completed in Q2?",
    "audience": "engineering",
    "category": "feasibility",
    "priority": "high",
    "context": "Multiple roadmap items depend on this timeline",
    "status": "pending",  # pending, answered, obsolete, deferred
    
    # === NEW FIELDS ===
    
    # Generation metadata
    "generation": {
        "type": "llm",  # llm | derived
        "source": "roadmap_analysis",  # roadmap_analysis | arch_assessment | competitive_assessment | contradiction | missing_coverage | dependency_conflict | etc.
        "generated_at": "2025-01-15T10:30:00Z",
        "generation_run_id": "gen_20250115_103000",  # Groups questions from same run
        "prompt_context": "Based on roadmap item 'Catalog GA' and arch assessment showing partial support"
    },
    
    # For derived questions - the evidence
    "derivation": {
        "pattern": "contradiction",  # Only for derived questions
        "evidence": [
            {
                "source_id": "chunk_123",
                "source_name": "Q4 Strategy",
                "lens": "your-voice",
                "content": "Catalog targets Q2",
            },
            {
                "source_id": "chunk_456",
                "source_name": "Eng Standup Notes",
                "lens": "team-conversational",
                "content": "Q2 is not realistic, Q3 more likely",
            }
        ]
    },
    
    # Lifecycle tracking
    "lifecycle": {
        "created_at": "2025-01-15T10:30:00Z",
        "obsoleted_at": null,
        "obsoleted_by": null,  # Decision ID that made this obsolete
        "obsolete_reason": null,
        "refreshed_at": "2025-01-16T09:00:00Z",  # Last generation run that kept this question
        "times_refreshed": 3  # How many generation runs kept this question
    },
    
    # Deduplication
    "deduplication": {
        "fingerprint": "catalog_api_q2_feasibility",  # Semantic fingerprint for matching
        "similar_questions": ["q_005", "q_012"],  # Related questions (not duplicates)
        "supersedes": null,  # If this replaced another question
        "superseded_by": null  # If this was replaced
    },
    
    # Existing fields preserved
    "source_references": [...],
    "validation": {...},
    "answer": null,
    "answered_by": null,
    "answered_at": null
}
```

### Generation Run Record

```python
{
    "id": "gen_20250115_103000",
    "timestamp": "2025-01-15T10:30:00Z",
    "triggered_by": "user",  # user | auto
    
    # What was analyzed
    "context_analyzed": {
        "roadmap_version": "2025-01-15",
        "roadmap_items": 24,
        "arch_assessments": ["align_001"],
        "competitive_assessments": ["analysis_001"],
        "active_decisions": 8,
        "existing_questions": 12,
        "source_chunks": 423
    },
    
    # Results
    "results": {
        "questions_generated": 8,
        "llm_generated": 5,
        "derived": 3,
        "duplicates_found": 2,
        "questions_marked_obsolete": 1,
        "questions_preserved": 7,
        "total_pending_after": 14
    },
    
    # For debugging/improvement
    "llm_prompt_hash": "abc123",
    "model_used": "claude-sonnet-4-20250514"
}
```

---

## Generation Process

### Step 1: Gather Current State

```python
def gather_generation_context() -> dict:
    """Gather all context needed for question generation."""
    
    context = {
        # Roadmap
        "roadmap": load_current_roadmap_structured(),
        "roadmap_items": extract_roadmap_items(),
        
        # Assessments
        "arch_assessments": load_architecture_assessments(),
        "competitive_assessments": load_competitive_assessments(),
        "impact_assessments": load_impact_assessments(),
        
        # Decisions (to know what's resolved)
        "active_decisions": [d for d in load_decisions() if d["status"] == "active"],
        
        # Existing questions (to deduplicate)
        "existing_questions": load_questions(),
        "pending_questions": [q for q in load_questions() if q["status"] == "pending"],
        "answered_questions": [q for q in load_questions() if q["status"] == "answered"],
        
        # Graph for derived questions
        "graph": load_unified_graph(),
        
        # Source stats
        "chunks_by_lens": get_chunks_by_lens_count(),
    }
    
    return context
```

### Step 2: Derive Questions from Graph Analysis

```python
def derive_questions_from_graph(context: dict) -> list[dict]:
    """
    Automatically derive questions from graph analysis.
    These are flagged as 'derived' type.
    """
    
    derived_questions = []
    graph = context["graph"]
    roadmap_items = context["roadmap_items"]
    decisions = context["active_decisions"]
    
    # === PATTERN 1: Contradictions ===
    contradictions = find_contradictions(graph)
    for contradiction in contradictions:
        derived_questions.append({
            "question": f"Conflicting information about {contradiction['topic']}: "
                       f"'{contradiction['statement_a'][:50]}...' vs "
                       f"'{contradiction['statement_b'][:50]}...'. Which is correct?",
            "audience": "leadership",
            "category": "alignment",
            "priority": "high",
            "context": f"Found in {contradiction['source_a']} ({contradiction['lens_a']}) "
                      f"and {contradiction['source_b']} ({contradiction['lens_b']})",
            "generation": {
                "type": "derived",
                "source": "contradiction",
                "generated_at": datetime.now().isoformat(),
            },
            "derivation": {
                "pattern": "contradiction",
                "evidence": [
                    {
                        "source_id": contradiction["chunk_a_id"],
                        "source_name": contradiction["source_a"],
                        "lens": contradiction["lens_a"],
                        "content": contradiction["statement_a"],
                    },
                    {
                        "source_id": contradiction["chunk_b_id"],
                        "source_name": contradiction["source_b"],
                        "lens": contradiction["lens_b"],
                        "content": contradiction["statement_b"],
                    }
                ]
            }
        })
    
    # === PATTERN 2: Missing Engineering Coverage ===
    for item in roadmap_items:
        supporting_chunks = get_supporting_chunks(graph, item["id"])
        has_engineering = any(c.get("lens") == "engineering" for c in supporting_chunks)
        
        if not has_engineering and item.get("horizon") in ["now", "next"]:
            derived_questions.append({
                "question": f"Has engineering validated the feasibility of '{item['name']}'?",
                "audience": "engineering",
                "category": "feasibility",
                "priority": "high" if item.get("horizon") == "now" else "medium",
                "context": f"Roadmap item '{item['name']}' in {item.get('horizon')} horizon "
                          f"has no engineering source documents",
                "generation": {
                    "type": "derived",
                    "source": "missing_coverage",
                    "generated_at": datetime.now().isoformat(),
                },
                "derivation": {
                    "pattern": "missing_coverage",
                    "evidence": [{
                        "roadmap_item": item["name"],
                        "horizon": item.get("horizon"),
                        "lenses_present": list(set(c.get("lens") for c in supporting_chunks)),
                        "missing_lens": "engineering"
                    }]
                }
            })
    
    # === PATTERN 3: Dependency Conflicts ===
    for item in roadmap_items:
        dependencies = item.get("dependencies", [])
        item_horizon = item.get("horizon", "future")
        horizon_order = {"now": 0, "next": 1, "later": 2, "future": 3}
        
        for dep_name in dependencies:
            dep_item = next((i for i in roadmap_items if i["name"] == dep_name), None)
            if dep_item:
                dep_horizon = dep_item.get("horizon", "future")
                
                # Check if dependency is in a later horizon
                if horizon_order.get(dep_horizon, 3) > horizon_order.get(item_horizon, 3):
                    derived_questions.append({
                        "question": f"'{item['name']}' is in {item_horizon} but depends on "
                                   f"'{dep_name}' which is in {dep_horizon}. How will this work?",
                        "audience": "product",
                        "category": "dependency",
                        "priority": "high",
                        "context": f"Dependency timing conflict detected",
                        "generation": {
                            "type": "derived",
                            "source": "dependency_conflict",
                            "generated_at": datetime.now().isoformat(),
                        },
                        "derivation": {
                            "pattern": "dependency_conflict",
                            "evidence": [{
                                "item": item["name"],
                                "item_horizon": item_horizon,
                                "dependency": dep_name,
                                "dependency_horizon": dep_horizon
                            }]
                        }
                    })
    
    # === PATTERN 4: Unaddressed Gaps ===
    gaps = graph.node_indices.get("gap", {}).values() if graph else []
    for gap in gaps:
        gap_data = gap.__dict__ if hasattr(gap, '__dict__') else gap
        
        # Check if gap has been addressed by a decision
        addressed_by = gap_data.get("addressed_by_decision")
        if not addressed_by:
            severity = gap_data.get("severity", "medium")
            if severity in ["critical", "significant"]:
                derived_questions.append({
                    "question": f"How should we address the gap: '{gap_data.get('description', 'Unknown')[:80]}'?",
                    "audience": "leadership",
                    "category": "direction",
                    "priority": "critical" if severity == "critical" else "high",
                    "context": f"Gap identified by {gap_data.get('identified_by_assessment', 'assessment')}, "
                              f"severity: {severity}",
                    "generation": {
                        "type": "derived",
                        "source": "unaddressed_gap",
                        "generated_at": datetime.now().isoformat(),
                    },
                    "derivation": {
                        "pattern": "unaddressed_gap",
                        "evidence": [{
                            "gap_id": gap_data.get("id"),
                            "description": gap_data.get("description"),
                            "severity": severity,
                            "identified_by": gap_data.get("identified_by_assessment")
                        }]
                    }
                })
    
    # === PATTERN 5: Missing Owner ===
    for item in roadmap_items:
        if not item.get("owner") and item.get("horizon") in ["now", "next"]:
            derived_questions.append({
                "question": f"Who owns delivery of '{item['name']}'?",
                "audience": "leadership",
                "category": "ownership",
                "priority": "high" if item.get("horizon") == "now" else "medium",
                "context": f"Roadmap item in {item.get('horizon')} horizon has no assigned owner",
                "generation": {
                    "type": "derived",
                    "source": "missing_owner",
                    "generated_at": datetime.now().isoformat(),
                },
                "derivation": {
                    "pattern": "missing_owner",
                    "evidence": [{
                        "item": item["name"],
                        "horizon": item.get("horizon")
                    }]
                }
            })
    
    # === PATTERN 6: Stale Sources ===
    # Check for roadmap items with only old sources
    stale_threshold_days = 90
    for item in roadmap_items:
        supporting_chunks = get_supporting_chunks(graph, item["id"])
        
        if supporting_chunks:
            # Check if all sources are old
            all_stale = True
            for chunk in supporting_chunks:
                # This would need source file modification dates
                # For now, skip if we can't determine staleness
                chunk_date = chunk.get("ingested_at", chunk.get("created_at"))
                if chunk_date:
                    try:
                        chunk_dt = datetime.fromisoformat(chunk_date.replace("Z", "+00:00"))
                        if (datetime.now(chunk_dt.tzinfo) - chunk_dt).days < stale_threshold_days:
                            all_stale = False
                            break
                    except:
                        all_stale = False
                        break
                else:
                    all_stale = False
                    break
            
            if all_stale and item.get("horizon") in ["now", "next"]:
                derived_questions.append({
                    "question": f"Is the plan for '{item['name']}' still current? "
                               f"All source documents are over {stale_threshold_days} days old.",
                    "audience": "product",
                    "category": "validation",
                    "priority": "medium",
                    "context": f"Sources may be outdated",
                    "generation": {
                        "type": "derived",
                        "source": "stale_sources",
                        "generated_at": datetime.now().isoformat(),
                    },
                    "derivation": {
                        "pattern": "stale_sources",
                        "evidence": [{
                            "item": item["name"],
                            "source_count": len(supporting_chunks),
                            "threshold_days": stale_threshold_days
                        }]
                    }
                })
    
    return derived_questions


def find_contradictions(graph) -> list[dict]:
    """
    Find contradictory statements in the graph.
    
    Looks for chunks with high similarity but different lenses
    that contain conflicting information.
    """
    
    contradictions = []
    
    if not graph:
        return contradictions
    
    chunks = list(graph.node_indices.get("chunk", {}).values())
    
    # Compare your-voice chunks against team chunks
    your_voice_chunks = [c for c in chunks if getattr(c, 'lens', c.get('lens')) == 'your-voice']
    team_chunks = [c for c in chunks if getattr(c, 'lens', c.get('lens')) in ['team-structured', 'team-conversational', 'engineering']]
    
    # Look for topic overlap with different statements
    # This is a simplified check - could be more sophisticated
    
    contradiction_keywords = [
        ("q1", "q2", "q3", "q4"),  # Timeline conflicts
        ("will", "won't", "can", "cannot", "can't"),  # Capability conflicts
        ("priority", "deprioritize"),  # Priority conflicts
        ("before", "after"),  # Sequence conflicts
    ]
    
    for yv_chunk in your_voice_chunks[:20]:  # Limit for performance
        yv_content = getattr(yv_chunk, 'content', yv_chunk.get('content', '')).lower()
        yv_id = getattr(yv_chunk, 'id', yv_chunk.get('id', ''))
        yv_source = getattr(yv_chunk, 'source_name', yv_chunk.get('source_name', ''))
        
        for team_chunk in team_chunks[:50]:
            team_content = getattr(team_chunk, 'content', team_chunk.get('content', '')).lower()
            team_id = getattr(team_chunk, 'id', team_chunk.get('id', ''))
            team_source = getattr(team_chunk, 'source_name', team_chunk.get('source_name', ''))
            team_lens = getattr(team_chunk, 'lens', team_chunk.get('lens', ''))
            
            # Check for topic overlap (shared important terms)
            yv_terms = set(extract_key_terms_simple(yv_content))
            team_terms = set(extract_key_terms_simple(team_content))
            
            overlap = yv_terms & team_terms
            
            if len(overlap) >= 3:  # Significant topic overlap
                # Check for potential contradiction signals
                # This is heuristic - could use LLM for better detection
                
                for keyword_group in contradiction_keywords:
                    yv_has = any(kw in yv_content for kw in keyword_group)
                    team_has = any(kw in team_content for kw in keyword_group)
                    
                    if yv_has and team_has:
                        # Potential contradiction found
                        topic = ", ".join(list(overlap)[:3])
                        
                        contradictions.append({
                            "topic": topic,
                            "chunk_a_id": yv_id,
                            "source_a": yv_source,
                            "lens_a": "your-voice",
                            "statement_a": getattr(yv_chunk, 'content', yv_chunk.get('content', ''))[:150],
                            "chunk_b_id": team_id,
                            "source_b": team_source,
                            "lens_b": team_lens,
                            "statement_b": getattr(team_chunk, 'content', team_chunk.get('content', ''))[:150],
                        })
                        break  # One contradiction per chunk pair
    
    # Deduplicate similar contradictions
    seen_topics = set()
    unique_contradictions = []
    for c in contradictions:
        topic_key = c["topic"]
        if topic_key not in seen_topics:
            seen_topics.add(topic_key)
            unique_contradictions.append(c)
    
    return unique_contradictions[:10]  # Limit to top 10
```

### Step 3: Generate LLM Questions

```python
def generate_llm_questions(context: dict) -> list[dict]:
    """
    Use Claude to generate questions based on full context.
    """
    
    # Build context summary for prompt
    roadmap_summary = format_roadmap_for_prompt(context["roadmap"])
    
    arch_summary = ""
    for assessment in context["arch_assessments"]:
        arch_summary += f"\n- {assessment.get('summary', 'No summary')}"
        gaps = assessment.get("gaps_exposed", [])
        if gaps:
            arch_summary += f"\n  Gaps: {len(gaps)}"
    
    competitive_summary = ""
    for assessment in context["competitive_assessments"]:
        comp_name = assessment.get("competitor_development", {}).get("competitor", "Unknown")
        competitive_summary += f"\n- {comp_name}: {assessment.get('headline', 'No headline')}"
    
    decisions_summary = "\n".join([
        f"- {d['decision']}" for d in context["active_decisions"]
    ])
    
    answered_summary = "\n".join([
        f"- {q['question'][:80]}... → {q.get('answer', 'Answered')[:50]}..."
        for q in context["answered_questions"][:10]
    ])
    
    pending_summary = "\n".join([
        f"- [{q.get('priority', 'medium')}] {q['question'][:80]}..."
        for q in context["pending_questions"]
    ])
    
    prompt = f"""You are analyzing a product roadmap and related materials to identify questions that need answers.

## CURRENT ROADMAP
{roadmap_summary}

## ARCHITECTURE ASSESSMENT FINDINGS
{arch_summary if arch_summary else "No architecture assessment available"}

## COMPETITIVE INTELLIGENCE
{competitive_summary if competitive_summary else "No competitive assessments available"}

## DECISIONS ALREADY MADE
{decisions_summary if decisions_summary else "No decisions recorded yet"}

## QUESTIONS ALREADY ANSWERED
{answered_summary if answered_summary else "No questions answered yet"}

## QUESTIONS ALREADY PENDING
{pending_summary if pending_summary else "No pending questions"}

---

## YOUR TASK

Generate questions that need answers to move this roadmap forward. 

IMPORTANT:
- Do NOT generate questions that are already answered above
- Do NOT generate questions that are already pending above
- Do NOT generate questions that are resolved by decisions above
- Focus on NEW questions surfaced by the current state

For each question, specify:
- question: The question text
- audience: engineering | leadership | product
- category: feasibility | investment | direction | trade-off | alignment | timing | scope | dependency | ownership | validation
- priority: critical | high | medium | low
- context: Why this question arose (reference specific roadmap items, assessments, or sources)

Return as JSON array:
```json
[
    {{
        "question": "...",
        "audience": "...",
        "category": "...",
        "priority": "...",
        "context": "..."
    }}
]
```

Generate 5-15 questions depending on complexity. Quality over quantity.
"""

    response = call_claude_api(prompt, model="claude-sonnet-4-20250514")
    
    # Parse response
    questions = parse_json_from_response(response)
    
    # Add generation metadata
    for q in questions:
        q["generation"] = {
            "type": "llm",
            "source": "holistic_analysis",
            "generated_at": datetime.now().isoformat(),
        }
    
    return questions
```

### Step 4: Deduplicate Questions

```python
def deduplicate_questions(
    new_questions: list[dict],
    existing_questions: list[dict],
    similarity_threshold: float = 0.85
) -> tuple[list[dict], list[dict]]:
    """
    Deduplicate new questions against existing ones.
    
    Returns:
        - unique_new: Questions that are genuinely new
        - duplicates: Questions that match existing ones (with match info)
    """
    
    unique_new = []
    duplicates = []
    
    # Get embeddings for existing questions
    existing_embeddings = {}
    for eq in existing_questions:
        if eq.get("status") != "obsolete":
            eq_text = eq["question"]
            eq_embedding = get_embedding(eq_text)
            existing_embeddings[eq["id"]] = {
                "question": eq,
                "embedding": eq_embedding
            }
    
    for new_q in new_questions:
        new_embedding = get_embedding(new_q["question"])
        
        # Check against all existing
        is_duplicate = False
        best_match = None
        best_similarity = 0
        
        for eq_id, eq_data in existing_embeddings.items():
            similarity = cosine_similarity(new_embedding, eq_data["embedding"])
            
            if similarity > best_similarity:
                best_similarity = similarity
                best_match = eq_data["question"]
            
            if similarity >= similarity_threshold:
                is_duplicate = True
                break
        
        if is_duplicate:
            duplicates.append({
                "new_question": new_q,
                "matches": best_match,
                "similarity": best_similarity
            })
        else:
            # Add fingerprint for future deduplication
            new_q["deduplication"] = {
                "fingerprint": generate_question_fingerprint(new_q["question"]),
                "similar_questions": [],
                "supersedes": None,
                "superseded_by": None
            }
            
            # Track similar (but not duplicate) questions
            if best_match and best_similarity > 0.6:
                new_q["deduplication"]["similar_questions"].append(best_match["id"])
            
            unique_new.append(new_q)
    
    return unique_new, duplicates


def generate_question_fingerprint(question: str) -> str:
    """Generate a semantic fingerprint for deduplication."""
    
    # Extract key terms and normalize
    terms = extract_key_terms_simple(question.lower())
    terms.sort()
    
    return "_".join(terms[:5])
```

### Step 5: Mark Obsolete Questions

```python
def mark_obsolete_questions(
    existing_questions: list[dict],
    decisions: list[dict]
) -> list[dict]:
    """
    Mark questions as obsolete if they've been resolved by decisions.
    
    Returns list of questions that were marked obsolete.
    """
    
    newly_obsolete = []
    
    for question in existing_questions:
        if question.get("status") == "obsolete":
            continue
        
        if question.get("status") == "answered":
            continue
        
        # Check if any decision resolves this question
        question_embedding = get_embedding(question["question"])
        
        for decision in decisions:
            if decision.get("status") != "active":
                continue
            
            decision_text = f"{decision['decision']} {decision.get('rationale', '')}"
            decision_embedding = get_embedding(decision_text)
            
            similarity = cosine_similarity(question_embedding, decision_embedding)
            
            if similarity > 0.75:
                # Decision likely resolves this question
                question["status"] = "obsolete"
                question["lifecycle"] = question.get("lifecycle", {})
                question["lifecycle"]["obsoleted_at"] = datetime.now().isoformat()
                question["lifecycle"]["obsoleted_by"] = decision["id"]
                question["lifecycle"]["obsolete_reason"] = f"Resolved by decision: {decision['decision'][:50]}..."
                
                newly_obsolete.append(question)
                break
    
    return newly_obsolete
```

### Step 6: Main Generation Function

```python
def generate_questions_holistic() -> dict:
    """
    Main function to generate questions holistically.
    
    Returns generation results summary.
    """
    
    run_id = f"gen_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # Step 1: Gather context
    context = gather_generation_context()
    
    # Step 2: Derive questions from graph
    derived_questions = derive_questions_from_graph(context)
    
    # Step 3: Generate LLM questions
    llm_questions = generate_llm_questions(context)
    
    # Step 4: Combine all new questions
    all_new_questions = derived_questions + llm_questions
    
    # Step 5: Deduplicate against existing
    unique_questions, duplicates = deduplicate_questions(
        all_new_questions,
        context["existing_questions"]
    )
    
    # Step 6: Mark obsolete questions
    newly_obsolete = mark_obsolete_questions(
        context["existing_questions"],
        context["active_decisions"]
    )
    
    # Step 7: Assign IDs and finalize
    existing_questions = context["existing_questions"]
    
    for q in unique_questions:
        q["id"] = f"q_{datetime.now().strftime('%Y%m%d%H%M%S')}_{len(existing_questions)}"
        q["status"] = "pending"
        q["created_at"] = datetime.now().isoformat()
        q["generation"]["generation_run_id"] = run_id
        q["lifecycle"] = {
            "created_at": datetime.now().isoformat(),
            "refreshed_at": datetime.now().isoformat(),
            "times_refreshed": 1
        }
        existing_questions.append(q)
    
    # Step 8: Update refresh timestamp on preserved questions
    for eq in existing_questions:
        if eq.get("status") == "pending" and eq not in unique_questions:
            eq["lifecycle"] = eq.get("lifecycle", {})
            eq["lifecycle"]["refreshed_at"] = datetime.now().isoformat()
            eq["lifecycle"]["times_refreshed"] = eq["lifecycle"].get("times_refreshed", 0) + 1
    
    # Step 9: Save
    save_questions(existing_questions)
    
    # Step 10: Record generation run
    run_record = {
        "id": run_id,
        "timestamp": datetime.now().isoformat(),
        "triggered_by": "user",
        "context_analyzed": {
            "roadmap_items": len(context.get("roadmap_items", [])),
            "arch_assessments": len(context.get("arch_assessments", [])),
            "competitive_assessments": len(context.get("competitive_assessments", [])),
            "active_decisions": len(context.get("active_decisions", [])),
            "existing_questions": len(context.get("existing_questions", []))
        },
        "results": {
            "questions_generated": len(unique_questions),
            "llm_generated": len([q for q in unique_questions if q["generation"]["type"] == "llm"]),
            "derived": len([q for q in unique_questions if q["generation"]["type"] == "derived"]),
            "duplicates_found": len(duplicates),
            "questions_marked_obsolete": len(newly_obsolete),
            "total_pending_after": len([q for q in existing_questions if q["status"] == "pending"])
        }
    }
    
    save_generation_run(run_record)
    
    return run_record["results"]
```

---

## UI Integration

### Generate Questions Button (Questions Page)

```python
def render_generate_questions_section():
    """Render the generate questions UI section."""
    
    st.subheader("🔄 Generate Questions")
    
    # Show what will be analyzed
    context = gather_generation_context()
    
    with st.expander("What will be analyzed", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Roadmap & Assessments**")
            st.caption(f"• {len(context.get('roadmap_items', []))} roadmap items")
            st.caption(f"• {len(context.get('arch_assessments', []))} architecture assessments")
            st.caption(f"• {len(context.get('competitive_assessments', []))} competitive assessments")
        
        with col2:
            st.markdown("**Decisions & Questions**")
            st.caption(f"• {len(context.get('active_decisions', []))} active decisions")
            st.caption(f"• {len(context.get('answered_questions', []))} answered questions")
            st.caption(f"• {len(context.get('pending_questions', []))} pending questions")
    
    # Show last generation run
    last_run = get_last_generation_run()
    if last_run:
        st.caption(f"Last run: {last_run['timestamp'][:16]} — "
                  f"{last_run['results']['questions_generated']} generated, "
                  f"{last_run['results']['duplicates_found']} duplicates filtered")
    
    # Generate button
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if st.button("🔄 Generate Questions", type="primary", use_container_width=True):
            with st.spinner("Analyzing context and generating questions..."):
                results = generate_questions_holistic()
            
            st.success(f"✅ Generation complete!")
            
            # Show results
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("New Questions", results["questions_generated"])
            col2.metric("LLM Generated", results["llm_generated"])
            col3.metric("Derived", results["derived"])
            col4.metric("Marked Obsolete", results["questions_marked_obsolete"])
            
            st.caption(f"Total pending: {results['total_pending_after']}")
            
            # Invalidate source cache
            invalidate_source_cache()
            
            st.rerun()
    
    with col2:
        st.caption("Generates new questions based on current roadmap, assessments, and decisions")
```

### Question List with Type Badges

```python
def render_question_card_with_generation_type(q: dict):
    """Render question card showing generation type."""
    
    generation = q.get("generation", {})
    gen_type = generation.get("type", "unknown")
    gen_source = generation.get("source", "unknown")
    
    # Type badge
    if gen_type == "llm":
        type_badge = "🤖 LLM"
        type_color = "blue"
    elif gen_type == "derived":
        type_badge = f"🔍 Derived ({gen_source})"
        type_color = "orange"
    else:
        type_badge = "❓ Unknown"
        type_color = "gray"
    
    priority_icons = {
        "critical": "🔴",
        "high": "🟠",
        "medium": "🟡",
        "low": "🟢"
    }
    priority_icon = priority_icons.get(q.get("priority", "medium"), "⚪")
    
    with st.container(border=True):
        # Header row
        col1, col2, col3 = st.columns([4, 2, 1])
        
        with col1:
            st.markdown(f"{priority_icon} **{q['question']}**")
        
        with col2:
            # Generation type badge
            if gen_type == "derived":
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
        
        # Meta info
        st.caption(f"{q.get('audience', 'unknown')} | {q.get('category', 'unknown')} | "
                  f"Created: {q.get('created_at', 'unknown')[:10]}")
        
        # For derived questions, show evidence
        if gen_type == "derived":
            derivation = q.get("derivation", {})
            evidence = derivation.get("evidence", [])
            
            if evidence:
                with st.expander(f"📊 Derivation Evidence ({len(evidence)} items)"):
                    for ev in evidence:
                        if "source_name" in ev:
                            st.markdown(f"**{ev.get('source_name')}** ({ev.get('lens', 'unknown')})")
                            st.caption(ev.get("content", "")[:200])
                        else:
                            st.json(ev)
        
        # Expandable details
        with st.expander("View Details"):
            if q.get("context"):
                st.info(f"**Context:** {q['context']}")
            
            st.divider()
            render_question_source_references(q)
            st.divider()
            render_question_validation(q)
```

### Filter by Generation Type

```python
def render_question_filters():
    """Render question list filters including generation type."""
    
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
        type_filter = st.selectbox(
            "Generation Type",
            ["all", "llm", "derived"],
            index=0
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

## Remove Inline Generation

### Update Synthesis

Remove question generation from synthesis prompt. The synthesis should only output the roadmap.

### Update Architecture Assessment

Remove question generation from architecture assessment. It should only output the assessment findings.

### Update Competitive Assessment

Remove question generation from competitive assessment. It should only output the analyst assessment.

**Questions are now ONLY generated via the "Generate Questions" button.**

---

## Testing Checklist

- [ ] Generate Questions button appears on Questions page
- [ ] Context summary shows what will be analyzed
- [ ] LLM questions are generated and tagged as "llm"
- [ ] Derived questions are generated for contradictions
- [ ] Derived questions are generated for missing coverage
- [ ] Derived questions are generated for dependency conflicts
- [ ] Derived questions are generated for unaddressed gaps
- [ ] Duplicates are filtered (not added twice)
- [ ] Obsolete questions are marked (resolved by decisions)
- [ ] Generation results summary displays correctly
- [ ] Questions show generation type badge
- [ ] Derived questions show evidence
- [ ] Filter by generation type works
- [ ] Validation feedback preserved across regeneration
- [ ] Synthesis no longer generates questions inline
- [ ] Assessments no longer generate questions inline

---

## Estimated Time

- Gather context function: 15 min
- Derive questions (all patterns): 45 min
- LLM question generation: 20 min
- Deduplication logic: 20 min
- Obsolescence detection: 15 min
- Main generation function: 15 min
- UI integration: 30 min
- Remove inline generation: 15 min
- Testing: 30 min

**Total: ~3.5 hours**
