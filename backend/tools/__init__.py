from abc import ABC, abstractmethod


class BaseTool(ABC):
    """Interface standard que chaque tool de l'agent doit implémenter."""

    name: str
    description: str  # Lu par le LLM (planner) pour choisir le bon tool.
    requires_validation: bool = False

    @abstractmethod
    def run(self, **kwargs) -> str:
        raise NotImplementedError


class ToolNotFoundError(KeyError):
    """Levée quand un tool demandé n'existe pas dans le registre statique."""


# Import après la définition de BaseTool : chaque module de tool fait
# `from tools import BaseTool`, ce qui créerait un import circulaire si ces
# imports arrivaient avant que BaseTool existe sur le module `tools`.
from tools.file_reader import FileReaderTool  # noqa: E402
from tools.web_search import WebSearchTool  # noqa: E402

_TOOLS: list[BaseTool] = [
    FileReaderTool(),
    WebSearchTool(),
]

_REGISTRY: dict[str, BaseTool] = {tool.name: tool for tool in _TOOLS}


def list_tools() -> list[BaseTool]:
    """Liste statique des tools disponibles (pas de chargement dynamique, cf. phase2.md)."""
    return list(_TOOLS)


def get_tool(name: str) -> BaseTool:
    try:
        return _REGISTRY[name]
    except KeyError:
        raise ToolNotFoundError(name) from None
