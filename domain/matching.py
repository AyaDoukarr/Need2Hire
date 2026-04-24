from typing import Any, Dict, List

from data.data_layer import (
    get_family_names,
    get_family_keywords,
    get_subfamily_names,
    get_subfamily_keywords,
)


def normalize_text(text: str) -> str:
    return (text or "").strip().lower()


def keyword_in_text(keyword: str, text: str) -> bool:
    return normalize_text(keyword) in normalize_text(text)


def score_family(user_text: str, job_family: str) -> Dict[str, Any]:
    text = normalize_text(user_text)
    keywords = get_family_keywords(job_family)

    matched_keywords = []
    score = 0

    for kw in keywords:
        if kw and kw.lower() in text:
            matched_keywords.append(kw)
            score += 1

    return {
        "famille": job_family,
        "score": score,
        "matched_keywords": matched_keywords,
    }


def score_families(user_text: str) -> List[Dict[str, Any]]:
    results = []

    for family in get_family_names():
        result = score_family(user_text, family)
        results.append(result)

    results.sort(key=lambda x: x["score"], reverse=True)
    return results


def score_subfamily(user_text: str, job_family: str, job_subfamily: str) -> Dict[str, Any]:
    text = normalize_text(user_text)
    keywords = get_subfamily_keywords(job_family, job_subfamily)

    matched_keywords = []
    score = 0

    for kw in keywords:
        if kw and kw.lower() in text:
            matched_keywords.append(kw)
            score += 1

    return {
        "sous_famille": job_subfamily,
        "score": score,
        "matched_keywords": matched_keywords,
    }


def score_subfamilies(user_text: str, job_family: str) -> List[Dict[str, Any]]:
    results = []

    for subfamily in get_subfamily_names(job_family):
        result = score_subfamily(user_text, job_family, subfamily)
        results.append(result)

    results.sort(key=lambda x: x["score"], reverse=True)
    return results