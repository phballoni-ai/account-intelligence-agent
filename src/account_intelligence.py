"""Offline, source-grounded B2B account brief generator (Python 3.10+)."""
import argparse
import json
from datetime import date
from pathlib import Path
from urllib.parse import urlsplit

KINDS = {"growth", "operations", "product", "financial", "other"}
PROMPTS = {
    "Operations": ("operations", "Would it be useful to compare how your team handles operational workflows today?"),
    "Sales": ("growth", "How is the team thinking about scaling its commercial process alongside this expansion?"),
    "Finance": ("financial", "How are you evaluating the financial trade-offs behind this initiative?"),
}


def _clean(value, name):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty string")
    return " ".join(value.split())


def validate(data):
    if not isinstance(data, dict):
        raise ValueError("Input must be a JSON object")
    company = _clean(data.get("company"), "company")
    domain = _clean(data.get("domain"), "domain")
    industry = _clean(data.get("industry"), "industry")
    size = data.get("employee_count")
    if type(size) is not int or size < 0:
        raise ValueError("employee_count must be a non-negative integer")
    industries = data.get("target_industries")
    if not isinstance(industries, list) or not all(isinstance(x, str) for x in industries):
        raise ValueError("target_industries must be a string list")
    span = data.get("employee_range")
    if (not isinstance(span, list) or len(span) != 2 or
            any(type(x) is not int or x < 0 for x in span) or span[0] > span[1]):
        raise ValueError("employee_range must be [minimum, maximum]")
    rows = data.get("evidence")
    if not isinstance(rows, list) or not rows:
        raise ValueError("At least one sourced evidence item is required")
    evidence = []
    for index, row in enumerate(rows, 1):
        if not isinstance(row, dict):
            raise ValueError(f"Evidence {index} must be an object")
        claim = _clean(row.get("claim"), f"evidence {index} claim")
        excerpt = _clean(row.get("excerpt"), f"evidence {index} excerpt")
        url = _clean(row.get("url"), f"evidence {index} url")
        parts = urlsplit(url)
        if parts.scheme != "https" or not parts.netloc or parts.username or parts.password:
            raise ValueError(f"Evidence {index} needs a public HTTPS source URL")
        kind = row.get("kind")
        if kind not in KINDS:
            raise ValueError(f"Evidence {index} has invalid kind")
        when = _clean(row.get("observed_on"), f"evidence {index} observed_on")
        try:
            date.fromisoformat(when)
        except ValueError as exc:
            raise ValueError(f"Evidence {index} observed_on must be YYYY-MM-DD") from exc
        evidence.append(dict(claim=claim, excerpt=excerpt, url=url, kind=kind, observed_on=when))
    return dict(company=company, domain=domain, industry=industry,
                employee_count=size, target_industries=industries,
                employee_range=span, evidence=evidence)


def fit_score(data):
    kinds = {row["kind"] for row in data["evidence"]}
    checks = [
        ("Target industry", 35, data["industry"].casefold() in
         {item.casefold() for item in data["target_industries"]}),
        ("Target headcount range", 25, data["employee_range"][0] <=
         data["employee_count"] <= data["employee_range"][1]),
        ("Growth signal provided", 20, "growth" in kinds),
        ("Operations signal provided", 20, "operations" in kinds),
    ]
    return sum(points for _, points, matched in checks if matched), checks


def _md(value):
    """Treat all submitted fields as plain text, not Markdown commands."""
    for symbol in ("\\", "`", "[", "]", "*", "_", "<", ">", "|", "!"):
        value = value.replace(symbol, "\\" + symbol)
    return value


def build_brief(data):
    data = validate(data)
    score, checks = fit_score(data)
    lines = [f"# {_md(data['company'])} — account briefing", "",
             "**Offline portfolio demo. Human review required before use.**", "",
             f"- Domain (user supplied): {_md(data['domain'])}",
             f"- Industry (user supplied): {_md(data['industry'])}",
             f"- Employees (user supplied): {data['employee_count']}", "",
             "## Source-backed notes", ""]
    for idx, row in enumerate(data["evidence"], 1):
        lines.extend([f"{idx}. **[{row['kind']}]** {_md(row['claim'])} [S{idx}]",
                      f"   - Supporting excerpt: “{_md(row['excerpt'])}”",
                      f"   - Source: {row['url']} (observed {row['observed_on']}; not fetched or verified by tool)"])
    lines += ["", f"## ICP fit: {score}/100", "",
              "Heuristic fit only; not a forecast of conversion or buying intent.", ""]
    for label, points, matched in checks:
        lines.append(f"- {label}: {'+' + str(points) if matched else '+0'} / {points}")
    lines += ["", "## Possible discovery questions (not verified pain points)", ""]
    kinds = {row["kind"] for row in data["evidence"]}
    for role, (kind, prompt) in PROMPTS.items():
        if kind in kinds:
            citation = next(i for i, row in enumerate(data["evidence"], 1) if row["kind"] == kind)
            lines.append(f"- **{role}** (inspired by [S{citation}]): {prompt}")
    if not any(kind in kinds for kind, _ in PROMPTS.values()):
        lines.append("- No category-specific question available; gather more evidence first.")
    lines += ["", "## Review checklist", "",
              "- Open each URL and check that the excerpt and claim match the original.",
              "- Re-check recency, relevance, permission to use, and target-person fit.",
              "- Do not send a message or present a suggested question as a proven problem.", ""]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Create an evidence-first account briefing from reviewed JSON")
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    try:
        data = json.loads(args.input.read_text(encoding="utf-8"))
        brief = build_brief(data)
        args.output.write_text(brief, encoding="utf-8")
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        parser.exit(2, f"Error: {exc}\n")
    print(f"Wrote brief to {args.output}")


if __name__ == "__main__":
    main()
