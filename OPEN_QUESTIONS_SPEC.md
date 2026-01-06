# Open Questions & Decision Log Specification

## Overview

This feature creates a feedback loop for roadmap development:

1. **Generate Questions** — After synthesis, identify open questions for Engineering, Leadership, and Product
2. **Collect Answers** — You gather responses from stakeholders
3. **Log Decisions** — Answers become timestamped decisions
4. **Re-synthesize** — Decision log informs subsequent roadmap generation

This transforms the roadmap from a static document into a living decision-making system.

---

## Data Model

### Question

```python
@dataclass
class Question:
    id: str                          # q_eng_001, q_lead_002, etc.
    question: str                    # The actual question
    audience: str                    # engineering, leadership, product
    category: str                    # feasibility, investment, direction, trade-off, alignment
    context: str                     # Why this question matters
    source_chunks: list[str]         # Chunk IDs that prompted this question
    related_roadmap_items: list[str] # Roadmap items affected by the answer
    priority: str                    # critical, high, medium, low
    status: str                      # pending, answered, deferred, obsolete
    created_at: str                  # ISO timestamp
    created_from_synthesis: str      # ID of synthesis run that generated this
```

### Answer

```python
@dataclass
class Answer:
    id: str                          # ans_001
    question_id: str                 # Links to question
    answer: str                      # The response
    answered_by: str                 # Person who provided the answer
    answered_at: str                 # ISO timestamp
    confidence: str                  # high, medium, low
    follow_up_needed: bool           # Does this raise more questions?
    notes: str                       # Additional context
```

### Decision

```python
@dataclass
class Decision:
    id: str                          # dec_001
    question_id: str                 # Original question
    answer_id: str                   # The answer that resolved it
    decision: str                    # The actual decision made
    rationale: str                   # Why this decision
    implications: list[str]          # What this affects
    owner: str                       # Who owns execution
    review_date: str                 # When to revisit (optional)
    status: str                      # active, superseded, revisiting
    created_at: str                  # ISO timestamp
```

---

## Question Categories

### By Audience

**Engineering**
- Technical feasibility
- Architecture decisions
- Capacity and timeline estimates
- Dependency clarifications
- Technical debt trade-offs
- Platform vs. product-specific choices

**Leadership**
- Investment prioritization
- Strategic direction choices
- Resource allocation
- Risk tolerance
- Cross-initiative trade-offs
- Timeline expectations

**Product**
- Scope decisions
- Customer priority trade-offs
- Feature sequencing
- Cross-team alignment
- MVP definition
- Success criteria

### By Category

| Category | Description | Example |
|----------|-------------|---------|
| **feasibility** | Can we do this? | "Can Catalog API be migrated in Q2 with current capacity?" |
| **investment** | Should we spend resources here? | "Is the churn agent worth 3 engineers for 2 quarters?" |
| **direction** | Which way should we go? | "Should we build native bundles or integrate partner solution?" |
| **trade-off** | What do we sacrifice? | "If we prioritize Catalog, what slips in Acquisition?" |
| **alignment** | Are we on the same page? | "Does the CPQ team agree Catalog is the blocker?" |
| **timing** | When should this happen? | "Is Q2 or Q3 the right target for GA?" |
| **scope** | What's in/out? | "Does MVP include multi-currency or is that v2?" |
| **dependency** | What blocks what? | "Is the billing migration actually required for this?" |

---

## Question Generation Prompt

Add to synthesis or as a separate step:

```markdown
## Open Questions Generation

After synthesizing the roadmap, identify open questions that need stakeholder input.

### What to Look For

**Tensions & Conflicts**
- Where sources disagree and hierarchy doesn't clearly resolve it
- Where conversational concerns contradict structured plans
- Where engineering feasibility is uncertain

**Missing Information**
- Decisions referenced but not documented
- Timelines stated without confidence
- Dependencies assumed but not confirmed

**Strategic Ambiguity**
- Multiple valid paths forward
- Investment levels not specified
- Priority conflicts between teams

**Risk Areas**
- Items flagged as risky without mitigation plans
- Dependencies on external factors
- Capacity concerns without resolution

### Question Quality Criteria

Good questions are:
- **Specific** — Not "What's the plan?" but "Is Q2 realistic for Catalog given API migration dependency?"
- **Actionable** — The answer leads to a decision
- **Audience-appropriate** — Engineering questions are technical, Leadership questions are strategic
- **Contextual** — Include why the question matters

Bad questions:
- Vague or open-ended without focus
- Already answered in the sources
- Asking for information rather than decisions
- Not tied to roadmap outcomes

### Output Format

For each question, provide:

```json
{
  "id": "q_[audience]_[number]",
  "question": "Clear, specific question",
  "audience": "engineering|leadership|product",
  "category": "feasibility|investment|direction|trade-off|alignment|timing|scope|dependency",
  "context": "Why this question matters for the roadmap",
  "source_tensions": "What in the sources prompted this question",
  "related_items": ["Roadmap items affected by the answer"],
  "priority": "critical|high|medium|low",
  "suggested_deadline": "When answer is needed by"
}
```

### Priority Guidelines

- **Critical**: Blocks roadmap finalization or major commitment
- **High**: Affects Q1-Q2 planning significantly  
- **Medium**: Important for Later horizon or cross-team alignment
- **Low**: Good to know but roadmap can proceed without it

Generate 3-7 questions per audience, prioritized by impact on roadmap decisions.
```

---

## Storage

### File Structure

```
data/
├── questions/
│   ├── questions.json          # All questions
│   ├── answers.json            # All answers
│   └── decisions.json          # Decision log
└── synthesis_runs/
    ├── run_2025-01-15_143000/
    │   ├── roadmap.md
    │   ├── questions_generated.json
    │   └── decisions_applied.json
    └── run_2025-01-16_091500/
        └── ...
```

### questions.json

```json
{
  "questions": [
    {
      "id": "q_eng_001",
      "question": "Can the Catalog API migration be completed in Q2 with current team capacity, or do we need contractor support?",
      "audience": "engineering",
      "category": "feasibility",
      "context": "Multiple roadmap items depend on Catalog. Team-conversational sources suggest Q2 is aggressive, but team-structured shows Q2 commitment.",
      "source_chunks": ["chunk_123", "chunk_456"],
      "related_roadmap_items": ["Catalog GA", "Acquisition Integration", "Experience Builder Launch"],
      "priority": "critical",
      "status": "pending",
      "created_at": "2025-01-15T14:30:00Z",
      "created_from_synthesis": "run_2025-01-15_143000"
    }
  ],
  "metadata": {
    "last_updated": "2025-01-15T14:30:00Z",
    "total_pending": 12,
    "total_answered": 5,
    "total_deferred": 2
  }
}
```

### decisions.json

```json
{
  "decisions": [
    {
      "id": "dec_001",
      "question_id": "q_eng_001",
      "answer_id": "ans_001",
      "decision": "Catalog API migration will target Q3. Q2 will focus on preparation and contractor onboarding.",
      "rationale": "Engineering confirmed Q2 is not feasible without compromising quality. Q3 gives buffer for proper testing.",
      "implications": [
        "Acquisition Integration moves to Q3",
        "Experience Builder MVP can proceed with mock Catalog data",
        "Need to set expectations with customers expecting Q2"
      ],
      "owner": "Sarah Chen",
      "review_date": "2025-03-01",
      "status": "active",
      "created_at": "2025-01-16T10:00:00Z"
    }
  ],
  "metadata": {
    "last_updated": "2025-01-16T10:00:00Z",
    "total_decisions": 8,
    "active_decisions": 7,
    "superseded_decisions": 1
  }
}
```

---

## CLI Commands

### Generate Questions

```python
@app.command()
def questions_generate(
    from_latest: bool = typer.Option(True, help="Generate from latest synthesis"),
    synthesis_id: str = typer.Option(None, help="Specific synthesis run ID"),
    output: Path = typer.Option(None, help="Output file path")
):
    """Generate open questions from synthesis results."""
    
    # Load synthesis context
    if from_latest:
        synthesis = load_latest_synthesis()
    else:
        synthesis = load_synthesis(synthesis_id)
    
    # Load existing questions to avoid duplicates
    existing = load_questions()
    
    # Generate questions via Claude
    prompt = build_questions_prompt(synthesis, existing)
    
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4000,
        messages=[{"role": "user", "content": prompt}]
    )
    
    # Parse and save questions
    new_questions = parse_questions_response(response)
    
    # Add to questions store
    for q in new_questions:
        q["status"] = "pending"
        q["created_at"] = datetime.now().isoformat()
        q["created_from_synthesis"] = synthesis["id"]
    
    save_questions(existing + new_questions)
    
    # Display
    console.print(f"\n[green]Generated {len(new_questions)} questions[/green]")
    
    for audience in ["engineering", "leadership", "product"]:
        audience_qs = [q for q in new_questions if q["audience"] == audience]
        if audience_qs:
            console.print(f"\n[bold]{audience.upper()}[/bold]")
            for q in audience_qs:
                priority_color = {"critical": "red", "high": "yellow", "medium": "white", "low": "dim"}.get(q["priority"], "white")
                console.print(f"  [{priority_color}][{q['priority']}][/{priority_color}] {q['id']}: {q['question']}")
```

### List Questions

```python
@app.command()
def questions_list(
    audience: str = typer.Option(None, help="Filter by audience"),
    status: str = typer.Option("pending", help="Filter by status"),
    priority: str = typer.Option(None, help="Filter by priority"),
    show_all: bool = typer.Option(False, help="Show all questions regardless of status")
):
    """List open questions."""
    
    questions = load_questions()
    
    # Apply filters
    if not show_all:
        questions = [q for q in questions if q["status"] == status]
    if audience:
        questions = [q for q in questions if q["audience"] == audience]
    if priority:
        questions = [q for q in questions if q["priority"] == priority]
    
    # Group by audience
    by_audience = {}
    for q in questions:
        aud = q["audience"]
        if aud not in by_audience:
            by_audience[aud] = []
        by_audience[aud].append(q)
    
    # Display
    for aud in ["engineering", "leadership", "product"]:
        if aud not in by_audience:
            continue
        
        console.print(f"\n[bold]{aud.upper()}[/bold] ({len(by_audience[aud])} questions)")
        
        for q in sorted(by_audience[aud], key=lambda x: {"critical": 0, "high": 1, "medium": 2, "low": 3}.get(x["priority"], 4)):
            priority_color = {"critical": "red", "high": "yellow", "medium": "white", "low": "dim"}.get(q["priority"], "white")
            status_icon = {"pending": "⏳", "answered": "✅", "deferred": "⏸️", "obsolete": "❌"}.get(q["status"], "?")
            
            console.print(f"\n  {status_icon} [{priority_color}]{q['id']}[/{priority_color}]")
            console.print(f"     {q['question']}")
            console.print(f"     [dim]Category: {q['category']} | Priority: {q['priority']}[/dim]")
            if q.get("context"):
                console.print(f"     [dim]Context: {q['context'][:100]}...[/dim]")
```

### Answer Question

```python
@app.command()
def questions_answer(
    question_id: str = typer.Argument(..., help="Question ID to answer"),
    answer: str = typer.Option(None, help="The answer (or will prompt interactively)"),
    answered_by: str = typer.Option(None, help="Who provided the answer"),
    confidence: str = typer.Option("medium", help="Confidence level: high, medium, low"),
    create_decision: bool = typer.Option(True, help="Create decision entry from answer")
):
    """Submit an answer to an open question."""
    
    questions = load_questions()
    question = next((q for q in questions if q["id"] == question_id), None)
    
    if not question:
        console.print(f"[red]Question {question_id} not found[/red]")
        raise typer.Exit(1)
    
    # Display question
    console.print(f"\n[bold]Question:[/bold] {question['question']}")
    console.print(f"[dim]Context: {question.get('context', 'None')}[/dim]")
    console.print(f"[dim]Category: {question['category']} | Audience: {question['audience']}[/dim]")
    
    # Get answer interactively if not provided
    if not answer:
        console.print("\n[bold]Enter your answer:[/bold]")
        answer = typer.prompt("Answer")
    
    if not answered_by:
        answered_by = typer.prompt("Answered by")
    
    # Create answer record
    answer_record = {
        "id": f"ans_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "question_id": question_id,
        "answer": answer,
        "answered_by": answered_by,
        "answered_at": datetime.now().isoformat(),
        "confidence": confidence,
        "follow_up_needed": False,
        "notes": ""
    }
    
    # Save answer
    answers = load_answers()
    answers.append(answer_record)
    save_answers(answers)
    
    # Update question status
    question["status"] = "answered"
    save_questions(questions)
    
    console.print(f"\n[green]Answer recorded: {answer_record['id']}[/green]")
    
    # Create decision if requested
    if create_decision:
        console.print("\n[bold]Create decision record:[/bold]")
        
        decision_text = typer.prompt("Decision (or press Enter to use answer)", default=answer)
        rationale = typer.prompt("Rationale", default="")
        implications_str = typer.prompt("Implications (comma-separated)", default="")
        owner = typer.prompt("Owner", default=answered_by)
        
        implications = [i.strip() for i in implications_str.split(",") if i.strip()]
        
        decision_record = {
            "id": f"dec_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "question_id": question_id,
            "answer_id": answer_record["id"],
            "decision": decision_text,
            "rationale": rationale,
            "implications": implications,
            "owner": owner,
            "review_date": None,
            "status": "active",
            "created_at": datetime.now().isoformat()
        }
        
        decisions = load_decisions()
        decisions.append(decision_record)
        save_decisions(decisions)
        
        console.print(f"[green]Decision recorded: {decision_record['id']}[/green]")
```

### View Decision Log

```python
@app.command()
def decisions_log(
    show_all: bool = typer.Option(False, help="Include superseded decisions"),
    since: str = typer.Option(None, help="Show decisions since date (YYYY-MM-DD)"),
    export: Path = typer.Option(None, help="Export to markdown file")
):
    """View the decision log."""
    
    decisions = load_decisions()
    
    # Filter
    if not show_all:
        decisions = [d for d in decisions if d["status"] == "active"]
    
    if since:
        since_date = datetime.fromisoformat(since)
        decisions = [d for d in decisions if datetime.fromisoformat(d["created_at"]) >= since_date]
    
    # Sort by date descending
    decisions = sorted(decisions, key=lambda x: x["created_at"], reverse=True)
    
    # Display
    console.print(f"\n[bold]Decision Log[/bold] ({len(decisions)} decisions)\n")
    
    for dec in decisions:
        status_icon = {"active": "✅", "superseded": "🔄", "revisiting": "🔍"}.get(dec["status"], "?")
        
        console.print(f"{status_icon} [bold]{dec['id']}[/bold] — {dec['created_at'][:10]}")
        console.print(f"   [cyan]Decision:[/cyan] {dec['decision']}")
        if dec.get("rationale"):
            console.print(f"   [dim]Rationale: {dec['rationale']}[/dim]")
        if dec.get("implications"):
            console.print(f"   [yellow]Implications:[/yellow]")
            for imp in dec["implications"]:
                console.print(f"      • {imp}")
        console.print(f"   [dim]Owner: {dec.get('owner', 'Unassigned')}[/dim]")
        console.print()
    
    # Export if requested
    if export:
        md_content = format_decisions_as_markdown(decisions)
        export.write_text(md_content)
        console.print(f"[green]Exported to {export}[/green]")
```

---

## Streamlit Integration

### New Page: Open Questions

```python
elif page == "❓ Open Questions":
    st.title("Open Questions")
    
    questions = load_questions()
    decisions = load_decisions()
    
    # Tabs for different views
    tab1, tab2, tab3 = st.tabs(["📋 Pending Questions", "✅ Answer Question", "📜 Decision Log"])
    
    with tab1:
        st.subheader("Pending Questions")
        
        # Filters
        col1, col2, col3 = st.columns(3)
        with col1:
            audience_filter = st.selectbox("Audience", ["All", "engineering", "leadership", "product"])
        with col2:
            priority_filter = st.selectbox("Priority", ["All", "critical", "high", "medium", "low"])
        with col3:
            category_filter = st.selectbox("Category", ["All", "feasibility", "investment", "direction", "trade-off", "alignment", "timing", "scope", "dependency"])
        
        # Filter questions
        pending = [q for q in questions if q["status"] == "pending"]
        
        if audience_filter != "All":
            pending = [q for q in pending if q["audience"] == audience_filter]
        if priority_filter != "All":
            pending = [q for q in pending if q["priority"] == priority_filter]
        if category_filter != "All":
            pending = [q for q in pending if q["category"] == category_filter]
        
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Pending", len([q for q in questions if q["status"] == "pending"]))
        col2.metric("Critical", len([q for q in pending if q["priority"] == "critical"]))
        col3.metric("Answered", len([q for q in questions if q["status"] == "answered"]))
        col4.metric("Decisions Made", len(decisions))
        
        # Display questions by audience
        for audience in ["engineering", "leadership", "product"]:
            audience_qs = [q for q in pending if q["audience"] == audience]
            if not audience_qs:
                continue
            
            st.markdown(f"### {audience.title()} ({len(audience_qs)})")
            
            for q in sorted(audience_qs, key=lambda x: {"critical": 0, "high": 1, "medium": 2, "low": 3}.get(x["priority"], 4)):
                priority_color = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "⚪"}.get(q["priority"], "⚪")
                
                with st.expander(f"{priority_color} {q['question'][:80]}..."):
                    st.write(f"**Question:** {q['question']}")
                    st.write(f"**Category:** {q['category']}")
                    st.write(f"**Priority:** {q['priority']}")
                    st.write(f"**Context:** {q.get('context', 'None provided')}")
                    
                    if q.get("related_roadmap_items"):
                        st.write(f"**Affects:** {', '.join(q['related_roadmap_items'])}")
                    
                    st.write(f"**Created:** {q['created_at'][:10]}")
                    
                    # Quick actions
                    col1, col2, col3 = st.columns(3)
                    if col1.button("Answer", key=f"ans_{q['id']}"):
                        st.session_state.answering_question = q['id']
                        st.experimental_rerun()
                    if col2.button("Defer", key=f"def_{q['id']}"):
                        update_question_status(q['id'], "deferred")
                        st.experimental_rerun()
                    if col3.button("Mark Obsolete", key=f"obs_{q['id']}"):
                        update_question_status(q['id'], "obsolete")
                        st.experimental_rerun()
        
        # Generate new questions button
        st.markdown("---")
        if st.button("🔄 Generate New Questions from Latest Synthesis"):
            with st.spinner("Generating questions..."):
                new_qs = generate_questions_from_synthesis()
                st.success(f"Generated {len(new_qs)} new questions")
                st.experimental_rerun()
    
    with tab2:
        st.subheader("Answer Question")
        
        # Select question to answer
        pending = [q for q in questions if q["status"] == "pending"]
        
        if not pending:
            st.info("No pending questions. Generate questions from synthesis first.")
        else:
            question_options = {f"{q['id']}: {q['question'][:60]}...": q['id'] for q in pending}
            selected = st.selectbox("Select Question", list(question_options.keys()))
            
            if selected:
                q_id = question_options[selected]
                question = next(q for q in pending if q["id"] == q_id)
                
                st.markdown(f"**Question:** {question['question']}")
                st.markdown(f"**Context:** {question.get('context', 'None')}")
                st.markdown(f"**Audience:** {question['audience']} | **Category:** {question['category']}")
                
                st.markdown("---")
                
                # Answer form
                answer_text = st.text_area("Your Answer", height=150)
                answered_by = st.text_input("Answered By")
                confidence = st.select_slider("Confidence", options=["low", "medium", "high"], value="medium")
                
                create_decision = st.checkbox("Create Decision Record", value=True)
                
                if create_decision:
                    st.markdown("#### Decision Details")
                    decision_text = st.text_area("Decision (leave blank to use answer)", height=100)
                    rationale = st.text_input("Rationale")
                    implications = st.text_input("Implications (comma-separated)")
                    owner = st.text_input("Owner", value=answered_by)
                
                if st.button("Submit Answer", type="primary"):
                    if not answer_text or not answered_by:
                        st.error("Please provide answer and your name")
                    else:
                        # Save answer
                        answer_record = save_answer(
                            question_id=q_id,
                            answer=answer_text,
                            answered_by=answered_by,
                            confidence=confidence
                        )
                        
                        # Save decision if requested
                        if create_decision:
                            save_decision(
                                question_id=q_id,
                                answer_id=answer_record["id"],
                                decision=decision_text or answer_text,
                                rationale=rationale,
                                implications=[i.strip() for i in implications.split(",") if i.strip()],
                                owner=owner or answered_by
                            )
                        
                        # Update question status
                        update_question_status(q_id, "answered")
                        
                        st.success("Answer recorded!")
                        st.experimental_rerun()
    
    with tab3:
        st.subheader("Decision Log")
        
        # Filters
        col1, col2 = st.columns(2)
        with col1:
            show_superseded = st.checkbox("Show superseded decisions")
        with col2:
            date_filter = st.date_input("Since", value=None)
        
        # Filter decisions
        filtered_decisions = decisions
        if not show_superseded:
            filtered_decisions = [d for d in filtered_decisions if d["status"] == "active"]
        if date_filter:
            filtered_decisions = [d for d in filtered_decisions if d["created_at"][:10] >= str(date_filter)]
        
        # Sort by date
        filtered_decisions = sorted(filtered_decisions, key=lambda x: x["created_at"], reverse=True)
        
        # Display
        for dec in filtered_decisions:
            status_icon = {"active": "✅", "superseded": "🔄", "revisiting": "🔍"}.get(dec["status"], "?")
            
            with st.expander(f"{status_icon} {dec['decision'][:60]}... ({dec['created_at'][:10]})"):
                st.write(f"**Decision:** {dec['decision']}")
                st.write(f"**Rationale:** {dec.get('rationale', 'None provided')}")
                
                if dec.get("implications"):
                    st.write("**Implications:**")
                    for imp in dec["implications"]:
                        st.write(f"  • {imp}")
                
                st.write(f"**Owner:** {dec.get('owner', 'Unassigned')}")
                st.write(f"**Status:** {dec['status']}")
                
                # Link to original question
                question = next((q for q in questions if q["id"] == dec["question_id"]), None)
                if question:
                    st.write(f"**Original Question:** {question['question']}")
                
                # Actions
                col1, col2 = st.columns(2)
                if dec["status"] == "active":
                    if col1.button("Mark for Review", key=f"rev_{dec['id']}"):
                        update_decision_status(dec["id"], "revisiting")
                        st.experimental_rerun()
                    if col2.button("Supersede", key=f"sup_{dec['id']}"):
                        update_decision_status(dec["id"], "superseded")
                        st.experimental_rerun()
        
        # Export button
        st.markdown("---")
        if st.button("📥 Export Decision Log"):
            md_content = format_decisions_as_markdown(filtered_decisions)
            st.download_button(
                "Download Markdown",
                md_content,
                file_name=f"decision_log_{datetime.now().strftime('%Y%m%d')}.md",
                mime="text/markdown"
            )
```

---

## Integration with Synthesis

### Decision Log in Synthesis Context

When generating a roadmap, include active decisions:

```python
def format_decisions_for_synthesis(decisions: list[dict]) -> str:
    """Format decision log for inclusion in synthesis context."""
    
    active = [d for d in decisions if d["status"] == "active"]
    
    if not active:
        return "No previous decisions recorded."
    
    output = ["## Decision Log", ""]
    output.append("The following decisions have been made and should be reflected in the roadmap:")
    output.append("")
    
    for dec in sorted(active, key=lambda x: x["created_at"], reverse=True):
        output.append(f"### {dec['id']} ({dec['created_at'][:10]})")
        output.append(f"**Decision:** {dec['decision']}")
        if dec.get("rationale"):
            output.append(f"**Rationale:** {dec['rationale']}")
        if dec.get("implications"):
            output.append("**Implications:**")
            for imp in dec["implications"]:
                output.append(f"  - {imp}")
        output.append(f"**Owner:** {dec.get('owner', 'Unassigned')}")
        output.append("")
    
    return "\n".join(output)
```

### Updated Synthesis Flow

```python
def generate_roadmap():
    """Generate roadmap with decision log integration."""
    
    # Load decisions
    decisions = load_decisions()
    decision_context = format_decisions_for_synthesis(decisions)
    
    # Load source chunks (existing logic)
    chunks = retrieve_for_synthesis()
    
    # Format context
    context = format_context_for_synthesis(chunks)
    
    # Add decision log
    context += f"\n\n# PREVIOUS DECISIONS\n\n{decision_context}"
    
    # Add instruction to respect decisions
    context += """

## Decision Log Integration

The decisions above have been made by stakeholders. When generating the roadmap:

1. **Respect active decisions** — These are resolved questions, incorporate their implications
2. **Note decision impacts** — Show how decisions affected roadmap items
3. **Flag if decisions conflict** — If new information contradicts a decision, surface this
4. **Don't re-open decided questions** — Unless new evidence makes them obsolete
"""
    
    # Generate roadmap
    # ... existing synthesis logic
```

### Add Open Questions to Synthesis Output

Update synthesis prompt to generate questions:

```markdown
### 11. Open Questions

After synthesizing the roadmap, identify questions that need stakeholder input.

**For Engineering:**
[3-5 questions about feasibility, capacity, architecture, dependencies]

**For Leadership:**
[3-5 questions about investment, priorities, strategic direction]

**For Product:**
[3-5 questions about scope, sequencing, customer priorities]

Each question should include:
- The specific question
- Category (feasibility/investment/direction/trade-off/alignment/timing/scope/dependency)
- Priority (critical/high/medium/low)
- Context (why this matters)
- Related roadmap items affected
```

---

## Implementation Order

1. **Data model and storage** (20 min)
   - Create Question, Answer, Decision dataclasses
   - Implement JSON storage functions

2. **Question generation prompt** (15 min)
   - Add to synthesis prompt
   - Create standalone generation function

3. **CLI commands** (30 min)
   - questions_generate
   - questions_list
   - questions_answer
   - decisions_log

4. **Streamlit pages** (45 min)
   - Pending questions view
   - Answer submission form
   - Decision log viewer

5. **Synthesis integration** (20 min)
   - Decision log in context
   - Questions in output

6. **Testing** (15 min)
   - Generate questions
   - Answer and create decisions
   - Verify decisions appear in next synthesis

---

## Success Criteria

- [ ] Questions generated after synthesis
- [ ] Questions categorized by audience and priority
- [ ] Answers can be submitted via CLI or Streamlit
- [ ] Decisions created from answers
- [ ] Decision log viewable and exportable
- [ ] Decisions included in subsequent synthesis
- [ ] Questions don't repeat resolved decisions
