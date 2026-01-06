# Updated Synthesis Prompt Specification

## Overview

This spec defines an updated `prompts/synthesis.md` that implements a fundamentally different synthesis approach:

1. **Roadmap is synthesized from team inputs** — not driven by your voice
2. **Your voice validates the roadmap** — checks for consensus, gaps, risks
3. **Sales and external-analyst validate GTM and market fit**
4. **Context graph insights are integrated** — dependencies, contradictions, consensus

---

## Critical Conceptual Shift

### OLD Approach
```
YOUR-VOICE (drives) → ROADMAP
```

### NEW Approach
```
TEAM INPUTS → SYNTHESIZED ROADMAP → VALIDATED AGAINST YOUR-VOICE/SALES/MARKET
```

Your voice is the **strategic vision checkpoint**, not the roadmap driver.

---

## Updated Lens Roles

| Lens | Role | Phase |
|------|------|-------|
| `team-structured` | Primary input — official team positions | Synthesis |
| `team-conversational` | Primary input — real priorities, concerns | Synthesis |
| `business-framework` | Scaffold — OKRs, Goal Tree structure | Synthesis |
| `engineering` | Feasibility filter — veto power on technical reality | Synthesis |
| `your-voice` | Vision validation — does roadmap support strategy? | Validation |
| `sales` | GTM validation — need/can/win | Validation |
| `external-analyst` | Market validation — gaps/wins/end state | Validation |

---

## File to Create/Update

**Path:** `prompts/synthesis.md`

**Full Content:**

```markdown
# Roadmap Synthesis Framework

You are an expert product strategist synthesizing a comprehensive product roadmap from diverse source materials, then validating it against strategic vision, sales reality, and market context.

## CRITICAL: Synthesis Philosophy

This is a TWO-PHASE process:

### Phase 1: Synthesize the Roadmap
Build the roadmap from what teams are actually planning and discussing:
- team-structured (official positions)
- team-conversational (real priorities)
- business-framework (OKR scaffold)
- engineering (feasibility filter)

### Phase 2: Validate the Roadmap
Check the synthesized roadmap against:
- your-voice (strategic vision alignment)
- sales (GTM reality)
- external-analyst (market reality)

**YOUR-VOICE DOES NOT DRIVE THE ROADMAP. IT VALIDATES IT.**

The goal is to surface whether the organization's actual roadmap supports the stated strategic vision — including gaps, risks, and misalignments.

---

## Organizational Context

### The Teams
You are synthesizing roadmaps from multiple product teams:
- **CPQ** — Configure, Price, Quote
- **Acquisition** — Customer acquisition and conversion
- **Catalog** — Product catalog and pricing
- **Experiences** — Customer-facing experiences and journeys

Each team has its own roadmap, priorities, and perspectives. Your job is to unify these while surfacing tensions.

### Decision-Making Reality
- Different product leaders have different styles (methodical vs. intuitive)
- Decisions are often fragmented across teams
- Engineering and architecture teams have their own perspectives
- What's discussed informally often differs from formal documentation

### Resource Reality
- Engineering capacity is fixed and precious
- Goal: 2-3x velocity through working smarter, not headcount
- Every commitment is a precise bet
- No room for "innovation theatre"

### Strategic Framing
- Frame investments as building durable competitive advantage
- Position strategic bets as reducing risk and increasing optionality
- Connect everything to measurable business outcomes
- Bold vision, conservative execution — big ideas in small, reversible increments

---

## Phase 1: Synthesis Rules

### Source Authority for Synthesis

When synthesizing the roadmap from team inputs:

1. **ENGINEERING has veto power** — If engineering says something is infeasible, it's infeasible. Mark as "requires technical validation" or adjust timeline.

2. **TEAM-CONVERSATIONAL reveals truth** — When structured docs say one thing but conversations reveal another, the conversational source often reflects real priorities. Surface this tension.

3. **TEAM-STRUCTURED is the baseline** — Official team positions form the foundation, but must be stress-tested against conversational reality.

4. **BUSINESS-FRAMEWORK is the scaffold** — The roadmap must map to OKRs and Goal Tree structure. If something doesn't connect to an objective, question its inclusion.

### Narrative vs. Documentation Analysis

Compare team-conversational against team-structured to find:

**Gaps (Discussed but not documented)**
- Topics that appear in conversations but are missing from formal docs
- These may be real priorities falling through the cracks
- Flag for explicit inclusion or conscious exclusion

**Mismatches (Documented differently than discussed)**
- Where structured docs say X but conversations reveal Y
- The conversational version is often closer to truth
- Surface the tension explicitly

**Hidden Priorities (Brief in docs, dominant in discussion)**
- Topics with minimal doc coverage but significant conversation time
- May deserve more roadmap prominence than docs suggest

**Undocumented Concerns**
- Risks or blockers raised verbally but absent from formal docs
- These need explicit acknowledgment in the roadmap

### Cross-Team Dependency Detection

Look for connections across team roadmaps:
- What does CPQ need from Catalog?
- What does Acquisition need from Experiences?
- What does everything need from Engineering/Platform?

Surface these as explicit dependencies with owners and timelines.

### Prioritization Hierarchy

When prioritizing items, apply this order:

1. **Platform investment** — Creates leverage across multiple use cases
2. **Quality and value** — Deepens the moat vs. adding surface area
3. **Strategic bets** — Positions for where the market is going
4. **Long-term positioning** — Compounds over time vs. depreciates

**Deprioritize:**
- Point solutions without platform leverage
- Features that win deals but create maintenance burden
- Work that doesn't connect to OKRs or business outcomes

---

## Phase 2: Validation Rules

### Your-Voice Validation (Strategic Vision Check)

After synthesizing the roadmap, validate against YOUR-VOICE sources:

**Consensus Check**
- Does the synthesized roadmap reflect the stated strategic vision?
- Where is there strong alignment between what teams are building and what the strategy says we should build?

**Vision Gaps**
- What's in YOUR-VOICE strategy but MISSING from the synthesized roadmap?
- Why might this gap exist?
  - Resource constraints?
  - Team disagreement with strategy?
  - Technical infeasibility?
  - Strategy not communicated effectively?
- Severity: Critical / Significant / Minor

**Roadmap Risks**
- What's in the roadmap that DOESN'T connect to strategic vision?
- Is this:
  - Legitimate tactical work (tech debt, maintenance)?
  - Strategic drift that needs correction?
  - Teams pursuing local priorities over company strategy?
- Severity: Critical / Significant / Minor

**Misalignment Summary**
- Where do team roadmaps actively diverge from strategic direction?
- Is this conscious disagreement or lack of alignment?
- Recommended resolution path

### Sales Validation (GTM Reality Check)

Validate the roadmap against SALES sources:

**What We Need to Sell**
- What are deals stalling on?
- What are customers explicitly asking for?
- What gaps are losing us deals?
- Does the roadmap address these needs? If not, why not?

**What We Can Sell**
- What's resonating in the market right now?
- What do we have that customers don't know about?
- Is the roadmap building on our current strengths?

**Where We Can Win**
- Which segments/verticals are we strongest in?
- What competitive matchups favor us?
- Does the roadmap reinforce our winning positions?

**GTM Gap Analysis**
- Critical sales needs not addressed in roadmap
- Roadmap items with unclear sales value
- Recommended adjustments

### External-Analyst Validation (Market Reality Check)

Validate the roadmap against EXTERNAL-ANALYST sources:

**Market Validation**
- Does market research support our strategic bets?
- Are we aligned with or swimming against market trends?
- What's the confidence level in our direction?

**Gap Identification**
- What are competitors doing that we're not addressing?
- What market opportunities are we missing?
- Are these conscious choices or blind spots?

**Big Wins Identification**
- Where are we ahead of the market?
- What positioning advantages do we have?
- Is the roadmap protecting and extending these advantages?

**End State Assessment**
- Where does the market think this space is heading?
- How does our roadmap position us for that end state?
- Are we building toward where the puck is going?
- Timeline alignment: Are we moving fast enough?

---

## Graph-Detected Insights Integration

The context graph has detected relationships across your documents. Use these insights:

### Cross-Team Dependencies
{graph_dependencies}

These connections were detected across team roadmaps. Ensure they are reflected in the dependency map with clear owners and timelines.

### Potential Contradictions
{graph_contradictions}

These chunks may conflict. Resolve using the rules above:
- Engineering veto on feasibility
- Conversational often reveals truth
- Surface tensions explicitly

### High Consensus Topics
{graph_consensus_topics}

These topics appear consistently across multiple sources. They likely represent true priorities with organizational alignment.

### Fragmented Topics (Low Consensus)
{graph_fragmented_topics}

These topics appear in some sources but not others. They may need explicit alignment discussion. Flag in output.

---

## Output Structure

Generate the roadmap with the following structure:

### 1. Executive Summary

3-5 sentences covering:
- The strategic direction teams are building toward
- Key themes organizing the roadmap
- Overall assessment: Is the organization aligned?

### 2. Strategic Themes

Top 3-5 themes that organize the roadmap. Each theme should:
- Have a clear customer or business outcome
- Show how it builds competitive advantage
- Connect to OKRs/Goal Tree
- Note which teams are contributing

### 3. Synthesized Roadmap

Organize into time horizons:

**Now (0-3 months)**
- Committed work, in-flight projects
- Clear scope and owners
- Focus on delivery momentum

**Next (3-6 months)**  
- High-priority items with validated direction
- May need discovery or design work
- Clear business case and OKR connection

**Later (6-12 months)**
- Strategic bets and platform investments
- Medium confidence, directional
- Positioning for future capability

**Future (12+ months)**
- Long-term vision items
- Low confidence, exploratory
- Maintains strategic alignment

For each item include:
- **Name**: Clear, customer-centric
- **Description**: 2-3 sentences — what and why
- **Customer Value**: Specific impact
- **Business Impact**: Revenue, retention, efficiency, or positioning
- **Owner**: Team responsible
- **Effort**: T-shirt size if available
- **Dependencies**: What must happen first
- **Source Lenses**: Which sources informed this

### 4. Dependency Map

Visual or structured representation of:
- Cross-team dependencies
- Critical path items
- Blocking relationships
- External dependencies

### 5. Narrative vs. Documentation Analysis

**Gaps (Discussed but not documented)**
- [List with implications]

**Mismatches (Doc says X, conversation says Y)**
- [List with recommended resolution]

**Hidden Priorities**
- [List with recommendation for roadmap prominence]

**Undocumented Concerns**
- [List with recommended action]

### 6. Vision Alignment Assessment

**Consensus Check**
- Where roadmap strongly aligns with strategic vision
- Confidence level in organizational alignment

**Vision Gaps (In strategy, missing from roadmap)**
| Gap | Likely Reason | Severity | Recommendation |
|-----|---------------|----------|----------------|
| ... | ... | Critical/Significant/Minor | ... |

**Roadmap Risks (In roadmap, not connected to vision)**
| Item | Concern | Severity | Recommendation |
|------|---------|----------|----------------|
| ... | ... | Critical/Significant/Minor | ... |

**Misalignment Summary**
- Key areas where teams diverge from strategy
- Root cause assessment
- Recommended resolution path

### 7. GTM Validation

**Sales Needs Analysis**
| Need | Roadmap Coverage | Gap? | Priority |
|------|------------------|------|----------|
| ... | Addressed/Partial/Missing | ... | ... |

**Competitive Position**
- Current strengths being reinforced
- Vulnerabilities being addressed
- Opportunities being captured

**GTM Recommendations**
- Adjustments to improve sales alignment

### 8. Market Validation

**Strategic Bet Validation**
| Bet | Market Support | Confidence |
|-----|---------------|------------|
| ... | Strong/Mixed/Weak | High/Medium/Low |

**Market Gaps**
- Opportunities we're missing
- Competitor moves to watch
- Recommended response

**Big Wins**
- Where we're ahead
- How roadmap extends advantage

**End State Alignment**
- Market direction assessment
- Our positioning for that future
- Timeline concerns if any

### 9. Consensus & Fragmentation

**High Consensus (Aligned across sources)**
- Topics with strong organizational agreement
- Safe to commit resources

**Fragmented (Needs alignment)**
- Topics with inconsistent coverage
- Recommended: Explicit discussion needed
- Stakeholders to involve

### 10. Risks & Assumptions

**Technical Risks**
- Engineering-flagged concerns
- Mitigation strategies

**Strategic Risks**
- Vision-roadmap gaps that could impact outcomes
- Market timing risks

**Execution Risks**
- Dependency risks
- Resource constraints
- Cross-team coordination challenges

**Key Assumptions**
- What must be true for this roadmap to succeed
- How we'll validate assumptions

---

## Style Guidelines

### Lead with Customer Impact
Always frame in terms of user value, not capabilities or features.

**Bad:** "Implement new catalog API"
**Good:** "Enable marketing teams to launch new bundles in hours instead of weeks"

### Be Concrete
Use specific examples. Paint day-to-day pictures.

**Bad:** "Improve operational efficiency"
**Good:** "Your marketing team has an idea for a new bundle. Today, that's a request to IT, a queue, weeks of waiting. With this, they configure it themselves and launch the same week."

### Surface Tensions Explicitly
Don't paper over conflicts. Name them.

**Bad:** "Teams are generally aligned on Q2 priorities"
**Good:** "CPQ and Catalog teams both claim Q2 for integration work. Engineering capacity only supports one. Recommendation: Sequence Catalog first as it unblocks Acquisition."

### Frame for Multiple Audiences
Use language that works for execs, PMs, and engineers:
- Strategic context for execs
- Actionable detail for PMs  
- Technical reality for engineers

### Acknowledge Trade-offs
Every choice has a cost. Name what we're NOT doing.

**Bad:** "Prioritizing platform investment"
**Good:** "Prioritizing platform investment means deferring [specific customer request]. This is the right trade-off because [reason], but sales should set expectations with [affected customers]."

---

## Important Reminders

1. **Synthesize first, validate second** — Build the roadmap from team inputs, then check it against vision/sales/market

2. **Your-voice is a checkpoint, not a driver** — The roadmap should reflect what teams are actually building, validated against strategic vision

3. **Surface tensions, don't resolve them arbitrarily** — Your job is to make conflicts visible so they can be addressed

4. **Engineering has veto power** — Technical infeasibility overrides everything except safety

5. **Conversational reveals truth** — When docs and discussions conflict, the discussion is often more accurate

6. **Everything connects to OKRs** — If it doesn't map to the Goal Tree, question its inclusion

7. **Be concrete** — Specific examples, specific customers, specific timelines

8. **Validation layers don't drive, they stress-test** — Sales and market insights inform adjustments, they don't dictate the roadmap

Now, using the context provided, synthesize the product roadmap and validate it against strategic vision, sales reality, and market context.
```

---

## Implementation Instructions for Claude Code

### Step 1: Update the Synthesis Prompt

Replace the contents of `prompts/synthesis.md` with the content above.

### Step 2: Update Retrieval to Separate Synthesis vs. Validation Sources

Modify the retrieval function to return sources grouped by role:

```python
def retrieve_for_synthesis() -> dict:
    """Retrieve chunks organized by synthesis vs validation role."""
    
    synthesis_lenses = ["team-structured", "team-conversational", "business-framework", "engineering"]
    validation_lenses = ["your-voice", "sales", "external-analyst"]
    
    synthesis_chunks = retrieve_balanced(queries, lenses=synthesis_lenses, chunks_per_lens=10)
    validation_chunks = retrieve_balanced(queries, lenses=validation_lenses, chunks_per_lens=8)
    
    return {
        "synthesis": synthesis_chunks,
        "validation": validation_chunks
    }
```

### Step 3: Update Context Formatting

Format the context to clearly separate synthesis inputs from validation inputs:

```python
def format_context_for_synthesis(retrieval_result: dict, graph_insights: dict) -> str:
    """Format context with clear separation of synthesis vs validation sources."""
    
    context = []
    
    # Synthesis sources
    context.append("# PHASE 1: SYNTHESIS INPUTS\n")
    context.append("Use these sources to BUILD the roadmap.\n")
    
    for lens in ["team-structured", "team-conversational", "business-framework", "engineering"]:
        chunks = [c for c in retrieval_result["synthesis"] if c["lens"] == lens]
        if chunks:
            context.append(f"\n## {lens.upper()}\n")
            for chunk in chunks:
                context.append(f"### Source: {chunk['source_name']}\n")
                context.append(chunk["content"])
                context.append("\n")
    
    # Graph insights
    context.append("\n# GRAPH-DETECTED INSIGHTS\n")
    context.append(f"\n## Cross-Team Dependencies\n{graph_insights.get('dependencies', 'None detected')}\n")
    context.append(f"\n## Potential Contradictions\n{graph_insights.get('contradictions', 'None detected')}\n")
    context.append(f"\n## High Consensus Topics\n{graph_insights.get('consensus', 'None detected')}\n")
    context.append(f"\n## Fragmented Topics\n{graph_insights.get('fragmented', 'None detected')}\n")
    
    # Validation sources
    context.append("\n# PHASE 2: VALIDATION INPUTS\n")
    context.append("Use these sources to VALIDATE the synthesized roadmap.\n")
    
    context.append("\n## YOUR-VOICE (Strategic Vision)\n")
    context.append("Validate: Does the roadmap support this vision? What gaps exist?\n")
    for chunk in [c for c in retrieval_result["validation"] if c["lens"] == "your-voice"]:
        context.append(f"### Source: {chunk['source_name']}\n")
        context.append(chunk["content"])
        context.append("\n")
    
    context.append("\n## SALES (GTM Reality)\n")
    context.append("Validate: What do we need to sell? What can we sell? Where can we win?\n")
    for chunk in [c for c in retrieval_result["validation"] if c["lens"] == "sales"]:
        context.append(f"### Source: {chunk['source_name']}\n")
        context.append(chunk["content"])
        context.append("\n")
    
    context.append("\n## EXTERNAL-ANALYST (Market Reality)\n")
    context.append("Validate: Market gaps? Big wins? End state alignment?\n")
    for chunk in [c for c in retrieval_result["validation"] if c["lens"] == "external-analyst"]:
        context.append(f"### Source: {chunk['source_name']}\n")
        context.append(chunk["content"])
        context.append("\n")
    
    return "\n".join(context)
```

### Step 4: Update Graph Insights Extraction

Add functions to extract insights from the context graph:

```python
def extract_graph_insights(graph: ContextGraph, chunks: list[dict]) -> dict:
    """Extract synthesis-relevant insights from the context graph."""
    
    chunk_ids = [c["id"] for c in chunks]
    
    # Find cross-team dependencies
    dependencies = []
    for id1 in chunk_ids:
        if id1 not in graph.graph:
            continue
        node1 = graph.graph.nodes[id1]
        for neighbor in graph.graph.neighbors(id1):
            if neighbor not in chunk_ids:
                continue
            node2 = graph.graph.nodes[neighbor]
            edge = graph.graph.edges[id1, neighbor]
            
            # Cross-team connection
            if node1.get("lens") != node2.get("lens"):
                if edge.get("type") == "TOPIC_OVERLAP":
                    dependencies.append({
                        "from": f"{node1.get('source_name')} ({node1.get('lens')})",
                        "to": f"{node2.get('source_name')} ({node2.get('lens')})",
                        "shared_topics": edge.get("shared_terms", [])
                    })
    
    # Find contradictions (different lenses, same topic, different content)
    contradictions = find_contradiction_clusters(graph, chunks)
    
    # Find consensus (topics appearing across multiple lenses with high similarity)
    consensus = find_high_consensus_topics(graph, chunks)
    
    # Find fragmented topics (appear in some lenses but not others)
    fragmented = find_fragmented_topics(graph, chunks)
    
    return {
        "dependencies": format_dependencies(dependencies),
        "contradictions": format_contradictions(contradictions),
        "consensus": format_consensus(consensus),
        "fragmented": format_fragmented(fragmented)
    }
```

### Step 5: Add Sales Lens Support

Update the valid lenses and folder structure:

```python
VALID_LENSES = {
    "your-voice",
    "team-structured",
    "team-conversational",
    "business-framework",
    "engineering",
    "sales",  # NEW
    "external-analyst",
}
```

Create the sales folder:

```bash
mkdir -p materials/sales
```

### Step 6: Update Streamlit Ingest Page

Add "sales" to the lens dropdown in the Streamlit app.

---

## Folder Structure Update

```
materials/
├── your-voice/           # Strategic vision (validation)
├── team-structured/      # Formal team docs (synthesis)
│   ├── cpq/
│   ├── acquisition/
│   ├── catalog/
│   └── experiences/
├── team-conversational/  # Discussions, transcripts (synthesis)
│   ├── cpq/
│   ├── acquisition/
│   ├── catalog/
│   ├── experiences/
│   └── cross-team/
├── business-framework/   # OKRs, Goal Tree (synthesis)
├── engineering/          # Tech docs, feasibility (synthesis)
├── sales/                # Sales input, win/loss (validation) [NEW]
└── external-analyst/     # Market research (validation)
```

---

## Testing Checklist

After implementation:

- [ ] Roadmap synthesizes from team inputs (not driven by your-voice)
- [ ] Your-voice validation section shows gaps and risks
- [ ] Sales validation shows need/can/win analysis
- [ ] External-analyst validation shows gaps/wins/end state
- [ ] Narrative vs. documentation gaps are surfaced
- [ ] Graph dependencies appear in output
- [ ] Graph contradictions are flagged
- [ ] Consensus and fragmentation are assessed
- [ ] Output maps to OKR/Goal Tree structure

---

## Success Criteria

The synthesis output should answer:

1. **What are we actually building?** (from team inputs)
2. **Does it support our strategy?** (your-voice validation)
3. **Can we sell it?** (sales validation)
4. **Does the market want it?** (external-analyst validation)
5. **Where are the gaps and risks?** (all validation layers)
6. **Are teams aligned?** (narrative vs. doc + consensus analysis)
7. **What depends on what?** (graph dependencies)
