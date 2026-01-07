# Zuora Product Roadmap: Synthesis & Validation Report

## Executive Summary

Teams across Zuora are building toward a unified commerce platform that enables customers to grow from self-serve beginnings to complex enterprise needs without ripping out and replacing systems. The roadmap organizes around three strategic themes: **Commerce Foundation** (the architectural "intersection" that enables omni-channel), **CPQ Evolution** (from current state to Magic Quadrant-ready), and **Experience Layer** (customer-facing capabilities that compose on the foundation).

**Overall Assessment: Partially Aligned, with Significant Execution Risk**

The organization has strong conceptual alignment on the "vendor for life" vision, but faces real tensions between:
- Strategic ambition vs. engineering capacity
- B2B complex NOAM priority vs. 60% of EMEA business that isn't B2B complex
- Platform investment vs. immediate customer commitments
- Architectural purity vs. startup-mode execution speed

The intersection concept—owning where products connect—is the right strategic move, but no one currently owns it with authority and resources. This is the critical gap.

---

## Strategic Themes

### Theme 1: Commerce Foundation (The Intersection)

**Customer Outcome:** Any Zuora customer can move between self-serve and sales-assisted motions without context loss, system changes, or implementation rework.

**Competitive Advantage:** This is the "vendor for life" moat—customers who start with Zuora at $50M can grow to $1B+ without ripping out systems. Stripe can't do this; Salesforce requires painful migrations.

**OKR Connection:** Platform composability, customer retention through growth stages, expansion revenue

**Contributing Teams:** Acquisition (BCS, orchestration), Catalog (products, bundles, rules), Experiences (UI layer), CPQ (quoting capabilities), Engineering/Architecture (Nav's platform services)

**Key Components:**
- Business Context Service (BCS) - the "brain" that knows who/what/where/why/when
- Rules Engine - unified business logic across all touchpoints
- Orchestration Layer - coordinates flows and actions
- Pricing Engine - separated from rating, fast and universal
- Context preservation - handoff from self-serve to sales-assisted without starting over

---

### Theme 2: CPQ Excellence

**Customer Outcome:** Sales teams can close complex B2B deals faster with fewer errors, while Deal Desk maintains governance and profitability.

**Competitive Advantage:** Return to Magic Quadrant. Differentiated by finance system integration (downstream impact visibility) and support for complex ramp deals, amendments, and multi-subscription scenarios.

**OKR Connection:** B2B complex SaaS priority (Silver Lake mandate), deal velocity, win rates

**Contributing Teams:** CPQ (Manfred), Catalog (bundles/configurator), Engineering (Next Gen CPQ)

**Key Components:**
- CPQ X maintenance (current Salesforce-native, needs "lick of paint")
- Next Gen CPQ (off-Salesforce, scalable, AI-compatible architecture)
- Configurator integration with Catalog
- Vibe Quoting (lightweight/viral entry point - separate from core roadmap)

---

### Theme 3: Experience Layer

**Customer Outcome:** Customers can deploy self-serve and sales-assisted experiences quickly without heavy implementation, using templates and low-code tools.

**Competitive Advantage:** Reduces implementation cost/time (the GS problem), enables faster time-to-value, supports the "reference architecture" that EMEA desperately needs.

**OKR Connection:** Implementation velocity, customer satisfaction, EMEA revenue unlock

**Contributing Teams:** Experiences (plasmic, portals, My Account), Acquisition (context, orchestration)

**Key Components:**
- Plasmic-based experience builder (low-code/pro-code flexibility)
- Template library by vertical/use case
- My Account / Subscriber Portal unification
- CPQ Light (abstracted CPQ consumed through experiences layer)

---

## Synthesized Roadmap

### NOW (0-3 months): Committed Delivery

| Item | Description | Customer Value | Business Impact | Owner | Dependencies | Source |
|------|-------------|----------------|-----------------|-------|--------------|--------|
| **CPQ X Stability** | Performance improvements, bug fixes for current Salesforce CPQ | Existing customers can trust the system for complex deals | Protects existing revenue, Boone's requirement | CPQ (Manfred) | None | Team-structured, Sales-conversational |
| **Next Gen CPQ MVP** | Core quoting flows off Salesforce with basic catalog integration | Large quote handling (>100 lines) without performance degradation | Enables enterprise deals that currently fail | CPQ (Manfred) | Catalog bundles | Team-structured, Engineering |
| **Catalog Bundles (Hard/Soft)** | Configurable and pre-configured bundle support in catalog | Marketing creates bundles without engineering | Reduces time-to-market for new offers | Catalog (Errol) | None | Team-structured, Team-conversational |
| **BCS Phase 1** | Basic context detection (location, channel, customer type) | Right pricing/products shown automatically | Enables omni-channel foundation | Acquisition | Catalog API | Team-structured, Engineering |
| **Experiences Platform Selection** | Complete Plasmic evaluation and contract | Foundation for all future experience work | Unblocks experience roadmap | Experiences (Jimmy) | Architecture review | Team-conversational |

---

### NEXT (3-6 months): High Priority with Direction

| Item | Description | Customer Value | Business Impact | Owner | Dependencies | Source |
|------|-------------|----------------|-----------------|-------|--------------|--------|
| **Next Gen CPQ Configurator** | Product configuration with catalog rules | Sales configures complex deals correctly the first time | Reduces quote errors, faster deal cycles | CPQ (Manfred) | Catalog rules engine | Team-structured |
| **Rules Engine Consolidation** | Single rules engine serving CPQ, Catalog, and Pricing | Consistent behavior across all touchpoints | Engineering efficiency, fewer bugs | Platform (Nav) | Architectural decision | Engineering, Team-conversational |
| **Deal Room v1** | Collaborative quote presentation for customers | Professional, interactive proposal experience | Competitive differentiation, faster signatures | CPQ (Manfred) | Next Gen CPQ | Team-structured |
| **Basic Orchestration** | Flow coordination for simple self-serve journeys | Customer can complete purchase without sales involvement | PLG motion enabled | Acquisition | BCS, Experiences | Team-conversational |
| **Experience Templates** | 3-5 templates for common use cases (SaaS, media) | Faster implementation, lower GS cost | EMEA deal unlock, reference architecture | Experiences | Plasmic contract | Team-conversational |

---

### LATER (6-12 months): Strategic Bets

| Item | Description | Customer Value | Business Impact | Owner | Dependencies | Source |
|------|-------------|----------------|-----------------|-------|--------------|--------|
| **CPQ Magic Quadrant Readiness** | Full configurability, visualization, competitive feature parity | Enterprise-grade CPQ for complex manufacturing/B2B | Analyst positioning, competitive wins | CPQ (Manfred) | All CPQ dependencies | Team-structured, External-analyst |
| **Omni-Channel Demo-Ready** | End-to-end self-serve to sales-assisted flow | "Vendor for life" story becomes real and demonstrable | Sales enablement, market positioning | Intersection (Jonathan/Nav) | BCS, Orchestration, Experiences, CPQ Light | Your-voice |
| **Pricing Engine Separation** | Dedicated pricing service, separated from billing rating | Sub-100ms pricing calls across all channels | Performance unlock, platform foundation | Platform (Nav) | Architectural authority | Engineering |
| **CPQ Light via Experiences** | Abstracted CPQ capabilities accessible through experience layer | SMB customers get quoting without full CPQ complexity | TAM expansion, EMEA unlock | Experiences + CPQ | Rules engine, BCS | Team-conversational |
| **AI-Assisted Quoting** | Goal-seek optimization, intelligent recommendations | Reps get optimal deal structure faster | Competitive differentiation | CPQ (Manfred) | Next Gen CPQ foundation | Team-structured |

---

### FUTURE (12+ months): Long-term Vision

| Item | Description | Customer Value | Business Impact | Owner | Dependencies | Source |
|------|-------------|----------------|-----------------|-------|--------------|--------|
| **Full Platform Composability** | Any capability usable from any touchpoint | Build exactly what you need, extend infinitely | Platform premium, reduced churn | Platform | All foundation complete | Your-voice |
| **Agentic Commerce** | AI agents that can configure, price, and quote autonomously | Buyer self-service for complex scenarios | Market leadership, efficiency gains | TBD | AI foundation, full platform | External-analyst |
| **Unified Contract Object** | Single contract representation across CPQ, Billing, Revenue | Complete lifecycle visibility | Reduces errors, enables analytics | Platform | Cross-team alignment | Team-conversational |

---

## Dependency Map

```
┌─────────────────────────────────────────────────────────────────┐
│                    STRATEGIC VISION                              │
│              "Vendor for Life" / Omni-Channel                    │
└─────────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
    ┌─────────────────┐ ┌─────────────┐ ┌─────────────────┐
    │   EXPERIENCES   │ │    CPQ      │ │    CATALOG      │
    │   (Templates,   │ │  (Next Gen, │ │   (Bundles,     │
    │    Portals)     │ │   CPQ X)    │ │    Rules)       │
    └────────┬────────┘ └──────┬──────┘ └────────┬────────┘
             │                 │                  │
             └────────┬────────┴────────┬─────────┘
                      │                 │
                      ▼                 ▼
    ┌─────────────────────────────────────────────────────────────┐
    │                    INTERSECTION LAYER                        │
    │  ┌─────────┐ ┌─────────────┐ ┌───────────┐ ┌─────────────┐  │
    │  │   BCS   │ │Rules Engine │ │Orchestrat.│ │Pricing Eng. │  │
    │  │(Context)│ │ (Universal) │ │  (Flows)  │ │ (Separated) │  │
    │  └─────────┘ └─────────────┘ └───────────┘ └─────────────┘  │
    └─────────────────────────────────────────────────────────────┘
                              │
                              ▼
    ┌─────────────────────────────────────────────────────────────┐
    │              CORE PLATFORM (BILLING, ORDERS, REVENUE)        │
    └─────────────────────────────────────────────────────────────┘
```

**Critical Path:**
1. Catalog Bundles → CPQ Configurator → CPQ Magic Quadrant
2. BCS Phase 1 → Rules Engine Consolidation → Orchestration → Omni-Channel
3. Plasmic → Experience Templates → CPQ Light

**Blocking Relationships:**
- Rules Engine ownership must be decided before consolidation can begin
- Pricing Engine separation requires Nav's authority and dedicated team
- CPQ Light requires both Rules Engine and Experiences foundation

**External Dependencies:**
- Plasmic contract (blocking experience roadmap)
- Salesforce sync stability (CPQ X depends on this continuing to work)

---

## Narrative vs. Documentation Analysis

### Gaps (Discussed but not documented)

| Gap | Source | Implication | Recommendation |
|-----|--------|-------------|----------------|
| **Intersection ownership** | Pervasive in conversational | No one has authority to deliver platform services | Create explicit "Intersection Team" with Nav + Jonathan ownership |
| **Reference architecture** | Paulo, EMEA discussions | EMEA losing deals due to implementation cost/time | Prioritize experience templates, document reference implementations |
| **CPQ X investment level** | Manfred, John discussions | Unclear how much maintenance vs. deprecation | Make explicit decision: maintain for 18 months, then sunset |
| **Pricing engine separation** | Nav architectural vision | Buried in engineering conversations, not in roadmap | Add to Later timeframe with explicit resourcing |
| **Rules engine consolidation** | Nav, Errol discussions | Multiple teams building rules logic independently | Escalate to architectural decision board |

### Mismatches (Docs say X, conversations reveal Y)

| Topic | Structured Position | Conversational Reality | Resolution |
|-------|--------------------|-----------------------|------------|
| **Vibe Quoting** | Part of CPQ roadmap | Teen running separately, Manfred excluded | Clarify: is this a playground experiment or roadmap item? |
| **BCS scope** | Acquisition team feature | Nav sees as platform service, Errol sees as catalog | Architectural decision needed on ownership |
| **Zephyr future** | Unified journey orchestration | Team unsure if Zephyr architecture fits needs | "Don't use the word Zephyr" - define outcome, then tool |
| **CPQ Next Gen timeline** | Aggressive dates in docs | Engineering conversations suggest significant work remains | Pressure-test timeline with delivery team |

### Hidden Priorities (Brief in docs, dominant in discussions)

| Topic | Doc Coverage | Discussion Time | Recommendation |
|-------|--------------|-----------------|----------------|
| **Data layer upstream** | Minimal | Significant (Shakir, Nav) | Add data strategy to platform roadmap |
| **Sales rep context** | Not documented | Multiple mentions of missing org chart, performance data | Include in BCS scope |
| **Order preview performance** | Not in roadmap | Nav identifies as "worst call" | Add to billing/platform backlog |

### Undocumented Concerns

| Concern | Source | Impact | Recommended Action |
|---------|--------|--------|-------------------|
| **Engineering capacity for intersection** | Nav | Can't deliver platform without dedicated team | Reallocation decision needed |
| **Tamil organizational dynamics** | Nav historical | May create execution friction | Jonathan air cover required |
| **Billing parity burden** | John/CPQ team | CPQ team spends significant time on billing sync | Quantify and address |
| **Four rating engines** | Engineering | No unified pricing service | Architectural consolidation |

---

## Vision Alignment Assessment

### Consensus Check ✓

**Strong Alignment:**
- "Vendor for life" concept has universal buy-in (Jonathan, Ken, Nav, sales leadership)
- Omni-channel as the target state is agreed
- Product teams should be "insulated" to deliver their roadmaps
- Intersection needs ownership (even if ownership isn't assigned yet)
- B2B complex SaaS is the priority (Silver Lake mandate understood)

**Confidence Level:** High that organizational intent is aligned. Medium confidence on execution alignment.

### Vision Gaps (In strategy, missing from roadmap)

| Gap | Strategy Source | Likely Reason | Severity | Recommendation |
|-----|-----------------|---------------|----------|----------------|
| **Data layer as strategic asset** | "Behavioral data, sales rep context, pre-quote information" | No clear owner, billing team focused elsewhere | **Significant** | Add explicit data strategy workstream |
| **$50M-$250M customer journey** | Core to "vendor for life" | NOAM focus on B2B complex, no one owns lighter segment | **Critical** | Define "Stage 1/Stage 2" product owner |
| **Platform shared services** | Nav's five-layer architecture | No organizational authority for intersection team | **Critical** | Exec decision on intersection ownership |
| **Reference implementation** | Implementation simplification | GS vs. Product tension, unclear ownership | **Significant** | Assign to Ken or Acquisition with GS partnership |

### Roadmap Risks (In roadmap, not connected to vision)

| Item | Concern | Severity | Recommendation |
|------|---------|----------|----------------|
| **Vibe Quoting** | Running as separate experiment, unclear strategic fit | **Minor** | Either integrate to roadmap or explicitly position as R&D |
| **CPQ X maintenance** | Significant ongoing investment in eventually-deprecated platform | **Significant** | Set explicit sunset date, minimize investment |
| **Team-specific rules implementations** | Each team building own rules logic | **Significant** | Consolidate before debt becomes unmanageable |

### Misalignment Summary

**Key Divergence: Product teams are building for B2B complex, but strategic vision requires self-serve capability**

The strategic vision describes a customer journey from $50M to $1B+, starting with simple self-serve and growing to complex enterprise. But:
- CPQ team is focused on complex (Next Gen CPQ, configurator, Deal Desk)
- Catalog team is focused on complex (bundles for enterprise scenarios)
- No product team owns the "light" end of the spectrum
- EMEA sales explicitly needs simpler deployment, but roadmap doesn't address it

**Root Cause:** Silver Lake mandate ("B2B complex NOAM") is being interpreted as "only B2B complex." The vision says we need both, but resource allocation says we're choosing complex.

**Recommended Resolution:**
1. Explicitly create "Stage 1/Stage 2" product owner (likely Acquisition team)
2. Define CPQ Light as real roadmap item, not just "use Experiences to abstract CPQ"
3. Fund reference architecture development with GS partnership
4. Use May SKO to commit to omni-channel demo, forcing cross-team delivery

---

## GTM Validation

### Sales Needs Analysis

| Need | Roadmap Coverage | Gap? | Priority |
|------|------------------|------|----------|
| **Close complex B2B deals faster** | Addressed (Next Gen CPQ, configurator) | No | High |
| **Magic Quadrant positioning** | Addressed (CPQ roadmap targets this) | Partial - timeline aggressive | High |
| **EMEA implementation cost reduction** | Partial (Experience templates) | Yes - needs reference architecture | High |
| **Self-serve to sales-assisted handoff** | Planned (BCS, orchestration) | Yes - 6+ months out | Medium |
| **Compete with Stripe at low end** | Not addressed | Yes - strategic gap | Medium |
| **Deal Room / collaborative quoting** | Addressed (Next Gen CPQ) | No | Medium |

### Competitive Position

**Current Strengths Being Reinforced:**
- Finance system integration (billing, rev rec visibility in quoting) ✓
- Complex B2B scenarios (ramps, amendments, multi-subscription) ✓
- Configurability for enterprise needs ✓

**Vulnerabilities Being Addressed:**
- Salesforce CPQ performance/scalability → Next Gen CPQ
- Implementation time/cost → Experience templates (partial)
- Quote volume handling → Next Gen CPQ architecture

**Vulnerabilities NOT Addressed:**
- Stripe competing at low end
- Salesforce Revenue Cloud threat
- Implementation cost for SMB

### GTM Recommendations

1. **Don't over-promise omni-channel for SKO** - Foundation won't be ready for demo-quality by May without significant execution acceleration

2. **Create EMEA-specific enablement** - Reference architecture + templates is the unlock; prioritize this for Paulo's 60% of business

3. **Position CPQ Light as "coming soon"** - Sales needs to know they can sell simpler customers today with path to light CPQ

4. **Quantify implementation cost reduction** - "4 weeks instead of 12 weeks" is the EMEA story; need proof points

---

## Market Validation

### Strategic Bet Validation

| Bet | Market Support | Confidence |
|-----|---------------|------------|
| **Unified commerce platform (omni-channel)** | Strong - Gartner emphasizes unified customer experience across journey | High |
| **API-first / modular architecture** | Strong - market moving to composable commerce | High |
| **CPQ Magic Quadrant return** | Mixed - competitive pressure increasing (Salesforce, PROS, Conga) | Medium |
| **Self-serve to sales-assisted spectrum** | Strong - recurring revenue models demand this | High |
| **AI-assisted quoting** | Strong - becoming table stakes per analysts | Medium |

### Market Gaps

**Opportunities We're Missing:**
- **Partner/channel enablement** - CPQ for resellers/distributors mentioned in analyst reports, not in our roadmap
- **Visual configuration** - Tacton leading in 3D/AR visualization; we have no capability
- **E-procurement integration (PunchOut)** - Mentioned as B2B differentiator, not on roadmap

**Competitor Moves to Watch:**
- **Salesforce Revenue Cloud** - Rebuilding CPQ from ground up; timeline matters
- **Stripe** - Bundling billing + PSP at lower price points; EMEA losing deals to this
- **DealHub, Subskribe** - Fast-moving challengers for mid-market SaaS

### Big Wins

**Where We're Ahead:**
- **Finance integration** - "Zuora CPQ is loved not only by sales teams but also by CFOs" - this is genuine differentiation
- **Complex agreement handling** - Multi-line, ramp, amendment support is mature
- **Subscription/recurring revenue DNA** - Deep domain expertise competitors lack

**How Roadmap Extends Advantage:**
- Next Gen CPQ maintains finance integration while improving UX
- Intersection layer makes finance integration accessible to lighter use cases

### End State Assessment

**Market Direction:** Gartner and Forrester both point toward unified, composable commerce platforms that span the full customer lifecycle. Digital-first, API-first, AI-augmented.

**Our Positioning for That Future:**
- Architecturally, the intersection vision is exactly right
- Execution timeline puts us 12-18 months behind where we should be
- Risk: Salesforce or Stripe builds this faster and we become "just billing"

**Timeline Concerns:**
- 6-month window Nav describes is real - aggregation happening in market
- CPQ Magic Quadrant cycle matters for competitive positioning
- EMEA revenue leak continues every quarter without reference architecture

---

## Consensus & Fragmentation

### High Consensus (Aligned across sources)

| Topic | Confidence | Safe to Commit |
|-------|------------|----------------|
| Omni-channel is the vision | High | Yes - invest |
| Product roadmaps should be insulated | High | Yes - protect |
| Intersection needs ownership | High | Yes - decide ownership |
| B2B complex is Silver Lake priority | High | Yes - but not to exclusion of Stage 1/2 |
| Implementation cost is a blocker | High | Yes - prioritize templates/reference |

### Fragmented (Needs alignment discussion)

| Topic | Inconsistency | Stakeholders to Involve | Recommended Action |
|-------|---------------|------------------------|-------------------|
| **Who owns BCS** | Acquisition feature vs. platform service | Nav, Errol, Jonathan | Architectural decision board |
| **Rules engine consolidation** | Each team building own | Nav, Errol, Manfred, Ken | Exec decision on single engine |
| **Zephyr future** | Keep/rebuild/tear apart | Alan, Errol, Nav | Outcome-first: define need, then tool |
| **CPQ X investment level** | Maintain vs. deprecate vs. sunset | Manfred, John, Shakir | Explicit decision and communication |
| **Pricing engine ownership** | Billing vs. Platform | Nav, Ken, Shakir | Platform architectural decision |

---

## Risks & Assumptions

### Technical Risks

| Risk | Source | Mitigation |
|------|--------|------------|
| **Rules engine fragmentation accelerates** | Multiple teams building rules independently | Consolidation decision within 30 days |
| **Pricing engine performance blocks omni-channel** | Order preview is "worst call" per Nav | Prioritize pricing separation |
| **Next Gen CPQ timeline slips** | Conversational evidence of complexity | Buffer expectations, protect core delivery |
| **Salesforce sync reliability** | CPQ X depends on this | Invest in stability while Next Gen matures |

### Strategic Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| **Vision-roadmap gap on Stage 1/2** | Lose EMEA revenue, can't compete at low end | Assign owner, fund reference architecture |
| **Intersection remains unowned** | Platform never materializes | Exec decision on Jonathan/Nav authority |
| **Silver Lake interprets "B2B complex" too narrowly** | Roadmap optimizes for 40% of potential market | Quantify Stage 1/2 opportunity, make case for investment |

### Execution Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| **Cross-team coordination fails** | High | High | Intersection as own product motion with authority |
| **Key person dependency (Nav)** | Medium | Critical | Ensure architectural vision is documented and shared |
| **Large customer disruption (Twilio-style)** | High | High | "Strategy makes trade-offs visible" - explicit prioritization |
| **Plasmic contract delays** | Medium | Medium | Parallel-path experience architecture if needed |

### Key Assumptions

| Assumption | How to Validate |
|------------|-----------------|
| Intersection ownership can be established | Shakir/Pete decision within 30 days |
| Engineering capacity can be reallocated to platform | Quantify current allocation, identify reallocation source |
| Nav's 6-month timeline is achievable with right team | Validate with engineering staffing plan |
| Reference architecture reduces implementation time by 60%+ | Pilot with 3-5 customers, measure |
| CPQ Light via Experiences is technically feasible | Architecture review with Nav/Errol |

---

## Appendix: Source Lens Summary

| Lens | Key Insight | Weight in Synthesis |
|------|-------------|---------------------|
| **Your-Voice** | "Vendor for life" requires intersection ownership; two product motions (roadmap + intersection) | Vision validation |
| **Team-Structured (CPQ)** | Next Gen CPQ PRD is comprehensive; configurator, deal room, workflows defined | Heavy for CPQ items |
| **Team-Structured (Acquisition)** | BCS, context service architecture documented; phased approach | Heavy for intersection |
| **Team-Conversational** | Intersection unowned; rules fragmented; pricing engine problematic; Zephyr future unclear | Reality check |
| **Sales-Conversational** | EMEA needs reference architecture; implementation cost kills deals; self-serve + assist spectrum | GTM validation |
| **Engineering** | Nav's five-layer architecture; 6-month window; authority without influence doesn't work | Feasibility filter |
| **External-Analyst** | Unified customer experience; composable commerce; CPQ market competitive | Market validation |

---

## Recommended Executive Decisions

1. **Create Intersection Team** with Jonathan as product owner and Nav as technical lead, with explicit authority over platform services (BCS, rules, pricing, orchestration)

2. **Fund Stage 1/2 Product Owner** - assign dedicated PM to $50M-$250M customer journey, likely within Acquisition team

3. **Rules Engine Consolidation Decision** - single architectural decision on one rules engine within 30 days

4. **CPQ X Sunset Date** - explicit decision: maintain for 18 months, minimal investment, sunset when Next Gen CPQ reaches parity

5. **Reference Architecture Investment** - joint Product/GS initiative with Q2 2025 deliverable

6. **May SKO Commitment** - decide now whether to commit to omni-channel demo; if yes, staff accordingly

---

*This roadmap was synthesized from team-structured documentation, team conversations, sales feedback, engineering input, and external analyst perspectives. The vision (your-voice) was used to validate alignment, not to drive prioritization. Where sources conflicted, conversational evidence was given priority over documentation, with engineering veto power on feasibility.*