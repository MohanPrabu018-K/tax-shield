"""Scan all tracked files in git repository for sensitive credentials and private keys."""
import subprocess
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

PATTERNS = [
    re.compile(r'(?i)(api[_-]?key|secret[_-]?key|auth[_-]?token)\s*[:=]\s*["\']([0-9a-zA-Z\-_]{24,})["\']'),
    re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----'),
    re.compile(r'(?i)AKIA[0-9A-Z]{16}'),
    re.compile(r'(?i)(ghp_[0-9a-zA-Z]{36}|github_pat_[0-9a-zA-Z_]{82})'),
]

IGNORE_EXTENSIONS = {'.png', '.ico', '.jpg', '.pdf', '.woff', '.woff2', '.tsbuildinfo'}


def run_scan():
    raw_files = subprocess.check_output(['git', 'ls-files'], cwd=str(REPO_ROOT), text=True).splitlines()
    findings = []
    
    for rel_path in raw_files:
        p = REPO_ROOT / rel_path
        if p.suffix in IGNORE_EXTENSIONS:
            continue
        # Skip example or doc templates
        if '.example' in rel_path.lower():
            continue
        try:
            with open(p, 'r', encoding='utf-8', errors='ignore') as fp:
                for lno, line in enumerate(fp, 1):
                    for pat in PATTERNS:
                        m = pat.search(line)
                        if m:
                            # mask secret in finding
                            matched_str = m.group(0)
                            masked = matched_str[:12] + "...[REDACTED]"
                            findings.append({
                                "file": rel_path,
                                "line": lno,
                                "match_snippet": masked
                            })
        except Exception:
            pass
            
    print(f"Total tracked files scanned: {len(raw_files)}")
    print(f"Sensitive findings count: {len(findings)}")
    for item in findings:
        print(f"  [FLAG] {item['file']}:{item['line']} -> {item['match_snippet']}")
        
    return findings


if __name__ == '__main__':
    res = run_scan()
    # Exit with code 0 if 0 leaks found
    sys.exit(0 if len(res) == 0 else 1)
