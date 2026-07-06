from pathlib import Path
import unittest


class ComfyRegistrationTests(unittest.TestCase):
    def test_advanced_workflow_is_not_registered_in_comfy_node_menu(self):
        init_py = Path("__init__.py").read_text(encoding="utf-8")

        self.assertNotIn("OAIAdvancedWorkflowNode", init_py)
        self.assertIn("OAIImageNode", init_py)
        self.assertIn("OAIVideoNode", init_py)
        self.assertIn("OAISeedanceAssetNode", init_py)
        self.assertIn("OAILLMNode", init_py)


if __name__ == "__main__":
    unittest.main()
