"""Tests for Tide OS tools"""
import pytest
from pathlib import Path
from tide.tools.base import Tool, ToolResult, Parameter, ParameterType, ValidationResult
from tide.tools.registry import ToolRegistry
from tide.tools.filesystem import ViewTool, LsTool


class TestParameter:
    def test_required_validation(self):
        param = Parameter("test", ParameterType.STRING, "desc", required=True)
        assert param.validate(None) == "Required parameter 'test' is missing"
        assert param.validate("") is None
    
    def test_type_validation(self):
        param = Parameter("num", ParameterType.INTEGER, "desc")
        assert param.validate(123) is None
        assert "must be integer" in param.validate("123")
    
    def test_enum_validation(self):
        param = Parameter("choice", ParameterType.STRING, "desc", enum=["a", "b"])
        assert param.validate("a") is None
        assert "must be one of" in param.validate("c")


class TestToolRegistry:
    def test_register_and_get(self):
        registry = ToolRegistry()
        
        @registry.register
        class TestTool(Tool):
            name = "test"
            description = "A test tool"
            
            def _execute(self) -> ToolResult:
                return ToolResult.success_result("ok")
        
        tool = registry.get("test")
        assert tool is not None
        assert tool.name == "test"
    
    def test_list_tools(self):
        registry = ToolRegistry()
        assert registry.list_tools() == []


class TestViewTool:
    def test_view_existing_file(self, tmp_path):
        test_file = tmp_path / "test.txt"
        test_file.write_text("line1\nline2\nline3")
        
        tool = ViewTool()
        result = tool.execute(path=str(test_file))
        
        assert result.success
        assert "line1" in result.output
        assert "line2" in result.output


class TestLsTool:
    def test_ls_directory(self, tmp_path):
        (tmp_path / "file1.txt").touch()
        (tmp_path / "subdir").mkdir()
        
        tool = LsTool()
        result = tool.execute(path=str(tmp_path))
        
        assert result.success
        assert "file1.txt" in result.output
