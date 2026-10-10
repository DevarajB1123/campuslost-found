import re
from datetime import datetime

STOP_WORDS = {
    'a', 'about', 'above', 'after', 'again', 'against', 'all', 'am', 'an', 'and',
    'any', 'are', 'aren', 'as', 'at', 'be', 'because', 'been', 'before', 'being',
    'below', 'between', 'both', 'but', 'by', 'can', 'could', 'did', 'do', 'does',
    'doing', 'don', 'down', 'during', 'each', 'few', 'for', 'from', 'further', 'had',
    'has', 'have', 'having', 'he', 'her', 'here', 'hers', 'herself', 'him', 'himself',
    'his', 'how', 'i', 'if', 'in', 'into', 'is', 'it', 'its', 'itself', 'just', 'me',
    'more', 'most', 'my', 'myself', 'no', 'nor', 'not', 'now', 'of', 'off', 'on',
    'once', 'only', 'or', 'other', 'our', 'ours', 'ourselves', 'out', 'over', 'own',
    's', 'same', 'she', 'should', 'so', 'some', 'such', 't', 'than', 'that', 'the',
    'their', 'theirs', 'them', 'themselves', 'then', 'there', 'these', 'they', 'this',
    'those', 'through', 'to', 'too', 'under', 'until', 'up', 'very', 'was', 'wasn',
    'we', 'were', 'what', 'when', 'where', 'which', 'while', 'who', 'whom', 'why',
    'will', 'with', 'won', 'would', 'lost', 'found', 'please', 'help', 'item', 'campus'
}

def tokenize(text):
    """Normalize text into lowercase alphanumeric keywords excluding stop words."""
    if not text:
        return set()
    words = re.findall(r'[a-zA-Z0-9]+', text.lower())
    return {w for w in words if len(w) > 2 and w not in STOP_WORDS}

def calculate_date_proximity_score(date_str_1, date_str_2):
    """Award points based on how close in time the two events occurred."""
    if not date_str_1 or not date_str_2:
        return 5
    try:
        d1 = datetime.strptime(date_str_1[:10], "%Y-%m-%d")
        d2 = datetime.strptime(date_str_2[:10], "%Y-%m-%d")
        diff_days = abs((d1 - d2).days)
        if diff_days <= 1:
            return 20
        elif diff_days <= 3:
            return 16
        elif diff_days <= 7:
            return 12
        elif diff_days <= 14:
            return 8
        elif diff_days <= 30:
            return 4
        else:
            return 0
    except Exception:
        return 5

def calculate_text_similarity(tokens1, tokens2):
    """Compute Jaccard token overlap between two sets of keywords (max 20 points)."""
    if not tokens1 or not tokens2:
        return 0
    intersection = tokens1.intersection(tokens2)
    union = tokens1.union(tokens2)
    if not union:
        return 0
    ratio = len(intersection) / len(union)
    return round(ratio * 20)

def compute_match_score(item_a, item_b):
    """
    Calculate similarity score between two items (0 to 100%).
    Takes dict or sqlite3.Row for item_a and item_b.
    """
    score = 0
    reasons = []

    # 1. Category check (35 points)
    cat_a = item_a['category'] if isinstance(item_a, dict) else item_a['category']
    cat_b = item_b['category'] if isinstance(item_b, dict) else item_b['category']
    if cat_a == cat_b:
        score += 35
        reasons.append(f"Identical Category: {cat_a}")
    else:
        # Check if words overlap in category
        cat_tokens_a = tokenize(cat_a)
        cat_tokens_b = tokenize(cat_b)
        if cat_tokens_a.intersection(cat_tokens_b):
            score += 15
            reasons.append("Related Category")

    # 2. Location check (25 points)
    loc_a = (item_a['location'] if isinstance(item_a, dict) else item_a['location']).strip().lower()
    loc_b = (item_b['location'] if isinstance(item_b, dict) else item_b['location']).strip().lower()
    if loc_a == loc_b:
        score += 25
        reasons.append(f"Exact Location Match: {item_a['location']}")
    else:
        loc_tokens_a = tokenize(loc_a)
        loc_tokens_b = tokenize(loc_b)
        if loc_tokens_a.intersection(loc_tokens_b):
            score += 18
            reasons.append("Same Campus Zone / Nearby Building")

    # 3. Date proximity (20 points max)
    date_a = item_a['item_date'] if isinstance(item_a, dict) else item_a['item_date']
    date_b = item_b['item_date'] if isinstance(item_b, dict) else item_b['item_date']
    date_score = calculate_date_proximity_score(date_a, date_b)
    score += date_score
    if date_score >= 12:
        reasons.append("Reported within few days of each other")

    # 4. Keyword similarity in Title & Description (20 points max)
    text_a = f"{item_a['title']} {item_a['description']}"
    text_b = f"{item_b['title']} {item_b['description']}"
    title_a_tokens = tokenize(item_a['title'])
    title_b_tokens = tokenize(item_b['title'])

    # Title match bonus
    title_overlap = title_a_tokens.intersection(title_b_tokens)
    text_tokens_a = tokenize(text_a)
    text_tokens_b = tokenize(text_b)
    text_score = calculate_text_similarity(text_tokens_a, text_tokens_b)

    if title_overlap:
        text_score = min(20, text_score + len(title_overlap) * 5)
        reasons.append(f"Key title terms matched: {', '.join(list(title_overlap)[:3])}")

    score += text_score

    # Cap at 100
    final_score = min(100, max(0, score))
    return final_score, reasons

def find_smart_matches(target_item, candidate_items, min_threshold=45):
    """
    Find matching items of the complementary type (LOST vs FOUND).
    Returns list of dicts with item details, match_score, and reasons.
    """
    target_type = target_item['type']
    opposite_type = 'FOUND' if target_type == 'LOST' else 'LOST'

    matches = []
    for candidate in candidate_items:
        # Candidate must be opposite type and open/active
        cand_type = candidate['type']
        cand_status = candidate['status']
        if cand_type != opposite_type or cand_status not in ('OPEN', 'CLAIM_PENDING'):
            continue
        if candidate['id'] == target_item['id']:
            continue

        score, reasons = compute_match_score(target_item, candidate)
        if score >= min_threshold:
            matches.append({
                'item': candidate,
                'match_score': score,
                'reasons': reasons
            })

    # Sort descending by match_score
    matches.sort(key=lambda x: x['match_score'], reverse=True)
    return matches

def detect_potential_duplicates(new_item, existing_items, threshold=70):
    """
    Check if a newly entered item is an accidental duplicate of an existing item
    of the SAME type.
    """
    duplicates = []
    for item in existing_items:
        if item['type'] != new_item['type']:
            continue
        if 'id' in new_item and item['id'] == new_item['id']:
            continue
        score, reasons = compute_match_score(new_item, item)
        if score >= threshold:
            duplicates.append({
                'item': item,
                'score': score,
                'reasons': reasons
            })
    duplicates.sort(key=lambda x: x['score'], reverse=True)
    return duplicates
