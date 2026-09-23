"""Exercise the Codex wrappers' real hook commands without running an agent."""

import json
import subprocess
import tempfile
import tomllib
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


class AgentGuardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.agents = {
            path.stem: tomllib.loads(path.read_text(encoding="utf-8"))
            for path in (REPO / ".codex" / "agents").glob("*.toml")
        }

    def run_hook(self, agent, event, cwd=REPO):
        command = self.agents[agent]["hooks"]["PreToolUse"][0]["hooks"][0]["command"]
        result = subprocess.run(
            command, input=json.dumps(event), text=True, shell=True, cwd=cwd,
            capture_output=True, timeout=15,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout) if result.stdout.strip() else {}

    def patch(self, body, cwd=REPO):
        return {
            "hook_event_name": "PreToolUse",
            "cwd": str(cwd),
            "tool_name": "apply_patch",
            "tool_input": {"command": f"*** Begin Patch\n{body}\n*** End Patch"},
        }

    def assert_denied(self, result):
        output = result["hookSpecificOutput"]
        self.assertEqual(output["hookEventName"], "PreToolUse")
        self.assertEqual(output["permissionDecision"], "deny")
        self.assertTrue(output["permissionDecisionReason"])

    def test_review_add_update_delete_and_move_inside_boundary(self):
        bodies = [
            "*** Add File: build/reviews/new.md\n+Review",
            "*** Update File: build/reviews/old.md\n@@\n-old\n+new",
            "*** Delete File: build/reviews/old.md",
            "*** Update File: build/reviews/old.md\n*** Move to: build/reviews/new.md\n@@\n-old\n+new",
        ]
        for body in bodies:
            with self.subTest(body=body):
                self.assertEqual(self.run_hook("nesa-assessor", self.patch(body)), {})

    def test_review_rejects_one_forbidden_file_in_a_batch(self):
        body = "*** Add File: build/reviews/new.md\n+Review\n*** Delete File: docs/agents.md"
        self.assert_denied(self.run_hook("nesa-assessor", self.patch(body)))

    def test_review_rejects_both_directions_of_a_move_across_boundary(self):
        for source, target in [
            ("build/reviews/old.md", "docs/new.md"),
            ("docs/old.md", "build/reviews/new.md"),
        ]:
            with self.subTest(source=source):
                body = f"*** Update File: {source}\n*** Move to: {target}\n@@\n-old\n+new"
                self.assert_denied(self.run_hook("nesa-assessor", self.patch(body)))

    def test_review_rejects_traversal_and_sibling_prefixes(self):
        for target in ["build/reviews/../../docs/new.md", "build/reviews-other/new.md", str(REPO / "README.md")]:
            with self.subTest(target=target):
                self.assert_denied(self.run_hook("nesa-assessor", self.patch(f"*** Add File: {target}\n+x")))

    def test_review_resolves_event_cwd_and_launcher_from_subdirectory(self):
        cwd = REPO / "docs"
        event = self.patch("*** Add File: ../build/reviews/new.md\n+x", cwd)
        self.assertEqual(self.run_hook("nesa-assessor", event, cwd), {})
        event = self.patch("*** Add File: build/reviews/new.md\n+x", cwd)
        self.assert_denied(self.run_hook("nesa-assessor", event, cwd))

    def test_review_rejects_symlink_escape(self):
        folder = REPO / "build" / "reviews"
        folder.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=folder) as temporary:
            link = Path(temporary) / "outside"
            try:
                link.symlink_to(REPO / "docs", target_is_directory=True)
            except OSError as exc:
                self.skipTest(f"Creating a symbolic link is unavailable: {exc}")
            event = self.patch(f"*** Add File: {link / 'new.md'}\n+x")
            self.assert_denied(self.run_hook("nesa-assessor", event))

    def test_review_keeps_claude_file_events(self):
        for tool, key in [("Edit", "file_path"), ("Write", "file_path"), ("NotebookEdit", "notebook_path")]:
            with self.subTest(tool=tool):
                event = {"tool_name": tool, "tool_input": {key: "build/reviews/new.md"}}
                self.assertEqual(self.run_hook("nesa-assessor", event), {})
                event["tool_input"][key] = "design-system/deck.css"
                self.assert_denied(self.run_hook("nesa-assessor", event))

    def test_review_keeps_vscode_file_events(self):
        for tool, key in [("create_file", "filePath"), ("replace_string_in_file", "filePath"),
                          ("edit_notebook_file", "notebookPath")]:
            with self.subTest(tool=tool):
                event = {"tool_name": tool, "tool_input": {key: "build/reviews/new.md"}}
                self.assertEqual(self.run_hook("nesa-assessor", event), {})
                event["tool_input"][key] = "design-system/deck.css"
                self.assert_denied(self.run_hook("nesa-assessor", event))

    def test_review_denies_unreadable_edit_inputs(self):
        for event in [None, [], {"tool_name": "apply_patch"},
                      {"tool_name": "apply_patch", "tool_input": {"command": "not a patch"}},
                      {"tool_name": "Write", "tool_input": {}}]:
            with self.subTest(event=event):
                self.assert_denied(self.run_hook("nesa-assessor", event))

    def test_canva_denies_direct_edits_even_in_output(self):
        for target in ["build/canva/out.html", "canva.local.json", "design-system/deck.css"]:
            with self.subTest(target=target):
                self.assert_denied(self.run_hook("canva-sync", self.patch(f"*** Add File: {target}\n+x")))
                event = {"tool_name": "Write", "tool_input": {"file_path": target}}
                self.assert_denied(self.run_hook("canva-sync", event, REPO / "docs"))

    def test_canva_denies_unreadable_event(self):
        self.assert_denied(self.run_hook("canva-sync", None))

    def test_hooks_leave_read_and_execute_tools_to_host_permissions(self):
        for agent in self.agents:
            for tool in ["Read", "Bash"]:
                with self.subTest(agent=agent, tool=tool):
                    self.assertEqual(self.run_hook(agent, {"tool_name": tool, "tool_input": {}}), {})


if __name__ == "__main__":
    unittest.main()
