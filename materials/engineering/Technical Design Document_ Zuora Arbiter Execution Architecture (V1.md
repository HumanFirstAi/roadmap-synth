# **Technical Design Document: Zuora Arbiter Execution Architecture (V1.1)**

**Author:** Tony Zhang 

**Last Updated:** December 19, 2025

## **1\. Executive Summary**

The Arbiter Execution Architecture (V1.1) implements a **High-Performance Decisioning Engine** capable of sub-10ms latency at the 99th percentile. To achieve this while managing massive data ingestion from Systems of Record (SoR), the architecture enforces a strict **CQRS (Command Query Responsibility Segregation)** pattern.

This design decouples the **Context Write Path** (Asynchronous, High-Throughput ETL) from the **Decision Read Path** (Synchronous, Low-Latency Compute). This isolation ensures that bursty backend processes (e.g., billing runs) never degrade the runtime experience for the client.

## **2\. Architectural Standards & Constraints**

To satisfy the Service Level Objectives (SLOs), all components must adhere to these standards:

1. **Zero-I/O Runtime:** The runtime decision path (`/execute`) must generally perform **zero** blocking database I/O. All state must be pre-fetched or retrieved from the L2 Cache (Redis).  
2. **Schema-First Contracts:** The handshake between the Data Loader (Writer) and BCS (Reader) is governed by strict **Apache Arrow Schemas**. We utilize the Arrow IPC format to enable **Zero-Parsing Overhead**. While network I/O still involves kernel copies, this eliminates the CPU-intensive JSON deserialization step at the application layer.  
   * *Note:* JSON Schemas are used in the Authoring Plane (Lane 1\) for UI validation, while Arrow is used in the Execution Plane (Lane 2\) for performance.  
3. **Fail-Close by Default:** In the event of missing context or ambiguous logic, the system must default to a safe, conservative state (e.g., "Deny Transaction") rather than guessing.

## **3\. High-Level Architecture: The "Two-Lane" Model**

### **3.1 Lane 1: The Definition & Hydration Plane (Write Path)**

* **Infrastructure:** MySQL (Graph Store), **Dedicated Loader App** (Stateless Java Consumer), Stateless Compiler Service.  
* **Responsibility:**  
  * Compiles Business Graphs into Executable Blueprints and **Bitmask Indices**.  
  * Transforms raw "System of Record" data into "Decision-Ready Context."  
* **SLO:**  
  * Blueprint Compilation: \< 2 seconds.  
  * Data Freshness: \< 15 seconds.

### **3.2 Lane 2: The Decision Execution Plane (Read Path)**

* **Infrastructure:** Stateless Java services, Redis Cluster, Local In-Memory Cache.  
* **Responsibility:** Executes compiled Blueprints against hydrated Context.  
* **SLO:** P99 Latency \< 10ms.

## **4\. Latency Budget (\<10ms P99)**

To guarantee the SLO, we allocate time budgets strictly:

| Operation | Budget | Technology Strategy |
| ----- | ----- | ----- |
| **Network RTT** | 2ms | gRPC over HTTP/2; Cluster locality. |
| **Context Fetch** | 3ms | Redis Pipeline (GET Arrow Buffer \+ GET Blueprint). **Near-Cache (L1) reduces this to 0.01ms.** |
| **Deserialization** | **\< 0.1ms** | **Apache Arrow IPC (Memory mapped access; Zero-Parsing).** |
| **Logic Execution** | 3ms | **SIMD Bitwise Filtering** \+ AOT Compiled CEL. |
| **Overhead/GC** | 1ms | Low-allocation garbage collection tuning. |
| **Total** | **\< 10ms** |  |

## **5\. Detailed Component Specifications**

### **5.1 Customer Data Loader (Context Writer)**

* **Pattern:** Event-Driven Consumer (Java Service).  
* **Input:** Kafka Topics (`billing.accounts`, `catalog.products`, `usage.aggregates`).  
* **Logic:**  
  1. **Batching & Deduplication:** Buffers incoming events in-memory (or local RocksDB) to merge rapid updates for the same entity (e.g., 5 updates in 100ms → 1 Write).  
  2. **Transformation:** Converts Domain Models (SoR) into Decision Models.  
  3. **Materialization:** Serializes the Context into an **Apache Arrow IPC Buffer**.  
  4. **Bitmasking:** Calculates the **Context Bitmask** (e.g., `Region=EU | VIP`) and embeds it in the Arrow metadata.  
  5. **Write:** Upserts the binary buffer to Redis using a **Hash Tag** strategy `context:{tenant_id}:{user_id}`.

### **5.2 Business Context Service (BCS \- The Runtime)**

* **Pattern:** Stateless Compute Function.  
* **Security:** JWT Validation (RSA-256) via Sidecar or Middleware.  
* **API Contract:**

```java
POST /v1/execute
Header: X-Tenant-ID: <string>
Header: Authorization: Bearer <JWT>
Body: {
  "client_id": "uuid",
  "action_intent": "checkout_pricing",
  "dynamic_inputs": { "cart_total": 500.00 }
}
```

* **Internal Logic:**  
  1. **AuthZ:** Validate JWT signature and scope claims.  
  2. **L1 Cache:** Check process-local memory for hot Blueprints.  
  3. **Request Coalescing:** Use **Singleflight** pattern. If 100 requests need `context:123`, only 1 network call is made to Redis.  
  4. **L2 Cache:** MGET `context:{user}` (Arrow Buffer) and `blueprint:{intent}`.  
  5. **Zero-Parsing Load:** Wrap byte array in `ArrowRecordBatch` (Direct memory access).  
  6. **Execution:** Run Blueprint VM (See Section 6.5).

### **5.3 Shared State Store (Redis Cluster)**

* **Role:** The decoupling buffer.  
* **Configuration:**  
  * **Eviction Policy:** `allkeys-lru`.  
  * **Client-Side Caching:** Enabled (Redis 6+) to invalidate L1 caches on write.  
  * **Persistence:** RDB (Snapshot) for warm restarts.

### **5.4 Graph Compiler Service (The Logic Writer)**

* **Pattern:** Asynchronous Worker.  
* **Trigger:** User publishes a Graph in the UI.  
* **Detailed 7-Step Pipeline:**  
  1. **Normalize:** Standardizes the graph structure.  
  2. **Lint:** Validates syntax and basic rules (e.g., detecting cycle candidates).  
  3. **Prune:** Removes disconnected or logically impossible paths.  
  4. **Order:** Performs topological sort.  
  5. **Arbitrate:** Groups `EXCLUDES` nodes into `SelectorStep`s.  
  6. **Synthesize Guards:** Converts dependencies into CEL guards.  
  7. **Optimize & Emit:**  
     * Generates **Rule Bitmasks** for SIMD filtering.  
     * Compiles CEL strings into ASTs.  
     * Writes the final Blueprint JSON to Redis.

## **6\. Object Model & Schema Design**

The DSS follows a three-tier lifecycle: **Authoring (Graph)** → **Compilation (Blueprint)** → **Execution (Runtime)**.

### **6.1 Core Domain Objects**

#### **6.1.1 Graph Object (GraphEntity)**

The visual representation of decision logic.

* **Nodes:**  
  * `DecisionNode`: Entry point or branching logic.  
  * `EvaluatorNode`: Predicate logic (CEL Expressions).  
  * `ActionNode`: Outcome or side effect.  
* **Edges:**  
  * `REQUIRES`: Dependency (A requires B to be true).  
  * `FLOWS_TO`: Sequence or choice (Decision A flows to Action B).  
  * `EXCLUDES`: Conflict (Action A and Action B cannot both occur).  
  * `NEUTRALIZES`: Cancellation (Action A cancels Action B if both pass).

#### **6.1.2 Blueprint Object (BlueprintEntity)**

The compiled artifact optimized for execution.

* **Steps:** `SequentialStep`, `SelectorStep`, `TaskStep`.  
* **Optimization Metadata:**  
  * `bitmask_index`: Map of `bit_position` to `attribute_value` (e.g., 0 \-\> "EU").  
  * `rule_masks`: Array of integers representing the requirements for each step.

#### **6.1.3 Mapping Specification (MappingSpecEntity)**

Defines how a raw event (e.g., from Kafka) is transformed into the evaluation context.

* **Source:** Raw event fields.  
* **Lookups:** Definitions for enriching the event with data from external tables (Fluss/MySQL). Supports multi-lookup (Product \+ Customer \+ Subscription).  
* **Map:** Direct field-to-field mapping from event to context.

### **6.2 Database Schema (MySQL)**

#### graphs

| Column | Type | Description |
| ----- | ----- | ----- |
| `id` | BIGINT (PK) | Auto-incrementing ID |
| `name` | VARCHAR(255) | Display name |
| `graph_json` | JSON | Full graph structure (nodes/edges) |
| `active_blueprint_id` | BIGINT (FK) | Currently deployed blueprint |
| `version` | INT | Version number |

#### blueprints

| Column | Type | Description |
| ----- | ----- | ----- |
| `id` | BIGINT (PK) | Auto-incrementing ID |
| `graph_id` | BIGINT (FK) | Link to source graph |
| `blueprint_json` | LONGTEXT | Flattened execution plan |
| `hash` | VARCHAR(64) | SHA-256 hash |
| `status` | VARCHAR | ACTIVE/INACTIVE |

#### context\_schemas

| Column | Type | Description |
| ----- | ----- | ----- |
| `id` | BIGINT (PK) | Auto-incrementing ID |
| `name` | VARCHAR(255) | e.g., "VIPContext" |
| `schema_json` | TEXT | JSON Schema (For UI/Validation) |
| `arrow_schema_def` | BLOB | Arrow Schema (For Runtime Serialization) |

#### context\_data

| Column | Type | Description |
| ----- | ----- | ----- |
| `id` | BIGINT (PK) | ID |
| `context_schema_id` | BIGINT (FK) | Schema Reference |
| `name` | VARCHAR | Lookup Key |
| `data_json` | TEXT | Enriched data payload |

#### mapping\_specs

| Column | Type | Description |
| ----- | ----- | ----- |
| `id` | BIGINT (PK) | Spec identifier |
| `name` | VARCHAR | Spec Name |
| `spec_json` | JSON | Lookup and mapping rules |

#### usage\_events

*(Simulation Input)*

| Column | Type | Description |
| ----- | ----- | ----- |
| `event_id` | VARCHAR (PK) | Unique Event ID |
| `customer_id` | VARCHAR | Customer Reference |
| `sku` | VARCHAR | Product Reference |
| `event_json` | TEXT | Constructed JSON for Flink Injection |

### **6.3 Relationship Matrix (Edges)**

The Compiler interprets edges to generate the Blueprint structure:

| Edge Type | Interpreted As | Compilation Effect |
| ----- | ----- | ----- |
| **FLOWS\_TO** | Control Flow | Determines branch membership in a `SelectorStep`. |
| **REQUIRES** | Hard Dependency | Becomes a `Runtime Guard` on the target node. |
| **DOMINATES** | Priority | Forces ordering in `SequentialStep` and sets suppression flags. |
| **EXCLUDES** | Mutual Exclusion | Groups nodes into a `SelectorStep` for arbitration. |
| **NEUTRALIZES** | Cancellation | Becomes a guard: `SKIP IF SOURCE_NODE_EXECUTED`. |

### **6.4 Data Ingestion Pipeline Object Design**

This section defines the data flow from Systems of Record (SoR) to the Decision Engine (Redis). To accommodate different scales, we define two implementation paths.

#### **6.4.1 Path A: Dedicated Loader App (Small/Moderate Scale)**

* **Implementation:** Stateless Java Service with Horizontal Autoscaling.  
* **Component:** `LoaderConsumer`  
  1. **Poll:** Reads batches from Kafka topics (Billing/Catalog).  
  2. **Enrich:** Performs simple in-memory joins against cached lookup maps (refreshed via CDC).  
  3. **Assemble:** Uses the **Apache Arrow Java API** to build `VectorSchemaRoot` objects.  
  4. **Bitmask:** Computes integer masks for categorical fields.  
  5. **Sink:** Writes `ArrowRecordBatch` bytes to Redis via Pipeline.

#### **6.4.2 Path B: Streaming Platform (High Scale)**

* **Implementation:** Apache Flink.  
* **Use Case:** High-volume streaming aggregation (e.g., real-time usage metering \> 50k EPS).  
* **Component:** `BlueprintExecutorFunction`  
  1. **Source:** Kafka Source.  
  2. **Enrichment:** Flink SQL performs **Temporal Joins** with lookup tables.  
  3. **Sink:** Flink Redis Sink writes the Arrow Buffer.

### **6.5 Execution Logic (The Optimized Engine)**

The runtime engine uses a **Filter-then-Evaluate** pattern to minimize CPU usage.

**1\. Sequential Execution**

```java
# Optimization: Singleflight (Request Coalescing) handles the fetch
blueprint, context = fetch_resources_coalesced(clientId, blueprintId)

# Optimization: Zero-Copy Load
arrow_reader = ArrowRecordBatch(context.buffer)
user_mask = context.metadata['bitmask'] # e.g., 101 (EU + Mobile)

for step in SequentialStep.children:
    # Optimization: SIMD Bitwise Pre-Filter
    # "rule_mask" is pre-calculated by Compiler.
    # If User lacks a required bit, we skip immediately (Nanoseconds).
    if (user_mask & step.rule_mask) != step.rule_mask:
        continue

    # Fallback: Heavy CEL Evaluation (Microseconds)
    # Only runs if the bitmask check passed.
    if step.guards.cel_program.eval(arrow_reader):
        execute(step)
```

**2\. Selector (Arbitration) Execution**

```java
candidates = []
for branch in SelectorStep.branches:
    # Optimization: SIMD Filter
    if (user_mask & branch.rule_mask) != branch.rule_mask:
        continue

    # Standard Guard Check
    if branch.guards.cel_program.eval(arrow_reader):
        candidates.add(branch)

# Conflict Resolution
winner = policy.apply(candidates, comparator)
execute(winner)
```

### **6.6 Conflict Resolution Mechanism**

Arbiter explicitly handles conflicting business logic (e.g., "Discount A" vs "Discount B" where only one is allowed).

**1\. Compile-Time Grouping** The `ExclusionArbitrator` scans the Graph for `EXCLUDES` edges. It logically groups all mutually exclusive nodes into a single container called a `SelectorStep`.

**2\. Runtime Selection** When the Blueprint Engine encounters a `SelectorStep`:

1. **Filter:** It evaluates the Guards for all candidate branches.  
2. **Score:** It calculates scores based on node metadata (e.g., `priority` field).  
3. **Select:** It applies the configured `Policy` (e.g., `BestMatch`) to pick the winner(s) using a `Comparator` (e.g., `HighestPriority`).

## **7\. Resilience & Consistency Strategies**

### **7.1 Cache Miss (Fail-Safe)**

If `GET context:{user}` returns `null` (Cache Miss):

* **Action:** Execute Blueprint using `Anonymous/Default` context.  
* **Healing:** Asynchronously trigger a Data Loader re-sync for this user.

### **7.2 Redis Outage**

* **Action:** Degrade to Local Cache (L1). If L1 is empty, fail closed (Deny).

### **7.3 Data Consistency (Read-Your-Writes)**

**Problem:** The Data Loader has a **5-second** lag. A user might perform an action (e.g., "Upgrade Plan") and immediately expect the new rules to apply.

**Strategy: Optimization Tokens (Mutation Tokens)**

1. **Issue:** When a critical write occurs (e.g., Plan Upgrade), the Mutation API returns a signed **Mutation Token** (JWT) containing the *new* state (e.g., `role=VIP`).  
2. **Propagate:** The Client passes this token in the `dynamic_inputs` of the `/execute` call.  
3. **Resolve:** The BCS Logic prefers `dynamic_inputs` (Token) over `redis_context` (Stale).  
4. **Result:** Immediate consistency for the user without waiting for the async ETL pipeline.

## **8\. Observability & Auditing**

* **Distributed Tracing:** Trace ID propagates from Client \-\> BCS \-\> Redis.  
* **Decision Logs:** Asynchronous push to `arbiter-decisions` Kafka topic.

## **9\. Next Steps (Implementation Phase)**

1. **Define the Schema Registry:** Establish the `.arrow` schemas.  
2. **Prototype the "Mutation Token":** Proof-of-concept for the consistency strategy.  
3. **Redis Benchmarking:** Validate `MGET` performance with Arrow binary payloads.

## **Appendix A: Node Taxonomy**

* **Evaluator:** Stateless condition (CEL).  
* **Decision:** Structural routing (BestMatch, AllMatch etc.).  
* **Action:** Effectful payload (e.g., "apply\_discount").  
* **Composite:** A group node containing a sub-graph.

## **Appendix B: API Specification**

This section details the REST API endpoints available in the Decision Authoring System (DAS).

### **B.1 Graph Management**

**Base Path:** `/dss/graphs`

#### **1\. Save Graph**

* **Endpoint:** `POST /dss/graphs`  
* **Description:** Saves a new graph or a new version of an existing graph.  
* **Request Body:** `SaveGraphRequest` (name, nodes, edges, contextSchemaIds)  
* **Response:** `GraphEntity`

#### **2\. Get All Graphs**

* **Endpoint:** `GET /dss/graphs`  
* **Description:** Retrieves all saved graphs.  
* **Response:** `List<GraphEntity>`

#### **3\. Get Graph by ID**

* **Endpoint:** `GET /dss/graphs/{id}`  
* **Description:** Retrieves a specific graph by its ID.  
* **Response:** `GraphEntity`

#### **4\. Get Graph History**

* **Endpoint:** `GET /dss/graphs/{name}/history`  
* **Description:** Retrieves all versions of a graph by its name.  
* **Response:** `List<GraphEntity>`

### **B.2 Authoring & Compilation**

**Base Path:** `/dss`

#### **1\. Compile Graph**

* **Endpoint:** `POST /dss/graphs/{graphId}/compile`  
* **Description:** Compiles a graph into an executable Blueprint.  
* **Request Body:** `CompileGraphRequest` (nodes, edges, contextSchemaIds)  
* **Response:** `CompileGraphResponse` (blueprint, metadata, errors, warnings)

#### **2\. Activate Blueprint**

* **Endpoint:** `POST /dss/blueprints/{id}/activate`  
* **Description:** Activates a specific blueprint version for a graph.  
* **Request Body:** `ActivateBlueprintRequest` (activatedBy)  
* **Response:** `ActivateBlueprintResponse`

### **B.3 Schema Management**

**Base Path:** `/dss/schemas`

#### **1\. List All Schemas**

* **Endpoint:** `GET /dss/schemas`  
* **Description:** Retrieves all context schemas.  
* **Response:** `List<ContextSchemaDTO>`

#### **2\. Get Schema by ID**

* **Endpoint:** `GET /dss/schemas/{id}`  
* **Description:** Retrieves a specific schema by its ID.  
* **Response:** `ContextSchemaDTO`

#### **3\. Create Schema**

* **Endpoint:** `POST /dss/schemas`  
* **Description:** Creates a new context schema.  
* **Request Body:** `ContextSchemaDTO`  
* **Response:** `ContextSchemaDTO`

#### **4\. Update Schema**

* **Endpoint:** `PUT /dss/schemas/{id}`  
* **Description:** Updates an existing schema.  
* **Request Body:** `ContextSchemaDTO`  
* **Response:** `ContextSchemaDTO`

#### **5\. Delete Schema**

* **Endpoint:** `DELETE /dss/schemas/{id}`  
* **Description:** Deletes a specific schema.  
* **Response:** `204 No Content`

### **B.4 Data Management**

**Base Path:** `/dss/data`

#### **1\. List All Context Data**

* **Endpoint:** `GET /dss/data`  
* **Description:** Retrieves all context data. Optional filtering by `schemaId`.  
* **Query Params:** `schemaId` (optional)  
* **Response:** `List<ContextDataDTO>`

#### **2\. Get Data by ID**

* **Endpoint:** `GET /dss/data/{id}`  
* **Description:** Retrieves a specific data entry.  
* **Response:** `ContextDataDTO`

#### **3\. Create Data**

* **Endpoint:** `POST /dss/data`  
* **Description:** Creates a new context data entry.  
* **Request Body:** `ContextDataDTO`  
* **Response:** `ContextDataDTO`

#### **4\. Update Data**

* **Endpoint:** `PUT /dss/data/{id}`  
* **Description:** Updates an existing data entry.  
* **Request Body:** `ContextDataDTO`  
* **Response:** `ContextDataDTO`

#### **5\. Delete Data**

* **Endpoint:** `DELETE /dss/data/{id}`  
* **Description:** Deletes a specific data entry.  
* **Response:** `204 No Content`

### **B.5 Evaluation (Runtime)**

**Base Path:** `/dss`

#### **1\. Evaluate Blueprint**

* **Endpoint:** `POST /dss/evaluate`  
* **Description:** Executes an activated blueprint against a given context.  
* **Request Body:** `EvaluateBlueprintRequest` (blueprintId, context)  
* **Response:** `EvaluateBlueprintResponse` (actions, rationale, metadata)

### **B.6 Mapping Specifications**

**Base Path:** `/dss/mapping-specs`

#### **1\. List All Mapping Specs**

* **Endpoint:** `GET /dss/mapping-specs`  
* **Description:** Lists all available mapping specifications in the database.  
* **Response:** `List<Map<String, Object>>` (id, name, version, dates)

#### **2\. Get Spec by Name and Version**

* **Endpoint:** `GET /dss/mapping-specs/{name}/{version}`  
* **Description:** Retrieves the JSON specification for a given name and version.  
* **Response:** `JSON string`

#### **3\. Upsert Mapping Spec**

* **Endpoint:** `PUT /dss/mapping-specs/{name}/{version}`  
* **Description:** Creates or updates a mapping specification.  
* **Request Body:** `JSON string`  
* **Response:** `JSON string`

#### **4\. Delete Mapping Spec**

* **Endpoint:** `DELETE /dss/mapping-specs/{name}/{version}`  
* **Description:** Deletes a mapping specification.  
* **Response:** `204 No Content`

#### **5\. Get Stream Event Mapping (v1)**

* **Endpoint:** `GET /dss/mapping-specs/stream-event/v1`  
* **Description:** Quick access to the default stream event mapping (v1).  
* **Response:** `JSON string`

### **B.7 Stream Simulation**

**Base Path:** `/dss/stream/simulation`

#### **1\. Inject Usage Event**

* **Endpoint:** `POST /dss/stream/simulation/inject`  
* **Description:** Simulates a usage event by injecting it into the pipeline.  
* **Request Body:** `Map<String, Object>` (eventId, customerId, sku, graphId, mappingSpecId, etc.)  
* **Response:** `{ "status": "injected", "eventId": "..." }`

#### **2\. Get Stream Results**

* **Endpoint:** `GET /dss/stream/simulation/results/{eventId}`  
* **Description:** Fetches evaluation results for a specific event from ClickHouse.  
* **Response:** `List<Map<String, Object>>`

#### **3\. Lookup Enrichment Data**

* **Endpoint:** `GET /dss/stream/simulation/lookup`  
* **Description:** Synchronously lookup data from the context store (used for UI previews).  
* **Query Params:** `schemaName`, `schemaVersion`, `key`  
* **Response:** `JSON string` (the data\_json)

### **B.8 Search**

**Base Path:** `/dss/search`

#### **1\. Universal Search**

* **Endpoint:** `GET /dss/search`  
* **Description:** Searches across graphs, schemas, and blueprints.  
* **Query Params:** `q` (search query), `type` (optional filter)  
* **Response:** `List<SearchResultDTO>`

### **B.9 AI Generation**

**Base Path:** `/dss/ai`

#### **1\. Generate Graph from Prompt**

* **Endpoint:** `POST /dss/ai/generate`  
* **Description:** Uses AI to generate a graph structure based on a natural language prompt.  
* **Request Body:** `{ "prompt": "..." }`  
* **Response:** `CompilerInput` (nodes and edges)

