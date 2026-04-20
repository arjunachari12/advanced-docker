from __future__ import annotations

import unittest
from unittest.mock import patch

from agent import local_plan, normalize_ollama_answer, run_agent


class AgentTest(unittest.TestCase):
    def test_local_plan_mentions_task(self) -> None:
        plan = local_plan("ship a secure image")
        self.assertIn("ship a secure image", plan)
        self.assertIn("Agent plan:", plan)
        self.assertIn("publish-agent", plan)

    def test_run_agent_can_use_local_planner_offline(self) -> None:
        plan = run_agent("test the agent", use_ollama=False)
        self.assertIn("test the agent", plan)
        self.assertIn("test-agent", plan)

    def test_run_agent_uses_ollama_when_available(self) -> None:
        with patch("agent.ollama_plan", return_value="1. Build\n2. Scan\n3. Push"):
            plan = run_agent("ship the agent", use_ollama=True)

        self.assertEqual(plan, "1. Build\n2. Scan\n3. Push")

    def test_ollama_answer_is_trimmed_to_three_steps(self) -> None:
        plan = normalize_ollama_answer("1. Build\n2. Test\n3. Scan\n4. Push", "ship")
        self.assertEqual(plan, "1. Build\n2. Test\n3. Scan")

    def test_free_form_ollama_answer_gets_normalized(self) -> None:
        plan = normalize_ollama_answer("Use docker build and then push it.", "ship a secure image")
        self.assertIn("Agent plan:", plan)
        self.assertIn("Ollama note:", plan)


if __name__ == "__main__":
    unittest.main()
