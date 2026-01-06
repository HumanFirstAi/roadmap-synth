# Engineering Persona - Roadmap Formatting

You are reformatting a product roadmap for an **engineering audience** (software engineers, architects, tech leads, engineering managers).

## Audience Needs

Engineers need to:
- Understand technical scope and complexity
- See architecture and system design implications
- Know infrastructure and tooling requirements
- Identify technical dependencies and blockers
- Assess technical debt and quality implications
- Plan sprints and resource allocation

## Output Requirements

### Length
5-10 pages (comprehensive technical detail acceptable)

### Structure

1. **Technical Vision** (1 paragraph)
   - High-level technical strategy
   - Major architectural themes or shifts

2. **Feature Implementation Details**
   For each major feature/initiative:
   - **Feature Name & User Value** (brief - 1 sentence)
   - **Technical Approach**: High-level architecture, key design decisions
   - **Components Affected**: What systems/services need changes?
   - **New Infrastructure**: Any new services, databases, tools, or platforms?
   - **APIs & Integrations**: External or internal API changes
   - **Non-Functional Requirements**: Performance, scalability, security, reliability
   - **Technical Complexity**: Story points or person-weeks if available
   - **Phases**: Can this be broken into smaller deliverables?
   - **Technical Dependencies**: Libraries, frameworks, platform requirements
   - **Technical Risks**: What's hard? What's unknown? What could fail?
   - **Testing Strategy**: Unit, integration, E2E, performance testing needs
   - **Rollout Plan**: Feature flags, gradual rollout, rollback strategy

3. **Technical Debt & Platform Work**
   - Critical tech debt that must be addressed
   - Infrastructure improvements needed
   - Platform investments that enable future features
   - Quality and reliability improvements

4. **Architecture Decisions**
   - Key architectural choices
   - Trade-offs made
   - Why we chose approach A over B

5. **Resource & Skill Requirements**
   - Team composition needed
   - Skills or expertise required
   - External dependencies (vendor tools, consultants)

6. **Timeline & Milestones**
   - Sprint or milestone-based timeline
   - Technical milestones (e.g., "API v2 stable", "Migration 50% complete")
   - Dependencies between technical workstreams

## Tone & Style

- **Technically precise**: Use correct technical terminology
- **Honest about complexity**: Don't sugarcoat hard problems
- **Detail-oriented**: Engineers want specifics
- **Pragmatic**: Focus on what's feasible and maintainable
- **Quality-conscious**: Call out testing, monitoring, and operational needs

## What to Include

✅ Technical architecture and design
✅ System components affected
✅ APIs and integration points
✅ Database/storage changes
✅ Performance and scalability requirements
✅ Security and compliance considerations
✅ Testing strategy
✅ Deployment and rollout approach
✅ Monitoring and observability needs
✅ Technical dependencies and blockers
✅ Technical debt implications
✅ Story points or person-weeks
✅ Infrastructure requirements

## What to Exclude

❌ Business justifications (keep brief)
❌ Marketing or sales details
❌ High-level strategic context (unless technical strategy)

## Feature Template

Use this format for each major feature:

### [Feature Name]
**User Value**: [1 sentence - just context]
**Timeline**: Sprint 12-15 (6-8 weeks)
**Effort**: 40-50 story points

**Technical Approach**:
[2-3 paragraphs describing architecture, key design decisions, technology choices]

**Components Affected**:
- API Gateway: [changes needed]
- User Service: [changes needed]
- Database: [schema changes, migrations]
- Frontend: [UI changes, new components]

**New Infrastructure**:
- Redis cluster for caching
- Kafka topic for event streaming
- New Lambda functions for async processing

**Non-Functional Requirements**:
- Performance: < 200ms p95 latency
- Scalability: Support 10K concurrent users
- Security: OAuth 2.0, encryption at rest
- Reliability: 99.9% uptime SLA

**Technical Dependencies**:
- Requires: Authentication service v2, Database migration #47
- Blocks: Mobile app v3.0, Partner API v2

**Technical Risks**:
- Database migration on large table (200M rows) - needs careful planning
- New caching layer adds complexity - need fallback strategy
- Third-party API rate limits may impact throughput

**Testing Strategy**:
- Unit tests: 80%+ coverage
- Integration tests: Critical paths
- Load testing: 2x expected peak load
- Chaos engineering: Fault injection tests

**Phases**:
1. Phase 1: Backend API (3 weeks)
2. Phase 2: Frontend integration (2 weeks)
3. Phase 3: Gradual rollout with feature flag (1 week)

## Example Framing

Instead of: "Improve user experience"
Say: "**Implement GraphQL API Layer** - Replace REST endpoints with GraphQL to reduce API calls by 60%, improve mobile app performance. Requires: Apollo Server setup, schema migration, gradual rollout behind feature flag. Complexity: 35 story points."

Now, reformat the master roadmap for the engineering audience following these guidelines.
