"""Lancement de commandes dans un container Docker jetable et isolé.

Utilisé par les tools "sensibles" (code_executor, browser_automation) — pas
un tool en soi, juste la mécanique Docker partagée entre eux pour éviter de
dupliquer la gestion du cycle de vie du container (création, timeout, arrêt
forcé, suppression garantie).
"""

import docker


class SandboxTimeoutError(TimeoutError):
    """Le container n'a pas terminé dans le délai imparti et a été tué."""


def _ensure_image(client, image: str) -> None:
    """`containers.create()` (API bas niveau) ne télécharge pas une image
    manquante, contrairement à `docker run` en CLI — il faut le faire
    explicitement, sans quoi la création échoue en 404 "No such image"."""
    try:
        client.images.get(image)
    except docker.errors.ImageNotFound:
        client.images.pull(image)


def run_in_container(
    image: str,
    command: list[str],
    timeout_seconds: int,
    mem_limit: str,
    nano_cpus: int,
    network_disabled: bool = True,
) -> str:
    """Crée, démarre, attend (avec timeout) puis détruit un container.

    Le container tourne toujours en isolation : réseau désactivé par défaut,
    mémoire et CPU plafonnés, et surtout **toujours supprimé** (`finally`),
    y compris en cas de timeout ou d'erreur du daemon Docker.
    """
    client = docker.from_env()
    _ensure_image(client, image)
    container = client.containers.create(
        image=image,
        command=command,
        network_disabled=network_disabled,
        mem_limit=mem_limit,
        nano_cpus=nano_cpus,
    )

    try:
        container.start()
        try:
            container.wait(timeout=timeout_seconds)
        except Exception as exc:
            container.kill()
            raise SandboxTimeoutError(f"Exécution interrompue après {timeout_seconds}s.") from exc

        return container.logs(stdout=True, stderr=True).decode("utf-8", errors="replace")
    finally:
        container.remove(force=True)
