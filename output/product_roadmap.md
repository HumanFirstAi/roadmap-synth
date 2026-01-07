# Zuora Product Roadmap
## Product Management Edition

---

## Strategic Context

Zuora is building toward a unified commerce platform that enables customers to grow from self-serve beginnings ($50M ARR) to complex enterprise needs ($1B+) without system replacement. This roadmap organizes around three pillars: **Commerce Foundation** (the platform services that enable omni-channel), **CPQ Excellence** (returning to Magic Quadrant leadership), and **Experience Layer** (customer-facing capabilities for rapid deployment). The core strategic bet is becoming the "vendor for life"—customers who start with Zuora should never need to leave, regardless of how their business model evolves.

**Key strategic tension to understand:** Silver Lake's mandate emphasizes B2B complex NOAM, but 60% of EMEA business and long-term growth require serving the lighter end of the spectrum. This roadmap attempts to balance both, but you'll need to defend prioritization decisions that may feel like they neglect one segment.

---

## Priorities & Rationale

### NOW (0-3 months): Committed Delivery

---

#### CPQ X Stability & Performance
**Timeline:** Q1 2025 | **Effort:** M (Medium - 4-6 weeks ongoing)

**User Value**
Sales reps using our Salesforce-native CPQ can trust the system during critical deal cycles. Deal Desk teams experience fewer errors and timeouts when processing complex quotes. This protects revenue on existing enterprise accounts who depend on CPQ X daily.

**Business Value**
- Protects existing ARR from at-risk enterprise accounts
- Maintains credibility with Boone's sales leadership team
- Bridges to Next Gen CPQ without customer disruption

**Success Metrics**
- Primary: Reduce CPQ-related support escalations by 30%
- Secondary: Quote generation time < 10 seconds for standard deals
- Validation: Zero major incidents during quarter

**Dependencies**
- Requires: Continued Salesforce sync reliability
- Blocks: Nothing (but failure here damages Next Gen CPQ credibility)

**Assumptions & Risks**
- Assumes: Salesforce platform stability continues
- Risks: Engineering time here competes with Next Gen CPQ investment

**Stakeholder Talking Points**
- "We're not abandoning current customers while building the future"
- "Stability investment protects our largest accounts"

---

#### Next Gen CPQ MVP
**Timeline:** Q1 2025 | **Effort:** L (Large - 8-12 weeks)

**User Value**
Sales teams closing enterprise deals with 100+ line items can finally complete quotes without system timeouts. Reps get a modern, responsive interface that doesn't require Salesforce expertise. Deal Desk gains visibility into quote status and approval workflows.

**Business Value**
- Enables enterprise deals that currently fail due to quote size
- Foundation for Magic Quadrant return (analyst-visible milestone)
- Removes Salesforce dependency for strategic flexibility

**Success Metrics**
- Primary: Successfully process quotes with 500+ line items
- Secondary: 50% reduction in quote generation time vs. CPQ X
- Validation: 3 lighthouse customers in beta by end of quarter

**Dependencies**
- Requires: Catalog Bundles (hard/soft) must be available
- Blocks: Configurator, Deal Room, and all downstream CPQ features

**Assumptions & Risks**
- Assumes: Architecture decisions on pricing service are finalized
- Risks: Timeline is aggressive based on engineering conversations—build in buffer for customer communications

**Stakeholder Talking Points**
- "This is the foundation for everything CPQ—can't accelerate other features without it"
- "Salesforce-free architecture enables future AI capabilities"

---

#### Catalog Bundles (Hard & Soft)
**Timeline:** Q1 2025 | **Effort:** M (Medium - 4-6 weeks)

**User Value**
Product Marketing can create and manage bundles without engineering tickets. Customers see logically grouped products (e.g., "Starter Package") rather than individual SKUs. Sales reps configure deals faster with pre-validated combinations.

**Business Value**
- Reduces time-to-market for new offers from weeks to days
- Enables competitive bundling strategies
- Foundation for configurator and guided selling

**Success Metrics**
- Primary: Bundle creation time < 30 minutes (self-serve by PM/PMM)
- Secondary: 10+ bundles created by end of quarter
- Validation: No engineering escalations for bundle changes

**Dependencies**
- Requires: None (foundational)
- Blocks: CPQ Configurator, Rules Engine consolidation

**Assumptions & Risks**
- Assumes: Current catalog architecture can support bundle complexity
- Risks: Rules for bundle validation may conflict with CPQ rules

**Stakeholder Talking Points**
- "This unlocks agility for competitive response"
- "Marketing owns their destiny without engineering bottlenecks"

---

#### Business Context Service (BCS) Phase 1
**Timeline:** Q1 2025 | **Effort:** M (Medium - 6 weeks)

**User Value**
Customers visiting self-serve experiences automatically see the right products, pricing, and currency based on their location and context. No more "select your region" dropdowns or pricing mismatches. Sales reps picking up a self-serve lead see full context of what the prospect already explored.

**Business Value**
- Foundation for omni-channel (the "vendor for life" vision)
- Reduces friction in self-serve purchase flow
- Enables personalization without custom development

**Success Metrics**
- Primary: Context detection accuracy > 95% (location, channel, customer type)
- Secondary: Context preserved across session handoffs
- Validation: Demo-ready for internal stakeholders

**Dependencies**
- Requires: Catalog API availability
- Blocks: Orchestration, Rules Engine integration, Omni-channel demo

**Assumptions & Risks**
- Assumes: Ownership question (Acquisition vs. Platform) gets resolved
- Risks: Scope creep—start narrow (location, channel, customer type only)

**Stakeholder Talking Points**
- "This is the brain that makes omni-channel possible"
- "Without context, we can't hand off from self-serve to sales"

---

#### Experiences Platform Selection (Plasmic)
**Timeline:** Q1 2025 | **Effort:** S (Small - contract/decision)

**User Value**
Implementation teams can build customer-facing experiences (checkout, account management, portals) in weeks instead of months. Pro-code and low-code options mean the right tool for each use case.

**Business Value**
- Unblocks entire experience roadmap
- Reduces implementation cost (the EMEA blocker)
- Enables reference architecture development

**Success Metrics**
- Primary: Contract signed, architecture approved
- Secondary: First pilot experience in development
- Validation: Engineering sign-off on integration approach

**Dependencies**
- Requires: Architecture review with Nav's team
- Blocks: Experience Templates, My Account unification, CPQ Light

**Assumptions & Risks**
- Assumes: Plasmic meets technical requirements after evaluation
- Risks: Contract negotiation delays cascade to all experience work

**Stakeholder Talking Points**
- "This decision unlocks 6+ months of roadmap"
- "Low-code reduces dependency on implementation services"

---

### NEXT (3-6 months): High Priority with Direction

---

#### Next Gen CPQ Configurator
**Timeline:** Q2 2025 | **Effort:** L (Large - 8-10 weeks)

**User Value**
Sales reps configure complex product combinations with guided workflows that prevent invalid configurations. Rules surface compatible options, required add-ons, and pricing implications in real-time. Deal Desk reviews pre-validated deals rather than catching errors after the fact.

**Business Value**
- Reduces quote errors by 40%+ (current estimate based on Deal Desk data)
- Faster deal cycles—configuration happens once, correctly
- Competitive parity with Salesforce Revenue Cloud configurator

**Success Metrics**
- Primary: Quote error rate reduced by 40%
- Secondary: Average configuration time reduced by 30%
- Validation: 5 enterprise customers using configurator in production

**Dependencies**
- Requires: Next Gen CPQ MVP, Catalog Bundles, Rules Engine decisions
- Blocks: CPQ Magic Quadrant submission, AI-assisted quoting

**Assumptions & Risks**
- Assumes: Rules Engine consolidation decision is made (otherwise we build on unstable foundation)
- Risks: Complex configuration rules require deep catalog integration

**Stakeholder Talking Points**
- "Configurator is table stakes for Magic Quadrant"
- "This is where CPQ pays for itself in reduced errors"

---

#### Rules Engine Consolidation
**Timeline:** Q2 2025 | **Effort:** XL (Extra Large - 12+ weeks, platform investment)

**User Value**
Business logic (pricing rules, eligibility, discounting, bundling) works consistently whether the customer is in self-serve checkout, sales-assisted CPQ, or partner portal. One rule change propagates everywhere automatically.

**Business Value**
- Engineering efficiency: one engine instead of four partial implementations
- Fewer bugs from inconsistent behavior across channels
- Foundation for true omni-channel (cannot have different rules in different places)

**Success Metrics**
- Primary: Single rules engine serving CPQ, Catalog, and Pricing
- Secondary: Rule change propagation time < 1 hour across all systems
- Validation: No "rules conflicts" bugs in quarter following launch

**Dependencies**
- Requires: Architectural decision on ownership (Nav's team)
- Blocks: Orchestration, CPQ Light, Omni-channel demo

**Assumptions & Risks**
- Assumes: Executive decision on who owns rules engine (currently fragmented)
- Risks: This is the highest-risk item—without consolidation, omni-channel vision fails

**Stakeholder Talking Points**
- "We cannot have customers seeing different prices in different channels"
- "This is infrastructure investment that enables everything else"

---

#### Deal Room v1
**Timeline:** Q2 2025 | **Effort:** M (Medium - 6 weeks)

**User Value**
Buyers receive interactive, professional proposals instead of PDF attachments. They can explore configurations, ask questions, and share internally. Sales reps see engagement analytics—who viewed what, for how long.

**Business Value**
- Competitive differentiation (ahead of most CPQ competitors)
- Faster deal cycles through buyer self-service
- Better win rates through professional presentation

**Success Metrics**
- Primary: 20% improvement in proposal-to-signature time
- Secondary: 50% buyer engagement with interactive proposals
- Validation: 10 deals closed through Deal Room

**Dependencies**
- Requires: Next Gen CPQ MVP
- Blocks: Advanced Deal Room features (multi-party, templates)

**Assumptions & Risks**
- Assumes: Buyers will engage with interactive proposals (validate with customer research)
- Risks: Security/compliance requirements from enterprise buyers

**Stakeholder Talking Points**
- "This is how modern B2B buying happens"
- "Engagement analytics help reps prioritize follow-up"

---

#### Basic Orchestration
**Timeline:** Q2 2025 | **Effort:** L (Large - 8 weeks)

**User Value**
Customers can complete simple purchases entirely self-serve—from product selection through checkout to provisioning. If they need help, context transfers seamlessly to sales. No more "please repeat your information."

**Business Value**
- Enables PLG motion (product-led growth)
- Reduces sales touch on simple deals, freeing reps for complex opportunities
- Foundation for expansion revenue (customers upgrade without sales involvement)

**Success Metrics**
- Primary: Self-serve purchase completion rate > 70%
- Secondary: Context preservation score > 95% on handoffs
- Validation: 100+ self-serve purchases processed

**Dependencies**
- Requires: BCS Phase 1, Experiences platform
- Blocks: Full omni-channel demo, CPQ Light

**Assumptions & Risks**
- Assumes: Customers want self-serve options (validate with customer research)
- Risks: Edge cases in flow coordination require extensive testing

**Stakeholder Talking Points**
- "PLG is how modern SaaS companies grow efficiently"
- "This lets sales focus on deals that need human touch"

---

#### Experience Templates (3-5 use cases)
**Timeline:** Q2 2025 | **Effort:** L (Large - 8-10 weeks)

**User Value**
Implementation teams start with proven templates for common use cases (SaaS signup, media subscription, usage billing) rather than blank canvas. Customers go live in weeks instead of months. Templates encode best practices from successful implementations.

**Business Value**
- Reduces implementation cost by 60%+ (the EMEA deal killer)
- Creates reference architecture for sales to demonstrate
- Accelerates time-to-value (customer sees ROI faster)

**Success Metrics**
- Primary: Implementation time reduced by 60% for templated use cases
- Secondary: 5+ customers deployed on templates
- Validation: Template NPS > 40 from implementation teams

**Dependencies**
- Requires: Plasmic contract signed, BCS for personalization
- Blocks: EMEA deal acceleration, reference architecture demos

**Assumptions & Risks**
- Assumes: Common patterns exist across customers (validate with GS)
- Risks: Templates become rigid; need extension points for customization

**Stakeholder Talking Points**
- "This is how we unlock EMEA growth"
- "Implementation cost is the objection we hear most—this addresses it directly"

---

### LATER (6-12 months): Strategic Bets

---

#### CPQ Magic Quadrant Readiness
**Timeline:** Q3-Q4 2025 | **Effort:** XL (Extra Large - ongoing)

**User Value**
Enterprise customers get full configurability, visualization, and workflow capabilities that compete with any CPQ on the market. Analysts validate our capabilities, giving buyers confidence in their selection.

**Business Value**
- Return to Gartner Magic Quadrant (visibility with enterprise buyers)
- Competitive positioning against Salesforce, PROS, Conga
- Validates strategic investment in CPQ

**Success Metrics**
- Primary: Gartner Magic Quadrant inclusion (Leader or Challenger quadrant)
- Secondary: Win rate improvement vs. named competitors
- Validation: Analyst briefing feedback is positive

**Dependencies**
- Requires: Configurator, Deal Room, full workflow capabilities
- Blocks: Nothing (this is a milestone, not a feature)

**Assumptions & Risks**
- Assumes: Feature parity timeline aligns with Gartner evaluation cycle
- Risks: Moving target—competitors are also investing heavily

**Stakeholder Talking Points**
- "Magic Quadrant is how enterprise buyers shortlist vendors"
- "Our finance integration is unique—analysts will recognize this"

---

#### Omni-Channel Demo-Ready
**Timeline:** Q3 2025 | **Effort:** L (Large - integration work)

**User Value**
Prospects see the "vendor for life" vision come to life: a customer starts self-serve, adds complexity, hands off to sales, gets a quote, signs, and provisions—all with full context preserved. This is the complete story.

**Business Value**
- Sales enablement for strategic positioning
- Validates platform investment
- Differentiates against Stripe (can't do complex) and Salesforce (can't do simple)

**Success Metrics**
- Primary: Demo works end-to-end without scripted workarounds
- Secondary: Sales team confidence score > 8/10
- Validation: Demo shown to 50+ prospects

**Dependencies**
- Requires: BCS, Orchestration, Experiences, CPQ Light—everything must work together
- Blocks: Full "vendor for life" go-to-market

**Assumptions & Risks**
- Assumes: All dependencies are delivered on time (high risk)
- Risks: Cross-team coordination is the hardest part—plan for integration time

**Stakeholder Talking Points**
- "This demo is the strategy made visible"
- "Warning: This requires all teams to deliver—coordination risk is real"

---

#### Pricing Engine Separation
**Timeline:** Q3-Q4 2025 | **Effort:** XL (Extra Large - platform refactoring)

**User Value**
Pricing calls return in < 100ms across all channels. Customers see real-time pricing updates during configuration. Self-serve checkout doesn't wait 3 seconds for price calculations.

**Business Value**
- Enables omni-channel at scale (current pricing is too slow)
- Reduces infrastructure cost (pricing calls are expensive today)
- Foundation for dynamic/personalized pricing

**Success Metrics**
- Primary: Pricing API response time < 100ms (p99)
- Secondary: Infrastructure cost reduced by 30%
- Validation: Load testing at 10x current volume

**Dependencies**
- Requires: Nav's architectural authority, dedicated platform team
- Blocks: Scalable omni-channel, AI pricing optimization

**Assumptions & Risks**
- Assumes: Can separate pricing from billing rating without business logic loss
- Risks: This is deep platform work—underestimate at your peril

**Stakeholder Talking Points**
- "Slow pricing kills self-serve conversion"
- "This is infrastructure debt we must address for scale"

---

#### CPQ Light via Experiences
**Timeline:** Q4 2025 | **Effort:** L (Large - 8-10 weeks)

**User Value**
SMB and mid-market customers get quoting capabilities without full CPQ complexity. Sales reps at smaller accounts can generate professional quotes. Implementation is days, not weeks.

**Business Value**
- TAM expansion into segments currently underserved
- EMEA unlock (60% of business that isn't B2B complex)
- Competitive response to Stripe, DealHub at lower price points

**Success Metrics**
- Primary: 50+ CPQ Light customers in first quarter
- Secondary: Implementation time < 5 days
- Validation: CAC payback < 12 months for CPQ Light customers

**Dependencies**
- Requires: Rules Engine consolidation, BCS, Experience Templates
- Blocks: Full segment coverage, competitive positioning at low end

**Assumptions & Risks**
- Assumes: CPQ capabilities can be meaningfully abstracted (not just "less features")
- Risks: "Light" customers may want features that pull toward complexity

**Stakeholder Talking Points**
- "This is how we compete with Stripe—they can't do what we do, but we can do what they do"
- "Light doesn't mean worse—it means right-sized"

---

#### AI-Assisted Quoting
**Timeline:** Q4 2025 | **Effort:** L (Large - 8-10 weeks)

**User Value**
Sales reps get intelligent recommendations for optimal deal structure. Goal-seek functionality suggests configurations that hit target margins or price points. Historical data surfaces successful patterns from similar deals.

**Business Value**
- Competitive differentiation (becoming table stakes per analysts)
- Margin improvement through optimized deal structures
- Rep productivity improvement

**Success Metrics**
- Primary: 10% improvement in average deal margin
- Secondary: Rep time-to-quote reduced by 25%
- Validation: Rep satisfaction score > 8/10 with AI suggestions

**Dependencies**
- Requires: Next Gen CPQ foundation, historical deal data pipeline
- Blocks: Full autonomous quoting (future)

**Assumptions & Risks**
- Assumes: Sufficient historical deal data for meaningful ML
- Risks: AI suggestions that lose deals will destroy trust quickly

**Stakeholder Talking Points**
- "AI is how we help reps sell better, not replace them"
- "Our finance integration means AI has better data than competitors"

---

### FUTURE (12+ months): Long-term Vision

---

#### Full Platform Composability
**Timeline:** 2026+ | **Effort:** XL (ongoing platform investment)

**User Value**
Customers build exactly what they need by combining capabilities. Any feature accessible from any touchpoint. Extension and customization without forking.

**Business Value**
- Platform premium pricing
- Reduced churn (hard to leave a composable platform)
- Partner ecosystem enablement

---

#### Agentic Commerce
**Timeline:** 2026+ | **Effort:** XL (R&D investment)

**User Value**
AI agents can configure, price, quote, and negotiate autonomously. Complex buyer scenarios handled without human involvement.

**Business Value**
- Market leadership in AI-native commerce
- Dramatic efficiency gains
- New business models (AI-to-AI commerce)

---

#### Unified Contract Object
**Timeline:** 2026+ | **Effort:** XL (cross-team coordination)

**User Value**
Single contract representation across CPQ, Billing, and Revenue. Complete lifecycle visibility from quote through renewal.

**Business Value**
- Reduced errors from data inconsistency
- Enables comprehensive analytics
- Foundation for intelligent renewals

---

## Sequencing & Dependencies

### Critical Path

```
Path A (CPQ Excellence):
Catalog Bundles → Next Gen CPQ MVP → Configurator → Magic Quadrant

Path B (Omni-Channel Foundation):
BCS Phase 1 → Rules Engine → Orchestration → Omni-Channel Demo

Path C (Experience Layer):
Plasmic Contract → Experience Templates → CPQ Light
```

### Parallel Work Streams

These can run simultaneously:
- **CPQ X Stability** runs parallel to Next Gen CPQ development
- **Catalog Bundles** runs parallel to BCS Phase 1
- **Deal Room** can start once Next Gen CPQ MVP is stable

### Blocking Relationships

| Blocker | What It Blocks | Risk Level |
|---------|---------------|------------|
| **Rules Engine ownership decision** | All rules consolidation work | 🔴 Critical |
| **Plasmic contract** | All experience layer work | 🟡 High |
| **BCS Phase 1** | Orchestration, omni-channel demo | 🟡 High |
| **Next Gen CPQ MVP** | Configurator, Deal Room, AI quoting | 🟡 High |
| **Catalog Bundles** | Configurator | 🟢 Medium |

### External Dependencies

- **Salesforce sync stability**: CPQ X depends on this continuing to work
- **Plasmic contract negotiation**: Blocking all experience work
- **Gartner evaluation cycle**: Timing matters for Magic Quadrant submission

---

## Success Criteria

### Quarterly Health Metrics

| Metric | Q1 Target | Q2 Target | Q3 Target |
|--------|-----------|-----------|-----------|
| CPQ-related support escalations | -20% | -30% | -40% |
| Quote generation time (p95) | < 15s | < 10s | < 5s |
| Self-serve purchase completion | N/A | 50% | 70% |
| Implementation time (templated) | Baseline | -30% | -60% |
| Omni-channel demo readiness | N/A | 50% | 100% |

### Validation Milestones

**Q1 2025**
- [ ] Next Gen CPQ processing 500+ line quotes in beta
- [ ] 3 lighthouse customers on Next Gen CPQ
- [ ] Plasmic contract signed
- [ ] BCS detecting context accurately in staging

**Q2 2025**
- [ ] Configurator reducing quote errors by 40%
- [ ] 5+ customers using experience templates
- [ ] Basic self-serve purchase flow working end-to-end
- [ ] Rules engine ownership decided and resourced

**Q3 2025**
- [ ] Omni-channel demo working without workarounds
- [ ] CPQ Magic Quadrant submission prepared
- [ ] CPQ Light MVP in customer hands

---

## Stakeholder Talking Points

### For Executive Leadership

**The strategic narrative:**
"We're building the only platform that serves customers from $50M to $1B+ without system replacement. This quarter, we're laying the foundation: Next Gen CPQ handles enterprise scale, BCS enables context preservation, and experience templates unlock implementation velocity."

**Defending B2B complex focus:**
"Silver Lake mandate is B2B complex, but we're not ignoring Stage 1/2 customers—BCS and experience templates are how we serve them efficiently. CPQ Light in Q4 completes the picture."

**On timeline risk:**
"Cross-team dependencies are our biggest risk. We're investing in the intersection layer specifically to reduce coordination overhead long-term."

### For Sales Leadership

**What to tell customers today:**
"Next Gen CPQ is coming—if you're hitting scale limits on CPQ X, you'll see relief in Q2. If you need simpler deployment, templates are coming Q2."

**EMEA-specific:**
"Reference architecture with templates is our answer to implementation cost objections. We're targeting 60% reduction in deployment time."

**Competitive positioning:**
"Stripe can't do complex. Salesforce can't do simple. We're building both on a single platform."

### For Engineering Partners

**On intersection ownership:**
"We're advocating for explicit ownership of BCS, rules, and orchestration. Until that's decided, expect coordination overhead."

**On Rules Engine:**
"Decision needed within 30 days. Currently four partial implementations—consolidation is required for omni-channel."

**On Pricing Engine:**
"Separation is on the roadmap for Q3/Q4. Nav's team needs dedicated resources."

### Common Objections & Responses

**"Why are we maintaining CPQ X while building Next Gen?"**
We can't disrupt existing enterprise customers. CPQ X maintenance is minimal—just stability. Explicit sunset date is 18 months after Next Gen parity.

**"Why isn't self-serve higher priority?"**
BCS and orchestration ARE the self-serve foundation. We're building infrastructure first, then the experience layer composes on it.

**"When can EMEA sell against Stripe?"**
CPQ Light in Q4 2025 is the direct answer. Until then, sell on our finance integration and complexity handling—our actual differentiation.

**"Is May SKO demo commitment realistic?"**
Risky. Requires all dependencies to hit. Recommend building demo with explicit "preview" positioning and fallback plan.

---

## Key Decisions Needed

| Decision | Owner | Deadline | Impact if Delayed |
|----------|-------|----------|-------------------|
| Intersection team ownership | Shakir/Pete | Feb 2025 | Platform services remain unowned |
| Rules engine consolidation | Architecture board | Feb 2025 | Fragmentation accelerates |
| CPQ X sunset date | CPQ leadership | Mar 2025 | Investment ambiguity continues |
| Stage 1/2 product owner | Jonathan | Mar 2025 | EMEA revenue leak continues |
| May SKO demo commitment | Exec team | Mar 2025 | Sales enablement unclear |

---

*This roadmap reflects current understanding as of synthesis date. Dependencies and timelines should be validated with engineering leads before external commitment. The intersection layer remains the critical risk—without ownership and resourcing, the omni-channel vision cannot be realized.*