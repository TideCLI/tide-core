"""
Testing & Validation Tools - Run tests, preview diffs, code transforms, error recovery
"""

import os
import re
import json
import subprocess
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

from .base import Tool, ToolResult, ToolParameter


class RunTestsTool(Tool):
    """Run tests and parse results"""
    name = "run_tests"
    description = "Auto-detect test framework, run tests, and return structured results"
    category = "testing"
    requires_confirmation = False
    timeout_seconds = 120
    max_output_length = 30000
    
    parameters = [
        ToolParameter("path", "string", "Project path", False, "."),
        ToolParameter("file", "string", "Test file to run", False, ""),
        ToolParameter("test_name", "string", "Specific test name to run", False, ""),
        ToolParameter("framework", "string", "Force framework: pytest, jest, go, cargo", False, ""),
        ToolParameter("verbose", "boolean", "Show verbose output", False, False)
    ]
    
    # Framework detection rules
    FRAMEWORKS = {
        "pytest": {
            "indicators": ["pytest.ini", "conftest.py", "setup.cfg"],
            "cmd": ["python", "-m", "pytest", "--tb=short", "-q"],
            "file_flag": "",
            "test_flag": "-k",
            "verbose_flag": "-v"
        },
        "jest": {
            "indicators": [],  # Detected via package.json
            "cmd": ["npx", "jest", "--no-coverage"],
            "file_flag": "",
            "test_flag": "-t",
            "verbose_flag": "--verbose"
        },
        "go": {
            "indicators": ["go.mod"],
            "cmd": ["go", "test"],
            "file_flag": "",
            "test_flag": "-run",
            "verbose_flag": "-v"
        },
        "cargo": {
            "indicators": ["Cargo.toml"],
            "cmd": ["cargo", "test"],
            "file_flag": "",
            "test_flag": "",
            "verbose_flag": "--verbose"
        }
    }
    
    def execute(self, params: Dict[str, Any]) -> ToolResult:
        result = ToolResult(tool_name=self.name)
        
        try:
            path = params.get("path", ".")
            file_path = params.get("file", "")
            test_name = params.get("test_name", "")
            framework = params.get("framework", "")
            verbose = params.get("verbose", False)
            
            project_path = Path(self.working_dir) / path
            
            # Detect framework
            if not framework:
                framework = self._detect_framework(project_path)
            
            if not framework:
                result.error = (
                    "Could not detect test framework. "
                    "Supported: pytest, jest, go, cargo. "
                    "Use framework parameter to specify."
                )
                result.success = False
                return result
            
            # Build command
            cmd = self._build_command(framework, file_path, test_name, verbose, project_path)
            
            # Run tests
            proc = subprocess.run(
                cmd, capture_output=True, text=True,
                cwd=str(project_path), timeout=self.timeout_seconds
            )
            
            # Parse results
            parsed = self._parse_results(framework, proc.stdout, proc.stderr, proc.returncode)
            
            # Build output
            output_lines = [
                f"Test Framework: {framework}",
                f"Command: {' '.join(cmd)}",
                f"Exit Code: {proc.returncode}",
                f"",
                f"Results:",
                f"  Total:   {parsed['total']}",
                f"  Passed:  {parsed['passed']}",
                f"  Failed:  {parsed['failed']}",
                f"  Skipped: {parsed['skipped']}",
                f"  Errors:  {parsed['errors']}",
            ]
            
            if parsed['failures']:
                output_lines.append(f"\nFailures:")
                for failure in parsed['failures'][:10]:  # Show first 10
                    output_lines.append(f"\n  FAIL: {failure.get('name', 'unknown')}")
                    if failure.get('file'):
                        output_lines.append(f"  File: {failure['file']}:{failure.get('line', '?')}")
                    if failure.get('message'):
                        output_lines.append(f"  Error: {failure['message'][:200]}")
            
            # Add raw output if verbose or few results
            if verbose or parsed['total'] < 20:
                raw = proc.stdout + proc.stderr
                if raw.strip():
                    output_lines.append(f"\nRaw Output:\n{self.truncate_output(raw, 5000)}")
            
            result.output = '\n'.join(output_lines)
            result.success = proc.returncode == 0
            result.metadata = parsed
            
        except subprocess.TimeoutExpired:
            result.error = f"Tests timed out after {self.timeout_seconds} seconds"
            result.success = False
        except Exception as e:
            result.error = str(e)
            result.success = False
        finally:
            result.set_finished()
        
        return result
    
    def _detect_framework(self, path: Path) -> str:
        """Detect test framework from project files"""
        # Check for Python
        if (path / "pytest.ini").exists() or (path / "conftest.py").exists():
            return "pytest"
        if (path / "pyproject.toml").exists():
            try:
                content = (path / "pyproject.toml").read_text()
                if "pytest" in content or "tool.pytest" in content:
                    return "pytest"
            except Exception:
                pass
        if (path / "setup.cfg").exists():
            return "pytest"
        
        # Check for any .py test files
        if list(path.rglob("test_*.py")) or list(path.rglob("*_test.py")):
            return "pytest"
        
        # Check for Node.js
        if (path / "package.json").exists():
            try:
                content = (path / "package.json").read_text()
                if "jest" in content:
                    return "jest"
                if "vitest" in content:
                    return "jest"  # vitest has jest-compatible CLI
            except Exception:
                pass
        
        # Check for Go
        if (path / "go.mod").exists():
            return "go"
        
        # Check for Rust
        if (path / "Cargo.toml").exists():
            return "cargo"
        
        return ""
    
    def _build_command(self, framework: str, file_path: str, test_name: str,
                       verbose: bool, project_path: Path) -> list:
        """Build the test command"""
        config = self.FRAMEWORKS.get(framework, {})
        cmd = list(config.get("cmd", []))
        
        if verbose and config.get("verbose_flag"):
            cmd.append(config["verbose_flag"])
        
        if file_path:
            cmd.append(file_path)
        elif framework == "go":
            cmd.append("./...")
        
        if test_name and config.get("test_flag"):
            cmd.extend([config["test_flag"], test_name])
        
        return cmd
    
    def _parse_results(self, framework: str, stdout: str, stderr: str,
                       return_code: int) -> Dict:
        """Parse test output into structured results"""
        parsed = {
            "total": 0, "passed": 0, "failed": 0,
            "skipped": 0, "errors": 0, "failures": [],
            "framework": framework
        }
        
        output = stdout + "\n" + stderr
        
        if framework == "pytest":
            self._parse_pytest(output, parsed)
        elif framework == "jest":
            self._parse_jest(output, parsed)
        elif framework == "go":
            self._parse_go(output, parsed)
        elif framework == "cargo":
            self._parse_cargo(output, parsed)
        else:
            # Generic: count pass/fail from return code
            parsed["total"] = 1
            if return_code == 0:
                parsed["passed"] = 1
            else:
                parsed["failed"] = 1
        
        return parsed
    
    def _parse_pytest(self, output: str, parsed: Dict):
        """Parse pytest output"""
        # Look for summary line: "X passed, Y failed, Z skipped"
        summary_match = re.search(
            r'(\d+)\s+passed(?:.*?(\d+)\s+failed)?(?:.*?(\d+)\s+skipped)?(?:.*?(\d+)\s+error)?',
            output
        )
        if summary_match:
            parsed["passed"] = int(summary_match.group(1) or 0)
            parsed["failed"] = int(summary_match.group(2) or 0)
            parsed["skipped"] = int(summary_match.group(3) or 0)
            parsed["errors"] = int(summary_match.group(4) or 0)
            parsed["total"] = parsed["passed"] + parsed["failed"] + parsed["skipped"] + parsed["errors"]
        
        # Parse FAILED lines
        for match in re.finditer(r'FAILED\s+(.+?)(?:\s+-\s+(.+))?$', output, re.MULTILINE):
            parsed["failures"].append({
                "name": match.group(1).strip(),
                "message": match.group(2) or ""
            })
    
    def _parse_jest(self, output: str, parsed: Dict):
        """Parse jest output"""
        # Jest summary: "Tests: X failed, Y passed, Z total"
        tests_match = re.search(r'Tests:\s+(?:(\d+)\s+failed,\s+)?(\d+)\s+passed,\s+(\d+)\s+total', output)
        if tests_match:
            parsed["failed"] = int(tests_match.group(1) or 0)
            parsed["passed"] = int(tests_match.group(2) or 0)
            parsed["total"] = int(tests_match.group(3) or 0)
    
    def _parse_go(self, output: str, parsed: Dict):
        """Parse go test output"""
        parsed["passed"] = output.count("--- PASS:")
        parsed["failed"] = output.count("--- FAIL:")
        parsed["skipped"] = output.count("--- SKIP:")
        parsed["total"] = parsed["passed"] + parsed["failed"] + parsed["skipped"]
        
        for match in re.finditer(r'--- FAIL: (\S+)', output):
            parsed["failures"].append({"name": match.group(1)})
    
    def _parse_cargo(self, output: str, parsed: Dict):
        """Parse cargo test output"""
        # "test result: ok. X passed; Y failed; Z ignored"
        result_match = re.search(r'test result:.*?(\d+)\s+passed.*?(\d+)\s+failed.*?(\d+)\s+ignored', output)
        if result_match:
            parsed["passed"] = int(result_match.group(1))
            parsed["failed"] = int(result_match.group(2))
            parsed["skipped"] = int(result_match.group(3))
            parsed["total"] = parsed["passed"] + parsed["failed"] + parsed["skipped"]


class DiffPreviewTool(Tool):
    """Preview file changes without applying them"""
    name = "diff_preview"
    description = "Preview proposed file changes as a diff without writing to disk"
    category = "testing"
    requires_confirmation = False
    
    parameters = [
        ToolParameter("file_path", "string", "Path to the file", True),
        ToolParameter("old_string", "string", "Text that would be replaced", True),
        ToolParameter("new_string", "string", "Replacement text", True),
        ToolParameter("context_lines", "integer", "Lines of context around changes", False, 3)
    ]
    
    def execute(self, params: Dict[str, Any]) -> ToolResult:
        result = ToolResult(tool_name=self.name)
        
        try:
            file_path = params.get("file_path", "")
            old_string = params.get("old_string", "")
            new_string = params.get("new_string", "")
            context_lines = params.get("context_lines", 3)
            
            if not file_path or not old_string:
                result.error = "file_path and old_string are required"
                result.success = False
                return result
            
            path = Path(self.working_dir) / file_path
            
            if not path.exists():
                result.error = f"File not found: {file_path}"
                result.success = False
                return result
            
            # Read current content
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check if old_string exists
            if old_string not in content:
                result.error = "old_string not found in file. No changes to preview."
                result.success = False
                return result
            
            # Count occurrences
            occurrences = content.count(old_string)
            
            # Generate preview (only first occurrence, like EditTool)
            new_content = content.replace(old_string, new_string, 1)
            
            # Generate diff
            from difflib import unified_diff
            old_lines = content.splitlines(keepends=True)
            new_lines = new_content.splitlines(keepends=True)
            
            diff = list(unified_diff(
                old_lines, new_lines,
                fromfile=f"a/{file_path}",
                tofile=f"b/{file_path}",
                n=context_lines
            ))
            
            if diff:
                # Count changes
                additions = sum(1 for l in diff if l.startswith('+') and not l.startswith('+++'))
                deletions = sum(1 for l in diff if l.startswith('-') and not l.startswith('---'))
                
                output = f"PREVIEW (not applied) for {file_path}:\n"
                output += f"+{additions} -{deletions} lines"
                if occurrences > 1:
                    output += f" (note: {occurrences} occurrences found, only first would be replaced)"
                output += f"\n\n{''.join(diff)}"
                
                result.output = output
                result.metadata = {
                    "file": file_path,
                    "additions": additions,
                    "deletions": deletions,
                    "occurrences": occurrences,
                    "applied": False
                }
            else:
                result.output = "No differences — old_string equals new_string"
                
        except Exception as e:
            result.error = str(e)
            result.success = False
        finally:
            result.set_finished()
        
        return result


class CodeTransformTool(Tool):
    """Structured code transformations"""
    name = "code_transform"
    description = "Perform code transformations: rename symbols, add imports, extract functions"
    category = "testing"
    requires_confirmation = True
    
    parameters = [
        ToolParameter("action", "string", "Action: rename, add_import, extract_function", True),
        ToolParameter("file_path", "string", "File path to transform", True),
        ToolParameter("old_name", "string", "Current symbol name (for rename)", False, ""),
        ToolParameter("new_name", "string", "New symbol name (for rename/extract_function)", False, ""),
        ToolParameter("import_statement", "string", "Import to add (e.g., 'from os import path')", False, ""),
        ToolParameter("scope", "string", "Scope: file or project (for rename)", False, "file"),
        ToolParameter("start_line", "integer", "Start line for extract_function", False, 0),
        ToolParameter("end_line", "integer", "End line for extract_function", False, 0)
    ]
    
    def execute(self, params: Dict[str, Any]) -> ToolResult:
        result = ToolResult(tool_name=self.name)
        
        try:
            action = params.get("action", "").lower()
            
            if action == "rename":
                result = self._rename(params)
            elif action == "add_import":
                result = self._add_import(params)
            elif action == "extract_function":
                result = self._extract_function(params)
            else:
                result.error = f"Unknown action: {action}. Use: rename, add_import, extract_function"
                result.success = False
                
        except Exception as e:
            result.error = str(e)
            result.success = False
        finally:
            result.set_finished()
        
        return result
    
    def _rename(self, params: Dict) -> ToolResult:
        result = ToolResult(tool_name=self.name)
        file_path = params.get("file_path", "")
        old_name = params.get("old_name", "")
        new_name = params.get("new_name", "")
        scope = params.get("scope", "file")
        
        if not all([file_path, old_name, new_name]):
            result.error = "file_path, old_name, and new_name are required"
            result.success = False
            return result
        
        if old_name == new_name:
            result.error = "old_name and new_name are the same"
            result.success = False
            return result
        
        # Build word-boundary pattern
        pattern = re.compile(rf'\b{re.escape(old_name)}\b')
        
        files_to_process = []
        if scope == "project":
            # Find all files containing the symbol
            project_path = Path(self.working_dir)
            for root, dirs, files in os.walk(project_path):
                dirs[:] = [d for d in dirs if d not in ['.git', 'node_modules', '__pycache__', '.venv', '.tide']]
                for f in files:
                    if f.endswith(('.py', '.js', '.ts', '.go', '.rs', '.java', '.tsx', '.jsx')):
                        fp = Path(root) / f
                        try:
                            content = fp.read_text(encoding='utf-8', errors='ignore')
                            if pattern.search(content):
                                files_to_process.append(fp)
                        except Exception:
                            pass
        else:
            path = Path(self.working_dir) / file_path
            if path.exists():
                files_to_process = [path]
            else:
                result.error = f"File not found: {file_path}"
                result.success = False
                return result
        
        # Perform rename
        total_replacements = 0
        files_changed = []
        
        for fp in files_to_process:
            try:
                content = fp.read_text(encoding='utf-8')
                new_content, count = pattern.subn(new_name, content)
                
                if count > 0:
                    fp.write_text(new_content, encoding='utf-8')
                    total_replacements += count
                    files_changed.append({
                        "file": str(fp.relative_to(self.working_dir)),
                        "replacements": count
                    })
            except Exception:
                pass
        
        output = f"Renamed '{old_name}' -> '{new_name}'\n"
        output += f"Total replacements: {total_replacements} across {len(files_changed)} file(s)\n"
        for fc in files_changed:
            output += f"  {fc['file']}: {fc['replacements']} replacements\n"
        
        result.output = output
        result.metadata = {
            "total_replacements": total_replacements,
            "files_changed": len(files_changed),
            "details": files_changed
        }
        return result
    
    def _add_import(self, params: Dict) -> ToolResult:
        result = ToolResult(tool_name=self.name)
        file_path = params.get("file_path", "")
        import_stmt = params.get("import_statement", "")
        
        if not file_path or not import_stmt:
            result.error = "file_path and import_statement are required"
            result.success = False
            return result
        
        path = Path(self.working_dir) / file_path
        if not path.exists():
            result.error = f"File not found: {file_path}"
            result.success = False
            return result
        
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if import already exists
        if import_stmt.strip() in content:
            result.output = f"Import already exists: {import_stmt}"
            return result
        
        lines = content.split('\n')
        
        # Find the right insertion point
        insert_at = 0
        last_import_line = -1
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            # Skip docstrings at the top
            if stripped.startswith('"""') or stripped.startswith("'''"):
                continue
            if stripped.startswith('import ') or stripped.startswith('from '):
                last_import_line = i
        
        if last_import_line >= 0:
            insert_at = last_import_line + 1
        else:
            # No imports found — insert after any initial comments/docstrings
            for i, line in enumerate(lines):
                stripped = line.strip()
                if stripped and not stripped.startswith('#') and not stripped.startswith('"""') and not stripped.startswith("'''"):
                    insert_at = i
                    break
        
        # Insert
        lines.insert(insert_at, import_stmt.strip())
        new_content = '\n'.join(lines)
        
        with open(path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        result.output = f"Added import to {file_path} at line {insert_at + 1}:\n  {import_stmt}"
        result.metadata = {"file": file_path, "line": insert_at + 1}
        return result
    
    def _extract_function(self, params: Dict) -> ToolResult:
        result = ToolResult(tool_name=self.name)
        file_path = params.get("file_path", "")
        new_name = params.get("new_name", "")
        start_line = params.get("start_line", 0)
        end_line = params.get("end_line", 0)
        
        if not all([file_path, new_name, start_line, end_line]):
            result.error = "file_path, new_name, start_line, and end_line are required"
            result.success = False
            return result
        
        path = Path(self.working_dir) / file_path
        if not path.exists():
            result.error = f"File not found: {file_path}"
            result.success = False
            return result
        
        with open(path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        if start_line < 1 or end_line > len(lines) or start_line > end_line:
            result.error = f"Invalid line range: {start_line}-{end_line} (file has {len(lines)} lines)"
            result.success = False
            return result
        
        # Extract lines (1-indexed)
        extracted = lines[start_line - 1:end_line]
        
        # Detect indentation of extracted block
        min_indent = float('inf')
        for line in extracted:
            if line.strip():
                indent = len(line) - len(line.lstrip())
                min_indent = min(min_indent, indent)
        if min_indent == float('inf'):
            min_indent = 0
        
        # Build new function
        func_lines = [f"def {new_name}():\n"]
        for line in extracted:
            if line.strip():
                # Re-indent: remove original indent, add 4-space indent
                func_lines.append("    " + line[min_indent:])
            else:
                func_lines.append("\n")
        func_lines.append("\n\n")
        
        # Build replacement: call the function at original indent
        call_indent = " " * min_indent
        call_line = f"{call_indent}{new_name}()\n"
        
        # Reconstruct file
        new_lines = (
            lines[:start_line - 1] +
            [call_line] +
            lines[end_line:] +
            ["\n"] +
            func_lines
        )
        
        with open(path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        
        result.output = (
            f"Extracted lines {start_line}-{end_line} into function '{new_name}()'\n"
            f"File: {file_path}\n"
            f"Original lines replaced with: {new_name}()\n"
            f"New function added at end of file"
        )
        result.metadata = {
            "function_name": new_name,
            "lines_extracted": end_line - start_line + 1,
            "file": file_path
        }
        return result


class ErrorRecoveryTool(Tool):
    """Analyze and recover from tool execution errors"""
    name = "error_recovery"
    description = "Diagnose tool errors and suggest or apply recovery strategies"
    category = "testing"
    requires_confirmation = False
    
    parameters = [
        ToolParameter("tool_name", "string", "The tool that failed", True),
        ToolParameter("error_message", "string", "The error message", True),
        ToolParameter("original_params", "object", "Original parameters that caused the error", False, {}),
        ToolParameter("auto_fix", "boolean", "Attempt automatic recovery", False, False)
    ]
    
    # Error patterns and their recovery strategies
    ERROR_PATTERNS = {
        "file not found": "file_recovery",
        "not found": "file_recovery",
        "old_string not found": "edit_recovery",
        "timed out": "timeout_recovery",
        "syntax error": "syntax_recovery",
        "permission denied": "permission_recovery",
        "not a git repository": "git_recovery",
        "json": "json_recovery",
        "command contains banned": "security_recovery",
        "tool not found": "tool_recovery"
    }
    
    def execute(self, params: Dict[str, Any]) -> ToolResult:
        result = ToolResult(tool_name=self.name)
        
        try:
            tool_name = params.get("tool_name", "")
            error_msg = params.get("error_message", "")
            original_params = params.get("original_params", {})
            auto_fix = params.get("auto_fix", False)
            
            if not tool_name or not error_msg:
                result.error = "tool_name and error_message are required"
                result.success = False
                return result
            
            # Match error to recovery strategy
            strategy = self._identify_strategy(error_msg)
            diagnosis = self._diagnose(tool_name, error_msg, original_params, strategy)
            
            output_lines = [
                f"Error Diagnosis:",
                f"  Tool: {tool_name}",
                f"  Error: {error_msg[:200]}",
                f"  Strategy: {strategy}",
                f"",
                f"Analysis:",
                f"  {diagnosis['analysis']}",
                f"",
                f"Suggestions:"
            ]
            
            for i, suggestion in enumerate(diagnosis['suggestions'], 1):
                output_lines.append(f"  {i}. {suggestion}")
            
            if diagnosis.get('corrected_params') and auto_fix:
                output_lines.append(f"\nAuto-fix: Corrected parameters generated")
                output_lines.append(f"  {json.dumps(diagnosis['corrected_params'], indent=2)}")
            
            result.output = '\n'.join(output_lines)
            result.metadata = {
                "strategy": strategy,
                "suggestions": diagnosis['suggestions'],
                "corrected_params": diagnosis.get('corrected_params'),
                "auto_fixable": diagnosis.get('auto_fixable', False)
            }
            
        except Exception as e:
            result.error = str(e)
            result.success = False
        finally:
            result.set_finished()
        
        return result
    
    def _identify_strategy(self, error_msg: str) -> str:
        """Match error to recovery strategy"""
        error_lower = error_msg.lower()
        for pattern, strategy in self.ERROR_PATTERNS.items():
            if pattern in error_lower:
                return strategy
        return "generic_recovery"
    
    def _diagnose(self, tool_name: str, error_msg: str,
                   original_params: Dict, strategy: str) -> Dict:
        """Generate diagnosis and recovery suggestions"""
        
        if strategy == "file_recovery":
            return self._diagnose_file_error(tool_name, error_msg, original_params)
        elif strategy == "edit_recovery":
            return self._diagnose_edit_error(tool_name, error_msg, original_params)
        elif strategy == "timeout_recovery":
            return self._diagnose_timeout(tool_name, error_msg, original_params)
        elif strategy == "syntax_recovery":
            return self._diagnose_syntax(tool_name, error_msg, original_params)
        elif strategy == "permission_recovery":
            return {
                "analysis": "The operation requires elevated permissions.",
                "suggestions": [
                    "Check file/directory ownership and permissions",
                    "Ensure the working directory is writable",
                    "The file may be read-only or locked by another process"
                ]
            }
        elif strategy == "git_recovery":
            return {
                "analysis": "The current directory is not a git repository.",
                "suggestions": [
                    "Verify you are in the correct project directory",
                    "Initialize a git repo with: git init",
                    "Check if .git directory exists"
                ]
            }
        elif strategy == "security_recovery":
            return {
                "analysis": "The command was blocked by security rules.",
                "suggestions": [
                    "Use a dedicated tool instead of bash for this operation",
                    "For git: use git_status, git_diff, git_commit tools",
                    "For file operations: use view, edit, write tools",
                    "Review the banned command list in BashTool"
                ]
            }
        elif strategy == "tool_recovery":
            return {
                "analysis": f"Tool '{tool_name}' does not exist.",
                "suggestions": [
                    "Check available tools with the 'tools' command",
                    "Tool names are case-sensitive",
                    f"Did you mean one of the registered tools?"
                ]
            }
        else:
            return {
                "analysis": f"Unexpected error in tool '{tool_name}'.",
                "suggestions": [
                    "Review the error message for clues",
                    "Try running the tool with simpler parameters",
                    "Check if the file/path exists and is accessible",
                    f"Error details: {error_msg[:200]}"
                ]
            }
    
    def _diagnose_file_error(self, tool_name: str, error_msg: str,
                              original_params: Dict) -> Dict:
        """Diagnose file-not-found errors"""
        file_path = original_params.get("file_path", "") or original_params.get("path", "")
        
        suggestions = [
            f"Check if the file path is correct: {file_path}",
            "Use the 'glob' tool to search for similar files",
            "Use the 'ls' tool to list directory contents"
        ]
        
        corrected_params = None
        
        # Try to find similar files
        if file_path:
            base_name = Path(file_path).name
            parent = Path(self.working_dir) / Path(file_path).parent
            
            if parent.exists():
                similar = []
                for f in parent.iterdir():
                    if f.name.lower().startswith(base_name[:3].lower()):
                        similar.append(str(f.relative_to(self.working_dir)))
                
                if similar:
                    suggestions.insert(0, f"Similar files found: {', '.join(similar[:5])}")
                    # Auto-fix: use the closest match
                    corrected_params = dict(original_params)
                    corrected_params["file_path"] = similar[0]
        
        return {
            "analysis": f"File '{file_path}' does not exist at the expected path.",
            "suggestions": suggestions,
            "corrected_params": corrected_params,
            "auto_fixable": corrected_params is not None
        }
    
    def _diagnose_edit_error(self, tool_name: str, error_msg: str,
                              original_params: Dict) -> Dict:
        """Diagnose edit string-not-found errors"""
        file_path = original_params.get("file_path", "")
        old_string = original_params.get("old_string", "")
        
        suggestions = [
            f"The exact text '{old_string[:80]}...' was not found in {file_path}",
            f"Use 'view' to read the file and find the correct text",
            "Whitespace and indentation must match exactly",
            "The file may have been modified since you last read it"
        ]
        
        # Try to find what's actually in the file
        if file_path:
            path = Path(self.working_dir) / file_path
            if path.exists():
                try:
                    content = path.read_text(encoding='utf-8')
                    # Try to find partial match
                    words = old_string.split()[:3]  # First 3 words
                    if words:
                        search = ' '.join(words)
                        for i, line in enumerate(content.split('\n'), 1):
                            if search in line:
                                suggestions.insert(0,
                                    f"Partial match found at line {i}: '{line.strip()[:80]}'"
                                )
                                break
                except Exception:
                    pass
        
        return {
            "analysis": "The text to replace was not found in the file. This usually means the content has changed or whitespace doesn't match.",
            "suggestions": suggestions,
            "auto_fixable": False
        }
    
    def _diagnose_timeout(self, tool_name: str, error_msg: str,
                           original_params: Dict) -> Dict:
        """Diagnose timeout errors"""
        return {
            "analysis": "The operation exceeded the time limit.",
            "suggestions": [
                "Try with a shorter/simpler operation",
                "If running tests, target a specific test file instead of the whole suite",
                "If running a command, check if it's waiting for input",
                "Increase the timeout parameter if the operation is expected to be slow"
            ]
        }
    
    def _diagnose_syntax(self, tool_name: str, error_msg: str,
                          original_params: Dict) -> Dict:
        """Diagnose syntax errors"""
        return {
            "analysis": "The code contains a syntax error.",
            "suggestions": [
                "Use the 'diagnostics' tool to check the file for syntax errors",
                "Use 'view' to read the file around the error location",
                "Common causes: missing colons, mismatched brackets, invalid indentation",
                f"Error details: {error_msg[:200]}"
            ]
        }
