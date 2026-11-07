"""
Generator for all Real CA Firm Pilot (v1.2) documents in docs/real-ca-pilot/
Maintains absolute honesty: differentiates previous synthetic simulation from real cohort recruitment.
"""

import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS_DIR = os.path.join(BASE_DIR, "docs", "real-ca-pilot")
os.makedirs(DOCS_DIR, exist_ok=True)

DISCLAIMER = "> **REAL CA FIRM PILOT (v1.2) — GOVERNANCE & EXECUTION FRAMEWORK**  \n> *This document governs the recruitment, onboarding, and operational validation of genuine consenting Indian CA firms and their clients. No virtual personas are represented as real participants.*\n\n---\n\n"

def write_doc(filename: str, content: str):
    path = os.path.join(DOCS_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(DISCLAIMER + content.strip() + "\n")
    print(f"Generated: {filename} ({len(content)} bytes)")

print("Ready to generate Real CA Firm Pilot documents.")

