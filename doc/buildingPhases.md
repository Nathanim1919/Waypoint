# Waypoint (Nexus) — Phased Build Roadmap

This document is a working reference, meant to sit beside `architecture.md`, `system_design.md`, and `adr.md` while building. It exists to answer one question at any point in the build: *what phase am I in, what's actually in scope, and what does "done" look like for the step I'm on.*

**How to use this doc:** before starting any new feature, check which phase it belongs to. If it doesn't belong to the current phase, don't build it yet — write it down as a forward note instead (several are already flagged below). If building reveals a better design than what's written here, update this doc and record *why* in an ADR. This doc is a map, not a contract.

---

## Guiding principles (carried through all three phases)

1. **Proof over feature-count.** Every step below ends with a concrete proof criterion — something you can actually demonstrate, not just "the code compiles."
2. **Don't build ahead of a real problem.** Tools, MCP, approval gating, queues, multi-agent — none of it exists until the phase that actually needs it. Building it early means guessing at a shape you don't have real requirements for yet.
3. **The model never touches the database directly.** This holds in every phase. The LLM proposes; your application code executes.
4. **When you deviate from this doc, write the ADR.** The doc is allowed to be wrong. Silent deviation is what makes a codebase and its documentation drift apart.

---

# PHASE 1 — RAG Foundation

**One-line goal:** a real user can create an org, invite teammates, create an agent, upload documents, and have a grounded conversation with that agent about those documents.

### In scope
- Auth, Organizations, Invitations
- Agent CRUD
- Knowledge: upload → extract → chunk → embed → retrieve
- Conversation + Message + a simple Run
- Deployment

### Explicitly NOT in Phase 1
- Tools / Tool Registry / MCP
- Skills
- Human approval / risk gating
- Queues, workers, async execution
- Evaluation, observability
- Any cross-agent behavior

If you find yourself building any of these while "just finishing Phase 1," stop — that's scope creep, and it's exactly the trap the original architecture notes called out repeatedly.

---

## Phase 1 schema

```
Organization
  id, name, created_at

User
  id, email, hashed_password, created_at

OrganizationMember
  id, organization_id, user_id, role (owner | admin | member)

Invitation
  id, organization_id, email, token, status (pending | accepted | expired), invited_by

Agent
  id, organization_id, name, instructions, model, created_at

KnowledgeSource
  id, organization_id, agent_id, type (pdf | markdown | text), source_uri, status

Document
  id, knowledge_source_id, raw_text, created_at

Chunk
  id, document_id, content, embedding (pgvector), metadata (JSON)

Conversation
  id, agent_id, user_id, created_at

Message
  id, conversation_id, role (user | assistant), content, created_at

Run
  id, conversation_id, message_id, status, started_at, finished_at
```

### The one deliberate schema decision worth remembering later

`KnowledgeSource` joins directly to `Agent` in Phase 1 — there is no `Skill` layer yet, even though Phase 2 will introduce Skills as the *only* path to knowledge and tools for an agent. This is intentional: Phase 1's job is proving RAG works, not building the final abstraction.

**Forward note for Phase 2:** when `Skill` ships, migrate this by giving every existing agent an implicit default Skill that wraps its current `KnowledgeSource` rows. Write the ADR for this migration when you get there — don't pre-build the Skill table now "just in case."

### Run state machine (Phase 1 — deliberately minimal)

```
PENDING → RUNNING → COMPLETED
                   → FAILED
```

No `WAITING_TOOL`, no `WAITING_APPROVAL` — those states don't exist until there's something to wait on (Phase 2). Adding them now would model a problem you don't have yet.

---

## Phase 1 build order

### Step 1 — Finish Auth + Org + Invite
*(Mostly scaffolded already, per current repo state.)*
- JWT issuing + `get_current_user` dependency
- Register / login endpoints
- `POST /organizations`, invite-by-email, accept-invite flow

**Proof:** create an org, invite a teammate by email, they accept the invite and can log in as a member of that org.

### Step 2 — Agent CRUD
- `POST /agents`, `GET /agents`, `GET /agents/{id}`
- Agent belongs to an org; only org members can manage it

**Proof:** create an agent via the API, list agents scoped correctly to the calling user's org (and *not* see another org's agents).

### Step 3 — Knowledge pipeline
- Upload endpoint → object storage
- Text extraction (start with plain text + PDF)
- Chunking strategy (pick one, document why in the ADR)
- Embedding + write to `pgvector`
- Retrieval: given a query, return top-K chunks by similarity

**Proof:** upload a real document, run a query against it directly (no LLM yet), and confirm the retrieved chunks are actually the relevant ones — check this by hand before trusting it.

### Step 4 — Conversation + Message + Run (retrieve + generate, no tool branch)
- `Conversation` created per agent+user
- On a new `Message`: retrieve relevant chunks → build context → call LLM → stream response → persist `Message` + `Run`
- Return sources alongside the answer

**Proof:** a full chat turn, streamed to the client, grounded in the uploaded document, with the source chunk(s) shown alongside the answer.

### Step 5 — Deploy
- Docker Compose (already started) → a real deployable environment
- Basic error handling and logging (not full observability — that's Phase 2/Month 2 territory)

**Proof:** someone outside your own machine can create an org, invite a teammate, create an agent, upload a doc, and chat with it — end to end, over the network.

---

# PHASE 2 — Agency & Integration

**One-line goal:** agents stop being read-only. They can be given specific, reusable capabilities (Skills), act through tools — including tools proxied through MCP servers and real external systems (email, Jira, Slack) — with risk-gated approval for anything consequential.

### In scope
- Skill (capability bundle: instructions + scoped tools + scoped knowledge)
- Tool Registry (local tools + MCP-backed tools)
- MCP integration
- External integrations: email, Jira, Slack
- Risk-gated human approval
- Run state machine expansion

### Explicitly NOT in Phase 2
- Cross-agent interaction
- Cross-knowledge interaction (an agent reading another agent's knowledge scope)
- Any orchestration layer above a single agent

---

## Phase 2 schema additions

```
Skill
  id, organization_id, name, description, instructions

AgentSkill (join)
  agent_id, skill_id

SkillTool (join)
  skill_id, tool_id

SkillKnowledgeSource (join)
  skill_id, knowledge_source_id      -- replaces the direct Agent↔KnowledgeSource join

Tool
  id, organization_id, name, description
  source_type: enum(local, mcp)
  mcp_connection_id: nullable FK (required if source_type = mcp)
  local_handler_ref: nullable str (required if source_type = local)
  risk_level: enum(low, medium, high)
  input_schema: JSON

MCPConnection
  id, organization_id, name, server_url, auth_config

Integration
  id, organization_id, type (email | jira | slack), config, connected_by
```

### Migration note (do this first, deliberately, with an ADR)
Every existing Phase-1 agent gets a default `Skill` created for it, wrapping its current `KnowledgeSource` rows via `SkillKnowledgeSource`. After this migration, `Agent` no longer reads knowledge directly — it only sees what its Skills grant it. This is the one place Phase 2 has to touch Phase 1 data, so do it as its own reviewed step, not buried inside a feature PR.

### Tool execution boundary (unchanged principle, now with two backends)
```
LLM → Tool Request → Tool Registry → Authorization → Risk Check
                                                          │
                              ┌───────────────────────────┘
                              ▼
                  local_handler_ref?  → call the Python function directly
                  mcp_connection_id?  → proxy the call through the MCP client
                              │
                              ▼
                          Result → LLM continues
```
The LLM never knows or cares which backend served the tool call. That indirection is the point — it's what lets you add Jira/Slack/email later as MCP servers or local integrations without changing the agent's reasoning loop at all.

### Risk tiers
| Tier | Examples | Behavior |
|---|---|---|
| Low | `search_knowledge`, `get_customer`, read-only Slack lookups | Executes automatically |
| Medium | `create_ticket`, `update_customer` | Configurable per org |
| High | `send_email`, Jira issue creation/deletion, anything financial | Requires human approval |

### Run state machine (Phase 2)
```
PENDING → RUNNING → WAITING_TOOL → RUNNING → WAITING_APPROVAL → RUNNING → COMPLETED
                                                                          → FAILED → RETRYING → RUNNING
                                                                                   → DEAD
```

---

## Phase 2 build order (suggested — revisit once Phase 1 is actually done)

1. Skill model + joins + the Phase 1→2 migration ADR
2. Tool model (local only first) + executor boundary + risk tiers, no approval flow yet
3. Approval flow: `PENDING_APPROVAL` state, approve/reject endpoint
4. MCP client integration — one real MCP server connected, one MCP-backed tool working end to end
5. External integrations: pick one (Slack is usually the fastest real integration to stand up), then email, then Jira
6. Run state machine fully wired with the new states

Each of these should get its own proof criterion when you actually start Phase 2 — don't lock them in speculatively now, define "done" for each step when you have real code in front of you.

---

# PHASE 3 — Cross-Agent & Cross-Knowledge Interaction

**One-line goal:** multiple agents collaborate on a task, and knowledge scopes can be deliberately shared or crossed between agents when that's the right design — not by default.

This phase is intentionally left less specified than Phase 1 and 2. Designing multi-agent orchestration before you've built and lived with a single working agent is exactly the mistake the original architecture notes warned against ("no multi-agent swarm... start with a capable single agent"). Phase 3 should be scoped for real once Phase 2 is done and you know what limitations of a single agent are actually motivating it.

### Open questions to resolve *when you get here*, not now
- Is cross-agent interaction agent-to-agent messages, or always mediated through an orchestrator agent?
- Does "cross-knowledge interaction" mean an org-wide knowledge scope agents can opt into, or explicit grants between specific agents?
- Does a multi-agent `Run` need its own entity (a `RunGroup` or similar), or does the existing `Run` model extend to represent a sub-run spawned by another agent?
- What's the blast-radius/approval story when one agent's action can trigger another agent's tool call?

### What's safe to assume now
- Whatever the shape, it builds *on top of* the Phase 2 Tool/Skill/Run model, not around it. Don't design Phase 3 in a way that requires reworking Phase 1/2 entities — if that seems necessary, that's a signal Phase 2 needs revisiting first, not that Phase 3 needs to route around it.

---

## Schema evolution at a glance

| Entity | Phase 1 | Phase 2 | Phase 3 |
|---|---|---|---|
| Organization, User, Member, Invitation | ✅ Core | — | — |
| Agent | ✅ Core | Gains Skills | Gains cross-agent links (TBD) |
| KnowledgeSource | Direct → Agent | Direct → Skill | Possible shared/org-wide scope (TBD) |
| Skill | — | ✅ Core | Possibly shared across agents (TBD) |
| Tool | — | ✅ Core (local + MCP) | — |
| MCPConnection | — | ✅ Core | — |
| Integration | — | ✅ Core | — |
| Run | Minimal state machine | Full state machine (tool/approval) | Possible multi-agent extension (TBD) |

---

## What you should be able to explain at the end of each phase

**End of Phase 1:** Why does knowledge join directly to Agent right now, and what has to change when Skills arrive? Why is the Run state machine this simple, and what would break if you tried to add tool-calling without expanding it?

**End of Phase 2:** Why does the LLM never see whether a tool is local or MCP-backed? Why do risk tiers exist as data on the `Tool`, not as an `if` statement in the executor? What happens to a Run if a high-risk tool call is rejected instead of approved?

**End of Phase 3:** Why did you choose the specific multi-agent shape you chose? What would happen if two agents' knowledge scopes conflicted? What's the blast radius if one agent's action cascades into three more agent runs?

If you can answer these from the system you actually built, that's the real deliverable — not the feature list.
