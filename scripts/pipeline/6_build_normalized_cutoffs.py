import json
import os
import re

workspace_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
raw_cutoffs_path = os.path.join(workspace_dir, "reference", "raw_college_cutoffs_mapping.json")
alias_registry_path = os.path.join(workspace_dir, "reference", "alias-to-canonical.json")
master_list_path = os.path.join(workspace_dir, "reference", "master-lists-of-colleges.json")
quotas_cats_path = os.path.join(workspace_dir, "reference", "master-quotas-and-categories.json")

out_ref_path = os.path.join(workspace_dir, "reference", "normalized_college_cutoffs.json")
out_public_path = os.path.join(workspace_dir, "public", "data", "ug_colleges_aiq_mapping.json")

MANUAL_AIQ_OVERRIDES = {
    "aiims bilaspur": "All India Institute of Medical Sciences, Bilaspur",
    "aiims bilaspur changar palasiyan": "All India Institute of Medical Sciences, Bilaspur",
    "aiims bibi nagar hyderabad": "All India Institute of Medical Sciences, Bibinagar",
    "aiims bibinagar hyderabad": "All India Institute of Medical Sciences, Bibinagar",
    "aiims deogarh": "All India Institute of Medical Sciences, Deoghar",
    "aiims rai bareli": "All India Institute of Medical Sciences, Raebareli",
    "belgaum inst of medical sci belgaum": "Belagavi Institute of Medical Sciences, Belagavi",
    "bidar institute of medical sci bidar": "Bidar Institute of Medical Sciences, Bidar",
    "b l d e university bijapur": "BLDE (Deemed to be University), Vijayapura",
    "bv deemed uni med college and hos sangli": "Bharati Vidyapeeth Deemed University Medical College and Hospital, Sangli",
    "autonomous state medical college society mirzapur": "Maa Vindhyavasini Autonomous State Medical College, Mirzapur",
    "autonomous state medical college etah": "Autonomous State Medical College Society, Etah, Uttar Pradesh",
    "autonomous state medical college fatehpur": "Autonomous State Medical College Society, Fatehpur",
    "autonomous state medical college ghazipur": "Maharishi Vishwamitra Autonomous State Medical College, Ghazipur",
    "autonomous state medical college gonda": "Autonomous State Medical College, Gonda",
    "autonomous state medical college kanpur dehat uttar pradesh": "Autonomous State Medical College, Kanpur Dehat",
    "autonomous state medical college lakhimpur kheri uttar pradesh": "Autonomous State Medical College, Lakhimpur Kheri",
    "autonomous state medical college kaushambi": "Autonomous State Medical College, Kaushambi",
    "autonomous state medical college sehud auraiya": "Autonomous State Medical College, Auraiya",
    "bhaarath medical college and hospital": "Bhaarath Medical College and Hospital, Chennai",
    "andaman and nicobar islands institute of medical s": "Andaman & Nicobar Islands Institute of Medical Sciences, Port Blair",
    "aarupadai veedu medical college and hospt puducherry": "Aarupadai Veedu Medical College & Hospital, Puducherry",
    "bangalore medical college and research institute": "Bangalore Medical College and Research Institute, Bangalore",
    "bhima bhoi medical college and hospital balangir": "Bhima Bhoi Medical College and Hospital, Balangir",
    "c institute of medical sciences chamarajanagar": "Chamarajanagar Institute of Medical Sciences, Chamarajanagar",
    "chengalpattu medical coll chengalpattu": "Chengalpattu Medical College, Chengalpattu",
    "chhattisgarh institute of medical sciences bilasp": "Chhattisgarh Institute of Medical Sciences, Bilaspur",
    "chettinad hos and res inst kancheepuram": "Chettinad Hospital and Research Institute, Kanchipuram",
    "chhindwara institute of medical sciences": "Chhindwara Institute of Medical Sciences, Chhindwara",
    "chikkamagaluru institute of medical sciences": "Chikkamagaluru Institute of Medical Sciences, Chikkamagaluru",
    "college government medical college alwar": "Government Medical College, Alwar",
    "amrita institute of medical science kochi": "Amrita School of Medicine, Elamakkara, Kochi"
}

INDIAN_STATES = {
    'andaman', 'nicobar', 'andhra', 'pradesh', 'arunachal', 'assam', 'bihar', 'chandigarh', 
    'chhattisgarh', 'dadra', 'nagar', 'haveli', 'daman', 'diu', 'delhi', 'goa', 'gujarat', 
    'haryana', 'himachal', 'jammu', 'kashmir', 'jharkhand', 'karnataka', 'kerala', 'ladakh', 
    'lakshadweep', 'madhya', 'maharashtra', 'manipur', 'meghalaya', 'mizoram', 'nagaland', 
    'odisha', 'orissa', 'puducherry', 'pondicherry', 'punjab', 'rajasthan', 'sikkim', 'tamil', 
    'nadu', 'telangana', 'tripura', 'uttar', 'uttarakhand', 'uttaranchal', 'west', 'bengal'
}

def clean_name(name):
    if not name: return ""
    n = name.lower()
    n = re.sub(r'(?<=\b[a-z])\.(?=[a-z]\b)', '', n)
    n = re.sub(r"[^\w\s]", " ", n)
    n = " ".join(n.split())
    while re.search(r'\b([a-z])\s+([a-z])\b', n):
        n = re.sub(r'\b([a-z])\s+([a-z])\b', r'\1\2', n)
    return " ".join(n.split())

def expand_abbreviations(text):
    t = clean_name(text)
    t = re.sub(r'\baiims\b', 'all india institute of medical sciences', t)
    t = re.sub(r'\bjipmer\b', 'jawaharlal institute of postgraduate medical education and research', t)
    t = re.sub(r"\bgovt\b|\bgov\b", "government", t)
    t = re.sub(r"\bmed\b", "medical", t)
    t = re.sub(r"\binst\b|\binstt\b|\binstitut\b", "institute", t)
    t = re.sub(r"\bcol\b|\bcollage\b|\bcoll\b", "college", t)
    t = re.sub(r"\bhosp\b|\bhospt\b", "hospital", t)
    t = re.sub(r"\bres\b", "research", t)
    t = re.sub(r'\bsciences\b|\bsci\b|\bsce\b', 'science', t)
    t = re.sub(r'\bcolleges\b', 'college', t)
    t = re.sub(r'\binstitutes\b', 'institute', t)
    t = re.sub(r'\bhospitals\b', 'hospital', t)
    t = re.sub(r"\bdeogarh\b", "deoghar", t)
    t = re.sub(r"\brai bareli\b|\braebarely\b", "raebareli", t)
    t = re.sub(r'\bsholapur\b', 'solapur', t)
    t = re.sub(r'\bbanglore\b', 'bangalore', t)
    t = re.sub(r'\bmangaluru\b', 'mangalore', t)
    t = re.sub(r'\bpuducherry\b|\bpondicherry\b', 'puducherry', t)
    t = re.sub(r'\belamkara\b', 'kochi', t)
    return " ".join(t.split())

def get_canonical_from_entry(entry):
    if isinstance(entry, dict):
        return entry.get("canonical")
    return entry

STOP_WORDS = {"government", "govt", "gmc", "medical", "college", "hospital", "institute", "institutes", "sciences", "research", "centre", "center", "and", "dr", "shri", "society", "trust", "memorial", "of", "for", "at", "in", "near", "post", "dist", "district", "road", "campus", "new", "no", "pin", "pincode", "india", "state", "autonomous"}

def get_tokens(name):
    clean = expand_abbreviations(name)
    tokens = [w for w in clean.split() if w not in STOP_WORDS and len(w) > 1]
    return set(tokens)

def build_normalized_cutoffs():
    print("Loading reference assets...")
    raw_cutoffs = json.load(open(raw_cutoffs_path, "r", encoding="utf-8"))
    alias_registry = json.load(open(alias_registry_path, "r", encoding="utf-8"))
    master_colleges = json.load(open(master_list_path, "r", encoding="utf-8"))
    master_quotas_cats = json.load(open(quotas_cats_path, "r", encoding="utf-8"))

    master_set = set(master_colleges)
    clean_master_map = {expand_abbreviations(m): m for m in master_colleges}
    master_tokens = {m: get_tokens(m) for m in master_colleges}

    # Build quota & category code lookups
    cat_map = {}
    for c in master_quotas_cats["categories"]:
        for v in c["raw_variations"]:
            cat_map[v.strip().lower()] = c["code"]

    quota_map = {}
    for q in master_quotas_cats["quotas"]:
        for v in q["raw_variations"]:
            quota_map[v.strip().lower()] = q["code"]

    def extract_master_cities(master_colleges):
        cities = set()
        EXCLUDE = {'hospital', 'research', 'institute', 'medical', 'college', 'sciences', 'and', 'the', 'of', 'for', 'society', 'trust', 'campus', 'centre', 'center', 'university', 'deemed', 'autonomous', 'govt', 'government', 'state', 'india', 'all', 'district', 'post', 'street', 'road', 'nagar', 'near', 'opp', 'opposite', 'behind', 'beside', 'block', 'building', 'complex', 'hall', 'nh', 'pin', 'pincode', 'dist', 'po', 'ps', 'taluk', 'taluka', 'distt', 'sector', 'marg', 'new', 'old', 'east', 'west', 'north', 'south', 'central', 'general', 'super', 'speciality', 'specialty', 'care', 'health', 'welfare', 'family', 'memorial', 'national', 'international', 'reg', 'regional', 'dental', 'ayurvedic', 'homeopathic', 'nursing', 'pharmacy'}.union(INDIAN_STATES)
        for m in master_colleges:
            parts = [p.strip() for p in m.split(',')]
            if len(parts) > 1:
                for p in parts[1:]:
                    clean_p = re.sub(r'[^a-zA-Z\s]', '', p).lower().strip()
                    if clean_p and clean_p not in EXCLUDE and len(clean_p) >= 3:
                        for w in clean_p.split():
                            if w not in EXCLUDE and len(w) >= 3 and not w.isdigit():
                                cities.add(w)
        return cities

    master_cities = extract_master_cities(master_colleges)

    def is_city_compatible(raw_str, candidate_m):
        r_low = raw_str.lower()
        c_low = candidate_m.lower()
        for city in master_cities:
            if city in r_low and city not in c_low:
                if city in ['pondicherry', 'puducherry'] and any(x in c_low for x in ['pondicherry', 'puducherry']): continue
                if city in ['mangalore', 'mangaluru'] and any(x in c_low for x in ['mangalore', 'mangaluru']): continue
                if city in ['kochi', 'elamkara'] and any(x in c_low for x in ['kochi', 'elamkara']): continue
                if city == 'puri' and ('dharmapuri' in r_low or 'tripura' in r_low or 'kanpur' in r_low): continue
                return False
        return True

    def resolve_single_string(s, full_raw_context=None):
        ctx = full_raw_context or s
        if s in master_set:
            if is_city_compatible(ctx, s):
                return s
        c_s = clean_name(s)
        if c_s in MANUAL_AIQ_OVERRIDES:
            cand = MANUAL_AIQ_OVERRIDES[c_s]
            if is_city_compatible(ctx, cand):
                return cand
        if c_s in alias_registry:
            cand = get_canonical_from_entry(alias_registry[c_s])
            if is_city_compatible(ctx, cand):
                return cand
        
        exp = expand_abbreviations(s)
        if exp in MANUAL_AIQ_OVERRIDES:
            cand = MANUAL_AIQ_OVERRIDES[exp]
            if is_city_compatible(ctx, cand):
                return cand
        if exp in alias_registry:
            cand = get_canonical_from_entry(alias_registry[exp])
            if is_city_compatible(ctx, cand):
                return cand
        if exp in clean_master_map:
            cand = clean_master_map[exp]
            if is_city_compatible(ctx, cand):
                return cand

        s_toks = get_tokens(s)
        if len(s_toks) >= 2:
            best_m = None
            best_score = 0
            for m, m_toks in master_tokens.items():
                if not m_toks:
                    continue
                common = s_toks.intersection(m_toks)
                score = len(common) / max(len(s_toks), len(m_toks))
                if len(common) >= 2 and score > best_score and score >= 0.55:
                    if is_city_compatible(ctx, m):
                        best_score = score
                        best_m = m
            if best_m:
                return best_m
        return None

    def resolve_college(raw_name):
        res = resolve_single_string(raw_name, full_raw_context=raw_name)
        if res:
            return res
        parts = [p.strip() for p in raw_name.split(",") if p.strip()]
        if parts:
            # Check individual parts (e.g., parts[0], parts[1], etc.) with full raw context
            for p in parts:
                res = resolve_single_string(p, full_raw_context=raw_name)
                if res:
                    return res
            # Check combined parts with full raw context
            if len(parts) > 1:
                res = resolve_single_string(f"{parts[0]}, {parts[1]}", full_raw_context=raw_name)
                if res:
                    return res
                res = resolve_single_string(f"{parts[1]}, {parts[0]}", full_raw_context=raw_name)
                if res:
                    return res
                res = resolve_single_string(f"{parts[0]} {parts[1]}", full_raw_context=raw_name)
                if res:
                    return res
                res = resolve_single_string(f"{parts[1]} {parts[0]}", full_raw_context=raw_name)
                if res:
                    return res
        return None

    normalized_groups = {}
    new_aliases_found = {}
    unmatched_raw_names = set()

    for item in raw_cutoffs:
        raw_c = item["college_name"]
        canon = resolve_college(raw_c)

        if not canon or not is_city_compatible(raw_c, canon):
            unmatched_raw_names.add(raw_c)
            continue

        clean_raw = clean_name(raw_c)
        if clean_raw not in alias_registry:
            new_aliases_found[clean_raw] = {
                "canonical": canon,
                "original_display": raw_c
            }
            alias_registry[clean_raw] = new_aliases_found[clean_raw]

        q_code = quota_map.get(item["quota"].strip().lower(), item["quota"])
        cat_code = cat_map.get(item["category"].strip().lower(), item["category"])
        course = item["course"]

        key = (canon, q_code, cat_code, course)
        if key not in normalized_groups:
            normalized_groups[key] = {
                "canonical_name": canon,
                "quota": q_code,
                "category": cat_code,
                "course": course,
                "r1_ranks": [],
                "r2_ranks": [],
                "r3_ranks": [],
                "all_ranks": [],
                "confirmed_seats": 0
            }

        grp = normalized_groups[key]
        if item.get("r1_opening_rank") is not None:
            grp["r1_ranks"].extend([item["r1_opening_rank"], item["r1_closing_rank"]])
            grp["all_ranks"].extend([item["r1_opening_rank"], item["r1_closing_rank"]])
        if item.get("r2_opening_rank") is not None:
            grp["r2_ranks"].extend([item["r2_opening_rank"], item["r2_closing_rank"]])
            grp["all_ranks"].extend([item["r2_opening_rank"], item["r2_closing_rank"]])
        if item.get("r3_opening_rank") is not None:
            grp["r3_ranks"].extend([item["r3_opening_rank"], item["r3_closing_rank"]])
            grp["all_ranks"].extend([item["r3_opening_rank"], item["r3_closing_rank"]])

        grp["r1_count"] = grp.get("r1_count", 0) + item.get("r1_allotted_count", 0)
        grp["r2_count"] = grp.get("r2_count", 0) + item.get("r2_allotted_count", 0)
        grp["r3_count"] = grp.get("r3_count", 0) + item.get("r3_allotted_count", 0)
        grp["confirmed_seats"] += item.get("confirmed_seats_allotted", 0)

    # Build final clean reference output array
    output_normalized = []
    for key, grp in normalized_groups.items():
        r1_o = min(grp["r1_ranks"]) if grp["r1_ranks"] else None
        r1_c = max(grp["r1_ranks"]) if grp["r1_ranks"] else None

        r2_o = min(grp["r2_ranks"]) if grp["r2_ranks"] else None
        r2_c = max(grp["r2_ranks"]) if grp["r2_ranks"] else None

        r3_o = min(grp["r3_ranks"]) if grp["r3_ranks"] else None
        r3_c = max(grp["r3_ranks"]) if grp["r3_ranks"] else None

        fin_o = min(grp["all_ranks"]) if grp["all_ranks"] else None
        fin_c = max(grp["all_ranks"]) if grp["all_ranks"] else None

        output_normalized.append({
            "college_name": grp["canonical_name"],
            "quota": grp["quota"],
            "category": grp["category"],
            "course": grp["course"],
            "r1_opening_rank": r1_o,
            "r1_closing_rank": r1_c,
            "r1_total_allotted": grp.get("r1_count", 0),
            "r2_opening_rank": r2_o,
            "r2_closing_rank": r2_c,
            "r2_total_allotted": grp.get("r2_count", 0),
            "r3_opening_rank": r3_o,
            "r3_closing_rank": r3_c,
            "r3_total_allotted": grp.get("r3_count", 0),
            "final_opening_rank": fin_o,
            "final_closing_rank": fin_c,
            "final_total_seats": grp["confirmed_seats"]
        })

    # Update alias-to-canonical.json
    if new_aliases_found:
        print(f"Adding {len(new_aliases_found)} new discovered aliases to alias-to-canonical.json...")
        with open(alias_registry_path, "w", encoding="utf-8") as f:
            json.dump(alias_registry, f, indent=2, ensure_ascii=False)

    print(f"Total raw cutoff groups processed: {len(raw_cutoffs)}")
    print(f"Total normalized master cutoff groups generated: {len(output_normalized)}")
    print(f"Unmatched raw names count: {len(unmatched_raw_names)}")

    # Save to reference/normalized_college_cutoffs.json
    with open(out_ref_path, "w", encoding="utf-8") as f:
        json.dump(output_normalized, f, indent=2, ensure_ascii=False)
    print(f"Saved normalized reference cutoffs to {out_ref_path}")

    # Build public/data/ug_colleges_aiq_mapping.json for Frontend CutoffExplorer
    college_cutoffs_lookup = {}
    for item in output_normalized:
        c_name = item["college_name"]
        if c_name not in college_cutoffs_lookup:
            college_cutoffs_lookup[c_name] = []
        college_cutoffs_lookup[c_name].append(item)

    # Load master-locations-reference.json for location metadata resolution
    loc_ref_path = os.path.join(workspace_dir, "reference", "master-locations-reference.json")
    loc_ref = json.load(open(loc_ref_path, "r", encoding="utf-8")) if os.path.exists(loc_ref_path) else {"official_states": [], "state_aliases": {}, "city_registry": {}}

    official_states_set = set(loc_ref.get("official_states", []))
    state_alias_map = loc_ref.get("state_aliases", {})
    city_registry = loc_ref.get("city_registry", {})

    def resolve_location(c_name):
        c_lower = c_name.lower().strip()
        parts = [p.strip() for p in c_name.split(",") if p.strip()]

        derived_city = parts[-1] if len(parts) > 1 else ""
        derived_state = ""

        # Check city registry
        for key, info in city_registry.items():
            if re.search(r'\b' + re.escape(key) + r'\b', c_lower):
                derived_city = info["city_name"]
                if not derived_state:
                    derived_state = info["state"]
                break

        # Check state aliases and official states if state not yet resolved
        if not derived_state:
            if parts:
                last_lower = parts[-1].lower()
                if parts[-1] in official_states_set:
                    derived_state = parts[-1]
                elif last_lower in state_alias_map:
                    derived_state = state_alias_map[last_lower]

        if not derived_state:
            for alias, target_st in state_alias_map.items():
                if re.search(r'\b' + re.escape(alias) + r'\b', c_lower):
                    derived_state = target_st
                    break

        if not derived_state:
            for st in official_states_set:
                if re.search(r'\b' + re.escape(st.lower()) + r'\b', c_lower):
                    derived_state = st
                    break

        return derived_city, derived_state

    # Extract unique canonical college names directly from input cutoff dataset, sorted alphabetically
    unique_input_canonical_colleges = sorted(list(college_cutoffs_lookup.keys()), key=lambda x: x.lower())

    # Load master colleges_details.json for accurate master college_id & college_type (INI, Govt, Deemed, Private)
    details_path = os.path.join(workspace_dir, "public", "data", "colleges_details.json")
    col_details = json.load(open(details_path, "r", encoding="utf-8")) if os.path.exists(details_path) else {}
    
    details_by_name = {}
    for cid, d_item in col_details.items():
        c_n = d_item.get("college_name", "").lower().strip()
        if c_n: details_by_name[c_n] = d_item
        for a in d_item.get("aliases", []):
            details_by_name[str(a).lower().strip()] = d_item
        for c in d_item.get("canonical_names", []):
            details_by_name[str(c).lower().strip()] = d_item

    public_mapping = []
    for idx, c_name in enumerate(unique_input_canonical_colleges):
        cutoffs = college_cutoffs_lookup[c_name]
        city, state = resolve_location(c_name)

        matched_det = details_by_name.get(c_name.lower().strip())
        real_cid = matched_det.get("college_id") if matched_det else f"ug_aiq_{idx+1:03d}"
        real_type = matched_det.get("college_type") if (matched_det and matched_det.get("college_type")) else ("Deemed" if "Deemed" in c_name or "Deemed" in (cutoffs[0]["quota"] if cutoffs else "") else ("Private" if "Private" in c_name else "Government"))

        public_mapping.append({
            "college_id": real_cid,
            "college_name": c_name,
            "city": city,
            "state": state,
            "college_type": real_type,
            "counseling_route": "AIQ",
            "matched_in_aiq": True,
            "aiq_college_name": c_name,
            "mcc_status": "Matched",
            "aiq_cutoffs_raw": cutoffs
        })

    os.makedirs(os.path.dirname(out_public_path), exist_ok=True)
    with open(out_public_path, "w", encoding="utf-8") as f:
        json.dump(public_mapping, f, indent=2, ensure_ascii=False)

    print(f"Saved public UI mapping to {out_public_path} ({len(public_mapping)} colleges strictly from input allotment file).")

if __name__ == "__main__":
    build_normalized_cutoffs()

