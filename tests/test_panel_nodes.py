import unittest


class PanelNodesTests(unittest.TestCase):
    def test_project_nodes_are_listed_in_chinese(self):
        from oai_bridge.panel import get_project_nodes

        nodes = get_project_nodes()
        self.assertEqual([node["display_name"] for node in nodes], ["OAI \u56fe\u50cf", "OAI \u89c6\u9891", "OAI Seedance \u56fe\u50cf\u8d44\u4ea7", "OAI LLM \u5bf9\u8bdd"])
        self.assertEqual([node["node_id"] for node in nodes], ["OAIImageNode", "OAIVideoNode", "OAISeedanceAssetNode", "OAILLMNode"])
        self.assertTrue(all(node["category"].startswith("OAI Bridge/") for node in nodes))
        self.assertTrue(all(node["description"] for node in nodes))
        video_node = next(node for node in nodes if node["node_id"] == "OAIVideoNode")
        self.assertIn("\u56fe\u7247\u8d44\u4ea7ID1", video_node["inputs"])
        self.assertNotIn("\u89c6\u9891\u8d44\u4ea7ID1", video_node["inputs"])
        self.assertNotIn("\u97f3\u9891\u8d44\u4ea7ID1", video_node["inputs"])
        asset_node = next(node for node in nodes if node["node_id"] == "OAISeedanceAssetNode")
        self.assertEqual(asset_node["inputs"], ["\u56fe\u50cf", "\u8d44\u4ea7\u540d\u79f0"])
        for node in nodes:
            self.assertNotIn("\u9ad8\u7ea7\u53c2\u6570JSON", node["inputs"])


if __name__ == "__main__":
    unittest.main()

