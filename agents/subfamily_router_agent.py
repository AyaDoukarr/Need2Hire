from services.llm_service import call_llm_json


def build_subfamily_router_prompt(job_family: str, subfamilies: list[str]) -> str:
    subfamilies_text = "\n".join(f"- {sub}" for sub in subfamilies) if subfamilies else "- Non précisé"

    return f"""
Tu es un classificateur RH spécialisé dans la qualification d’un besoin de recrutement.

Ta mission :
Identifier la sous-famille métier AXA la plus probable à partir d’un besoin de recrutement.

Contexte :
- Famille métier déjà verrouillée : {job_family}

Tu dois choisir uniquement parmi les sous-familles suivantes :
{subfamilies_text}

Règles :
- Réponds uniquement avec un JSON valide.
- N'ajoute aucun texte avant ou après.
- Ne choisis qu'une seule sous-famille métier.
- Si le besoin est trop ambigu, retourne "indeterminee".
- Le score de confiance doit être compris entre 0 et 1.
- Les raisons doivent être courtes, concrètes et basées sur les mots-clés ou éléments visibles dans le texte.
- N'invente jamais une sous-famille absente de la liste.

Réponds exactement avec cette structure :

{{
  "sous_famille_detectee": "string",
  "confiance": 0.0,
  "raisons": ["string"]
}}
"""


def run_subfamily_router(user_input: str, job_family: str, subfamilies: list[str]):
    prompt = build_subfamily_router_prompt(job_family, subfamilies)
    return call_llm_json(prompt, user_input, temperature=0)