# Core Idea and Specs

# Product Architecture Specification: Agentic Vibe Quoting Platform

Oct 2025  
Navneet Jain

To start with, please note that there are few terms that are being used in development at this stage. The final name can be anything but Agentic Quoting \= Vibe Quoting is an integral part of the next gen CPQ solution and is not a separate component. Next Gen CPQ was originally conceived to be conversation, agentic, and at the same time, modular. Our goal is to deliver and enrich the capabilities of a CPQ without overwhelming the users. See the directional document here \- [Architectural Perspective for Next Gen of  CPQ: Thought Piece](https://docs.google.com/document/d/1OkDZZfgdfm04ZokxWSLjlRfqqpNajJ74sYyU3N_OW5w/edit?tab=t.0#heading=h.lye6wcnifvy)

This document talks about what Agentic Quoting is supposed to be. Nomenclature and taxonomy aside. 

[**Principles	2**](#principles)

[**Introduction	2**](#introduction)

[**Specs	3**](#specs)

[Functional Specs	3](#functional-specs)

[Technical Architecture and Flows (Evolving)	4](#technical-architecture-and-flows-\(evolving\))

[Authentication & Authorization	4](#authentication-&-authorization)

[**Capability View	5**](#capability-view)

[Invocation modes	5](#invocation-modes)

[Conversation \+ panel (dual mode)	6](#conversation-+-panel-\(dual-mode\))

[Proposal DSL (Sample)	6](#proposal-dsl-\(sample\))

[Deterministic pricing & goal‑seek	7](#deterministic-pricing-&-goal‑seek)

[Learning from history (suggestions, not decisions)	7](#learning-from-history-\(suggestions,-not-decisions\))

[Validation & governance	7](#validation-&-governance)

[Attachments to kickoff Quoting	8](#attachments-to-kickoff-quoting)

[Promote to CPQ & submit to Deal Desk	8](#promote-to-cpq-&-submit-to-deal-desk)

[**Model for brainstorming (Work in progress)	9**](#model-for-brainstorming-\(work-in-progress\))

# Principles {#principles}

- Modular \- a component outside current CPQ(X).   
- API first and headless.  
- Integrally independent \- can be integrated with any CRM or Ordering/Billing should there be a need. Has a DSL of its own.   
- Conversational: A large percentage of functions are achievable by conversation  
- Dual mode: Talk to it and touch it. The chat suggests and the panel lets you pin down details.  
- Separation of concerns: Exploration in Agentic/Vibe; governance by Deal Desk; system of record in CPQ/Billing/CRM.  
- Deterministic maths: LLMs never compute prices. A pricing engine does. LLMs propose and explain.

# Introduction {#introduction}

The strategic vision for the Agentic Vibe Quoting Platform is predicated on a fundamental architectural shift: to stop thinking of CPQ as a single, monolithic application and instead re-imagine it as a platform composed of distinct, integrated components, each purpose built for the job it needs to do (JTBD). The core thesis is the decoupling of the front-end seller experience from the back-end systems of decisioning and governance. This vision is realised through three architectural pillars, each designed to serve a specific persona and their unique job-to-be-done as articulated in the document I have linked above. 

To acknowledge \- the word agentic has come to be used a lot these days and often is associated with automation. For us, the term "Agentic" signifies a move beyond simple workflow automation to the active augmentation of human intelligence and decision making. This platform is not merely a tool for assembling quotes more efficiently; it is an active participant in the sales process, equipped with AI agents that provide predictive insights, intelligent recommendations, and conversational guidance.

![][image1]

# Specs {#specs}

The Agentic/Vibe Quoting Studio is the rep centric "fast lane" of the platform. Its singular purpose is to eliminate friction from the quoting process, allowing sales reps to build momentum and get accurate, professional proposals in front of customers as quickly as possible. It serves as an intuitive entry point for all deals, whether they are simple, high velocity transactions or the initial shaping of a complex, strategic engagement. 

The guiding design philosophy is to empower the rep, not to constrain them: "Don’t block; guide on demand". It is a companion to the formal CPQ system, designed for exploration, speed, and fluidity before a deal is committed to the official system of record.  

## Functional Specs {#functional-specs}

* **Kick Start the Quote:** The Sales rep is allowed to upload a presentation, excel sheet, a pdf \- any unstructured data that they have prepared with their customer and get going with the conversation interface (see next) from thereon. They can kick start the flow from CRM or directly enter the Agentic Vibe Quoting platform.   
* **Conversational Interface:** The core of the experience is a guided, QnA flow that constructs the quote. This "progressive disclosure" interface asks simple, context aware questions (e.g., "Who is the customer?", "What is the subscription term?") to build the quote structure, abstracting away the underlying complexity of the product catalogue and pricing rules.    
* **Template Driven Creation:** To accelerate common quoting scenarios, reps can initiate a new Vibe from a library of predefined templates. These templates can prepopulate customer information, product bundles, and commercial terms for specific deal types like "New Business \- Mid-Market" or "Enterprise Renewal".  
* **Real Time Preview:** A persistent, dynamic preview of the final order form is always visible on the screen. This panel updates in real-time as the rep makes selections, providing instant visual feedback and eliminating the need to generate a full PDF to see the impact of a change.    
* **AI Powered Recommendations:** The Intelligence Service proactively suggests relevant product bundles, upsells, and cross-sells directly within the interface. These recommendations are based on historical data of successful quotes, customer firmographics, and the current quote context, helping reps maximise deal value.  
* **Scenario Modelling:** Reps have the ability to create and compare multiple "what-if" scenarios within a single Vibe. This allows them to model different product configurations, discount levels, or payment terms and instantly see the impact on key deal metrics like Total Contract Value (TCV), Annual Contract Value (ACV), and Net Recurring Revenue (NRR).    
* **Predictive Deal Check:** A one click "Would this pass?" function provides an on demand reality check. This feature calls the **Intelligence Service** (more on this later), which uses a machine learning model to predict the likelihood of the current deal configuration passing the formal approval process. The response includes not just a probability score but also an explanation of the key contributing factors, providing actionable coaching to the rep.    
* **Ephemeral Data Model:** All data created within the Agentic Vibe Quoting Studio is ephemeral and seller owned. It exists as a lightweight "pre-quote" object and does not create any official artifacts in the downstream CPQ or billing systems. This low friction approach encourages exploration without polluting the system of record. A formal quote object is only created when the rep explicitly clicks "Promote to CPQ".  

## Technical Architecture and Flows (Evolving) {#technical-architecture-and-flows-(evolving)}

The Vibe Quoting Studio is architected as a modern, responsive web application that communicates with a dedicated set of backend microservices via the API Gateway.

* Frontend Technology: A contemporary single page application (SPA) framework, such as React or Vue.js, should be considered.Component driven nature of these tech can fit the dynamic and interactive user interface required, particularly for the real time preview panel and the conversational flow.  
* **API Interactions:** All communication from the frontend is directed exclusively to the API Gateway, which then routes requests to the appropriate microservices. The primary interactions are with the **Quoting Service** (to manage the state of the Vibe/pre-Quote object), the **Product Service** (for real time product and price lookups), and the **Intelligence Service** (to fetch recommendations and predictive checks).

### Authentication & Authorization {#authentication-&-authorization}

- Auth \- back and forth between CRM \<\> Agentic interface  
- Iframing the agentic interface 

Both the problems are being discussed and brainstormed in the document here: [NextGen CPQ - Integration with OneID](https://docs.google.com/document/d/1D8y-RCLCBya7tyuThV7INRO068B6l0n0-tnFfrVJoHc/edit?tab=t.0#heading=h.8sjlqbu0tdvq)

**Initiating a Agentic/Vibe Quoting Session**

**![][image2]**

**Promoting a Pre-Quote to CPQ** 

![][image3]

# Capability View {#capability-view}

## Invocation modes {#invocation-modes}

* **Standalone**: Launch Agentic/Vibe with SSO; choose account or create prospect; build quote.

* **Contextual from CRM (e.g. Salesforce Opportunity)**: “Open in Agentic/Vibe” deep links with context (account, stage, amount, contacts). On Promote, we create/update the CRM Quote/Opportunity artefacts.

##  Conversation \+ panel (dual mode) {#conversation-+-panel-(dual-mode)}

* Chat proposes bundles, ramps, discounts, terms; panel shows structured schema (the Proposal DSL) for precise edits and comparisons (scenarios/versions).  
* “Why?” is first‑class: every suggestion cites history and policy rationale with links.

## Proposal DSL (Sample) {#proposal-dsl-(sample)}

(Data model will be discussed separately.)  
A compact YAML/JSON dialect to represent a pre‑quote proposal (ephemeral until promotion).

**Goals**: Ideally it should be human readable, versionable, diffable, maps cleanly to CPQ quote lines later.

| proposal:   id: xyfsasd111   account\_ref: CRM:001xxyy123231   currency: USD   term\_months: 36   start\_date: 2025-11-01   scenarios:     \- key: baseline       items:         \- sku: ZUORA-PLATFORM           kind: recurring           uom: seat           qty: 250           price\_list: 120.00           discount: 0.15           \# 15%           ramps:             \- months: 12               qty: 200             \- months: 24               qty: 250           commitments:             min\_commit: 200             overage\_rate: 1.2         \- sku: ZUORA-ANALYTICS           kind: recurring           qty: 1           price\_list: 30000.00           billing: annual\_in\_advance       terms:         payment: net30         termination\_for\_convenience: false         auto\_renew: true   constraints:     target\_metric: ACV     target\_value: 275000   notes: Customer prefers annual billing. Competitive pressure from X. Budget bound $A to $B |
| :---- |

**Mapping to CPQ on promotion**

* scenario.key can be mapped to CPQ Quote Version (or a custom object?)  
* item can be mapped to Quote Line(s); ramps explode into intervalled lines.  
* commitments may need to be mapped to term/usage fields where supported otherwise pass through as proposal metadata to an extension object. 

## Deterministic pricing & goal‑seek {#deterministic-pricing-&-goal‑seek}

All totals, proration and ramps are calculated by Pricing Service. LLMs call price.quote or preview method with a Proposal DSL blob.

**We will also add/support item specific goal seek (solve one variable keeping others fixed) and ramp aware adjustments.**

(Specs: TBC)

## **Learning from history (suggestions, not decisions)** {#learning-from-history-(suggestions,-not-decisions)}

* Data: prior quotes (won/lost), approvals, cycle times, margin outcomes, redline themes.  
* Pipelines: upfront ingestion and learning followed by nightly ingestion into a History Service (plus a small online store).  
* Potential Techniques (as researched):  
  * KNN retrieval on semantic embeddings: “similar deals” list.  
  * Price bands per sku/segment/term using robust statistics (say P50 to P90).  
  * Propensity hints (which bundles/ramps **reduce approvals**) using gradient boosted trees on tabular features.  
* Guardrails: No auto pricing. Suggestions are annotated and clickable: “Apply”, “Explain”, “Ignore”.  
* Privacy: Anonymise customer identifiers in model features; tenancy isolation.

(This section is a work in progress but gives an overview of the objective at a high level.) 

## Validation & governance {#validation-&-governance}

* Local checks: schema, maths invariants, catalogue eligibility (read only), obvious constraints (e.g., discount ≤ 95%).  
* Policy simulation (may be in CPQ/Deal Desk?): margin thresholds, term limits, contractual flags, rev‑impact pre checks. Returns pass/fail with reasons and required approvers.  
* Promotion gate: must have zero blocking violations to promote.

![][image4]

## Attachments to kickoff Quoting {#attachments-to-kickoff-quoting}

User uploads PDFs/PowerPoints/Excels (RFPs, legacy orders).

![][image5]

## Promote to CPQ & submit to Deal Desk {#promote-to-cpq-&-submit-to-deal-desk}

* Promote: Create/update CPQ Quote \+ CRM linkage. Store the “Proposal snapshot” at promotion to CPQ (Proposal \+ priced total \+ Promotions \+ overrides).  
* Submit: Send to Deal Desk/DCC for formal approvals. On success, publish to Deal Room.

**Note that I am using DCC as I have referred to in the previous document. Please consider it as a placeholder and not a formal name of the module.** 

![][image6]

# Model for brainstorming (Work in progress) {#model-for-brainstorming-(work-in-progress)}

![][image7]

# Refinement and Additional Details

# Introduction and Background

As established, enterprise CPQ is still form driven, rule heavy and slow. Reps avoid it, Deal Desk becomes a bottleneck, approval trees and catalogue changes make the engine complicated and time consuming making buyers wait. Complexity explodes when discounts, ramps, commitments, multi currency, multi‑subscription and renewals show up together.

We flip the model from “validate everything by rules” to precedent driven quoting with learned guardrails. If your draft quote is statistically consistent with recently approved deals in the same cohort (segment × region × product family) and doesn’t violate any hard rules, it is **approved by design**. Exceptions rise with evidence. Rules still exist (plain‑English or JSON) for non-negotiables.

Our solution is to build a search first quoting app that assembles quotes by analogy to similar, successful deals, keeps calculations deterministic (pinned catalogue/price‑book snapshot, rounding, timezone), and exports a portable JSON contract so downstream CPQ/Billing can execute without loss.

This document considers a minimum shippable product. In ≤ 60 seconds, a rep moves from natural language intent to a buyer ready proposal. Our goal is to demo net new, renewal, and basic amendment end‑to‑end. We support ramps, commitments/prepaids, multi‑currency, and multi‑subscription quoting. We include explainable approvals and one‑click counterfactual repair (“reduce discount 3% to go Green”).

# Principles & Guardrails

1. **Search first, form last.** Start with a command bar. Show forms only when editing.  
2. **Governance by precedent.** Learned Green/Amber/Red bands mean fast paths for standard deals.  
3. **Deterministic maths.** Every quote pins a price book snapshot, rounding, timezone. Recompute is exact.  
4. **Lossless core; graceful extras.** Our JSON data contract is vendor neutral. Adapters degrade transparently.  
5. **Progressive complexity.** The Green path is one screen. Ramps/commitments unfold when needed.  
6. **Dual policy control.** Learnt guardrails for velocity. Explicit rules for legal/finance invariants.  
7. **Audit everywhere.** Every auto approval cites precedents, similarity and bands.

# Personas & goals

* **AE/CSM.** Draft quotes in seconds, minimal friction, instant buyer preview, confidence they’re “in policy”.  
* **Deal Desk.** Fewer escalations. Exceptions arrive with evidence and proposed “minimal edits”.  
* **Finance/RevOps.** Margin and revenue treatment protected. Totals/taxes/FX remain deterministic and approvals are explainable.  
* **Legal.** Clause insertion and approvals driven by facts (region, customer paper, data residency).  
* **Sales Ops/IT.** Vendor neutral outputs, simple CRM hooks, adapters with explicit capability flags.

# Journeys

## First run / returning

* **First run** (1 to 2 mins): choose segment & region defaults, preferred currency, toggle “show example precedents”.  
* **Returning**: home shows a **command bar**, **recent quotes**, and **precedent cards** (approved deals in cohort). Filters drawer: segment, region, currency, industry. A “Policy” pill shows Green bands for that cohort.

## Net new quote: Green path in ≤ 60s

1. **Intent.** “150 Billing Pro seats for ABC, 3‑year, monthly, including onboarding.”  
2. **Precedents.** Top‑K similar approved quotes appear as cards with structure, price band (min/p50/p90), discount pattern, similarity %.  
3. **Compose.** “Use this precedent” clones structure, applies the current price‑book snapshot, aligns discounts inside cohort bands, pins calculation context.  
4. **Guardrails.** **Green ribbon** with explainer: “Within Enterprise/APAC band, closest precedents: QUOTE-0123/QUOTE‑0789.”  
5. **Preview & Publish.** Instant order form preview. Publish creates a Proposal and Deal Room.  
6. **Accept.** Buyer accepts following by materialising Agreement \+ Subscription(s).

## Net‑new with advanced concepts

* **Ramps** (quantity/price/discount): open a Schedule editor to define windows with deterministic collision rules  
* **Commitments/Prepaids**: wizard for Min‑Spend, Prepaid Balance, Usage Pool with coverage (what accrues) and applyTo (what can consume).

* **Multi subscription**: add multiple offers, choose co‑term to agreement or staggered starts (align to bill cycle). Shared or per‑subscription commitments.  
* **Guardrails** re‑score on every edit. If Amber, show counterfactual repair; if Red, compile an evidence pack and route to approvals.

## Renewal

* “Renew ABC Billing Pro for 24 months, \+20 seats, annual billing.”  
* Pull current Agreement/Subscriptions \>\> auto compose renewal respecting price protection and uplift ranges.  
* Green if within cohort bands and contract constraints \>\> publish proposal \>\> execute renewal actions.

## Basic amendment

* “Add Analytics add‑on to ABC, 1 unit, next bill date.”  
* Build a ChangeSet with ADD\_COMPONENT, apply proration per policy.  
* If Amber, show repair \>\> publish and execute amendment.

## Versions, drafts & scenarios

* **Drafts** auto save. Publish creates Quote vN (immutable).  
* **Versions** compare highlights line/schedule deltas. Scenario groups quotes as Good/Better/Best.  
* **One proposal \<\> one scenario** to keep acceptance unambiguous. Alternates can be viewed in the Deal Room but only one becomes the offer of record.

# Domain model

* Offer / Component / PriceComponent \- seller‑facing view over catalogue (recurring/one‑time/usage; tiered/volume/per‑unit/formula/pool).  
* Constraint \-  REQUIRES/EXCLUDES/CARDINALITY across components/offers.  
* Schedule \- time‑slice mutable fields (quantity, price, discount) into windows; the generalisation of Ramps.  
* Quote \- priced instance with lines, schedules, overrides, pinnedContext (package@version, price‑book snapshot, rounding, timezone).  
* Scenario \- option label and groups related quotes.  
* Proposal \- buyer snapshot (docs, clauses, validity).  
* Agreement \- executed contract (term, governing price book, subscriptions, commitments, payment schedules).  
* Subscription \- runs under an agreement; has lines, bill cycle, term, schedules.  
* Commitment/Prepaid \- first‑class monetary commitments: MIN\_SPEND, PREPAID\_BALANCE, USAGE\_POOL; explicit coverage vs applyTo; settlement/drawdown rules.  
* ChangeSet \- renewal/amend actions (ADD\_COMPONENT, CHANGE\_QUANTITY, CHANGE\_TERM, REPRICE, etc.).  
* ApprovalPolicy / Rule \- rules emit approvals; policies orchestrate stages and SLAs.  
* Event \- immutable audit (proposal.published, approval.requested, agreement.executed, commitment.allocated).  
* Adapter \- target‑system capabilities and mappings; degradation explicit when not supported.