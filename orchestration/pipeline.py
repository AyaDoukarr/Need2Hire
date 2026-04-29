from config import STRICT_INVALID_MESSAGE
from domain.matching import score_families, score_subfamilies
from domain.scoring import compute_qualification_score, compute_qualification_confidence
from domain.rules import (
    should_stop_for_invalid_input,
    lock_family,
    lock_subfamily,
    tr as tr_rules,
)
from data.data_layer import get_subfamily_names
from i18n import tr
from agents.family_router_agent import run_family_router
from agents.subfamily_router_agent import run_subfamily_router
from agents.extractor_agent import run_extraction
from agents.market_benchmark_agent import run_market_benchmark


def run_pipeline(user_input: str, lang: str = "fr"):
    user_input = (user_input or "").strip()

    # 1. Validation simple
    if should_stop_for_invalid_input(user_input):
        return {
            "status": "stop",
            "error": STRICT_INVALID_MESSAGE
        }

    # 2. Pré-matching Python sur les familles
    family_scores = score_families(user_input)
    family_decision = lock_family(family_scores)

    locked_family = None
    family_router_output = None

    if family_decision["status"] == "locked":
        locked_family = family_decision["famille"]

    elif family_decision["status"] == "uncertain":
        # 3. Fallback LLM pour confirmer la famille
        family_router_output = run_family_router(user_input)

        famille_detectee = family_router_output.get("famille_detectee", "indeterminee")
        confiance = float(family_router_output.get("confiance", 0))

        if famille_detectee == "indeterminee" or confiance < 0.5:
            return {
                "status": "stop",
                "error": tr("ambiguous_need_error", lang),
                "family_scores": family_scores,
                "family_router_output": family_router_output,
            }

        locked_family = famille_detectee

    else:
        return {
            "status": "stop",
            "error": STRICT_INVALID_MESSAGE,
            "family_scores": family_scores,
        }

    # 4. Pré-matching Python sur les sous-familles de la famille verrouillée
    subfamily_scores = score_subfamilies(user_input, locked_family)
    subfamily_decision = lock_subfamily(subfamily_scores)

    locked_subfamily = "Non précisé"
    subfamily_router_output = None

    if subfamily_decision["status"] == "locked":
        locked_subfamily = subfamily_decision["sous_famille"]

    elif subfamily_decision["status"] == "uncertain":
        subfamilies = get_subfamily_names(locked_family)

        if subfamilies:
            subfamily_router_output = run_subfamily_router(
                user_input=user_input,
                job_family=locked_family,
                subfamilies=subfamilies,
            )

            sous_famille_detectee = subfamily_router_output.get("sous_famille_detectee", "indeterminee")
            confiance = float(subfamily_router_output.get("confiance", 0))

            if sous_famille_detectee != "indeterminee" and confiance >= 0.5:
                locked_subfamily = sous_famille_detectee

    # 5. Extraction structurée
    extraction_result = run_extraction(
        user_input=user_input,
        job_family=locked_family,
        job_subfamily=locked_subfamily,
        lang=lang,
    )

    # 6. Benchmark marché (optionnel - ne doit pas bloquer le pipeline)
    market_benchmark = None
    fiche_poste = extraction_result.get("fiche_de_poste_axa", {}) if extraction_result else {}
    
    if fiche_poste and fiche_poste.get("intitule_poste"):
        try:
            market_benchmark = run_market_benchmark(
                job_family=locked_family,
                job_subfamily=locked_subfamily,
                fiche_poste=fiche_poste,
                lang=lang,
            )
        except Exception:
            # En cas d'échec, on continue sans benchmark
            market_benchmark = None

    # 7. KPI déterministes
    computed_score = compute_qualification_score(
        result=extraction_result,
        source_text=user_input,
        lang=lang,
    )

    confidence = compute_qualification_confidence(
        result=extraction_result,
        computed_score=computed_score,
        lang=lang,
    )

    return {
        "status": "success",
        "input_text": user_input,
        "family": locked_family,
        "subfamily": locked_subfamily,
        "family_scores": family_scores,
        "subfamily_scores": subfamily_scores,
        "family_decision": family_decision,
        "subfamily_decision": subfamily_decision,
        "family_router_output": family_router_output,
        "subfamily_router_output": subfamily_router_output,
        "result": extraction_result,
        "score": computed_score,
        "confidence": confidence,
        "market_benchmark": market_benchmark,
    }