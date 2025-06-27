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


def map_career_type(current_study):
    try:
        current_study = current_study.strip()
        normalized_current_study = normalize_text(current_study)

        # Comparar con TYPE_CHOICES
        for eng, esp in TYPE_CHOICES:
            if normalize_text(esp) in normalized_current_study:
                return eng
        return "unknown"
    except (json.JSONDecodeError, KeyError, IndexError):
        return "unknown"
