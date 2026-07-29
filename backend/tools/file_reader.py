from pathlib import Path

from config import get_settings
from tools import BaseTool

settings = get_settings()


def _resolve_safe_path(path: str) -> Path:
    """Résout `path` relativement au répertoire sandbox et refuse toute
    tentative de sortie (`../..`, chemin absolu, symlink pointant dehors)."""
    sandbox_root = Path(settings.sandbox_path).resolve()
    candidate = (sandbox_root / path).resolve()

    if not candidate.is_relative_to(sandbox_root):
        raise ValueError(f"Chemin hors du répertoire sandbox : {path}")
    if not candidate.is_file():
        raise FileNotFoundError(f"Fichier introuvable dans le sandbox : {path}")

    return candidate


class FileReaderTool(BaseTool):
    name = "file_reader"
    description = (
        "Lit le contenu texte d'un fichier situé dans le répertoire sandbox autorisé "
        "(SANDBOX_PATH). Argument : path (chemin relatif au sandbox)."
    )
    requires_validation = False

    def run(self, path: str, **kwargs) -> str:
        target = _resolve_safe_path(path)
        return target.read_text(encoding="utf-8", errors="replace")
