import glob
import json
import os
import re

def slugify(text):
    text = str(text).lower()
    text = re.sub(r'[^a-z0-9]', '', text)
    return text

def slugify_state(st):
    s = str(st).lower().strip()
    s = s.replace('&', 'and')
    s = s.replace('-', '_')
    s = s.replace(' ', '_')
    s = ''.join(c for c in s if c.isalnum() or c == '_')
    return s

def standardize_data():
    workspace_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    data_dir = os.path.join(workspace_dir, "public", "data")
    
    # 1. Load Master Details Registry (924 colleges)
    details_path = os.path.join(data_dir, "colleges_details.json")
    details = json.load(open(details_path, "r", encoding="utf-8")) if os.path.exists(details_path) else {}
    
    # Load Alias Registry
    alias_ref_path = os.path.join(workspace_dir, "reference", "alias-to-canonical.json")
    alias_ref = json.load(open(alias_ref_path, "r", encoding="utf-8")) if os.path.exists(alias_ref_path) else {}

    # Build resolution mappings
    name_to_id = {}
    name_to_type = {}
    name_to_state = {}
    slug_to_canonical = {}

    for cid, info in details.items():
        can_name = info["college_name"]
        c_type = info.get("college_type") or info.get("management") or "Government"
        c_state = info.get("state") or ""

        name_to_id[can_name] = cid
        name_to_type[can_name] = c_type
        name_to_state[can_name] = c_state
        slug_to_canonical[slugify(can_name)] = can_name

        # Also map aliases
        for al in info.get("aliases", []):
            slug_to_canonical[slugify(al)] = can_name

    for alias_str, val in alias_ref.items():
        can = val.get("canonical") if isinstance(val, dict) else val
        if can and can in name_to_id:
            slug_to_canonical[slugify(alias_str)] = can

    # Helper function to resolve any raw college name to canonical info
    def resolve_college(raw_name):
        raw_str = str(raw_name).strip()
        if raw_str in name_to_id:
            can_name = raw_str
        else:
            s = slugify(raw_str)
            can_name = slug_to_canonical.get(s, raw_str)

        cid = name_to_id.get(can_name)
        if not cid:
            # Fallback lookup on details keys if cid missing
            s_can = slugify(can_name)
            for k, info in details.items():
                if slugify(info["college_name"]) == s_can:
                    cid = k
                    can_name = info["college_name"]
                    break

        return can_name, cid, name_to_type.get(can_name, "Government"), name_to_state.get(can_name, "")

    # 2. Standardize UG, PG, SS all.json datasets & summary.json & state files
    for level in ["ug", "pg", "ss"]:
        all_file = os.path.join(data_dir, level, "all.json")
        if not os.path.exists(all_file):
            continue

        all_data = json.load(open(all_file, "r", encoding="utf-8"))
        updated_items = []
        unique_colleges_set = set()
        total_seats_sum = 0
        state_grouped_data = {}

        for item in all_data:
            raw_cname = item.get("college_name")
            can_name, cid, ctype, cstate = resolve_college(raw_cname)

            if not cid:
                cid = item.get("college_id") or f"{level}_{slugify(can_name)}"

            item["college_name"] = can_name
            item["college_id"] = cid
            item["college_type"] = ctype
            if cstate and not item.get("state"):
                item["state"] = cstate

            unique_colleges_set.add(can_name)
            seats_val = item.get("seats", 0)
            if isinstance(seats_val, int):
                total_seats_sum += seats_val

            updated_items.append(item)

            # Group for state JSON files
            item_state = item.get("state", cstate)
            if item_state:
                st_slug = slugify_state(item_state)
                if st_slug not in state_grouped_data:
                    state_grouped_data[st_slug] = []
                state_grouped_data[st_slug].append(item)

        # Write standardized all.json
        with open(all_file, "w", encoding="utf-8") as f:
            json.dump(updated_items, f, indent=2, ensure_ascii=False)
        print(f"[{level.upper()}] Saved standardized {all_file} ({len(updated_items)} items, {len(unique_colleges_set)} unique colleges, {total_seats_sum:,} total seats).")

        # Update summary.json
        summary_file = os.path.join(data_dir, level, "summary.json")
        if os.path.exists(summary_file):
            summary_data = json.load(open(summary_file, "r", encoding="utf-8"))
            summary_data["totalColleges"] = len(unique_colleges_set)
            summary_data["totalSeats"] = total_seats_sum
            with open(summary_file, "w", encoding="utf-8") as f:
                json.dump(summary_data, f, indent=2, ensure_ascii=False)
            print(f"[{level.upper()}] Saved updated {summary_file}.")

        # Regenerate State JSON files
        states_dir = os.path.join(data_dir, level, "states")
        os.makedirs(states_dir, exist_ok=True)
        
        # Clear existing state files
        for old_sf in glob.glob(os.path.join(states_dir, "*.json")):
            os.remove(old_sf)

        for st_slug, st_items in state_grouped_data.items():
            sf_path = os.path.join(states_dir, f"{st_slug}.json")
            with open(sf_path, "w", encoding="utf-8") as f:
                json.dump(st_items, f, indent=2, ensure_ascii=False)

        print(f"[{level.upper()}] Regenerated {len(state_grouped_data)} state files in {states_dir}.")

    # 3. Synchronize ug_colleges_aiq_mapping.json
    aiq_file = os.path.join(data_dir, "ug_colleges_aiq_mapping.json")
    if os.path.exists(aiq_file):
        aiq_data = json.load(open(aiq_file, "r", encoding="utf-8"))
        updated_aiq = []
        for col in aiq_data:
            raw_cname = col.get("college_name")
            can_name, cid, ctype, cstate = resolve_college(raw_cname)

            col["college_name"] = can_name
            if cid:
                col["college_id"] = cid
            col["college_type"] = ctype
            if cstate:
                col["state"] = cstate

            # Pull latest details metadata if available
            if cid and cid in details:
                col["city"] = details[cid].get("city") or col.get("city", "")
                col["state"] = details[cid].get("state") or col.get("state", "")

            updated_aiq.append(col)

        with open(aiq_file, "w", encoding="utf-8") as f:
            json.dump(updated_aiq, f, indent=2, ensure_ascii=False)
        print(f"[AIQ] Saved synchronized {aiq_file} ({len(updated_aiq)} colleges).")

if __name__ == "__main__":
    standardize_data()
