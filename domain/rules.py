from typing import Any, Dict, List

from i18n import tr

MIN_INPUT_LENGTH = 20

FAMILY_MIN_SCORE_STRONG = 3
FAMILY_MIN_SCORE_WEAK = 2

SUBFAMILY_MIN_SCORE_STRONG = 2
SUBFAMILY_MIN_SCORE_WEAK = 1

FAMILY_CONFIDENCE_STRONG = 0.75
FAMILY_CONFIDENCE_WEAK = 0.50


def should_stop_for_invalid_input(user_input: str) -> bool:
    return len((user_input or "").strip()) < MIN_INPUT_LENGTH


def estimate_family_confidence(family_scores: List[Dict[str, Any]]) -> float:
    if not family_scores:
        return 0.0

    top_score = family_scores[0].get("score", 0)
    second_score = family_scores[1].get("score", 0) if len(family_scores) > 1 else 0

    if top_score <= 0:
        return 0.0

    if top_score >= 4 and second_score == 0:
        return 0.95
    if top_score >= 3 and top_score > second_score:
        return 0.85
    if top_score >= 2 and top_score > second_score:
        return 0.70
    if top_score >= 2 and top_score == second_score:
        return 0.55
    if top_score == 1:
        return 0.40

    return 0.30


def lock_family(family_scores: List[Dict[str, Any]]) -> Dict[str, Any]:
    if not family_scores:
        return {
            "status": "stop",
            "reason": "Aucune famille détectée"
        }

    top = family_scores[0]
    confidence = estimate_family_confidence(family_scores)

    if top["score"] >= FAMILY_MIN_SCORE_STRONG and confidence >= FAMILY_CONFIDENCE_STRONG:
        return {
            "status": "locked",
            "famille": top["famille"],
            "confidence": confidence,
            "matched_keywords": top.get("matched_keywords", [])
        }

    if top["score"] >= FAMILY_MIN_SCORE_WEAK and confidence >= FAMILY_CONFIDENCE_WEAK:
        return {
            "status": "uncertain",
            "familles_candidates": [f["famille"] for f in family_scores[:2]],
            "confidence": confidence,
            "matched_keywords": top.get("matched_keywords", [])
        }

    return {
        "status": "stop",
        "reason": "Famille métier non identifiable avec assez de confiance",
        "confidence": confidence,
        "matched_keywords": top.get("matched_keywords", [])
    }


def estimate_subfamily_confidence(subfamily_scores: List[Dict[str, Any]]) -> float:
    if not subfamily_scores:
        return 0.0

    top_score = subfamily_scores[0].get("score", 0)
    second_score = subfamily_scores[1].get("score", 0) if len(subfamily_scores) > 1 else 0

    if top_score <= 0:
        return 0.0

    if top_score >= 3 and second_score == 0:
        return 0.95
    if top_score >= 2 and top_score > second_score:
        return 0.85
    if top_score >= 1 and top_score > second_score:
        return 0.70
    if top_score >= 1 and top_score == second_score:
        return 0.55

    return 0.30


def lock_subfamily(subfamily_scores: List[Dict[str, Any]]) -> Dict[str, Any]:
    if not subfamily_scores:
        return {
            "status": "stop",
            "reason": "Aucune sous-famille détectée"
        }

    top = subfamily_scores[0]
    confidence = estimate_subfamily_confidence(subfamily_scores)

    if top["score"] >= SUBFAMILY_MIN_SCORE_STRONG:
        return {
            "status": "locked",
            "sous_famille": top["sous_famille"],
            "confidence": confidence,
            "matched_keywords": top.get("matched_keywords", [])
        }

    if top["score"] >= SUBFAMILY_MIN_SCORE_WEAK:
        return {
            "status": "uncertain",
            "sous_familles_candidates": [f["sous_famille"] for f in subfamily_scores[:2]],
            "confidence": confidence,
            "matched_keywords": top.get("matched_keywords", [])
        }

    return {
        "status": "stop",
        "reason": "Sous-famille non identifiable avec assez de confiance",
        "confidence": confidence,
        "matched_keywords": top.get("matched_keywords", [])
    }