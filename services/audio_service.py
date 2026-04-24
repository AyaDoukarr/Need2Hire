import tempfile

from config import client, AUDIO_MODEL


def transcribe_audio_file(file_path: str, language: str = "fr") -> str:
    with open(file_path, "rb") as af:
        transcript = client.audio.transcriptions.create(
            model=AUDIO_MODEL,
            file=af,
            language=language,
            response_format="json",
        )

    text = getattr(transcript, "text", None)
    if not text:
        raise ValueError("La transcription audio est vide.")

    return text.strip()


def save_uploaded_audio_to_temp(uploaded_file, suffix: str) -> str:
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(uploaded_file.read())
        return tmp.name