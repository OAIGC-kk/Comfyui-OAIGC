# ComfyUI-OAIGC / OAI Bridge

OAI Bridge 是一个面向 ComfyUI 的中文自定义节点插件，用于连接 OAIGC/OAI 统一 API 后端，在 ComfyUI 内完成图像、视频、Seedance 资产上传和 LLM 对话任务。

> 这是新版重构版本。旧版单文件节点实现已经废弃，本仓库现在只保留新的 `oai_bridge` 包结构和中文面板。

## 功能

- `OAI 图像`：提交图像生成/编辑任务，支持动态模型/应用列表。
- `OAI 视频`：提交文生视频、图生视频等视频任务。
- `OAI Seedance 图像资产`：把图像 URL 上传为 Seedance 可用资产 ID。
- `OAI LLM 对话`：通过统一 API 调用文本对话能力。
- 中文配置面板：在 ComfyUI 前端配置 API 地址、Token，并刷新/缓存模型列表。
- 本地媒体上传：本地图片、音频、视频输入会通过上传接口转换为公网 URL 后提交任务。

## 安装

进入 ComfyUI 的 `custom_nodes` 目录：

```bash
cd ComfyUI/custom_nodes
git clone https://github.com/OAIGC-kk/Comfyui-OAIGC.git
```

重启 ComfyUI 后，在节点搜索中输入 `OAI` 或查看 `OAI Bridge` 分类。

## 升级

如果你已经从本仓库安装过，进入插件目录后拉取最新代码：

```bash
cd ComfyUI/custom_nodes/Comfyui-OAIGC
git pull
```

然后重启 ComfyUI。

## 配置

1. 打开 ComfyUI。
2. 在 OAI Bridge 面板中填写 API 地址和 API Token。
3. 点击刷新模型/应用列表。
4. 在工作流中添加 `OAI 图像`、`OAI 视频`、`OAI Seedance 图像资产` 或 `OAI LLM 对话` 节点。

配置会保存在本地 `oai_bridge_data/config.json`，该文件不会提交到 Git 仓库。

## 项目结构

```text
Comfyui-OAIGC/
├── __init__.py
├── pyproject.toml
├── oai_bridge/
│   ├── client.py
│   ├── config.py
│   ├── media.py
│   ├── nodes_image.py
│   ├── nodes_video.py
│   ├── nodes_seedance_asset.py
│   ├── nodes_llm.py
│   ├── registry.py
│   ├── routes.py
│   └── tasks.py
├── web/
│   ├── oai_bridge_panel.css
│   └── oai_bridge_panel.js
└── tests/
```

## 开发检查

```bash
python -m pytest
```

## 注意

- 请不要把 API Token 写进工作流截图、公开 JSON 或 Git 仓库。
- 新版已经舍弃旧版 `oaigc.py` 单文件节点实现，旧工作流中的旧节点可能需要重新添加为新版节点。
- 本插件需要较新的 ComfyUI 插件入口支持 `comfy_api.latest.ComfyExtension`。
