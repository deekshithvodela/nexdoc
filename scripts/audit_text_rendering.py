import json
import os
import re
import glob

def audit_text_artifacts():
    print("=============================================================")
    print("      TEXT RENDERING, MARKDOWN ARTIFACTS & ENCODING AUDIT   ")
    print("=============================================================\n")

    public_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'public'))

    # Patterns for potential markdown artifacts and funny/corrupted characters in rendered UI/data
    markdown_artifacts_pattern = re.compile(
        r'(\*\*[^*]+\*\*|__[^_]+__|#{1,6}\s+[^\n]+|\[[^\]]+\]\([^)]+\)|`[^`]+`)',
        re.IGNORECASE
    )
    funny_chars_pattern = re.compile(
        r'([\ufffd\u0080-\u009f\u00a0]|&amp;amp;|<\/div>div>)',
        re.IGNORECASE
    )

    findings = []

    # 1. Scan HTML and JS files
    code_files = glob.glob(os.path.join(public_dir, '**', '*.html'), recursive=True) + \
                 glob.glob(os.path.join(public_dir, '**', '*.js'), recursive=True)

    for filepath in code_files:
        rel_path = os.path.relpath(filepath, public_dir)
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            lines = f.readlines()

        for line_num, line in enumerate(lines, 1):
            # Check funny chars
            fc_matches = funny_chars_pattern.findall(line)
            if fc_matches:
                findings.append((rel_path, line_num, 'Funny Character / Corrupted Syntax', line.strip()))

            # Check markdown artifacts in HTML/JS strings (ignore comments or markdown files)
            if not rel_path.endswith('.md'):
                md_matches = markdown_artifacts_pattern.findall(line)
                if md_matches:
                    # Filter out js code like `template literals` or valid JS operations
                    for m in md_matches:
                        # If string contains markdown bold **text** or markdown header ### Header or markdown link [text](url)
                        if m.startswith('**') or m.startswith('__') or m.startswith('#') or (m.startswith('[') and '](' in m):
                            findings.append((rel_path, line_num, 'Markdown Artifact in Web Code', line.strip()))

    # 2. Scan JSON Data files
    json_files = glob.glob(os.path.join(public_dir, 'data', '**', '*.json'), recursive=True)
    json_findings = []

    for filepath in json_files:
        rel_path = os.path.relpath(filepath, public_dir)
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()

        # Check for replacement char \ufffd or weird control chars
        if '\ufffd' in content:
            json_findings.append((rel_path, 'Replacement Character \\ufffd detected'))
        
        # Check for markdown headers or markdown links inside JSON strings
        md_in_json = re.findall(r'"[^"]*(\*\*|__|\#{1,3}\s+|\[[^\]]+\]\([^)]+\))[^"]*"', content)
        if md_in_json:
            json_findings.append((rel_path, f"Markdown syntax in JSON data: {md_in_json[:3]}"))

    # Report Code Findings
    print(f"1. CODEBASE AUDIT ({len(code_files)} files scanned):")
    if not findings:
        print("   -> PASS: Zero funny characters, corrupted tags, or unparsed markdown artifacts in HTML/JS.")
    else:
        print(f"   -> FINDINGS: {len(findings)} potential issues found:")
        for rel_path, line_num, ftype, snippet in findings[:10]:
            print(f"      - {rel_path}:L{line_num} [{ftype}] -> {snippet[:90]}")

    # Report JSON Findings
    print(f"\n2. DATASET AUDIT ({len(json_files)} JSON files scanned):")
    if not json_findings:
        print("   -> PASS: Zero funny characters or markdown artifacts in JSON datasets.")
    else:
        print(f"   -> FINDINGS: {len(json_findings)} issues found in datasets:")
        for rel_path, desc in json_findings[:10]:
            print(f"      - {rel_path}: {desc}")

    print("\n=============================================================")
    if not findings and not json_findings:
        print("   RESULT: 100% CLEAN — NO MARKDOWN ARTIFACTS OR FUNNY CHARACTERS!")
    else:
        print("   RESULT: ISSUES DETECTED FOR CLEANUP!")
    print("=============================================================")

if __name__ == '__main__':
    audit_text_artifacts()
