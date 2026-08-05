import json
import os

workspace_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
data_path = os.path.join(workspace_dir, "aiq-cutoff-data", "consolidated_all_india_quota_allotment.json")
out_path = os.path.join(workspace_dir, "reference", "raw_college_cutoffs_mapping.json")

def generate_raw_cutoffs():
    print(f"Loading allotment data from {data_path}...")
    with open(data_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    print(f"Loaded {len(data)} candidate rank records.")

    # Group by (un-normalized raw_college_name, quota, category, course)
    cutoff_groups = {}

    def get_group(college, quota, category, course):
        c_name = college.strip()
        q_name = quota.strip()
        cat_name = category.strip()
        crs_name = course.strip()
        key = (c_name, q_name, cat_name, crs_name)
        if key not in cutoff_groups:
            cutoff_groups[key] = {
                "college_name": c_name,
                "quota": q_name,
                "category": cat_name,
                "course": crs_name,
                "r1_ranks": [],
                "r2_ranks": [],
                "r3_ranks": [],
                "all_ranks": [],
                "confirmed_seats": 0
            }
        return cutoff_groups[key]

    for d in data:
        air = d.get("all_india_rank")
        if not air or not isinstance(air, int):
            continue

        # Track Round 1 Allotments & Ranks
        r1_inst = d.get("r1_allotted_institute")
        if r1_inst and r1_inst != "-":
            grp = get_group(
                r1_inst,
                d.get("r1_allotted_quota", "-"),
                d.get("r1_allotted_category", "-"),
                d.get("r1_course", "MBBS")
            )
            grp["r1_ranks"].append(air)
            grp["all_ranks"].append(air)

        # Track Round 2 Allotments & Ranks
        r2_inst = d.get("r2_allotted_institute")
        if r2_inst and r2_inst != "-":
            grp = get_group(
                r2_inst,
                d.get("r2_allotted_quota", "-"),
                d.get("r2_allotted_category", "-"),
                d.get("r2_course", "MBBS")
            )
            grp["r2_ranks"].append(air)
            grp["all_ranks"].append(air)

        # Track Round 3 Allotments & Ranks
        r3_inst = d.get("r3_allotted_institute")
        if r3_inst and r3_inst != "-":
            grp = get_group(
                r3_inst,
                d.get("r3_allotted_quota", "-"),
                d.get("r3_allotted_category", "-"),
                d.get("r3_course", "MBBS")
            )
            grp["r3_ranks"].append(air)
            grp["all_ranks"].append(air)

        # Track Confirmed Seats Allotted (Excluding candidates who upgraded out or were Not Allotted)
        final_inst = d.get("final_allotted_institute")
        final_rem = d.get("final_status_remarks", "")
        if final_inst and final_inst != "-" and "Not Allotted" not in final_rem:
            grp = get_group(
                final_inst,
                d.get("final_allotted_quota", "-"),
                d.get("final_allotted_category", "-"),
                d.get("final_course", "MBBS")
            )
            grp["confirmed_seats"] += 1

    output_list = []
    for key, grp in cutoff_groups.items():
        r1_o = min(grp["r1_ranks"]) if grp["r1_ranks"] else None
        r1_c = max(grp["r1_ranks"]) if grp["r1_ranks"] else None

        r2_o = min(grp["r2_ranks"]) if grp["r2_ranks"] else None
        r2_c = max(grp["r2_ranks"]) if grp["r2_ranks"] else None

        r3_o = min(grp["r3_ranks"]) if grp["r3_ranks"] else None
        r3_c = max(grp["r3_ranks"]) if grp["r3_ranks"] else None

        fin_o = min(grp["all_ranks"]) if grp["all_ranks"] else None
        fin_c = max(grp["all_ranks"]) if grp["all_ranks"] else None

        output_list.append({
            "college_name": grp["college_name"],
            "quota": grp["quota"],
            "category": grp["category"],
            "course": grp["course"],
            "r1_opening_rank": r1_o,
            "r1_closing_rank": r1_c,
            "r1_allotted_count": len(grp["r1_ranks"]),
            "r2_opening_rank": r2_o,
            "r2_closing_rank": r2_c,
            "r2_allotted_count": len(grp["r2_ranks"]),
            "r3_opening_rank": r3_o,
            "r3_closing_rank": r3_c,
            "r3_allotted_count": len(grp["r3_ranks"]),
            "final_opening_rank": fin_o,
            "final_closing_rank": fin_c,
            "confirmed_seats_allotted": grp["confirmed_seats"]
        })

    print(f"Generated {len(output_list)} raw college cutoff mapping records.")

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output_list, f, indent=2, ensure_ascii=False)

    print(f"Saved raw cutoffs mapping to {out_path}")

if __name__ == "__main__":
    generate_raw_cutoffs()
