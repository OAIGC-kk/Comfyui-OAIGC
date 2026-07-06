from pathlib import Path
import unittest

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib


class PanelEntryTests(unittest.TestCase):
    def test_web_extension_name_is_url_safe(self):
        pyproject = Path("pyproject.toml")
        self.assertTrue(pyproject.exists(), "pyproject.toml is required for a URL-safe frontend extension name")

        data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
        self.assertEqual(data["project"]["name"], "oai-bridge")
        self.assertEqual(data["tool"]["comfy"]["web"], "web")

    def test_legacy_space_named_web_directory_is_not_registered(self):
        init_py = Path("__init__.py").read_text(encoding="utf-8")
        self.assertNotIn("WEB_DIRECTORY", init_py)

    def test_panel_uses_floating_button_without_hidden_legacy_menu(self):
        js = Path("web/oai_bridge_panel.js").read_text(encoding="utf-8")

        self.assertIn("ensurePanelEntry", js)
        self.assertIn("oai-bridge-floating-entry", js)
        self.assertIn("document.body.appendChild", js)
        self.assertNotIn("extensions/OAI Bridge", js)
        self.assertNotIn(".comfy-menu", js)
        self.assertNotIn("legacyMenu", js)

    def test_panel_entry_is_top_centered(self):
        css = Path("web/oai_bridge_panel.css").read_text(encoding="utf-8")

        self.assertIn(".oai-bridge-floating-entry", css)
        self.assertIn("left: 50%", css)
        self.assertIn("transform: translateX(-50%)", css)
        self.assertNotIn("right: 16px", css)

    def test_panel_hides_backend_urls_and_links_token_site(self):
        js = Path("web/oai_bridge_panel.js").read_text(encoding="utf-8")

        self.assertNotIn("baseUrl", js)
        self.assertNotIn("base_url", js)
        self.assertNotIn("uploadUrl", js)
        self.assertNotIn("upload_url", js)
        self.assertNotIn("API 地址", js)
        self.assertNotIn("上传地址", js)
        self.assertIn("https://oaigc.cn", js)
        self.assertIn("tokenLink", js)
        self.assertIn("\\u83b7\\u53d6 API Token", js)

    def test_panel_loads_nodes_and_click_adds_node_to_graph(self):
        js = Path("web/oai_bridge_panel.js").read_text(encoding="utf-8")

        self.assertIn("/oai-bridge/nodes", js)
        self.assertIn("projectNodes", js)
        self.assertIn("\\u9879\\u76ee\\u8282\\u70b9", js)
        self.assertIn("node-list", js)
        self.assertIn("addNodeToGraph", js)
        self.assertIn("LiteGraph.createNode", js)
        self.assertIn("app.graph.add", js)
        self.assertIn("data-node-type", js)

    def test_image_node_widgets_are_filtered_by_selected_model(self):
        js = Path("web/oai_bridge_panel.js").read_text(encoding="utf-8")

        self.assertIn("beforeRegisterNodeDef", js)
        self.assertIn("OAIImageNode", js)
        self.assertIn("updateOAIImageWidgetVisibility", js)
        self.assertIn("MODEL_VISIBLE_WIDGETS", js)
        self.assertIn("Agnes Image 2.1 Flash", js)
        self.assertIn("\\u5206\\u8fa8\\u7387", js)
        self.assertIn("AI\\u6263\\u56fe", js)
        self.assertIn("AI\\u6269\\u56fe", js)
        self.assertIn("\\u5411\\u4e0a\\u6269\\u5c55", js)
        self.assertNotIn("widget.type = \"hidden\"", js)
        self.assertIn("draw: widget.draw", js)
        self.assertIn("widget.draw = () => {};", js)
        self.assertIn("restoreLegacyHiddenWidget", js)
        self.assertIn("BANANA_MODELS_WITH_HD", js)
        self.assertIn("getSelectedBananaModel", js)
        self.assertIn("patchOAIImageBananaModelWidget", js)
        self.assertIn("ALI_SUPPORTED_ASPECT_RATIOS", js)
        self.assertIn("normalizeOAIImageWidgetValues", js)
        self.assertIn("widget.type === \"hidden\"", js)
        self.assertIn("widget.hidden = false", js)
        self.assertIn("widget.disabled = false", js)
        self.assertIn("setSize", js)
        self.assertIn("OAIVideoNode", js)
        self.assertIn("ADVANCED_WIDGET_NAMES", js)
        self.assertIn("installOAIVideoWidgetFilter", js)
        self.assertIn("VIDEO_MODEL_VISIBLE_WIDGETS", js)
        self.assertIn("updateOAIVideoWidgetVisibility", js)
        self.assertIn("patchOAIVideoModelWidget", js)
        self.assertNotIn("seedance2.0-visio", js)
        self.assertNotIn("seedance2.0-fast-vision", js)
        self.assertNotIn("\\u53c2\\u8003\\u89c6\\u9891URL", js)


    def test_hidden_widgets_use_comfy_hidden_flags(self):
        js = Path("web/oai_bridge_panel.js").read_text(encoding="utf-8")

        self.assertIn("widget.hidden = true", js)
        self.assertIn("widget.disabled = true", js)

    def test_cutout_model_does_not_show_prompt_widget(self):
        js = Path("web/oai_bridge_panel.js").read_text(encoding="utf-8")

        self.assertIn("[\"AI\\u6263\\u56fe\"]: []", js)
        self.assertIn("IMAGE_FIELD.prompt", js)

if __name__ == "__main__":
    unittest.main()






