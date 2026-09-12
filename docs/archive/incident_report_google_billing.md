# Formal Technical Incident Report & Billing Adjustment Request

**Target Project:** `gen-lang-client-0170965498`  
**Billing Account:** `0168ED-AC9826-9985C0`  
**Service Affected:** Google Cloud Vertex AI / Gemini API  
**Date of Incident:** August 2026  
**Subject:** Request for One-Time Courtesy Credit Replenishment / Billing Adjustment Due to AI Automation Estimation Error  

---

## 1. Executive Summary

This document serves as a formal incident report and billing appeal regarding unintended API consumption on Google Cloud Project `gen-lang-client-0170965498`. 

During the development of an open-source physics encyclopedia and knowledge graph (`terra`), an automated AI coding assistant provided inaccurate pricing estimates and failed to account for multi-token candidate grounding overhead when executing batch processing against the Vertex AI Gemini API. As a result, an automated batch process ran unmonitored overnight, unintentionally exhausting the account's promotional credits and drawing against prepaid funds.

All root-cause vulnerabilities have since been identified, fixed, and permanently safeguarded with hard client-side circuit breakers. We respectfully request a **one-time billing adjustment or replenishment of the exhausted promotional credits**.

---

## 2. Technical Root Cause Analysis (RCA)

A thorough post-incident audit revealed three distinct technical factors that led to the unexpected token surge:

1. **Context Window Grounding Payload Underestimation**:
   * The AI assistant estimated processing costs based strictly on the visible output text (~50 tokens per formula).
   * In practice, each batch request injected a top-25 candidate grounding pool of related equations into the prompt to ensure mathematical rigor, increasing input context size to **2,000–2,500 tokens per request**.
   * Under `gemini-2.5-pro` Vertex AI pricing ($1.25 / 1M input, $5.00 / 1M output), the actual cost per request was approximately 10× higher than the assistant's projected estimate.

2. **Unaccounted Hybrid Reasoning Tokens (`thoughts_token_count`)**:
   * In newer reasoning models (e.g., `gemini-3.7-flash`), Google's inference engine generates hundreds to thousands of internal reasoning tokens (`thoughts_token_count`).
   * The client script was initially configured to tally only visible completion tokens (`candidates_token_count`), concealing the true token volume billed by the Google Cloud backend.

3. **Absence of Client-Side Dollar Circuit Breakers**:
   * The initial batch runner lacked a hard cumulative dollar kill switch. When the process was left running in the background, it continued processing requests without halting at the intended budget threshold.

---

## 3. Permanent Corrective Actions & Safeguards Implemented

To guarantee that an unintended API surge can never occur again, the following safeguards have been engineered into the codebase:

| Safeguard | Implementation Details | Status |
| :--- | :--- | :---: |
| **Hard Dollar Circuit Breaker** | Thread-safe atomic spend tracker (`--max-cost-dollars`) that immediately kills all workers the exact moment spend hits the ceiling. | ✅ **Active** |
| **Full-Spectrum Token Accounting** | Captures 100% of billable token metadata from `response.usage_metadata`, including `prompt_token_count`, `candidates_token_count`, and `thoughts_token_count`. | ✅ **Active** |
| **Strict Request Ceilings** | Hard formula processing limit (`--limit N`) enforcing an absolute upper bound on total API calls per execution. | ✅ **Active** |
| **Live Telemetry & Budget Meter** | Real-time CLI dashboard displaying live dollar spend, cost per request, and remaining budget margin. | ✅ **Active** |

---

## 4. Formal Request for Billing Consideration

The usage occurred purely during non-commercial development and testing of an educational scientific platform due to automated assistant misconfiguration, rather than production commercial traffic.

We respectfully request that Google Cloud Billing Support consider:
1. A **one-time courtesy credit adjustment** or replenishment of the promotional/trial credits consumed by the Vertex AI API surge.
2. An account review under Google Cloud's developer courtesy exemption policy for unintended API spikes.

---

**Prepared on behalf of Account Holder:**  
*Project ID:* `gen-lang-client-0170965498`  
*Billing Account ID:* `0168ED-AC9826-9985C0`  
*Repository:* [Physics Lab / Terra Encyclopedia](https://github.com/jholobetz/terra)
