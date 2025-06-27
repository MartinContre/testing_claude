import json
import unicodedata

# Definición de los tipos
TYPE_CHOICES = [
    ("secondary ", "Secundaria"),
    ("high_school", "Bachillerato"),
    ("degree", "Licenciatura"),
    ("engineer", "Ingenieria"),
    ("specialty", "Especialidad"),
    ("master", "Maestria"),
    ("doctorate", "Doctorado"),
]


def normalize_text(text):
    """Normaliza el texto eliminando tildes y convirtiendo a minúsculas."""
    return "".join(
        c for c in unicodedata.normalize("NFD", text) if unicodedata.category(c) != "Mn"
    ).lower()


def map_career_type(career_json):
    """Mapea el tipo de carrera basado en el campo JSON."""
    try:
        careers = json.loads(career_json)
        if not careers:
            return "unknown"

        first_career = careers[0]["name"].strip()
        normalized_career = normalize_text(first_career)

        for eng, esp in TYPE_CHOICES:
            if normalize_text(esp) in normalized_career:
                return eng
        return "unknown"
    except (json.JSONDecodeError, KeyError, IndexError):
        return "unknown"
