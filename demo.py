#!/usr/bin/env python3
"""
Account Intelligence Agent - Interactive CLI Demo
Plug-and-play interactive terminal demonstration.
Requires zero external API keys and runs purely on Python standard library.
"""

import json
import sys
import time
from pathlib import Path

from src.account_intelligence import build_brief, fit_score, validate

SAMPLE_PATH = Path(__file__).parent / "examples" / "fictional_account.json"

# ANSI Terminal Colors
BOLD = "\033[1m"
GREEN = "\033[92m"
BLUE = "\033[94m"
CYAN = "\033[96m"
YELLOW = "\033[93m"
RESET = "\033[0m"


def type_print(text: str, delay: float = 0.005):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()


def render_score_bar(score: int, total: int = 100, length: int = 25):
    filled = int(length * (score / total))
    bar = "█" * filled + "░" * (length - filled)
    return f"[{bar}] {score}/{total}"


def main():
    print(f"\n{BOLD}{CYAN}{'=' * 65}{RESET}")
    print(f"{BOLD}{CYAN}  ACCOUNT INTELLIGENCE AGENT — INTERACTIVE CLI DEMO{RESET}")
    print(f"{BOLD}{CYAN}{'=' * 65}{RESET}\n")

    if not SAMPLE_PATH.is_file():
        print(f"Error: Could not find sample data at {SAMPLE_PATH}")
        sys.exit(1)

    with open(SAMPLE_PATH, "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    print(f"{BOLD}1. INGESTING & VALIDATING TARGET ACCOUNT DATA...{RESET}")
    time.sleep(0.3)
    data = validate(raw_data)
    print(f"   • Company:    {BOLD}{data['company']}{RESET}")
    print(f"   • Domain:     {CYAN}{data['domain']}{RESET}")
    print(f"   • Industry:   {data['industry']}")
    print(f"   • Headcount:  {data['employee_count']} employees")
    print(f"   • Evidence:   {len(data['evidence'])} verified source observations loaded.")
    print()

    print(f"{BOLD}2. ANALYZING EVIDENCE & EVALUATING ICP FIT...{RESET}")
    time.sleep(0.4)
    score, checks = fit_score(data)

    for label, points, matched in checks:
        status = f"{GREEN}MATCH (+{points}){RESET}" if matched else f"{YELLOW}MISS (+0){RESET}"
        print(f"   • {label:<28} : {status}")

    print()
    print(f"   {BOLD}Overall ICP Score:{RESET}  {GREEN}{BOLD}{render_score_bar(score)}{RESET}")
    print()

    print(f"{BOLD}3. GENERATING EXECUTIVE BRIEF & DISCOVERY ANGLES...{RESET}")
    time.sleep(0.4)
    brief = build_brief(data)

    print(f"\n{BOLD}{BLUE}--- EXECUTIVE BRIEF PREVIEW ---{RESET}\n")
    type_print(brief, delay=0.002)

    output_path = Path(__file__).parent / "brief.md"
    output_path.write_text(brief, encoding="utf-8")

    print(f"\n{BOLD}{GREEN}✓ Complete!{RESET} Brief successfully saved locally to: {CYAN}brief.md{RESET}")
    print(f"{YELLOW}Note:{RESET} This demo executed locally with zero API credits consumed.\n")


if __name__ == "__main__":
    main()
