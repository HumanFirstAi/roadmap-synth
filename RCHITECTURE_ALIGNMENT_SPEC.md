# Architecture Alignment Analysis Specification

## Overview

This feature creates a direct mapping between functional roadmap items and technical architecture/design documents to:

1. **Assess alignment** — Does the architecture support what product wants to build?
2. **Surface gaps** — Where are architectural changes needed?
3. **Identify risks** — What technical risks exist for each roadmap item?
4. **Generate questions** — Engineering-led questions that flow into the Open Questions system

This ensures functional product requirements are closely aligned with architectural and technical decisions.

---

## Key Difference: Full Document Context

Unlike normal retrieval (which uses chunks), this feature loads **full architecture documents** as context. This is critical because:

- Architecture docs have interconnected concepts
- Chunking loses system-wide relationships
- Technical decisions span multiple sections
- Dependencies are often documented across a document

### Document Selection

```
materials/engineering/
├── architecture/           # Full docs loaded for alignment analysis
│   ├── system-architecture.md
│   ├── data-model.md
│   ├── api-design.md
│   └── integration-patterns.md
├── tech-specs/            # Full docs loaded for alignment analysis
│   ├── catalog-service.md
│   ├── pricing-engine.md
│   └── event-system.md
└── feasibility/           # May use chunks (shorter docs)
    └── ...
```

---

## Data Model

### ArchitectureDocument

```python
@dataclass
class ArchitectureDocument:
    id: str                      # doc_arch_001
    path: str                    # materials/engineering/architecture/system-architecture.md
    title: str                   # System Architecture Overview
    doc_type: str                # architecture, tech-spec, design-doc
    content: str                 # Full document content
    token_count: int             # For context window management
    key_components: list[str]    # Extracted: ["Catalog Service", "Pricing Engine", "Event Bus"]
    last_updated: str            # File modification date
    loaded_at: str               # When loaded for analysis
```

### AlignmentAssessment

```python
@dataclass
class AlignmentAssessment:
    id: str                              # align_001
    roadmap_item: str                    # "Catalog GA"
    roadmap_item_description: str        # Full description from roadmap
    horizon: str                         # now, next, later, future
    
    # Alignment analysis
    architecture_supports: str           # full, partial, no, unknown
    confidence: str                      # high, medium, low
    
    # Details
    supporting_components: list[str]     # Components that enable this
    required_changes: list[dict]         # Changes needed
    technical_risks: list[dict]          # Risks identified
    dependencies: list[dict]             # Technical dependencies
    
    # Sequencing
    prerequisite_work: list[str]         # What must happen first (technical)
    enables: list[str]                   # What this unblocks (technical)
    
    # Questions generated
    questions: list[dict]                # Engineering questions for this item
    
    # Metadata
    analyzed_at: str                     # Timestamp
    architecture_docs_used: list[str]    # Which docs informed this
```

### RequiredChange

```python
@dataclass
class RequiredChange:
    component: str               # "Catalog Service"
    change_type: str            # new, modify, deprecate, migrate
    description: str            # What needs to change
    effort_estimate: str        # S, M, L, XL
    risk_level: str             # low, medium, high
    blocking: bool              # Does this block the roadmap item?
```

### TechnicalRisk

```python
@dataclass
class TechnicalRisk:
    risk: str                   # Description of the risk
    severity: str               # critical, high, medium, low
    likelihood: str             # high, medium, low
    mitigation: str             # Possible mitigation
    owner: str                  # Who should address this (team/role)
```

---

## Architecture Document Loading

### Full Document Loader

```python
import os
from pathlib import Path
from dataclasses import dataclass
import tiktoken

ARCHITECTURE_PATHS = [
    "materials/engineering/architecture",
    "materials/engineering/tech-specs",
]

MAX_TOKENS_PER_DOC = 30000  # Skip very large docs
MAX_TOTAL_TOKENS = 100000   # Context budget for architecture

def load_architecture_documents() -> list[ArchitectureDocument]:
    """Load full architecture documents for alignment analysis."""
    
    enc = tiktoken.get_encoding("cl100k_base")
    documents = []
    total_tokens = 0
    
    for base_path in ARCHITECTURE_PATHS:
        path = Path(base_path)
        if not path.exists():
            continue
        
        for file_path in path.rglob("*"):
            if file_path.suffix not in [".md", ".txt", ".rst"]:
                continue
            
            content = file_path.read_text()
            token_count = len(enc.encode(content))
            
            # Skip very large docs
            if token_count > MAX_TOKENS_PER_DOC:
                print(f"Skipping {file_path} ({token_count} tokens > {MAX_TOKENS_PER_DOC})")
                continue
            
            # Check total budget
            if total_tokens + token_count > MAX_TOTAL_TOKENS:
                print(f"Token budget reached, stopping at {total_tokens} tokens")
                break
            
            # Extract key components (simple heuristic)
            key_components = extract_components_from_doc(content)
            
            # Determine doc type
            if "architecture" in str(file_path).lower():
                doc_type = "architecture"
            elif "spec" in str(file_path).lower():
                doc_type = "tech-spec"
            else:
                doc_type = "design-doc"
            
            documents.append(ArchitectureDocument(
                id=f"doc_arch_{len(documents):03d}",
                path=str(file_path),
                title=extract_title(content, file_path),
                doc_type=doc_type,
                content=content,
                token_count=token_count,
                key_components=key_components,
                last_updated=get_file_modified_date(file_path),
                loaded_at=datetime.now().isoformat()
            ))
            
            total_tokens += token_count
    
    return documents


def extract_components_from_doc(content: str) -> list[str]:
    """Extract key component names from architecture doc."""
    import re
    
    components = set()
    
    # Look for common patterns
    patterns = [
        r'##\s+([A-Z][a-zA-Z\s]+(?:Service|Engine|API|System|Module|Component))',
        r'\*\*([A-Z][a-zA-Z\s]+(?:Service|Engine|API|System|Module|Component))\*\*',
        r'`([A-Z][a-zA-Z]+(?:Service|Engine|API))`',
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, content)
        components.update(matches)
    
    return list(components)[:20]  # Limit to top 20


def extract_title(content: str, file_path: Path) -> str:
    """Extract document title."""
    # Try to find # Title
    lines = content.split('\n')
    for line in lines[:10]:
        if line.startswith('# '):
            return line[2:].strip()
    
    # Fall back to filename
    return file_path.stem.replace('-', ' ').replace('_', ' ').title()
```

---

## Alignment Analysis Prompt

```python
ARCHITECTURE_ALIGNMENT_PROMPT = """
You are a technical architect analyzing alignment between a product roadmap and system architecture.

## Your Task

For each roadmap item, assess whether the current architecture supports it and identify gaps, risks, and required changes.

## Architecture Context

The following are the FULL architecture and technical design documents for the system:

{architecture_docs}

## Roadmap Items to Analyze

{roadmap_items}

## Analysis Instructions

For EACH roadmap item, provide:

### 1. Alignment Assessment

- **Architecture Supports**: Does the current architecture support this item?
  - `full` — Architecture fully supports, no changes needed
  - `partial` — Some support exists, but changes required
  - `no` — Architecture does not support, significant work needed
  - `unknown` — Cannot determine from available docs

- **Confidence**: How confident is this assessment?
  - `high` — Clear documentation exists
  - `medium` — Some inference required
  - `low` — Significant gaps in documentation

### 2. Supporting Components

List the existing components/services that enable this roadmap item.

### 3. Required Changes

For each change needed:
- **Component**: Which component needs to change
- **Change Type**: `new` (build new), `modify` (change existing), `deprecate` (remove), `migrate` (move/transform)
- **Description**: What specifically needs to change
- **Effort**: T-shirt size (S/M/L/XL)
- **Risk Level**: low/medium/high
- **Blocking**: Does this block the roadmap item from starting?

### 4. Technical Risks

For each risk:
- **Risk**: Description of the technical risk
- **Severity**: critical/high/medium/low
- **Likelihood**: high/medium/low
- **Mitigation**: How could this be mitigated
- **Owner**: Who should address this

### 5. Dependencies

Technical dependencies:
- **Prerequisite Work**: What must be done first (technically)
- **Enables**: What does completing this unblock (technically)
- **External Dependencies**: Third-party or cross-team dependencies

### 6. Engineering Questions

Generate 2-5 specific questions for engineering about this roadmap item. Questions should:
- Be specific and actionable
- Reference specific components or systems when relevant
- Help clarify feasibility, approach, or risk
- Be answerable by engineering leadership or architects

Question format:
```json
{
  "question": "Specific question text",
  "category": "feasibility|architecture|capacity|timeline|dependency|risk",
  "priority": "critical|high|medium|low",
  "context": "Why this question matters",
  "component": "Relevant component if applicable"
}
```

## Output Format

Return JSON:

```json
{
  "assessments": [
    {
      "roadmap_item": "Item name",
      "roadmap_item_description": "Full description",
      "horizon": "now|next|later|future",
      
      "architecture_supports": "full|partial|no|unknown",
      "confidence": "high|medium|low",
      "summary": "2-3 sentence summary of alignment status",
      
      "supporting_components": ["Component1", "Component2"],
      
      "required_changes": [
        {
          "component": "Component name",
          "change_type": "new|modify|deprecate|migrate",
          "description": "What needs to change",
          "effort": "S|M|L|XL",
          "risk_level": "low|medium|high",
          "blocking": true|false
        }
      ],
      
      "technical_risks": [
        {
          "risk": "Risk description",
          "severity": "critical|high|medium|low",
          "likelihood": "high|medium|low",
          "mitigation": "Mitigation approach",
          "owner": "Team or role"
        }
      ],
      
      "dependencies": {
        "prerequisite_work": ["Item1", "Item2"],
        "enables": ["Item3", "Item4"],
        "external": ["External dependency 1"]
      },
      
      "questions": [
        {
          "question": "Question text",
          "category": "feasibility",
          "priority": "high",
          "context": "Why this matters",
          "component": "Relevant component"
        }
      ]
    }
  ],
  
  "cross_cutting_concerns": {
    "architectural_gaps": ["Gap 1", "Gap 2"],
    "systemic_risks": ["Risk 1", "Risk 2"],
    "recommended_adrs": ["ADR topic 1", "ADR topic 2"],
    "sequencing_recommendations": "Narrative about technical sequencing"
  }
}
```

## Important Notes

1. **Be specific** — Reference actual components, APIs, and systems from the docs
2. **Surface unknowns** — If docs don't cover something, say so
3. **Think dependencies** — Technical work often has ordering constraints
4. **Consider scale** — What works for MVP may not work at scale
5. **Flag debt** — Note if roadmap items will create or require addressing tech debt

Now analyze the alignment between the roadmap and architecture.
"""
```

---

## Integration with Open Questions

### Flow Architecture Questions to Open Questions

```python
def generate_architecture_alignment(
    roadmap: dict,
    architecture_docs: list[ArchitectureDocument]
) -> dict:
    """Generate architecture alignment analysis and engineering questions."""
    
    # Format architecture docs
    arch_context = format_architecture_docs(architecture_docs)
    
    # Format roadmap items
    roadmap_items = format_roadmap_items_for_analysis(roadmap)
    
    # Build prompt
    prompt = ARCHITECTURE_ALIGNMENT_PROMPT.format(
        architecture_docs=arch_context,
        roadmap_items=roadmap_items
    )
    
    # Call Claude (use Opus for complex analysis)
    response = client.messages.create(
        model="claude-opus-4-20250514",
        max_tokens=8000,
        messages=[{"role": "user", "content": prompt}]
    )
    
    # Parse response
    analysis = parse_alignment_response(response)
    
    # Extract questions and add to Open Questions system
    engineering_questions = extract_engineering_questions(analysis)
    add_questions_to_system(engineering_questions, source="architecture_alignment")
    
    return analysis


def extract_engineering_questions(analysis: dict) -> list[dict]:
    """Extract all engineering questions from alignment analysis."""
    
    questions = []
    
    for assessment in analysis.get("assessments", []):
        roadmap_item = assessment.get("roadmap_item", "Unknown")
        
        for q in assessment.get("questions", []):
            questions.append({
                "id": f"q_eng_arch_{len(questions):03d}",
                "question": q["question"],
                "audience": "engineering",
                "category": q.get("category", "architecture"),
                "priority": q.get("priority", "medium"),
                "context": f"From architecture alignment analysis for: {roadmap_item}. {q.get('context', '')}",
                "source_type": "architecture_alignment",
                "related_roadmap_items": [roadmap_item],
                "related_component": q.get("component"),
                "status": "pending",
                "created_at": datetime.now().isoformat()
            })
    
    return questions


def add_questions_to_system(questions: list[dict], source: str):
    """Add generated questions to the Open Questions system."""
    
    existing = load_questions()
    
    # Avoid duplicates (simple check on question text similarity)
    existing_texts = {q["question"].lower() for q in existing}
    
    new_questions = []
    for q in questions:
        if q["question"].lower() not in existing_texts:
            q["source"] = source
            new_questions.append(q)
    
    save_questions(existing + new_questions)
    
    return len(new_questions)
```

---

## CLI Commands

### Analyze Architecture Alignment

```python
@app.command()
def architecture_alignment(
    roadmap_file: Path = typer.Option("output/master-roadmap.md", help="Roadmap file to analyze"),
    output: Path = typer.Option("output/architecture-alignment.md", help="Output file"),
    add_questions: bool = typer.Option(True, help="Add generated questions to Open Questions"),
    use_opus: bool = typer.Option(True, help="Use Opus for higher quality analysis")
):
    """Analyze alignment between roadmap and architecture documents."""
    
    console.print("[bold]Architecture Alignment Analysis[/bold]\n")
    
    # Load architecture documents
    with console.status("Loading architecture documents..."):
        arch_docs = load_architecture_documents()
    
    console.print(f"Loaded {len(arch_docs)} architecture documents:")
    for doc in arch_docs:
        console.print(f"  • {doc.title} ({doc.token_count} tokens)")
    
    total_tokens = sum(d.token_count for d in arch_docs)
    console.print(f"Total: {total_tokens} tokens\n")
    
    # Load roadmap
    if not roadmap_file.exists():
        console.print(f"[red]Roadmap file not found: {roadmap_file}[/red]")
        console.print("Run 'roadmap generate' first.")
        raise typer.Exit(1)
    
    roadmap_content = roadmap_file.read_text()
    roadmap = parse_roadmap_for_analysis(roadmap_content)
    
    console.print(f"Found {len(roadmap['items'])} roadmap items to analyze\n")
    
    # Run analysis
    with console.status("Analyzing architecture alignment (this may take a minute)..."):
        analysis = generate_architecture_alignment(
            roadmap=roadmap,
            architecture_docs=arch_docs,
            use_opus=use_opus
        )
    
    # Save results
    output_content = format_alignment_report(analysis)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(output_content)
    
    console.print(f"[green]Analysis saved to {output}[/green]\n")
    
    # Summary
    console.print("[bold]Summary[/bold]")
    
    full_support = len([a for a in analysis["assessments"] if a["architecture_supports"] == "full"])
    partial_support = len([a for a in analysis["assessments"] if a["architecture_supports"] == "partial"])
    no_support = len([a for a in analysis["assessments"] if a["architecture_supports"] == "no"])
    
    console.print(f"  Full support: {full_support}")
    console.print(f"  Partial support: {partial_support}")
    console.print(f"  No support: {no_support}")
    
    # Count questions
    total_questions = sum(len(a.get("questions", [])) for a in analysis["assessments"])
    console.print(f"\n  Engineering questions generated: {total_questions}")
    
    # Add questions
    if add_questions:
        questions = extract_engineering_questions(analysis)
        added = add_questions_to_system(questions, source="architecture_alignment")
        console.print(f"  Questions added to Open Questions: {added}")
    
    # Cross-cutting concerns
    cross_cutting = analysis.get("cross_cutting_concerns", {})
    if cross_cutting.get("architectural_gaps"):
        console.print("\n[yellow]Architectural Gaps Identified:[/yellow]")
        for gap in cross_cutting["architectural_gaps"]:
            console.print(f"  • {gap}")
    
    if cross_cutting.get("recommended_adrs"):
        console.print("\n[cyan]Recommended ADRs:[/cyan]")
        for adr in cross_cutting["recommended_adrs"]:
            console.print(f"  • {adr}")
```

### List Architecture Documents

```python
@app.command()
def architecture_docs(
    show_components: bool = typer.Option(False, help="Show extracted components")
):
    """List available architecture documents."""
    
    docs = load_architecture_documents()
    
    console.print(f"\n[bold]Architecture Documents[/bold] ({len(docs)} total)\n")
    
    total_tokens = 0
    for doc in docs:
        console.print(f"[cyan]{doc.title}[/cyan]")
        console.print(f"  Path: {doc.path}")
        console.print(f"  Type: {doc.doc_type}")
        console.print(f"  Tokens: {doc.token_count}")
        
        if show_components and doc.key_components:
            console.print(f"  Components: {', '.join(doc.key_components[:5])}")
        
        console.print()
        total_tokens += doc.token_count
    
    console.print(f"[bold]Total tokens: {total_tokens}[/bold]")
```

---

## Streamlit Integration

### New Page: Architecture Alignment

```python
elif page == "🏗️ Architecture Alignment":
    st.title("Architecture Alignment Analysis")
    
    st.markdown("""
    This analysis maps functional roadmap items to technical architecture to identify:
    - Whether architecture supports planned features
    - Required technical changes
    - Technical risks and dependencies
    - Engineering questions that need answers
    """)
    
    # Tabs
    tab1, tab2, tab3 = st.tabs(["📊 Analysis", "📄 Architecture Docs", "❓ Engineering Questions"])
    
    with tab1:
        st.subheader("Roadmap-Architecture Alignment")
        
        # Check for existing analysis
        alignment_file = Path("output/architecture-alignment.json")
        
        col1, col2 = st.columns([3, 1])
        with col2:
            if st.button("🔄 Run Analysis", type="primary"):
                with st.spinner("Analyzing alignment (this may take 1-2 minutes)..."):
                    arch_docs = load_architecture_documents()
                    roadmap = load_latest_roadmap()
                    analysis = generate_architecture_alignment(roadmap, arch_docs)
                    save_alignment_analysis(analysis)
                st.success("Analysis complete!")
                st.experimental_rerun()
        
        if alignment_file.exists():
            analysis = load_alignment_analysis()
            
            # Summary metrics
            assessments = analysis.get("assessments", [])
            
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Items Analyzed", len(assessments))
            col2.metric("Full Support", len([a for a in assessments if a["architecture_supports"] == "full"]))
            col3.metric("Partial Support", len([a for a in assessments if a["architecture_supports"] == "partial"]))
            col4.metric("No Support", len([a for a in assessments if a["architecture_supports"] == "no"]))
            
            # Filter
            support_filter = st.multiselect(
                "Filter by support level",
                ["full", "partial", "no", "unknown"],
                default=["partial", "no"]
            )
            
            # Display assessments
            for assessment in assessments:
                if assessment["architecture_supports"] not in support_filter:
                    continue
                
                support_icon = {
                    "full": "✅",
                    "partial": "⚠️",
                    "no": "❌",
                    "unknown": "❓"
                }.get(assessment["architecture_supports"], "❓")
                
                with st.expander(f"{support_icon} {assessment['roadmap_item']} ({assessment['horizon']})"):
                    st.write(f"**Description:** {assessment['roadmap_item_description']}")
                    st.write(f"**Architecture Support:** {assessment['architecture_supports']} (confidence: {assessment['confidence']})")
                    st.write(f"**Summary:** {assessment.get('summary', 'N/A')}")
                    
                    # Supporting components
                    if assessment.get("supporting_components"):
                        st.write("**Supporting Components:**")
                        for comp in assessment["supporting_components"]:
                            st.write(f"  • {comp}")
                    
                    # Required changes
                    if assessment.get("required_changes"):
                        st.write("**Required Changes:**")
                        for change in assessment["required_changes"]:
                            blocking = "🚫 BLOCKING" if change.get("blocking") else ""
                            st.write(f"  • **{change['component']}** ({change['change_type']}, {change['effort']}) — {change['description']} {blocking}")
                    
                    # Technical risks
                    if assessment.get("technical_risks"):
                        st.write("**Technical Risks:**")
                        for risk in assessment["technical_risks"]:
                            severity_color = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}.get(risk["severity"], "⚪")
                            st.write(f"  {severity_color} {risk['risk']}")
                            st.write(f"     Mitigation: {risk['mitigation']}")
                    
                    # Dependencies
                    deps = assessment.get("dependencies", {})
                    if deps.get("prerequisite_work"):
                        st.write(f"**Prerequisites:** {', '.join(deps['prerequisite_work'])}")
                    if deps.get("enables"):
                        st.write(f"**Enables:** {', '.join(deps['enables'])}")
                    
                    # Questions
                    if assessment.get("questions"):
                        st.write(f"**Engineering Questions:** {len(assessment['questions'])}")
                        for q in assessment["questions"]:
                            st.write(f"  • [{q['priority']}] {q['question']}")
            
            # Cross-cutting concerns
            cross_cutting = analysis.get("cross_cutting_concerns", {})
            
            st.markdown("---")
            st.subheader("Cross-Cutting Concerns")
            
            if cross_cutting.get("architectural_gaps"):
                st.write("**Architectural Gaps:**")
                for gap in cross_cutting["architectural_gaps"]:
                    st.write(f"  • {gap}")
            
            if cross_cutting.get("systemic_risks"):
                st.write("**Systemic Risks:**")
                for risk in cross_cutting["systemic_risks"]:
                    st.write(f"  • {risk}")
            
            if cross_cutting.get("recommended_adrs"):
                st.write("**Recommended ADRs:**")
                for adr in cross_cutting["recommended_adrs"]:
                    st.write(f"  • {adr}")
            
            if cross_cutting.get("sequencing_recommendations"):
                st.write("**Sequencing Recommendations:**")
                st.write(cross_cutting["sequencing_recommendations"])
            
            # Export
            st.markdown("---")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📥 Export as Markdown"):
                    md_content = format_alignment_report(analysis)
                    st.download_button(
                        "Download",
                        md_content,
                        file_name="architecture-alignment.md",
                        mime="text/markdown"
                    )
            with col2:
                if st.button("📥 Export as JSON"):
                    st.download_button(
                        "Download",
                        json.dumps(analysis, indent=2),
                        file_name="architecture-alignment.json",
                        mime="application/json"
                    )
        
        else:
            st.info("No analysis found. Click 'Run Analysis' to analyze roadmap against architecture.")
    
    with tab2:
        st.subheader("Architecture Documents")
        
        docs = load_architecture_documents()
        
        st.write(f"**{len(docs)} documents loaded** ({sum(d.token_count for d in docs)} total tokens)")
        
        for doc in docs:
            with st.expander(f"📄 {doc.title} ({doc.token_count} tokens)"):
                st.write(f"**Path:** {doc.path}")
                st.write(f"**Type:** {doc.doc_type}")
                st.write(f"**Last Updated:** {doc.last_updated}")
                
                if doc.key_components:
                    st.write(f"**Key Components:** {', '.join(doc.key_components)}")
                
                st.markdown("---")
                st.markdown("**Content Preview:**")
                st.code(doc.content[:2000] + "..." if len(doc.content) > 2000 else doc.content)
    
    with tab3:
        st.subheader("Engineering Questions from Architecture Analysis")
        
        questions = load_questions()
        arch_questions = [q for q in questions if q.get("source") == "architecture_alignment"]
        
        if not arch_questions:
            st.info("No architecture-related questions yet. Run an analysis to generate questions.")
        else:
            pending = [q for q in arch_questions if q["status"] == "pending"]
            answered = [q for q in arch_questions if q["status"] == "answered"]
            
            st.write(f"**{len(pending)} pending** | {len(answered)} answered")
            
            for q in sorted(pending, key=lambda x: {"critical": 0, "high": 1, "medium": 2, "low": 3}.get(x["priority"], 4)):
                priority_icon = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}.get(q["priority"], "⚪")
                
                with st.expander(f"{priority_icon} {q['question'][:80]}..."):
                    st.write(f"**Question:** {q['question']}")
                    st.write(f"**Category:** {q['category']}")
                    st.write(f"**Context:** {q.get('context', 'N/A')}")
                    
                    if q.get("related_component"):
                        st.write(f"**Component:** {q['related_component']}")
                    
                    if q.get("related_roadmap_items"):
                        st.write(f"**Roadmap Items:** {', '.join(q['related_roadmap_items'])}")
                    
                    if st.button("Go to Answer", key=f"goto_{q['id']}"):
                        st.session_state.answering_question = q['id']
                        # Navigate to Open Questions page
```

---

## Output Format: Alignment Report

```markdown
# Architecture Alignment Report

Generated: 2025-01-15 14:30:00

## Executive Summary

- **Items Analyzed:** 24
- **Full Support:** 8 (33%)
- **Partial Support:** 12 (50%)
- **No Support:** 4 (17%)

### Key Findings

1. Catalog-related roadmap items require significant API migration work
2. Event system needs enhancement for real-time features
3. Three items have blocking technical dependencies

---

## Alignment Details

### 🟢 Full Support

#### Feature: Basic Pricing Display
- **Horizon:** Now
- **Architecture Support:** Full (High Confidence)
- **Summary:** Current Pricing Engine fully supports this with existing APIs.
- **Supporting Components:** Pricing Engine, Product API
- **Required Changes:** None
- **Technical Risks:** None identified

---

### ⚠️ Partial Support

#### Feature: Dynamic Bundle Configuration
- **Horizon:** Next
- **Architecture Support:** Partial (Medium Confidence)
- **Summary:** Bundle logic exists but needs extension for dynamic rules.

**Supporting Components:**
- Catalog Service (partial)
- Pricing Engine (full)

**Required Changes:**
| Component | Change | Effort | Risk | Blocking |
|-----------|--------|--------|------|----------|
| Catalog Service | Add dynamic rule engine | L | Medium | No |
| Admin UI | Bundle configuration screens | M | Low | No |

**Technical Risks:**
- 🟠 **Performance at scale** — Dynamic rules may impact pricing calculation time
  - Mitigation: Implement caching layer for rule evaluation
  - Owner: Platform Team

**Dependencies:**
- Prerequisites: Catalog API v2 migration
- Enables: Advanced Pricing Rules, Experience Builder

**Engineering Questions:**
1. [HIGH] Can the rule engine handle 1000+ rules without performance degradation?
2. [MEDIUM] Should bundle rules be evaluated at runtime or pre-computed?

---

### ❌ No Support

#### Feature: Real-time Collaboration
- **Horizon:** Later
- **Architecture Support:** No (High Confidence)
- **Summary:** Current architecture has no WebSocket or real-time event infrastructure.

**Required Changes:**
| Component | Change | Effort | Risk | Blocking |
|-----------|--------|--------|------|----------|
| Event System | Add WebSocket gateway | XL | High | Yes |
| All Services | Emit real-time events | L | Medium | Yes |

**Technical Risks:**
- 🔴 **Infrastructure complexity** — WebSocket at scale requires significant ops investment
  - Mitigation: Consider managed service (Pusher, Ably)
  - Owner: Architecture Team

**Engineering Questions:**
1. [CRITICAL] Build vs. buy for real-time infrastructure?
2. [HIGH] What's the expected concurrent user count for real-time features?

---

## Cross-Cutting Concerns

### Architectural Gaps
1. No real-time/WebSocket infrastructure
2. Event system is fire-and-forget, no guaranteed delivery
3. No feature flag system for gradual rollouts

### Systemic Risks
1. Catalog API migration is on critical path for 60% of roadmap items
2. Single point of failure in Pricing Engine

### Recommended ADRs
1. ADR: Real-time infrastructure approach (build vs. buy)
2. ADR: Event delivery guarantees
3. ADR: Catalog API v2 migration strategy

### Sequencing Recommendations
The Catalog API migration should be prioritized as it unblocks the most roadmap items. Real-time infrastructure should be a parallel workstream given its long lead time. Consider splitting the Event System enhancement into phases.

---

## Engineering Questions Summary

| Priority | Count |
|----------|-------|
| Critical | 3 |
| High | 12 |
| Medium | 8 |
| Low | 2 |

All questions have been added to the Open Questions system.
```

---

## Implementation Order

1. **Architecture document loader** (20 min)
   - Load full docs from engineering folders
   - Token counting and budget management
   - Component extraction

2. **Alignment analysis prompt** (15 min)
   - Create detailed prompt
   - Define output schema

3. **Analysis function** (25 min)
   - Call Claude with full context
   - Parse response
   - Save results

4. **Question integration** (15 min)
   - Extract questions from analysis
   - Add to Open Questions system
   - Link to roadmap items

5. **CLI commands** (20 min)
   - architecture-alignment command
   - architecture-docs listing

6. **Streamlit page** (30 min)
   - Analysis view with filtering
   - Document browser
   - Question links

7. **Report formatting** (15 min)
   - Markdown export
   - JSON export

8. **Testing** (20 min)
   - Test with real architecture docs
   - Verify questions flow to Open Questions

---

## Success Criteria

- [ ] Full architecture documents loaded (not chunked)
- [ ] Each roadmap item assessed for architecture support
- [ ] Required changes identified with effort estimates
- [ ] Technical risks surfaced with mitigations
- [ ] Engineering questions generated per roadmap item
- [ ] Questions flow into Open Questions system
- [ ] Cross-cutting concerns identified (gaps, ADRs needed)
- [ ] Report exportable as Markdown
