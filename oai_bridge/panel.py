from __future__ import annotations

from typing import Any


def get_project_nodes() -> list[dict[str, Any]]:
    return [
        {
            "node_id": "OAIImageNode",
            "display_name": "OAI \u56fe\u50cf",
            "category": "OAI Bridge/\u56fe\u50cf",
            "description": "\u6587\u751f\u56fe\u3001\u56fe\u751f\u56fe\u3001\u56fe\u50cf\u7f16\u8f91\u7b49\u56fe\u50cf\u7c7b\u80fd\u529b\u7edf\u4e00\u5165\u53e3\u3002",
            "inputs": ["\u5e94\u7528", "\u63d0\u793a\u8bcd", "\u56fe\u72471", "\u56fe\u72472", "\u56fe\u72473", "\u753b\u9762\u6bd4\u4f8b", "\u6570\u91cf"],
            "outputs": ["\u56fe\u50cf"],
        },
        {
            "node_id": "OAIVideoNode",
            "display_name": "OAI \u89c6\u9891",
            "category": "OAI Bridge/\u89c6\u9891",
            "description": "Seedance \u89c6\u9891\u3001\u56fe\u7247/\u89c6\u9891/\u97f3\u9891\u8f93\u5165\u548c Seedance \u56fe\u50cf\u8d44\u4ea7\u5f15\u7528\u7edf\u4e00\u5165\u53e3\u3002",
            "inputs": ["\u5e94\u7528", "\u89c6\u9891\u6a21\u578b", "\u63d0\u793a\u8bcd", "\u56fe\u72471", "\u89c6\u98911", "\u97f3\u98911", "\u56fe\u7247\u8d44\u4ea7ID1", "\u753b\u9762\u6bd4\u4f8b", "\u65f6\u957f", "\u6e05\u6670\u5ea6", "\u751f\u6210\u97f3\u9891"],
            "outputs": ["\u89c6\u9891"],
        },
        {
            "node_id": "OAISeedanceAssetNode",
            "display_name": "OAI Seedance \u56fe\u50cf\u8d44\u4ea7",
            "category": "OAI Bridge/\u89c6\u9891",
            "description": "\u628a ComfyUI \u56fe\u50cf\u8f93\u5165\u4e0a\u4f20\u5e76\u6ce8\u518c\u4e3a Seedance \u56fe\u50cf\u8d44\u4ea7\uff0c\u8f93\u51fa\u8d44\u4ea7 ID \u4f9b\u89c6\u9891\u8282\u70b9\u5f15\u7528\u3002",
            "inputs": ["\u56fe\u50cf", "\u8d44\u4ea7\u540d\u79f0"],
            "outputs": ["\u8d44\u4ea7ID"],
        },
        {
            "node_id": "OAILLMNode",
            "display_name": "OAI LLM \u5bf9\u8bdd",
            "category": "OAI Bridge/\u6587\u672c",
            "description": "\u8c03\u7528 OAI \u540e\u7aef LLM \u5bf9\u8bdd\u63a5\u53e3\uff0c\u8f93\u51fa\u6587\u672c\u56de\u590d\u5185\u5bb9\u3002",
            "inputs": ["\u6a21\u578b", "\u524d\u7f6e\u63d0\u793a\u8bcd", "\u7528\u6237\u8f93\u5165\u63d0\u793a\u8bcd", "\u56fe\u72471"],
            "outputs": ["\u56de\u590d\u5185\u5bb9"],
        },
    ]

