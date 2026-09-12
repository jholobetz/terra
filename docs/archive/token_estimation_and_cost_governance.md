# 🛡️ Deterministic Token Estimation & AI Cost Governance Architecture

> **Document Status**: Active Architecture Standard  
> **Topic**: Solving LLM Token Estimation Errors, Thinking Token Overruns, and Financial Safeguards  
> **Applies to**: All AI batch pipelines, formula enrichment engines, and interactive drafting endpoints in Terra Physics Lab.

---

## 1. Executive Summary & Problem Definition

In modern LLM application development, relying on traditional heuristic estimations (such as `word_count / 4` or assumed static response sizes) leads to severe financial and operational failures. 

During early batch runs against Vertex AI on Google Cloud, an unintended overrun occurred due to three compound factors:
1. **Dynamic Grounding Context Inflation**: Injecting candidate formulas into prompts multiplied input payload sizes from ~100 tokens to 2,000–2,500 tokens per equation.
2. **Dynamic Reasoning / Thinking Tokens**: Newer Gemini models generate internal thinking tokens (`thoughts_token_count`) that were unmonitored by early client scripts and billed at premium output rates.
3. **Reactive Post-Facto Circuit Breakers**: Cost checks were executed *after* API responses arrived across concurrent worker threads, allowing in-flight batches to accumulate debt.

This document establishes a **permanent, deterministic 5-pillar architectural framework** that eliminates estimation error and makes unauthorized billing overruns mathematically impossible.

---

## 2. The Core Failure Modes of Traditional Token Estimation

```
Traditional (Broken) Model:
[Prompt Drafted] ──> [Guess Token Size (~500)] ──> [Dispatch Batch] ──> [Surprise 10x Bill]
                                                                              ▲
                                  Hidden Reasoning Tokens + Grounding Injections ─┘
```

### A. The Thinking Token "Black Box"
Modern reasoning engines (Gemini 2.5/3.7 with `ThinkingConfig`, OpenAI o-series, Claude 3.7 Extended Thinking) produce an unpredictable volume of internal thinking tokens before emitting visible JSON:
* A simple definition might generate **200 thinking tokens**.
* A complex tensor Lagrangian might trigger **4,000 thinking tokens**.
* Internal reasoning tokens are billed as **output tokens** (costing up to 10× more than input tokens).

### B. Dynamic Grounding & Context Expansion
When retrieval-augmented generation (RAG) or candidate pooling is injected into prompts:
* The input prompt size varies drastically based on the retrieved neighbors.
* Without measuring the exact combined string prior to sending, token estimation is blind.

### C. Asymmetric Pricing Tier Multipliers
* **Flash Models**: ~$0.075 / 1M input, ~$0.30 / 1M output.
* **Pro Models**: ~$1.25 / 1M input, ~$5.00 / 1M output.
* A fallback misconfiguration or model mismatch produces a **16× price jump**, turning a minor calculation discrepancy into a significant financial spike.

---

## 3. The 5-Pillar Deterministic Solution Framework

```
                       [Candidate Prompt & Context Built]
                                       │
                                       ▼
    Pillar 1: Pre-Flight count_tokens() ───────> Exact Input Token Count ($0.00 Cost)
                                       │
                                       ▼
    Pillar 2: Bounded Worst-Case Cap    ───────> max_output + thinking_budget = Output Ceiling
                                       │
                                       ▼
    Pillar 3: Pre-Dispatch Budget Check ───────> (Current + WorstCase > Cap?) ──YES──> 🛑 ABORT
                                       │ NO
                                       ▼
    Pillar 4: Mandatory Canary Batch    ───────> Run 5 Items First & Require Human "y" Approval
                                       │
                                       ▼
    Pillar 5: Zero-Debt Payment Shield  ───────> Free Tier Key ($0.00) / Prepaid Wallet Only
```

---

### Pillar 1: Deterministic Pre-Flight Token Counting (`count_tokens`)
**Rule**: Never estimate or approximate input tokens.

Google’s GenAI SDK provides a free, zero-cost token counting endpoint. Every batch runner must query `count_tokens` before dispatching generative calls:

```python
# Exact deterministic measurement of input tokens before any billing event
input_tokens = client.models.count_tokens(
    contents=[SYSTEM_PROMPT, prompt]
).total_tokens
```

---

### Pillar 2: Mathematically Bounded Worst-Case Output Caps
**Rule**: Never allow unconstrained generation or unbounded thinking budgets.

Every batch request must enforce strict, immutable upper bounds:
```python
MAX_COMPLETION_TOKENS = 800
MAX_THINKING_TOKENS = 512

gen_config = {
    'temperature': 0.1,
    'response_mime_type': 'application/json',
    'max_output_tokens': MAX_COMPLETION_TOKENS,
    'thinking_config': types.ThinkingConfig(thinking_budget=MAX_THINKING_TOKENS)
}
```

#### The Worst-Case Cost (WCC) Formula:
$$\text{Max Output Tokens} = \text{max\_output\_tokens} + \text{thinking\_budget}$$
$$\text{WCC} = (\text{exact\_input\_tokens} \times \text{rate}_{\text{input}}) + (\text{Max Output Tokens} \times \text{rate}_{\text{output}})$$

Because both `exact_input_tokens` and `Max Output Tokens` are strictly bounded, the **maximum possible cost of the API call is known to the exact penny before the call is made**.

---

### Pillar 3: Pre-Dispatch Rejection (Guard Before Call, Not After)
**Rule**: Cost accounting must evaluate the ceiling *before* placing the network call, not after responses are received.

```python
with budget_lock:
    projected_spend = current_session_spend + worst_case_cost
    if max_cost_dollars > 0 and projected_spend > max_cost_dollars:
        circuit_breaker_event.set()
        raise BudgetExceededException(
            f"Pre-dispatch abort: Next request (${worst_case_cost:.4f}) would push spend "
            f"(${projected_spend:.4f}) over budget cap (${max_cost_dollars:.2f})."
        )
```

---

### Pillar 4: Mandatory "Canary Batch" with User Approval
**Rule**: Batch runs over 10 items require a mandatory 5-item pilot calibration.

1. **Step 1**: Execute exactly 5 items.
2. **Step 2**: Calculate empirical statistics:
   * Median & 95th-percentile input tokens.
   * Median & 95th-percentile thinking tokens.
   * Actual average cost per item.
3. **Step 3**: Display explicit telemetry and block execution for human confirmation:
   ```text
   =======================================================
   🔬 CANARY BATCH CALIBRATION REPORT (5 formulas)
   =======================================================
   • Avg Input Tokens:     2,140
   • Avg Thinking Tokens:    480
   • Avg Output Tokens:      510
   • Avg Cost Per Formula: $0.00062 USD
   -------------------------------------------------------
   Estimated Cost for Full Batch (1,250 formulas): $0.78 USD
   Hard Budget Ceiling Enforced:                  $1.50 USD
   =======================================================
   Proceed with full execution? [y/N]: 
   ```

---

### Pillar 5: Zero-Debt Payment Architecture (The Physical Airgap)
**Rule**: Code-level safeguards are secondary to structural account isolation.

1. **Local Development & Interactive Drafting**:
   * Use **Google AI Studio Pure Free Tier (`GEMINI_FREE_API_KEY`)**.
   * Has no credit card or billing account attached.
   * Hard-locked to **$0.00**. Exhaustion results in HTTP 429 quota pause, never financial charges.
2. **Production / High-Throughput Batch Compute**:
   * If paid infrastructure is required, use a **prepaid card or pre-funded GCP balance** ($10–$25 maximum).
   * Do not attach open-ended post-paid corporate or personal credit cards to autonomous AI developer projects.

---

## 4. Implementation Checklist for New Scripts

Before any new AI script or batch runner is approved for execution in Terra:
- [ ] Uses `count_tokens` for pre-flight input sizing.
- [ ] Explicitly sets both `max_output_tokens` and `thinking_budget`.
- [ ] Enforces a mandatory, non-zero default budget limit (e.g., `--max-cost-dollars` defaults to $1.00, never 0.0).
- [ ] Evaluates budget *prior* to dispatching concurrent threads.
- [ ] Includes a canary calibration step for batches > 10 items.
- [ ] Defaults to `provider="free"` (Google AI Studio Free Tier).

---

*Authored for Terra Physics Lab Architecture Documentation — September 2026*
