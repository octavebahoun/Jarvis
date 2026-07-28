from config import get_settings
from tools import BaseTool
from tools._sandbox import run_in_container

settings = get_settings()

MAX_OUTPUT_CHARS = 10_000  # cf. phase2.md : résultats tronqués avant d'être renvoyés au LLM


class CodeExecutorTool(BaseTool):
    name = "code_executor"
    description = (
        "Exécute du code Python dans un container Docker isolé et jetable "
        "(réseau désactivé, mémoire/CPU limités) et renvoie stdout/stderr. "
        "Argument : code (le script Python à exécuter)."
    )
    requires_validation = True

    def run(self, code: str, **kwargs) -> str:
        output = run_in_container(
            image=settings.code_executor_image,
            command=["python", "-c", code],
            timeout_seconds=settings.code_executor_timeout_seconds,
            mem_limit=settings.code_executor_memory_limit,
            nano_cpus=int(settings.code_executor_cpu_limit * 1_000_000_000),
            network_disabled=True,
        )
        return output[:MAX_OUTPUT_CHARS]
