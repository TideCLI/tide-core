"""
Git Tools - Version control operations for Tide
Tools: git_status, git_diff, git_commit, git_log
"""

import subprocess
from pathlib import Path
from typing import Dict, Any
from datetime import datetime

from .base import Tool, ToolResult, ToolParameter


class GitStatusTool(Tool):
    """Show git repository status"""
    name = "git_status"
    description = "Show the current git status including staged, unstaged, and untracked files"
    category = "git"
    requires_confirmation = False

    parameters = [
        ToolParameter("path", "string", "Repository path", False, "."),
        ToolParameter("short", "boolean", "Use short format", False, False)
    ]

    def execute(self, params: Dict[str, Any]) -> ToolResult:
        result = ToolResult(tool_name=self.name)

        try:
            path = params.get("path", ".")
            repo_path = Path(self.working_dir) / path

            # Verify git repo
            if not (repo_path / ".git").exists():
                result.error = f"Not a git repository: {repo_path}"
                result.success = False
                return result

            # Get porcelain status for parsing
            cmd = ["git", "status", "--porcelain=v2", "--branch"]
            proc = subprocess.run(
                cmd, capture_output=True, text=True,
                cwd=str(repo_path), timeout=15
            )

            if proc.returncode != 0:
                result.error = f"git status failed: {proc.stderr.strip()}"
                result.success = False
                return result

            # Parse porcelain v2 output
            branch = ""
            upstream = ""
            ahead = 0
            behind = 0
            staged = []
            unstaged = []
            untracked = []

            for line in proc.stdout.strip().split('\n'):
                if not line:
                    continue

                # Branch info
                if line.startswith("# branch.head"):
                    branch = line.split()[-1]
                elif line.startswith("# branch.upstream"):
                    upstream = line.split()[-1]
                elif line.startswith("# branch.ab"):
                    parts = line.split()
                    for p in parts:
                        if p.startswith("+"):
                            try:
                                ahead = int(p[1:])
                            except ValueError:
                                pass
                        elif p.startswith("-"):
                            try:
                                behind = int(p[1:])
                            except ValueError:
                                pass

                # Changed entries (porcelain v2 format)
                elif line.startswith("1 ") or line.startswith("2 "):
                    parts = line.split('\t')
                    status_info = parts[0].split()
                    file_path = parts[-1] if '\t' in line else status_info[-1]

                    xy = status_info[1] if len(status_info) > 1 else ".."

                    # X = staged status, Y = unstaged status
                    if len(xy) >= 2:
                        if xy[0] != '.':
                            staged.append({
                                "file": file_path,
                                "status": self._status_char(xy[0])
                            })
                        if xy[1] != '.':
                            unstaged.append({
                                "file": file_path,
                                "status": self._status_char(xy[1])
                            })

                # Untracked
                elif line.startswith("? "):
                    untracked.append(line[2:].strip())

            # Build output
            output_parts = []
            output_parts.append(f"Branch: {branch}")
            if upstream:
                output_parts.append(f"Upstream: {upstream}")
                if ahead or behind:
                    output_parts.append(f"  Ahead: {ahead}, Behind: {behind}")

            output_parts.append("")

            if staged:
                output_parts.append(f"Staged ({len(staged)}):")
                for s in staged:
                    output_parts.append(f"  [{s['status']}] {s['file']}")

            if unstaged:
                output_parts.append(f"\nUnstaged ({len(unstaged)}):")
                for u in unstaged:
                    output_parts.append(f"  [{u['status']}] {u['file']}")

            if untracked:
                output_parts.append(f"\nUntracked ({len(untracked)}):")
                for ut in untracked:
                    output_parts.append(f"  {ut}")

            if not staged and not unstaged and not untracked:
                output_parts.append("Working tree clean — nothing to commit.")

            result.output = '\n'.join(output_parts)
            result.metadata = {
                "branch": branch,
                "upstream": upstream,
                "ahead": ahead,
                "behind": behind,
                "staged_count": len(staged),
                "unstaged_count": len(unstaged),
                "untracked_count": len(untracked),
                "clean": not staged and not unstaged and not untracked
            }

        except subprocess.TimeoutExpired:
            result.error = "git status timed out"
            result.success = False
        except Exception as e:
            result.error = str(e)
            result.success = False
        finally:
            result.set_finished()

        return result

    def _status_char(self, c: str) -> str:
        """Convert porcelain status character to readable string"""
        mapping = {
            'M': 'modified', 'A': 'added', 'D': 'deleted',
            'R': 'renamed', 'C': 'copied', 'T': 'type-changed',
            'U': 'unmerged', '?': 'untracked', '!': 'ignored'
        }
        return mapping.get(c, c)


class GitDiffTool(Tool):
    """Show git diff of changes"""
    name = "git_diff"
    description = "Show the diff of changes in the git repository"
    category = "git"
    requires_confirmation = False
    max_output_length = 30000

    parameters = [
        ToolParameter("path", "string", "Repository path", False, "."),
        ToolParameter("staged", "boolean", "Show only staged changes", False, False),
        ToolParameter("file", "string", "Diff a specific file only", False, ""),
        ToolParameter("ref1", "string", "First commit/branch reference", False, ""),
        ToolParameter("ref2", "string", "Second commit/branch reference", False, ""),
        ToolParameter("stat_only", "boolean", "Show only file stats, not full diff", False, False)
    ]

    def execute(self, params: Dict[str, Any]) -> ToolResult:
        result = ToolResult(tool_name=self.name)

        try:
            path = params.get("path", ".")
            staged = params.get("staged", False)
            file_path = params.get("file", "")
            ref1 = params.get("ref1", "")
            ref2 = params.get("ref2", "")
            stat_only = params.get("stat_only", False)

            repo_path = Path(self.working_dir) / path

            if not (repo_path / ".git").exists():
                result.error = f"Not a git repository: {repo_path}"
                result.success = False
                return result

            # Build command
            cmd = ["git", "diff", "--no-color"]

            if stat_only:
                cmd.append("--stat")

            if staged:
                cmd.append("--cached")
            elif ref1:
                if ref2:
                    cmd.append(f"{ref1}...{ref2}")
                else:
                    cmd.append(ref1)

            if file_path:
                cmd.extend(["--", file_path])

            proc = subprocess.run(
                cmd, capture_output=True, text=True,
                cwd=str(repo_path), timeout=30
            )

            diff_output = proc.stdout

            if not diff_output.strip():
                mode = "staged" if staged else "unstaged"
                if ref1:
                    mode = f"{ref1}...{ref2}" if ref2 else ref1
                result.output = f"No {mode} changes found."
                result.metadata = {"files_changed": 0, "insertions": 0, "deletions": 0}
                return result

            # Count stats
            files_changed = 0
            insertions = 0
            deletions = 0
            changed_files = []

            for line in diff_output.split('\n'):
                if line.startswith('diff --git'):
                    files_changed += 1
                    # Extract filename: "diff --git a/file b/file" -> "file"
                    parts = line.split(' b/')
                    if len(parts) > 1:
                        changed_files.append(parts[-1])
                elif line.startswith('+') and not line.startswith('+++'):
                    insertions += 1
                elif line.startswith('-') and not line.startswith('---'):
                    deletions += 1

            # Truncate if needed
            diff_output = self.truncate_output(diff_output)

            # Build header
            mode = "Staged" if staged else "Unstaged"
            if ref1:
                mode = f"{ref1}...{ref2}" if ref2 else f"vs {ref1}"

            header = f"{mode} changes: {files_changed} file(s), +{insertions} -{deletions}\n"
            if changed_files:
                header += "Files: " + ", ".join(changed_files[:10])
                if len(changed_files) > 10:
                    header += f" ... and {len(changed_files) - 10} more"
                header += "\n"

            result.output = header + "\n" + diff_output
            result.metadata = {
                "files_changed": files_changed,
                "insertions": insertions,
                "deletions": deletions,
                "changed_files": changed_files[:20],
                "mode": mode
            }

        except subprocess.TimeoutExpired:
            result.error = "git diff timed out"
            result.success = False
        except Exception as e:
            result.error = str(e)
            result.success = False
        finally:
            result.set_finished()

        return result


class GitCommitTool(Tool):
    """Create a git commit"""
    name = "git_commit"
    description = "Stage files and create a git commit with a message"
    category = "git"
    requires_confirmation = True

    parameters = [
        ToolParameter("message", "string", "Commit message", True),
        ToolParameter("files", "array", "Files to stage (empty = all)", False, []),
        ToolParameter("path", "string", "Repository path", False, "."),
        ToolParameter("amend", "boolean", "Amend the last commit", False, False)
    ]

    def execute(self, params: Dict[str, Any]) -> ToolResult:
        result = ToolResult(tool_name=self.name)

        try:
            message = params.get("message", "").strip()
            files = params.get("files", [])
            path = params.get("path", ".")
            amend = params.get("amend", False)

            if not message and not amend:
                result.error = "Commit message is required"
                result.success = False
                return result

            repo_path = Path(self.working_dir) / path

            if not (repo_path / ".git").exists():
                result.error = f"Not a git repository: {repo_path}"
                result.success = False
                return result

            # Stage files
            if files:
                for f in files:
                    proc = subprocess.run(
                        ["git", "add", f],
                        capture_output=True, text=True,
                        cwd=str(repo_path), timeout=10
                    )
                    if proc.returncode != 0:
                        result.error = f"Failed to stage {f}: {proc.stderr.strip()}"
                        result.success = False
                        return result
            else:
                # Stage all changes
                proc = subprocess.run(
                    ["git", "add", "-A"],
                    capture_output=True, text=True,
                    cwd=str(repo_path), timeout=10
                )
                if proc.returncode != 0:
                    result.error = f"Failed to stage files: {proc.stderr.strip()}"
                    result.success = False
                    return result

            # Check if there are staged changes
            check = subprocess.run(
                ["git", "diff", "--cached", "--quiet"],
                capture_output=True, cwd=str(repo_path), timeout=5
            )

            if check.returncode == 0 and not amend:
                result.error = "Nothing to commit — no staged changes"
                result.success = False
                return result

            # Create commit
            cmd = ["git", "commit"]
            if amend:
                cmd.append("--amend")
            if message:
                cmd.extend(["-m", message])

            proc = subprocess.run(
                cmd, capture_output=True, text=True,
                cwd=str(repo_path), timeout=15
            )

            if proc.returncode != 0:
                result.error = f"Commit failed: {proc.stderr.strip()}"
                result.success = False
                return result

            # Get the commit hash
            hash_proc = subprocess.run(
                ["git", "rev-parse", "--short", "HEAD"],
                capture_output=True, text=True,
                cwd=str(repo_path), timeout=5
            )
            commit_hash = hash_proc.stdout.strip()

            # Get commit stats
            stat_proc = subprocess.run(
                ["git", "diff", "--stat", "HEAD~1..HEAD"],
                capture_output=True, text=True,
                cwd=str(repo_path), timeout=5
            )

            output = f"Committed: {commit_hash}\n"
            output += f"Message: {message}\n"
            if stat_proc.stdout:
                output += f"\n{stat_proc.stdout.strip()}"

            result.output = output
            result.metadata = {
                "commit_hash": commit_hash,
                "message": message,
                "files_committed": len(files) if files else "all",
                "amend": amend
            }

        except subprocess.TimeoutExpired:
            result.error = "git commit timed out"
            result.success = False
        except Exception as e:
            result.error = str(e)
            result.success = False
        finally:
            result.set_finished()

        return result


class GitLogTool(Tool):
    """Show git commit history"""
    name = "git_log"
    description = "Show the git commit history with formatting options"
    category = "git"
    requires_confirmation = False

    parameters = [
        ToolParameter("path", "string", "Repository path", False, "."),
        ToolParameter("count", "integer", "Number of commits to show", False, 10),
        ToolParameter("oneline", "boolean", "One line per commit", False, True),
        ToolParameter("file", "string", "Show history for specific file", False, ""),
        ToolParameter("author", "string", "Filter by author name", False, ""),
        ToolParameter("since", "string", "Show since date (e.g., '2 weeks ago')", False, ""),
        ToolParameter("graph", "boolean", "Show branch graph", False, False)
    ]

    def execute(self, params: Dict[str, Any]) -> ToolResult:
        result = ToolResult(tool_name=self.name)

        try:
            path = params.get("path", ".")
            count = min(params.get("count", 10), 100)  # Cap at 100
            oneline = params.get("oneline", True)
            file_path = params.get("file", "")
            author = params.get("author", "")
            since = params.get("since", "")
            graph = params.get("graph", False)

            repo_path = Path(self.working_dir) / path

            if not (repo_path / ".git").exists():
                result.error = f"Not a git repository: {repo_path}"
                result.success = False
                return result

            # Build command with a separator for reliable parsing
            separator = "|||TIDE_SEP|||"
            fmt = f"%h{separator}%an{separator}%ar{separator}%s"

            cmd = ["git", "log", f"-n{count}", f"--pretty=format:{fmt}"]

            if graph:
                cmd.append("--graph")

            if author:
                cmd.append(f"--author={author}")

            if since:
                cmd.append(f"--since={since}")

            if file_path:
                cmd.extend(["--", file_path])

            proc = subprocess.run(
                cmd, capture_output=True, text=True,
                cwd=str(repo_path), timeout=15
            )

            if proc.returncode != 0:
                result.error = f"git log failed: {proc.stderr.strip()}"
                result.success = False
                return result

            # Parse output
            commits = []
            output_lines = []

            for line in proc.stdout.strip().split('\n'):
                if not line or separator not in line:
                    if graph and line:
                        output_lines.append(line)
                    continue

                parts = line.split(separator)
                if len(parts) >= 4:
                    commit = {
                        "hash": parts[0].strip(),
                        "author": parts[1].strip(),
                        "date": parts[2].strip(),
                        "message": parts[3].strip()
                    }
                    commits.append(commit)

                    if oneline:
                        output_lines.append(
                            f"  {commit['hash']}  {commit['date']:>15}  {commit['author']:<20}  {commit['message'][:60]}"
                        )
                    else:
                        output_lines.append(f"commit {commit['hash']}")
                        output_lines.append(f"Author: {commit['author']}")
                        output_lines.append(f"Date:   {commit['date']}")
                        output_lines.append(f"\n    {commit['message']}\n")

            header = f"Commit history ({len(commits)} commits):\n\n"
            result.output = header + '\n'.join(output_lines)
            result.metadata = {
                "commit_count": len(commits),
                "commits": commits[:20]  # First 20 for metadata
            }

        except subprocess.TimeoutExpired:
            result.error = "git log timed out"
            result.success = False
        except Exception as e:
            result.error = str(e)
            result.success = False
        finally:
            result.set_finished()

        return result
