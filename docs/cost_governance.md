# 🛡️ Deterministic Token Estimation & AI Cost Governance Architecture

> **Status**: Active Architecture Standard (Updated for Gemini 4 Argon Plan Changes)  
> **Scope**: Zero-Cost Local-First Execution, LLM Token Estimation, Thinking Token Overrun Prevention & Financial Safeguards  
> **Authoritative References**: [`CLAUDE.md`](../CLAUDE.md), [`GEMINI.md`](../GEMINI.md), [`README.md`](../README.md), [`docs/architecture.md`](architecture.md)

---

## 1. Executive Summary & The Gemini 4 Argon Billing Reality

Historically, early Physics Lab documentation assumed that Google AI Studio keys (`GEMINI_FREE_API_KEY` / `GEMINI_API_KEY`) operated on an unbillable `$0.00` free tier. **Since the upgrade to Gemini 4 Argon, Google AI Studio / Gemini API plans have changed**: external API calls against `generativelanguage.googleapis.com` can incur metered token charges, and relying on an assumed "$0.00 free tier" is a critical financial vulnerability.

Furthermore, during batch runs or live runtime calls against cloud LLM providers, unintended cost overruns occur due to four compound factors:
1. **Unnecessary External API Calls for Local-Solvable Tasks**: Firing cloud LLM calls for tasks that can be solved deterministically in local Python/SymPy or directly in-session by the active Antigravity coding agent.
2. **Uncached Runtime Embedding Calls**: Firing synchronous `embedContent` HTTP calls on every user search query without a persistent local query-vector cache.
3. **Dynamic Reasoning / Thinking Tokens**: Reasoning models generate internal thinking tokens (`thoughts_token_count`) billed at premium output rates (up to 10× input rates) when `thinking_budget` is uncapped.
4. **Reactive Post-Facto Circuit Breakers**: Cost checks executed *after* API responses arrive across concurrent worker threads allow in-flight batches to accumulate debt.

This document establishes a **permanent, deterministic 6-pillar architectural framework** that prioritizes **$0.00 local/in-session execution first** and enforces strict pre-dispatch gates whenever external API calls are explicitly authorized.

---

## 2. The Core Failure Modes of Traditional Token Estimation

```
Traditional (Broken) Model:
[Task Identified] ──> [Call External Gemini API Directly] ──> [Guess Token Size] ──> [Surprise Metered Bill]
                                                                                          ▲
                   Assumed "$0.00 Free Tier" + Hidden Thinking Tokens + Uncached Queries ─┘
```

### A. The Myth of the "$0.00 API Key" Under Gemini 4 Argon
Under Gemini 4 Argon plan structures, API keys attached to cloud projects or upgraded studio tiers are metered per 1M input/output tokens. Treating `GEMINI_FREE_API_KEY` or `GEMINI_API_KEY` as "physically incapable of incurring debt" leads developers to run un-gated loops (`gqs.py seed`, `generate_gemini_formula.py`, or 25-worker async scripts) without pre-flight cost checks.

### B. The Thinking Token "Black Box"
Modern reasoning engines produce an unpredictable volume of internal thinking tokens before emitting visible JSON:
* A simple definition might generate **200 thinking tokens**.
* A complex tensor Lagrangian might trigger **4,000+ thinking tokens**.
* Internal reasoning tokens are billed as **output tokens** (costing up to 10× more than input tokens).

### C. Uncached Live Runtime Vector Queries
Calling `generativelanguage.googleapis.com/v1beta/models/gemini-embedding-001:embedContent` on every user search request in [`SemanticSearchService::embedQuery()`](../app/logic/SemanticSearchService.php) without persistent disk caching repeatedly bills identical or common search terms.

---

## 3. The 6-Pillar Deterministic Cost Governance Framework

```
                     [Enrichment / Audit / Search Task Triggered]
                                        │
                                        ▼
  Pillar 0: Local-First & In-Session Gate ──> Can Local SymPy / AST / Active Agent solve it?
                                        │         ├── YES ──> Execute Locally ($0.00 External API Cost)
                                        │         ▼ NO (Requires --allow-external-api)
  Pillar 1: Pre-Flight count_tokens()     ──> Exact Input Token Measurement Before Dispatch
                                        │
                                        ▼
  Pillar 2: Bounded Worst-Case Output Cap ──> max_output_tokens + thinking_budget = Hard Ceiling
                                        │
                                        ▼
  Pillar 3: Pre-Dispatch Budget Check     ──> (SessionSpend + WorstCaseCost > BudgetCap?) ──YES──> 🛑 ABORT
                                        │ NO
                                        ▼
  Pillar 4: Mandatory Canary & Confirmation > Display Exact Worst-Case $ Cost & Require Human [y/N]
                                        │
                                        ▼
  Pillar 5: Persistent Embedding Caching  ──> Normalize & Cache Query Vectors on Disk (Zero Repeat Calls)
```

---

### Pillar 0: Local-First & In-Session Agent Execution Mandate (Zero External API Calls)
**Rule**: Never invoke an external `google.genai` network API call when a task can be performed deterministically or in-session.

1. **In-Session Antigravity Agent First**:
   * When working interactively inside an Antigravity coding session, formula drafting, title curation, prose decorruption, and variable audits MUST be performed directly in-session using local Python scripts, cross-shard indexes, and the active coding agent's intelligence—incurring **zero external `google-genai` SDK calls**.
2. **Deterministic Local Engines**:
   * Symbolic algebra, dimensional homogeneity, Taylor expansions, and Legendre transformations MUST use the local sandboxed SymPy CAS engine ([`lib/cas/cas_engine.py`](../lib/cas/cas_engine.py)).
   * Derivation lineage discovery and DAG healing MUST use [`scripts/fixlineage`](../scripts/fixlineage) and [`scripts/maintenance/lineage_resolver.py`](../scripts/maintenance/lineage_resolver.py).
3. **Explicit CLI Opt-In Flag (`--allow-external-api`)**:
   * CLI maintenance tools (`gqs.py seed`, `gqs.py formula-auto-seed`, `scripts/maintenance/generate_gemini_formula.py`) MUST block external `google.genai` network calls by default unless `--allow-external-api` is explicitly passed on the command line.

---

### Pillar 1: Deterministic Pre-Flight Token Counting (`count_tokens`)
**Rule**: Never estimate or approximate input tokens when `--allow-external-api` is used.

Every external API runner must query `client.models.count_tokens()` before dispatching generative calls:

```python
# Exact deterministic measurement of input tokens before any billing event
input_tokens = client.models.count_tokens(
    model=MODEL_NAME,
    contents=[SYSTEM_PROMPT, prompt]
).total_tokens
```

---

### Pillar 2: Mathematically Bounded Worst-Case Output Caps
**Rule**: Never allow unconstrained generation or unbounded thinking budgets.

Every external generative request must enforce strict, immutable upper bounds on both completion tokens and thinking tokens:
```python
MAX_COMPLETION_TOKENS = 800
MAX_THINKING_TOKENS = 512

gen_config = types.GenerateContentConfig(
    temperature=0.1,
    response_mime_type='application/json',
    max_output_tokens=MAX_COMPLETION_TOKENS,
    thinking_config=types.ThinkingConfig(thinking_budget=MAX_THINKING_TOKENS)
)
```

#### The Worst-Case Cost (WCC) Formula:
$$\text{Max Output Tokens} = \text{max\_output\_tokens} + \text{thinking\_budget}$$
$$\text{WCC} = (\text{exact\_input\_tokens} \times \text{rate}_{\text{input}}) + (\text{Max Output Tokens} \times \text{rate}_{\text{output}})$$

Because both `exact_input_tokens` and `Max Output Tokens` are strictly bounded, the **maximum possible cost of the API call is known before the call is made**.

---

### Pillar 3: Pre-Dispatch Rejection (Guard Before Call, Not After)
**Rule**: Cost accounting must evaluate the ceiling *before* placing the network call, not after responses are received, and concurrency must default to `1` (sequential) unless a strict thread-locked budget ceiling is active.

```python
with budget_lock:
    projected_spend = current_session_spend + worst_case_cost
    if projected_spend > max_cost_dollars:
        circuit_breaker_event.set()
        raise RuntimeError(
            f"Pre-dispatch abort: Next request (${worst_case_cost:.4f}) would push spend "
            f"(${projected_spend:.4f}) over budget cap (${max_cost_dollars:.2f})."
        )
```

---

### Pillar 4: Mandatory Interactive Cost Confirmation & Canary Batch
**Rule**: Any external API script must print the exact pre-flight token count and estimated worst-case dollar cost and require explicit human `[y/N]` confirmation before firing network requests. Batch runs over 10 items require a 5-item canary calibration first:

```text
=======================================================
🔬 EXTERNAL API COST & CANARY PRE-FLIGHT REPORT
=======================================================
• Target Model:         gemini-flash-latest
• Items Queued:         5 formulas
• Measured Input Tokens: 1,850 tokens total
• Max Output + Thinking: 1,312 tokens / item (6,560 max)
• Worst-Case Batch Cost: $0.0042 USD
• Hard Budget Ceiling:   $0.5000 USD
=======================================================
Authorize external metered API execution? [y/N]: 
```

---

### Pillar 5: Persistent Query Embedding Caching (`SemanticSearchService.php`)
**Rule**: Runtime user search queries must never trigger redundant external `embedContent` API calls.

1. **Normalized Query Disk Cache**:
   * [`SemanticSearchService::embedQuery()`](../app/logic/SemanticSearchService.php) normalizes the search string (`strtolower(trim(preg_replace('/\s+/', ' ', $text)))`), hashes it with SHA-256, and checks the persistent local cache (`public/cache/embeddings_query_cache.json`) before making any network request.
2. **Offline / Zero-API Search Fallback**:
   * If `DISABLE_EXTERNAL_EMBEDDING_API=1` is set in `.env` (or if no API key is configured), `SemanticSearchService` automatically falls back to local lexical + reverse-LaTeX trie search at **$0.00 runtime cost**.
