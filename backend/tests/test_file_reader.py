import pytest

from tools.file_reader import FileReaderTool


@pytest.fixture
def sandbox(tmp_path, monkeypatch):
    import tools.file_reader as file_reader_module

    monkeypatch.setattr(file_reader_module.settings, "sandbox_path", str(tmp_path))
    return tmp_path


def test_reads_file_inside_sandbox(sandbox):
    (sandbox / "note.txt").write_text("bonjour depuis le sandbox", encoding="utf-8")

    content = FileReaderTool().run(path="note.txt")

    assert content == "bonjour depuis le sandbox"


def test_reads_file_in_subdirectory(sandbox):
    subdir = sandbox / "docs"
    subdir.mkdir()
    (subdir / "readme.md").write_text("# Titre", encoding="utf-8")

    content = FileReaderTool().run(path="docs/readme.md")

    assert content == "# Titre"


def test_rejects_path_traversal_outside_sandbox(sandbox):
    outside = sandbox.parent / "secret.txt"
    outside.write_text("ne devrait jamais être lisible", encoding="utf-8")

    with pytest.raises(ValueError):
        FileReaderTool().run(path="../secret.txt")


def test_rejects_absolute_path_outside_sandbox(sandbox):
    with pytest.raises(ValueError):
        FileReaderTool().run(path="/etc/passwd")


def test_raises_for_missing_file(sandbox):
    with pytest.raises(FileNotFoundError):
        FileReaderTool().run(path="ne_existe_pas.txt")
