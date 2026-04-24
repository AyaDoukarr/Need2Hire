import json
from typing import Any, Dict

from config import client, TEXT_MODEL


def extract_json(text_output: str) -> Dict[str, Any]:
    text_output = (text_output or "").strip()

    for marker in ["```json", "```"]:
        if text_output.startswith(marker):
            text_output = text_output[len(marker):].strip()

    if text_output.endswith("```"):
        text_output = text_output[:-3].strip()

    start = text_output.find("{")
    end = text_output.rfind("}")

    if start == -1 or end == -1 or end < start:
        raise ValueError(f"Réponse non exploitable : {text_output}")

    return json.loads(text_output[start:end + 1])


def call_llm_json(system_prompt: str, user_input: str, temperature: float = 0) -> Dict[str, Any]:
    response = client.chat.completions.create(
        model=TEXT_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input},
        ],
        temperature=temperature,
    )

    content = response.choices[0].message.content
    return extract_json(content)


def call_llm_text(system_prompt: str, user_input: str, temperature: float = 0.2) -> str:
    response = client.chat.completions.create(
        model=TEXT_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input},
        ],
        temperature=temperature,
    )

    return (response.choices[0].message.content or "").strip()