import tools.code_executor as code_executor_module
from tools.code_executor import CodeExecutorTool


def test_code_executor_runs_disabled_network_and_truncates(monkeypatch):
    captured = {}

    def fake_run_in_container(**kwargs):
        captured.update(kwargs)
        return "x" * 20_000

    monkeypatch.setattr(code_executor_module, "run_in_container", fake_run_in_container)

    result = CodeExecutorTool().run(code="print(1)")

    assert len(result) == code_executor_module.MAX_OUTPUT_CHARS
    assert captured["network_disabled"] is True
    assert captured["command"] == ["python", "-c", "print(1)"]


def test_code_executor_requires_validation():
    assert CodeExecutorTool().requires_validation is True
