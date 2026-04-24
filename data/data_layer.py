import csv
import json
from pathlib import Path
from typing import Any, Dict, List

from config import TAXONOMY_CSV_PATH, REFERENCE_CSV_PATH, IT_REFERENCE_CSV_PATH

FAMILIES_JSON_PATH = "data/familles_metiers_axa.json"


def load_csv_rows(csv_path: str) -> List[Dict[str, Any]]:
    path = Path(csv_path)

    if not path.is_absolute():
        path = Path(__file__).resolve().parent.parent / csv_path

    print("Lecture CSV:", path)

    if not path.exists():
        print("FICHIER INTROUVABLE:", path)
        return []

    try:
        with open(path, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            print("NB LIGNES:", len(rows))
            return rows
    except Exception as e:
        print("ERREUR LECTURE CSV:", path, e)
        return []

def load_json_file(json_path: str) -> Dict[str, Any]:
    path = Path(json_path)
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


TAXONOMY_ROWS = load_csv_rows(TAXONOMY_CSV_PATH)
REFERENCE_ROWS = load_csv_rows(REFERENCE_CSV_PATH)
IT_REFERENCE_ROWS = load_csv_rows(IT_REFERENCE_CSV_PATH)
FAMILIES_DATA = load_json_file(FAMILIES_JSON_PATH)


def normalize_family_label(label: str) -> str:
    value = (label or "").strip().lower()
    mapping = {
        "it, data & transformation": "it / data & transformation",
        "it / data & transformation": "it / data & transformation",
        "actuariat / assurance": "actuariat / assurance",
        "marketing / communication / rse": "marketing / communication / rse",
        "juridique / audit / conformité": "juridique / audit / conformité",
        "ressources humaines": "ressources humaines",
        "gestion d'actifs": "gestion d'actifs",
        "commercial salarié": "commercial salarié",
        "commercial entrepreneur": "commercial entrepreneur",
        "finance": "finance",
        "banque": "banque",
        "actuariat": "actuariat",
        "générique": "générique",
    }
    return mapping.get(value, value)


def normalize_subfamily_label(label: str) -> str:
    return (label or "").strip().lower()


def text_matches_family_or_subfamily(text: str, family: str, subfamily: str) -> bool:
    txt = normalize_subfamily_label(text)
    fam = normalize_family_label(family)
    sub = normalize_subfamily_label(subfamily)
    return (fam and fam in txt) or (sub and sub not in ["", "non précisé"] and sub in txt)


def build_job_families_from_taxonomy(rows: List[Dict[str, Any]]) -> List[str]:
    families = sorted({
        (r.get("famille_metier_axa", "") or "").strip()
        for r in rows
        if (r.get("famille_metier_axa", "") or "").strip()
    })
    return ["Générique"] + families


def build_subfamilies_map(rows: List[Dict[str, Any]]) -> Dict[str, List[str]]:
    mapping: Dict[str, List[str]] = {}
    for row in rows:
        fam = (row.get("famille_metier_axa", "") or "").strip()
        sub = (row.get("sous_famille_metier", "") or "").strip()
        if not fam or not sub:
            continue
        mapping.setdefault(fam, [])
        if sub not in mapping[fam]:
            mapping[fam].append(sub)

    for fam in mapping:
        mapping[fam] = sorted(mapping[fam])

    return mapping


JOB_FAMILIES = build_job_families_from_taxonomy(TAXONOMY_ROWS)
JOB_SUBFAMILIES = build_subfamilies_map(TAXONOMY_ROWS)


def filter_taxonomy_rows(job_family: str, job_subfamily: str) -> List[Dict[str, Any]]:
    if not TAXONOMY_ROWS:
        return []

    if job_family == "Générique":
        return TAXONOMY_ROWS[:8]

    results = []
    for row in TAXONOMY_ROWS:
        fam = (row.get("famille_metier_axa", "") or "").strip()
        sub = (row.get("sous_famille_metier", "") or "").strip()
        if fam == job_family and (job_subfamily in ("Non précisé", "") or sub == job_subfamily):
            results.append(row)

    return results[:10]


def extract_reference_examples(job_family: str, job_subfamily: str, max_examples: int = 6) -> List[str]:
    examples: List[str] = []
    normalized_family = normalize_family_label(job_family)
    normalized_subfamily = normalize_subfamily_label(job_subfamily)

    for row in REFERENCE_ROWS:
        fam = normalize_family_label(row.get("famille_metier_axa", ""))
        sub = normalize_subfamily_label(row.get("sous_famille_metier", ""))
        title = (row.get("intitule_poste", "") or "").strip()

        if fam == normalized_family and (normalized_subfamily in ["", "non précisé"] or sub == normalized_subfamily) and title:
            examples.append(title)

    if normalized_family == "it / data & transformation":
        for row in IT_REFERENCE_ROWS:
            title = (row.get("intitule_poste", "") or "").strip()
            specialite = row.get("specialite_it", "") or ""
            mots_cles = row.get("mots_cles", "") or ""

            if normalized_subfamily in ["", "non précisé"]:
                if title:
                    examples.append(title)
            else:
                if (
                    text_matches_family_or_subfamily(specialite, job_family, job_subfamily)
                    or text_matches_family_or_subfamily(title, job_family, job_subfamily)
                    or text_matches_family_or_subfamily(mots_cles, job_family, job_subfamily)
                ) and title:
                    examples.append(title)

    return sorted(set(examples))[:max_examples]


def build_taxonomy_summary(job_family: str, job_subfamily: str) -> str:
    refs = filter_taxonomy_rows(job_family, job_subfamily)
    detailed_examples = extract_reference_examples(job_family, job_subfamily)

    if not refs and not detailed_examples:
        return "Aucune entrée de taxonomie trouvée."

    blocks = []
    for i, row in enumerate(refs, 1):
        blocks.append(
            f"Référence métier {i}\n"
            f"- Famille métier AXA : {row.get('famille_metier_axa', 'Non précisé')}\n"
            f"- Sous-famille métier : {row.get('sous_famille_metier', 'Non précisé')}\n"
            f"- Exemples de postes : {row.get('exemples_postes', 'Non précisé')}\n"
            f"- Mots-clés métier : {row.get('mots_cles', 'Non précisé')}\n"
        )

    if detailed_examples:
        blocks.append("Exemples de postes issus du référentiel détaillé :\n- " + "\n- ".join(detailed_examples))

    return "\n\n".join(blocks)


def extract_taxonomy_keywords(job_family: str, job_subfamily: str) -> List[str]:
    refs = filter_taxonomy_rows(job_family, job_subfamily)
    items: List[str] = []

    for row in refs:
        raw = row.get("mots_cles", "") or ""
        items.extend([x.strip() for x in raw.split(";") if x.strip()])

    return sorted(set(items))


def extract_reference_competences(job_family: str, job_subfamily: str) -> List[str]:
    skills: List[str] = []
    normalized_family = normalize_family_label(job_family)
    normalized_subfamily = normalize_subfamily_label(job_subfamily)

    for row in REFERENCE_ROWS:
        fam = normalize_family_label(row.get("famille_metier_axa", ""))
        sub = normalize_subfamily_label(row.get("sous_famille_metier", ""))

        if fam == normalized_family and (normalized_subfamily in ["", "non précisé"] or sub == normalized_subfamily):
            raw = row.get("competences_techniques", "") or ""
            skills.extend([x.strip() for x in raw.split(";") if x.strip()])

    if normalized_family == "it / data & transformation":
        for row in IT_REFERENCE_ROWS:
            specialite = row.get("specialite_it", "") or ""
            intitule = row.get("intitule_poste", "") or ""
            mots_cles = row.get("mots_cles", "") or ""

            if normalized_subfamily in ["", "non précisé"]:
                raw = row.get("competences_techniques", "") or ""
                skills.extend([x.strip() for x in raw.split(";") if x.strip()])
            else:
                if (
                    text_matches_family_or_subfamily(specialite, job_family, job_subfamily)
                    or text_matches_family_or_subfamily(intitule, job_family, job_subfamily)
                    or text_matches_family_or_subfamily(mots_cles, job_family, job_subfamily)
                ):
                    raw = row.get("competences_techniques", "") or ""
                    skills.extend([x.strip() for x in raw.split(";") if x.strip()])

    return sorted(set(skills))


def extract_reference_questions(job_family: str, job_subfamily: str) -> List[str]:
    questions = [
        "Quel est l'intitulé exact du poste ?",
        "Quelles sont les missions principales ?",
        "Quelles compétences sont obligatoires ?",
        "Quel niveau d'expérience est attendu ?",
        "Quel est le contexte d'équipe ou d'organisation ?",
        "Quelle localisation ou quel périmètre géographique est visé ?",
        "Quelles compétences sont indispensables et lesquelles sont seulement souhaitables ?",
    ]

    extras = {
        "it / data & transformation": [
            "Le poste est-il orienté data, développement, architecture, produit, qualité, sécurité, cloud ou transformation ?",
            "Quels environnements techniques, outils ou pratiques agiles sont attendus ?",
        ],
        "finance": [
            "Le besoin porte-t-il sur audit, comptabilité, contrôle de gestion, contrôle interne ou risk management ?",
        ],
        "banque": [
            "Quels produits bancaires ou types de financement doivent être maîtrisés ?",
        ],
    }

    questions.extend(extras.get(normalize_family_label(job_family), []))

    if job_subfamily and job_subfamily != "Non précisé":
        questions.append(f"Quelles spécificités métier liées à '{job_subfamily}' doivent être absolument couvertes ?")

    return questions


# -----------------------------
# NOUVELLES FONCTIONS POUR LE JSON MÉTIER
# -----------------------------

def get_families_data() -> Dict[str, Any]:
    return FAMILIES_DATA


def get_family_names() -> List[str]:
    familles = FAMILIES_DATA.get("familles_metiers", {})
    return list(familles.keys())


def get_family_data(job_family: str) -> Dict[str, Any]:
    familles = FAMILIES_DATA.get("familles_metiers", {})
    return familles.get(job_family, {})


def get_family_keywords(job_family: str) -> List[str]:
    family_data = get_family_data(job_family)
    return family_data.get("mots_cles_famille", [])


def get_subfamily_names(job_family: str) -> List[str]:
    family_data = get_family_data(job_family)
    subfamilies = family_data.get("sous_familles", {})
    return list(subfamilies.keys())


def get_subfamily_data(job_family: str, job_subfamily: str) -> Dict[str, Any]:
    family_data = get_family_data(job_family)
    subfamilies = family_data.get("sous_familles", {})
    return subfamilies.get(job_subfamily, {})


def get_subfamily_keywords(job_family: str, job_subfamily: str) -> List[str]:
    subfamily_data = get_subfamily_data(job_family, job_subfamily)
    return subfamily_data.get("mots_cles", [])


def get_subfamily_examples(job_family: str, job_subfamily: str) -> List[str]:
    subfamily_data = get_subfamily_data(job_family, job_subfamily)
    return subfamily_data.get("exemples_postes", [])

print("TAXONOMY_CSV_PATH =", TAXONOMY_CSV_PATH)
print("REFERENCE_CSV_PATH =", REFERENCE_CSV_PATH)
print("IT_REFERENCE_CSV_PATH =", IT_REFERENCE_CSV_PATH)
print("TAXONOMY_ROWS =", len(TAXONOMY_ROWS))
print("REFERENCE_ROWS =", len(REFERENCE_ROWS))
print("IT_REFERENCE_ROWS =", len(IT_REFERENCE_ROWS))