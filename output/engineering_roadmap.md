# Zuora Product Roadmap: Engineering Perspective

## Technical Vision

We're building a composable commerce platform centered on an **intersection layer**—shared services (BCS, Rules Engine, Orchestration, Pricing Engine) that enable any customer touchpoint to access consistent business logic. The architectural goal: product teams (CPQ, Catalog, Experiences) consume platform services rather than building their own, eliminating the current fragmentation where four separate rating engines and multiple rules implementations create tech debt and inconsistency. The 6-month window Nav identified is real—if we don't consolidate now, aggregation will happen organically and messily.

---

## Critical Architecture Decisions Needed

Before detailed implementation planning, these architectural decisions are blocking multiple workstreams:

| Decision | Options | Impact | Owner | Deadline |
|----------|---------|--------|-------|----------|
| **Rules Engine Ownership** | A) Platform owns single engine B) Each team maintains own C) Federated with shared interface | Blocks: CPQ Configurator, Catalog bundles, Orchestration | Architecture Board | 30 days |
| **BCS Scope & Ownership** | A) Acquisition feature B) Platform service C) Catalog extension | Blocks: All intersection work | Jonathan/Nav | 30 days |
| **Pricing Engine Separation** | A) Extract from billing B) Build new C) Wrapper around existing | Blocks: Sub-100ms pricing, omni-channel | Platform/Billing | 45 days |
| **Zephyr Future** | A) Extend current B) Replace C) Abandon, build outcome-specific | Blocks: Orchestration layer | Alan/Errol/Nav | 60 days |

---

## System Architecture: Target State

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           EXPERIENCE LAYER                                   │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │  Self-Serve │  │  My Account │  │   Portals   │  │  Third-Party UIs    │ │
│  │  (Plasmic)  │  │             │  │             │  │  (Customer-built)   │ │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────────┬──────────┘ │
└─────────┼────────────────┼────────────────┼────────────────────┼────────────┘
          │                │                │                    │
          ▼                ▼                ▼                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          PRODUCT SERVICES                                    │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │     CPQ     │  │   Catalog   │  │ Acquisition │  │    Billing/Rev      │ │
│  │  (Next Gen) │  │  (Bundles)  │  │  (Journeys) │  │    (Core)           │ │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────────┬──────────┘ │
└─────────┼────────────────┼────────────────┼────────────────────┼────────────┘
          │                │                │                    │
          └────────────────┴────────┬───────┴────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                       INTERSECTION LAYER (Platform)                          │
│                                                                              │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────────────┐  │
│  │       BCS       │  │  Rules Engine   │  │       Orchestration         │  │
│  │ (Context Svc)   │  │   (Universal)   │  │         (Flows)             │  │
│  │                 │  │                 │  │                             │  │
│  │ • Who (customer)│  │ • Eligibility   │  │ • Journey coordination      │  │
│  │ • What (product)│  │ • Pricing rules │  │ • State management          │  │
│  │ • Where (geo)   │  │ • Validation    │  │ • Event routing             │  │
│  │ • Why (context) │  │ • Bundling      │  │ • Async processing          │  │
│  │ • When (time)   │  │ • Constraints   │  │ • Retry/compensation        │  │
│  └────────┬────────┘  └────────┬────────┘  └─────────────┬───────────────┘  │
│           │                    │                         │                   │
│           └────────────────────┼─────────────────────────┘                   │
│                                │                                             │
│  ┌─────────────────────────────┴─────────────────────────────────────────┐  │
│  │                        PRICING ENGINE                                  │  │
│  │                        (Separated)                                     │  │
│  │                                                                        │  │
│  │  • Sub-100ms response time (p95)                                       │  │
│  │  • Separated from billing rating                                       │  │
│  │  • Supports real-time quoting, self-serve, POS                         │  │
│  │  • Consumes rules from Rules Engine                                    │  │
│  └────────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          CORE PLATFORM                                       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │   Orders    │  │ Subscriptions│  │   Revenue   │  │     Data Layer      │ │
│  │             │  │             │  │             │  │                     │ │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## NOW (0-3 months): Implementation Details

### 1. CPQ X Stability & Performance

**User Value**: Existing enterprise customers can trust the system for complex deals.

**Timeline**: Ongoing, Sprint 1-6

**Effort**: ~25 story points/sprint (maintenance allocation)

**Technical Approach**:

This is maintenance work on the Salesforce-native CPQ. Focus on performance optimization and critical bug fixes only—no new features. The goal is to keep current customers functional while Next Gen CPQ matures.

Key performance issues to address:
- Quote save operations exceeding 30s on complex quotes (>50 lines)
- Salesforce sync reliability issues causing data inconsistency
- SOQL query limits being hit on large accounts

**Components Affected**:
- CPQ X Salesforce Package: Query optimization, batch processing improvements
- Sync Service: Retry logic, conflict resolution, monitoring
- Quote Line Processing: Pagination, lazy loading

**Non-Functional Requirements**:
- Performance: Quote save < 10s for quotes under 100 lines
- Reliability: Sync success rate > 99.5%
- Monitoring: Full observability on sync failures with alerting

**Technical Risks**:
- Salesforce governor limits constrain optimization options
- Sync architecture is fundamentally brittle—fixes are tactical, not strategic
- Investment competes with Next Gen CPQ resources

**Testing Strategy**:
- Regression suite for all changes (existing)
- Performance benchmarks on representative data sets
- Sync reliability monitoring with automated alerts

---

### 2. Next Gen CPQ MVP (Off-Salesforce Core)

**User Value**: Large quote handling (>100 lines) without performance degradation.

**Timeline**: Sprint 1-12 (3 months)

**Effort**: 150-180 story points

**Technical Approach**:

Build the core quoting engine as a standalone service, independent of Salesforce. This is the foundation for all future CPQ capabilities. Architecture choices:

- **Event-driven architecture**: Quote lifecycle events published to Kafka for downstream consumption
- **Domain-driven design**: Quote, QuoteLine, PricingResult as core aggregates
- **CQRS pattern**: Separate read/write models for performance at scale
- **API-first**: GraphQL for complex queries, REST for simple operations

The MVP scope is deliberately limited: create quote, add lines, apply pricing, save/retrieve. No configurator, no approvals, no workflows yet.

**Components Affected**:
- New Service: `cpq-core-service` (Kotlin/Spring Boot)
- New Database: PostgreSQL for quote storage (consider TimescaleDB for audit trail)
- API Gateway: New routes for CPQ endpoints
- Event Bus: Kafka topics for quote events

**New Infrastructure**:
```
┌─────────────────────────────────────────────────────────────┐
│  cpq-core-service (New)                                     │
│  ├── Quote Management API                                   │
│  ├── Pricing Integration                                    │
│  └── Event Publisher                                        │
├─────────────────────────────────────────────────────────────┤
│  PostgreSQL (cpq-db)                                        │
│  ├── quotes                                                 │
│  ├── quote_lines                                            │
│  ├── pricing_snapshots                                      │
│  └── audit_log                                              │
├─────────────────────────────────────────────────────────────┤
│  Kafka Topics                                               │
│  ├── cpq.quote.created                                      │
│  ├── cpq.quote.updated                                      │
│  ├── cpq.quote.priced                                       │
│  └── cpq.quote.finalized                                    │
└─────────────────────────────────────────────────────────────┘
```

**APIs & Integrations**:
- Consumes: Catalog API (product data), Pricing Engine (price calculation), Customer Service (account data)
- Exposes: Quote CRUD, Quote Line management, Price calculation trigger
- Events: Publishes quote lifecycle events for downstream systems

**Non-Functional Requirements**:
- Performance: < 500ms for quote operations up to 500 lines
- Scalability: Handle 1000 concurrent quote sessions
- Availability: 99.9% uptime
- Data: Full audit trail, point-in-time quote reconstruction

**Technical Dependencies**:
- Catalog API (stable—v1 available)
- Pricing Engine (current billing pricing endpoint—will need migration when separated)
- Authentication: OAuth 2.0 via existing identity service

**Technical Risks**:

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Pricing Engine performance blocks complex quotes | High | High | Implement caching layer, async pricing for large quotes |
| Catalog data model doesn't support CPQ needs | Medium | High | Early integration testing, schema alignment sessions with Catalog team |
| Event ordering issues with CQRS | Medium | Medium | Implement idempotency, event versioning from start |

**Phases**:
1. **Phase 1 (4 weeks)**: Core domain model, basic CRUD, unit tests
2. **Phase 2 (4 weeks)**: Pricing integration, event publishing, integration tests
3. **Phase 3 (4 weeks)**: Performance optimization, load testing, hardening

**Testing Strategy**:
- Unit tests: 85%+ coverage on domain logic
- Integration tests: All Catalog/Pricing integration paths
- Contract tests: Pact tests for API consumers
- Load testing: 2x expected peak (2000 concurrent sessions)
- Chaos testing: Pricing service failure scenarios

**Rollout Plan**:
- Feature flag: `cpq.nextgen.enabled`
- Initial: Internal testing only
- Phase 1: 5 design partners (hand-selected)
- Phase 2: New customers only (no migration)

---

### 3. Catalog Bundles (Hard/Soft)

**User Value**: Marketing creates bundles without engineering involvement.

**Timeline**: Sprint 1-8 (2 months)

**Effort**: 80-100 story points

**Technical Approach**:

Implement two bundle types in the catalog service:

- **Hard Bundles**: Fixed product combinations, sold as single SKU. Components not individually modifiable.
- **Soft Bundles**: Configurable product combinations with constraints. Components can be swapped within rules.

The bundle definition model:
```json
{
  "bundleId": "uuid",
  "type": "HARD | SOFT",
  "components": [
    {
      "productId": "uuid",
      "quantity": { "min": 1, "max": 10, "default": 1 },
      "required": true,
      "substitutes": ["product-id-1", "product-id-2"]
    }
  ],
  "constraints": [
    {
      "type": "MUTUAL_EXCLUSION | REQUIRES | QUANTITY_RATIO",
      "definition": { ... }
    }
  ],
  "pricing": {
    "type": "SUM_COMPONENTS | FIXED | DISCOUNT_PERCENT",
    "value": { ... }
  }
}
```

**Components Affected**:
- Catalog Service: New bundle domain, constraint engine, API extensions
- Catalog Database: Bundle tables, constraint definitions
- Admin UI: Bundle builder interface (separate effort)

**New Infrastructure**:
- Constraint evaluation engine (embedded, rules-engine-compatible interface)
- Bundle pricing calculator

**APIs & Integrations**:
- New endpoints: `/bundles`, `/bundles/{id}/validate`, `/bundles/{id}/price`
- Consumed by: CPQ (configurator), Experiences (self-serve), Admin UI
- Events: `catalog.bundle.created`, `catalog.bundle.updated`

**Non-Functional Requirements**:
- Performance: Constraint validation < 100ms for bundles up to 50 components
- Scalability: Support 10,000+ bundle definitions
- Versioning: Full bundle version history, point-in-time retrieval

**Technical Dependencies**:
- Rules Engine decision (constraints may move to shared rules engine)
- Pricing Engine integration for bundle pricing

**Technical Risks**:

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Constraint engine duplicates Rules Engine work | High | Medium | Design constraint interface to be rules-engine-compatible from start |
| Complex bundles create performance issues | Medium | Medium | Limit initial complexity, add caching layer |
| CPQ Configurator requirements unclear | Medium | High | Joint design sessions with CPQ team before finalizing schema |

**Phases**:
1. **Phase 1 (3 weeks)**: Hard bundle support (fixed combinations)
2. **Phase 2 (3 weeks)**: Soft bundle support (configurable)
3. **Phase 3 (2 weeks)**: Constraint engine, validation API

**Testing Strategy**:
- Unit tests: 80%+ coverage
- Integration tests: Bundle → Pricing, Bundle → CPQ
- Performance tests: Constraint evaluation at scale

---

### 4. BCS Phase 1 (Business Context Service)

**User Value**: Right pricing/products shown automatically based on context.

**Timeline**: Sprint 1-8 (2 months)

**Effort**: 60-80 story points

**Technical Approach**:

BCS is the "brain" of the intersection layer—it determines context for any commerce interaction. Phase 1 focuses on basic context detection:

- **Location context**: IP geolocation, explicit country selection
- **Channel context**: Self-serve, sales-assisted, partner, API
- **Customer context**: Anonymous, known prospect, existing customer
- **Time context**: Current date/time for time-based rules

Context is assembled into a `BusinessContext` object that downstream services consume:

```json
{
  "contextId": "uuid",
  "timestamp": "2025-01-15T10:30:00Z",
  "location": {
    "country": "US",
    "region": "CA",
    "currency": "USD",
    "locale": "en-US"
  },
  "channel": {
    "type": "SELF_SERVE",
    "source": "pricing-page",
    "sessionId": "uuid"
  },
  "customer": {
    "type": "KNOWN_PROSPECT",
    "accountId": "uuid",
    "segment": "SMB",
    "attributes": { ... }
  },
  "derived": {
    "priceListId": "uuid",
    "catalogViewId": "uuid",
    "eligiblePromotions": ["promo-1", "promo-2"]
  }
}
```

**Components Affected**:
- New Service: `business-context-service`
- API Gateway: Context enrichment middleware
- Downstream Services: Catalog, Pricing, CPQ consume context

**New Infrastructure**:
```
┌─────────────────────────────────────────────────────────────┐
│  business-context-service                                   │
│  ├── Context Assembly API                                   │
│  ├── Location Detection (MaxMind integration)               │
│  ├── Customer Resolution                                    │
│  └── Context Caching (Redis)                                │
├─────────────────────────────────────────────────────────────┤
│  Redis Cluster                                              │
│  └── Context cache (TTL: 5 min)                             │
└─────────────────────────────────────────────────────────────┘
```

**APIs & Integrations**:
- Exposes: `GET /context` (assemble from request), `GET /context/{id}` (retrieve cached)
- Consumes: Customer Service, Geolocation Service
- Consumed by: All commerce touchpoints

**Non-Functional Requirements**:
- Performance: < 50ms for context assembly (p95)
- Availability: 99.99% (critical path for all commerce)
- Caching: Context cached for session duration

**Technical Dependencies**:
- Customer Service API (stable)
- Geolocation service (MaxMind or equivalent)
- **Ownership decision required** (Acquisition vs. Platform)

**Technical Risks**:

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Ownership dispute blocks progress | High | High | Escalate for decision within 2 weeks |
| Context scope creep | Medium | Medium | Strict Phase 1 scope, defer advanced context to Phase 2 |
| Performance on critical path | Medium | High | Aggressive caching, circuit breaker pattern |

**Phases**:
1. **Phase 1a (3 weeks)**: Location and channel context
2. **Phase 1b (3 weeks)**: Customer context integration
3. **Phase 1c (2 weeks)**: Derived context (price list, catalog view)

**Testing Strategy**:
- Unit tests: 90%+ coverage (critical service)
- Integration tests: All downstream consumers
- Load testing: 10K requests/second sustained
- Chaos testing: Dependency failure scenarios

---

### 5. Experiences Platform Selection (Plasmic Evaluation)

**User Value**: Foundation for rapid experience development.

**Timeline**: Sprint 1-4 (1 month)

**Effort**: 20-30 story points (evaluation and integration)

**Technical Approach**:

Complete evaluation of Plasmic as the low-code/pro-code experience builder. Key evaluation criteria:

1. **Component integration**: Can we embed React components (existing and new)?
2. **Data binding**: How does it connect to our APIs (GraphQL, REST)?
3. **Performance**: SSR/SSG capabilities, bundle size, runtime performance
4. **Extensibility**: Can developers extend when low-code isn't enough?
5. **Deployment**: Integration with our CI/CD, hosting options
6. **Security**: Auth integration, data handling, compliance

**Components Affected**:
- New: Plasmic project setup, component library integration
- Existing: Authentication flow integration

**Deliverables**:
1. Technical evaluation document with recommendation
2. Proof-of-concept: Simple self-serve flow using Plasmic
3. Integration architecture for production use
4. Cost/benefit analysis

**Technical Risks**:

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Plasmic doesn't meet requirements | Medium | High | Parallel evaluation of alternatives (Builder.io) |
| Contract negotiation delays | Medium | Medium | Start technical work with trial license |
| Vendor lock-in concerns | Low | Medium | Abstract integration layer for portability |

**Decision Required**: Architecture review sign-off before contract commitment.

---

## NEXT (3-6 months): Implementation Details

### 6. Next Gen CPQ Configurator

**User Value**: Sales configures complex deals correctly the first time.

**Timeline**: Sprint 12-20 (8 weeks)

**Effort**: 120-150 story points

**Technical Approach**:

The configurator sits between the catalog (what can be sold) and the quote (what is being sold). It enforces rules, suggests valid configurations, and prevents invalid ones.

Architecture:
- **Configuration Session**: Stateful session tracking current selections
- **Rule Evaluation**: Real-time constraint checking against catalog rules
- **Guided Selling**: Suggestion engine based on context and selections
- **Validation**: Pre-submission validation of complete configuration

```
┌─────────────────────────────────────────────────────────────┐
│                    Configurator Service                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │  Session    │  │    Rule     │  │      Guided         │  │
│  │  Manager    │  │  Evaluator  │  │      Selling        │  │
│  └──────┬──────┘  └──────┬──────┘  └──────────┬──────────┘  │
│         │                │                    │              │
│         └────────────────┼────────────────────┘              │
│                          │                                   │
│  ┌───────────────────────┴───────────────────────────────┐  │
│  │              Configuration State Store                 │  │
│  │              (Redis + PostgreSQL)                      │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
          │                          │
          ▼                          ▼
┌─────────────────┐        ┌─────────────────────┐
│  Catalog API    │        │    Rules Engine     │
│  (Bundles,      │        │    (Constraints)    │
│   Products)     │        │                     │
└─────────────────┘        └─────────────────────┘
```

**Components Affected**:
- New Service: `cpq-configurator-service`
- CPQ Core: Integration with configuration results
- UI: Configuration interface (separate effort)

**Technical Dependencies**:
- **CRITICAL**: Catalog Bundles must be complete
- **CRITICAL**: Rules Engine decision must be made
- CPQ Core MVP must be stable

**Non-Functional Requirements**:
- Performance: Rule evaluation < 200ms for configurations up to 100 items
- State: Configuration sessions persist for 7 days
- Concurrency: Support collaborative configuration (future)

**Technical Risks**:

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Rules Engine ownership blocks integration | High | Critical | Cannot start without this decision |
| Complex rule combinations create performance issues | Medium | High | Rule evaluation caching, async validation |
| Catalog schema changes during development | Medium | Medium | Version tolerance, schema evolution strategy |

**Phases**:
1. **Phase 1 (3 weeks)**: Basic configuration with hard bundles
2. **Phase 2 (3 weeks)**: Soft bundle configuration, constraint validation
3. **Phase 3 (2 weeks)**: Guided selling, suggestions

---

### 7. Rules Engine Consolidation

**User Value**: Consistent behavior across all touchpoints.

**Timeline**: Sprint 12-24 (12 weeks)

**Effort**: 200-250 story points

**Technical Approach**:

Currently, we have rules implemented in:
- Catalog (bundle constraints)
- CPQ X (approval rules, pricing rules)
- Billing (rating rules)
- Acquisition (eligibility rules)

Consolidation strategy:
1. **Define universal rule schema** that covers all use cases
2. **Build shared rules engine service** with high-performance evaluation
3. **Migrate rules** from each system incrementally
4. **Maintain compatibility layers** during transition

Rule types to support:
- Eligibility rules (who can buy what)
- Pricing rules (discounts, adjustments)
- Constraint rules (bundles, compatibility)
- Approval rules (deal desk, governance)
- Validation rules (data quality)

**Components Affected**:
- New Service: `rules-engine-service`
- Catalog: Migration of constraint rules
- CPQ: Migration of pricing/approval rules
- Billing: Interface for rating rules (may remain separate)

**New Infrastructure**:
```
┌─────────────────────────────────────────────────────────────┐
│                    Rules Engine Service                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │    Rule     │  │    Rule     │  │      Rule           │  │
│  │   Parser    │  │  Evaluator  │  │      Store          │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
│                                                              │
│  Supported Engines:                                          │
│  • Decision Tables (simple rules)                            │
│  • Expression Language (complex rules)                       │
│  • ML Model Integration (future)                             │
└─────────────────────────────────────────────────────────────┘
```

**Technical Dependencies**:
- **CRITICAL**: Architectural decision on single engine approach
- **CRITICAL**: Buy-in from all consuming teams

**Technical Risks**:

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Teams resist migration | High | High | Executive mandate, demonstrate value early |
| Performance regression during migration | Medium | High | Parallel run, gradual cutover |
| Edge cases in rule migration | High | Medium | Extensive testing, fallback to legacy |

**Phases**:
1. **Phase 1 (4 weeks)**: Core engine, rule schema, basic evaluation
2. **Phase 2 (4 weeks)**: Catalog constraint migration
3. **Phase 3 (4 weeks)**: CPQ rules migration, pricing rules

---

### 8. Deal Room v1

**User Value**: Professional, interactive proposal experience.

**Timeline**: Sprint 16-22 (6 weeks)

**Effort**: 80-100 story points

**Technical Approach**:

Deal Room is a collaborative space where sales and customers interact on quotes. Core capabilities:
- Quote presentation with professional formatting
- Interactive pricing exploration (within approved ranges)
- Document attachment and e-signature integration
- Activity tracking and notifications

**Components Affected**:
- New Service: `deal-room-service`
- New Frontend: Deal Room web application
- CPQ Core: Quote sharing, permissions

**APIs & Integrations**:
- DocuSign/Adobe Sign integration for e-signature
- Notification service for activity alerts
- CPQ Core for quote data

**Non-Functional Requirements**:
- Security: Row-level access control, audit trail
- Performance: Real-time updates via WebSockets
- Mobile: Responsive design for tablet/mobile

**Technical Risks**:

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| E-signature integration complexity | Medium | Medium | Standard DocuSign API, proven pattern |
| Real-time sync edge cases | Medium | Medium | Operational transform or CRDT for collaboration |

---

### 9. Basic Orchestration

**User Value**: Customer can complete purchase without sales involvement.

**Timeline**: Sprint 14-22 (8 weeks)

**Effort**: 100-120 story points

**Technical Approach**:

Orchestration coordinates multi-step flows across services. For Phase 1, focus on self-serve purchase flows:

1. Product selection (Catalog)
2. Pricing (Pricing Engine)
3. Cart management (new)
4. Checkout (Payment, Order creation)
5. Provisioning trigger (downstream)

Architecture decision needed: **Zephyr vs. new orchestration approach**

Options:
- **A) Extend Zephyr**: Leverage existing investment, but architecture concerns
- **B) Build new on Temporal**: Modern workflow engine, better fit for commerce
- **C) Lightweight custom**: Simple state machine for MVP, scale later

**Components Affected**:
- New/Modified: Orchestration service
- New: Cart service
- Integration: Payment service, Order service

**Technical Dependencies**:
- BCS Phase 1 (context for flows)
- Zephyr decision
- Experience layer (UI for flows)

**Technical Risks**:

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Zephyr architecture doesn't fit | Medium | High | Outcome-first: define flow needs, then evaluate |
| Cart state complexity | Medium | Medium | Redis for session, PostgreSQL for persistence |
| Payment integration edge cases | High | Medium | Partner with existing billing payment code |

---

### 10. Experience Templates

**User Value**: Faster implementation, lower cost.

**Timeline**: Sprint 14-24 (10 weeks)

**Effort**: 80-100 story points

**Technical Approach**:

Build 3-5 reference templates for common use cases:
1. **SaaS Pricing Page**: Self-serve signup with tiered pricing
2. **Media Subscription**: Content subscription with trials
3. **Usage-Based Signup**: Metered pricing with estimates
4. **My Account Portal**: Subscriber self-service
5. **Partner Portal**: Reseller/partner experience

Each template includes:
- Plasmic design templates
- Pre-built component configurations
- API integration patterns
- Deployment scripts
- Documentation

**Components Affected**:
- Plasmic: Template projects
- Component Library: Reusable React components
- Documentation: Implementation guides

**Technical Dependencies**:
- Plasmic contract (blocking)
- BCS (context-aware templates)
- Orchestration (flow execution)

**Technical Risks**:

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Templates too rigid | Medium | Medium | Make customization easy, provide escape hatches |
| Maintenance burden | Medium | Medium | Automation for template updates |

---

## LATER (6-12 months): Implementation Details

### 11. CPQ Magic Quadrant Readiness

**User Value**: Enterprise-grade CPQ for complex B2B.

**Timeline**: Sprint 24-48 (6 months)

**Effort**: 400-500 story points

**Technical Approach**:

Complete the CPQ feature set for Magic Quadrant positioning:
- Full configurator with complex rules
- Visual configuration (2D diagrams)
- Advanced approval workflows
- Multi-currency, multi-language
- Salesforce integration (as one channel, not dependency)
- API completeness for custom integrations

**Key Milestones**:
1. Configurator complete (Sprint 28)