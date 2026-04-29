from pathlib import Path
import os
from dotenv import load_dotenv
from openai import OpenAI

BASE_DIR = Path(__file__).resolve().parent
env_path = BASE_DIR / ".env"
load_dotenv(env_path)

APP_TITLE = "SQORUS | IA RH Recrutement"

TEXT_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
AUDIO_MODEL = os.getenv("GROQ_AUDIO_MODEL", "whisper-large-v3-turbo")
API_KEY = os.getenv("GROQ_API_KEY")

_STRICT_INVALID_MESSAGE_BASE = "Veuillez préciser un besoin métier réel."
STRICT_INVALID_MESSAGE = "⚠️ " + _STRICT_INVALID_MESSAGE_BASE

TAXONOMY_CSV_PATH = str(BASE_DIR / "data" / "axa_taxonomie_metiers.csv")
REFERENCE_CSV_PATH = str(BASE_DIR / "data" / "axa_referentiel_metiers.csv")
IT_REFERENCE_CSV_PATH = str(BASE_DIR / "data" / "axa_fiches_poste_it_enrichi.csv")

client = OpenAI(
    api_key=API_KEY,
    base_url="https://api.groq.com/openai/v1"
)