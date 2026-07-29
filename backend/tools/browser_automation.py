from config import get_settings
from tools import BaseTool
from tools._sandbox import run_in_container

settings = get_settings()

MAX_OUTPUT_CHARS = 10_000  # cf. phase2.md : résultats tronqués avant d'être renvoyés au LLM


def _build_script(url: str, selector: str | None) -> str:
    """Script exécuté à l'intérieur du container Playwright — navigue vers
    `url` et extrait le texte de la page (ou d'un sélecteur CSS précis)."""
    return f"""
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto({url!r}, timeout=20000, wait_until="load")
    selector = {selector!r}
    content = page.locator(selector).inner_text() if selector else page.inner_text("body")
    browser.close()

print(content)
"""


class BrowserAutomationTool(BaseTool):
    name = "browser_automation"
    description = (
        "Navigue vers une URL dans un navigateur headless (Playwright, sandboxé) "
        "et extrait le texte de la page. Arguments : url (obligatoire), "
        "selector (optionnel, sélecteur CSS pour cibler un élément précis)."
    )
    requires_validation = True

    def run(self, url: str, selector: str | None = None, **kwargs) -> str:
        script = _build_script(url, selector)
        output = run_in_container(
            image=settings.browser_automation_image,
            command=["python", "-c", script],
            timeout_seconds=settings.browser_automation_timeout_seconds,
            mem_limit=settings.browser_automation_memory_limit,
            nano_cpus=int(settings.browser_automation_cpu_limit * 1_000_000_000),
            # Contrairement à code_executor : le réseau doit rester activé,
            # tout l'intérêt du tool est d'atteindre de vrais sites.
            network_disabled=False,
        )
        return output[:MAX_OUTPUT_CHARS]
