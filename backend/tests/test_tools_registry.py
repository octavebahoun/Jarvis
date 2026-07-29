import pytest

import tools


def test_list_tools_includes_file_reader():
    names = [tool.name for tool in tools.list_tools()]
    assert "file_reader" in names


def test_get_tool_returns_instance():
    tool = tools.get_tool("file_reader")
    assert isinstance(tool, tools.BaseTool)
    assert tool.requires_validation is False


def test_get_tool_raises_for_unknown_name():
    with pytest.raises(tools.ToolNotFoundError):
        tools.get_tool("does_not_exist")
