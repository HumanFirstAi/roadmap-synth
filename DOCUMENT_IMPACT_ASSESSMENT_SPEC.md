# Document Impact Assessment Specification

## Overview

This feature creates a gated ingestion flow where new documents are assessed for novelty before being added to the knowledge base. The assessment compares the new document against:

- Current synthesized roadmap
- Existing indexed chunks
- Architecture documents

The output is an impact assessment that determines whether the document adds novel value or replicates existing understanding.

---

## Problem Statement

Currently, all documents are ingested without evaluation:
- Redundant content pollutes the index
- Novel insights get buried among duplicates
- No visibility into what new information a document brings
- Roadmap updates happen manually without knowing what changed

This feature solves these problems by:
1. Assessing documents before ingestion
2. Classifying novelty and impact
3. Recommending whether to ingest
4. Identifying specific roadmap impacts
5. Enabling informed decisions about updates

---

## Workflow

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  1. UPLOAD NEW DOCUMENT                                     │
│     User provides document + selects lens type              │
│                        │                                    │
│                        ▼                                    │
│  2. PARSE & EXTRACT                                         │
│     Full document loaded, key concepts extracted            │
│                        │                                    │
│                        ▼                                    │
│  3. COMPARE AGAINST EXISTING                                │
│     • Semantic similarity to existing chunks                │
│     • Concept overlap with roadmap                          │
│     • Alignment/conflict with architecture                  │
│                        │                                    │
│                        ▼                                    │
│  4. NOVELTY CLASSIFICATION                                  │
│     • Novel concepts identified                             │
│     • New tensions surfaced                                 │
│     • Reinforcements noted                                  │
│     • Contradictions flagged                                │
│                        │                                    │
│                        ▼                                    │
│  5. IMPACT SCORING                                          │
│     HIGH / MEDIUM / LOW                                     │
│                        │                                    │
│                        ▼                                    │
│  6. RECOMMENDATION                                          │
│     • Ingest + Update Roadmap                               │
│     • Ingest Only                                           │
│     • Skip / Archive                                        │
│                        │                                    │
│                        ▼                                    │
│  7. USER DECISION                                           │
│     Accept recommendation or override                       │
│                        │                                    │
│           ┌───────────┴───────────┐                        │
│           ▼                       ▼                         │
│     ┌──────────┐           ┌──────────┐                    │
│     │  INGEST  │           │   SKIP   │                    │
│     └────┬─────┘           └──────────┘                    │
│          │                                                  │
│          ▼                                                  │
│  8. OPTIONAL: REGENERATE ROADMAP                            │
│     With new content included                               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Data Model

### ImpactAssessment

```python
@dataclass
class ImpactAssessment:
    id: str                              # assess_001
    document_path: str                   # Path to assessed document
    document_name: str                   # Filename
    lens: str                            # Suggested/selected lens
    assessed_at: str                     # ISO timestamp
    
    # Document stats
    document_tokens: int                 # Token count
    document_summary: str                # AI-generated summary
    
    # Novelty analysis
    novel_concepts: list[NovelConcept]   # New ideas not in existing sources
    new_tensions: list[NewTension]       # Conflicts/contradictions found
    alternative_approaches: list[Alternative]  # Different ways suggested
    reinforcements: list[Reinforcement]  # Things that confirm existing
    contradictions: list[Contradiction]  # Things that contradict existing
    
    # Similarity analysis
    most_similar_chunks: list[dict]      # Top N similar existing chunks
    avg_similarity_score: float          # How similar to existing content
    unique_content_ratio: float          # % of content that's novel
    
    # Impact scoring
    impact_level: str                    # high, medium, low
    impact_score: float                  # 0-1 numeric score
    impact_reasons: list[str]            # Why this impact level
    
    # Roadmap impact
    roadmap_impacts: list[RoadmapImpact] # Specific impacts on roadmap
    new_questions_generated: list[dict]  # Questions this raises
    
    # Recommendation
    recommendation: str                  # ingest_and_update, ingest_only, skip
    recommendation_rationale: str        # Why this recommendation
    
    # User action
    user_decision: str                   # accepted, overridden, pending
    user_notes: str                      # User's notes on decision
    action_taken: str                    # ingested, skipped, archived
    action_at: str                       # When action was taken
```

### NovelConcept

```python
@dataclass
class NovelConcept:
    concept: str                         # Description of the concept
    source_quote: str                    # Exact quote from document
    category: str                        # feature, requirement, risk, opportunity, constraint
    relevance: str                       # high, medium, low
    related_roadmap_areas: list[str]     # Which roadmap areas this touches
    suggested_action: str                # What to do with this concept
```

### NewTension

```python
@dataclass
class NewTension:
    tension: str                         # Description of the tension
    source_quote: str                    # Quote from new document
    conflicts_with: str                  # What existing content it conflicts with
    conflict_source: str                 # Where the conflict exists (roadmap, chunk, architecture)
    severity: str                        # critical, high, medium, low
    resolution_needed: bool              # Does this need explicit resolution?
    suggested_resolution: str            # How to resolve
```

### Reinforcement

```python
@dataclass
class Reinforcement:
    concept: str                         # What is being reinforced
    source_quote: str                    # Quote from new document
    reinforces: str                      # What existing content it reinforces
    confidence_boost: str                # How much this increases confidence
```

### Contradiction

```python
@dataclass
class Contradiction:
    statement: str                       # The contradicting statement
    source_quote: str                    # Quote from new document
    contradicts: str                     # What it contradicts
    contradiction_source: str            # Where (roadmap item, chunk, architecture)
    severity: str                        # critical, high, medium, low
    which_is_correct: str                # new, existing, unclear, both_valid
```

### RoadmapImpact

```python
@dataclass
class RoadmapImpact:
    impact_type: str                     # add_item, modify_item, elevate_priority, add_risk, new_dependency, new_question
    description: str                     # What the impact is
    roadmap_section: str                 # Which section affected
    specific_item: str                   # Specific item if applicable
    urgency: str                         # immediate, next_update, future
```

---

## Assessment Prompt

```python
IMPACT_ASSESSMENT_PROMPT = """
You are an expert analyst assessing a new document's impact on an existing product roadmap and knowledge base.

## Your Task

Analyze the new document and determine:
1. What novel concepts does it introduce?
2. What tensions or contradictions does it surface?
3. Does it reinforce or contradict existing understanding?
4. What is its overall impact on the roadmap?
5. Should it be ingested?

## CRITICAL: Extraction Only for Quotes

When identifying concepts, tensions, or contradictions:
- Use EXACT quotes from the documents
- DO NOT paraphrase or interpret
- Cite specific text that supports each finding

## Existing Context

### Current Roadmap
{roadmap_content}

### Existing Knowledge (Most Relevant Chunks)
{relevant_chunks}

### Architecture Context
{architecture_summary}

## New Document to Assess

**Proposed Lens:** {proposed_lens}
**Document:**
{new_document}

## Analysis Instructions

### 1. Novel Concepts

Identify concepts in the new document that are NOT present in existing context:

- New feature ideas or requirements
- New customer needs or use cases
- New risks or concerns not previously documented
- New opportunities not previously identified
- New constraints or limitations

For each novel concept:
- Extract the exact quote
- Categorize (feature, requirement, risk, opportunity, constraint)
- Assess relevance (high, medium, low)
- Identify related roadmap areas
- Suggest what to do with it

### 2. New Tensions

Identify tensions between the new document and existing content:

- Timeline conflicts
- Priority disagreements
- Resource contentions
- Strategic direction differences
- Technical approach conflicts

For each tension:
- Quote the source from new document
- Identify what it conflicts with
- Assess severity
- Suggest resolution

### 3. Alternative Approaches

Does the document suggest different ways of doing things?

- Different technical solutions
- Different prioritization
- Different customer focus
- Different timeline

### 4. Reinforcements

What existing content does this document reinforce?

- Confirms priorities
- Validates direction
- Adds evidence
- Strengthens confidence

### 5. Contradictions

What existing content does this document directly contradict?

- Factual contradictions
- Priority contradictions
- Timeline contradictions
- Approach contradictions

For each contradiction, assess which is likely correct.

### 6. Similarity Analysis

How similar is this document to existing content?

- Is it mostly restating known information?
- What percentage is genuinely new?
- Which existing chunks is it most similar to?

### 7. Impact Scoring

**HIGH Impact** (score 0.7-1.0):
- Contains multiple novel concepts
- Surfaces critical tensions
- Would significantly change roadmap
- Introduces new strategic considerations

**MEDIUM Impact** (score 0.4-0.69):
- Contains some novel concepts
- Adds nuance to existing understanding
- May affect specific roadmap items
- Provides useful reinforcement

**LOW Impact** (score 0.0-0.39):
- Mostly replicates existing knowledge
- No significant novel concepts
- Minimal roadmap impact
- Could be skipped without loss

### 8. Roadmap Impact

If ingested, how would this affect the roadmap?

- New items to add?
- Items to modify?
- Priorities to change?
- Risks to elevate?
- Dependencies to add?
- Questions to raise?

### 9. Recommendation

Based on analysis, recommend:

- **ingest_and_update**: High impact, should ingest and regenerate roadmap
- **ingest_only**: Medium impact, worth adding to knowledge base
- **skip**: Low impact, doesn't add significant value
- **archive**: Keep for reference but don't ingest

## Output Format

Return JSON:

```json
{
  "document_summary": "2-3 sentence summary of the document",
  
  "novel_concepts": [
    {
      "concept": "Description of novel concept",
      "source_quote": "Exact quote from document",
      "category": "feature|requirement|risk|opportunity|constraint",
      "relevance": "high|medium|low",
      "related_roadmap_areas": ["Area 1", "Area 2"],
      "suggested_action": "What to do with this"
    }
  ],
  
  "new_tensions": [
    {
      "tension": "Description of tension",
      "source_quote": "Exact quote from new document",
      "conflicts_with": "What it conflicts with",
      "conflict_source": "roadmap|chunk|architecture",
      "severity": "critical|high|medium|low",
      "resolution_needed": true|false,
      "suggested_resolution": "How to resolve"
    }
  ],
  
  "alternative_approaches": [
    {
      "approach": "Description of alternative",
      "source_quote": "Exact quote",
      "differs_from": "Current approach",
      "merit": "Why this might be better/worse"
    }
  ],
  
  "reinforcements": [
    {
      "concept": "What is reinforced",
      "source_quote": "Exact quote",
      "reinforces": "What existing content",
      "confidence_boost": "high|medium|low"
    }
  ],
  
  "contradictions": [
    {
      "statement": "The contradicting statement",
      "source_quote": "Exact quote",
      "contradicts": "What it contradicts",
      "contradiction_source": "roadmap|chunk|architecture",
      "severity": "critical|high|medium|low",
      "which_is_correct": "new|existing|unclear|both_valid"
    }
  ],
  
  "similarity_analysis": {
    "avg_similarity_score": 0.65,
    "unique_content_ratio": 0.35,
    "most_similar_to": ["chunk_id_1", "chunk_id_2"],
    "overlap_summary": "Description of what overlaps"
  },
  
  "impact_assessment": {
    "impact_level": "high|medium|low",
    "impact_score": 0.75,
    "impact_reasons": [
      "Reason 1",
      "Reason 2"
    ]
  },
  
  "roadmap_impacts": [
    {
      "impact_type": "add_item|modify_item|elevate_priority|add_risk|new_dependency|new_question",
      "description": "What the impact is",
      "roadmap_section": "Section affected",
      "specific_item": "Item name if applicable",
      "urgency": "immediate|next_update|future"
    }
  ],
  
  "new_questions": [
    {
      "question": "Question text",
      "audience": "engineering|leadership|product",
      "category": "feasibility|investment|direction|trade-off",
      "priority": "critical|high|medium|low",
      "context": "Why this question arose"
    }
  ],
  
  "recommendation": {
    "action": "ingest_and_update|ingest_only|skip|archive",
    "rationale": "Why this recommendation",
    "confidence": "high|medium|low"
  }
}
```

Now analyze the new document against the existing context.
"""
```

---

## Implementation

### Assessment Function

```python
import json
from pathlib import Path
from datetime import datetime

def assess_document_impact(
    document_path: Path,
    proposed_lens: str,
    use_opus: bool = False
) -> ImpactAssessment:
    """
    Assess a new document's impact on the existing roadmap and knowledge base.
    """
    
    # 1. Load new document
    document_content = document_path.read_text()
    document_tokens = count_tokens(document_content)
    
    # 2. Load existing context
    roadmap = load_latest_roadmap()
    
    # 3. Find similar existing chunks
    similar_chunks = find_similar_chunks(document_content, top_n=20)
    
    # 4. Load architecture summary
    architecture_summary = get_architecture_summary()
    
    # 5. Build prompt
    prompt = IMPACT_ASSESSMENT_PROMPT.format(
        roadmap_content=roadmap,
        relevant_chunks=format_chunks_for_assessment(similar_chunks),
        architecture_summary=architecture_summary,
        proposed_lens=proposed_lens,
        new_document=document_content
    )
    
    # 6. Call Claude
    model = "claude-opus-4-20250514" if use_opus else "claude-sonnet-4-20250514"
    
    response = client.messages.create(
        model=model,
        max_tokens=8000,
        messages=[{"role": "user", "content": prompt}]
    )
    
    # 7. Parse response
    analysis = parse_assessment_response(response)
    
    # 8. Build assessment object
    assessment = ImpactAssessment(
        id=f"assess_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        document_path=str(document_path),
        document_name=document_path.name,
        lens=proposed_lens,
        assessed_at=datetime.now().isoformat(),
        document_tokens=document_tokens,
        document_summary=analysis.get("document_summary", ""),
        novel_concepts=parse_novel_concepts(analysis),
        new_tensions=parse_tensions(analysis),
        alternative_approaches=parse_alternatives(analysis),
        reinforcements=parse_reinforcements(analysis),
        contradictions=parse_contradictions(analysis),
        most_similar_chunks=analysis.get("similarity_analysis", {}).get("most_similar_to", []),
        avg_similarity_score=analysis.get("similarity_analysis", {}).get("avg_similarity_score", 0),
        unique_content_ratio=analysis.get("similarity_analysis", {}).get("unique_content_ratio", 0),
        impact_level=analysis.get("impact_assessment", {}).get("impact_level", "low"),
        impact_score=analysis.get("impact_assessment", {}).get("impact_score", 0),
        impact_reasons=analysis.get("impact_assessment", {}).get("impact_reasons", []),
        roadmap_impacts=parse_roadmap_impacts(analysis),
        new_questions_generated=analysis.get("new_questions", []),
        recommendation=analysis.get("recommendation", {}).get("action", "skip"),
        recommendation_rationale=analysis.get("recommendation", {}).get("rationale", ""),
        user_decision="pending",
        user_notes="",
        action_taken="",
        action_at=""
    )
    
    # 9. Save assessment
    save_assessment(assessment)
    
    return assessment


def find_similar_chunks(document_content: str, top_n: int = 20) -> list[dict]:
    """Find chunks most similar to the new document."""
    
    # Embed document (or key sections)
    # For long documents, embed multiple sections and aggregate
    
    sections = split_for_similarity(document_content)
    
    all_similar = []
    seen_ids = set()
    
    for section in sections:
        embedding = embedder.embed_query(section)
        results = table.search(embedding).limit(top_n).to_list()
        
        for r in results:
            if r["id"] not in seen_ids:
                seen_ids.add(r["id"])
                all_similar.append(r)
    
    # Sort by similarity and return top N
    all_similar.sort(key=lambda x: x.get("_distance", 1))
    return all_similar[:top_n]


def format_chunks_for_assessment(chunks: list[dict]) -> str:
    """Format chunks for inclusion in assessment prompt."""
    
    output = []
    
    for chunk in chunks:
        output.append(f"### Chunk: {chunk['id']}")
        output.append(f"**Lens:** {chunk.get('lens', 'unknown')}")
        output.append(f"**Source:** {chunk.get('source_path', 'unknown')}")
        output.append(f"**Content:**")
        output.append(chunk.get("content", chunk.get("text", ""))[:1000])
        output.append("")
    
    return "\n".join(output)


def get_architecture_summary() -> str:
    """Get a summary of architecture for context."""
    
    arch_docs = load_architecture_documents()
    
    if not arch_docs:
        return "No architecture documents available."
    
    summaries = []
    for doc in arch_docs[:5]:  # Top 5 docs
        summaries.append(f"**{doc.title}**")
        summaries.append(f"Components: {', '.join(doc.key_components[:5])}")
        summaries.append(f"Preview: {doc.content[:500]}...")
        summaries.append("")
    
    return "\n".join(summaries)
```

### Action Functions

```python
def ingest_assessed_document(assessment_id: str, regenerate_roadmap: bool = False) -> dict:
    """Ingest a document that has been assessed."""
    
    # Load assessment
    assessment = load_assessment(assessment_id)
    
    if assessment.action_taken:
        raise ValueError(f"Assessment {assessment_id} already actioned: {assessment.action_taken}")
    
    # Ingest the document
    document_path = Path(assessment.document_path)
    chunks = ingest_document(document_path, assessment.lens)
    
    # Update assessment
    assessment.action_taken = "ingested"
    assessment.action_at = datetime.now().isoformat()
    save_assessment(assessment)
    
    # Add any new questions to Open Questions
    if assessment.new_questions_generated:
        add_questions_to_system(
            assessment.new_questions_generated,
            source=f"impact_assessment_{assessment_id}"
        )
    
    result = {
        "assessment_id": assessment_id,
        "chunks_created": len(chunks),
        "questions_added": len(assessment.new_questions_generated)
    }
    
    # Optionally regenerate roadmap
    if regenerate_roadmap:
        roadmap = generate_roadmap()
        result["roadmap_regenerated"] = True
        result["roadmap_path"] = "output/master-roadmap.md"
    
    return result


def skip_assessed_document(assessment_id: str, reason: str = "") -> dict:
    """Skip ingesting a document."""
    
    assessment = load_assessment(assessment_id)
    
    assessment.action_taken = "skipped"
    assessment.action_at = datetime.now().isoformat()
    assessment.user_notes = reason
    save_assessment(assessment)
    
    return {"assessment_id": assessment_id, "action": "skipped"}


def archive_assessed_document(assessment_id: str, reason: str = "") -> dict:
    """Archive a document for reference without ingesting."""
    
    assessment = load_assessment(assessment_id)
    
    # Move document to archive folder
    source = Path(assessment.document_path)
    archive_dir = Path("materials/archive")
    archive_dir.mkdir(exist_ok=True)
    
    dest = archive_dir / source.name
    source.rename(dest)
    
    assessment.document_path = str(dest)
    assessment.action_taken = "archived"
    assessment.action_at = datetime.now().isoformat()
    assessment.user_notes = reason
    save_assessment(assessment)
    
    return {"assessment_id": assessment_id, "action": "archived", "archived_to": str(dest)}
```

---

## CLI Commands

### Assess Document

```python
@app.command()
def assess(
    document: Path = typer.Argument(..., help="Path to document to assess"),
    lens: str = typer.Option(..., help="Proposed lens for the document"),
    use_opus: bool = typer.Option(False, help="Use Opus for higher quality analysis")
):
    """Assess a new document's impact on the roadmap."""
    
    if lens not in VALID_LENSES:
        console.print(f"[red]Invalid lens: {lens}[/red]")
        console.print(f"Valid lenses: {', '.join(VALID_LENSES)}")
        raise typer.Exit(1)
    
    if not document.exists():
        console.print(f"[red]Document not found: {document}[/red]")
        raise typer.Exit(1)
    
    console.print(f"\n[bold]Assessing Document Impact[/bold]")
    console.print(f"Document: {document}")
    console.print(f"Proposed Lens: {lens}\n")
    
    with console.status("Analyzing document against existing knowledge..."):
        assessment = assess_document_impact(document, lens, use_opus=use_opus)
    
    # Display results
    display_assessment(assessment)
    
    # Prompt for action
    console.print("\n[bold]What would you like to do?[/bold]")
    console.print("1. Ingest and update roadmap")
    console.print("2. Ingest only")
    console.print("3. Skip")
    console.print("4. Archive")
    
    choice = typer.prompt("Choice", type=int, default=get_default_choice(assessment))
    
    if choice == 1:
        result = ingest_assessed_document(assessment.id, regenerate_roadmap=True)
        console.print(f"[green]Ingested {result['chunks_created']} chunks and regenerated roadmap[/green]")
    elif choice == 2:
        result = ingest_assessed_document(assessment.id, regenerate_roadmap=False)
        console.print(f"[green]Ingested {result['chunks_created']} chunks[/green]")
    elif choice == 3:
        reason = typer.prompt("Reason for skipping (optional)", default="")
        skip_assessed_document(assessment.id, reason)
        console.print("[yellow]Document skipped[/yellow]")
    elif choice == 4:
        reason = typer.prompt("Reason for archiving (optional)", default="")
        result = archive_assessed_document(assessment.id, reason)
        console.print(f"[yellow]Document archived to {result['archived_to']}[/yellow]")


def display_assessment(assessment: ImpactAssessment):
    """Display assessment results in console."""
    
    # Impact level with color
    impact_color = {"high": "red", "medium": "yellow", "low": "green"}.get(assessment.impact_level, "white")
    
    console.print(f"\n[bold]Assessment: {assessment.id}[/bold]")
    console.print(f"Document: {assessment.document_name}")
    console.print(f"Tokens: {assessment.document_tokens}")
    console.print(f"\n[bold]Summary:[/bold] {assessment.document_summary}")
    
    # Impact
    console.print(f"\n[{impact_color}][bold]Impact Level: {assessment.impact_level.upper()}[/bold][/{impact_color}]")
    console.print(f"Score: {assessment.impact_score:.2f}")
    console.print(f"Unique Content: {assessment.unique_content_ratio:.0%}")
    
    for reason in assessment.impact_reasons:
        console.print(f"  • {reason}")
    
    # Novel concepts
    if assessment.novel_concepts:
        console.print(f"\n[bold]Novel Concepts ({len(assessment.novel_concepts)})[/bold]")
        for concept in assessment.novel_concepts[:5]:
            relevance_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(concept.relevance, "⚪")
            console.print(f"  {relevance_icon} {concept.concept}")
            console.print(f"     [dim]\"{concept.source_quote[:100]}...\"[/dim]")
    
    # New tensions
    if assessment.new_tensions:
        console.print(f"\n[bold]New Tensions ({len(assessment.new_tensions)})[/bold]")
        for tension in assessment.new_tensions:
            severity_icon = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}.get(tension.severity, "⚪")
            console.print(f"  {severity_icon} {tension.tension}")
            console.print(f"     Conflicts with: {tension.conflicts_with}")
    
    # Contradictions
    if assessment.contradictions:
        console.print(f"\n[bold]Contradictions ({len(assessment.contradictions)})[/bold]")
        for contradiction in assessment.contradictions:
            console.print(f"  ⚠️ {contradiction.statement}")
            console.print(f"     Contradicts: {contradiction.contradicts}")
    
    # Reinforcements
    if assessment.reinforcements:
        console.print(f"\n[bold]Reinforcements ({len(assessment.reinforcements)})[/bold]")
        for reinforcement in assessment.reinforcements[:3]:
            console.print(f"  ✓ {reinforcement.concept}")
    
    # Roadmap impacts
    if assessment.roadmap_impacts:
        console.print(f"\n[bold]Roadmap Impacts ({len(assessment.roadmap_impacts)})[/bold]")
        for impact in assessment.roadmap_impacts:
            urgency_icon = {"immediate": "🔴", "next_update": "🟡", "future": "🟢"}.get(impact.urgency, "⚪")
            console.print(f"  {urgency_icon} [{impact.impact_type}] {impact.description}")
    
    # New questions
    if assessment.new_questions_generated:
        console.print(f"\n[bold]New Questions Generated ({len(assessment.new_questions_generated)})[/bold]")
        for q in assessment.new_questions_generated[:3]:
            console.print(f"  • [{q['audience']}] {q['question'][:80]}...")
    
    # Recommendation
    rec_color = {
        "ingest_and_update": "red",
        "ingest_only": "yellow",
        "skip": "green",
        "archive": "dim"
    }.get(assessment.recommendation, "white")
    
    console.print(f"\n[{rec_color}][bold]Recommendation: {assessment.recommendation.upper()}[/bold][/{rec_color}]")
    console.print(f"{assessment.recommendation_rationale}")


def get_default_choice(assessment: ImpactAssessment) -> int:
    """Get default choice based on recommendation."""
    return {
        "ingest_and_update": 1,
        "ingest_only": 2,
        "skip": 3,
        "archive": 4
    }.get(assessment.recommendation, 3)
```

### List Assessments

```python
@app.command()
def assessments(
    status: str = typer.Option("all", help="Filter by status: pending, actioned, all"),
    limit: int = typer.Option(20, help="Number of assessments to show")
):
    """List document impact assessments."""
    
    all_assessments = load_all_assessments()
    
    # Filter
    if status == "pending":
        all_assessments = [a for a in all_assessments if a.user_decision == "pending"]
    elif status == "actioned":
        all_assessments = [a for a in all_assessments if a.action_taken]
    
    # Sort by date
    all_assessments = sorted(all_assessments, key=lambda x: x.assessed_at, reverse=True)[:limit]
    
    console.print(f"\n[bold]Document Assessments[/bold] ({len(all_assessments)} shown)\n")
    
    for a in all_assessments:
        impact_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(a.impact_level, "⚪")
        status_icon = "✅" if a.action_taken else "⏳"
        
        console.print(f"{status_icon} {impact_icon} [bold]{a.document_name}[/bold]")
        console.print(f"   ID: {a.id} | Lens: {a.lens} | Impact: {a.impact_level}")
        console.print(f"   Novel: {len(a.novel_concepts)} | Tensions: {len(a.new_tensions)} | Recommendation: {a.recommendation}")
        if a.action_taken:
            console.print(f"   [dim]Action: {a.action_taken} at {a.action_at[:10]}[/dim]")
        console.print()
```

---

## Streamlit Integration

### New Page: Document Assessment

```python
elif page == "📄 Assess Document":
    st.title("Document Impact Assessment")
    
    st.markdown("""
    Upload a new document to assess its impact on the existing roadmap and knowledge base.
    The assessment will identify:
    - Novel concepts not in existing sources
    - New tensions or contradictions
    - Reinforcements of existing understanding
    - Recommended action (ingest, skip, archive)
    """)
    
    # Tabs
    tab1, tab2 = st.tabs(["📤 New Assessment", "📋 Assessment History"])
    
    with tab1:
        st.subheader("Assess New Document")
        
        # File upload
        uploaded_file = st.file_uploader(
            "Upload document",
            type=["txt", "md", "pdf", "docx", "pptx"]
        )
        
        # Lens selection
        lens = st.selectbox(
            "Proposed Lens",
            list(VALID_LENSES),
            help="How should this document be classified?"
        )
        
        # Analysis options
        use_opus = st.checkbox(
            "Use Opus for higher quality analysis",
            value=False,
            help="Opus provides better analysis but costs more"
        )
        
        if uploaded_file and st.button("🔍 Assess Impact", type="primary"):
            # Save uploaded file temporarily
            temp_path = Path(f"temp/{uploaded_file.name}")
            temp_path.parent.mkdir(exist_ok=True)
            temp_path.write_bytes(uploaded_file.getvalue())
            
            with st.spinner("Analyzing document against existing knowledge (this may take a minute)..."):
                assessment = assess_document_impact(temp_path, lens, use_opus=use_opus)
            
            # Store in session for display
            st.session_state.current_assessment = assessment
            st.experimental_rerun()
        
        # Display current assessment
        if "current_assessment" in st.session_state:
            assessment = st.session_state.current_assessment
            
            st.markdown("---")
            st.subheader(f"Assessment: {assessment.document_name}")
            
            # Impact level banner
            impact_color = {"high": "red", "medium": "orange", "low": "green"}.get(assessment.impact_level, "gray")
            st.markdown(f"""
            <div style="background-color: {impact_color}; padding: 10px; border-radius: 5px; color: white;">
                <h3>Impact Level: {assessment.impact_level.upper()}</h3>
                <p>Score: {assessment.impact_score:.2f} | Unique Content: {assessment.unique_content_ratio:.0%}</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.write(f"**Summary:** {assessment.document_summary}")
            
            # Metrics
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Novel Concepts", len(assessment.novel_concepts))
            col2.metric("New Tensions", len(assessment.new_tensions))
            col3.metric("Reinforcements", len(assessment.reinforcements))
            col4.metric("Contradictions", len(assessment.contradictions))
            
            # Novel concepts
            if assessment.novel_concepts:
                st.subheader("Novel Concepts")
                for concept in assessment.novel_concepts:
                    relevance_color = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(concept.relevance, "⚪")
                    with st.expander(f"{relevance_color} {concept.concept}"):
                        st.write(f"**Category:** {concept.category}")
                        st.write(f"**Relevance:** {concept.relevance}")
                        st.write(f"**Source Quote:** \"{concept.source_quote}\"")
                        st.write(f"**Related Areas:** {', '.join(concept.related_roadmap_areas)}")
                        st.write(f"**Suggested Action:** {concept.suggested_action}")
            
            # Tensions
            if assessment.new_tensions:
                st.subheader("New Tensions")
                for tension in assessment.new_tensions:
                    severity_color = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}.get(tension.severity, "⚪")
                    with st.expander(f"{severity_color} {tension.tension}"):
                        st.write(f"**Severity:** {tension.severity}")
                        st.write(f"**Source Quote:** \"{tension.source_quote}\"")
                        st.write(f"**Conflicts With:** {tension.conflicts_with}")
                        st.write(f"**Resolution Needed:** {'Yes' if tension.resolution_needed else 'No'}")
                        if tension.suggested_resolution:
                            st.write(f"**Suggested Resolution:** {tension.suggested_resolution}")
            
            # Contradictions
            if assessment.contradictions:
                st.subheader("Contradictions")
                for contradiction in assessment.contradictions:
                    with st.expander(f"⚠️ {contradiction.statement[:60]}..."):
                        st.write(f"**Statement:** {contradiction.statement}")
                        st.write(f"**Source Quote:** \"{contradiction.source_quote}\"")
                        st.write(f"**Contradicts:** {contradiction.contradicts}")
                        st.write(f"**Severity:** {contradiction.severity}")
                        st.write(f"**Which is Correct:** {contradiction.which_is_correct}")
            
            # Roadmap impacts
            if assessment.roadmap_impacts:
                st.subheader("Roadmap Impacts")
                for impact in assessment.roadmap_impacts:
                    urgency_color = {"immediate": "🔴", "next_update": "🟡", "future": "🟢"}.get(impact.urgency, "⚪")
                    st.write(f"{urgency_color} **[{impact.impact_type}]** {impact.description}")
            
            # Questions generated
            if assessment.new_questions_generated:
                st.subheader(f"Questions Generated ({len(assessment.new_questions_generated)})")
                for q in assessment.new_questions_generated:
                    st.write(f"• [{q['audience']}] {q['question']}")
            
            # Recommendation
            st.markdown("---")
            st.subheader("Recommendation")
            
            rec_color = {
                "ingest_and_update": "🔴",
                "ingest_only": "🟡",
                "skip": "🟢",
                "archive": "⚪"
            }.get(assessment.recommendation, "⚪")
            
            st.write(f"{rec_color} **{assessment.recommendation.replace('_', ' ').title()}**")
            st.write(assessment.recommendation_rationale)
            
            # Action buttons
            st.markdown("---")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                if st.button("✅ Ingest & Update Roadmap", type="primary"):
                    with st.spinner("Ingesting and regenerating roadmap..."):
                        result = ingest_assessed_document(assessment.id, regenerate_roadmap=True)
                    st.success(f"Ingested {result['chunks_created']} chunks and regenerated roadmap!")
                    del st.session_state.current_assessment
                    st.experimental_rerun()
            
            with col2:
                if st.button("📥 Ingest Only"):
                    with st.spinner("Ingesting document..."):
                        result = ingest_assessed_document(assessment.id, regenerate_roadmap=False)
                    st.success(f"Ingested {result['chunks_created']} chunks!")
                    del st.session_state.current_assessment
                    st.experimental_rerun()
            
            with col3:
                if st.button("⏭️ Skip"):
                    skip_assessed_document(assessment.id)
                    st.info("Document skipped")
                    del st.session_state.current_assessment
                    st.experimental_rerun()
            
            with col4:
                if st.button("📁 Archive"):
                    result = archive_assessed_document(assessment.id)
                    st.info(f"Document archived to {result['archived_to']}")
                    del st.session_state.current_assessment
                    st.experimental_rerun()
    
    with tab2:
        st.subheader("Assessment History")
        
        all_assessments = load_all_assessments()
        
        # Filters
        col1, col2 = st.columns(2)
        with col1:
            status_filter = st.selectbox("Status", ["All", "Pending", "Actioned"])
        with col2:
            impact_filter = st.selectbox("Impact Level", ["All", "High", "Medium", "Low"])
        
        # Apply filters
        filtered = all_assessments
        if status_filter == "Pending":
            filtered = [a for a in filtered if not a.action_taken]
        elif status_filter == "Actioned":
            filtered = [a for a in filtered if a.action_taken]
        
        if impact_filter != "All":
            filtered = [a for a in filtered if a.impact_level == impact_filter.lower()]
        
        # Sort by date
        filtered = sorted(filtered, key=lambda x: x.assessed_at, reverse=True)
        
        st.write(f"**{len(filtered)} assessments**")
        
        for assessment in filtered:
            impact_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(assessment.impact_level, "⚪")
            status_icon = "✅" if assessment.action_taken else "⏳"
            
            with st.expander(f"{status_icon} {impact_icon} {assessment.document_name} ({assessment.assessed_at[:10]})"):
                st.write(f"**ID:** {assessment.id}")
                st.write(f"**Lens:** {assessment.lens}")
                st.write(f"**Impact:** {assessment.impact_level} ({assessment.impact_score:.2f})")
                st.write(f"**Summary:** {assessment.document_summary}")
                st.write(f"**Novel Concepts:** {len(assessment.novel_concepts)}")
                st.write(f"**Tensions:** {len(assessment.new_tensions)}")
                st.write(f"**Recommendation:** {assessment.recommendation}")
                
                if assessment.action_taken:
                    st.write(f"**Action Taken:** {assessment.action_taken} at {assessment.action_at[:10]}")
                    if assessment.user_notes:
                        st.write(f"**Notes:** {assessment.user_notes}")
```

---

## Storage

### File Structure

```
data/
├── assessments/
│   ├── assessments.json           # All assessments
│   └── archive/                   # Archived raw assessments
└── ...

materials/
├── archive/                       # Archived documents (not ingested)
│   └── ...
└── ...
```

### assessments.json

```json
{
  "assessments": [
    {
      "id": "assess_20250115143000",
      "document_path": "temp/quarterly_review.md",
      "document_name": "quarterly_review.md",
      "lens": "team-conversational",
      "assessed_at": "2025-01-15T14:30:00Z",
      "document_tokens": 3500,
      "document_summary": "Quarterly review meeting notes discussing...",
      "novel_concepts": [...],
      "new_tensions": [...],
      "impact_level": "high",
      "impact_score": 0.78,
      "recommendation": "ingest_and_update",
      "action_taken": "ingested",
      "action_at": "2025-01-15T14:35:00Z"
    }
  ],
  "metadata": {
    "total_assessed": 45,
    "total_ingested": 32,
    "total_skipped": 10,
    "total_archived": 3
  }
}
```

---

## Implementation Order

1. **Data models** (15 min)
   - ImpactAssessment dataclass
   - Supporting dataclasses
   - Storage functions

2. **Assessment prompt** (20 min)
   - Create detailed prompt
   - Define output schema

3. **Assessment function** (30 min)
   - Load document
   - Find similar chunks
   - Call Claude
   - Parse response

4. **Action functions** (20 min)
   - ingest_assessed_document
   - skip_assessed_document
   - archive_assessed_document

5. **CLI commands** (25 min)
   - assess command
   - assessments list command
   - Display functions

6. **Streamlit page** (35 min)
   - Upload and assess tab
   - Assessment history tab
   - Action buttons

7. **Testing** (20 min)
   - Test with various document types
   - Verify novelty detection
   - Test action flow

---

## Success Criteria

- [ ] Documents can be uploaded for assessment
- [ ] Assessment identifies novel concepts with exact quotes
- [ ] Assessment identifies tensions and contradictions
- [ ] Impact level (high/medium/low) is accurate
- [ ] Recommendation matches impact analysis
- [ ] User can accept or override recommendation
- [ ] Ingested documents flow into normal chunking/indexing
- [ ] Questions generated flow into Open Questions
- [ ] Assessment history is maintained
- [ ] Archived documents are properly stored
