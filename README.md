# Account Intelligence Agent

An **evidence-first account research CLI** for B2B business development. Turn a small, reviewed collection of public-source excerpts into a one-page executive briefing with citations, an ICP fit score, and role-specific conversation starters.

> **Status: v0.1 offline MVP.** This project runs **100% plug-and-play locally** without consuming any API credits or external tokens. The included sample is fictional; no proprietary data is used.

## Quick Start (Plug-and-Play)

Clone the repository and run the interactive CLI demo right away:

```bash
git clone https://github.com/phballoni-ai/account-intelligence-agent.git
cd account-intelligence-agent

# Run the interactive demo (Zero config, runs immediately)
python demo.py
```

Or run the pipeline directly on custom inputs:

```bash
python -m src.account_intelligence --input examples/fictional_account.json --output brief.md
python -m unittest discover -s tests -v
```

## Why this matters

A BDR needs a usable account brief, not a list of unsourced AI guesses. This prototype only reports claims provided with a source URL and verbatim supporting excerpt. It separates verified input from a suggested angle and leaves the final decision to a human.

```mermaid
flowchart LR
  A[Reviewed evidence JSON] --> B[Input validation]
  B --> C[Deterministic ICP fit score]
  C --> D[Markdown executive brief]
  D --> E[Human review before outreach]
```

## Input contract

```json
{
  "company": "Example Company",
  "domain": "example.com",
  "industry": "B2B software",
  "employee_count": 120,
  "target_industries": ["B2B software"],
  "employee_range": [50, 500],
  "evidence": [
    {
      "claim": "Company announced an expansion",
      "excerpt": "Exact short quotation from the source",
      "url": "https://example.com/news",
      "kind": "growth",
      "observed_on": "2026-10-01"
    }
  ]
}
```

`kind` must be one of `growth`, `operations`, `product`, `financial`, or `other`. Input text is untrusted; the program renders it as data, not as instructions. If evidence is empty the program refuses to produce a brief. A URL is an attribution label; the tool **does not fetch or verify the destination**. Always manually check source accuracy and recency.

## Scoring (transparent heuristic, not a prediction)

- Industry in target list: +35
- Employee count in target range: +25
- Growth evidence present: +20
- Operations evidence present: +20

The result is a transparent **fit score (0–100)**, not a lead-conversion estimate. Conversation starters are generic prompts based on evidenced categories, not assertions that the company has a particular pain point. No invented contact names, savings figures, or performance claims.

## Privacy and Security

Never commit customer lists, private data, credentials, or confidential documents. This demo runs offline, makes no external network requests, and sends no messages.
