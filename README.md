# 🏛️ Legacy System Archaeologist

An autonomous multi-agent system that explores an undocumented legacy codebase, reconstructs how it actually works, traces dependencies, and answers investigation/impact questions — with every claim backed by cited evidence from code, database, configuration, and (later) logs and Git history.

Think **Google Maps for a 15-year-old enterprise application**. Ask it *"what happens when an order is cancelled?"* or *"what breaks if I delete this class?"* and it investigates the codebase the way a senior engineer would, then shows its evidence — not just an answer.

This is not a code generator. The problem being solved is **recovering knowledge that already exists implicitly inside a large, poorly documented system**.

> **Note:** This is a personal learning project, not a startup idea or product pitch. The goal is to genuinely understand how agentic AI systems work under the hood — tool-calling, memory, planning, multi-agent coordination — by building the mechanics by hand before reaching for any framework, and to have something real to show and explain in interviews. It is not intended to be commercialized.

---

## Why this project

Legacy Java/Spring backend systems are rarely fully documented, and tribal knowledge disappears when engineers leave. Existing "AI code assistant" tools tend to either assume a fully modern, fully annotated Spring/JPA stack, or hallucinate confident-sounding answers with no way to verify them.

This project is built around one hard rule instead: **no claim without cited evidence** — and, going further, **no claim trusted just because it cites evidence**. Two early investigations in this project's own build log (see `NOTES` / dev log) produced claims that cited real file/line evidence but told a *wrong* story about what that evidence meant. Catching that gap — not just requiring citations, but questioning whether the citations actually support the claim — is the core problem this project exists to solve.

## Framework-agnostic by design

The legacy codebase being analyzed may run Spring Boot with JPA, or it may be raw servlets with inline JDBC `Statement` calls, or MyBatis/iBatis XML mappers, or any mix of these. Tools are built against **ground truth first**, never against framework assumptions:

- **Code search** — plain substring/grep-style search (via `ripgrep`), not annotation-dependent
- **Call references** — AST-level parsing (via `tree-sitter`), works on any class whether or not it's a `@Service`
- **SQL detection** *(planned)* — resolves `@Query` annotations, inline JDBC string literals, and XML mapper files to the same evidence shape

Framework annotations (`@Repository`, `@Entity`, `@Query`) are treated as optional bonus signals a tool *can* use if present — never as something a tool assumes exists. A tree-sitter grammar parses `@Service` as a generic `annotation` node, structurally no different from any other annotation — so there's no way for these tools to accidentally depend on framework metadata.

## Multi-agent design (why each agent exists)

Not `Research Agent → Writer Agent → Summary Agent` for its own sake — each agent exists because the underlying problem genuinely requires a different source of evidence:

| Agent | Evidence source |
|---|---|
| **Code Archaeologist** | Source code — call graphs, class hierarchy, AST search |
| **DB Archaeologist** *(planned)* | Schema, relationships, triggers, stored procedures |
| **API Archaeologist** *(later)* | REST/SOAP/Kafka/webhooks/scheduled jobs |
| **Config Archaeologist** *(later)* | Properties/YAML/env vars/K8s secrets |
| **Git Historian** *(later)* | Not just what the code does, but *why* — commit history, related issues |
| **Log Archaeologist** *(later)* | Actual runtime behavior vs. static code behavior |
| **Critic** | Challenges other agents' claims, demands evidence — and checks that cited evidence actually supports the claim being made |
| **Verifier** *(later)* | Claim → evidence → cross-check → confidence level |

## Current status

Built with a **hand-rolled agent runtime first** — no LangChain/LangGraph/MCP yet — so the underlying mechanics (tool-calling protocol, planning loop, memory, guardrails, multi-agent coordination, evidence-based verification) are actually understood before any framework is introduced.

**Working today (single-agent):**
- Raw HTTP calls to an LLM API (Gemini), no SDK
- Structured JSON output enforcement + validation (`claim` / `evidence` / `confidence` schema)
- `search_codebase(keyword)` — ripgrep-based text search tool
- A hand-rolled ReAct loop (goal → tool call → observation → repeat, capped iterations) using native function-calling
- `get_call_references(method_name)` — tree-sitter AST-based call-site search, precise where text search is ambiguous
- Short-term memory: an explicit, role-tagged scratchpad (`action`/`observation` per iteration) — evaluated against relying on the provider's own session state, currently using session-based memory for reliability
- Long-term memory: a flat vector store of past investigation claims, with hand-written cosine similarity retrieval

**Not yet built:**
- Investigation planning / task decomposition
- DB Archaeologist and SQL-detection tooling
- Self-correction / retry on malformed tool calls
- The citation guardrail (reject claims with no evidence) and the Critic pass
- Multi-agent message bus and turn-taking
- Structured evidence graph output

See the project's Notion dev log for the day-by-day build history, including the false starts and what each one taught.

## Roadmap / future scope

Beyond the two-agent (Code + DB) evidence loop planned for the initial build:

- **API / Config / Git / Log Archaeologists** — broaden evidence sources beyond static code
- **Confidence-calibrated evidence graph with contradiction detection** — rather than a single "verified" checkmark per claim, explicitly surface when two claims (from different agents, or the same agent across investigations) *disagree*, instead of silently picking one
- **Impact ("blast radius") analysis as a dependency graph**, not prose — "what breaks if I delete this" rendered as a subgraph with a per-node confidence/severity score
- **Static-vs-actual drift detection** — a dedicated report comparing what the code says happens against what git history and runtime logs show actually happens, since that gap is exactly what static analysis alone can never catch
- **Cost/confidence dashboard** — token cost and tool-call count per investigation, alongside the resulting claim's confidence, to make the system's own resource use visible rather than hidden
- A human-approval gate before any write/destructive action (the system starts, and stays, strictly read-only)

## Tech stack

- Python (no agent framework — hand-rolled tool-calling, ReAct loop, memory)
- Gemini API via raw HTTP (`requests`) — no SDK
- `ripgrep` for text search
- `tree-sitter` + `tree-sitter-java` for AST-level Java parsing
- `numpy` for vector math (hand-written cosine similarity)

## Fixture repo

Tools are developed and tested against a small, deliberately messy Java fixture repository (`fixture-repo/`) that intentionally mixes three coding styles in one codebase, to force framework-agnostic behavior:
- A Spring Boot–style service (`@Service`, `@Autowired`)
- A raw servlet with zero annotations
- A DAO class mixing inline JDBC `Statement` (string-concatenated SQL) and `PreparedStatement`

---

*This project pivoted from an earlier idea, "The Coach" (a competitive-programming coach) — dropped in favor of a project that plays directly to real Java/Spring/legacy-systems backend depth instead of a side interest.*
