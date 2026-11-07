"""
Generator for all 33 virtual customer validation documents.
Outputs to docs/virtual-customer-validation/
"""

import os
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS_DIR = os.path.join(BASE_DIR, "docs", "virtual-customer-validation")
os.makedirs(DOCS_DIR, exist_ok=True)

DISCLAIMER = "> **Simulated virtual-user product evaluation using synthetic identities and financial data. This is not real-world customer validation.**\n\n---\n\n"

def write_doc(filename: str, content: str):
    path = os.path.join(DOCS_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(DISCLAIMER + content.strip() + "\n")
    print(f"Generated: {filename} ({len(content)} bytes)")

print("Ready to generate documents.")
