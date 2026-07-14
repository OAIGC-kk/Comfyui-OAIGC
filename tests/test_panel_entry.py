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
        self.assertNotIn("\u0041\u0050\u0049 \u5730\u5740", js)
        self.assertNotIn("\u4e0a\u4f20\u5730\u5740", js)
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
        self.assertIn("showWidget(widget)", js)
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

    def test_widget_layout_refresh_preserves_typed_array_node_sizes(self):
        js = Path("web/oai_bridge_panel.js").read_text(encoding="utf-8")

        self.assertIn("const currentSize = node.size || [0, 0];", js)
        self.assertIn("node.setSize([", js)
        self.assertIn("Math.max(currentSize[0] || 0, computedSize[0] || 0)", js)
        self.assertIn("Math.max(currentSize[1] || 0, computedSize[1] || 0)", js)
        self.assertNotIn("Array.isArray(node.size)", js)
        self.assertNotIn("node.setSize(node.computeSize())", js)

    def test_cutout_model_does_not_show_prompt_widget(self):
        js = Path("web/oai_bridge_panel.js").read_text(encoding="utf-8")

        self.assertIn("CUTOUT_IMAGE_MODEL", js)
        self.assertIn("[CUTOUT_IMAGE_MODEL]: []", js)
        self.assertIn("IMAGE_FIELD.prompt", js)



    def test_frontend_restricts_media_input_connections_by_type(self):
        js = Path("web/oai_bridge_panel.js").read_text(encoding="utf-8")

        self.assertIn("MEDIA_INPUT_RULES", js)
        self.assertIn("patchOAIInputConnectionTypes", js)
        self.assertIn("onConnectInput", js)
        self.assertIn("return false", js)
        self.assertIn("\"IMAGE\"", js)
        self.assertIn("\"VIDEO\"", js)
        self.assertIn("\"AUDIO\"", js)
        self.assertIn("OAIImageNode", js)
        self.assertIn("OAIVideoNode", js)
        self.assertIn("OAILLMNode", js)
        self.assertIn("OAISeedanceAssetNode", js)
        self.assertIn("numberedMediaFields(\"\\u56fe\\u7247\", 12, \"IMAGE\")", js)
        self.assertIn("numberedMediaFields(\"\\u56fe\\u7247\", 9, \"IMAGE\")", js)
        self.assertIn("numberedMediaFields(\"\\u89c6\\u9891\", 3, \"VIDEO\")", js)
        self.assertIn("numberedMediaFields(\"\\u97f3\\u9891\", 3, \"AUDIO\")", js)
        self.assertIn("\\u56fe\\u50cf", js)

    def test_frontend_displays_dynamic_cost_badge(self):
        js = Path("web/oai_bridge_panel.js").read_text(encoding="utf-8")

        self.assertIn("/oai-bridge/cost", js)
        self.assertIn(r'DEFAULT_IMAGE_MODEL = "GPT \u751f\u56fe"', js)
        self.assertIn("MODEL_COST_MODELS", js)
        self.assertIn("buildGptImageCostRequest", js)
        self.assertIn(r'COST_BADGE_TEXT = "O\u5e01"', js)
        self.assertIn("installOAICostBadge", js)
        self.assertIn("drawOAICostBadge", js)
        self.assertIn("refreshOAICost", js)
        self.assertIn("buildImageCostRequest", js)
        self.assertIn("buildBananaCostRequest", js)
        self.assertIn('appId: "banana"', js)
        self.assertIn("maybeRefreshOAICostFromDraw", js)
        self.assertIn("__oaiBridgeCostDrawCheckAt", js)
        self.assertIn("buildVideoCostRequest", js)
        self.assertIn("getCostRequestSignature", js)
        self.assertIn("__oaiBridgeCostSignature", js)
        self.assertIn("options.force", js)
        self.assertIn('setNodeCost(node, "...")', js)
        self.assertIn("scheduleOAICostRefresh(node, { force: true })", js)
        self.assertIn("return buildGptImageCostRequest(node)", js)
        self.assertIn('appId: "gpt-image"', js)
        self.assertNotIn('kind: "gpt_image"', js)
        self.assertIn("fast: asCostBool(getWidgetValue(node, IMAGE_FIELD.fast", js)
        self.assertNotIn("[DEFAULT_IMAGE_MODEL]: (node) =>", js)
        self.assertIn("resolution: getWidgetValue(node, IMAGE_FIELD.resolution", js)
        self.assertIn("n: Number(getWidgetValue(node, IMAGE_FIELD.count", js)
        self.assertIn("parameter.hd = asCostBool(getWidgetValue(node, IMAGE_FIELD.hd", js)
        self.assertIn("COST_BADGE_HEADER_Y = -54", js)
        self.assertIn("COST_BADGE_CATEGORY_RESERVED_WIDTH", js)
        self.assertIn("const y = COST_BADGE_HEADER_Y", js)
        self.assertIn('__oaiBridgeCostKind = "image"', js)
        self.assertIn('__oaiBridgeCostKind === "image"', js)
        self.assertIn('__oaiBridgeCostKind = "video"', js)
        self.assertIn("workflow_app_cost", Path("oai_bridge/client.py").read_text(encoding="utf-8"))
        self.assertIn("model_cost", Path("oai_bridge/client.py").read_text(encoding="utf-8"))
        self.assertIn("seedance_cost", Path("oai_bridge/client.py").read_text(encoding="utf-8"))

    def test_frontend_restores_saved_previews_from_history(self):
        js = Path("web/oai_bridge_panel.js").read_text(encoding="utf-8")

        self.assertIn("restoreNodePreviewsFromHistory", js)
        self.assertIn("findLatestHistoryOutputs", js)
        self.assertIn("/history", js)
        self.assertIn("node.images = null", js)
        self.assertIn("node.imgs = null", js)
        self.assertIn("app.graph?.setDirtyCanvas", js)
        self.assertIn("comfyApi.addEventListener?.(\"graphChanged\"", js)

    def test_frontend_persists_native_preview_images_on_execution(self):
        js = Path("web/oai_bridge_panel.js").read_text(encoding="utf-8")

        self.assertIn("PREVIEW_PROPERTY", js)
        self.assertIn("rememberNodePreviewImages", js)
        self.assertIn("getStoredPreviewImages", js)
        self.assertIn("patchPreviewRestoreExecution", js)
        self.assertIn("onExecuted", js)
        self.assertIn("oaiBridgePreviewOnConfigure", js)
        self.assertIn("applyStoredNodePreview(this)", js)
        self.assertIn("writeNativePreviewOutput", js)
        self.assertNotIn("node.previewImages", js)
        self.assertNotIn("ctx.drawImage", js)
        self.assertNotIn("prototype.onDrawBackground", js)

    def test_frontend_schedules_preview_restore_when_graph_loads(self):
        js = Path("web/oai_bridge_panel.js").read_text(encoding="utf-8")

        self.assertIn("oai.bridge.preview-restore", js)
        self.assertIn("nodeCreated(node)", js)
        self.assertIn("loadedGraphNode(node)", js)
        self.assertIn("afterConfigureGraph()", js)
        self.assertIn("schedulePreviewRestore(2500)", js)

    def test_frontend_restores_save_image_preview_from_upstream_node(self):
        js = Path("web/oai_bridge_panel.js").read_text(encoding="utf-8")

        self.assertIn("getUpstreamImageNodeIds", js)
        self.assertIn("getCandidateOutputIdsForNode", js)
        self.assertIn("getLinkSourceNode", js)
        self.assertIn("input?.link", js)
        self.assertIn("outputs?.[String(outputId)]", js)

if __name__ == "__main__":
    unittest.main()

