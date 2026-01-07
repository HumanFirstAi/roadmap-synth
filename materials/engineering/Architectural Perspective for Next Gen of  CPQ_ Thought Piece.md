# Architectural Perspective for Next Gen of  CPQ

Sep 2025

# Executive Summary 

**Zuora Announces Next-Generation Quoting & Deal Governance Platform**

Next Gen of CPQ \= Next generation quoting and deal governance platform, designed to transform how mid-to-large enterprise SaaS companies structure, approve, and close deals.

The new platform decouples seller experience from decisioning and governance, introduces a **lightweight “Vibe Quoting” surface** for reps, and delivers a **Deal Command Center** for centralised approvals, policy enforcement, and profitability checks. Buyer and seller collaboration moves into a **Deal Room**: a cryptographically secure digital workspace with redline management, clause playbooks, and mutual action plans.

The result: faster cycle times, consistent policy enforcement, improved margins, and measurable buyer satisfaction while leveraging existing CPQ and billing systems.

# Introduction

Assuming that we all acknowledge that CPQ is needed in the space we are going to play in \- mid to large enterprise SaaS. 

We have many CPQ applications out there, but these are invariably heavy. **Reps avoid it** on complex deals and even small deals suffer from latency, cluttered guided selling, and complicated approvals. **Deal Desk ends up doing operational execution** rather than strategic support, decisioning, and governance \- they actually do a bit of everything. **Buyers experience the pain** through long cycles, redlines over email and reissued order forms.

After a few discussions and including inputs from Tien here is the summary of a “potential position” (and options) \- **Separate how reps work from how quotes are governed:** 

1) Put decisioning and governance in a service,   
2) keep collaboration (including buyer collab) in a Deal Room,   
3) and simplify rep quoting through a lightweight “Vibe Quoting” surface 

A DSL based Proposal layer (commercial abstraction of the Quote and Pricing) sitting atop the existing CPQ/billing stack acts as the architectural basis for a modern AI-first interface.

The document outlines three strategic options, their tradeoffs, and where each fits. I believe a hybrid approach may be the one to test. 

- Extract Deal Desk into a Decision & Governance Service: policy, approvals, clause playbooks; consumed by any surface (CPQ, Lite Quote/Vibe Quote, partner portal). This can stay in conventional CPQ itself.   
- Give reps a quick entry point with progressive disclosure and instant order form preview.  
- Run collaboration in a Deal Room (Salesforce seems to have a concept of digital sales room) with audit, clause suggestions and mutual action plans.

# Context & Problem Framing

The following is influenced by my discussion with the stakeholders involved in Sales process at Zuora \- 

* **Complexity & performance:** multi catalogue sprawl, slow loads, fragile guided selling, no reliable order form preview, heavy AE enablement.  
* **Workflow gaps:** approvals are inconsistent; contract language isn’t first class; customer‑paper paths are manual.  
* **Reality of the field:**  
  * **Large/complex deals:** reps tend to avoid CPQ; Deal Desk effectively builds the quote.  
  * **Smaller deals:** reps can self-serve but still require Deal Desk to review/approve.  
* **Buyer collaboration is fragmented:** proposals, order forms and redlines live across email, slides and PDFs.

**Question**: What is the split of High Velocity Deals vs High Complexity Deals in our ICP? 

* **High Velocity Deals**: Standard deals that need to be quoted and closed with maximum speed.  
* **High Complexity Deals**: Strategic deals that involve non standard terms, complex pricing, and require rigorous oversight to protect margins and ensure compliance.  

## Key Personas (apart from the customer)

**Sales Rep**

* Sales Reps like momentum. Their primary goal is velocity \- getting accurate, professional quotes in front of customers as quickly as possible to keep the deal moving.    
* They view traditional CPQ as a roadblock. It’s a clunky, desktop first system with a steep learning curve, too many fields, and rigid approval workflows that stall their deals.   
  * They need to generate a quote between meetings, from their phone, not spend an hour navigating a complex system.  
* Their ideal tool will be a lightweight, intuitive "Quoting Studio." It is awesome if it is mobile first, template driven, and intelligent, guiding them to the right options without overwhelming them.  

**The Deal Desk**

* The Deal Desk is the strategic command centre for (primarily) high value, non standard deals. Their primary goal is governance \- structuring deals that are profitable, compliant, and operationally sound.    
* They operate in a world of disconnected systems and manual processes. They chase approvals via email and Slack, struggle with version control, and lack the tools to properly analyse deal profitability and risk.   
  * Standard CPQ tools are often too rigid to model the creative, non standard deal structures they specialise in.    
* Their ideal tool will be a powerful "Deal Command Centre".   
  * This is a dedicated workspace for structuring complex deals, modelling profitability, managing multi-stage approval workflows, and ensuring compliance with legal and financial guardrails.  

## Assumptions

* Only the sales rep sends quotes/proposals to customers. Deal Desk approves and advises; it does not face the customer directly.  
* Not all customers or deals are the same; **we need graded experiences aligned to complexity and risk**.

# Strategic Vision (Evolution from CPQ)

**As opposed to conventional CPQ, where every persona is given one size fits all solution with complicated permission control, we should aim to change the game.**

The solution is not to choose one persona over the other. Rather, the solution (most probably) is to **stop thinking of CPQ as a single, monolithic application**. A modern CPQ should be a platform composed of distinct, integrated components, **each purpose built for the job** it needs to do. Let’s look at the components of this architecture: 

## Component 1: The Rep-Centric "Vibe Quoting" Studio

This is the fast lane for sales reps. It's a lightweight, intelligent front-end designed for speed and ease of use, enabling reps to build and send the majority of standard quotes in minutes.

* **Key Features:** It is a template driven vibe quoting application that allows reps to generate professional, on brand quotes from any device. 

  * It uses a conversational, progressive disclosure interface, asking simple questions to guide the rep and provides an instant preview of the order form.   
  * AI (not just GenAI) is embedded to suggest optimal product bundles based on previous patterns of successful quotes, and upsells based on historical data largely obviating progressive evaluations of rules that affect performance negatively.   
* **The Job It Does:** It eliminates friction for a large number of deals that are standard, dramatically increasing sales productivity and reducing the time-to-quote. And even in the complex deals, it allows them to get started without friction. It gets the rep out of the presentations, excel sheets, and from the traditional confinement of a structured system like Salesforce. 

## Component 2: The "Deal Command Centre" (DCC)

This is the company’s governance and decisioning engine: a dedicated workspace where Deal Desk, Finance, and Legal orchestrate complex deals, enforce risk controls, and maximize profitability. It leverages AI-driven search across prior quotes to accelerate structuring of non-standard transactions. While standard deals also pass through Deal Desk, the real value here is in handling the messy, high-value cases that require deep expertise and leverage AI to improve the process. Furthermore it obviates the need for complex rule-management and consequently the dependence of finance organizations on their IT counterparts. 

* **Key Features:** The DCC provides advanced tools for deal structuring, profitability analysis, and revenue recognition compliance.   
  * Its core is a robust, no-code engine that automates complex, multi stage approval processes across departments.   
  * All commercial policies, legal clauses, and pricing guardrails are centralised here, acting as a service that any front-end can call upon.    
  * We can repurpose conventional CPQ for power users and DCC use cases (for Deal Desk)  
* **The Job It Does:** It provides the rigorous control and strategic oversight required for the 20% of deals that carry the most value and risk, ensuring every complex deal is profitable and compliant both based on historical precedent and structural rules.

## Component 3: The Collaborative "Deal Room"

This is the shared, customer facing workspace that bridges the internal and external deal processes. Instead of emailing static PDFs, every quote lives in a cryptographically secure, interactive digital sales room. The cryptographically secure, collaborative interface invites rep, deal desk, and the customer. 

* **Key Features:** It's a single hub where buyers and sellers can access all deal related content, ask questions, and collaborate in real time.   
  * It provides sellers with invaluable analytics on buyer behavioral engagement such as who is viewing what content and for how long, while giving buyers a modern, transparent experience.  
* **The Job It Does:** It transforms quoting from a transactional step into a collaborative and conversational process, increasing buyer engagement, reducing cognitive load on the buyer and shortening sales cycles.

Note: Key principles of API first architecture, headless backend are a given. 

# Investment Pathways

From today’s hybrid model, we are intentionally defining two distinct paths, each optimised for excellence against its core persona. The goal of this document is to align on a unified architectural vision: a three component platform that elevates conventional CPQ into a persona driven system, delivering best in class capabilities for every role.

## Path 1: "Vibe Quoting" for the Reps

* **The Play:** Focus initial investment on building the lightweight, rep-centric Vibe Quoting Studio. This would integrate with a customer's existing "classic" CPQ, which would continue to be used by the Deal Desk for complex deals.  
* Delivers immediate wins for sales reps and boosts seller productivity with minimal disruption to back-end billing and revenue processes.   
  * It addresses a high volume pain point and opens a path for product-led growth.    
* We would be supporting two interaction models, and critical policy enforcement would remain buried in the legacy CPQ system.   
  * It's a productivity play, not a full transformation.  
* **Possible Candidates:** Organisations wanting to see immediate seller productivity gains without committing to a deep re-platforming of their core deal governance.

## Path 2: "Deal Command Centre" for the Deal Desk

* **The Play:** Focus first on building the DCC as a centralised decision and governance service. This would involve extracting and centralising all approval logic, policy, and compliance checks into a powerful engine that other systems (including the existing CPQ) can call via API.  
* Creates a single, consistent source of truth for all commercial decisions, which is highly defensible and scalable across any channel (direct sales, partners, self-service). It solves high value architectural and functional problems around compliance, auditability, search, and margin control for large enterprises.    
* Requires a heavier upfront investment in designing a modern and AI/rules engine and data contracts. The main consideration is that this approach requires rationalizing parts of the customer’s existing CPQ, since decision logic needs to be centralized. This isn’t a rip-and-replace — it’s a structured transformation that simplifies governance, reduces duplication, and sets the foundation for scale.  
* **Possible Candidates:** Organisations prioritising control, auditability, and the ability to scale governance across multiple selling channels.

# Appendix

## Questions we should try to answer 

* Are we aligned that rep experience and decisioning should be decoupled?  
* Which segments (mid size to large enterprise) must Vibe Quote support first?  
  * \[Manfred\]: it has to be mid-sized to large enterprise, as there is a division of labor (rep and deal desk) and complex deals. Vertical we focus on is SaaS first and SaaS with some hardware second, then other verticals like FinTech, biz services, etc.  
* How do we measure success of chosen option? 

## Capability model 

**Experience layer (who touches it)**

* **Vibe Quoting**: reps; template and voice friendly; progressive questions; instant order form preview; autosave.  
* **Deal Room (buyer and deal desk collaboration)**: buyer \+ deal desk \+ rep; proposals, comments, redlines, clause suggestions, mutual action plan; full audit.  
* **Classic CPQ UI**: Deal Desk and power users for complex quotes.

**Decision, Governance, & orchestration (who decides)**

* Policy engine for approvals (discount/margin/term), revenue checks (variable consideration, allocation flags), clause/playbook selection, exception routing; integrates with Slack/Teams for approvals.  
* **Proposal Service**: commercial bundles and entitlements with T\&Cs; maps to technical catalogue; versions and eligibility rules.

**Systems of record (where it lands)**

* **CRM**: opportunity, forecast, ownership.  
* **CPQ/Billing/Revenue**:  pricing accuracy, order capture, rating and revenue schedule.  
* **CLM**: clause library, playbooks, redline storage, signature package. (not Zuora)  
* **Catalog**: Product, plan, pricing, packaging including bundle rules and pricing rules. 