"""
Generate human-readable (pretty-printed) copies of all data files.
Run as the final pipeline step to keep readable copies in sync with minified data.
"""
import json
import os
import glob

workspace_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
data_dir = os.path.join(workspace_dir, "public", "data")
ref_dir = os.path.join(workspace_dir, "reference")
out_dir = os.path.join(workspace_dir, "readable")

# Files to generate readable copies for
TARGETS = {
    # Dataset files
    "ug_all.json": os.path.join(data_dir, "ug", "all.json"),
    "pg_all.json": os.path.join(data_dir, "pg", "all.json"),
    "ss_all.json": os.path.join(data_dir, "ss", "all.json"),
    "colleges_details.json": os.path.join(data_dir, "colleges_details.json"),
    "ug_colleges_aiq_mapping.json": os.path.join(data_dir, "ug_colleges_aiq_mapping.json"),
    "aiq_cutoffs_master.json": os.path.join(data_dir, "aiq_cutoffs_master.json"),
    "aiq_cutoffs_summary.json": os.path.join(data_dir, "aiq_cutoffs_summary.json"),
    # Reference files
    "college_name_reference.json": os.path.join(ref_dir, "college-name-reference.json"),
}

def main():
    os.makedirs(out_dir, exist_ok=True)

    total = 0
    for out_name, src_path in TARGETS.items():
        if not os.path.exists(src_path):
            print(f"  Skip (missing): {src_path}")
            continue

        with open(src_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        out_path = os.path.join(out_dir, out_name)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        size_kb = os.path.getsize(out_path) // 1024
        print(f"  {out_name}: {size_kb}KB")
        total += 1

    # Also generate state-level files for PG (largest dataset)
    pg_states_dir = os.path.join(out_dir, "pg_states")
    os.makedirs(pg_states_dir, exist_ok=True)
    for fpath in sorted(glob.glob(os.path.join(data_dir, "pg", "states", "*.json"))):
        fname = os.path.basename(fpath)
        with open(fpath, "r", encoding="utf-8") as f:
            data = json.load(f)
        out_path = os.path.join(pg_states_dir, fname)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        total += 1

    print(f"\n  Generated {total} readable files in {out_dir}/")

if __name__ == "__main__":
    print("Generating readable data copies...")
    main()
