#!/usr/bin/env python3
"""
Normalize comma spacing in all CSV and JSON files in the nexdoc project.

Transforms inconsistent comma spacing patterns:
  - "College, City , Address"  (space-comma-space)
  - "College, City,Address"    (comma-no-space)

Into canonical form:
  - "College, City, Address"   (comma-space)

Rule: re.sub(r'\\s*,\\s*', ', ', value)
"""

import csv
import json
import os
import re
import sys
import io

# Directories/files to skip
SKIP_DIRS = {'.git', 'node_modules', 'venv', '.github', '.agents', 'scratch'}
SKIP_FILES = {'package.json', 'package-lock.json'}

# The normalization regex: collapse any whitespace around commas to ", "
COMMA_PATTERN = re.compile(r'\s*,\s*')

def normalize_string(s):
    """Normalize comma spacing in a string value."""
    return COMMA_PATTERN.sub(', ', s)

def needs_normalization(s):
    """Check if a string has inconsistent comma spacing."""
    # Has space before comma, OR comma not followed by space (but followed by non-empty)
    if re.search(r'\s,', s):
        return True
    if re.search(r',[^\s]', s):
        return True
    return False

def normalize_json_value(obj):
    """Recursively normalize all string values in a JSON object."""
    changes = 0
    if isinstance(obj, str):
        new_val = normalize_string(obj)
        if new_val != obj:
            return new_val, 1
        return obj, 0
    elif isinstance(obj, list):
        new_list = []
        for item in obj:
            new_item, c = normalize_json_value(item)
            new_list.append(new_item)
            changes += c
        return new_list, changes
    elif isinstance(obj, dict):
        new_dict = {}
        for k, v in obj.items():
            new_v, c = normalize_json_value(v)
            new_dict[k] = new_v
            changes += c
        return new_dict, changes
    else:
        return obj, 0

def process_json_file(filepath, dry_run=False):
    """Process a JSON file, normalizing all string values."""
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    new_data, changes = normalize_json_value(data)

    if changes > 0 and not dry_run:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(new_data, f, indent=2, ensure_ascii=False)
            f.write('\n')

    return changes

def process_csv_file(filepath, dry_run=False):
    """Process a CSV file, normalizing all string cell values."""
    # Read the file
    with open(filepath, 'r', encoding='utf-8', newline='') as f:
        content = f.read()

    # Detect line ending
    if '\r\n' in content:
        line_ending = '\r\n'
    else:
        line_ending = '\n'

    # Parse CSV
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
                new_v = normalize_string(v)
                if new_v != v:
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
        # Skip unwanted directories
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

    if dry_run:
        print("=== DRY RUN MODE (no files will be modified) ===\n")

    files = find_files(root_dir)
    total_changes = 0
    files_changed = 0

    print(f"Found {len(files)} CSV/JSON files to process\n")

    for filepath in files:
        relpath = os.path.relpath(filepath, root_dir)
        try:
            if filepath.endswith('.json'):
                changes = process_json_file(filepath, dry_run)
            elif filepath.endswith('.csv'):
                changes = process_csv_file(filepath, dry_run)
            else:
                continue

            if changes > 0:
                print(f"  {'[DRY] ' if dry_run else ''}Modified: {relpath} ({changes} values normalized)")
                total_changes += changes
                files_changed += 1
        except Exception as e:
            print(f"  ERROR: {relpath}: {e}")

    print(f"\n{'[DRY RUN] ' if dry_run else ''}Summary:")
    print(f"  Files processed: {len(files)}")
    print(f"  Files {'would be ' if dry_run else ''}modified: {files_changed}")
    print(f"  Total values {'would be ' if dry_run else ''}normalized: {total_changes}")

if __name__ == '__main__':
    main()
