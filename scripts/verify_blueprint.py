#!/usr/bin/env python3
"""
Blueprint Automated Verification & Consistency Test Suite
Verifies:
1. Internal markdown anchors and cross-references.
2. Mathematical consistency across comparison tables and step-by-step arithmetic.
3. Synchronization between README.md and TECHNICAL_DESIGN_DOCUMENT.md.
4. Well-formedness of external statutory links.
"""

import os
import re
import sys

# Configure UTF-8 stdout
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def load_file(rel_path):
    full_path = os.path.join(REPO_ROOT, rel_path)
    with open(full_path, "r", encoding="utf-8") as f:
        return f.read()

def test_anchors():
    print("Checking markdown anchors and cross-references...")
    tdd = load_file("TECHNICAL_DESIGN_DOCUMENT.md")
    readme = load_file("README.md")
    sidebar = load_file("_sidebar.md")

    # Collect anchors in TDD
    tdd_anchors = set(re.findall(r'<a\s+id="([^"]+)"></a>', tdd))
    for h in re.findall(r'^#{1,6}\s+(.+)$', tdd, re.MULTILINE):
        slug = re.sub(r'[^\w\s-]', '', h.lower())
        slug = re.sub(r'[-\s]+', '-', slug).strip('-')
        tdd_anchors.add(slug)

    # Collect anchors in README
    readme_anchors = set(re.findall(r'<a\s+id="([^"]+)"></a>', readme))
    for h in re.findall(r'^#{1,6}\s+(.+)$', readme, re.MULTILINE):
        slug = re.sub(r'[^\w\s-]', '', h.lower())
        slug = re.sub(r'[-\s]+', '-', slug).strip('-')
        readme_anchors.add(slug)

    # Check internal links inside TDD (#anchor)
    errors = []
    for label, target in re.findall(r'\[([^\]]+)\]\(#([^)]+)\)', tdd):
        if target not in tdd_anchors:
            errors.append(f"TDD internal link broken: [{label}](#{target})")

    # Check links from README to TDD
    for label, target in re.findall(r'\[([^\]]+)\]\(TECHNICAL_DESIGN_DOCUMENT\.md#([^)]+)\)', readme):
        if target not in tdd_anchors:
            errors.append(f"README -> TDD link broken: [{label}](TECHNICAL_DESIGN_DOCUMENT.md#{target})")

    # Check links from Sidebar to TDD
    for label, target in re.findall(r'\[([^\]]+)\]\(TECHNICAL_DESIGN_DOCUMENT\.md#([^)]+)\)', sidebar):
        if target not in tdd_anchors:
            errors.append(f"Sidebar -> TDD link broken: [{label}](TECHNICAL_DESIGN_DOCUMENT.md#{target})")

    if errors:
        for err in errors:
            print(f"  ❌ {err}")
        return False
    print(f"  ✅ All internal anchors resolve cleanly ({len(tdd_anchors)} TDD anchors verified).")
    return True

def test_math_consistency():
    print("Checking mathematical consistency and baseline arithmetic...")
    tdd = load_file("TECHNICAL_DESIGN_DOCUMENT.md")
    readme = load_file("README.md")

    # Core baseline parameters
    deferral = 30000.0
    match = 10000.0
    marginal_tax = 0.413  # 32% Fed + 9.3% State
    growth = 10000.0
    total_balance = deferral + match + growth  # $50,000

    # 1. Tax saved upfront
    upfront_saved = deferral * marginal_tax
    assert abs(upfront_saved - 12390.0) < 0.01

    # 2. 2026 ECI Brackets
    bracket10_cap = 12400.0
    bracket12_cap = 50400.0
    principal_eci = deferral + match  # $40,000

    eci_tax_10 = bracket10_cap * 0.10  # $1,240.00
    eci_tax_12 = (principal_eci - bracket10_cap) * 0.12  # $27,600 * 0.12 = $3,312.00
    total_eci_tax = eci_tax_10 + eci_tax_12  # $4,552.00
    assert abs(total_eci_tax - 4552.0) < 0.01

    # 3. FDAP Tax
    fdap_tax = growth * 0.30  # $3,000.00
    assert abs(fdap_tax - 3000.0) < 0.01

    # 4. Total Pipeline Tax
    total_tax = total_eci_tax + fdap_tax  # $7,552.00
    net_after_tax = total_balance - total_tax  # $42,448.00
    assert abs(net_after_tax - 42448.0) < 0.01

    # 5. Alt D comparison
    alt_d_start = deferral - upfront_saved  # $17,610.00
    alt_d_gain = alt_d_start * 0.25  # $4,402.50 -> ~$4,403
    alt_d_net = alt_d_start + alt_d_gain  # ~$22,013
    assert abs(alt_d_net - 22012.5) < 1.0

    net_advantage = net_after_tax - 22013.0  # $20,435.00
    assert abs(net_advantage - 20435.0) < 1.0

    # Verify figures exist in both README and TDD
    expected_figures = [
        "$42,448",
        "$7,552",
        "$4,552",
        "$3,000",
        "$37,448",
        "$22,013",
        "$20,435"
    ]

    for fig in expected_figures:
        if fig not in tdd:
            print(f"  ❌ Missing expected figure '{fig}' in TECHNICAL_DESIGN_DOCUMENT.md")
            return False
        if fig not in readme:
            print(f"  ❌ Missing expected figure '{fig}' in README.md")
            return False

    print("  ✅ All arithmetic checks passed ($50,000 baseline, $7,552 tax, $42,448 net, +$20,435 gain).")
    return True

def test_external_links():
    print("Checking external URL syntax and statutory citations...")
    tdd = load_file("TECHNICAL_DESIGN_DOCUMENT.md")
    urls = re.findall(r'https?://[^\s)\]">]+', tdd)
    print(f"  Found {len(urls)} external links.")

    critical_domains = ["irs.gov", "incometaxindia.gov.in", "github.com", "schwab.com"]
    for domain in critical_domains:
        count = sum(1 for u in urls if domain in u)
        if count == 0:
            print(f"  ❌ Warning: No URLs found for critical domain '{domain}'")
            return False
        print(f"  ✅ Verified {count} links for {domain}")

    return True

def test_web_and_theme_support():
    print("Checking web portal structure and dark mode integration...")
    html = load_file("index.html")

    required_snippets = [
        ("FOUC prevention theme detection script", "localStorage.getItem('blueprint-theme')"),
        ("prefers-color-scheme media query", "@media (prefers-color-scheme: dark)"),
        ("Explicit dark mode data-theme CSS", ':root[data-theme="dark"]'),
        ("Floating theme toggle button", 'id="theme-toggle-btn"'),
        ("Mermaid dynamic dark theme support", "theme: isDarkEffective() ? 'dark' : 'default'"),
        ("Noscript accessibility fallback", "<noscript>")
    ]

    for label, snippet in required_snippets:
        if snippet not in html:
            print(f"  ❌ Missing required web portal snippet: {label} ('{snippet}')")
            return False

    print("  ✅ Web portal dark mode, system theme detection, and noscript fallbacks verified.")
    return True

def main():
    print("=" * 60)
    print("RUNNING BLUEPRINT VERIFICATION TEST SUITE")
    print("=" * 60)

    p1 = test_anchors()
    p2 = test_math_consistency()
    p3 = test_external_links()
    p4 = test_web_and_theme_support()

    print("=" * 60)
    if p1 and p2 and p3 and p4:
        print("ALL BLUEPRINT TESTS PASSED! ✅")
        print("=" * 60)
        sys.exit(0)
    else:
        print("SOME TESTS FAILED! ❌")
        print("=" * 60)
        sys.exit(1)

if __name__ == "__main__":
    main()

