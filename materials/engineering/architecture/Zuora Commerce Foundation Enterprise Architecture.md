# Zuora Commerce Foundation Enterprise Architecture

## Commerce, Catalog, & (Next Gen) CPQ

Navneet Jain

Dec 2025

# Purpose

Our goal is to build a Commerce Foundation that allows Zuora to power true omni channel monetisation:

* Same platform for self serve, sales assisted, and sales led motions.  
* Same decisioning fabric for packaging, pricing, promotions, recommendations, and governance.  
* Same orders and revenue outcomes, regardless of channel, persona, or experience.

This is the architectural layer that lets Zuora become a **“**vendor for life**”**: customers start with a light self service footprint, grow into complex CPQ and enterprise motions, and never have to rip and replace.

The document lays out:

1. The flows we must support.  
2. The layered architecture.  
3. The Commerce Foundation and its major components (with key sub components).  
4. How self serve commerce, Next Gen CPQ, and future agentic surfaces sit on top of it.  
5. How the unified decision system works and where we keep options open for implementation details.

# Commerce Flows & Journeys

The focus is to design for three primary motions, with smooth transitions between them:

1. **Self Serve (PLG)**: customer signs up, discovers products, configures, and checks out without a salesperson.  
2. **Sales Assisted**: customer starts in self service mode and then transitions to “Talk to Sales” mode where rep continues from the same context.  
3. **Sales Led (CPQ)**: complex opportunities initiated and driven by sales, solutions, or partners.

The foundation must provide and guarantee:

* **Context preservation:** everything the customer did in self serve is visible to the rep and vice versa.  
* **Channel agnostic decisions:** rules and pricing outcomes are identical whether invoked from self service, CPQ, or an API.  
* **Order centric outcomes:** all paths converge on Orders (and downstream Billing/ Revenue) with consistent semantics.

## Self Service flow (simplified sequence)

1. Entry & identity  
   * User arrives via web/app.  
   * {Identity, tenant, channel…} are resolved (anonymous, trial, logged in account, etc.).  
2. Context assembly  
   * The experience layer calls Business Context Service (BCS) with session and account identifiers.  
     * identity to be figured out  
   * BCS returns a context object: segment, region, lifecycle state, entitlements, usage highlights, etc.  
3. Product discovery & offer construction  
   * Experience calls **Decision Orchestrator** with {context, decisionType="offer:list"}.  
     * Offer or product list \- we will have to generalise what we call products and plans in this terminology  
   * Orchestrator consults Catalog, Packaging, Pricing, Promotions, and (optionally) Recommendations to return:  
     * Eligible products/bundles  
     * Prices, promotions, and constraints  
     * Any recommended offers (“Good/Better/Best”, upsell, downgrade options).  
4. Configuration & pricing  
   * As user configures (quantities, terms, options), the experience repeatedly calls:  
     * decisionType="configure:validate" : compatibility, inclusions/exclusions.  
     * decisionType="price:quote" : full pricing waterfall.  
5. Checkout to order  
   * Final cart is converted into a normalised order via Order API.  
   * Orders drive subscriptions, billing schedules, and revenue rules.

![][image1]

### **Self Service to Sales Assisted**

At any point, the customer clicks “Talk to Sales”. We do not start over:

1. Experience persists a Cart/Quote Context (cart, tentative bundle, experiment history, etc.) in a shared store.  
2. Sales rep opens the same customer in CPQ:  
   * CPQ experience loads BCS context and Quote Context.  
   * Rep sees exactly what the customer did: products viewed, in progress configuration, pricing explored.  
3. CPQ uses the same Decision Orchestrator endpoints for configuration and pricing:  
   * Only difference is persona & channel in the context \- this lights up additional capabilities (negotiated pricing, advanced bundles, approvals, etc.).  
4. After negotiation, the rep either:  
   * Places an order directly, or  
   * Publishes an offer/quote back to self‑serve for digital acceptance.

This is  omni channel in practice: two surfaces, one context, one decision system.

![][image2]

### **Sales Led (CPQ) motion**

For large, complex deals:

1. Opportunity originates in CRM.  
2. CPQ experience opens with CRM \+ Zuora context hydrated via BCS. // more on this in separate documents already (Next Gen CPQ).  
3. Sales rep builds solutions using:  
   * Configurator (powered by packaging/config rules).  
   * Pricing (waterfall and dynamic rules).  
   * Promotions (programmatic and discretionary).  
4. Approvals, document generation, and contracts execute on top of the same decisions.  
5. Finalised quote is converted into Orders, with full traceability of decisions.

# Architectural View

We structure the system in four layers:

1. **Channel & Interaction Layer**: self serve portals, CPQ UI, CRM widgets, agentic interfaces, partner APIs.  
2. **Experience & Flow Layer**: reusable UI components and flow orchestrations that implement journeys.  
3. **Commerce Foundation (Shared Services)**: common capabilities used by all commerce experiences and CPQ.  
4. **Core Platform & Domains**: Billing, Orders, Revenue, data platform, identity, notifications.

**At a high level:**

* Experiences consume the Commerce Foundation via stable APIs.  
* Decision Orchestrator and Business Context Service sit at the center of the foundation.  
* CPQ and other domain apps are first class clients of the foundation, not part of it.

# Architectural Principles

A few non‑negotiables:

1. **Contex first, omni channel**  
   Decisions are taken on **{context and intent}**, not on which product made the call.  
2. **Composable, event driven foundation.**  
   Each capability is an independently deployable service, integrated via APIs and events.  
3. **Everything as configuration**  
   Pricing, packaging, promos, eligibility, and flows are represented as data and rules, not custom code.  
4. **Unified decision contract**  
   One Decision Orchestrator contract for all “what should I do/show/charge?” questions, with clear decision types and responses.  
5. **AI native, auditor friendly**  
   Deterministic guardrails and explainable logs wrap any ML/AI pieces. You can replay “why did we make that decision?” at any time. // *think of Amplitude replay \- we should be able to provide that kind of replay of decisions here*.   
6. **Tenant isolation & versioned behavior**  
   Every decision references a versioned rule set and catalog snapshot.We can reproduce a decision from six months ago even after rules change. The historical replay is easier said than done but capturing the lower level audit details is important to prove to downstream systems that we have done it right and repeatably right.   
7. **Performance by design**  
   Precomputation, caching, and compiled rules. Hot paths optimised for sub 100ms end to end.

# Commerce Foundation: Components & Sub Components

![][image3]

Here is what I consider the **Commerce Foundation**:

A set of shared, multi tenant services that provide context, decisions, catalog semantics, and governance for all commerce & CPQ experiences, converging on Orders.

We break it into the following major components in the subsequent sections.

![][image4]

## Business Context Service (BCS)

[Adaptive Context Architecture & Design](https://docs.google.com/document/d/1ygto2J91v4WXqtI0JGWlkjONJdzB4I1oZUxoCjYjkOQ/edit?tab=t.0#heading=h.n6fy2xe6n9om)  
[Zuora Context Service - Architectural Brainstorming](https://docs.google.com/document/d/1PXvCQ1w41BB2jhx3qZiNU43_MSIR9a4NRmzW56AVRMo/edit?tab=t.0#heading=h.radrlwifu3do)

**![][image5]**

**Purpose:** Provide a unified, queryable business context for any interaction: who is this, where are they from, what is the scope of interaction, what’s their lifecycle, what are they entitled to, what just happened.

Conceptually, BCS spans a three tier context graph:

1. **Interaction context:** channel, device, location, session, referring application.  
2. **Customer lifecycle:** account, subscriptions and changes, entitlements, usage, payments.  
3. **Decision state:** offers shown, prices presented, promotions applied, experiments, approvals.

**Sub components:**

1. **Context Schema Registry (This may evolve into Model Context Repo)**  
   * Defines typed attributes and groups (e.g., segment, industry, churnRisk, geo, channel, persona, lifecycleStage).  
   * Supports custom attributes and mappings to Zuora objects and external sources.  
2. **Context Resolver**  
   * Stateless API that accepts identifiers (accountId, subscriptionId, sessionId, CRM ids, etc.) and returns a hydrated context object.  
   * Can synthesise from:  
     * Core Zuora systems (Billing, Orders, Revenue)  
     * Catalog & Entitlements  
     * External data (CRM, CDP, usage stores)  
     * Real time session data.  
3. **Context Store**  
   * Read optimised store for context snapshots:  
     * Hot store (cache/Redis) for low latency.  
     * Historical store for audits and replay.  
   * Supports graph like relationships (account \> subscriptions \> Products & entitlements) to enable fast traversal.  
4. **Event Ingestion and Sync**  
   * Listens to relevant Zuora and external events (subscription changes, bill runs, usage, lifecycle milestones).  
   * Updates context projections incrementally (no nightly batch assumptions).  
   * This is nuanced and must be authored specific to the nature of the user. A registered user has a much richer and refined context assisted by this Event ingestion pipeline. However, an anon user landing on the sales funnel will have an initial context that doesn't have a lot of events in the back.   
5. **Privacy and Governance**  
   * Attribute level access control (no leaking sensitive attributes into channels that should not see them).  
   * Compliance hooks (PII, consent flags).

**BCS is not a CDP**, but it behaves like a lightweight subscription context platform purpose built for monetisation decisions.

## Unified Decision Engine: Fronted by Decision Orchestrator and Backed by Domain Engines

Note: The terms have evolved while I wrote it. You will see Decision Engine at times. But I was thinking that Decision Engine doesn't need to be a thing in the front \- we can call it Decision Orchestrator as DO is the one that abstracts the engine complexity away. Terms: 

* **Decision Engine**: the overall system that executes commercial decisions.  
* **Decision Orchestrator (DO)**: the runtime “front” of the Decision Engine that exposes the API, routes to plans, runs the execution pipeline, and coordinates domain engines.  
* **Domain Engines**: specialised backends (pricing, packaging/config, promotions, entitlements, approvals, recommendations) that encapsulate domain specific logic and data.

**Purpose:** Provide a single decision API for all commerce and CPQ domains: 

* packaging and configuration  
* pricing  
* promotions and incentives  
* recommendations / next best actions/offer  
* approvals and governance  
* entitlement and elgibility  
* experience decisions (e.g., which flow/layout/variant to use).

At runtime it does three things:

1. **Collects context and intent**: takes a tenant, decision type, context (from Business Context Service), and a domain payload (cart, quote, candidate set, etc.). This is the **Input**  
2. **Routes to domain engines**: chooses and executes a decision pipeline that invokes the appropriate domain engines (pricing, packaging, promos, recommendations, entitlements, approvals) in a defined order.  
3. **Arbitrates outcomes**: resolves conflicts, applies multi objective optimisation, and enforces guardrails (margin floors, discount caps, eligibility, persona/channel constraints) producing final decision artefacts..

This is central to our composability story: experiences talk to a unified decision engine with a stable contract. We are then free to rewire or improve internals behind that surface. The implementation must separate the **contract** from **engine** implementation so that: 

- we can evolve the internals i.e. domain engines without breaking clients. This feeds into and meets our composability promise.   
- we can change internal algorithms or technologies without breaking clients.

At a high level the following component diagram describes the Unified Decision System/Decision Engine. Each component/Sub component is described in subsequent sections. 

![][image6]

### How does UDS/Decision Engine operate? 

At a high level, the Decision Engine is a vertical pipeline:

1. Callers construct a decision request and pass in context and payload (your inputs).  
2. The Decision Orchestrator:  
   * routes the request to the right policy/plan  
   * executes that plan by invoking domain engines in sequence  
   * performs optimisation and guardrail checks  
   * produces final decision artefacts.  
3. Domain Engines do the domain specific work (pricing, configuration, promotions, entitlements, approvals, recommendations).  
4. The engine returns outputs back to the caller, and optionally emits commands to monetisation and events to the platform.

The following schematic demonstrates how a channel agnostic Commerce Foundation architecture can power commerce through Unified Decision Engine. 

![][image7]

### Decision contract

Every caller i.e self service, CPQ, partner API, agentic assistant, interacts with the Decision Orchestrator via the same contract:

| {   "tenantId": "...",    "decisionType": "price:quote | offer:list | configure:validate |                           promo:apply | nbo | nba | approval:evaluate | ...",   "context": { ...from BCS... },   "payload": { ...domain specific input... },   "options": { "explain": true, "strategy": "maximise\_margin|maximise\_conversion|balanced" } } |
| :---- |

And the response always contains:

* **decisions**: the selected actions (offers, prices, approvals, recommended options etc.).  
* **alternatives** (optional): candidates that were considered but not selected.  
* **explain**: machine and human readable trace: which rule sets fired, which constraints applied, what was overridden.  
* **metadata**: versioned rule set id, catalog snapshot id, timestamps.

**From the perspective of consumers, this is the only interface that matters**. Everything else is an implementation detail.

### Decision Orchestrator: Runtime architecture

The Decision Orchestrator is a runtime component. Control plane concerns (config, compilation, lifecycle) are separate, described later. At runtime, the orchestration pipeline involves the following:

1. Caller sends a Decision Request (per contract above)  
2. DO validates and normalises the request  
3. DO resolves which plan to run (based on tenant, decisionType, context, and control plane configuration)  
4. DO executes that plan through:  
   * deterministic rules  
   * domain engine calls  
   * optimisation  
   * guardrails and finalisation  
5. DO returns outputs and logs a full decision trace.

DO consists of several Run time components.  
 

#### Run Time Components

1. **Decision API**  
   * Single entry point into the Decision Engine.  
   * Validates decisionType, required fields, tenant.  
   * Normalises context and payload to internal structures.  
   * Hooks in authN/authZ and correlation ids via standard IDP (say OneId).  
2. **Decision Router (or Plan Resolver)**

Given (tenantId, decisionType, optional scenario/mode, context attributes), the plan resolver selects the plan id and version to execute from the Plan Store (control plane).

* The plan encodes:  
  * which stages run in which order  
    * which domain engines are invoked at each stage  
    * which rule sets and guardrails apply

This is where we interpret “price:quote maps to  \[Eligibility \>\> Packaging rules \>\> Pricing waterfall \>\> Promotions \>\> Optimisation\]”.

Note: we don't have to go all the way and choose the pieces of this component that we want to implement. For example, we don't need to go all the way to build an entire executable plan. We can center ourselves on predefined recipes that execute a predefined order of operations but have a dynamic set of rules and constraints (as phase 1). 

In nutshell Decision Router: 

* Maps decisionType (and optionally scenario/mode) to a configured decision pipeline (sequence of domain engines calls through various stages of operation/orchestration).  
  * maps a price:quote/cart request to \[Eligibility \> Packaging rules \> Pricing waterfall \> Promotions \> Optimisation\].  
  * It also decides which policy/plan to load from the plan store for the specified decision type and context.   
3. **Execution Pipeline**  
   The Execution Pipeline is the core of the runtime. It is where the Rules Engine Layer / Optimisation Layer / Guardrails & Governance concepts actually live.

**Deterministic Rules Engine Layer** 

* Executes deterministic rules that can be expressed as predicates, constraints, and derivations, for example:  
  * Pricing decision tables and expressions  
    * Merchandising inclusion/exclusion  
    * Bundle/configuration constraints  
    * Approval thresholds  
  * Implementation:   
    * Can be backed by existing Rete based tech (e.g., current pricing engine), plus a modern expression language for simpler cases.   
    * // although we may have to consider changing the existing tech \- separate thread.   
    * We may anyway need a modern expression language (CEL can do well)

    **Note**: Rule sets are modelled as versioned configuration artefacts, not embedded code. They are compiled into execution plans but always traceable back to a tenant scoped config.

**Domain Engine Invocation Stage**

* Executes the sequence of domain specific calls defined in the plan, for example:  
  * invoke Packaging/Config Engine for bundle validity and adjustments  
    * invoke Pricing Engine for waterfall pricing  
    * invoke Promotion Engine for eligibilities and deltas  
    * invoke Recommendation Engine for candidates.  
  * Each engine is treated as a pure function (request \>\> response) with no orchestration logic inside the engine.

**Optimisation Layer (Scoring & Arbitration)**

* Applies multi objective scoring when there are multiple valid outcomes:  
  * Margin, ARR growth, penetration, conversion, churn risk, etc.  
  * Internally can use:  
    * Simple heuristics (weighted scoring, priority rules).  
    * ML models or bandits where appropriate.  
  * Outputs a ranked list. Orchestrator then selects from that list according to strategy (e.g., maximise margin, maximise conversion, balanced) and guardrails.  
4. **Guardrails & Governance**  
   * Global (or cross cutting) constraints: margin floors, maximum discount, promo caps, approval requirements.  
   * Compliance constraints.  
   * Channel/persona constraints (e.g., self serve cannot override contract pricing).  
   * Guardrails always run after optimisation. They can reject/veto or adjust decisions that are attractive but not allowed.  
   * We will have guardrails per domain and as such separate domain engines may have a specialised set of stipulation over the core Guardrails and Governance.   
5. **Decision Trace Log: Explainability & Logging**  
   * Every decision generates a **decision log**:  
     * Context snapshot  
     * Rule sets and versions used  
     * Calculated values (e.g., pricing waterfall)  
     * Chosen vs non chosen options (for audit and analysis)  
   * Supports replay: given an old decision id, recompute with the same rule versions and catalog state.

### Domain engines and separation of concerns

The Orchestrator deliberately does not hard code all domain logic. Instead, it invokes domain specific engines behind stable interfaces. Domain Engines are specialised execution components that encapsulate the logic and data structures of each domain. They are invoked by the Plan Execution Engine through well defined interfaces. Key domain engines are: 

* **Pricing Engine**: executes pricing waterfall, rate cards, dynamic pricing rules, and margin calculation.  
* **Packaging / Config Engine**: enforces configuration rules and bundle logic (eligibility, compatibility, dependencies, substitutions).  
* **Promotion Engine**: evaluates promotion eligibility, stacking, precedence, and caps.  
* **Entitlement Engine**: validates rights and eligibility based on existing subscriptions and entitlements.  
* **Approval Engine**: determines approval requirements and routes based on discounts, margins, regions, and T\&Cs.  
* **Recommendation Engine**: generates and ranks crosssell/upsell/downgrade/retention options.

This separation of engines is intentional:

* **Functionally**  
  * Each domain has different semantics (monetary calculations vs combinatorial constraints vs behavioural ranking).  
  * Rules, data models, governance, optimisation, tuning, and KPIs differ by domain.

* **Technically**  
  * Different engines may optimally use different algorithms and data stores. Say \-   
    * Rete/decision tables for pricing  
    * constraint solving for configuration  
    * temporal and stacking logic for promotions  
    * graph like reasoning for entitlements,  
    * organisational graph for approvals  
    * vector search / ML for recommendations.  
  * Latency and throughput expectations differ (e.g., recommendations vs approvals).

* **Architecturally**

  * Domains become **bounded contexts** with clear ownership.  
  * Teams can evolve engine implementations independently while the Orchestrator provides a uniform decision surface.  
  * We can scale, deploy, and test engines independently.

**Important:** From a foundation perspective, this is **one decision system/engine** and **one contract**. Under the hood, we are free to use multiple engines specialised for pricing, configuration, recommendation, etc., as long as they are mediated through the Orchestrator.

### Configuration and control plane

Runtime alone is not enough. We also need a way to author and govern rules and policies, compile them into executable plans, manage their lifecycle and rollout, and simulate changes safely.

For this, the Decision Engine has a config/control plane. Conceptually we keep it simple:

* **Config** \= where rules/policies live and how they are versioned.  
* **Control plane** \= how configs become plans, how plans are rolled out, and how we simulate and govern them.

We treat these as one logical subsystem with the following responsibilities:

**Policy and Rule Registry**

* Stores high level policies and rule sets per tenant and decisionType.  
* Rules are data, not code. Such as \- 

  * eligibility filters  
  * packaging constraints  
  * pricing adjustments  
  * promotion conditions  
  * approval thresholds  
  * optimisation objectives

**Plan Compiler**

* Compiles policies and rules into execution plans:  
  * resolves which rule sets, stages, and domain engine invocations apply for a given decisionType,  
  * arranges them into an efficient runtime pipeline.  
* Compiled plans are immutable artefacts referenced by (tenantId, decisionType, planVersion).

**Plan Store**

* Persists compiled plans and exposes them to the runtime (Plan Resolver & Router) via a read optimised API.  
* Maintains which plan version is active per tenant and decisionType.  
* Acts as the bridge between config/control plane and runtime.

**Lifecycle & Rollout Management**

* Decision pipelines and rule sets are managed via Config Service.  
* Sample lifecycle: draft to test to staged to active to retired.  
* Feature flags can be used for progressive rollout and A/B testing.  
* From an implementation perspective, the Orchestrator always runs compiled execution plans, but these plans are derived from and traceable to configuration in Config Service.

**Simulation and Governance**

* Uses the same Execution Pipeline as runtime, but drives it with historical or synthetic traffic to evaluate new plans before activation.  
* Outputs KPIs (ARR, margin, discount distributions, approval volume, etc.) to support risk aware changes.  
* Integrates with decision logs to detect conflicts (e.g., rules that are always shadowed) and opportunities for simplification.

From an implementation perspective:

* Rules and policies live in the Config/Control plane.  
* Compiled plans are stored centrally and cached in the runtime.  
* Runtime never edits plans, it only reads and executes them. Alll changes go through the control plane.

## Catalog & Offer Service

**Purpose:** Provide a unified, extensible modeling layer for products, plans, bundles, and higher level offers.

We, eventually, will need an Offer layer on top of existing catalog that already caters to some of the following: 

* Products, plans, charges, features & entitlements (core).  
* Extended merchandising attributes (families, categories, tags, compatibility labels).  
* Relationships (bundles, add‑ons, substitutions, supersessions, upsell/downsell paths).

This is covered in the documentation:

[Commerce Foundation Master Rules and Optimization Strategy](https://docs.google.com/document/d/11yxFUFhzJYtfAjHweGytQ24yNba78tTD0Btygkpe7KY/edit?tab=t.0)

[Zuora Commerce\_Merchandising\_Packaging\_Bundles](https://docs.google.com/document/d/1cV7qS8HM0NXVJCae4vhEUqVUC6uyX0yhV4MWY_Bx6hc/edit?tab=t.0)

This service broadly contains: 

1. **Product & Plan Model**  
   * Authoritative representation of products and plans as understood by Orders & Billing.  
   * No mutation of core accounting semantics from the foundation.  
2. **Offer Model**  
   * Abstracts what can be sold into Offers (gives one name to sellable constructs):  
     * Standalone products.  
     * Hard bundles.  
     * Configurable bundles (templates with constraint rules).  
     * Soft bundles/marketing packages.  
   * Offers reference underlying products/plans by id, never duplicating accounting logic.  
3. **Relationship Store**  
   * Stores cross product relationships: requires, excludes, supersedes, compatibleWith, recommendedWith.  
   * Used heavily by Packaging & Merchandising rules.  
   * We can consider modelling these relations as rules and move these to the Decision Engine. This needs a bit more thought from user's perspective  
4. **Catalog Indexes**  
   * Search and discovery indexes for fast product/offer retrieval.  
   * Exposed via domain APIs (product search, offer search, “eligible for context X”).  
5. **Versioning & Lifecycle**  
   * Versioned products/plans/offers (and relationships) that support effective dating and eventually \- segment specific variants. (Part of this is already there implemented)

## Pricing Engine/Service

**Purpose:** Implement the **pricing waterfall** as a service, using dynamic rules executed via the Decision Orchestrator.

Key responsibilities:

* Calculate base price, contract/segment price, PRPC adjustments, and extended/discounted prices.  
* Support dynamic pricing using context and usage.  
* Provide simulation and what‑if analysis.

Pricing Engine/Service will broadly comprise of \- 

1. **Pricing Model & Rate Cards**  
   * Stores list prices, segment prices, and rate tables.  
   * Supports charge models (flat, per unit, tiered, volume, usage, discount \- the core models and then extensions).  
2. **Pricing Engine**  
   * Executes:  
     * PRP ‑level decision tables and expressions.  
     * Master pricing rules that can operate across products/plans.  
   * Works as a domain engine behind decisionType="price:quote".  
3. **Waterfall Executor**  
   * Applies pricing steps in deterministic order (e.g., base \> contract/segment \> dynamic adjustments \> promotions).  
   * Produces a full pricing explanation and interim values.  
4. **Simulation & Test Harness**  
   * Allows teams to test rule changes on synthetic or historical traffic.  
   * Outputs impact on margin, ARR, and customer segments.  
   * We should aim for a central simulation framework and workbench

This component deserves its own detailed design. Will be tackled separately. 

## Promotion & Incentive Service

**Purpose:** Provide structured promotions that integrate cleanly with pricing and packaging.

Responsibilities:

* Model promotions (discounts, free periods, coupon codes, loyalty rewards).  
* Govern eligibility, stacking, caps, budgets.  
* Coordinate with Pricing via the Orchestrator.

**It contains:**

1. **Promotion Model**  
   * Types: % discount, fixed discount, free period, bundle discount, spend thresholds, etc.  
   * Scope: charge, plan, bundle, account, usage band.  
2. **Eligibility & Stacking Rules**  
   * Uses a Deterministic rules engine via the Orchestrator.  
   * Handles:  
     * Temporal constraints (start/end dates, windows).  
     * Segment/region/product eligibility.  
     * Stacking and priority logic.  
3. **Redemption & Accrual**  
   * Tracks promotion usage (per customer, per program).  
   * Enforces frequency and budget caps.  
4. **Analytics & Optimisation Hooks**  
   * Emits signals into analytics for performance evaluation.  
   * Can feed Optimisation Layer to tune which promos to surface for which contexts.

(Detailed design separately) 

## Packaging & Configuration Service

**Purpose:** Make complex packaging and configuration declarative and reusable across self service and CPQ.

Responsibilities:

* Express valid combinations of products, plans, features, and add‑ons.  
* Enforce constraints (compatibility, dependencies, cardinality).  
* Support configurable bundles and guided selling.

**Sub‑components:**

1. **Constraint Model**  
   * requires, excludes, oneOf, atLeastOne, min/max quantities, dependency chains.  
   * Rules attached at levels: family, product, offer, feature.  
2. **Configuration Engine**  
   * Evaluates configuration validity.  
   * Returns:  
     * Allowed choices.  
     * Violations and suggested corrections.  
   * Backed by a constraint solver or well structured rules, accessible via decisionType="configure:validate".  
3. **Guided Selling Templates**  
   * Higher level flows (“MedTech clinic bundle”, “Connected equipment kit”) that combine questions \+ rules \+ catalog queries.  
   * Implemented in Experience Layer but powered by foundation rules.  
4. **Runtime Session State (lightweight)**  
   * Keeps configuration state for in progress sessions (self serve or CPQ) in a shared store to enable handoff.

## Entitlements & Eligibility Service (ZEMS 2.0)

**Purpose:** Provide a single source of truth for what a customer is entitled to, and use it in both:

* Run time enforcement (can they use X feature?).  
* Commercial decisions (are they eligible for Y offer?).

Contains:

1. **Entitlement Model**  
   * Features mapped to products/plans.  
   * Quantities, usage limits, flags (beta, restricted).  
2. **Grant/Revoke API**  
   * Driven from Orders and subscription changes.  
   * Writes into the entitlement store.  
3. **Eligibility Checks**  
   * Evaluated via Decision Orchestrator in packaging and promotion decisions.  
   * Example: “Only show AI bundle if customer has base platform entitlement.”  
4. **Audit & Analytics**  
   * Track entitlement changes and usage.  
   * Used by BCS to enrich context.

## Config & Governance Service

**Purpose:** Treat configuration as versioned artifacts with lifecycle, audit, and deployments for rules, flows, offers, layouts, and settings. It consists: 

1. **Config Registry**  
   * Stores configuration modules:  
     * Rule sets.  
     * Decision pipelines.  
     * Experience flows.  
     * Layouts, templates.  
   * Strong typing and schema validation.  
2. **Versioning & Promotion**  
   * Dev to test to staging to production environments.  
   * Declarative promotion manifests (bundle of configs). Works with core platform of Zuora (i.e. deployment manager)  
   * Rollback support. // to be supported by the core platform   
3. **Tenant Views (good to have)**  
   * Single pane of glass of what is active in each tenant.  
   * Helps correlate behaviors with configuration history.  
4. **GitOps / Automation Integration (through core platform)**  
   * Optional Git backing for configuration for advanced customers and internal teams.  
   * CI/CD hooks for automated validation and deployment.

## Observability & Analytics

**Purpose:** Make decisions measurable and debuggable.

Consists of \- 

1. **Decision Log Store**  
   * Append only log of decisions (structured).  
   * Indexed by tenant, decision type, context attributes, and rule versions.  
2. **Metrics & Dashboards**  
   * Latency, throughput, error rates.  
   * Business KPIs per decision type (win rates, conversion, margin impact, promo performance).  
3. **Simulation & Replay**  
   * Given historical traffic, rerun with new configuration in a sandbox to estimate impact.  
4. **ML Feature Feeds**  
   * Curated features for Optimisation Layer (e.g., past responses to similar offers).