# Related Documents

[Product Architecture Specs: Agentic Vibe Quoting](https://docs.google.com/document/d/1N0Z5ak-CxLtlsl0CCAtKYqxrp6ReiC0PPrwehs9vlDo/edit?tab=t.0#heading=h.lr36o569tnr6)  
[Architectural Perspective for Next Gen of  CPQ: Thought Piece](https://docs.google.com/document/d/1OkDZZfgdfm04ZokxWSLjlRfqqpNajJ74sYyU3N_OW5w/edit?tab=t.0#heading=h.lye6wcnifvy)  
[Lucidchart](https://lucid.app/lucidchart/1fa0e543-c555-4d98-8809-7a9c9be12f63/edit?invitationId=inv_899e17ba-3313-4090-9289-a622d456c39d&page=-AHue6fegAec#)

[Innovation Thru’ Next Gen CPQ](https://docs.google.com/presentation/d/1musReMJ9fnVD96b0JYGd9b9XnQS4BRnziQ4F6ylDGBQ/edit?slide=id.g36db3cd3bcf_0_3374#slide=id.g36db3cd3bcf_0_3374)  
	

# Next Gen of CPQ @ Zuora

# Next Gen of CPQ @ Zuora

## … as opposed to Next Gen CPQ …

May/June 2025  
Navneet Jain 

We have discussed Next Gen CPQ at Zuora for a few months now. Instead, I am going to write this piece for the Next Generation of CPQ at Zuora. The connotation of Next Gen CPQ is that it is a separate CPQ that sits away from CPQ that is used by our current customers; on the other hand, Next Generation of CPQ analyses a true strategic vision for what should be Zuora’s overall CPQ offering in say June 2026\.

# Related Documents

[Product Architecture Specs: Agentic Vibe Quoting](https://docs.google.com/document/d/1N0Z5ak-CxLtlsl0CCAtKYqxrp6ReiC0PPrwehs9vlDo/edit?tab=t.0#heading=h.lr36o569tnr6)  
[Architectural Perspective for Next Gen of  CPQ: Thought Piece](https://docs.google.com/document/d/1OkDZZfgdfm04ZokxWSLjlRfqqpNajJ74sYyU3N_OW5w/edit?tab=t.0#heading=h.lye6wcnifvy)

This document is structured in multiple tabs. Please go through the relevant tabs as needed. 

# Background

## What do we have ? 

We already have a CPQ offering that allows customers to build quotes, view metrics, handle ramps, implement multi subscription quoting, generate quote docs and integrate with Zuora billing. This CPQ is native to Salesforce and is installed as a managed package. There is 2 way sync established with Quote data saved in Salesforce and Accounts, Subscription (and related data) synced back to Salesforce from Zuora Billing. This CPQ relies on Salesforce as platform to achieve several functional outcomes: 

- Approvals  
- RBAC (role-based access control)  
- Integrations and workflows (triggers, flows)  
- Quote notifications    
- Integrated Quote reporting

### What works (as listed in the paragraph above)

- Product browsing and selection  
- Core quote creation  
- Ramps  
- Multi subscription quoting  
- Integration with billing

### What does not work

This can be divided into 2 main categories: Functional, that we just haven’t been able to get to/capability gap, and 2\) architectural limitations. I am not mentioning the parity gaps against billing in this section. 

- Functional gaps include features such as deal scoring, goal seeking, native approval mechanism, advanced document generation, detailed metrics etc.   
- Architectural limitations may not really be limitations but at this point, can be grouped along with \- this includes reliance on Salesforce and its platform, limited to Zuora Billing, Scale especially when it comes to rules.  (Governer limits, heap size, CPU timeout)  
- One key aspect that must be analyzed is the cause behind the spread of our customers across CPQ versions. I am not very close to the reasons for why customers don’t change but I have been in front of customers where I have had first hand realisation that customers simply “cannot” change \- not just easily but it takes a considerable effort. 

Some of the recent enhancements have helped this CPQ cover some of the gaps. Some of these recent advancements include: 

- Multi subscription quoting  
- ?

It should be noted that these recent enhancements require their baking time and current adoption rate is \<xx/\>  
![][image1]  
![][image2]

### Extensibility

- UI extensibility through Extensibility Framework (JS)  
- Backend and logic extensibility through Rules and Custom Actions (Apex)

## Objectives

Zuora’s strategic objectives for CPQ include: 

- Get maximum share of 7000 SF customers   
- Convert the pricing model for existing Zuora customers to seat based and recover additional $xx mn ARR  
- Establish its position as a technology leader in AI first CPQ and Commerce  
- Functional parity and beyond with best in class CPQ in the market 

To quantify and make these goals SMART (Specific, Measurable, Achievable, Relevant, and Time-bound), we need to answer a few questions: 

- How many customers out of the aforementioned 7,000 can we practically acquire  
  - \[satish\] based on the screenshot from a recent webinar which discussed about SF CPQ migration with several end customers, we potentially have a target of 5600 customers.\[extrapolating from the survey below, 80% of 7000 plan to leave SF CPQ\]  
    - https://event.on24.com/eventRegistration/console/apollox/mainEvent?\&eventid=5008047\&sessionid=1\&username=\&partnerref=\&format=fhvideo1\&mobile=\&flashsupportedmobiledevice=\&helpcenter=\&key=BBCBFCC0E5C879F5E5D318BD1E6F0D5A\&newConsole=true\&nxChe=true\&newTabCon=true\&consoleEarEventConsole=true\&consoleEarCloudApi=false\&text\_language\_id=en\&playerwidth=748\&playerheight=526\&eventuserid=769774890\&contenttype=A\&mediametricsessionid=663013426\&mediametricid=7035010\&usercd=769774890\&mode=launch  
  - ![][image3]  
- What is the profile of those customers   
- How much revenue can we acquire per seat and what is it dependent upon  
  - Parity with billing  
  - Additional features  
  - An understanding of how much can we recover if \<scope\> is achieved  
- Competitive analysis of what we lacking with an order of priority 

Along with the above, there are some additional objectives that stem from architectural limitations \- 

- CRM agnostic  
- Billing agnostic  
- Enterprise scale

Each of these points need to be understood on its own merit \- 

**CRM Agnostic**: the reason behind wanting a CRM agnostic CRM are two-fold: 

- Be able to sell CPQ to other CRMs. But this needs to be validated. Key point being we cannot force the customers to change their CRM. CPQ must fit into the ecosystem.   
  - What % of our target market uses Salesforce as their CRM. The point being that if 2/3rds or more of our target market uses Salesforce as a CRM then we must perfect our fitment into Salesforce because that market itself is huge. It is best to not spread ourselves thin.   
  - The additional effort required to build adapters to other CRMs and stabilise over time with parity must not outweigh the ROI i.e. number of customers/deals we acquire on those CRMs.   
  - Hence, my recommendation is that unless our target market is heavily spread (which I don’t think it is), we focus on Salesforce as our CRM host.   
- Overcome the Salesforce limitations \- Salesforce limitations such as API limits are often talked about as one of the major constraints for delivering a best in class CPQ. Having said that, we are seeing the advent of CPQs (such as Nue) that are working on Salesforce and are eating into our market share. Apart from this, the other constraint is extensibility using Apex. Customers extending the capability of our CPQ using Apex coding often end up creating an ecosystem within an ecosystem that has presented us tall challenges even in migration of CPQ versions. 

**Billing Agnostic:** I won’t go into too much detail into this but unlike CRM agnostic objective, this one is much more natural and straightforward. We can achieve it using Adapter design patterns and in fact the same can be achieved via the Integration framework that is being built. The core of this is to encapsulate the 2 way billing data model complexity and billing concepts of a provider from CPQ. CPQ has a grammar of its own and will not worry about the contract laid out by external providers. Instead this work will be handled by the Integration framework. More on this later. 

**Scale**:   
\<\>

## Limitations of Salesforce as platform for CPQ

- Governor limits  
- Dependence and hence royalties   
- Specific niche dev skills (SF development)   
- Restrictive in being able to utilising core assets as back and forth calls consume SF APIs and end up being time consuming 

# Options

Broadly, we have two options for the next generation of CPQ. 

| Enhance the existing CPQ  | Develop a new CPQ  |
| :---- | :---- |
| Existing customers continue to use this CPQ and are offered new features | Existing customers will be migrated in some way, shape or form. It could be feature level migration, cohort based migration, double dip transition.  |
| We will leave out the objectives such as CRM agnostic, Billing agnostic behind in order to achieve it.  | Can build adapters but see the next point. It is still going to be important to focus on Zuora Billing and Salesforce CRM to start with. |
| Focus only on Salesforce | Eventually we can target other CRMs too but there must be one focus in the beginning to do it well.  |
| Continue to leverage Salesforce platform features.  | Build the features such as approval and RBAC outside Salesforce. This allows us to control our user base better and have a shot at offering richer features.  |
| 2 way sync (including data connect) will continue and may have to be enhanced | New sync adapters will be built to understand the grammar of various applications.  |
| Entire org focusses on one CPQ | Current CPQ must still be supported while building and migrating to new CPQ.  |

There are a few other aspects that we must consider while we are deciding on which approach to follow \- 

- The existing CPQ must still be enhanced while we build a new CPQ. This is to support the objective of offering new features and billing parity to be able to move customers to a seat based licensing.   
  - Underlying hypothesis being that by offering a richer CPQ we will be able to uplift the current contracts  
- To be a leader in AI first, we may not be able to wait for a new CPQ to come up and offer AI based capability. Hence, there will be a time of parallel efforts spent into the AI based enhancements. 

## The Third Approach

There is a third approach though. Knowing that migration of existing customers is a notorious undertaking and Zuora already has a majority of customers spread across the version other than the latest one, it is imperative to derisk our endeavour. Migration can be derisked by building new CPQ as fully backward compatible or by building bridges and translators but there is still an element of customer migration, SOPs, data model transition, and an obvious biggest factor being resistance due to competing priorities. 

Imagine a world where the customers using existing CPQ (lets say we limit these to CPQ 9 and 10), can continue to use their established ecosystem but can leverage a brand new Fully AI native experience in Zuora’s CPQ-X AI as well. I will illustrate this with a few scenarios and then articulate what this option may look like. 

Scenario 1   
Customer is using CPQ X (or 9). Has implemented basic product selection, offers a couple of products and has a couple of quote templates that the sales rep chooses before generating a quote. 

Scenario 2   
Customer is using CPQ X. Has implemented a flavour of guided selling using product filters that enables the sales rep to put together a quote with an array of products. They have also implemented product level rules that enable them to discount based on quantity or set of products. 

Scenario 3   
Similar to Scn 2 but the customer has implemented an array of rules that enforce product compatibility and has auto selection of Quote templates based on the context of the quote and opportunity. Sales rep can override the template and choose from a set of 10 templates. 

… and so on. 

![][image4]

### The New World Order

**Vision**  
We evolve Zuora CPQ in a dual mode architecture:

* Keep CPQ X as the enterprise grade, structured quoting engine.  
* Add Agentic CPQ which is an autonomous, AI powered quoting assistant that can read catalog and quote rules, rate cards, and even interpret custom Apex quoting logic to produce identical or improved outcomes.

The customer decides how and when to adopt the Agentic model. Switching back to CPQ X remains seamless.

**Key Principles**

* No Heavy Migration: Existing catalog, rules, approvals, and Apex customisations are leveraged directly by the Agentic CPQ.  
* Code Aware Agents: We train the Agentic CPQ on customer specific Apex logic, so output matches CPQ X behaviour. Alternatively, if there is a flow that is customised, it can become an agent of its own. This is where we can actually implement the Concierge-Special Agent architecture.   
* Potential Progressive Adoption: Start with “Assist Mode” (agent recommends, CPQ X executes), then move to “Autonomous Mode”. We can choose on the spectrum of fully ready Agentic CPQ to Assistance Mode.   
* Feature Convergence: Enhancements like Product Configurator, Deal Room, and Iframe Embedding apply to both CPQ X and Agentic CPQ. These additional features will be wrapped in microservices.   
* Bidirectional Interoperability: A quote started in Agentic CPQ can be resumed in CPQ X, and vice versa.

### Considerations

- Following this approach implies that Agentic CPQ doesn’t need to have conventional quote generation experience. Any enhancements in that experience will be made in CPQ-X (version XI ? ).   
- Deal Room, Deal Scoring etc will be available in the next version of CPQ X.  
- Goal Seek will be an agent that generates quotes (doesn’t have to be just goal seek).  
- Document Generation will also be available in Agentic CPQ.   
- All the elements and data will be available to both the CPQ applications.   
- Data Model enhancements such as Agreement, Proposal will eventually be made available to both. 

Note that data model enhancements may not be readily available in CPQX and hence an adapter will be required. 

![][image5]  
![][image6]

# Agentic CPQ 

* Deliver a conversational, agent orchestrated quote experience with zero migration pain.  
* Preserve deterministic outcomes by executing existing Apex logic via an adapter layer 

## Primary Actors

* Sales User (human)  
* Quote Builder Agent (QBA) \- orchestrator; owns the conversation and quote lifecycle.  
* Product Discovery Agent (PDA) \- finds/curates products & bundles based on intent and constraints.  
* Configurator Agent (CFA) \- applies recommendations, upsells/cross sells, templates.  
* Compatibility/Rules Agent/Engine (CRE) \- validates product/package compatibility and policy rules.  
* Apex Adapter & Policy Agent/Engine (AAPE) \- executes customer Apex or its compiled equivalent.  
* Pricing & Rating Service (PRS) \- calculates list/net, ramps, discounts, taxes.  
* Approvals Service (APS) \- policy based approvals & routing.  
* Deal Room \- customer facing quote, redlines, acceptance/e‑signature.

![][image7]

## Agent vs Service: Decision Making Principles

**Agents**

* Goal-directed, language-driven planners that break tasks into tool calls.  
* Good for ambiguity, exploration, negotiation, and multi-step reasoning.  
* Non-deterministic by nature; outputs depend on context and policy.

**Services (AAPE/CRE/PRS)**

* Pure functions: same inputs give same outputs. Low latency, testable, versioned.  
* Auditable & governable: return reason codes, rule ids, and artifacts.   
* Safety/performance is critical: pricing, tax, and policy must be stable under load.

**Design rule of thumb**

* If the step requires planning under ambiguity then make it an agent (e.g., discovery, configuration recommendations, summarising options).  
* If the step requires deterministic calculation or enforcement then make it a service (e.g., price math, compatibility, policy execution).

## High Level Flow (Happy Path)

1. **Preflight Context**  
   * QBA pulls Opportunity, Account/Customer, Contacts, and Current Holdings/Subscriptions.  
   * If a customer is new, QBA proposes a prospect shell account (minimal profile) or enrichment flow.

2. **Intent Capture & Normalization**  
   * User states goal (e.g., “renew ACME for 12 months, add 200 seats APAC, 10% uplift”).  
   * QBA normalizes into structured intent (SKUs, regions, terms, dates, constraints).

3. **Discovery Loop**  
   * QBA calls PDA with structured intent.  
   * PDA queries Catalog, availability, eligibility; proposes products, bundles, ramps, contract terms.  
   * QBA \<\> PDA iterate until the proposal meets guardrails and user confirms.

4. **Visualisation & Draft Quote**  
   * QBA renders a live visual: line items, tiers, ramps, term, MRR/TCV summaries.  
   * Inline Warnings/Errors appear (compatibility, missing data, policy limits).

5. **Compatibility & Policy Validation**

   * QBA calls CRE for product, packaging, and entitlement checks.  
   * QBA invokes AAPE at policy checkpoints to match legacy outcomes.  
   * Blocking issues require resolution; non blocking produces warnings.

6. **Recommendations & Config**  
   * CFA proposes upsells/cross sells, swap suggestions, or cost optimised bundles.  
   * CFA can apply templates (segment/region/playbook) or defaults set by AAPE outputs.

7. **Pricing & Rating**  
   * PRS computes list \> net with discounts, ramps, promotions, taxes, edge cases.  
   * AAPE may run discount/exception logic before/after PRS depending on customer’s legacy order.

8. **Review & Approvals**  
   * QBA assembles the quote packet (calculate breakdowns, policy attestations, audit).  
   * APS routes for auto approve or manager/legal/finance per policy.

9. **Deal Room & Customer Acceptance**  
   * QBA publishes to Deal Room: terms, options, change log, redlines, e‑signature.  
   * On accept, quote is committed and order/subscription created.

10. **Handover & Audit**  
    * All steps logged with: inputs, rules, Apex invocations, decisions, and deltas.  
    * Quote is openable in CPQ X (shared object model) or continued in Agentic CPQ.

## Apex Compatibility (Inline Agents?)

Can possibly provide three implementation tracks (can have a choice per customer or can mix):

1. **Apex Adapter (Direct Execution)**  
   * Run vetted Apex functions in a sandboxed runtime via invocation descriptors (what to call, with which data snapshot).  
   * Pros: perfect behavioral parity. Cons: sandbox management & performance.

2. **Policy DSL Transpilation** *(*recommended*)*  
   * Compile common Apex rule patterns into a deterministic Policy DSL (e.g., JSON/YAML rules with predicates, calculators, and effects).  
   * Pros: portable, testable, faster; supports explainability. Cons: one‑time translation.

3. **Oracle Mode (Record/Replay)**  
   * For ultra complex legacy blocks, build an oracle: capture inputs/outputs from Apex in CPQ X and replay to match outcomes during migration period.  
   * Pros: zero behavioral drift. Cons: limited transparency.

The AAPE hosts all three: adapter, compiler/transpiler, and oracle, chosen per rule block. It exposes a single deterministic API to QBA/CFA/PRS/APS.

## Guardrails & Governance

* Determinism windows: agentic steps that must produce identical outputs are pinned to AAPE/PRS checkpoints.  
* Policy tiers: soft warnings vs hard blocks, with escalation rules.  
* Audit & Explainability: every decision cites rule id/version, inputs, and result.

## First Time Setup

![][image8]

Aug 21, 2025

**Notes**

—-----

**Flow 2 : Initiate the agent**

- Fetch all the config and templates, rules, code from the CPQX instance (assuming that this customer has a CPQ X instance)  
- Convert Rules into ACPQ rules  
- Templates  
- Default values   
- CPQ settings   
- Apex code and plugins // 

Assume the quote is created in the Agentic CPQ 

- Handover the quote to CPQ-X  
- Method 1- Continuous sync to CPQX (salesforce)  
- Method 2 \- sync when the customer requests to move it to CPQ-X


# Core Functional Architecture

# Next Gen CPQ: Functional Architecture and Design

Apr 28 2025  
Navneet Jain

Note that this document is a living document. It aims at thinking about the next gen CPQ at a high level and gradually diving deeper into each component/module thereby forming a functional understanding of what we need to build. This understanding will comprise component design, interfaces, and information schema. 

Some goals that are at the forefront while drafting this document: 

* Decouple CPQ from CRM and Billing stacks.  
* Outperform Logik.io (configuration depth) and Salesforce RLM (flexible domain model).  
* Deliver solution & product selling via reusable templates, dynamic rules, and catalog entities/config/relationships.  
* Provide a Billing agnostic adapter covering Zuora, Stripe, Metronome, Chargebee, and more in future.  
* Maintain full auditability with immutable snapshots and fine grained workflow states.

![][image9]

(See the Component and System Interactions)

# Principles 

| Principle | Why it matters for CPQ |
| ----- | ----- |
| Domain driven, microservice MCP | Keeps fast moving catalog/config/quote logic separate, lets each domain scale and upgrade independently. |
| API first & headless UI | All functions are callable via gRPC/REST \+ GraphQL. Lightweight React/Next widgets embed in SF, Dynamics, HubSpot, Deal Room, partner portals. |
| Event driven core | Quote, pricing, approval, subscription events stream to Kafka/or alike; enables real time metrics, AI feedback loops, async approvals. |
| “Rule as data” low code extensibility | Product, quote, ramp, approval, and pricing rules live in a versioned rule store (DMN/Kogito/Drools/Z-rules); admins edit without re-deploying. |
| Multiorg, multi tenant | Shared services, tenant scoped data, pluggable RBAC (IAM) as described in PRD user profiles section . |
| AI native | Isolate AI inference behind a sidecar “AI Framework” service; agents can call catalog, pricing, quote services with minimal extra latency. |
| Security & compliance | OAuth 2.1/OIDC, scoped JWT, field level encryption (PII), ASC-606 / SOC 2 event audit. Leverage OneId, BYOK here.  |
| Observability by default | OpenTelemetry traces across every quote action; per tenant SLO dashboards surface latency, error budgets. |

# Perils of Creating a Net New Application

Audits  
One id/tenant management   
Data access management   
Deployment and Config management   
Entire platform 

# Work Items (Immediate Fruits With High ROI)

I recommend building Next Gen CPQ in a way that we develop new services that are usable in the existing CPQ as well or otherwise across Zuora (think Commerce in general). 

The backend of Configurator service is something that can be useful not only for Next Gen CPQ but also for commerce and for existing CPQ as well. In fact, Zuora should have only one Configurator. As such, it is a candidate for standalone development and can be considered for prioritisation. Since the configurator in its real sense is an orchestrator that executes rules based on an input and generates the output that leads to update of the line items, it is in fact an extension of the existing Zuora rule engine (or any rule engine in general), it helps our case to ship something central. 

Another such component is Metrics Domain. Zuora has struggled with metrics \- with orders, with quotes and everywhere. Developing this as a separate service can be really powerful. My recommendation is that the Analytics team should build metrics as a service that is central across Zuora’s product suite.

# High Level Functional Flows/Actions and Ownership

| Functional Action | Description | User Role | System/Component Involved |
| ----- | ----- | ----- | ----- |
| Browse and Filter Catalog | Navigate categories, filter by attributes, guided selling filters | Customer (Self serve), Sales Rep | Catalog Service |
| Configure Products | Choose attributes, enforce compatibility and selection rules | Customer (Self serve), Sales Rep | Configurator Service |
| Compare Products | Comparison of features, attributes, pricing | Customer, Sales Rep | Catalog \+ UI Layer |
| Create Quote | Create new draft quote manually or from catalog/configurator | Sales Rep, Customer (self serve) | CPQ Engine (Quote Manager) |
| Generate Quick Quote | Auto generated simple quotes for smaller deals | Sales Rep | CPQ Engine \+ Pricing Engine |
| Version Quotes | Create, edit, and manage multiple versions of quotes | Sales Rep | CPQ Engine (Version Manager) |
| Apply Discounts | Apply manual or guided discounts | Sales Rep | Pricing Engine, Rules Engine |
| Config Bundles and Subscriptions \- building Solutions | Configure static, dynamic, and head bundles; create new or modify subscriptions | Sales Rep | Configurator \+ Subscription Manager |
| Deal Room Collaboration | Share quotes internally/externally for review and negotiation | Sales Rep, Approvers, Customers | Deal Room Service |
| Apply Pricing Rules / Promotions | Automatically apply conditional discounts or promos | System (Pricing Engine) | Pricing Engine, Promotion Engine |
| Approval Workflow | Trigger approval based on thresholds (e.g., discount \> X%) | Sales Rep, Approver | Approval Workflow Engine |
| Change Quote Terms | Modify payment terms, contract periods, billing start dates | Sales Rep | CPQ Engine \+ Billing Integration |
| Contract Finalisation | Create contracts from quotes, handle redlining and signing | Sales Rep, Legal | CLM Integration (Contract Lifecycle Management) |
| Push to Billing | Push finalised quotes/orders to billing system (Zuora, Stripe, etc.) | System | Billing Adapter Layer |
| Order Creation | Convert accepted quotes into orders | Customer, Sales Rep | Order Management |
| Quote Metrics Calculation | Calculate ARR, TCV, MRR, discount %, margin % per quote/version | System | Metrics Engine inside CPQ |

# Component Design

| Component | Responsibility | Classification |
| ----- | ----- | ----- |
| Catalog Service | Manages product discovery, search, filtering, comparison | External Integration |
| Configurator Service | Manages attribute selection, rules enforcement, option dependency management | CPQ native experience. Catered by an external service for commerce use cases across Zuora |
| CPQ Engine (Quote Manager) | Orchestrates quote creation, versioning, lifecycle management | CPQ Core |
| Deal Room Experience | Provides a unified experience aggregating quotes, approvals, discounts | Experience Layer |
| Deal Engine Experience | Purpose built experience for complex quotes for managing multiple quote line items and achieving group level actions.  | Experience Layer |
| Deal Desk Experience | \<tbc\> | Experience Layer |
| Admin Hub | Once central place to manage all things CPQ config | Experience Layer with a config master in the backend |
| Pricing Engine | Calculates final prices, applies price models (tiered, volume, usage, ramp) | Standalone service, Integrated with CPQ |
| Promotion Engine | Applies automatic promotions and dynamic adjustments | CPQ Native |
| Rules Engine | Evaluates discount, pricing, product compatibility rules | Suggest leveraging a core commerce rule engine. Performance factors TBC |
| Approval Manager | Manages multistep quote approval flows and escalations | CPQ Native \- can be an external service or CRM native |
| Metrics Engine | Computes financial metrics (ARR, TCV, MRR, margin, discounts) | CPQ Native backed by central Analytics |
| Billing Adapter Layer | Translates quotes into canonical billing payloads for billing systems | CPQ Native (note that billing system is external) |
| Order Management | Converts accepted quotes into orders and triggers fulfillment | External Integration |
| Contract Lifecycle Management (CLM) Integration | Manages contract drafting, negotiation, redlining, and signing | External Integration |
| Layout Manager | Layout manager leverages the inputs from the templates and the renders prebuilt components for a given proposal/quote flow.  | CPQ Core |
| Flow Orchestrator | Entire quotation flow is built as a set of independent tasks with inputs and outputs defined. The Orchestrator manages the handoffs in sync or async mode as needed. It can feed off the templates and build a working instance at the run time.  | CPQ Core |

![][image10]

# Admin Domain

[Next Gen CPQ - Functional Doc - Draft](https://docs.google.com/document/d/1FXSYCEFs8ZA4LPiwEL1JFL9recXYidZ8m8imvxRZr-E/edit?tab=t.5rovw78jk9jj)

# Catalog Domain

High level what CPQ needs from the catalog: 

* **Product Structures**: Simple products, *configurable* products, nested bundles  
  * Should solutions / BOM be here?   
  * Ideally solutions are created of products and must be stored with nesting and packaging specific to context   
  * As such, solutions ultimately will find their way into the catalog // design item  
* **Attributes & Values**: Attribute metadata including types, formatting, mandatory/optional status, visibility rules, hierarchical values, effective dating and relationships.  
  * visibility rules, hierarchical values, relationships \- are not available in the attributes today  
  * Note that these attributes represent the metadata of catalog entities. Zuora doesn’t support it today. Each product can have its own set of attributes and as such it is more dynamic set of KVs that can be stored as JSON  
  * Has already been discussed and is definitely doable.   
* **Product Categories**: Taxonomy for classification and filtering, supporting guided discovery and compatibility enforcement  
  * Category has to be on the product and other first level entities. Current category is not really useful  
* **Features & Entitlements**: Breakdown of what’s included in the product. Powers benefit based selling, entitlement driven configuration, and attribute level pricing triggers.  
  * Nesting of features to allow solution selling and complex relationships   
  * Feature relationship and Feature attributes relations  
  * Feature level pricing   
* **Rate Plans / Charges / Rate Cards**: Pricing container and price. For one time goods, product can be associated with the price directly, indirectly enforcing a plan behind the scenes for any backward compatibility.   
* **Attribute Based Pricing**: CPQ needs to perform conditional price lookups based on selected attributes (e.g., region, storage, device type). Already supported with Contextual pricing and ABP/DP.   
* **Relationships & Compatibility**: Cross product rules, substitute definitions, must have/cannot have constraints, inclusion/exclusion, relationships driven from catalog metadata.  
* **Support for Solution Selling**: The catalog must allow for grouped solutions made up of multiple configurable products, services, and entitlements across different layers.  
  * Solution can be stored as composite products. 

Data Model (considering ground up)

- Key is to enable nesting of products, features, and relationships   
- Be able to store the unstructured metadata.   
  - Options: store the attributes separately and allow attributes to have a behaviour   
  - Or store attributes as just unstructured data on product object 

| Entity | Fields | Comments |
| ----- | ----- | ----- |
| Product | id, sku, name, type (simple, configurable, bundle), description, category\_id, status, effective\_date, state, metadata\_json | metadata\_json is a flexible unstructured KV string storing the characteristics of the product for rule based config, pricing, or guided selling. See Product Attribute object as well. |
| Product Category | id, name, description, parent\_category\_id, hierarchy\_level | Used for navigation, filtering, and nesting. It is not an attribute of the product but helps in giving the product a character such as product may belong to category “Computer” and by the relationship of category, it may be a parent product for another product of category “Storage”. In addition, category can have its own characteristics that help keep products leaner as they inherit all the properties of the category.  |
| Product Attribute | id, product\_id, name, datatype, validation\_rule, default\_value | \[Optional\] This object can store a set of attributes. Contextual service can be extended to perform this job.  The objective is that for full configurability, attributes may have their own characteristics. With metadata\_json, we can store unstructured attributes but by storing the metadata about the attributes we can enforce validations, and hence, structure the rules. This is key for the configurator.  |
| Product Attribute Value | product\_attribute\_id, value | Represents selected or available values. Drives rules and UI rendering. |
| Product Relationship | id, source\_product\_id, related\_product\_id, relationship\_type (cross sell, up sell, replacement, downgrade, upgrade) | Enables cross product rules and guided recommendations. Useful in guided selling and deal structuring. |
| Bundle | bundle\_id, component\_product\_id, min\_qty, max\_qty, default\_qty, optional | Supports nested and optional bundle configurations. Needed for head/dynamic bundle logic. |

Feature and Product Feature objects will remain similar to what exists today but to allow for nesting of Features, we will need a Feature hierarchy. 

# (Product) Configurator Service 

Configurator handles complex product configurations and allows such rules/configs to be dynamically built based on attribute selections, compatibility rules, guided flows, and dependency validations. It enforces product eligibility, inclusion/exclusion, conditional visibility of features/attributes, validates cross product relationships (e.g., must have, cannot have rules, if then \<\>), and supports guided selling experiences. It guarantees that what is quoted is technically and commercially valid according to both product definitions and deal-specific conditions.

Examples of Configurator Behavior:

* Selecting a *Cloud License* automatically prompts the user to choose a *Data Region* attribute.  
* Choosing *High Availability* configuration dynamically disables incompatible single instance deployment models.  
* Choosing *High Availability* configuration dynamically adds a new feature that is a must have.   
* Configurable bundles allow optional add ons (e.g., Support Plans) based on core product selection.  
* Attribute driven pricing changes: selecting Premium Storage automatically increases monthly price.

Further it can be extended to: 

* Ask contextual questions like "Do you need disaster recovery?" during the guided flows and based on the choice we can reveal options dynamically.

Configurator primarily will be driven by the Rules. And the rules can be: 

- Selection rules: dependency enforcement \- must have, exclude/include   
- Relationship rules: Product \<\> Product relations  
- Application of hierarchies (Feature or product hierarchy)

**To avoid any hardcoding, Features, Products, Plans and Pricing elements will be associated with rules to drive run time behaviour. Configurator is responsible for deciphering the context and orchestrating the rules to generate the desired outcome. Outcome can be a configured product, a warning, or an exception.**  

**![][image11]**

# Pricing Engine

* Catalog provides base pricing for core products, however contextual, and hence for browsing; CPQ Pricing Engine computes dynamic deal specific pricing  
* CPQ Pricing Engine applies discounts, volume tiers, ramp schedules, and customer specific terms at quote time. // we should use a core pricing engine (“new” rating can do the job here)  
* Pricing decisions are context sensitive: driven by customer type, deal size, product configuration, contract terms. In our current catalog, we support contextual pricing but CPQ needs more than just that.   
* CPQ owns financial metrics (ARR, TCV, MRR), not Catalog; hence it must control pricing computation.

Overall, Pricing Engine will sit outside CPQ but it will need to support all the permutations that a certain purchase flow requires.It is a stateless microservice invoked synchronously. 

The inputs are *(product details, attributes, qty, attribute-values, dates)*   
and the output is *(listPrice, netPrice, discountBreakdown, rampSchedule, tax)*.

*// it is also important to keep the core logic of pricing in one place for the entire product suite. Hence, CPQ should document the requirements and leverage the central pricing engine.*

Examples: 

* A customer purchasing 1-10 units pays $100 per unit, but buying more than 10 units triggers a $90 per unit tiered price.  
* A SaaS subscription configured for usage based billing charges $0.05 per API call, with monthly minimums automatically enforced.  
* A bundled offer where selecting Product A and Product B together applies a 15% bundle discount dynamically.  
* Customers in "Enterprise" segment automatically qualify for negotiated pricing pulled during quote generation.  
* Multi year quotes automatically apply ramp schedules where Year 1 pricing is discounted, and full price resumes in Year 2\.

# Quotation Engine (QE)

A single, auditable workspace to draft, negotiate, approve, and fulfil any “commercial scenario”. 

* Net new purchases, renewals, mid term amendments, partial cancellations, ramps, composite solution deals.  
* Template driven UI & workflow via Proposal Template / QuoteTemplate (layout, default terms).  
* Billing aware separation of sales intent (Quote Line Item) vs. billing execution (Quote Charge Detail).

  ### **New Quote Flow**

  #### **CRM Opportunity \>\> Proposal Creation**

* **Trigger:** User clicks 'Create a Proposal' on the CRM Opportunity page.  
* **Contextual Data:**  
  * Customer Information  
    * Contact Information  
    * Location Information  
  * Opportunity Information  
  * Company Information  
  * History and Metrics (TCV, ACV)  
  * Price Guidance (if applicable)  
  * Any additional context attributes

**API Call:**

* POST /proposal/create  
* **Module**: Core Quote and Proposal service  
* **Purpose:** Triggers the creation of a Proposal in CPQ, initialises Quote UI  
* **Input:** Contextual Data from CRM  
* **Output:** Proposal ID, Draft quote initialisation  
* **Interfaces:** CRM \>\> Proposal Service \>\> DB \>\> UI renderer  
* **Database Interaction:** Save initial proposal context and metadata in Proposal DB  
* **Outcome:** New Proposal is created and initialised in Quote UI, ready for user interaction  
* **Challenges:** Data integrity from CRM, context missing edge cases

#### **Quote UI Initialisation and Template Selection**

* **Trigger:** Proposal has been created with the contextual info and proposal Id is available   
* **Flow:** Prepopulated Quote UI is rendered with contextual data.  
* **Module/Sub Model:** Quote UI Renderer & Template Service  
* **Input:** Proposal ID, Contextual Data  
* **Output:** Rendered Quote UI, Prefilled Forms  
* **Interfaces:** Template Service \>\> UI Renderer \>\> DB  
* **Database Interaction:** Fetch templates and customer preferences from Template DB  
* **Outcome:** Quote UI is displayed with templates or pre-filled data, ready for product selection  
* **Challenges:** Real time UI updates, error handling on missing templates

  #### **Product Selection (Guided Selling)**

* **Trigger:** User navigates to Product Selection  
* **Flow:**  
  * Context based   
  * Template based   
  * Manual flow  
    (template and context based flows can be combined into one)

**Module:** Product Selector

* **Input:** Context and Template Data, or just opportunity and proposal info with initial info from Quote  
* **Output:** List of Eligible Products  
* **Interfaces:** Product Selector \>\> Product Catalog Service \>\>DB  
* **API Call:**  
  * GET /products?context=...\&products In ...  
* **Database Interaction:** Fetch eligible products and plans  
* **Outcome:** User is presented with a list of eligible products, with guided options based on context or based on manually selected filters  
* **Challenges:** Product eligibility conflicts, real time price calculation  
  Add pricing calls/engine 

  #### **Configurator (If Invoked)**

* **Trigger:** User selects complex product configuration or solution config  
* **Flow:**  
  * Manage discounts  
  * Add/Remove AddOns  
  * Handle product relationships

**Module:** Configurator Service

* **Input:** Product Selection Data, User Selections  
* **Mode**:   
  * Live user interactions   
* **Output:** Configured Products, Bundles, Solutions   
* **Interfaces:** Product Selector \>\> Configurator \>\> DB  
* **API Call:**  
  * POST /configurator/apply  
* **Database Interaction:** Store configurations, applied rules, and update outcomes  
* **Outcome:** Configured products/bundles/solutions with base price evaluation and ready for overall proposal pricing and further customisation  
* **Challenges:** Rule conflicts, data syncing issues

  #### **Price Evaluation and Rule Engine**

* **Trigger:** Product selection or configuration update  
* **Flow:** Realtime price and rule evaluation

**Module:** Pricing Engine

* **Input:** Product, Configuration Data, Attributes, Contextual info, Customer/quote  metrics/info  
* **Output:** Evaluated Price, Applied Rules  
* **Interfaces:** Configurator \>\> Pricing Engine \>\> DB  
* **API Call:**  
  * POST /pricing/evaluate  
* **Database Interaction:** Fetch rules and constraints  
* **Outcome:** Display of accurate, real time prices, factoring in rules and adjustments with price waterfall  
* **Challenges:** Rule evaluation speed, edge cases for multi-tier pricing

  #### **Negotiation and Deal Room**

* **Trigger:** Sales Rep initiates Deal Room session

**Module:** Deal Room Service

* **Input:** Quote Snapshot, Real-Time Updates  
* **Output:** Negotiation Outcome, Updated Quote Versions  
* **Interfaces:** UI Renderer \>\> Deal Room \>\> Core Quote Service or Pricing Engine   
* **API Call:**  
  * POST /dealroom/initiate  
* **Database Interaction:** Save quote state as new versions  
* **Outcome:** Negotiation room is live, with versioned quotes that track every adjustment  
* **Challenges:** Version control, concurrent updates, handling edge cases of multi-party negotiations

  #### **Versioning and Drafting**

* **Trigger:** Save during negotiation or manual update

**Module:** Versioning Service

* **Input:** Quote Updates  
* **Output:** New Quote Version  
* **Interfaces:** Deal Room (or Quote Service) \>\> Versioning \>\> DB  
* **Database Interaction:** Store each quote version with unique identifiers  
* **Outcome:** Historical tracking of every change in the quote, easily traceable and restorable  
* **Challenges:** Consistency, rollback strategy, handling merge conflicts

  #### **Customer Acceptance and Submission**

* **Trigger:** Customer accepts the quote

**Module:** Approval Service

* **Input:** Accepted Quote  
* **Output:** Approval Request  
* **Interfaces:** Deal Room \>\> Approval \>\> DB  
* **API Call:**  
  * POST /approval/submit  
* **Database Interaction:** Update status in Approval DB  
* **Outcome:** Quote is locked for approval, pending workflow completion  
* **Challenges:** Approval bottlenecks, policy conflicts, multi-stage approvals

  #### **Order Creation and Contract Generation**

* **Trigger:** Quote is Approved

**Module:** Order Management & Contract Service

* **Input:** Approved Quote Data  
* **Output:** Generated Order and Contract  
* **Interfaces:** Approval \>\> Order Management \>\> Contract Service \>\> DB  
* **API Call:**  
  * POST /contract/create  
  * POST /order/create  
* **Database Interaction:** Store Order and Contract details in the database  
* **Outcome:** A fully executed Order and a legally binding Contract are generated  
* **Challenges:** Sync issues with CRM, contract obligations, multi-signatory handling

  #### **Integration with Billing System**

* **Trigger:** Order is generated

**Module:** Billing Adapter

* **Input:** Order Information  
* **Output:** Billing Schedule, Invoices  
* **Interfaces:** Order Management \>\> Billing Adapter \>\> DB  
* **API Call:**  
  * POST /billing/publish  
* **Database Interaction:** Record billing triggers and generate invoice schedules  
* **Outcome:** Invoices are generated and sent to the customer based on the agreed terms  
* **Challenges:** Invoice errors, sync with payment gateways

  #### **Audit, Exception Handling and Corrections**

* **Trigger:** Any failure or rejection during approval, submission, or billing

**Module:** Exception Handler

* **Input:** Error Event, Rejected Quote  
* **Output:** Error Log, Correction Request  
* **Interfaces:** Any Module \>\> Exception Handler \>\> DB  
* **Database Interaction:** Log errors, track corrections  
* **Outcome:** Issues are identified, corrected, and resubmitted for approval or billing  
* **Challenges:** Root cause identification, re-syncing after correction


  

- There will be a client action button that we create on the host CRM Opportunity page \- “*Create a Proposal*”. QE comes with this button, and behind this button we call an API *POST /proposal/create*    
  - Before this API is called, the logic behind this button (JS for example) will populate the entire request body  
  - This request body contains the context:  
    - Customer info  
      - Location info   
      - Contact info  
    - Opp Info  
      - Company info  
    - History and metrics (TCV, ACV)  
    - Price guidance (optional)  
    - And other context attributes   
  - On click, this button will lead to Quote UI \- which is prepopulated with the information captured   
- With the help of context user will be shown templates, if applicable   
  - If there is no template available or applicable then prepopulate the relevant info based on the context   
- Next, if user has additional information to be populated, highlight that, else, open Guided Selling flow (this is where product selection happens)  
- Allow user to select products, plans and see the prices  
  - If template was selected the pre-filtered list of products is shown as per the template  
  - If a context is provided then context based product, plan, and prices are shown.   
  - Context and template can co-exist and influence the product, plans and prices being shown   
  - If template and/or context is not provided then user is directed to a product selector view where in user will have to select the filter values \- this same experience will be needed even if templates/context is provided because the list of eligible products can be long   
- From product selector the user can choose to invoke configurator in case if the proposal/quote involves complex product configuration requirements  
- If configurator is invoked  
- If configurator is not invoked 

## Assumptions

* One Proposal per Opportunity  
* Pricing Engine is stateless and hence, a given set of inputs will lead to same output always  
* Quote version doesn’t mutate but the workflow states captures mutation of the quote

## Terms and Definitions

| Term | Definition | Trigger / Usage | Why It Matters |
| :---- | :---- | :---- | :---- |
| Proposal | Deal level envelope that maps 1:1 with CRM Opportunity and aggregates multiple Quotes. Supports composite quoting. | Created once per deal via Proposal Template. Can be created without a template as well. | Provides single forecast object, aggregated ARR/TCV, top level approvals, unified e-sign packet and seamless composite quoting. |
| Quote | Self contained commercial scenario (new, amendment, ramp, renewal) within a Proposal. | Added via Quote Template; may be several per Proposal. Can be created without a template as well. | Allows variants/alternatives while preserving single deal context. |
| Quote Version | Immutable snapshot of a Quote at a specific point in negotiation. | Triggered on any structural change: add/remove line, price override, discount, term change. Not triggered on UI only edits (e.g., note text). | Enables comparison, deltas, rollback, approval reset, and legal audit trail. |
| Quote Line Item | Defines WHAT is being sold: product, quantity, configuration snapshot, list/net price. | Created/updated by Configurator \+ Pricing. | Serves as an atomic unit for pricing, discounting, and approval thresholds. |
| Quote Charge Detail | Defines HOW the line is billed: charge type (recurring/usage/one‑time), frequency, ramp, tiers. | Auto generated by Pricing Engine after Q Line Item price calc. | Decouples sales intent from billing facts \- feeds Billing Adapter directly. |
| Workflow (WorkflowState/ApprovalTask) | Finite state machine \+ task list governing quote lifecycle (draft  \>\> pending \>\> approved \>\> accepted). | Triggered by Approval Policy thresholds or manual submit for approval. | Ensures governance, SLA tracking, and audit ready status changes. |
| Quote Document | Rendered customer facing document (PDF/HTML) bound to a single Quote version. | Generated post approval, pre-signature via Document Service. | Captures exact commercial terms sent to customer; stored for compliance. |
| Proposal Document? | Proposal can aggregate multiple Quotes; each Quote may have distinct pricing and terms. Document must lock to the specific Quote version that the customer signs. |  | Since Proposal is an envelope, it can be packaged after all the quotes are signed.  It ensures legal clarity; avoids ambiguity when only one of many quotes is accepted. |

## Object Model

| Entity | Key Fields | Notes |
| :---- | :---- | :---- |
| Proposal | id, number, customer\_id, status, base\_currency, total\_arr, total\_tcv, \<total level metrics\> | Roll up object; aggregates metrics from Quotes and acts as an envelope for multi quote scenarios. Captures the deal context.  |
| Proposal Template | id, name, layout\_json, workflow\_json, default\_term\_months | Drives UI (tabs, panels) \+ approver roles.Workflow\_json and layout\_json are the key elements |
| Quote | id, proposal\_id, type(enum), status, currency, term\_start, term\_end, template\_id, version\_counter, version\_index | Actual quote, new purchase, amend, renewal etc.  |
| Quote Template | id, name, default\_line\_items\_json, approval\_policy | Fast creation through templates. Can be combined with Proposal Template object |
| Quote Line Item | id, quote\_id, product\_id, \<plan info \- charge info\>, qty, config\_json, list\_price, net\_price | What is sold. Updated on negotiation  |
| Quote Charge Detail | id, line\_item\_id, charge\_type, frequency, amount (json) | How billed (recurring / usage / one time); amount\_json may include tier table.This is captured for futuristic position \- Line item is quote facing and charge details is billing representation. Can be one to many Note: We may be able to run with QLI without QCD but I am keeping this concept so that we can build the flexibility for billing agnostic CPQ. The separation of sales intent vs billing intent offers that flexibility.  |
| Ramp Schedule | id, line\_item\_id, start, end, qty, unit\_price | Multi period ramps. |
| Quote Version | id, quote\_id, version\_no, author\_id, snapshot\_json, created\_ts | For audit. Snapshot includes Metrics. Immutable |
| Amendment Relation | amend\_quote\_id, original\_quote\_id, delta\_metrics | Capture delta metrics \- a pain point today. |
| Workflow State | id, quote\_id, state, actor\_id, tstmp, comments, rules\_json | Lifecycle \+ approval tracking for quote and captures the outcome and logs of/from every state  |
| Quote Document | id, quote\_id, template\_id, signed\_uri | Generated doc & e‑sign. |

![][image12]

![][image13]

Originals at: [Lucidchart](https://lucid.app/lucidchart/bc433580-c11c-42db-a762-b05b9dd224d6/edit?page=2ePaXZQeJ6y_&invitationId=inv_44ba6b2a-d8c7-4ce6-81c5-38d4de01bc89#) (tab Sequence Diagrams)

ER Diagrams \- draft: [Lucidchart](https://lucid.app/lucidchart/bc433580-c11c-42db-a762-b05b9dd224d6/edit?invitationId=inv_44ba6b2a-d8c7-4ce6-81c5-38d4de01bc89&page=r1Dbu1HiXluv#)

## Sample Template Structure

Template for proposal and quote will describe its workflow and the layout for the UI. Below is a sample and not complete schema just yet:

This concept will evolve further since this leads to the next gen CPQ to be self sufficient. Will work with the UX team to complete the layout schema.

Note that it may affect the object model a slight bit since templates will be stored and the related components will also need to be stored. Structures for the same will be refined in coming iterations.  

| {   "id": "QT\_RAMP\_001",   "name": "Enterprise Ramp Template",   "description": "Used for high value ramped deals.",   "defaultQuoteLines": \[     {"productId": "SAAS\_PRO", "qty": 100, "config": {"edition": "Enterprise"}},     {"productId": "ONBOARDING", "qty": 1}   \],   "layout": {     "panels": \[       {"id": "lines", "label": "Products", "components": \["lineGrid"\]},       {"id": "ramp", "label": "Ramp", "components": \["rampTimeline"\]},       {"id": "review", "label": "Summary", "components": \["metricsBar", "docViewer"\]}     \],     "approverPanel": {"visible": true, "side": "right"},     "headerFields": \["quoteStatus", "approverQueue"\]   },   "workflow": {     "tiers": \[       {"if": "Discount \> 10", "approvers": \["SalesDirector"\], "slaHours": 24},       {"if": "ARR \> 200000", "approvers": \["VPFinance"\], "escalationRole": "CFO", "slaHours": 48}     \],     "autoApprove": false,     "fallback": "RevOps"   },   "fields": \["Opportunity Type", "Region", "Implementation Owner"\],   "relatedSets": \["EntitlementSet", "LegalClauses"\],   "rules": \["DiscountPolicy", "RampConstraintRule"\] }  |
| :---- |

# Metrics Domain

\<WIP\>

# Billing Abstraction Layer

\<WIP\>

# Workflow DSL

\<WIP\>

# Contracts and Orders Domain

\<WIP\>

# Assumptions

- Simple product \>\> feature level comparison 

# Quote Assist and Goal Seeking

# AI Powered Quote Assist and Goal Seeking in Next Generation of CPQ

Navneet Jain  
Aug 2025

## Refer to : [Product Architecture Specs: Agentic Vibe Quoting](https://docs.google.com/document/d/1N0Z5ak-CxLtlsl0CCAtKYqxrp6ReiC0PPrwehs9vlDo/edit?tab=t.0#heading=h.lr36o569tnr6)

# **DRAFT: Work In Progress**

# Introduction

NB but still important: Modern Configure-Price-Quote (CPQ) systems are evolving beyond basic price books, rate cards, product configurations, and manual discounts. 

Sales teams today want to (and must) configure complex product bundles, subscription plans, and services while hitting specific financial targets like Annual Contract Value (ACV), Total Contract Value (TCV), or monthly budget limits. Traditionally, reaching these targets has been a manual, trial and error process wherein sales reps adjust quantities, discounts, or terms until the quote meets a goal. This approach is time consuming and prone to error. There is a clear need for a smarter solution that can *“goal seek”* an optimal quote configuration automatically. 

In other words, CPQ should assist the user by **back solving from the desired outcome** (the goal) to the quote parameters, much like Excel’s Goal Seek works for formulas but on a far more complex scale.

In a world where monetisation is augmented by AI, a next generation CPQ can act as an intelligent assistant to optimise quotes within given constraints. This **Quote Assist** or **Goal Seek** capability would allow a user (or even an AI agent) to specify a business goal. For example \-

*“Achieve a 3 year TCV of $500k while keeping the product mix constant”*   
or *“Limit the customer’s monthly payment to $10k”* 

**It is a must to have the system find the combination of prices, discounts, quantities, and terms to meet that goal.** 

The benefit is twofold: **sales efficiency** (faster, data driven quote iterations) and **commercial optimisation** (maximising revenue or margin within policy limits). The number of variables that impact deal outcomes can be so vast that it’s *“impossible for human analysis to understand the risk that comes with adjusting a few levers in pursuit of a specific goal”* . We are at the confluence of a technology revolution that can solve it. An AI driven approach can sift through these variables and constraints to find solutions that a human might miss, giving organisations confidence that they’re delivering optimised quotes without violating business rules.

This document, written from an Architect’s perspective, proposes a comprehensive design for a Goal Seek/Quote Assist module in Zuora’s next generation CPQ. We will introduce the problem and its facets, explore solution approaches (both functional and technical), discuss the mathematical optimisation models that could be employed, and outline how such a module integrates with existing CPQ and policy frameworks. Competitor offerings and industry trends will be referenced where relevant. 

The goal is to provide product managers, architects, executives, and engineers with a thorough, practical, and forward looking blueprint for an AI powered quote optimisation capability that can disrupt the market.

# The Need for Goal Seeking in Quoting

## Why is “goal seeking” needed in CPQ? 

Traditional CPQ tools excel at applying configured pricing rules (like volume discounts or bundle pricing) and ensuring product compatibility, but they largely rely on the user to manually adjust parameters to reach a desired outcome . For example, if a sales rep has a target price in mind, they might tweak the discount field repeatedly until the quote total matches that target. This is essentially a manual goal seek. 

As deal structures become more complex (recurring subscriptions, usage based charges, multi year contracts with varying billing schedules, etc.), the space of possible adjustments grows exponentially. A rep might ask: 

*“What if we extend the contract term from 1 year to 3 years: how does that impact ACV and cash flow?”*  
 *or “What discount do I need to hit the customer’s budget of $50k annually?”*   
*or “Is there a different product configuration that meets the customer’s requirements at a lower cost?”* 

Each of these questions is a what-if scenario involving multiple variables. Manually exploring these scenarios is inefficient and risks suboptimal outcomes. A **Goal Seek** capability addresses these problems by letting the user specify the goal and letting the system do the heavy lifting to find the solution. 

## Categories of Goals

There are a few key categories of goals that Quote Assist should handle:

* **Price or Revenue Targets:** This includes hitting a specific ACV, TCV, or gross margin.   
  * For instance, a SaaS company might want to ensure a quote yields an ACV of at least $100,000, or a services firm might target a 40% margin on a professional services deal.   
  * The goal seek engine would adjust pricing parameters (unit prices, discounts, one-time fees, etc.) or suggest upsell/cross-sell items to meet that revenue target.   
  * In essence, the user defines *“make the total \= X”* or *“make the margin \= Y%”* and the system finds how.   
  * Some CPQ vendors have started addressing this in narrow ways. For example, Salesforce CPQ allows reps to enter a Target Customer Amount at the quote or group level, which automatically back calculates the required discount to reach that total.   
  * However, **this is limited** to a single discount field adjustment. 

  Our vision is far broader: **multi variable price goal seeking across the entire quote**. Notably, Provus introduced an AI Goal Seek feature that “will generate pricing scenarios for achieving specified revenue or margin goals”. This underscores the demand for intelligent revenue targeting tools.

* **Cash Flow and Payment Goals:** In many industries (especially those offering subscription or financing options), the payment schedule and payment terms are as important as the total price. A customer might say, *“I can afford at most $5,000 per month”* or *“I have a $20,000 capex budget now, put the rest in operating expenses over the next 2 years.”*   
  * Here the goal seek is about cash flow optimisation i.e., structuring upfront vs recurring payments, or adjusting billing frequency, term lengths, and financing, to meet a cash flow profile.   
  * For example, extending a contract term from 2 years to 3 years might lower the annual payment, or introducing quarterly billing could align with the customer’s budget cycles.   
  * The Quote Assist should handle such goals by considering all payment related variables: term duration, billing frequency, financing options (zero upfront vs partial upfront), payment schedule etc.   
  * The outcome might be a rebalanced payment schedule that matches the customer’s budget constraints while still delivering the product value.   
  * Currently, sales reps often do this by hand (e.g., manually splitting charges or offering custom payment terms).   
  * Automating this would be a strong differentiator, especially for solution bundles that combine one time fees (which could be financed) with recurring charges.

* **Product and Entitlements Fit:** Another facet of quote assistance is recommending the optimal product mix or configuration to meet a customer’s stated needs or budget. This is akin to guided selling but with an optimisation twist.   
  * For example, a customer might describe requirements (features needed, usage levels, etc.), and instead of the rep picking a pre packaged bundle, the system can suggest which products, service tiers, or entitlements best fulfill those needs at the best price.   
  * Or conversely, the customer might say, *“I want everything in your Gold package, but I cannot spend more than $50k annually”*.   
  * A goal seek mechanism could then attempt to adjust the package; maybe reduce the quantity of certain add ons or switch to an annual billing with a discount, to meet the budget goal without removing core entitlements.   
  * In essence, this is **configuration optimisation**: finding the right combination of products, options, and quantities that maximises value for both customer and vendor under given constraints.   
  * This overlaps with classic guided configuration and needs based recommendations (often powered by AI analysing past deals or customer usage patterns).   
  * For instance, CPQ systems like Tacton emphasize AI driven product recommendations to ensure every offer is relevant and profitable .   
    Our proposed Quote Assist module would incorporate this by treating certain product choices as variables in the goal seek process i.e. if the goal is cost reduction, it might suggest a cheaper product variant; if the goal is feature maximisation within a budget, it finds the best combination of entitlements that fit the cap.

By addressing these three facets \- **Pricing targets, Cash flow constraints, and Product fit**, a Quote Assist module can cover a wide range of real world use cases. It essentially transforms the quoting exercise from a one shot configuration into a **multi dimensional optimisation** problem, solved with AI/algorithms in seconds. This not only saves time but also systematically **explores options that a human might overlook**, delivering more optimal quotes. The end result is a quoting process that is goal driven rather than purely input driven: the user tells the system what they want to achieve, and the system figures out how to achieve it (if possible).

# Variables and Constraints in Quote optimisation

Enabling goal seeking in CPQ requires clarity on which variables the system can adjust and what constraints must be respected. In a typical quote, there are numerous parameters that affect the outcome (price, cost, value) of the deal. Our solution must identify which of these parameters are allowed to change during the optimisation and which are fixed, either by user choice or by policy. 

## Variables

| Category | Description | Examples |
| ----- | ----- | ----- |
| **Product Selection** | Which products or services are included. | Include optional add on X or not. |
| **Product Configuration & Entitlements** | The specific configuration of a product, such as edition or feature tier, and included entitlements. | Basic vs Premium tier; Standard support vs Premium support. |
| **Quantity** | The number of units, seats, or usage volume. | 500 licenses; 10 devices. |
| **Price Components** | Unit prices or rates for each item. Discounts or markups can apply at line or overall deal level. | System may apply extra discount to meet target price. |
| **Recurring vs One Time Charge Balance** | Balance between one time charges (setup, equipment) and recurring charges (subscription, maintenance). Costs can shift between upfront and recurring. | Reduce upfront fee and increase recurring fee to ease customer cash flow. |
| **Contract Term Length** | Duration of the subscription or contract. Term length affects pricing and discounts. | Longer commitments may unlock discounts; shorter terms may raise ACV. |
| **Billing and Payment Schedule** | Defines billing frequency and payment timing. Impacts cash flow. | Monthly, quarterly, annual, or milestone billing; upfront vs arrears payments. |
| **Financing Options** | Alternate payment structures for large one time costs. | Instead of $30k upfront, pay $1k/month for 30 months. |
| **Entitlement Levels or Service Levels** | Support or SLA levels may be chosen separately from product tier. | Cheaper support levels may reduce total cost. |
| **Quantity based Tier Adjustments** | Adjusting committed usage volume can change unit prices (volume discounts). | Committing to 20% more usage lowers per-unit cost enough to meet target. |
| **Timing Constraints** | Deal terms related to start date or deferrals for cash flow alignment. | Customer defers billing start by one quarter. |
| **Other T\&C** | Commitment, payment terms, commitment layout can alter the pricing and cash flow as well. | Customer wants to pay for $1M annual commitment over 2 quarters.  |

Not all variables will be in play for every scenario. The user (or an admin default) will define which levers are within scope for adjustment. For example, a sales rep might lock certain fields: *“The customer insists on Product A and 100 user licenses, so don’t change those but feel free to adjust term, price, and optional add-ons.”* 

In the user interface, this could be a set of checkboxes or toggles next to each quote parameter indicating whether the Goal Seek engine is allowed to modify it. By selecting the goal type and marking adjustable fields, the user essentially sets up the optimisation problem.

## Constraints

Constraints are rules that the solution must not violate when searching for a valid quote configuration. Constraints come from multiple levels:

* **Product Constraints (Catalog rules):** These are rules like compatibility (certain products must or must not be sold together), configuration rules (if option A is selected, option B must have a certain value), and valid ranges (min/max quantity for a product, allowed subscription terms for a service, etc.).   
  * CPQ systems traditionally enforce these via product rule engines or constraint logic.   
  * The Goal Seek must respect them. For instance, it shouldn’t add an incompatible product just because it’s cheaper, or extend a subscription beyond the max term allowed for that product.   
  * This is essentially the configuration validity constraint set by product management.   
  * We can incorporate these as hard constraints in the solver (e.g., if product A implies product B also included, then any solution must adhere to that).   
  * The use of a constraint solver is natural here \- we can have a bunch of AI constraint solvers based on the category of the constraint and specialisation of the Solver Agent. 

* **Pricing and Policy Constraints:** Every organisation has pricing guardrails. These include discount limits (e.g. “maximum discount on Product X is 30% without higher approval”), margin floors (e.g., “don’t propose deals with less than 10% profit margin”), and overall approval policies.   
  * In a Goal Seek scenario, the system should be aware of these limits so it doesn’t propose an outlaw deal.   
  * For example, if a target price is so low that it would require a 50% discount but policy caps discounts at 40%, the engine should recognise no valid solution exists under current constraints (or flag that it would violate a policy).   
  * Policies might also dictate which variables can change. For example \- maybe sales is not allowed to alter billing frequency for certain product lines, or cannot extend term beyond 36 months without approval.   
  * All such policies should be modeled as constraints. A robust design would include a Policy Configuration interface where business admins define these rules.   
  * It is possible that some already exist in the CPQ (as part of approval workflows or price rules). It might even have a mode to override or relax constraints with proper approvals, but by default it operates within allowed bounds.

* **Customer specific Constraints:** Sometimes a particular customer has negotiated terms that must be honored. For example, a specific client might already have a price agreement in place (perhaps via a contract or an enterprise license agreement) that sets a fixed price for a certain product or a cap on annual price increases. Or the customer simply insists, “We cannot go above $X in year one.”   
  * These effectively become additional constraints on the solution.   
  * In CPQ, customer specific pricing or terms are often handled via contracted pricing or account specific discounts.   
  * The Goal Seek engine should incorporate those inputs as fixed parameters or constraints.   
  * If a customer has a pre-negotiated 20% discount on all software, the engine should work from that adjusted price baseline, not list price.   
  * If the customer’s procurement policy forbids multi year commitments, then extending term is not an option in the goal seek.

* **Organisational or Segment Constraints:** At a higher level, the company might have strategic constraints or playbooks: e.g., *“For deals in EMEA region, no more than quarterly billing”* (perhaps for compliance), or *“We do not allow terms longer than 5 years”*, or *“We don’t finance hardware for customers in certain risk tiers”*. These overarching rules ensure the solution aligns with business strategy and risk tolerance. They would be configured likely at an org level or segment level in the policy engine.

In summary, the policy control must be multi layered and highly configurable, spanning product level, customer level, and global constraints. 

We envision a Policy Rules component that feeds into the Goal Seek engine. It enforces T\&C and other associated rules/constraints. This component could be part of the CPQ admin settings where administrators define: Discount limits per product or product family, margin requirements, allowed ranges for terms, approved financing options, customer exceptions, etc. The Goal Seek engine will treat these as inviolable unless explicitly told that a particular run is exploring beyond policy (and even then, it should flag violations clearly). Maintaining trust is crucial and I strongly believe that users (and approvers) will only adopt an AI suggested quote if they know it won’t accidentally break a rule and cause problems downstream.

**Note**

It’s worth noting that because of constraints, sometimes Goal Seeking may find no feasible solution. In those cases, the Quote Assist should gracefully handle it by informing the user which constraint is most problematic (e.g., “Cannot meet the $50k target without exceeding max discount 30% on Product A”). This could allow the user to relax or request an exception for a constraint, or adjust the goal. The interplay of objectives vs constraints is at the core of the design: the module must obey the *laws (constraints)* of the quote while trying to bend reality to achieve the *goal*. **In technical terms, this becomes an instance of a constrained optimisation or constraint satisfaction problem.**

# Competitive Landscape and Industry Trends

No single incumbent CPQ product today offers the full spectrum of goal seeking we envision (spanning price, cash flow, and configuration simultaneously). This gap is an opportunity for Zuora’s new CPQ to differentiate itself as a true disruptor. By learning from what early movers like Provus and PROS are doing, and going a step further in generalising the solution, we can deliver a first of its kind comprehensive quote optimisation assistant. This will position our CPQ at the cutting edge of the industry, built with AI integration into sales processes. 

Moreover, it aligns perfectly with Zuora’s domain of monetisation: as companies adopt new monetisation models (subscriptions, usage billing, hybrid offerings), they need smarter tools to configure and price those offerings optimally. 

A greenfield implementation allows us to architect this capability natively with AI and advanced algorithms, rather than bolting it on as an afterthought.

# Proposed Solution: Quote Assist Goal Seeking Module

## The mathematics behind this problem

Technically the problem is to create a solver that works on:

- Objective (O): Objective can be to minimise or maximise a value   
- Constraints (C): guardrails, inequalities or equalities that must be satisfied. C is a set of such equations (c1, c2, c3..)  
- Variables (V): values that can be adjusted. V is a set of such variables (v1, v2, v3..)

Quote is modelled as a set of line items (say i line items) with product metadata, costs, tiers, and policy bounds. Decision variables are split into continuous (prices/discounts, amortised amounts) and discrete (include/exclude, tier/plan picks, term options).

**Decision Variables:** 

* Quantity: q where value of q \> 0 (seats, devices, units)  
* Discount: d where discount value is a fraction i.e. % 0% \< d \<= 100%  
* Eligibility: y where item may be excluded or included {0,1}  
* And similarly others such as   
  * Contract terms  
  * Installments   
  * Etc. 

**Constraints**

The solver must always obey business and policy rules, such as:

* Inclusion rules (e.g., Product A cannot be sold without Product B).  
* Quantity rules (e.g., minimum 10 seats, maximum 1,000).  
* Discount limits (e.g., max 20% discount on this product).  
* Margin floors (e.g., gross margin must stay above 15%).  
* Cash flow caps (e.g., upfront must not exceed $5k; monthly must not exceed $3k).  
* Customer specific terms (e.g., fixed price per seat for a named account).  
* Global constraints (e.g., maximum contract term 60 months).

If no solution exists within these constraints, the system must explain which rules conflict with the goal.

**Derived Values (system derives these)**

From those variables, the system calculates:

* Net Price per unit \= List Price × (1 – Discount).  
* Monthly Recurring Charges (R) \= sum of all recurring items (including any financed amounts).  
* Upfront Payment (U) \= all one time fees not financed (this is the minimum, recurring charges may be billed along with on first invoice).  
* Total Contract Value (TCV) \= Upfront Payment \+ (Monthly Charges × Contract Term).  
* Annual Contract Value (ACV) \= TCV ÷ (Contract Term in years).

**Objectives (end goal: solver tries to achieve this outcome)**

Different goals translate to different optimisation objectives:

* Target TCV or ACV: minimise the difference between actual and target contract value.  
* Cash flow alignment: keep upfront and monthly charges within the customer’s budget.  
* Margin maximisation: maximise profit margin while meeting revenue or budget goals.  
* Discount minimisation: reach the customer’s target with the least discount possible.  
* Value maximisation: within a budget, maximise the product mix or entitlements delivered.

**Multi Objective Scenarios**

It is possible for the rep to chain several objectives. Solver should be built for one objective only but in an Objective Chain scenario, all but one objective should be converted to constraints with tolerances (+/- delta). Having done, the final solver can then create scenarios (like Pareto scenarios) by adjusting delta values across constraints. User can denote a primary objective which then is retained as Objective and is not converted to constraint. 

Example: Meet ACV within 2% of X while keeping the discount minimal and minimising the increase of term length. 

This can be understood as lexicographic objectives. On the other hand, there can be objectives that are non sequential but must be achieved all at once. The same strategy can work in those cases as well. 

Challenges 

- Fractional values for discreet quantities such as number of seats  
- Objective Chains  
- 

# Administration

# Functional Architecture: N-CPQ (Administration)

Navneet Jain  
Apr 2025

# Admin Domain

The admin domain has two main components: 

- IT/Ops Admin \- IT admin configures the technical aspects of the CPQ and prepares it for Sales admins to come in and make it ready for Sales reps and deal desk.   
- Sales Admin \- Sales admins are supposed to work with the journeys, templates, and rules. They are the ones who create the blueprints for quotes and quote flows. 

The following depicts a heat map of Zuora platform’s capability against what CPQ needs as a whole. A deeper analysis of capability will be undertaken to ensure the build/extend decisions are taken with due criteria and inline with the future needs \-   
![][image14]

## Architectural guardrails (embed in ADRs)

1. **Config as Source of Truth**:  No CPQ runtime service may cache admin config \> 1 h without subscribing to event invalidation.  
2. **Fail closed**: Access allowed only if RBAC, feature flag and tenant entitlements all evaluate true.  
3. **Immutable Artifacts**: Rule commits and content versions are WORM(Write Once Read Many); supersede, never mutate.  
4. **Layered Secrets**: Admin UI never touches raw secrets; registry only stores Vault references.  
5. **Zero Trust Events**: Webhook payloads signed (HMAC-SHA256) and schema validated on the consumer side.

## Capabilities

| \# | Capability | Role / purpose | Z Platform | CPQ behaviour & data | Engineering outcome |
| ----- | ----- | ----- | ----- | ----- | ----- |
| 1 | **Styling & Branding** | Set logo, colours, company themes, and flow-based colours | No pre-built theming in the Central platform | Stores theme.json, CSS bundle, asset URLs; applied at runtime to CPQ UI & public Deal Room | Theme Service (S3 / CDN), React Admin page, live preview |
| 2 | **3rd Party Integrations** | Configure CRM, e-signature, tax, ERP, Slack webhooks, and Billing systems | Re-use Zuora Workflow connector engine and integration hub/extend | Persists connector secrets, schedules, and retry rules | Connector registry table, secrets vault hooks, prebuilt workflow templates |
| 3 | **Content Hub** | Version contract/ proposal templates, collateral, marketing, CIS | None | S3 doc store \+ metadata; merge field map/html document template mappings for rendering PDFs | Content microservice, version API, diff viewer |
| 4 | **User Preferences** | Default locale/date/number formats, dashboard presets | None in the core platform | Also adds CPQ sections (quoteView, dealScoreUnits) | Extend preference schema, GET/PUT endpoints |
| 5 | **Rules & Workflow Governance** | Git style repo for DMN/JSON/Drools rules; approve/publish WF templates | None in the central platform can own it. | Stores rule branches, runs tests, promotes to prod, and publishes Temporal WF packages | Rule store service, React low-code editor, test harness, audit hook |

| Capability | Role / purpose | Reuse status | CPQ extension required | Engineering tasks |
| ----- | ----- | ----- | ----- | ----- |
| **Identity & SSO (OneID)** | Corporate authentication, MFA | **High reuse** | Propagate auth claims (tenantId, roles) to CPQ  | Gateway mapper, UI link outs to OneID config and link ins to CPQ |
| **Schema Manager** | Custom objects/ fields | **Reuse**  | Register CPQ objects and extensions (Quote, QuoteLine, RuleSet) | Metadata mapping, dynamic serializers, JSON extensions |
| **Observability Config** | Tenant metrics, alert routing | **Reuse** | Emit OpenTelemetry spans with the CPQ namespace | Add trace exporter \+ dashboards |
| **Feature Flags / Entitlements** | Gradual rollout, licensing | **Reuse** | Define cpq.enabled, cpq.beta.\* flags | Register flags; add flag check SDK Understand billing and other 3rd party components, flags, and design a mapping for intelligent feature exposure |
| **Events & Webhooks** | Outbound event delivery | **Reuse** | Publish CPQ CloudEvents (QuoteCreated, ApprovalNeeded) | Schema registry entries; HMAC config screen |
| **RBAC / ABAC** | Object \+ attribute security | **Extend** | Define CPQ roles; add territory ABAC hook (see AWS) | Policy engine table, admin UI role editor |
| **Org Hierarchy** | Territory/ reporting tree | **Extend** | Store sales territory graph; feed ABAC & approvals | Territories ? graph DB for roles and approvals, import API |
| **Tenant / Env Mgmt** | Prod / sandbox cloning | **Extend** | Include CPQ metadata in clone \+ refresh jobs This is different from conventional Zuora tenant management | Clone CPQ config, delta migration scripts |
| **Audit & Compliance** | Immutable log, exports | **Extend** | Tag every CPQ config/quote event with source=CPQ | Adapter to audit events, export scheduler for users |
| **Localisation** | Currencies, FX rates, calendars | **New** | Pricing service subscribes to FX feed; UI picks locale and ensures the correct TZ and language  Locale behaviour as compared to core Zuora needs to be figured out | FX event consumer, localisation of messages, processes?  |

## Tenant & Environment Strategy: Options, Trade-offs, and Engineering Hooks

### Option A – Classic Zuora model

**One tenant \= one environment** (Prod, Central Sandbox, additional Sandboxes on demand)

| Metric | What it gives us | Hidden tax |
| ----- | ----- | ----- |
| **Isolation** | Hard boundary (data, rate limits, feature flags). Perfect for SOC-2 & PCI scoping. | Cross tenant promotion scripts are expensive; can’t run integration tests spanning Prod+SBX data. |
| **Cloning** | Central Sandbox tooling already clones Billing objects. | CPQ has new tables (Quotes, RuleStore). Clone jobs must be extended to include them. |
| **Perf / quotas** | Each env has its own compute pool, thus, noisy neighbour risk is zero across the environments. | Every new SBX spins infra; customers pay $$$. |
| **CI/CD fit** | Same pattern Zuora Billing uses today and hence leads to tooling familiarity. | Multi SBX pipelines \= long feedback loops; hard to fan out dev sandboxes per engineer. |
| **Compliance** | Meets current Zuora audit & export flows OOTB. | None ?  |

**Engineering delta**

1. Extend deployment manager to include CPQ tables \+ S3 assets.  
2. Add CPQ Sandbox rate limits in Governor Limits service.  
3. Write promotion job: SBX to Prod (rule hashes, themes, templates).  
4. Cost model update: CPQ SBX \= N vCPU \+ storage; plug into billing metering.

### Option B – Environment-in-Tenant model

**One tenant** carries **many logical environments** (dev-a, dev-b, ut, stage, prod).

| Axis | What it gives us | Hidden tax |
| ----- | ----- | ----- |
| **Dev velocity** | Engineers spin scratch env in seconds (POST /envs). Perfect for branch-based CI pipelines. | Must add env\_id column to **every** multi-tenant table (Billing side too if we ever share DB). |
| **Cost** | Same vCPU pool; data table partitioning \- hence, cheaper. | Quotas must enforce per-env resource caps; risk of blast radius if ACL misconfigured. |
| **Promotion** | Simple: update env pointer (rule\_hash) from ut to stage to prod. No export/import. | Need a deterministic config bundle generator for audit (hash of all objects). |
| **Compliance** | Data never leaves the tenant leading to a simpler GDPR story. | BUT isolation is logical; SOC-2 evidence must show RLS works. |
| **Perf** | Shared cache, fewer cold starts. | Heavy tests can starve if quotas are wrong. |
| **User mgmt** | Same OneID directory; env claim appended. | Complex UI: Rep sees only prod quotes, Dev sees dev quotes. |

**Engineering delta**

1. Add env\_id (UUID) to the row level security filter in CPQ schemas, default env\_id='prod'.  
2. Gateway header X-Zuora-Env: dev-a stamped by Admin UI toggle.  
3. Promotion service: diff/merge envs \- apply transactional migration; keep change set in WORM.  
4. Rate Limiter: (tenant\_id, env\_id, api\_group) tuple.  
5. Observability: SLO dashboards must split by env; error budgets independent.

### Option C (Hybrid) 

Physical tenant boundary stays; inside each tenant we allow multiple logical envs. Think Prod \+ Central Sandbox (physical) and dev/UT/stage inside the sandbox.

**Why**

* Keeps SOC-2 & noisy neighbour guarantees on prod vs non prod.  
* Gives engineering squads scratch environments without extra infra invoice.  
* Mirrors Zuora Billing’s “Central SBX” purchase model; no packaging change.

**Architectural Limits**

1. **Prod env remains physically isolated**: never share DB node/pool with any sandbox rows.  
2. **Promotion is unidirectional**: sandbox to prod only; prod data cannot leak into non prod except via curated subset (e.g., masked accounts/test copy).  
3. **Config bundle hash**: every promotion produces SHA-256 digest stored in Audit Trail.  
4. **Rate limit sandbox**: 20% of prod quota by default; override requires IT ticket.  
5. **Env expiry**: scratch env auto deletes after 7 days idle (configurable).

## Rules and Workflow Administration

* How do we roll back a bad rule in flight?  
* Can rule versions be pinned per quote?  
* Who approves promotion across envs?

## Integrations

* Failure mode matrix (CRM 5xx, e-sign timeout, etc.)  
* Where are secrets stored & audited?  
* How do we hot swap a cert without downtime?  
* What’s the standard error back to CPQ UI

# Catalog Hierarchy

# Catalog Structure and Hierarchy

Navneet Jain  
Apr/ May 2025

# Goals

Evolve Zuora catalog into a hierarchical catalog (master \> child \> virtual).

- A tenant can run one global master, children such as geo cloned (US, CA, MX) and virtual catalogs for segments (Education, Mining).  
- Any node can nest further categories/sub categories.  
- Each node has its own metadata and can inherit from the parent (display name, SEO slug/description, locale, currency, access rules).  
- A SKU can appear in several catalogs and several nodes.  
- Every product can be assigned to one or more categories, either  
  - **Manually**: a user drags SKU-123 into “Hardware \> Sensors”.  
  - **Automatic**: a category carries a small rule like  
     “include any product where discountPercent \> 0”.  
     When a product meets that rule, the system drops it into that category.  
    - Categories fill via attribute/rule (e.g. “type \== SaaS” \> “SaaS”).  
  - More on product categories later.   
- Product Ranking \- display or recommendation ranking for products, assignment manually and in later versions through rules to boost or bury.

# Use Case (Example)

Assume that a business sells 3 different products (or services) across the globe: 

- Hardware: GPS Sensor, 5G Gateway  
- Software: Fleet Core Platform, Analytics, Monitoring Application  
- Services: Installation, Support

Now the business wants to rapidly launch new geo locations without having to duplicate the products or proliferate the catalog. 

They can set it up as: 

- Catalog: Global Master  
  - Hardware  
    - GPS Sensor  
    - 5G Gateway  
  - Software   
    - Fleet Core  
    - Analytics  
    - Monitoring  
  - Services  
    - Installation   
    - Support  
  - Dynamic (// these will be rule driven nodes)  
    - New Arrivals: Rule: launch date \< 30 days  
    - Top Shelf: Rule: Discount \> 0

So in this example the concepts in play are: 

| Concept | Where you see it |
| ----- | ----- |
| Category / sub category | “Hardware \> GPS Sensors” |
| Dynamic category | “Top Shelf” & “New Arrivals” \- these are automatically populated based on rules.  |
| Single SKU, many nodes | GPS Sensor lives in GPS Sensors and appears into the Top Shelf the moment it gets 10 % off. |
| Child Catalog | Read below to understand the child catalog concept |

| Child catalog | What it inherits | What is overridden |
| ----- | ----- | ----- |
| Canada (type: CHILD) | Entire tree, English copy | Currency CAD, locale en-CA / fr-CA. Prices converted, French copy auto generated; everything else identical. |
| Mexico | Entire tree | Currency MXN, locale es-MX. Gateways product maybe hidden because that product cannot be sold in Mexico. |

The hierarchy stays, but currency, language, and product visibility can change per child.

A child catalogue is represented as a Node in the Node/Catalog setup, with a defined parent. Typically the master catalogue will be the parent. Child catalogues inherit structure, schema fragments, and product assignments from their parent node. Local variations such as language, currency, and product visibility are introduced using the overrides property on the Node.

**Virtual Catalog: TBC**

## SKU Propagation 

SKU: GPS-SENSOR-EU  
Attributes: region=\["EU","NA"\], discountPercent=10, segment=\["B2B","Education"\]

(Assume that segment is an attribute)

| Catalog / node | Why it appears there |
| ----- | ----- |
| Global \> Hardware \> GPS Sensors | Manually assigned. |
| Global \> Dynamic \> Top Shelf | Matches rule discountPercent \> 0\. |
| Canada \> Hardware \> GPS Sensors | Inherits manual assignment; CAD price auto generated using FX. |
| Education \> Hardware \> GPS Sensors | Catalog root rule segment=="Education" is true. |

# Thought Board for Achieving Catalog Hierarchy

| Capability | Comments | Example |
| ----- | ----- | ----- |
| Versioning & rollback | Immutable catalog\_version with hash.  Publish and rollback capability.  Each published version of the catalogue is treated as an immutable, point-in-time snapshot. This is achieved by generating a new catalogue\_version\_id that references specific, versioned Node definitions and Product records. Rollbacks are implemented by simply redirecting the live system to point to an earlier catalogue\_version\_id, enabling rapid restoration without requiring data reprocessing or transformation. | Discount was rolled out incorrectly \> leads to rollback in one click (to previous version). |
| Locale & currency inheritance | Node inherits locale\[\], currency\[\] from nearest ancestor unless overridden.  | CA child defaults to en-CA and CAD; virtual catalog overrides locale only. |
| Rule inheritance | Rules cascade down the tree; children can add or mask a parent rule. Each Node may have a set o attributes that are applied to the constituent products/plans and hence product browsing can leverage that.  The same can be implemented using product rules. Similarly, the product allocation (or plans) to a certain node should also be governed by rules (manual as a pressure release mechanism). These rules are used during the materialisation process to determine which products should be included under that Node. | Master rule “exclude BETA SKUs”; Canada child masks it for internal testers. The rules operate on product metadata (attributes, tags, or custom fields), supporting use cases such as “include products where discountPercent \> 0” or “exclude products with status \= End-of-Life”. |
| Schema extension via category | Category can attach **schema fragments** (extra custom field set) that become available on member SKUs. These fragments extend the product data model for any product associated with that Node. Schema fragments are inherited by all descendant Nodes and are merged as part of the product schema initialisation process. This enables differentiated data models for categories (e.g. hardware vs software) without fragmenting the global schema. | Node “Hardware” adds wattage, ip\_rating; only those SKUs expose the fields in API. |
| Feature/ Entitlement propagation | Node can carry entitlement bundles (features) automatically granted when any SKU under it is sold. Each node can have overriding capabilities. This allows for contextual enrichment, such as including a priority support feature for all products in a “Business Class” category without altering the core product definition. | “Premium Analytics” node adds feature.analyticsPro. \#**Future**  |
| Lifecycle scheduling | Node can have active\_from / active\_to; the subtree below a given node will be hidden beyond active\_to Note: I haven’t used start/end date as used elsewhere in Zuora for explicit clarity of such a field.  | Seasonal sub category (Black Friday) expires on Oct 1\. |
| Segmentation ACL | Node level ACL (segment, channel, tier). Evaluated in JWT claims. These access filters are evaluated at query time and enable dynamic, user specific segmentation (e.g. visibility limited to users in the government sector or a specific geography). The filters are based on attributes present in the user's context (e.g. JWT claims or session attributes).  | “Gov Only” node visible to users with segment \=gov. In Zuora this can be mapped to account or subscription.  |
| Search facets & analytics | Node path materialised in search index. Store the discovery path (or click path) (node\_id, product\_id, ….\`). | This can help in boost/bury |
| Bulk ops & CI/CD | YAML/JSON bundle format for deployment manager or operations such as promotions. |  |

| Rule of thumb: the Catalog hierarchy never touches tiers or rate cards directly; it references up to the Charge level, leaving detailed pricing to the existing engine, as is. |
| :---- |

# Object Model Evolution 

Core objects remain as is. 

| New object (DB table) | Purpose in the new hierarchy | Key columns / structure | How it links to existing Zuora objects | Sample data |
| :---- | :---- | :---- | :---- | :---- |
| Catalog | Top level container: “TeleSense Global”, “Canada Child”, “XXX Virtual” | catalog\_id (PK),  Type (master/child/virtual)Parent\_id, Defaults:  {locale\[\], currency\[\]} | Pure wrapper. Does not touch Product or PRP tables \- just groups nodes. | catalog\_id \= Global, type \= master, default\_locale \= \["en-US"\] |
| Catalog\_ver | Immutable snapshot each time someone publishes a catalog; enables rollback | pub\_id (PK), Catalog\_id, Version\_num, (use the versioning concept from catalog)  Hash (SHA 256?),  published\_at | Downstream (CPQ, Storefront) call specific hash so they always use a known snapshot Alternatively version can be retrieved by timestamp or version number. |  |
| Node | One row per point in the tree : master root, category, child root, dynamic, etc. | node\_id (PK), Catalog\_id, path (ltree) Type (see next table), Meta\_json (slug, SEO, etc.) | Does not hold price. Links to content only. | node\_id \= "Hardware.GPSSensors", type \= category |
| Node\_ruleset | Optional rule that tells a node which Rate Plans it should auto include. Other rules can be added  | Rule\_set\_id (PK) Node\_id, Dsl\_json  version | Evaluates against Product Rate Plan attributes or Rate Card fields | Rule JSON: discountPercent\>0 for “Top Shelf” node |
| Node\_schema | Additional attributes/ custom field schema extension/ fragment automatically attached to SKUs in this node | extension\_id (PK) node\_id   Json\_schema // consider collapsing it within Node | Stored via Zuora Custom Fields engine under namespace x\_catalog\_… | Adds wattage & ip\_rating fields to all hardware PRPs |
| Node\_acl | Segment / channel visibility rules (such as “Gov only”) | Acl\_id (PK), Node\_id, Segment, Effect // can be enforced using access rules. ACL itself can be done away with and we can leverage rulesets with type “ACL” | Can be integrated with OneId upon some enhancements so that the relevant information is captured in OneId (at entity or org level) JWT claims supplied by OneID then can be matched and nodes can be shown/hidden CPQ/storefront render | node\_id \= Compliance.HIPAA, allow segment=“Gov” |
| Assignment | Connects a NODE to a PRPId. Also shows why it got there | Node\_id (FK), ProductratePlanId (FK), Source \= manual | Rule priority |  |

| Node Type  | Label | Typical purpose | Relation to legacy data |
| :---- | :---- | :---- | :---- |
| masterRoot | Master Catalog | Global blueprint tree | New container only |
| childRoot | Child Catalog | Geo clone with currency / locale overrides | New container only |
| virtualRoot | Virtual Catalog | Segment / campaign lens (Education, Mining, etc.) | New container only |
| category | Category | First merchandising bucket | Replaces informal “Product Category” custom field |
| subcategory | Sub category | Deeper bucket inside a category | Same as above |
| dynamicCategory | Auto populated | Populates via NODE\_RULESET | Was impossible in flat list |
| aiCollection | AI generated categories/collections | Populated at read time by recommendation engine | Entirely new |
| bundleNode | Bundle | Pre assembled kit priced as group; still resolves to existing PRPs | PRP groupings are currently done manually now native. Once bundle capability is released, we can roll into this as well.  |
| solutionSet | Solution / BOM | Cross product dependency tree for configurator | New |

## Notes and Design Considerations

* **ASSIGNMENT** references ProductRatePlanId, not Product.  
  * Helps manage the granularity ie lets the users expose “Core Monthly” but not “Core Annual” if needed.  
  * **NODE** carries meta\_json (slug, SEO, locale), **never price**. Prices stay on PRPC, Charge, Tier, or Rate Card objects.  
* **Rate Card** context  
  When a CPQ or self service/storefront viewer resolves a ProductRatePlanId, it also needs to know the charges and relevant rate card records that apply based on the context of the end customer/user (country, industry, etc.).  
  The catalog with BCS supplies the structure and context; and the rate card supplies the price/numbers.  
* **Schema Extensions/Fragments**  
  NODE\_SCHEMA attaches extra attributes/custom fields to any PRP/PRPC that lives under that node (e.g., “wattage” for hardware). Those extensions will be stored in Zuora’s existing Custom Fields engine under a namespace like x\_catalog\_.

## Why “NODE” instead of “Category”

Using a single, type flagged concept and hence, object, means every current and future shelf/category/collection (static, rule driven, AI generated, bundle, seasonal, etc.) is expressed the same way. Hence, traversal, rule evaluation, ACL checks, and versioning all share one piece of code. Business users still see clear names (“Category”, “Virtual Catalog”); the generic term *NODE* lives only in storage and APIs.

- Allows for extensibility: Two fixed levels force new tables every time we invent a different layer (say shelf or layer?) (e.g., “AI picks”, “Bundle”, “Virtual root”)  
  - A NODE row can declare any type string, so new merchandising ideas are an add data operation, not a change schema project.  
- Uniform traversal: FE code would need special branching logic (first hop to catalog root, then down to category, then maybe jump to a dynamic layer).  
  - Every element in the tree is a NODE, so the UI just follows parent\_node\_id from root to leaf without caring what kind of node it meets.  
- Rule & ACL reuse: Separate tables would require duplicate rule engines and permission checks for each table.  
  - A single rule/ACL service attaches to NODEs, so the same logic secures a category, a virtual catalog, or a dynamic “Top Shelf” layer.  
- Versioning & rollback: With multiple tables, creating a catalog snapshot or rolling back changes means diffing several datasets.  
  - Publishing is simply “snapshot all NODE rows under this catalog\_id.” One hash, one rollback step.  
- Future AI collections: AI driven layers (“Customers like you buy…”) don’t map to a classic category/sub category concept.  
  - They’re stored as NODEs with type="aiCollection" and a resolver reference. No new schema, just new data.

# Contracts

The Contracts as documented below can be refined. This document gives direction and high level specs of what is required. 

| Verb and Path | Payload / params | Notes |
| ----- | ----- | ----- |
| POST /commerce/catalogs | create Master / Child / Virtual |  |
| GET /commerce/catalogs/{catalogId} | ?version= or date or tag? | read tree |
| POST /commerce/catalogs/{catalogId}/clone | clone to child | emits CatalogCloneRequested event |
| POST /commerce/catalogs/{catalogId}/publish | publish draft to live | emits CatalogPublished event |
| POST /commerce/catalogs/{catalogId}/rollback | rollback to sha256 | emits CatalogRolledBack |
| DELETE /commerce/catalogs/{catalogId} | soft-delete |  |
| POST /commerce/nodes | { "catalogId", "path":"Hardware.GPS", "type":"category", "meta":{…} } | Path must be unique in catalog |
| PUT /commerce/nodes/{nodeId} | patchable: meta, type | Changing parentPath triggers subtree move // not supported |
| DELETE /commerce/nodes/{nodeId} |  | Orphan children auto-adopt parent unless cascade=true |
| PUT /commerce/nodes/{nodeId}/rule | full dsl\_json with parameters, conditions, attributes | Upserts rule \- version increments internally |
| DELETE /commerce/nodes/{nodeId}/rule |  | Node becomes static |
| POST /commerce/rules/preview | { "rule": { "expression":"discountPercent \> 0" }, "sampleRatePlanIds": \["RP-123","RP-456"\] } |  |
| PUT /commerce/nodes/{nodeId}/product-rate-plans/{prpId} |  | Can have a bulk end point as well |
| DELETE /commerce/nodes/{nodeId}/product-rate-plans/{prpId} |  | Can have a bulk end point as well |

# Options

An alternative design is to do away with the concept of Nodes and Catalogs, but introduce “Categories”. Categories can be nested and similar to nodes, will carry a schema extension and a ruleset. Products/PRPs will be associated with categories. The downside in this approach is that it is rigid and every new layer then either has to become a category or a new object. This can however be a faster path to release.   
In such a model, we will drop Catalog, Catalog Version, and replace all possible capabilities of Nodes with capabilities for Category. 

# Use Case Coverage

| Use Case | Comments wrt to design |
| ----- | ----- |
| Soft bundle / marketing package (price \= sum of parts) | Create a bundleNode; manual or rule based ASSIGNMENT lists its member PRPs. |
| Solution selling (Hardware \+ Software \+ Services shown as a package) | Node type solutionSet; hierarchy can nest unlimited levels, and Node\_metadata can carry the copies.  |
| Simple dynamic layers (Top Shelf, New Arrivals) | dynamicCategory \+ NODE\_RULESET DSL |
| Segment / channel based fencing/restrictions  | NODE\_ACL (segment, channel) |
| Schema inheritance (example \- extra attributes only for hardware) | NODE\_SCHEMA fragment auto adds custom fields to PRP/PRPC. |

### Search Facets and Ancestry Materialisation

During catalogue materialisation, the full ancestry path of each product is recorded and indexed. This path is embedded into the search index and used to power faceted filtering, breadcrumb navigation, and ranking algorithms (e.g. boost or bury logic). It also enables precise analytics on discovery paths and click-through behaviour.

### Bundles and Solution Sets

Nodes with metadata of type `bundle` or `solutionSet` support complex packaging models. A `bundle` node represents a predefined group of products sold as a single unit. A `solutionSet` node is used to support product configurators and solution-selling, where each child node represents an option group or selectable component (e.g. hardware, software, services).

### Schema Resolution at Product Creation

To resolve the circular dependency between schema inheritance and product filtering, the system decouples schema derivation from the catalogue structure by freezing a product's schema at the time of creation. This ensures that by the time a product is evaluated for inclusion via filters, its schema is complete and immutable.

#### Workflow

1. Select Base Categories  
    During product creation, the user selects one or more base Nodes (categories) where the product should reside.

2. Merge Schema Fragments  
    The system traverses the ancestry of all selected base Nodes and aggregates all `schema_definition` fragments. These are merged into a single schema definition. If conflicts arise (e.g. same field with conflicting types), the process fails with a validation error.

3. Generate Merged Schema ID  
    A deterministic key is computed (e.g. using a hash of sorted node IDs and versions) and used to check for an existing merged schema. If one exists, it is reused; otherwise, the merged schema is stored and assigned a new ID.

4. Link Product to Schema  
    The new product version is permanently linked to the resolved `merged_schema_id`, which becomes the authoritative schema for that version.

5. Populate Attribute Values  
    The user is presented with all fields defined in the merged schema and can populate values as part of the product creation process.

# Object Model Evolution

# Object Model Evolution 

[https://lucid.app/lucidchart/1fa0e543-c555-4d98-8809-7a9c9be12f63/edit?invitationId=inv\_899e17ba-3313-4090-9289-a622d456c39d\&page=-AHue6fegAec\#](https://lucid.app/lucidchart/1fa0e543-c555-4d98-8809-7a9c9be12f63/edit?invitationId=inv_899e17ba-3313-4090-9289-a622d456c39d&page=-AHue6fegAec#)

# APEX Conversion

# APEX Conversion Thought Process

Zuora’s legacy CPQ was delivered as a Salesforce managed package , meaning custom business logic (for pricing, product rules, validations, etc.) was often implemented in Salesforce Apex code. Apex is Salesforce’s proprietary Java like language used to extend platform functionality. These customisations were tightly coupled to Salesforce i.e. they run only inside the Salesforce org and rely on Salesforce data structures (SObjects, SOQL queries, etc.). 

Now, we are developing a new CPQ solution outside Salesforce, eliminating the Salesforce dependency. The challenge is migrating the existing Apex based logic to a new environment so that Salesforce is no longer required.

# Principles and Constraints

Key constraints and goals for this migration include:

* **No/Low Code Preferred:** Ideally avoid hand writing a large codebase again. A configuration driven or automated solution is desired to reduce maintenance and reliance on specialised Apex developers.  
* **Standalone Abstraction Layer:** The solution should be an independent layer (e.g. a service or engine) separate from the CPQ application, so the logic isn’t locked into another monolithic system. This makes it easier to modify or replace in the future without affecting core CPQ.  
* **AWS Preferred:** The target runtime should preferably be on AWS (for scalability and familiarity), but open to other platforms as needed.  
* **Preserve Logic 100%:** The migrated solution must replicate exactly the same business rules and outcomes as the Apex code. Quotes configured in the new CPQ should behave identically to the legacy system.  
* **Testable & Deterministic:** The new logic layer should be fully unit testable and yield deterministic results (given the same inputs, it produces the same outputs every time, with no hidden state or randomness). This is crucial to validate that the migration was successful and to ensure reliability going forward.

Migrating off Apex is challenging because Apex code cannot run outside Salesforce’s cloud. Apex is executed on Salesforce’s multi-tenant platform (via an interpreter that ultimately runs on a Java VM ), so we need to **rehost or rewrite** that logic. 

## Challenges in Converting Apex Logic

Before diving into solutions, it’s worth noting what makes migrating Apex tricky:

* **Salesforce Specific APIs:** Apex code often uses SOQL (Salesforce’s query language) and references Salesforce objects (e.g., Quote, Account) and fields. These calls must be replaced with equivalent data access in the new system (e.g., via Zuora APIs or a new data model).  
* **Data Access:** Apex often uses SOQL queries and operates on Salesforce objects. In the new system, the data (products, quotes, etc.) will reside in Zuora’s own database or other microservices. The translated code must call the appropriate APIs or database queries to fetch data.   
* **Salesforce Libraries:** Apex has builtin libraries (for example, Math, String methods, etc.) which Java also has, so most will map directly. For sending emails or callouts, we can use standard languages libraries or AWS services (e.g. Amazon SES for emails, or simply have the logic call external HTTP endpoints using Apache HTTPClient or similar).  
* **Stateful Context:** Salesforce manages the context of the APEX and the component it runs in. All of this needs to be performed by the newly built mechanism.   
* **Governor Limits and Patterns:** Apex code may have been written in a certain way to avoid Salesforce governor limits (bulk-ification patterns, etc.). In a standalone environment, those limits vanish, but the logic might need slight adjustments for efficiency.  
* **Triggers vs Event Handling:** In Salesforce, Apex triggers fire on data changes. Outside Salesforce, we may need an event-driven mechanism or explicit service calls from the CPQ app to invoke the logic at the right time (e.g., “on quote update, call external logic service”).  
* **Testing Parity:** Salesforce required Apex unit tests for deployment; those tests can be repurposed as validation tests for the new solution. Ensuring all those tests pass in the new environment is a good measure of success.  
* **Simulating Component Registration:** To preserve a metadata-driven approach, we can implement a plugin registry within our solution.

# Solution Options

## **Option 1: Automated Apex Code *Transpilation* to AWS Microservices**

One approach is to convert the Apex code into an equivalent in a standard programming language (such as Java or Node.js) and deploy it on AWS as independent services or serverless functions. Apex’s syntax and semantics are very close to Java, making direct translation feasible . In fact, Apex runs on a Salesforce managed Java runtime under the hood, which indicates that conceptually Apex logic can be expressed in Java .

* Use a code transpilation tool or process to translate Apex classes into Java classes (or another language of choice). This can be done via open source projects or AI-assisted converters. E.g. \- [https://github.com/tzmfreedom/apex2java](https://github.com/tzmfreedom/apex2java)  
* Can also consider \- [https://www.codeporting.ai/](https://www.codeporting.ai/)   
* Handle Salesforce specific elements during conversion:  
  * Replace SOQL queries with calls to the new CPQ’s API or database queries. This might be semi-automatic: for instance, a query List\<Account\> acc \= \[SELECT Id, Name FROM Account WHERE ...\]; would need to call the Zuora (or CRM) API to fetch account data instead.

  * Remove Apex only constructs (like @AuraEnabled annotations triggers context, etc.) or replace them with standard equivalents.  
  * Such constructs must be known and there can be different constructs that are used across implementations.   
* Deploy on AWS: The converted code can be packaged as microservices. Options include:  
  * AWS Lambda Functions: Deploy each piece of logic as a Lambda, which the CPQ system can invoke via an API Gateway or direct SDK calls. This is scalable and requires no server management.  
  * Containerised Services: If the logic is complex or needs to maintain state between calls, one could containerise the Java application (e.g., on AWS Fargate or Kubernetes). But most CPQ rules logic should be stateless and suitable for Lambdas.  
* Preserve and test logic: Because this is essentially the same code just in a new form, it preserves the logic exactly. We would bring over all the conditional logic, calculations, and data manipulations as-is. The migrated code can be validated by running the original Apex unit tests (rewritten in JUnit or another testing framework) to ensure it produces identical outcomes.  
  * Apex should already have unit tests.

## Option 2: No Code Business Rules Engine on AWS

Another strategy is to forgo writing code entirely and express the CPQ customisations in a business rules engine or workflow system. Many CPQ customisations boil down to rules: “if certain conditions are met, then take some actions (set a field, add a product, adjust a price, throw an error)”. Instead of hard coding these in Apex or any language, we can use a declarative rules platform where administrators or analysts configure the logic via a UI or configuration files.

* Choose a rules engine that can be hosted on AWS. We can consider using ZRules as well.  
  * For example, OpenRules is a solution where business logic is defined in Excel spreadsheets or tables and then deployed as decision services on AWS (including as AWS Lambda functions or REST endpoints) .   
  * Similarly, AWS Marketplace offerings or SaaS like DecisionRules.io, Nected, or Decisions provide no-code rule authoring and AWS deployment .  
  * Not ZRules is pretty much based on DecisionRules so that may work.  
* Model the Apex logic as a set of rules:  
  * Each Apex “if/then” or business check can become a rule condition and an associated action. For instance, an Apex snippet that says *“if product X is added and region is Y, then automatically add product Z”* would be configured as a rule with condition *Product \== X AND Region \== Y* and action *Add Product Z* .  
  * Calculations (like setting a discount or price) can be done by rules that compute a value based on inputs (some engines allow formula expressions or script in actions).  
  * Validation logic (“if condition not met, throw error”) becomes a rule that triggers a validation message to the user.  
* Use the rules engine’s execution platform to run these rules during quoting. For example, a rules engine service could be invoked whenever a quote is being edited or finalised.   
  * The CPQ system (outside Salesforce) would call the rules engine, pass in the quote data (products, customer info, etc.), and the engine returns any adjustments or errors.   
  * This is conceptually similar to how Zuora’s legacy CPQ had an internal rules engine for product selection and pricing in Salesforce, except now it’s an external, standalone engine.  
* **Maintain via configuration:** Once set up, business users or solution architects can adjust rules via a GUI (or by editing a spreadsheet for OpenRules).   
  * No Apex or code knowledge is needed. Rules are typically written in a semi natural language or simple condition-action format.   
  * For example, Subskribe introduced a domain specific rule language (“Zeppa”) precisely so that non engineers can configure quote behaviors instead of writing Apex code .   
    * Their philosophy is that a tailored rules language is a *“scalpel”* for SaaS quoting logic, whereas Apex was a *“blunt hammer”* requiring heavy developer involvement .  
  * These rules can be configured using NLP as well.   
* **Testing and determinism:** Each rule or decision table can be tested with sample inputs. Many rule engines allow simulation of rules to see which ones would fire for a given scenario.   
  * We can reuse scenarios from Apex tests to ensure the rules produce the same outcomes. Because the rules are formally defined, given the same input, the engine will deterministically execute the matching rules.

### Option 3: Domain Specific Abstraction Layer (Custom Low-Code DSL)

A third approach is to create a custom abstraction layer, essentially, design your own domain specific language or configuration schema for the CPQ logic, then build a runtime to execute it. This is somewhat a middle ground: instead of using a generic third-party rules engine, you craft a solution tailored exactly to the types of customisations in your legacy Apex. It’s like building a mini rule engine specifically for your needs, which can then be used going forward for any new logic as well.

# CPQ DSL

# CPQ \- Domain Specific Language

Sep/Oct 2025  
Navneet Jain

[**Scope, intent, and alignment	3**](#scope,-intent,-and-alignment)

[Alignment to the mental model	3](#alignment-to-the-mental-model)

[Lossless core vs best value extras	3](#lossless-core-vs-best-value-extras)

[Lossless core	3](#lossless-core)

[Best value extras (portable where supported or otherwise degrade/limit gracefully)	4](#best-value-extras-\(portable-where-supported-or-otherwise-degrade/limit-gracefully\))

[**Data Model	4**](#data-model)

[**Concepts and DSL	4**](#concepts-and-dsl)

[Some High Level Conundrums	4](#some-high-level-conundrums)

[Configuration model in one view	4](#configuration-model-in-one-view)

[Package (Header: Meta, rounding, time, effective dating)	5](#package-\(header:-meta,-rounding,-time,-effective-dating\))

[Price Books (which prices, and when)	6](#price-books-\(which-prices,-and-when\))

[Offers & Components (commercial view over the technical catalogue)	7](#offers-&-components-\(commercial-view-over-the-technical-catalogue\))

[Attribute Based Pricing	8](#attribute-based-pricing)

[Schedules (ramps, holidays, protection)	9](#schedules-\(ramps,-holidays,-protection\))

[Rules	10](#rules)

[Approval Policies	11](#approval-policies)

[Rules & Approvals (Together) (policy, not UI)	12](#rules-&-approvals-\(together\)-\(policy,-not-ui\))

[Scenarios & Quotes (options and the priced instance)	12](#scenarios-&-quotes-\(options-and-the-priced-instance\))

[Proposal (buyer snapshot)	13](#proposal-\(buyer-snapshot\))

[Agreements (contract container)	14](#agreements-\(contract-container\))

[Agreement & Subscriptions (the contract and what runs)	14](#agreement-&-subscriptions-\(the-contract-and-what-runs\))

[Commitments & Prepayments (with clear scope)	15](#commitments-&-prepayments-\(with-clear-scope\))

[Payment Schedules (instalments & milestones)	17](#payment-schedules-\(instalments-&-milestones\))

[Deal Room (buyer collaboration)	17](#deal-room-\(buyer-collaboration\))

[Adapters (interoperability contract)	18](#adapters-\(interoperability-contract\))

[Events (audit trail)	18](#events-\(audit-trail\))

[TBC	19](#tbc)

[Complete Example	19](#complete-example)

[Schema	27](#schema)

[**Challenges, Conundrums, and Open Thought Threads	27**](#challenges,-conundrums,-and-open-thought-threads)

[Impedance mismatch between applications and Adapter conundrum	27](#impedance-mismatch-between-applications-and-adapter-conundrum)

[Schedule Vs Quote Line Item: Time Slices	27](#schedule-vs-quote-line-item:-time-slices)

[Proposal & Scenarios	28](#proposal-&-scenarios)

[**Appendix	29**](#appendix)

[Why Package	29](#why-package)

This document codifies a JSON first DSL for the CPQ platform. It defines each concept’s shape, then shows a combined, e2e package. It intentionally aligns with the general entity models: Quote, QuoteLineItem, Ramp/RampInterval, Approval/ApprovalItem, Scenario, Proposal/QuoteDocument, DealRoom, Extended Schema, OrderActionType etc so the runtime and DSL stay close.

**Pre Read Notes** 

- This is for now an aim at V1 and feedback will be considered to evolve it to be a comprehensive DSL.   
- Terminology is subjective. As such, if you have any suggestions on terms/taxonomy then please leave your suggestions at the bottom of this document.   
- Some items are open and being thought through. You will see a TBC section and a section documenting the conundrums. Please feel free to provide your inputs, should there be any. 

# Scope, intent, and alignment {#scope,-intent,-and-alignment}

The objective is to provide a vendor neutral, declarative language that captures “offers”, pricing, time slicing, rules/approvals, scenarios, proposals and buyer collaboration, and can be losslessly exported to Zuora Orders, Salesforce CPQ, and others as needed.

## Alignment to the mental model {#alignment-to-the-mental-model}

* Commercial **Offer** fronts the technical catalogue (Product \> ProductRatePlan \> ProductRatePlanCharge).  
* **PriceComponent** equals a priced charge instance (recurring / one‑time / usage).  
* **Schedule** generalises Ramp/RampInterval generalised to any mutable field.  
* **Quote/QuoteLineItem** hold configured instances.  
* **Scenario** groups quotes into options.  
* **Proposal** publishes the chosen scenario with documents and clauses.  
* Accepting a proposal instantiates an **Agreement** with one or more **Subscriptions**.  
* **Approvals** are artefacts/output from rules, not UI click paths.  
* **Commitment / Commitment Fund / Pool** become explicit monetary commitments with drawdown and/or minimum spend semantics.  
* Deal Room is the system of engagement for buyers (and potentially internal approvers too). 

## Lossless core vs best value extras {#lossless-core-vs-best-value-extras}

### Lossless core {#lossless-core}

The objective is to have a painless roundtrip across engines. 

* Package/versioning, rounding, timezone  
* Rate cards/Price books with effective dating  
* Offers/components mapping to the technical catalogue  
* Price components (recurring/one‑time/usage) with tiers/blocks/volume, min commit, overage, currency  
* Schedules (time slicing) for quantity, unit price, discounts  
* Constraints (requires/excludes/cardinality)  
* Quote with term, lines, overrides, and pinned versions  
* Rules with deterministic priority and approval emissions  
* Approval policies (stages, ANY/ALL, SLA, escalation)  
* Adapters with capability declarations  
* Event stream (audit)  
* Extensions (namespaced custom fields)

### Best value extras (portable where supported or otherwise degrade/limit gracefully) {#best-value-extras-(portable-where-supported-or-otherwise-degrade/limit-gracefully)}

* Attribute/Formula pricing  
* Pooled/drawdown usage with rollover  
* Proration, free periods, price protection at renewal  
* Clause injection & playbooks (CLM aware)  
* Deal Room access policies and Mutual Action Plans  
* Scenario analytics and deltas

# Data Model {#data-model}

Working copy: [Lucidchart](https://lucid.app/lucidchart/1fa0e543-c555-4d98-8809-7a9c9be12f63/edit?invitationId=inv_899e17ba-3313-4090-9289-a622d456c39d&page=-AHue6fegAec#)

# Concepts and DSL {#concepts-and-dsl}

## Some High Level Conundrums {#some-high-level-conundrums}

### Configuration model in one view {#configuration-model-in-one-view}

The top level construct for us is Proposal \- one that the buyer signs and is all encompassing.   
But, as you would see, we are not dumping everything into the proposal. Why not dump everything into the proposal?   
Because proposals are buyer snapshots. The calculation contract (catalogue versions, rules, price books, rounding, timezone) must be decided and then pinned so numbers stay reproducible.

**Where do rounding / timezone live if they rarely change?** In practice, they live as defaults at the tenant and customer level, with a clear override hierarchy:

* **TenantConfig**: organisation wide defaults (e.g., rounding, default timezone)  
* **AccountProfile**: customer specific overrides (e.g., timezone “America/New\_York”, bill cycle preferences)  
* **Package**: versioned commercial artefacts (offers, rules, price books) and *defaults* only if neither tenant nor account specify them. This is introduced into this piece of work. 

**Evaluation context (what the engine actually used):**

* Every Quote pins pinnedContext (the effective rounding/timezone/priceBook and package versions used).  
* Proposals reference the quote(s). Agreements/Subscriptions inherit the pinned context on execution.

This keeps customer level behaviour stable while still giving us a versioned package for offers/rules/price books.

## Package (Header: Meta, rounding, time, effective dating) {#package-(header:-meta,-rounding,-time,-effective-dating)}

**Why Introduce Package?**

Short answer: Given above. More details here and then in Appendix. 

Initially, my thought was to elevate Proposal to the overarching level but then I have decided to introduce a Package/Header concept. The package header (meta, rounding, time, effective dating) is infrastructure for calculation and interoperability, while a proposal is a buyer facing snapshot. If we bury engine wide settings inside the proposal, we lose determinism, portability, and reuse across quotes, scenarios, and agreements. More detailed thought process is in the Appendix. 

Generally such settings are governed by the tenant or customer level configuration. But since we are going to be independent and agnostic of north or south system, capturing such configuration can help us stay independent. 

| {   "cpqDsl": "1.0",   "package": {     "id": "zcom.myCompany.core",     "version": "1.3.0",     "defaultCurrency": "USD",     "locale": "en-AU",     "rounding": { "mode": "HALF\_UP", "scale": 2 },     "time": { "timezone": "Australia/Sydney" }   } } |
| :---- |

Example of interplay between tenant config and package: 

| {   "tenantConfig": {     "rounding": { "mode": "HALF\_UP", "scale": 2 },     "time": { "timezone": "UTC" }   },   "accountProfiles": \[     {       "accountRef": "acc-789",       "rounding": { "mode": "HALF\_UP", "scale": 2 },       "time": { "timezone": "America/New\_York" },       "billing": { "defaultBillCycleDay": 15 }     }   \],   "cpqDsl": "1.0",   "package": {     "id": "zcom.myCompany.core",     "version": "1.3.0",     "defaultCurrency": "USD",     "defaults": { "time": { "timezone": "Australia/Sydney" } }   } } |
| :---- |

Acknowledged that Zuora doesn’t support account profiles today but this is a concept that I hope to introduce ultimately \- even more so with commerce becoming a mainstay. 

## Price Books (which prices, and when) {#price-books-(which-prices,-and-when)}

A rate card or price book is a dated set of prices for a currency/market. It makes repricing deterministic: historic quotes can be recomputed verbatim. Note that in our catalog Rate Cards are within the charges and associated thereof. Price Books will be an aggregated version of all the rate cards at the catalog level, generated dynamically based on context attributes. Going forward we will refer to this concept as Price Books. 

However, it is important to note that the pricebooks must be versioned and snapshots should be taken so that we can preserve the state of PBs as offered to a customer or a set of customers at a certain time. 

Options: we can consider price book snapshots or the pricebook at a point in time can be generated on the fly based on effective dating in the rate cards. This needs more thinking. Snapshotting provides determinism but it has a cost. 

Lastly, since we are keeping the offered price book at the proposal level, I believe that we must materialise it and keep a snapshot. Eventually it will be versioned. As such, treating it as a first class concept. 

| {   "priceBooks": \[     {       "id": "pb.global.vip.usd.v2025",       "currency": "USD",       "market": \["GLOBAL"\],       "customerType": \["VIP"\],       "effectiveFrom": "2025-01-01",       "effectiveTo": null     }   \] } |
| :---- |

## Offers & Components (commercial view over the technical catalogue) {#offers-&-components-(commercial-view-over-the-technical-catalogue)}

Offers are what sellers choose. Components inside an offer point to the technical catalogue (Product \> Rate Plan \> Charge) and define PriceComponents (recurring, one‑time, usage).

| {   "offers": \[     {       "id": "offer.2025Jan.billing.pro",       "label": "Billing Pro",       "priceBookRef": "pb.global.vip.usd.v2025",       "entitlements": \[{ "id": "feature.rate-engine" },                         { "id": "feature.invoice-branding", "limit": 3 }\],       "components": \[         {           "id": "comp.subscription.base",           "productRef": "prod.billing",           "ratePlanRef": "rp.billing.pro",           "priceComponents": \[             {               "id": "pc.charge.recurring.license",               "chargeType": "RECURRING",               "name": "License Fee",               "model": "PER\_UNIT",               "uom": "user",               "listPrice": { "amount": 120, "currency": "USD" },               "minQty": 10,               "discount": { "type": "PERCENTAGE", "max": 30 }             }           \]         }       \]     }   \] }  |
| :---- |

Example 2: 

| {   "offers": \[     {       "id": "offer.billing.pro",       "label": "Billing Pro",       "description": "Core billing with advanced rating",       "priceBookRef": "pb.global.VIP.usd.v2025",       "effectiveFrom": "2025-01-01",       "entitlements": \[         { "id": "feature.rate-engine" },         { "id": "feature.invoice-branding", "limit": 3 }       \],       "eligibility": { "segments": \["MID\_MARKET", "ENTERPRISE"\],                         "regions": \["NA", "EU", "APAC"\] },       "components": \[         {           "id": "comp.subscription.base",           "productRef": "prod.billing",           "ratePlanRef": "rp.billing.pro",           "priceComponents": \[             {               "id": "pc.charge.recurring.license",               "chargeType": "RECURRING",               "model": "PER\_UNIT",               "uom": "user",               "listPrice": { "amount": 120.0, "currency": "USD" },               "minQty": 10,               "discount": { "type": "PERCENTAGE", "max": 30 }             },             {               "id": "pc.usage.api-calls",               "chargeType": "USAGE",               "model": "TIERED\_BLOCK",               "tiers": \[                 …               \],               "minimumCommit": { …}             }           \]         }       \],       "constraints": \[         { "type": "REQUIRES",            "if": "comp.subscription.base",            "thenOffer": "offer.revenue.addon"          }       \]     }   \] }  |
| :---- |

## Attribute Based Pricing {#attribute-based-pricing}

| {   "offers": \[     {       "id": "offer.analytics.addon",       "label": "Analytics Add‑on",       "components": \[         {           "id": "comp.analytics",           "productRef": "prod.analytics",           "ratePlanRef": "rp.analytics",           "priceComponents": \[             {               "id": "pc.recurring.formula",               "chargeType": "RECURRING",               "model": "FORMULA",               "formula": "base \+ (seats \* seatRate) \+ (storageGb \* storageRate)",               "vars": {                 "base": 500,                 "seats": { "var": "line.attrs.seats" },                 "seatRate": 12.0,                 "storageGb": { "var": "line.attrs.storageGb" },                 "storageRate": 0.2               },               "proration": { "mode": "DAILY", "alignTo": "BILL\_CYCLE\_DAY" }             }           \]         }       \]     }   \] }  |
| :---- |

## Schedules (ramps, holidays, protection) {#schedules-(ramps,-holidays,-protection)}

A reusable Schedule time slices any mutable field (quantity, unitPrice, discount). It generalises “ramps”.

| {   "schedules": \[     {       "id": "sched.qty.stepup",       "target": { "scope": "LINE", "componentRef": "comp.subscription.base", "field": "quantity" },       "windows": \[         { "start": "2025-03-01", "end": "2025-08-31", "value": 100 },         { "start": "2025-09-01", "end": "2026-02-28", "value": 150 },         { "start": "2026-03-01", "end": "2028-02-28", "value": 200 }       \]     }   \] } |
| :---- |

## Rules {#rules}

Note that putting this DSL here doesn’t mean we implement rules in the core with exactly this DSL. I believe we need a rule engine that handles more complicated scenarios and hence that should be tackled outside this document. 

To be viable for enterprise use, the rules engine requires a more robust conditional language. This could involve adopting a standard like JSONLogic or designing a more structured JSON object for defining compound conditions with explicit boolean operators. The engine must also be able to access and evaluate a wider range of variables, including quote line details, configuration attributes, and fields from the customer account; and formulations like \-

* Complex Boolean Logic: Nesting of AND, OR, and NOT conditions (e.g., "if (Discount \> 15% AND Region is 'EMEA') OR (Product Family is 'Hardware' AND Term \< 12 months)").  
* Quote Line Evaluation: Checking for the presence of specific products or product families within the quote.  
* Configuration Logic: Evaluating user selected ConfigurationAttributes to drive pricing or validation.  
* Cross Object Lookups: Querying fields on related objects, such as the customer Account, to drive logic (e.g., "apply special pricing if Account.Type is 'Strategic Partner'"). 


| {   "rules": \[     {       "id": "rule.discount.guardrail",       "priority": 90,       "stopOnFire": false,       "when": { "\>": \[ { "var": "quote.header.discountPct" }, 25 \] },       "then": \[         { "action": "REQUIRE\_APPROVAL",            "payload": { "policyRef": "approval.dealdesk" } },         { "action": "EXPLAIN",            "payload": { "code": "DISCOUNT\_HIGH",                         "message": "Discount exceeds threshold" } }       \],       "scope": "QUOTE"     },     {       "id": "rule.require-dpa",       "priority": 70,       "stopOnFire": false,       "when": { "==": \[ { "var": "account.region" }, "EU" \] },       "then": \[         { "action": "INJECT\_CLAUSE",            "payload": { "clauseRef": "DPA.v5" } },         { "action": "REQUIRE\_APPROVAL",            "payload": { "policyRef": "approval.legal" } }       \],       "scope": "QUOTE"     }   \] } |
| :---- |

## Approval Policies {#approval-policies}

| {     "approvalPolicies": \[         {             "id": "approval.dealdesk",             "name": "Deal Desk Approval",             "mode": "SEQUENTIAL",             "stages": \[                 {                     "name": "Commercial",                     "mode": "ANY",                     "approvers": \[                         "role:DealDeskManager"                     \],                     "slaHours": 24,                     "escalateTo": "role:SalesOpsLead"                 },                 {                     "name": "Finance",                     "mode": "ALL",                     "approvers": \[                         "role:RevOps"                     \],                     "slaHours": 24                 },                 {                     "name": "Legal",                     "mode": "ANY",                     "approvers": \[                         "role:LegalCounsel"                     \],                     "condition": {                         "var": "quote.flags.customerPaper"                     },                     "delegation": {                         "allowed": true,                         "windowHours": 72                     }                 }             \],             "emits": \[                 "approvalItem.discount",                 "approvalItem.variableConsideration"             \]         }     \] } |
| :---- |

## Rules & Approvals (Together) (policy, not UI) {#rules-&-approvals-(together)-(policy,-not-ui)}

Declarative conditions that fire actions (e.g., add components, require approvals, inject clauses). Fired rules emit approval items and an explain trail.

| {   "rules": \[     {       "id": "rule.discount.guardrail",       "priority": 90,       "stopOnFire": false,       "when": { "\>": \[ { "var": "quote.header.discountPct" }, 25 \] },       "then": \[         { "action": "REQUIRE\_APPROVAL", "payload": { "policyRef": "approval.dealdesk" } },         { "action": "EXPLAIN", "payload": { "code": "DISCOUNT\_HIGH", "message": "Discount exceeds threshold" } }       \],       "scope": "QUOTE"     }   \],   "approvalPolicies": \[     {       "id": "approval.dealdesk",       "name": "Deal Desk Approval",       "mode": "SEQUENTIAL",       "stages": \[         { "name": "Commercial", "mode": "ANY", "approvers": \["role:DealDeskManager"\], "slaHours": 24 }       \]     }   \] } |
| :---- |

## Scenarios & Quotes (options and the priced instance) {#scenarios-&-quotes-(options-and-the-priced-instance)}

Scenarios are options sellers present. A Quote is a priced configuration pinned to specific package and price book versions, plus the effective rounding/timezone after tenant/account overrides.

| {   "scenarios": \[     {       "id": "scen.optionA",        "name": "Option A \- Billing Pro",        "isPrimary": true,        "status": "APPROVED"      }   \],   "quotes": \[     {       "id": "Q-001",       "scenarioRef": "scen.optionA",       "accountRef": "acc-789",       "currency": "USD",       "term": { "periodType": "MONTHS", "length": 36 },       "pinnedContext": {         "package": "com.myCompany.core@1.3.0",         "priceBook": "pb.global.usd.v2025",         "rounding": { "mode": "HALF\_UP", "scale": 2 },         "time": { "timezone": "America/New\_York" }       },       "lines": \[         {           "offerRef": "offer.billing.pro",           "componentRef": "comp.subscription.base",           "quantity": 150,           "scheduleRefs": \["sched.qty.stepup"\],           "overrides": { "pc.recurring.license": { "discountPct": 20 } }         }       \],       "totals": { "arr": xx, "mrr": xx, "tcv": xx }     }   \] } |
| :---- |

## Proposal (buyer snapshot) {#proposal-(buyer-snapshot)}

A publishable pack that references one scenario/quote set, with documents and clause IDs. It’s the thing the buyer sees. 

Under consideration (open question): would a proposal with multiple scenarios make sense? 

| {   "proposals": \[     {       "id": "P-9001",       "name": "MyCompany x ZCom \- Commercials",       "effectiveDate": "2025-02-15",       "expiryDate": "2025-03-15",       "status": "APPROVED",       "baseCurrency": "USD",       "scenarioRef": "scen.optionA",       "quoteRefs": \["Q-001"\],       "documents": \[{ "type": "ORDER\_FORM",                        "templateRef": "doc.order.standard.v3" }\],       "clauses": \["MSA.v7", "Docxxx", “Non Standard xxx”\]     }   \] } |
| :---- |

## Agreements (contract container)  {#agreements-(contract-container)}

An Agreement is the commercial contract under which one or more Subscriptions run. It pins the term, the governing price book, the billing account, and any commitments/prepayments that span subscriptions.

| {   "agreements": \[     {       "id": "AG-2025-EXAMPLE-01",       "title": "Master Subscription Agreement for ABC Company",       "accountRef": "acc-123",       "billingAccountRef": "bill-acc-001",       "type": "SUBSCRIPTION\_AGREEMENT",       "term": { "start": "2025-03-01",                  "end": "2028-02-28",                   "autoRenew": { "enabled": true,                                  "periodType": "YEARS", "length": 1 } },       "priceBookRef": "pb.global.usd.vip.v2025",       "origin": { "proposalRef": "P-9001", "acceptedAt": "2025-02-20T11:30:00Z" },       "governing": { "currency": "USD", "paymentTerm": "NET\_30" },       "notes": "MSA \+ Non Standard terms \+ Enterprise SLA \+ xxx"     }   \] } |
| :---- |

## Agreement & Subscriptions (the contract and what runs) {#agreement-&-subscriptions-(the-contract-and-what-runs)}

As stated above. Just an extended example: 

| {   "agreements": \[     {       "id": "AG-2025-EXAMPLE-01",       "title": "Master Subscription Agreement — ZCom",       "accountRef": "acc-789",       "billingAccountRef": "bill-acc-001",       "term": { "start": "2025-03-01", "end": "2028-02-28" },       "origin": { "proposalRef": "P-9001",                    "acceptedAt": "2025-02-20T11:30:00Z" },       "subscriptions": \[         {           "id": "SUB-001",           "name": "Billing Pro — Primary",           "billCycle": { "day": 15, "align": "BILL\_CYCLE\_DAY" },           "term": { "periodType": "MONTHS",                      "length": 36, "coTermToAgreement": true },           "lines": \[             {               "offerRef": "offer.billing.pro",               "componentRef": "comp.subscription.base",               "quantity": 150,               "schedules": \[                 {                   "target": { "field": "quantity" },                   "windows": \[                     { "start": "2025-03-01",                        "end": "2025-08-31", "value": 100 },                     { "start": "2025-09-01",                        "end": "2026-02-28", "value": 150 },                     { "start": "2026-03-01",                        "end": "2028-02-28", "value": 200 }                   \]                 }               \]             }           \]         }       \]     }   \] } |
| :---- |

## Commitments & Prepayments (with clear scope) {#commitments-&-prepayments-(with-clear-scope)}

Commitments carry two distinct scopes:

* coverage: which charges count towards the commitment’s meter  
* applyTo: which charges the commitment can consume or settle.

Use MIN\_SPEND (meter \+ top‑up), PREPAID\_BALANCE (fund \+ drawdown), or USAGE\_POOL\_COMMIT (blocks \+ overage). 

Overlaps resolve by priority, exclusive, then allocationStrategy.

| {   "commitments": \[     {       "id": "COM-001",       "agreementRef": "AG-2025-EXAMPLE-01",       "type": "MIN\_SPEND",       "currency": "USD",       "amount": 120000,       "coverage": {         "chargeSelector": { "subscriptionRef": "SUB-001",                              "chargeType": "RECURRING" },         "measureAgainst": "NET\_AFTER\_DISCOUNT",         "includeTax": false       },       "measurement": { "period": "YEAR", "evaluateOn": "ANNIVERSARY" },       "settlement": { "mode": "INVOICE\_TOP\_UP", "graceDays": 15 },       "priority": 50,       "exclusive": false,       "allocationStrategy": "FIFO"     },     {       "id": "COM-002",       "agreementRef": "AG-2025-EXAMPLE-01",       "type": "PREPAID\_BALANCE",       "currency": "USD",       "amount": 60000,       "coverage": { "chargeSelector":                           { "subscriptionRef": "SUB-001",                             "chargeType": "USAGE" } },       "applyTo": { "chargeSelector":                           { "anyOf": \[ { "chargeType": "USAGE" },                                        { "tag": "overage" } \] } },       "drawdown": { "order": "OLDEST\_FIRST",                      "rollover": { "mode": "PERCENT", "value": 0 } },       "expiry": { "at": "2026-02-28", "forfeitUnspent": true },       "paymentScheduleRef": "PS-001",       "priority": 10,       "exclusive": true,       "allocationStrategy": "MAX\_SAVINGS"     },     {       "id": "COM-003",       "agreementRef": "AG-2025-EXAMPLE-01",       "type": "USAGE\_POOL\_COMMIT",       "pool": {         "name": "api-calls",         "commitBlocks": 200,         "blockSize": 1000,         "overagePricePerBlock": 0.003,         "rollover": { "mode": "PERCENT", "value": 50 }       },       "coverage": { "chargeSelector": { "componentRef": "comp.api.pool" } },       "priority": 20     }   \] } |
| :---- |

Note that the design of Zuora’s commitment model done for twilio and tradeweb may differ from this. 

## Payment Schedules (instalments & milestones) {#payment-schedules-(instalments-&-milestones)}

Funding for prepayments often happens in parts: on signature, on go‑live, 90 days later. These entries tell Finance what to invoice, and when.

| {   "paymentSchedules": \[     {       "id": "PS-001",       "name": "40/30/30 — Signature/Go‑Live/+90d",       "currency": "USD",       "entries": \[         { "sequence": 1,            "type": "PERCENT\_OF\_COMMIT",            "value": 40,            "due": { "event": "AGREEMENT\_SIGNED" } },         { "sequence": 2,            "type": "PERCENT\_OF\_COMMIT",            "value": 30,            "due": { "event": "MILESTONE", "name": "GO\_LIVE" } },         { "sequence": 3,            "type": "PERCENT\_OF\_COMMIT",            "value": 30,            "due": { "event": "MILESTONE", "name": "GO\_LIVE",                     "offsetDays": 90 } }       \]     }   \] } |
| :---- |

## Deal Room (buyer collaboration) {#deal-room-(buyer-collaboration)}

A single buyer hub for proposals, comments, redlines and a mutual action plan. Keeps email back and forth out of the critical path.

| {   "dealRooms": \[     {       "id": "DR-100",       "title": "myCompany x ZCom \- Commercials",       "proposalRef": "P-9001",       "access": {         "contacts": \["contact:procurement@example.com", "contact:legal@example.com"\],         "tokenTtlHours": 72,         "audit": true,         "maskPIIInLogs": true       }     }   \] } |
| :---- |

## Adapters (interoperability contract) {#adapters-(interoperability-contract)}

Declares what a target system supports and how to translate. If a feature can’t be modelled natively, the adapter says so up front.

The following is just a shot at making adapters declarative. 

| {   "adapters": \[     {       "system": "zuora",       "version": "orders-v2",       "capabilities": {         "minSpend": true,         "prepaidBalance": true,         "usagePools": true,         "paymentSchedules": true       },       "mappings": {         "subscriptionToOrderActions": \[           { "action": "NEW\_SUBSCRIPTION" },           { "if": { "var": "line.schedules" },                      "action": "CHANGE\_TERM\_CONDITIONS" }         \]       }     },     {       "system": "salesforce\_cpq",       "version": "spring-25",       "capabilities": {         "minSpend": "partial",         "prepaidBalance": "downstream",         "usagePools": false,         "paymentSchedules": "partial"       },       "mappings": {         "agreementToContract": "SBQQ\_\_Contract\_\_c",         "subscriptionToAsset": "SBQQ\_\_Subscription\_\_c"       }     }   \] } |
| :---- |

## Events (audit trail) {#events-(audit-trail)}

A standard event log lets you reproduce “who decided what, when” across approvals, commitment allocations, and publication.

**Under consideration**: adopt CNCF guidelines for CloudEvents (to be explored \- because this may impact Zuora Audit or Notifications). 

| //sample only {   "events": \[     { "at": "2025-02-20T11:30:00Z",        "type": "proposal.accepted",        "data": { "proposalRef": "P-9001" } },     { "at": "2025-03-01T00:00:00Z",        "type": "agreement.executed",        "data": { "agreementRef": "AG-2025-EXAMPLE-01" } },     { "at": "2025-03-01T00:00:01Z",        "type": "commitment.allocated",        "data": { "commitmentRef": "COM-002", "amount": 1540.0 } }   \] } |
| :---- |

## TBC {#tbc}

- Configurable Product Model  
- Amendments and Subscription Lifecycle

## Complete Example {#complete-example}

| {     "tenantConfig": {         "rounding": {             "mode": "HALF\_UP",             "scale": 2         },         "time": {             "timezone": "UTC"         }     },     "accountProfiles": \[         {             "accountRef": "acc-789",             "time": {                 "timezone": "America/New\_York"             },             "billing": {                 "defaultBillCycleDay": 15             }         }     \],     "cpqDsl": "1.0",     "package": {         "id": "com.myCompany.core",         "version": "1.3.0",         "defaultCurrency": "USD"     },     "priceBooks": \[         {             "id": "pb.global.VIP.usd.v2025",             "currency": "USD",             "market": \[                 "GLOBAL"             \],             "effectiveFrom": "2025-01-01"         }     \],     "offers": \[         {             "id": "offer.billing.pro",             "label": "Billing Pro",             "priceBookRef": "pb.global.VIP.usd.v2025",             "components": \[                 {                     "id": "comp.subscription.base",                     "productRef": "prod.billing",                     "ratePlanRef": "rp.billing.pro",                     "priceComponents": \[                         {                             "id": "pc.charge.recurring.license",                             "chargeType": "RECURRING",                             "model": "PER\_UNIT",                             "uom": "user",                             "listPrice": {                                 "amount": 120,                                 "currency": "USD"                             },                             "minQty": 10,                             "discount": {                                 "type": "PERCENTAGE",                                 "max": 30                             }                         }                     \]                 }             \]         }     \],     "schedules": \[         {             "id": "sched.qty.stepup",             "target": {                 "scope": "LINE",                 "componentRef": "comp.subscription.base",                 "field": "quantity"             },             "windows": \[                 {                     "start": "2025-03-01",                     "end": "2025-08-31",                     "value": 100                 },                 {                     "start": "2025-09-01",                     "end": "2026-02-28",                     "value": 150                 },                 {                     "start": "2026-03-01",                     "end": "2028-02-28",                     "value": 200                 }             \]         }     \],     "rules": \[         {             "id": "rule.discount.guardrail",             "priority": 90,             "stopOnFire": false,             "when": {                 "\>": \[                     {                         "var": "quote.header.discountPct"                     },                     25                 \]             },             "then": \[                 {                     "action": "REQUIRE\_APPROVAL",                     "payload": {                         "policyRef": "approval.dealdesk"                     }                 },                 {                     "action": "EXPLAIN",                     "payload": {                         "code": "DISCOUNT\_HIGH"                     }                 }             \],             "scope": "QUOTE"         }     \],     "approvalPolicies": \[         {             "id": "approval.dealdesk",             "name": "Deal Desk Approval",             "mode": "SEQUENTIAL",             "stages": \[                 {                     "name": "Commercial",                     "mode": "ANY",                     "approvers": \[                         "role:DealDeskManager"                     \],                     "slaHours": 24                 }             \]         }     \],     "scenarios": \[         {             "id": "scen.optionA",             "name": "Option A — Billing Pro",             "isPrimary": true,             "status": "APPROVED"         }     \],     "quotes": \[         {             "id": "Q-001",             "scenarioRef": "scen.optionA",             "accountRef": "acc-789",             "currency": "USD",             "term": {                 "periodType": "MONTHS",                 "length": 36             },             "pinnedContext": {                 "package": "com.myCompany.core@1.3.0",                 "priceBook": "pb.global.VIP.usd.v2025",                 "rounding": {                     "mode": "HALF\_UP",                     "scale": 2                 },                 "time": {                     "timezone": "America/New\_York"                 }             },             "lines": \[                 {                     "offerRef": "offer.billing.pro",                     "componentRef": "comp.subscription.base",                     "quantity": 150,                     "scheduleRefs": \[                         "sched.qty.stepup"                     \],                     "overrides": {                         "pc.recurring.license": {                             "discountPct": 20                         }                     }                 }             \],             "totals": {                 "arr": null,                 "mrr": null,                 "tcv": null             }         }     \],     "proposals": \[         {             "id": "P-9001",             "name": "myCompany x ZCom — Commercials",             "effectiveDate": "2025-02-15",             "expiryDate": "2025-03-15",             "status": "APPROVED",             "baseCurrency": "USD",             "scenarioRef": "scen.optionA",             "quoteRefs": \[                 "Q-001"             \],             "documents": \[                 {                     "type": "ORDER\_FORM",                     "templateRef": "doc.order.standard.v3"                 }             \],             "clauses": \[                 "MSA.v7",                 "DPA.v5"             \]         }     \],     "paymentSchedules": \[         {             "id": "PS-001",             "name": "40/30/30 — Signature/Go‑Live/+90d",             "currency": "USD",             "entries": \[                 {                     "sequence": 1,                     "type": "PERCENT\_OF\_COMMIT",                     "value": 40,                     "due": {                         "event": "AGREEMENT\_SIGNED"                     }                 },                 {                     "sequence": 2,                     "type": "PERCENT\_OF\_COMMIT",                     "value": 30,                     "due": {                         "event": "MILESTONE",                         "name": "GO\_LIVE"                     }                 },                 {                     "sequence": 3,                     "type": "PERCENT\_OF\_COMMIT",                     "value": 30,                     "due": {                         "event": "MILESTONE",                         "name": "GO\_LIVE",                         "offsetDays": 90                     }                 }             \]         }     \],     "agreements": \[         {             "id": "AG-2025-EXAMPLE-01",             "title": "Master Subscription Agreement — ZCom",             "accountRef": "acc-789",             "billingAccountRef": "bill-acc-001",             "term": {                 "start": "2025-03-01",                 "end": "2028-02-28"             },             "origin": {                 "proposalRef": "P-9001",                 "acceptedAt": "2025-02-20T11:30:00Z"             },             "subscriptions": \[                 {                     "id": "SUB-001",                     "name": "Billing Pro — Primary",                     "billCycle": {                         "day": 15,                         "align": "BILL\_CYCLE\_DAY"                     },                     "term": {                         "periodType": "MONTHS",                         "length": 36,                         "coTermToAgreement": true                     },                     "lines": \[                         {                             "offerRef": "offer.billing.pro",                             "componentRef": "comp.subscription.base",                             "quantity": 150,                             "schedules": \[                                 {                                     "target": {                                         "field": "quantity"                                     },                                     "windows": \[                                         {                                             "start": "2025-03-01",                                             "end": "2025-08-31",                                             "value": 100                                         },                                         {                                             "start": "2025-09-01",                                             "end": "2026-02-28",                                             "value": 150                                         },                                         {                                             "start": "2026-03-01",                                             "end": "2028-02-28",                                             "value": 200                                         }                                     \]                                 }                             \]                         }                     \]                 }             \],             "commitments": \[                 {                     "id": "COM-001",                     "type": "MIN\_SPEND",                     "currency": "USD",                     "amount": 120000,                     "coverage": {                         "chargeSelector": {                             "subscriptionRef": "SUB-001",                             "chargeType": "RECURRING"                         },                         "measureAgainst": "NET\_AFTER\_DISCOUNT",                         "includeTax": false                     },                     "measurement": {                         "period": "YEAR",                         "evaluateOn": "ANNIVERSARY"                     },                     "settlement": {                         "mode": "INVOICE\_TOP\_UP",                         "graceDays": 15                     },                     "priority": 50,                     "exclusive": false,                     "allocationStrategy": "FIFO"                 },                 {                     "id": "COM-002",                     "type": "PREPAID\_BALANCE",                     "currency": "USD",                     "amount": 60000,                     "coverage": {                         "chargeSelector": {                             "subscriptionRef": "SUB-001",                             "chargeType": "USAGE"                         }                     },                     "applyTo": {                         "chargeSelector": {                             "anyOf": \[                                 {                                     "chargeType": "USAGE"                                 },                                 {                                     "tag": "overage"                                 }                             \]                         }                     },                     "drawdown": {                         "order": "OLDEST\_FIRST",                         "rollover": {                             "mode": "PERCENT",                             "value": 0                         }                     },                     "expiry": {                         "at": "2026-02-28",                         "forfeitUnspent": true                     },                     "paymentScheduleRef": "PS-001",                     "priority": 10,                     "exclusive": true,                     "allocationStrategy": "MAX\_SAVINGS"                 }             \]         }     \],     "dealRooms": \[         {             "id": "DR-100",             "title": "myCompany x ZCom — Commercials",             "proposalRef": "P-9001",             "access": {                 "contacts": \[                     "contact:procurement@example.com",                     "contact:legal@example.com"                 \],                 "tokenTtlHours": 72,                 "audit": true             }         }     \],     "adapters": \[         {             "system": "zuora",             "version": "orders-v2",             "capabilities": {                 "minSpend": true,                 "prepaidBalance": true,                 "usagePools": true,                 "paymentSchedules": true             }         }     \],     "events": \[         {             "at": "2025-02-20T11:30:00Z",             "type": "proposal.accepted",             "data": {                 "proposalRef": "P-9001"             }         }     \] }  |
| :---- |

## Schema {#schema}

[CPQ-DSL-Schema.json](https://drive.google.com/file/d/1iFVtwJ4dfAfBBdoCEqiQIVdKKI7fbRIn/view?usp=drive_link)

# Challenges, Conundrums, and Open Thought Threads  {#challenges,-conundrums,-and-open-thought-threads}

## Impedance mismatch between applications and Adapter conundrum {#impedance-mismatch-between-applications-and-adapter-conundrum}

A primary goal of the DSL is to be "vendor neutral" and allow for offers to be "losslessly exported to Zuora Orders, Salesforce CPQ, and others". This is facilitated by an Adapter concept, which declaratively lists the capabilities of the target system (e.g., "minSpend": true). This ambition aligns with modern architectural trends favoring composable, infrastructure agnostic systems that avoid vendor lock-in.   

It must be acknowledged however that the Adapter model whilst being flexible has vast challenges and must overcome the complexity of achieving meaningful interoperability between mature CPQ platforms. The core challenge is not simply a matter of feature parity but of fundamental impedance mismatch between their underlying data models.

For instance, the proposed DSL's model flows from Offer to Component to PriceComponent. Salesforce CPQ, in contrast, is architected around a deeply integrated set of objects: a Product can be a Bundle containing Product Options grouped by Product Features, with pricing and configuration logic driven by Price Rules and Product Rules that can execute complex logic, including lookups to other objects.   
Zuora's model is purpose built for the subscription lifecycle, centered on a Product Catalog of ProductRatePlans and ProductRatePlanCharges, where changes to an active subscription are managed via explicit Order Actions (e.g., New Subscription, Amendment, Renewal).

Whilst I have proposed declarative DSL for Adapter, I do acknowledge that it may require a transformation engine for bringing two heterogeneous applications together. 

## Schedule Vs Quote Line Item: Time Slices {#schedule-vs-quote-line-item:-time-slices}

The QuoteLine object can reference multiple schedules via its scheduleRefs array. Now, it can lead to confusion if more than one schedule tries to modify the same field over the same time period. We can restrict QLI \<\> to Schedule to be 1:1 but is that practical? 

For example, a standard three year quantity step up schedule might dictate a quantity of 100 for the first year. A sales user could then apply a separate promotional schedule that offers a quantity of 120 for the first six months as a deal sweetener.    
   
We probably need to introduce a resolution strategy. Does the last schedule applied win? Are the values summed? Is the maximum value chosen? Is it an error condition that blocks calculation? This could be implemented as a priority field on the schedule reference within the quote line, or an overrideBehavior property (e.g., REPLACE, SUM, MAX) that explicitly declares how colliding values should be handled.

## Proposal & Scenarios {#proposal-&-scenarios}

Would a proposal with multiple scenarios make sense? From an architectural and commercial clarity standpoint, the answer seems like it should be no. 

A Proposal represents a specific, actionable, and often legally binding offer. Including multiple scenarios within a single proposal introduces ambiguity. Which option is the customer accepting? How are totals calculated? A cleaner architectural pattern will be to maintain the Proposal as a representation of a single Scenario and its associated Quote(s). 

To present options to a buyer, the DealRoom concept can be leveraged, or a new ScenarioComparison (too much I guess) object could be introduced. This object would present multiple scenarios, and an action taken on one of them (e.g., "Select Option A") would then generate a distinct Proposal for that single, chosen scenario. This maintains a clean 1:1 relationship between a formal proposal and the specific commercial terms it represents.   

## 

# Appendix {#appendix}

## Why Package  {#why-package}

* **Deterministic maths & audit**  
  Rounding mode, precision, timezone, and price book or catalog /version are part of the calculation contract. They must be pinned before a quote/proposal is produced so the same inputs always recompute to the same outputs (today and two years from now). The proposal in this model holds buyer totals (ARR/MRR/TCB/TCV) but not the engine contract (rounding/timezone/price book), so we can’t reliably re-price a historic proposal without a separate package header.

* **Reuse across scenarios/quotes**  
  One package (catalogue, rules, approvals, price book/rate cards) powers many scenarios and quotes. Several of those may become proposals, others won’t. Keeping the meta on the package prevents drift and duplicate settings scattered across multiple proposals. Our data model already separates Scenario, Quote and Proposal for this reason.

* **Effective dating (Rate Cards/ Price Books)**  
  Which list prices apply is a function of rate cards/ pricebook with dates, not of a single proposal. If “what’s current” is embedded in a proposal, we can’t cleanly compare scenarios, nor can we amend/renew with the correct vintage. 

  * Pinning priceBookRef at the package, then recording it in the quote’s pinnedVersions, solves this. We have Price/Rate Plan/Charge, ramps and renewal/term objects, but not a single place to pin the effective rate/card price book for recompute.

* **Interoperability (adapters)**  
  Cross system parity (Zuora Orders, Salesforce CPQ, etc.) depends on adapter capabilities and mapping rules that are global to the package, not specific to a proposal. Adapters cannot be held hostage to internal concepts of the engine.

* **Performance & governance**  
  Engines cache/catalogue by package id/version, not by proposal. Rules and approvals (who, when, SLA) are policy and hence they shouldn’t be replicated per proposal. A package acts like “code”: it’s reviewed once, versioned, then referenced by many proposals: clean change control. Our Workflow/Approval objects fit this pattern.

* **Lifecycle separation**  
  Proposal is a publishable artifact (doc set \+ clauses) that a buyer sees. Package is the spec to produce that artifact. Our Proposal object has baseCurrency, status, documents and totals with Quote/QuoteLine/Ramp living below it and Agreement/Subscription live after acceptance. Keeping engine meta at package level keeps those transitions clean.

**What goes where (rule of thumb):**

* **Package (engine contract):** rounding mode/scale, timezone, rate card/pricebook/effective dates, adapter capabilities/mappings, global rules & approvals.  
* **Quote/Scenario (commercial config):** term, lines, overrides, schedules, and pinnedVersions back to the package.  
* **Proposal (buyer snapshot):** selected scenario/quotes, documents/clauses, presented totals, expiry.  
* **Agreement/Subscription (execution):** what actually runs post signature (terms, bill cycle, commitments).

