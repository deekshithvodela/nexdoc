import csv
import os
import re
import json

def clean_csv_file(filepath):
    print(f"Cleaning CSV {filepath}...")
    if not os.path.exists(filepath):
        print(f"File {filepath} not found!")
        return

    # Read the data
    with open(filepath, mode="r", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)
        rows = list(reader)

    # Find column indices
    try:
        name_idx = header.index("collegeName")
        code_idx = header.index("collegeCode")
    except ValueError as e:
        print(f"Required columns not found in {filepath}: {e}")
        return

    updated_count = 0
    for row in rows:
        if len(row) <= name_idx:
            continue
        college_name = row[name_idx]
        if ":" in college_name:
            parts = college_name.split(":", 1)
            prefix = parts[0].strip()
            # Verify prefix looks like a code
            if "/" in prefix or re.match(r"^[A-Z0-9/]+$", prefix, re.IGNORECASE):
                rest_name = parts[1].strip()
                row[name_idx] = rest_name
                # Only overwrite collegeCode if it is empty/falsy
                if len(row) > code_idx and not row[code_idx].strip():
                    row[code_idx] = prefix
                updated_count += 1

    print(f"Updated {updated_count} rows in CSV {filepath}.")

    # Write back the updated data
    with open(filepath, mode="w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)

def clean_json_file(filepath):
    print(f"Cleaning JSON {filepath}...")
    if not os.path.exists(filepath):
        print(f"File {filepath} not found!")
        return

    with open(filepath, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except Exception as e:
            print(f"Failed to load JSON: {e}")
            return

    if not isinstance(data, list):
        print("JSON is not a list, skipping...")
        return

    updated_count = 0
    for row in data:
        if not isinstance(row, dict):
            continue
        college_name = row.get("collegeName", "")
        if college_name and ":" in college_name:
            parts = college_name.split(":", 1)
            prefix = parts[0].strip()
            if "/" in prefix or re.match(r"^[A-Z0-9/]+$", prefix, re.IGNORECASE):
                rest_name = parts[1].strip()
                row["collegeName"] = rest_name
                # Set/update collegeCode if empty or missing
                if not row.get("collegeCode", "").strip():
                    row["collegeCode"] = prefix
                updated_count += 1

    print(f"Updated {updated_count} rows in JSON {filepath}.")

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    clean_csv_file("nmc-data/mbbs_colleges.csv")
    clean_csv_file("nmc-data/all_colleges_courses.csv")
    clean_json_file("nmc-data/mbbs_colleges.json")
    clean_json_file("nmc-data/all_colleges_courses.json")
