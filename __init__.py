from __future__ import annotations

from typing_extensions import override

from comfy_api.latest import ComfyExtension

from .oai_bridge.nodes_image import OAIImageNode
from .oai_bridge.nodes_video import OAIVideoNode
from .oai_bridge.nodes_seedance_asset import OAISeedanceAssetNode
from .oai_bridge.nodes_llm import OAILLMNode
from .oai_bridge.routes import register_routes

register_routes()


class OAIBridgeExtension(ComfyExtension):
    @override
    async def get_node_list(self):
        return [OAIImageNode, OAIVideoNode, OAISeedanceAssetNode, OAILLMNode]


async def comfy_entrypoint() -> OAIBridgeExtension:
    return OAIBridgeExtension()


