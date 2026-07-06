from __future__ import annotations

import json

from comfy_api.latest import IO

from .tasks import run_app

MODE_FIELD = "\u6a21\u5f0f"
APP_ID_FIELD = "\u5e94\u7528ID"
PARAMS_FIELD = "\u53c2\u6570JSON"
MODE_TASK = "\u901a\u7528\u4efb\u52a1"
MODE_BANANA = "Banana\u540c\u6b65"
MODE_SEEDANCE = "Seedance"


class OAIAdvancedWorkflowNode(IO.ComfyNode):
    @classmethod
    def define_schema(cls):
        return IO.Schema(
            node_id="OAIAdvancedWorkflowNode",
            display_name="OAI \u9ad8\u7ea7\u5de5\u4f5c\u6d41",
            category="OAI Bridge/\u9ad8\u7ea7",
            description="\u4f7f\u7528\u5e94\u7528 ID \u548c JSON \u53c2\u6570\u76f4\u63a5\u8c03\u7528 OAI \u540e\u7aef\uff0c\u8fd4\u56de\u7ed3\u679c\u94fe\u63a5\u3002",
            inputs=[
                IO.Combo.Input(MODE_FIELD, options=[MODE_TASK, MODE_BANANA, MODE_SEEDANCE], tooltip="\u9009\u62e9\u540e\u7aef\u8c03\u7528\u6a21\u5f0f\u3002"),
                IO.String.Input(APP_ID_FIELD, default="", tooltip="\u540e\u7aef appId\u3002"),
                IO.String.Input(PARAMS_FIELD, multiline=True, default="{}", tooltip="\u53d1\u9001\u7ed9\u540e\u7aef\u7684\u53c2\u6570 JSON\u3002"),
            ],
            outputs=[IO.String.Output(display_name="\u7ed3\u679c\u94fe\u63a5")],
        )

    @classmethod
    async def execute(cls, **kwargs):
        mode = kwargs[MODE_FIELD]
        app_id = kwargs[APP_ID_FIELD]
        params_json = kwargs[PARAMS_FIELD]
        try:
            parameter = json.loads(params_json or "{}")
        except json.JSONDecodeError as exc:
            raise ValueError("\u53c2\u6570JSON \u683c\u5f0f\u4e0d\u6b63\u786e\u3002") from exc
        mode_map = {MODE_TASK: "task_submit", MODE_BANANA: "banana_sync", MODE_SEEDANCE: "seedance"}
        app = {"id": app_id, "mode": mode_map[mode]}
        url = await run_app(app, parameter)
        return IO.NodeOutput(url)