#!/usr/bin/env python3
"""
Template-based college name normalization.

Strategy: For each group of variant spellings of the same college,
pick the most-frequent form as the canonical template and replace
all other variants with it — across ALL CSV and JSON files.

This catches broken word boundaries like "AGARTAL A" vs "AGARTALA",
"BASAIDA RAPUR" vs "BASAIDARAPUR", etc. that regex-based comma
normalization cannot fix.
"""

import csv
import json
import os
import re
import io
import sys
from collections import Counter, defaultdict

SKIP_DIRS = {'.git', 'node_modules', 'venv', '.github', '.agents', 'scratch'}
SKIP_FILES = {'package.json', 'package-lock.json'}


def aggressive_key(name):
    """Fuzzy key: lowercase, strip all non-alphanumeric, remove trailing pincode."""
    n = name.lower().strip()
    n = re.sub(r'[^a-z0-9]', '', n)
    n = re.sub(r'\d{6}$', '', n)
    return n

def build_template_map(cutoff_master_path):
    """Build variant->template map from the cutoff master file.
    
    Template selection: fewest spaces (= fewest OCR-broken words), then most frequent.
    """
    with open(cutoff_master_path, 'r', encoding='utf-8') as f:
        rows = list(csv.DictReader(f))

    name_counts = Counter(r['college_name'] for r in rows)

    groups = defaultdict(list)
    for name, count in name_counts.items():
        groups[aggressive_key(name)].append((name, count))

    template_map = {}
    for k, variants in groups.items():
        if len(variants) <= 1:
            continue
        # Fewest spaces = cleanest (OCR breaks add spurious spaces), then most frequent
        variants.sort(key=lambda x: (x[0].count(' '), -x[1]))
        template = variants[0][0]
        for name, _ in variants[1:]:
            template_map[name] = template

    # Hardcoded overrides for variants that aggressive fuzzy key doesn't group
    overrides = {
        "GOVERNMENT MEDICAL COLLEGE, ANANTNAG J&K, VERINAG ROAD DIALGAM ANANTNAG, Jammu And Kashmir, 192210":
        "Government Medical College, Anantnag, verinag Road Dialgam Anantnag 192210, Jammu And Kashmir, 192210"
    }
    template_map.update(overrides)

    return template_map


def apply_to_string(value, template_map):
    """Replace a string value if it matches a variant exactly."""
    if value in template_map:
        return template_map[value], True
    return value, False


def process_json_file(filepath, template_map, dry_run=False):
    """Process a JSON file, replacing variant strings with templates."""
    with open(filepath, 'r', encoding='utf-8') as f:
        raw = f.read()

    # Quick check: does the file contain any variant?
    has_any = any(variant in raw for variant in template_map)
    if not has_any:
        return 0

    data = json.loads(raw)
    changes = [0]

    def walk(obj):
        if isinstance(obj, str):
            new_val, changed = apply_to_string(obj, template_map)
            if changed:
                changes[0] += 1
                return new_val
            return obj
        elif isinstance(obj, list):
            return [walk(item) for item in obj]
        elif isinstance(obj, dict):
            return {k: walk(v) for k, v in obj.items()}
        return obj

    new_data = walk(data)

    if changes[0] > 0 and not dry_run:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(new_data, f, indent=2, ensure_ascii=False)
            f.write('\n')

    return changes[0]


def process_csv_file(filepath, template_map, dry_run=False):
    """Process a CSV file, replacing variant strings with templates."""
    with open(filepath, 'r', encoding='utf-8', newline='') as f:
        content = f.read()

    # Quick check
    has_any = any(variant in content for variant in template_map)
    if not has_any:
        return 0

    if '\r\n' in content:
        line_ending = '\r\n'
    else:
        line_ending = '\n'

    reader = csv.DictReader(io.StringIO(content))
    fieldnames = reader.fieldnames
    if not fieldnames:
        return 0

    rows = list(reader)
    changes = 0
    new_rows = []

    for row in rows:
        new_row = {}
        for k in fieldnames:
            v = row.get(k, '')
            if v and isinstance(v, str):
                new_v, changed = apply_to_string(v, template_map)
                if changed:
                    changes += 1
                new_row[k] = new_v
            else:
                new_row[k] = v
        new_rows.append(new_row)

    if changes > 0 and not dry_run:
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=fieldnames, lineterminator=line_ending)
        writer.writeheader()
        writer.writerows(new_rows)
        with open(filepath, 'w', encoding='utf-8', newline='') as f:
            f.write(output.getvalue())

    return changes


def find_files(root_dir):
    """Find all CSV and JSON files to process."""
    files = []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fname in filenames:
            if fname in SKIP_FILES:
                continue
            if fname.endswith('.csv') or fname.endswith('.json'):
                files.append(os.path.join(dirpath, fname))
    return sorted(files)


def main():
    dry_run = '--dry-run' in sys.argv
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    cutoff_path = os.path.join(root_dir, 'aiq-cutoff-data', 'mbbs_cutoff_master.csv')

    if dry_run:
        print("=== DRY RUN MODE ===\n")

    # Step 1: Build template map from cutoff master
    template_map = build_template_map(cutoff_path)
    print(f"Template map: {len(template_map)} variant -> template replacements")
    for variant, template in sorted(template_map.items(), key=lambda x: x[1]):
        print(f"  {variant[:80]}")
        print(f"    -> {template[:80]}")
    print()

    # Step 2: Apply to all files
    files = find_files(root_dir)
    total_changes = 0
    files_changed = 0

    for filepath in files:
        relpath = os.path.relpath(filepath, root_dir)
        try:
            if filepath.endswith('.json'):
                changes = process_json_file(filepath, template_map, dry_run)
            elif filepath.endswith('.csv'):
                changes = process_csv_file(filepath, template_map, dry_run)
            else:
                continue

            if changes > 0:
                print(f"  {'[DRY] ' if dry_run else ''}Modified: {relpath} ({changes} replacements)")
                total_changes += changes
                files_changed += 1
        except Exception as e:
            print(f"  ERROR: {relpath}: {e}")

    print(f"\n{'[DRY RUN] ' if dry_run else ''}Summary:")
    print(f"  Files processed: {len(files)}")
    print(f"  Files modified: {files_changed}")
    print(f"  Total replacements: {total_changes}")


if __name__ == '__main__':
    main()
