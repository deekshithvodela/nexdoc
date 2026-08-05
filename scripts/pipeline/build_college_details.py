import json
import os
import re
import subprocess

def slugify(text):
    text = str(text).lower()
    text = re.sub(r'[^a-z0-9]', '', text)
    return text

def build_college_details():
    workspace_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    # Load Master Colleges List (926 colleges)
    master_ref_path = os.path.join(workspace_dir, "reference", "master-lists-of-colleges.json")
    master_colleges = json.load(open(master_ref_path, "r", encoding="utf-8")) if os.path.exists(master_ref_path) else []
    
    # Load existing details from file
    existing_details_path = os.path.join(workspace_dir, "public", "data", "colleges_details.json")
    existing_details = json.load(open(existing_details_path, "r", encoding="utf-8")) if os.path.exists(existing_details_path) else {}

    # Attempt to load rich legacy details from git history (HEAD~3) for original accurate management types
    legacy_git_details = {}
    try:
        git_cmd = ["git", "show", "HEAD~3:public/data/colleges_details.json"]
        res = subprocess.run(git_cmd, capture_output=True, text=True, cwd=workspace_dir)
        if res.returncode == 0:
            legacy_git_details = json.loads(res.stdout)
            print(f"Loaded {len(legacy_git_details)} rich legacy detail records from git history.")
    except Exception as e:
        print(f"Could not load git history details (using current filesystem details): {e}")

    # Load Location Reference
    loc_ref_path = os.path.join(workspace_dir, "reference", "master-locations-reference.json")
    loc_ref = json.load(open(loc_ref_path, "r", encoding="utf-8")) if os.path.exists(loc_ref_path) else {"official_states": [], "state_aliases": {}, "city_registry": {}}

    official_states_set = set(loc_ref.get("official_states", []))
    state_alias_map = loc_ref.get("state_aliases", {})
    city_registry = loc_ref.get("city_registry", {})

    # Load Alias Registry for aliases array population
    alias_ref_path = os.path.join(workspace_dir, "reference", "alias-to-canonical.json")
    alias_ref = json.load(open(alias_ref_path, "r", encoding="utf-8")) if os.path.exists(alias_ref_path) else {}

    canonical_to_aliases = {}
    for alias_str, val in alias_ref.items():
        can = val.get("canonical") if isinstance(val, dict) else val
        if can:
            if can not in canonical_to_aliases:
                canonical_to_aliases[can] = set()
            canonical_to_aliases[can].add(can)
            canonical_to_aliases[can].add(alias_str)

    # City Synonym Registry (Old Name -> Official Canonical City Name)
    city_synonyms = {
        'mangalore': 'Mangaluru', 'mangaluru': 'Mangaluru',
        'bangalore': 'Bengaluru', 'bengaluru': 'Bengaluru',
        'belgaum': 'Belagavi', 'belagavi': 'Belagavi',
        'cochin': 'Kochi', 'kochi': 'Kochi',
        'trivandrum': 'Thiruvananthapuram', 'thiruvananthapuram': 'Thiruvananthapuram',
        'calicut': 'Kozhikode', 'kozhikode': 'Kozhikode',
        'baroda': 'Vadodara', 'vadodara': 'Vadodara',
        'benares': 'Varanasi', 'varanasi': 'Varanasi',
        'pondicherry': 'Puducherry', 'puducherry': 'Puducherry',
        'bombay': 'Mumbai', 'mumbai': 'Mumbai',
        'madras': 'Chennai', 'chennai': 'Chennai',
        'calcutta': 'Kolkata', 'kolkata': 'Kolkata',
        'poona': 'Pune', 'pune': 'Pune',
        'gurgaon': 'Gurugram', 'gurugram': 'Gurugram',
        'gauhati': 'Guwahati', 'guwahati': 'Guwahati',
        'simla': 'Shimla', 'shimla': 'Shimla',
        'allahabad': 'Prayagraj', 'prayagraj': 'Prayagraj',
        'gulbarga': 'Kalaburagi', 'kalaburagi': 'Kalaburagi',
        'bellary': 'Ballari', 'ballari': 'Ballari',
        'bijapur': 'Vijayapura', 'vijayapura': 'Vijayapura',
        'mysore': 'Mysuru', 'mysuru': 'Mysuru',
        'hubli': 'Hubballi', 'hubballi': 'Hubballi',
        'shimoga': 'Shivamogga', 'shivamogga': 'Shivamogga',
        'tumkur': 'Tumakuru', 'tumakuru': 'Tumakuru'
    }

    # Index details by slugified college_name
    details_by_slug = {}
    for k, v in legacy_git_details.items():
        if isinstance(v, dict):
            c_name = v.get("college_name") or k
            details_by_slug[slugify(c_name)] = v

    for k, v in existing_details.items():
        if isinstance(v, dict):
            c_name = v.get("college_name") or k
            s = slugify(c_name)
            if s not in details_by_slug:
                details_by_slug[s] = v

    state_abbrev = {
        "Andaman and Nicobar Islands": "AN", "Andhra Pradesh": "AP", "Arunachal Pradesh": "AR",
        "Assam": "AS", "Bihar": "BR", "Chandigarh": "CH", "Chhattisgarh": "CG",
        "Dadra and Nagar Haveli and Daman and Diu": "DN", "Delhi": "DL", "Goa": "GA",
        "Gujarat": "GJ", "Haryana": "HR", "Himachal Pradesh": "HP", "Jammu and Kashmir": "JK",
        "Jharkhand": "JH", "Karnataka": "KA", "Kerala": "KL", "Ladakh": "LA",
        "Lakshadweep": "LD", "Madhya Pradesh": "MP", "Maharashtra": "MH", "Manipur": "MN",
        "Meghalaya": "ML", "Mizoram": "MZ", "Nagaland": "NL", "Odisha": "OR",
        "Puducherry": "PY", "Punjab": "PB", "Rajasthan": "RJ", "Sikkim": "SK",
        "Tamil Nadu": "TN", "Telangana": "TG", "Tripura": "TR", "Uttar Pradesh": "UP",
        "Uttarakhand": "UK", "West Bengal": "WB"
    }

    # Location resolution helper
    def resolve_location(c_name, address="", legacy_city=""):
        c_lower = c_name.lower().strip()
        address_lower = address.lower().strip()

        derived_city = ""
        derived_state = ""

        # Check legacy city if valid and not a state
        if legacy_city and legacy_city not in official_states_set:
            derived_city = city_synonyms.get(legacy_city.lower(), legacy_city)

        # Check city synonyms first
        if not derived_city:
            for old_c, canonical_c in city_synonyms.items():
                if re.search(r'\b' + re.escape(old_c) + r'\b', c_lower) or re.search(r'\b' + re.escape(old_c) + r'\b', address_lower):
                    derived_city = canonical_c
                    break

        # Check city registry if not matched
        if not derived_city:
            for key, info in city_registry.items():
                if re.search(r'\b' + re.escape(key) + r'\b', c_lower) or re.search(r'\b' + re.escape(key) + r'\b', address_lower):
                    derived_city = info["city_name"]
                    derived_state = info["state"]
                    break

        # Resolve city from name parts if still state or empty
        if not derived_city or derived_city in official_states_set:
            parts = [p.strip() for p in c_name.split(",") if p.strip()]
            for part in reversed(parts):
                if part in official_states_set or part in state_alias_map or part in state_alias_map.values():
                    continue
                clean_p = re.sub(r'(?i)\b(distt|district|dist|road|campus|society|hospital|institute)\b.*', '', part).strip()
                if clean_p and len(clean_p) >= 3 and clean_p not in official_states_set:
                    derived_city = city_synonyms.get(clean_p.lower(), clean_p)
                    break

        # Resolve state
        if not derived_state:
            for st in official_states_set:
                if re.search(r'\b' + re.escape(st.lower()) + r'\b', c_lower) or re.search(r'\b' + re.escape(st.lower()) + r'\b', address_lower):
                    derived_state = st
                    break

        if not derived_state:
            for alias, target_st in state_alias_map.items():
                if re.search(r'\b' + re.escape(alias) + r'\b', c_lower) or re.search(r'\b' + re.escape(alias) + r'\b', address_lower):
                    derived_state = target_st
                    break

        # Standardize city via synonym lookup
        if derived_city and derived_city.lower() in city_synonyms:
            derived_city = city_synonyms[derived_city.lower()]

        return derived_city, derived_state

    # Track sequence counters per state and sector to guarantee unique codes
    state_sector_counters = {}
    used_college_ids = set()

    def generate_unique_code(st_prefix, sector_code, tier_code):
        key = f"{st_prefix}_{sector_code}_{tier_code}"
        state_sector_counters[key] = state_sector_counters.get(key, 0) + 1
        seq_num = state_sector_counters[key]
        
        c_code = f"{st_prefix}/{seq_num:03d}/{sector_code}/{tier_code}"
        c_id = f"ug_{st_prefix.lower()}{seq_num:03d}{sector_code.lower()}{tier_code}"
        
        while c_id in used_college_ids:
            state_sector_counters[key] += 1
            seq_num = state_sector_counters[key]
            c_code = f"{st_prefix}/{seq_num:03d}/{sector_code}/{tier_code}"
            c_id = f"ug_{st_prefix.lower()}{seq_num:03d}{sector_code.lower()}{tier_code}"
            
        used_college_ids.add(c_id)
        return c_code, c_id

    output_details = {}

    for c_name in master_colleges:
        matched_obj = details_by_slug.get(slugify(c_name)) or {}

        address = matched_obj.get("address", "")
        legacy_city = matched_obj.get("city", "")
        city, state = resolve_location(c_name, address, legacy_city)
        if not state:
            state = matched_obj.get("state") or ("Delhi" if "AIIMS" in c_name and "Delhi" in c_name else "India")

        # Determine sector and college_type accurately
        raw_mgmt = str(matched_obj.get("management") or matched_obj.get("college_type") or "").strip()
        c_name_lower = c_name.lower()

        # Full Institutes of National Importance (INI) matching
        is_ini = any(kw in c_name_lower for kw in [
            'all india institute of medical sciences', 'aiims',
            'jawaharlal institute of postgraduate medical education', 'jipmer',
            'postgraduate institute of medical education and research', 'pgimer',
            'national institute of mental health and neurosciences', 'nimhans',
            'sree chitra tirunal'
        ]) or "National Importance" in matched_obj.get("university", "")

        if is_ini:
            college_type = "INI"
            sector_code = "I"
            st_prefix = "IN"
        elif raw_mgmt == "Deemed" or "Deemed" in c_name or "Deemed" in matched_obj.get("university", ""):
            college_type = "Deemed"
            sector_code = "P"
            st_prefix = state_abbrev.get(state, "IN")
        elif raw_mgmt in ["Private", "Trust", "Society"] or "Private" in c_name or "Trust" in c_name or "Society" in c_name or "Foundation" in c_name or "Charitable" in c_name or "A J Institute" in c_name or "Adichunchanagiri" in c_name or "Akash" in c_name or "Al-Azhar" in c_name or "Shri Rawatpura" in c_name:
            college_type = "Private"
            sector_code = "P"
            st_prefix = state_abbrev.get(state, "IN")
        elif raw_mgmt == "Government" or "Government" in c_name or "Govt" in c_name or "Autonomous State" in c_name or "ESI" in c_name or "ESIC" in c_name or "Municipal" in c_name or "Command" in c_name or "Armed Forces" in c_name or "Rajkiya" in c_name:
            college_type = "Government"
            sector_code = "G"
            st_prefix = state_abbrev.get(state, "IN")
        else:
            college_type = raw_mgmt if raw_mgmt in ["Government", "Private", "Deemed", "INI"] else ("Government" if "Medical College" in c_name and ("District" in c_name or "State" in c_name or "Govt" in c_name) else "Private")
            sector_code = "I" if college_type == "INI" else ("G" if college_type == "Government" else "P")
            st_prefix = "IN" if college_type == "INI" else state_abbrev.get(state, "IN")

        tier_code = "1" if college_type in ["Government", "INI"] else "3"

        college_code, college_id = generate_unique_code(st_prefix, sector_code, tier_code)

        # Collect aliases and generate dual city aliases
        aliases_set = canonical_to_aliases.get(c_name, set([c_name]))
        if "aliases" in matched_obj and isinstance(matched_obj["aliases"], list):
            aliases_set.update(matched_obj["aliases"])
        elif "canonical_names" in matched_obj and isinstance(matched_obj["canonical_names"], list):
            aliases_set.update(matched_obj["canonical_names"])

        # Auto-generate dual city aliases if city synonym applies
        for old_c, new_c in city_synonyms.items():
            if old_c in c_name.lower() and old_c != new_c.lower():
                pattern = re.compile(re.escape(old_c), re.IGNORECASE)
                alt_name = pattern.sub(new_c, c_name)
                aliases_set.add(alt_name)
            elif new_c.lower() in c_name.lower() and old_c != new_c.lower():
                pattern = re.compile(re.escape(new_c), re.IGNORECASE)
                alt_name = pattern.sub(old_c.capitalize(), c_name)
                aliases_set.add(alt_name)

        aliases_list = sorted(list(aliases_set))

        # Extract pincode from address if missing
        pincode = matched_obj.get("pincode", "")
        if not pincode and address:
            pin_match = re.search(r'\b\d{6}\b', address)
            if pin_match:
                pincode = pin_match.group(0)

        output_details[college_id] = {
            "college_id": college_id,
            "college_code": college_code,
            "college_name": c_name,
            "college_type": college_type,
            "management": matched_obj.get("management") or college_type,
            "state": state,
            "city": city,
            "pincode": pincode,
            "address": address or f"{c_name}, {city}, {state}",
            "website": matched_obj.get("website", ""),
            "email": matched_obj.get("email", ""),
            "telephone": matched_obj.get("telephone", ""),
            "fax": matched_obj.get("fax", ""),
            "year_of_inc": matched_obj.get("year_of_inc", ""),
            "university": matched_obj.get("university", ""),
            "status": matched_obj.get("status", "Recognized"),
            "status_text": matched_obj.get("status_text", ""),
            "dean_name": matched_obj.get("dean_name", ""),
            "dean_designation": matched_obj.get("dean_designation", ""),
            "contacts": matched_obj.get("contacts", []),
            "aliases": aliases_list,
            "canonical_names": aliases_list
        }

    out_file = os.path.join(workspace_dir, "public", "data", "colleges_details.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(output_details, f, indent=2, ensure_ascii=False)

    print(f"Saved standardized details directory to {out_file} ({len(output_details)} master colleges).")

if __name__ == "__main__":
    build_college_details()
