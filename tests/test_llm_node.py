import asyncio
import sys
import types
import unittest


def _install_fake_comfy_io():
    class FakeInput:
        def __init__(self, name, options=None, **kwargs):
            self.name = name
            self.options = options
            self.kwargs = kwargs

    class FakeOutput:
        def __init__(self, *args, **kwargs):
            self.args = args
            self.kwargs = kwargs

    class FakeSchema:
        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)

    class FakeNodeOutput:
        def __init__(self, *args, **kwargs):
            self.args = args
            self.kwargs = kwargs

    class FakeIO:
        class ComfyNode:
            pass

        class Schema(FakeSchema):
            pass

        NodeOutput = FakeNodeOutput

        class Combo:
            Input = FakeInput

        class String:
            Input = FakeInput
            Output = FakeOutput

        class Image:
            Input = FakeInput

    comfy_api = types.ModuleType("comfy_api")
    latest = types.ModuleType("comfy_api.latest")
    latest.IO = FakeIO
    sys.modules["comfy_api"] = comfy_api
    sys.modules["comfy_api.latest"] = latest


class LLMNodeTests(unittest.TestCase):
    def test_schema_exposes_documented_dialogue_fields_without_video_or_advanced_inputs(self):
        _install_fake_comfy_io()

        from oai_bridge.nodes_llm import OAILLMNode

        schema = OAILLMNode.define_schema()
        input_names = [item.name for item in schema.inputs]

        self.assertEqual(schema.node_id, "OAILLMNode")
        self.assertEqual(schema.display_name, "OAI LLM \u5bf9\u8bdd")
        self.assertEqual(schema.category, "OAI Bridge/\u6587\u672c")
        self.assertEqual([output.kwargs.get("display_name") for output in schema.outputs], ["\u56de\u590d\u5185\u5bb9"])
        self.assertIn("\u6a21\u578b", input_names)
        self.assertIn("\u524d\u7f6e\u63d0\u793a\u8bcd", input_names)
        self.assertIn("\u7528\u6237\u8f93\u5165\u63d0\u793a\u8bcd", input_names)
        self.assertIn("\u56fe\u72471", input_names)
        self.assertNotIn("\u89c6\u9891\u5730\u5740", input_names)
        self.assertNotIn("\u9ad8\u7ea7\u53c2\u6570JSON", input_names)

    def test_schema_model_combo_uses_default_model_options(self):
        _install_fake_comfy_io()

        from oai_bridge.nodes_llm import LLM_MODEL_OPTIONS, OAILLMNode

        schema = OAILLMNode.define_schema()
        model_input = next(item for item in schema.inputs if item.name == "\u6a21\u578b")

        self.assertEqual(
            LLM_MODEL_OPTIONS,
            [
                "gpt-5.4",
                "gpt-5.5",
                "claude-opus-4-8",
                "claude-opus-4-7",
                "gemini-3.1-pro-preview",
                "gemini-3-flash-preview",
            ],
        )
        self.assertEqual(model_input.options, LLM_MODEL_OPTIONS)
        self.assertEqual(model_input.kwargs.get("default"), "gpt-5.5")

    def test_schema_exposes_six_optional_image_inputs(self):
        _install_fake_comfy_io()

        from oai_bridge.nodes_llm import OAILLMNode

        schema = OAILLMNode.define_schema()
        image_inputs = [item for item in schema.inputs if item.name.startswith("\u56fe\u7247")]

        self.assertEqual([item.name for item in image_inputs], [f"\u56fe\u7247{index}" for index in range(1, 7)])
        self.assertTrue(all(item.kwargs.get("optional") for item in image_inputs))

    def test_execute_returns_dialogue_content_and_sends_empty_video(self):
        _install_fake_comfy_io()

        import oai_bridge.nodes_llm as nodes_llm
        from oai_bridge.nodes_llm import OAILLMNode

        captured = {}

        async def fake_run_dialogue(parameter):
            captured.update(parameter)
            return "\u4f60\u597d\u5440"

        async def fake_upload_image_tensor(client, image, filename):
            return f"uploaded://{filename}"

        async def run_case():
            original_run_dialogue = nodes_llm.run_dialogue
            original_upload_image_tensor = nodes_llm.upload_image_tensor
            nodes_llm.run_dialogue = fake_run_dialogue
            nodes_llm.upload_image_tensor = fake_upload_image_tensor
            try:
                return await OAILLMNode.execute(
                    **{
                        nodes_llm.MODEL_FIELD: "gpt-5.4",
                        nodes_llm.SYSTEM_PROMPT_FIELD: "\u4f60\u662f\u52a9\u624b",
                        nodes_llm.USER_INPUT_FIELD: "\u4f60\u597d",
                        nodes_llm.IMAGE_FIELDS[0]: "image-tensor",
                    }
                )
            finally:
                nodes_llm.run_dialogue = original_run_dialogue
                nodes_llm.upload_image_tensor = original_upload_image_tensor

        output = asyncio.run(run_case())

        self.assertEqual(output.args, ("\u4f60\u597d\u5440",))
        self.assertEqual(captured["model"], "gpt-5.4")
        self.assertEqual(captured["system_prompt"], "\u4f60\u662f\u52a9\u624b")
        self.assertEqual(captured["user_input"], "\u4f60\u597d")
        self.assertEqual(captured["images"], ["uploaded://image_1.png"])
        self.assertEqual(captured["video"], "")


if __name__ == "__main__":
    unittest.main()