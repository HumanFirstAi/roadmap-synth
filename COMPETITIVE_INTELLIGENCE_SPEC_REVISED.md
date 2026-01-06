# Competitive Intelligence Assessment Specification (Revised)

## Critical Framing

**You are an industry analyst**, not a strategist. Your job is to objectively assess how a competitor development impacts an existing roadmap. 

### Core Principles

1. **The roadmap is the source of truth** — It represents what is being built, not being built, and when
2. **No novel concepts** — Claude NEVER suggests new features, technologies, or approaches not in the roadmap
3. **No strategy creation** — Claude assesses impact, does not create strategy or make recommendations
4. **Analyst objectivity** — Written as an industry analyst would write a research note
5. **Grounded in evidence** — All assessments cite specific roadmap items or analyst research

### What This Is

An **analyst research note** that answers:
- How does this competitor development impact the roadmap as it currently exists?
- Which roadmap items help defend against this?
- Which roadmap items are now more/less relevant?
- What gaps exist in the current roadmap relative to this development?
- What questions does this raise for decision-makers?

### What This Is NOT

- A strategy document
- A recommendation for new features
- A proposal for roadmap changes
- A creative exercise in competitive response

---

## Analyst Persona

```
You are a senior industry analyst at a research firm covering this market. 

You have been asked to write an objective assessment of how a competitor's 
recent development impacts a company's published roadmap.

Your assessment must:
- Be grounded in the roadmap as it exists (no suggestions for changes)
- Reference specific roadmap items by name
- Use analyst research for market context
- Maintain objectivity (you are not an employee, you are an analyst)
- Identify what the roadmap addresses and what it doesn't
- Raise questions without answering them

Your assessment must NOT:
- Suggest new features or capabilities
- Recommend roadmap changes
- Propose novel technical approaches
- Create strategy (that's for the company to decide)
- Speculate beyond what's in the roadmap and analyst research
```

---

## Data Model

### CompetitorDevelopment

```python
@dataclass
class CompetitorDevelopment:
    id: str                              # comp_001
    competitor: str                      # "Competitor X"
    development_type: str                # product_launch, feature, acquisition, partnership, funding, strategy_shift
    title: str                           # "Competitor X launches AI-powered pricing"
    description: str                     # Full description of the development
    source_url: str                      # Where this was announced/reported
    announced_date: str                  # When announced
    created_at: str                      # When added to system
```

### AnalystAssessment

```python
@dataclass
class AnalystAssessment:
    id: str                              # analysis_001
    development_id: str                  # Links to CompetitorDevelopment
    assessed_at: str                     # Timestamp
    
    # Context used
    roadmap_version: str                 # Which roadmap version was assessed
    analyst_docs_used: list[str]         # Which analyst docs provided context
    
    # Executive summary
    headline: str                        # One-line analyst headline
    executive_summary: str               # 3-5 sentence summary
    
    # Market context (from analyst research)
    market_context: MarketContext
    
    # Impact assessment
    overall_impact: str                  # significant, moderate, minimal, none
    impact_timeline: str                 # immediate, near_term, medium_term, long_term
    confidence: str                      # high, medium, low
    
    # Roadmap analysis (grounded in existing roadmap only)
    roadmap_strengths: list[RoadmapStrength]    # Items that address this
    roadmap_gaps: list[RoadmapGap]              # Gaps relative to this development
    roadmap_timing: list[TimingAssessment]      # Timing implications
    
    # Competitive position
    competitive_position_assessment: str  # Narrative on where company stands
    customer_segment_implications: list[SegmentImplication]
    
    # Questions raised (not answers)
    strategic_questions: list[StrategicQuestion]
    
    # Analyst conclusion
    analyst_conclusion: str              # Objective conclusion
```

### MarketContext

```python
@dataclass
class MarketContext:
    relevant_trends: list[str]           # From analyst research
    market_direction: str                # Where market is heading
    customer_expectations: str           # What customers expect
    competitive_landscape: str           # Current competitive dynamics
    analyst_quotes: list[str]            # Direct quotes from analyst research
```

### RoadmapStrength

```python
@dataclass
class RoadmapStrength:
    roadmap_item: str                    # Exact name from roadmap
    horizon: str                         # now, next, later, future
    how_it_addresses: str                # How this item addresses the threat
    coverage_level: str                  # full, partial, tangential
    timing_adequacy: str                 # ahead, on_pace, behind, unclear
    source_quote: str                    # Quote from roadmap describing this item
```

### RoadmapGap

```python
@dataclass
class RoadmapGap:
    gap_description: str                 # What the gap is
    severity: str                        # critical, significant, moderate, minor
    competitor_capability: str           # What competitor has
    roadmap_coverage: str                # What roadmap says (or doesn't say) about this
    is_acknowledged: bool                # Is this gap acknowledged in roadmap?
    relevant_roadmap_items: list[str]    # Related items that partially address
    analyst_perspective: str             # What analyst research says about importance
```

### TimingAssessment

```python
@dataclass
class TimingAssessment:
    roadmap_item: str                    # Item being assessed
    current_horizon: str                 # Where it sits in roadmap
    timing_implication: str              # more_urgent, less_relevant, unchanged, uncertain
    rationale: str                       # Why this timing implication
```

### SegmentImplication

```python
@dataclass
class SegmentImplication:
    segment: str                         # Customer segment
    implication: str                     # What this means for the segment
    roadmap_relevance: str               # How roadmap addresses this segment
    risk_level: str                      # high, medium, low
```

### StrategicQuestion

```python
@dataclass
class StrategicQuestion:
    question: str                        # The question raised
    question_type: str                   # timing, investment, priority, scope, positioning
    context: str                         # Why this question is raised
    relevant_roadmap_items: list[str]    # Roadmap items this relates to
    # NOTE: No suggested answer — that's for leadership to decide
```

---

## Assessment Prompt

```python
ANALYST_ASSESSMENT_PROMPT = """
You are a senior industry analyst at a research firm covering this market.

## Your Role

You have been asked to write an objective analyst assessment of how a competitor's development impacts a company's roadmap.

## CRITICAL CONSTRAINTS

1. **The roadmap is fixed** — You are assessing impact on the roadmap AS IT EXISTS
2. **No recommendations** — You do NOT suggest changes, new features, or strategy
3. **No novel concepts** — You do NOT introduce ideas not already in the roadmap
4. **Analyst objectivity** — You write as an external analyst, not an employee
5. **Evidence-based** — Every claim must reference a specific roadmap item or analyst research
6. **Questions, not answers** — You raise strategic questions but do not answer them

## What You MUST Do

- Reference specific roadmap items by name
- Quote or cite analyst research for market context
- Identify what the roadmap addresses and what it doesn't
- Assess timing implications for existing roadmap items
- Raise questions for decision-makers to consider

## What You MUST NOT Do

- Suggest new features or capabilities
- Recommend roadmap changes
- Propose technical approaches not in the roadmap
- Create strategy or action plans
- Speculate beyond the evidence

---

## ANALYST RESEARCH CONTEXT

Use this analyst research to understand market dynamics, customer expectations, and competitive landscape. Quote directly when relevant.

{analyst_documents}

---

## THE ROADMAP (Source of Truth)

This is what the company IS building. Your assessment must be grounded in this.

{roadmap_content}

---

## COMPETITOR DEVELOPMENT TO ASSESS

**Competitor:** {competitor}
**Development Type:** {development_type}
**Title:** {development_title}
**Announced:** {announced_date}

**Description:**
{development_description}

**Source:** {source_url}

---

## ASSESSMENT INSTRUCTIONS

### 1. Executive Summary

Write a headline (one line) and 3-5 sentence executive summary.

Format: "[IMPACT LEVEL]: [Headline]"
Example: "MODERATE IMPACT: Competitor X's AI pricing creates pressure on Catalog timeline"

### 2. Market Context

Using the analyst research provided, establish:
- Relevant market trends
- Where the market is heading
- What customers expect in this area
- Current competitive dynamics

**Include direct quotes from analyst research.**

### 3. Roadmap Strengths

Identify roadmap items that address this competitive development.

For EACH strength:
- Name the EXACT roadmap item
- State which horizon it's in (Now/Next/Later/Future)
- Explain how it addresses the threat
- Assess coverage level (full/partial/tangential)
- Assess timing adequacy (ahead/on_pace/behind/unclear)
- Quote the roadmap's description of this item

### 4. Roadmap Gaps

Identify gaps in the roadmap relative to this development.

For EACH gap:
- Describe what the gap is
- Assess severity (critical/significant/moderate/minor)
- State what the competitor has
- State what the roadmap says (or doesn't say) about this
- Note if the gap is acknowledged in the roadmap
- List any roadmap items that partially address this
- Include analyst perspective on the importance of this capability

**IMPORTANT:** You are identifying gaps, not recommending how to fill them.

### 5. Timing Assessment

For relevant roadmap items, assess timing implications:
- Is this item now more urgent given the competitive development?
- Is this item less relevant?
- Is timing unchanged?
- Is timing uncertain?

**IMPORTANT:** You are assessing implications, not recommending changes.

### 6. Customer Segment Implications

For relevant customer segments:
- What does this development mean for the segment?
- How does the current roadmap address this segment?
- What is the risk level?

### 7. Competitive Position Assessment

Write a narrative assessment of the competitive position:
- Where does the company stand relative to this development?
- What advantages exist based on the roadmap?
- What vulnerabilities exist based on the roadmap?

**Ground this in specific roadmap items and analyst research.**

### 8. Strategic Questions Raised

List questions that this development raises for decision-makers.

For EACH question:
- State the question clearly
- Categorize: timing, investment, priority, scope, positioning
- Explain why this question is raised
- Note relevant roadmap items

**CRITICAL: Do NOT suggest answers. These are questions for leadership.**

### 9. Analyst Conclusion

Write a 2-3 paragraph objective conclusion as an industry analyst would.

---

## OUTPUT FORMAT

Return JSON:

```json
{
  "headline": "IMPACT_LEVEL: One-line headline",
  "executive_summary": "3-5 sentence summary",
  
  "market_context": {
    "relevant_trends": ["Trend 1", "Trend 2"],
    "market_direction": "Where market is heading",
    "customer_expectations": "What customers expect",
    "competitive_landscape": "Current dynamics",
    "analyst_quotes": [
      "Direct quote from analyst research 1",
      "Direct quote from analyst research 2"
    ]
  },
  
  "overall_impact": "significant|moderate|minimal|none",
  "impact_timeline": "immediate|near_term|medium_term|long_term",
  "confidence": "high|medium|low",
  
  "roadmap_strengths": [
    {
      "roadmap_item": "Exact item name from roadmap",
      "horizon": "now|next|later|future",
      "how_it_addresses": "How this addresses the development",
      "coverage_level": "full|partial|tangential",
      "timing_adequacy": "ahead|on_pace|behind|unclear",
      "source_quote": "Quote from roadmap about this item"
    }
  ],
  
  "roadmap_gaps": [
    {
      "gap_description": "What the gap is",
      "severity": "critical|significant|moderate|minor",
      "competitor_capability": "What competitor has",
      "roadmap_coverage": "What roadmap says or doesn't say",
      "is_acknowledged": true|false,
      "relevant_roadmap_items": ["Items that partially address"],
      "analyst_perspective": "What analyst research says about importance"
    }
  ],
  
  "timing_assessments": [
    {
      "roadmap_item": "Item name",
      "current_horizon": "now|next|later|future",
      "timing_implication": "more_urgent|less_relevant|unchanged|uncertain",
      "rationale": "Why this implication"
    }
  ],
  
  "segment_implications": [
    {
      "segment": "Segment name",
      "implication": "What this means",
      "roadmap_relevance": "How roadmap addresses",
      "risk_level": "high|medium|low"
    }
  ],
  
  "competitive_position_assessment": "Narrative assessment grounded in roadmap and research",
  
  "strategic_questions": [
    {
      "question": "The question raised",
      "question_type": "timing|investment|priority|scope|positioning",
      "context": "Why this question is raised",
      "relevant_roadmap_items": ["Related items"]
    }
  ],
  
  "analyst_conclusion": "2-3 paragraph objective conclusion"
}
```

Now write your analyst assessment.
"""
```

---

## Implementation

### Assessment Function

```python
def generate_analyst_assessment(
    development: CompetitorDevelopment,
    use_opus: bool = True
) -> AnalystAssessment:
    """
    Generate an analyst assessment of competitor development against roadmap.
    
    This is an ASSESSMENT, not a strategy document.
    The roadmap is the source of truth.
    No novel concepts are introduced.
    """
    
    # 1. Load full analyst documents (the analytical lens)
    analyst_docs = load_analyst_documents()
    analyst_context = format_analyst_documents_for_assessment(analyst_docs)
    
    # 2. Load current roadmap (the source of truth)
    roadmap = load_latest_roadmap()
    roadmap_version = get_roadmap_version()
    
    # 3. Build prompt
    prompt = ANALYST_ASSESSMENT_PROMPT.format(
        analyst_documents=analyst_context,
        roadmap_content=roadmap,
        competitor=development.competitor,
        development_type=development.development_type,
        development_title=development.title,
        development_description=development.description,
        source_url=development.source_url,
        announced_date=development.announced_date
    )
    
    # 4. Call Claude
    model = "claude-opus-4-20250514" if use_opus else "claude-sonnet-4-20250514"
    
    response = client.messages.create(
        model=model,
        max_tokens=6000,
        messages=[{"role": "user", "content": prompt}]
    )
    
    # 5. Parse and validate response
    analysis = parse_analyst_response(response)
    
    # 6. Validate no novel concepts introduced
    validate_no_novel_concepts(analysis, roadmap)
    
    # 7. Build assessment object
    assessment = AnalystAssessment(
        id=f"analysis_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        development_id=development.id,
        assessed_at=datetime.now().isoformat(),
        roadmap_version=roadmap_version,
        analyst_docs_used=[d.path for d in analyst_docs],
        headline=analysis.get("headline", ""),
        executive_summary=analysis.get("executive_summary", ""),
        market_context=parse_market_context(analysis),
        overall_impact=analysis.get("overall_impact", "unknown"),
        impact_timeline=analysis.get("impact_timeline", "unknown"),
        confidence=analysis.get("confidence", "medium"),
        roadmap_strengths=parse_strengths(analysis),
        roadmap_gaps=parse_gaps(analysis),
        roadmap_timing=parse_timing(analysis),
        competitive_position_assessment=analysis.get("competitive_position_assessment", ""),
        customer_segment_implications=parse_segments(analysis),
        strategic_questions=parse_questions(analysis),
        analyst_conclusion=analysis.get("analyst_conclusion", "")
    )
    
    # 8. Save assessment
    save_analyst_assessment(assessment)
    
    # 9. Add strategic questions to Open Questions (as questions, not recommendations)
    add_strategic_questions_to_system(assessment.strategic_questions, development)
    
    return assessment


def validate_no_novel_concepts(analysis: dict, roadmap: str) -> None:
    """
    Validate that the analysis doesn't introduce concepts not in the roadmap.
    
    Raises warning if potential novel concepts detected.
    """
    
    # Extract all roadmap item names
    roadmap_items = extract_roadmap_item_names(roadmap)
    roadmap_lower = roadmap.lower()
    
    warnings = []
    
    # Check strengths reference real roadmap items
    for strength in analysis.get("roadmap_strengths", []):
        item = strength.get("roadmap_item", "")
        if item and item.lower() not in roadmap_lower:
            warnings.append(f"Strength references unknown roadmap item: {item}")
    
    # Check timing assessments reference real items
    for timing in analysis.get("timing_assessments", []):
        item = timing.get("roadmap_item", "")
        if item and item.lower() not in roadmap_lower:
            warnings.append(f"Timing assessment references unknown roadmap item: {item}")
    
    if warnings:
        print("⚠️ Validation warnings:")
        for w in warnings:
            print(f"  - {w}")


def add_strategic_questions_to_system(
    questions: list[StrategicQuestion],
    development: CompetitorDevelopment
) -> None:
    """
    Add strategic questions to Open Questions system.
    
    These are questions raised by the assessment, NOT recommendations.
    """
    
    formatted_questions = []
    
    for q in questions:
        formatted_questions.append({
            "id": f"q_competitive_{datetime.now().strftime('%Y%m%d%H%M%S')}_{len(formatted_questions)}",
            "question": q.question,
            "audience": "leadership",  # Strategic questions go to leadership
            "category": q.question_type,
            "priority": "high",  # Competitive questions are high priority
            "context": f"Raised by analyst assessment of: {development.competitor} - {development.title}. {q.context}",
            "source": f"competitive_analysis_{development.id}",
            "related_roadmap_items": q.relevant_roadmap_items,
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            # NOTE: No suggested answer - these are questions for leadership
        })
    
    if formatted_questions:
        existing = load_questions()
        save_questions(existing + formatted_questions)
```

---

## Output Format: Analyst Research Note

The output should read like an actual analyst research note:

```markdown
# Competitive Assessment: [Competitor] [Development]

**Date:** January 15, 2025
**Analyst:** [System-generated]
**Roadmap Version:** v2025-01-10

---

## SIGNIFICANT IMPACT: Competitor X's AI Pricing Creates Urgency for Catalog Timeline

**Executive Summary**

Competitor X's launch of AI-powered dynamic pricing represents a significant 
development in the market. Based on our assessment of [Company]'s current roadmap, 
the "Catalog GA" item in the Next horizon provides partial coverage of this 
capability, though timing may now be more critical. The roadmap's "Dynamic Pricing 
Engine" in the Later horizon would fully address this competitive move, but the 
current timeline suggests Competitor X will have 6-12 months of market advantage.

---

## Market Context

According to [Analyst Firm] research:

> "The shift toward AI-powered pricing is accelerating, with 67% of enterprises 
> indicating they will evaluate dynamic pricing solutions in the next 18 months."

The market is moving toward real-time, AI-driven pricing capabilities. Customer 
expectations are shifting from static price lists to dynamic, context-aware pricing.

---

## Roadmap Strengths

### Catalog GA (Next Horizon)
- **Coverage:** Partial
- **Timing:** On pace, but now more urgent
- **Assessment:** The Catalog GA item includes "enhanced pricing display" which 
  addresses basic requirements but does not include AI-driven recommendations.

*Roadmap states: "Catalog GA will enable real-time pricing display with 
customer-specific adjustments based on tier and volume."*

### Dynamic Pricing Engine (Later Horizon)
- **Coverage:** Full
- **Timing:** Behind (competitor has launched, this is 6-12 months out)
- **Assessment:** This item fully addresses the competitive capability but 
  current timeline creates a market gap.

*Roadmap states: "Dynamic Pricing Engine will leverage ML models to optimize 
pricing in real-time based on demand signals and competitive positioning."*

---

## Roadmap Gaps

### Gap: Real-time Competitive Price Monitoring
- **Severity:** Moderate
- **Competitor Capability:** Competitor X includes automated competitive price 
  tracking in their solution
- **Roadmap Coverage:** Not explicitly addressed in current roadmap
- **Analyst Perspective:** [Research firm] notes that "competitive price 
  awareness is becoming table stakes for enterprise pricing solutions"

### Gap: AI Model Explainability
- **Severity:** Minor
- **Competitor Capability:** Competitor X emphasizes "explainable AI" in their 
  pricing recommendations
- **Roadmap Coverage:** Dynamic Pricing Engine item does not mention explainability
- **Acknowledged:** No

---

## Timing Implications

| Roadmap Item | Current Horizon | Implication |
|--------------|-----------------|-------------|
| Catalog GA | Next | More urgent — foundational for pricing capabilities |
| Dynamic Pricing Engine | Later | Unchanged in scope, but timing may need evaluation |
| Experience Builder | Next | Unchanged — not directly related |

---

## Customer Segment Implications

### Enterprise Segment
- **Implication:** Enterprise customers evaluating pricing solutions may now 
  include Competitor X in their consideration set
- **Roadmap Relevance:** Dynamic Pricing Engine addresses this, but timing gap exists
- **Risk Level:** Medium

### Mid-Market Segment
- **Implication:** Less immediate impact — AI pricing may be perceived as 
  enterprise-focused initially
- **Roadmap Relevance:** Catalog GA meets current needs
- **Risk Level:** Low

---

## Strategic Questions Raised

This assessment raises the following questions for leadership consideration:

1. **Timing Question:** Given this competitive development, does the current 
   timeline for Dynamic Pricing Engine require re-evaluation?
   - *Relevant items: Dynamic Pricing Engine, Catalog GA*

2. **Investment Question:** What is the cost/benefit of accelerating pricing 
   capabilities vs. maintaining current roadmap sequence?
   - *Relevant items: Dynamic Pricing Engine*

3. **Positioning Question:** How should the company position against Competitor X's 
   AI pricing claims during the gap period?
   - *Relevant items: Catalog GA, Dynamic Pricing Engine*

**Note:** These questions are raised for leadership consideration. This assessment 
does not recommend specific answers.

---

## Analyst Conclusion

Competitor X's AI-powered pricing launch represents a significant market development 
that directly relates to [Company]'s roadmap. The current roadmap demonstrates 
awareness of the market direction — the Dynamic Pricing Engine in the Later horizon 
would fully address this capability.

The primary consideration is timing. The roadmap shows the capability is planned, 
but Competitor X's launch creates a 6-12 month window where they will have market 
positioning advantage. The Catalog GA item in the Next horizon provides partial 
coverage during this gap.

This assessment identifies what the roadmap addresses and where gaps exist relative 
to this specific competitive development. Strategic decisions about prioritization 
or timeline adjustments remain with company leadership.

---

*This assessment is based on the roadmap dated 2025-01-10 and analyst research 
from [sources]. It reflects an objective external analyst perspective and does 
not recommend strategic actions.*
```

---

## CLI Commands

```python
@app.command()
def competitor_assess(
    development_id: str = typer.Argument(..., help="Development ID to assess"),
    use_opus: bool = typer.Option(True, help="Use Opus for higher quality")
):
    """
    Generate analyst assessment of competitor development.
    
    This produces an objective analyst research note, not a strategy document.
    The roadmap is the source of truth.
    """
    
    console.print("[bold]Analyst Assessment[/bold]")
    console.print("[dim]Note: This is an objective assessment, not a strategy document[/dim]\n")
    
    # Load development
    development = load_competitor_development(development_id)
    
    console.print(f"Competitor: {development.competitor}")
    console.print(f"Development: {development.title}")
    
    # Load context
    analyst_docs = load_analyst_documents()
    console.print(f"\nAnalyst research context: {len(analyst_docs)} documents")
    
    roadmap = load_latest_roadmap()
    console.print(f"Roadmap: Using current version as source of truth")
    
    with console.status("Generating analyst assessment..."):
        assessment = generate_analyst_assessment(development, use_opus=use_opus)
    
    # Display
    display_analyst_assessment(assessment)
    
    # Note about questions
    console.print(f"\n[dim]{len(assessment.strategic_questions)} strategic questions added to Open Questions[/dim]")
    console.print("[dim]These are questions raised for leadership, not recommendations[/dim]")
```

---

## Streamlit Integration

Update the Streamlit page to reflect the analyst framing:

```python
elif page == "🎯 Competitive Intelligence":
    st.title("Competitive Intelligence")
    
    st.markdown("""
    ### Analyst Assessment Tool
    
    This tool generates **objective analyst assessments** of competitor developments 
    against your roadmap.
    
    **Important:** This produces analyst research notes, not strategy recommendations.
    - The roadmap is the source of truth
    - No new features or approaches are suggested
    - Questions are raised for leadership, not answered
    """)
    
    # ... rest of implementation
```

---

## Success Criteria

- [ ] Roadmap is treated as source of truth
- [ ] No novel concepts introduced by Claude
- [ ] All roadmap items referenced are real items from the roadmap
- [ ] Analyst research is quoted/cited for market context
- [ ] Gaps identified, not filled with suggestions
- [ ] Questions raised, not answered
- [ ] Output reads like professional analyst research note
- [ ] Strategic questions flow to Open Questions (without recommendations)
