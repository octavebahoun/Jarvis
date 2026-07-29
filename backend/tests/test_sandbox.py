import docker
import pytest

import tools._sandbox as sandbox_module
from tools._sandbox import SandboxTimeoutError, run_in_container


class _FakeContainer:
    def __init__(self, logs=b"", wait_exception=None):
        self.started = False
        self.killed = False
        self.removed = False
        self._logs = logs
        self._wait_exception = wait_exception

    def start(self):
        self.started = True

    def wait(self, timeout=None):
        if self._wait_exception:
            raise self._wait_exception
        return {"StatusCode": 0}

    def kill(self):
        self.killed = True

    def logs(self, stdout=True, stderr=True):
        return self._logs

    def remove(self, force=False):
        self.removed = True


class _FakeContainersAPI:
    def __init__(self, container):
        self._container = container
        self.create_kwargs = None

    def create(self, **kwargs):
        self.create_kwargs = kwargs
        return self._container


class _FakeImagesAPI:
    """Par défaut, l'image est déjà présente localement (cas le plus courant
    une fois qu'elle a été téléchargée une première fois)."""

    def __init__(self, image_present=True):
        self.image_present = image_present
        self.pulled = []

    def get(self, image):
        if not self.image_present:
            raise docker.errors.ImageNotFound(f"image manquante : {image}")
        return {"Id": image}

    def pull(self, image):
        self.pulled.append(image)
        self.image_present = True


class _FakeDockerClient:
    def __init__(self, container, image_present=True):
        self.containers = _FakeContainersAPI(container)
        self.images = _FakeImagesAPI(image_present=image_present)


def test_run_in_container_returns_logs_and_cleans_up(monkeypatch):
    container = _FakeContainer(logs=b"hello world")
    client = _FakeDockerClient(container)
    monkeypatch.setattr(sandbox_module.docker, "from_env", lambda: client)

    output = run_in_container(
        image="python:3.11-slim",
        command=["python", "-c", "print('hi')"],
        timeout_seconds=5,
        mem_limit="128m",
        nano_cpus=500_000_000,
    )

    assert output == "hello world"
    assert container.started is True
    assert container.removed is True
    assert client.containers.create_kwargs["network_disabled"] is True
    assert client.images.pulled == []  # image déjà présente : pas de pull


def test_run_in_container_pulls_image_when_missing_locally(monkeypatch):
    container = _FakeContainer(logs=b"ok")
    client = _FakeDockerClient(container, image_present=False)
    monkeypatch.setattr(sandbox_module.docker, "from_env", lambda: client)

    run_in_container(
        image="python:3.11-slim",
        command=["python", "-c", "print(1)"],
        timeout_seconds=5,
        mem_limit="128m",
        nano_cpus=500_000_000,
    )

    assert client.images.pulled == ["python:3.11-slim"]


def test_run_in_container_kills_and_raises_on_timeout(monkeypatch):
    container = _FakeContainer(wait_exception=Exception("timed out"))
    client = _FakeDockerClient(container)
    monkeypatch.setattr(sandbox_module.docker, "from_env", lambda: client)

    with pytest.raises(SandboxTimeoutError):
        run_in_container(
            image="python:3.11-slim",
            command=["python", "-c", "while True: pass"],
            timeout_seconds=1,
            mem_limit="128m",
            nano_cpus=500_000_000,
        )

    assert container.killed is True
    assert container.removed is True  # toujours nettoyé, même en cas de timeout


def test_run_in_container_removes_container_even_if_start_fails(monkeypatch):
    class _BoomContainer(_FakeContainer):
        def start(self):
            raise RuntimeError("docker daemon indisponible")

    container = _BoomContainer()
    client = _FakeDockerClient(container)
    monkeypatch.setattr(sandbox_module.docker, "from_env", lambda: client)

    with pytest.raises(RuntimeError):
        run_in_container(
            image="python:3.11-slim",
            command=["python", "-c", "print(1)"],
            timeout_seconds=5,
            mem_limit="128m",
            nano_cpus=500_000_000,
        )

    assert container.removed is True
