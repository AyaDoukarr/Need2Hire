from services.llm_service import call_llm_json

PROMPT = """
Tu es un classificateur RH.

Ta mission :
Identifier la famille métier AXA la plus probable à partir d’un besoin de recrutement.

Tu dois choisir uniquement parmi :
- IT / Data & Transformation
- Banque
- Finance
- Actuariat / Assurance
- Marketing / Communication / RSE
- Commercial Salarié
- Commercial Entrepreneur
- Ressources Humaines
- Juridique / Audit / Conformité

Règles :
- Réponds uniquement avec un JSON valide.
- N'ajoute aucun texte avant ou après.
- Ne choisis qu'une seule famille métier.
- Si le besoin est trop ambigu, retourne "indeterminee".
- Le score de confiance doit être compris entre 0 et 1.
- Les raisons doivent être courtes, concrètes et basées sur les mots-clés ou éléments visibles dans le texte.

Réponds exactement avec cette structure :

{
  "famille_detectee": "string",
  "confiance": 0.0,
  "raisons": ["string"]
}
"""


def run_family_router(user_input: str):
    return call_llm_json(PROMPT, user_input, temperature=0)