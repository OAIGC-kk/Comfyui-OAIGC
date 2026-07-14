import { app } from "../../scripts/app.js";
import { api as comfyApi } from "../../scripts/api.js";

const TEXT = {
  panelTitle: "OAI Bridge \u8282\u70b9\u7ba1\u7406",
  close: "\u5173\u95ed",
  tokenSection: "API Token",
  tokenPlaceholder: "\u8bf7\u8f93\u5165 API Token",
  tokenSaved: "\u5df2\u4fdd\u5b58\uff1a",
  tokenLink: "\u83b7\u53d6 API Token",
  saveConfig: "\u4fdd\u5b58 Token",
  testConnection: "\u6d4b\u8bd5\u8fde\u63a5",
  refreshApps: "\u5237\u65b0\u5e94\u7528\u5217\u8868",
  cacheStatus: "\u67e5\u770b\u7f13\u5b58\u72b6\u6001",
  projectNodes: "\u9879\u76ee\u8282\u70b9",
  nodeHint: "\u70b9\u51fb\u5361\u7247\u5373\u53ef\u6dfb\u52a0\u5230\u5f53\u524d\u753b\u5e03",
  noNodes: "\u6682\u65e0\u8282\u70b9\u3002",
  unnamedNode: "\u672a\u547d\u540d\u8282\u70b9",
  noDescription: "\u6682\u65e0\u8bf4\u660e\u3002",
  inputs: "\u8f93\u5165",
  outputs: "\u8f93\u51fa",
  none: "\u65e0",
  configReadFailed: "\u8bfb\u53d6\u914d\u7f6e\u5931\u8d25\u3002",
  nodesReadFailed: "\u8bfb\u53d6\u9879\u76ee\u8282\u70b9\u5931\u8d25\u3002",
  configSaved: "Token \u5df2\u4fdd\u5b58\u3002",
  testDone: "\u6d4b\u8bd5\u5b8c\u6210\u3002",
  refreshDone: "\u5237\u65b0\u5b8c\u6210\u3002",
  updatedAt: "\u66f4\u65b0\u65f6\u95f4\uff1a",
  appCount: "\u5e94\u7528\u6570\u91cf\uff1a",
  cacheSource: "\u7f13\u5b58\u6765\u6e90\uff1a",
  unknown: "\u672a\u77e5",
  addedPrefix: "\u5df2\u6dfb\u52a0\u8282\u70b9\uff1a",
  addFailed: "\u6dfb\u52a0\u8282\u70b9\u5931\u8d25\uff1a",
  graphUnavailable: "\u672a\u627e\u5230 ComfyUI \u753b\u5e03\u3002",
  liteGraphUnavailable: "\u672a\u627e\u5230 LiteGraph \u8282\u70b9\u521b\u5efa\u5668\u3002",
  nodeUnavailable: "\u672a\u627e\u5230\u8be5\u8282\u70b9\u7c7b\u578b\u3002",
};

const bridgeApi = {
  async get(path) {
    const res = await fetch(path);
    return await res.json();
  },
  async post(path, body = {}) {
    const res = await fetch(path, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    return await res.json();
  },
};

const IMAGE_NODE_ID = "OAIImageNode";
const VIDEO_NODE_ID = "OAIVideoNode";
const LLM_NODE_ID = "OAILLMNode";
const SEEDANCE_ASSET_NODE_ID = "OAISeedanceAssetNode";
const IMAGE_FIELD = Object.freeze({
  model: "\u6a21\u578b",
  prompt: "\u63d0\u793a\u8bcd",
  aspect: "\u753b\u9762\u6bd4\u4f8b",
  count: "\u6570\u91cf",
  magnification: "\u653e\u5927\u500d\u6570",
  preLlm: "\u63d0\u793a\u8bcd\u4f18\u5316",
  bananaModel: "Banana\u6a21\u578b",
  imageSize: "\u56fe\u50cf\u89c4\u683c",
  hd: "\u9ad8\u6e05\u6a21\u5f0f",
  fast: "\u5feb\u901f\u6a21\u5f0f",
  gptModel: "GPT\u6a21\u578b",
  resolution: "\u5206\u8fa8\u7387",
  expandTop: "\u5411\u4e0a\u6269\u5c55",
  expandBottom: "\u5411\u4e0b\u6269\u5c55",
  expandLeft: "\u5411\u5de6\u6269\u5c55",
  expandRight: "\u5411\u53f3\u6269\u5c55",
  extra: "\u9ad8\u7ea7\u53c2\u6570JSON",
});

const VIDEO_FIELD = Object.freeze({
  model: "\u89c6\u9891\u6a21\u578b",
  prompt: "\u63d0\u793a\u8bcd",
  aspect: "\u753b\u9762\u6bd4\u4f8b",
  duration: "\u65f6\u957f",
  resolution: "\u6e05\u6670\u5ea6",
  generateAudio: "\u751f\u6210\u97f3\u9891",
  extra: "\u9ad8\u7ea7\u53c2\u6570JSON",
});

const ADVANCED_WIDGET_NAMES = new Set([IMAGE_FIELD.extra, VIDEO_FIELD.extra]);

const DEFAULT_IMAGE_MODEL = "GPT \u751f\u56fe";
const ALI_IMAGE_MODEL = "\u963f\u91cc\u9020\u76f8-\u6587\u751f\u56fe";
const BANANA_IMAGE_MODEL = "Banana\u751f\u56fe";
const AGNES_IMAGE_MODEL = "Agnes Image 2.1 Flash";
const CUTOUT_IMAGE_MODEL = "AI\u6263\u56fe";
const OUTPAINT_IMAGE_MODEL = "AI\u6269\u56fe";
const ALI_SUPPORTED_ASPECT_RATIOS = new Set(["9:16", "2:3", "1:1", "4:3", "3:2", "16:9"]);
const DEFAULT_BANANA_MODEL = "banana2";
const BANANA_MODELS_WITH_HD = new Set(["banana"]);
const MODEL_VISIBLE_WIDGETS = Object.freeze({
  [ALI_IMAGE_MODEL]: [
    IMAGE_FIELD.prompt,
    IMAGE_FIELD.aspect,
    IMAGE_FIELD.count,
    IMAGE_FIELD.magnification,
    IMAGE_FIELD.preLlm,
  ],
  [BANANA_IMAGE_MODEL]: [
    IMAGE_FIELD.prompt,
    IMAGE_FIELD.aspect,
    IMAGE_FIELD.bananaModel,
    IMAGE_FIELD.imageSize,
    IMAGE_FIELD.fast,
  ],
  [DEFAULT_IMAGE_MODEL]: [
    IMAGE_FIELD.prompt,
    IMAGE_FIELD.aspect,
    IMAGE_FIELD.gptModel,
    IMAGE_FIELD.fast,
    IMAGE_FIELD.resolution,
  ],
  [AGNES_IMAGE_MODEL]: [
    IMAGE_FIELD.prompt,
    IMAGE_FIELD.aspect,
    IMAGE_FIELD.count,
    IMAGE_FIELD.resolution,
  ],
  [CUTOUT_IMAGE_MODEL]: [],
  [OUTPAINT_IMAGE_MODEL]: [
    IMAGE_FIELD.expandTop,
    IMAGE_FIELD.expandBottom,
    IMAGE_FIELD.expandLeft,
    IMAGE_FIELD.expandRight,
  ],
});

const IMAGE_WIDGET_NAMES = new Set([
  IMAGE_FIELD.model,
  IMAGE_FIELD.hd,
  ...ADVANCED_WIDGET_NAMES,
  ...Object.values(MODEL_VISIBLE_WIDGETS).flat(),
]);

const DEFAULT_VIDEO_MODEL = "seedance2.0";
const VIDEO_MODEL_VISIBLE_WIDGETS = Object.freeze({
  [DEFAULT_VIDEO_MODEL]: [
    VIDEO_FIELD.prompt,
    VIDEO_FIELD.aspect,
    VIDEO_FIELD.duration,
    VIDEO_FIELD.resolution,
    VIDEO_FIELD.generateAudio,
  ],
  ["seedance2.0-fast"]: [
    VIDEO_FIELD.prompt,
    VIDEO_FIELD.aspect,
    VIDEO_FIELD.duration,
    VIDEO_FIELD.resolution,
    VIDEO_FIELD.generateAudio,
  ],
});

const VIDEO_WIDGET_NAMES = new Set([
  VIDEO_FIELD.model,
  ...ADVANCED_WIDGET_NAMES,
  ...Object.values(VIDEO_MODEL_VISIBLE_WIDGETS).flat(),
]);

function numberedMediaFields(prefix, count, type) {
  return Object.fromEntries(Array.from({ length: count }, (_, index) => [`${prefix}${index + 1}`, type]));
}

const MEDIA_INPUT_RULES = Object.freeze({
  [IMAGE_NODE_ID]: numberedMediaFields("\u56fe\u7247", 12, "IMAGE"),
  [VIDEO_NODE_ID]: {
    ...numberedMediaFields("\u56fe\u7247", 9, "IMAGE"),
    ...numberedMediaFields("\u89c6\u9891", 3, "VIDEO"),
    ...numberedMediaFields("\u97f3\u9891", 3, "AUDIO"),
  },
  [LLM_NODE_ID]: numberedMediaFields("\u56fe\u7247", 6, "IMAGE"),
  [SEEDANCE_ASSET_NODE_ID]: { "\u56fe\u50cf": "IMAGE" },
});

function isOAINodeDefinition(nodeType, nodeData) {
  const typeName = nodeData?.name || nodeData?.node_id || nodeType?.comfyClass || "";
  return Boolean(MEDIA_INPUT_RULES[typeName]);
}

function getMediaRuleTypeName(node) {
  const typeName = getNodeTypeName(node);
  if (MEDIA_INPUT_RULES[typeName]) return typeName;
  return Object.keys(MEDIA_INPUT_RULES).find((candidate) => typeName.includes(candidate)) || "";
}

function getInputMediaType(node, inputIndex) {
  const typeName = getMediaRuleTypeName(node);
  const inputName = node?.inputs?.[inputIndex]?.name || node?.inputs?.[inputIndex]?.label;
  return MEDIA_INPUT_RULES[typeName]?.[inputName] || null;
}

function normalizeSocketTypes(type) {
  if (!type) return [];
  if (Array.isArray(type)) return type.flatMap((item) => normalizeSocketTypes(item));
  if (typeof type === "object") {
    return normalizeSocketTypes(type.type || type.name || type.value);
  }
  return String(type)
    .split(",")
    .map((item) => item.trim().toUpperCase())
    .filter(Boolean);
}

function getOutputSocketType(outputType, outputSlot, outputNode, outputIndex) {
  const slotType = outputSlot?.type || outputSlot?.name;
  const nodeType = outputNode?.outputs?.[outputIndex]?.type || outputNode?.outputs?.[outputIndex]?.name;
  return outputType || slotType || nodeType;
}

function isCompatibleSocketType(actualType, expectedType) {
  const types = normalizeSocketTypes(actualType);
  if (!types.length) return false;
  return types.includes(expectedType) || types.includes("*");
}

function isMediaInputConnectionAllowed(node, inputIndex, outputType, outputSlot, outputNode, outputIndex) {
  const expectedType = getInputMediaType(node, inputIndex);
  if (!expectedType) return true;
  const actualType = getOutputSocketType(outputType, outputSlot, outputNode, outputIndex);
  return isCompatibleSocketType(actualType, expectedType);
}

function patchOAIInputConnectionTypes(nodeType) {
  if (!nodeType?.prototype || nodeType.prototype.__oaiBridgeInputTypesPatched) return;
  const originalOnConnectInput = nodeType.prototype.onConnectInput;
  nodeType.prototype.onConnectInput = function oaiBridgeOnConnectInput(inputIndex, outputType, outputSlot, outputNode, outputIndex, ...args) {
    if (!isMediaInputConnectionAllowed(this, inputIndex, outputType, outputSlot, outputNode, outputIndex)) {
      return false;
    }
    return originalOnConnectInput?.apply(this, [inputIndex, outputType, outputSlot, outputNode, outputIndex, ...args]);
  };
  nodeType.prototype.__oaiBridgeInputTypesPatched = true;
}
const COST_BADGE_TEXT = "O\u5e01";
const COST_BADGE_HEADER_Y = -54;
const COST_BADGE_CATEGORY_RESERVED_WIDTH = 190;
const MODEL_COST_MODELS = Object.freeze({
  [AGNES_IMAGE_MODEL]: (node) => ({
    model: "agnes-image-2.1-flash",
    prompt: getWidgetValue(node, IMAGE_FIELD.prompt, ""),
    ratio: getWidgetValue(node, IMAGE_FIELD.aspect, "1:1"),
    size: getWidgetValue(node, IMAGE_FIELD.resolution, "1K"),
    n: Number(getWidgetValue(node, IMAGE_FIELD.count, 1)),
  }),
});
const IMAGE_COST_APP_IDS = Object.freeze({
  [ALI_IMAGE_MODEL]: "z-imagewenshengt",
  [CUTOUT_IMAGE_MODEL]: "tupiankoutu",
  [OUTPAINT_IMAGE_MODEL]: "kuotu",
});
const SEEDANCE_COST_MODEL_VALUES = Object.freeze({
  [DEFAULT_VIDEO_MODEL]: "seed-2",
  ["seedance2.0-fast"]: "seed-2-fast",
});

function getWidgetValue(node, name, fallback = undefined) {
  const widget = findWidget(node, name);
  return widget?.value ?? fallback;
}

function asCostBool(value) {
  return !["\u5426", "false", "False", "0", "no", "No", false].includes(value);
}

function buildGptImageCostRequest(node) {
  return {
    kind: "workflow",
    payload: {
      appId: "gpt-image",
      parameter: {
        prompt: getWidgetValue(node, IMAGE_FIELD.prompt, ""),
        model: getWidgetValue(node, IMAGE_FIELD.gptModel, "gpt-image-2"),
        size: getWidgetValue(node, IMAGE_FIELD.aspect, "1:1"),
        fast: asCostBool(getWidgetValue(node, IMAGE_FIELD.fast, "\u662f")),
        resolution: getWidgetValue(node, IMAGE_FIELD.resolution, "1K"),
      },
    },
  };
}

function buildBananaCostRequest(node) {
  const bananaModel = getWidgetValue(node, IMAGE_FIELD.bananaModel, DEFAULT_BANANA_MODEL);
  const parameter = {
    model: bananaModel,
    prompt: getWidgetValue(node, IMAGE_FIELD.prompt, ""),
    size: getWidgetValue(node, IMAGE_FIELD.aspect, "1:1"),
    image_size: getWidgetValue(node, IMAGE_FIELD.imageSize, "1k"),
    fast: asCostBool(getWidgetValue(node, IMAGE_FIELD.fast, "\u662f")),
  };
  if (bananaModel === "banana") {
    parameter.hd = asCostBool(getWidgetValue(node, IMAGE_FIELD.hd, "\u5426"));
  }
  return { kind: "workflow", payload: { appId: "banana", parameter } };
}

function buildImageCostRequest(node) {
  const model = getSelectedImageModel(node);
  if (model === DEFAULT_IMAGE_MODEL) return buildGptImageCostRequest(node);
  if (model === BANANA_IMAGE_MODEL) return buildBananaCostRequest(node);

  const modelCostFactory = MODEL_COST_MODELS[model];
  if (modelCostFactory) {
    return { kind: "model", payload: modelCostFactory(node) };
  }

  const appId = IMAGE_COST_APP_IDS[model];
  if (!appId) return null;

  if (model === ALI_IMAGE_MODEL) {
    return {
      kind: "workflow",
      payload: {
        appId,
        parameter: {
          prompt: getWidgetValue(node, IMAGE_FIELD.prompt, ""),
          num: Number(getWidgetValue(node, IMAGE_FIELD.count, 1)),
          magnification: Number(getWidgetValue(node, IMAGE_FIELD.magnification, 1.1)),
          aspect_ratio: getWidgetValue(node, IMAGE_FIELD.aspect, "1:1"),
          use_pre_llm: asCostBool(getWidgetValue(node, IMAGE_FIELD.preLlm, "\u662f")),
        },
      },
    };
  }

  if (model === OUTPAINT_IMAGE_MODEL) {
    return {
      kind: "workflow",
      payload: {
        appId,
        parameter: {
          image: "",
          top: String(getWidgetValue(node, IMAGE_FIELD.expandTop, "1")),
          bottom: String(getWidgetValue(node, IMAGE_FIELD.expandBottom, "1")),
          left: String(getWidgetValue(node, IMAGE_FIELD.expandLeft, "1")),
          right: String(getWidgetValue(node, IMAGE_FIELD.expandRight, "1")),
        },
      },
    };
  }

  return { kind: "workflow", payload: { appId, parameter: { image: "" } } };
}

function buildVideoCostRequest(node) {
  const model = getSelectedVideoModel(node);
  const modelValue = SEEDANCE_COST_MODEL_VALUES[model] || SEEDANCE_COST_MODEL_VALUES[DEFAULT_VIDEO_MODEL];
  return {
    kind: "seedance",
    payload: {
      model: modelValue,
      prompt: getWidgetValue(node, VIDEO_FIELD.prompt, ""),
      metadata: {
        ratio: getWidgetValue(node, VIDEO_FIELD.aspect, "16:9"),
        duration: Number(getWidgetValue(node, VIDEO_FIELD.duration, 4)),
        resolution: getWidgetValue(node, VIDEO_FIELD.resolution, "720p"),
        generate_audio: asCostBool(getWidgetValue(node, VIDEO_FIELD.generateAudio, "\u662f")),
      },
    },
  };
}

function buildCostRequest(node) {
  if (node?.__oaiBridgeCostKind === "image") return buildImageCostRequest(node);
  if (node?.__oaiBridgeCostKind === "video") return buildVideoCostRequest(node);
  const typeName = getNodeTypeName(node);
  if (typeName === IMAGE_NODE_ID || typeName.includes(IMAGE_NODE_ID)) return buildImageCostRequest(node);
  if (typeName === VIDEO_NODE_ID || typeName.includes(VIDEO_NODE_ID)) return buildVideoCostRequest(node);
  return null;
}

function setNodeCost(node, value) {
  node.__oaiBridgeCostText = value === null || value === undefined || value === "" ? `-- ${COST_BADGE_TEXT}` : `${value} ${COST_BADGE_TEXT}`;
  app?.graph?.setDirtyCanvas?.(true, true);
  app?.canvas?.setDirty?.(true, true);
}

function getCostRequestSignature(request) {
  try {
    return JSON.stringify(request);
  } catch (error) {
    return String(Date.now());
  }
}

async function refreshOAICost(node, options = {}) {
  const request = buildCostRequest(node);
  if (!request) {
    node.__oaiBridgeCostSignature = "";
    setNodeCost(node, null);
    return;
  }
  const signature = getCostRequestSignature(request);
  if (!options.force && node.__oaiBridgeCostSignature === signature && node.__oaiBridgeCostText && !node.__oaiBridgeCostPending) return;
  node.__oaiBridgeCostSignature = signature;
  node.__oaiBridgeCostPending = true;
  setNodeCost(node, "...");
  const ticket = (node.__oaiBridgeCostTicket || 0) + 1;
  node.__oaiBridgeCostTicket = ticket;
  try {
    const response = await bridgeApi.post("/oai-bridge/cost", request);
    if (node.__oaiBridgeCostTicket !== ticket) return;
    setNodeCost(node, response?.ok ? response.cost : null);
  } catch (error) {
    if (node.__oaiBridgeCostTicket === ticket) setNodeCost(node, null);
  } finally {
    if (node.__oaiBridgeCostTicket === ticket) node.__oaiBridgeCostPending = false;
  }
}

function scheduleOAICostRefresh(node, options = {}) {
  if (options.force) node.__oaiBridgeCostSignature = "";
  clearTimeout(node.__oaiBridgeCostTimer);
  node.__oaiBridgeCostTimer = setTimeout(() => refreshOAICost(node, options), 300);
}

function maybeRefreshOAICostFromDraw(node) {
  const now = Date.now();
  if (now - (node.__oaiBridgeCostDrawCheckAt || 0) < 500) return;
  node.__oaiBridgeCostDrawCheckAt = now;
  const request = buildCostRequest(node);
  const signature = request ? getCostRequestSignature(request) : "";
  if (signature !== (node.__oaiBridgeCostSignature || "")) scheduleOAICostRefresh(node, { force: true });
}

function drawOAICostBadge(node, ctx) {
  maybeRefreshOAICostFromDraw(node);
  const text = node.__oaiBridgeCostText;
  if (!text || !ctx) return;
  ctx.save();
  ctx.font = "12px sans-serif";
  const paddingX = 8;
  const width = Math.ceil(ctx.measureText(text).width) + paddingX * 2;
  const height = 20;
  const nodeWidth = node.size?.[0] || 180;
  const x = Math.max(8, nodeWidth - width - COST_BADGE_CATEGORY_RESERVED_WIDTH);
  const y = COST_BADGE_HEADER_Y;
  ctx.fillStyle = "rgba(20, 20, 20, 0.76)";
  if (ctx.roundRect) {
    ctx.beginPath();
    ctx.roundRect(x, y, width, height, 5);
    ctx.fill();
  } else {
    ctx.fillRect(x, y, width, height);
  }
  ctx.fillStyle = "#f7d774";
  ctx.textBaseline = "middle";
  ctx.fillText(text, x + paddingX, y + height / 2);
  ctx.restore();
}

function patchCostCallbacks(node) {
  if (!node?.widgets) return;
  for (const widget of node.widgets) {
    if (widget.__oaiBridgeCostPatched) continue;
    const originalCallback = widget.callback;
    widget.callback = function oaiBridgeCostWidgetCallback(value, ...args) {
      const result = originalCallback?.apply(this, [value, ...args]);
      scheduleOAICostRefresh(node, { force: true });
      return result;
    };
    widget.__oaiBridgeCostPatched = true;
  }
}

function installOAICostBadge(node) {
  if (!node || node.__oaiBridgeCostInstalled) {
    patchCostCallbacks(node);
    scheduleOAICostRefresh(node);
    return;
  }
  const originalOnDrawForeground = node.onDrawForeground;
  node.onDrawForeground = function oaiBridgeCostForeground(ctx, ...args) {
    const result = originalOnDrawForeground?.apply(this, [ctx, ...args]);
    drawOAICostBadge(this, ctx);
    return result;
  };
  node.__oaiBridgeCostInstalled = true;
  patchCostCallbacks(node);
  scheduleOAICostRefresh(node);
}


function getWidgetName(widget) {
  return widget?.name || widget?.label;
}

function findWidget(node, name) {
  return node?.widgets?.find((widget) => getWidgetName(widget) === name);
}

function getSelectedImageModel(node) {
  return findWidget(node, IMAGE_FIELD.model)?.value || DEFAULT_IMAGE_MODEL;
}

function getSelectedBananaModel(node) {
  return findWidget(node, IMAGE_FIELD.bananaModel)?.value || DEFAULT_BANANA_MODEL;
}

function inferWidgetType(widget) {
  const originalType = widget?.__oaiBridgeOriginal?.type;
  if (originalType && originalType !== "hidden") return originalType;
  if (Array.isArray(widget?.options?.values)) return "combo";
  if (typeof widget?.value === "number") return "number";
  if (typeof widget?.value === "boolean") return "toggle";
  return "text";
}

function restoreLegacyHiddenWidget(widget) {
  if (!widget) return;
  const original = widget.__oaiBridgeOriginal || {};
  if (widget.type === "hidden") {
    widget.type = original.type || inferWidgetType(widget);
  }
  if (original.computeSize) {
    widget.computeSize = original.computeSize;
  }
  if (original.draw) {
    widget.draw = original.draw;
  }
  widget.hidden = false;
  widget.disabled = false;
  delete widget.__oaiBridgeHidden;
  delete widget.__oaiBridgeOriginal;
}
function showWidget(widget) {
  if (!widget?.__oaiBridgeHidden) return;
  const original = widget.__oaiBridgeOriginal || {};
  if (original.computeSize) {
    widget.computeSize = original.computeSize;
  } else {
    delete widget.computeSize;
  }
  if (original.draw) {
    widget.draw = original.draw;
  } else {
    delete widget.draw;
  }
  widget.hidden = false;
  widget.disabled = false;
  delete widget.__oaiBridgeHidden;
  delete widget.__oaiBridgeOriginal;
}

function hideWidget(widget) {
  if (!widget || widget.__oaiBridgeHidden) return;
  widget.__oaiBridgeOriginal = {
    computeSize: widget.computeSize,
    draw: widget.draw,
  };
  widget.hidden = true;
  widget.disabled = true;
  widget.computeSize = () => [0, -4];
  widget.draw = () => {};
  widget.__oaiBridgeHidden = true;
}
function refreshNodeLayout(node) {
  if (node?.computeSize && node?.setSize) {
    const computedSize = node.computeSize();
    const currentSize = node.size || [0, 0];
    node.setSize([
      Math.max(currentSize[0] || 0, computedSize[0] || 0),
      Math.max(currentSize[1] || 0, computedSize[1] || 0),
    ]);
  }
  app?.graph?.setDirtyCanvas?.(true, true);
  app?.canvas?.setDirty?.(true, true);
}

function hideAdvancedWidgets(node) {
  if (!node?.widgets) return;
  for (const widget of node.widgets) {
    const name = getWidgetName(widget);
    if (ADVANCED_WIDGET_NAMES.has(name)) hideWidget(widget);
  }
  refreshNodeLayout(node);
}

function normalizeOAIImageWidgetValues(node) {
  if (getSelectedImageModel(node) !== ALI_IMAGE_MODEL) return;
  const aspectWidget = findWidget(node, IMAGE_FIELD.aspect);
  if (aspectWidget && !ALI_SUPPORTED_ASPECT_RATIOS.has(aspectWidget.value)) {
    aspectWidget.value = "1:1";
  }
}
function updateOAIImageWidgetVisibility(node) {
  if (!node?.widgets) return;
  normalizeOAIImageWidgetValues(node);
  const model = getSelectedImageModel(node);
  const visible = new Set([IMAGE_FIELD.model, ...(MODEL_VISIBLE_WIDGETS[model] || MODEL_VISIBLE_WIDGETS[DEFAULT_IMAGE_MODEL])]);
  if (model === BANANA_IMAGE_MODEL && BANANA_MODELS_WITH_HD.has(getSelectedBananaModel(node))) {
    visible.add(IMAGE_FIELD.hd);
  }

  for (const widget of node.widgets) {
    const name = getWidgetName(widget);
    if (!IMAGE_WIDGET_NAMES.has(name)) continue;
    if (visible.has(name)) {
      showWidget(widget);
    } else {
      hideWidget(widget);
    }
  }

  scheduleOAICostRefresh(node, { force: true });
  refreshNodeLayout(node);
}

function scheduleOAIImageWidgetVisibility(node) {
  updateOAIImageWidgetVisibility(node);
  requestAnimationFrame?.(() => updateOAIImageWidgetVisibility(node));
  setTimeout(() => updateOAIImageWidgetVisibility(node), 0);
}

function patchOAIImageModelWidget(node) {
  const modelWidget = findWidget(node, IMAGE_FIELD.model);
  if (!modelWidget || modelWidget.__oaiBridgePatched) return;

  const originalCallback = modelWidget.callback;
  modelWidget.callback = function oaiBridgeModelCallback(value, ...args) {
    const result = originalCallback?.apply(this, [value, ...args]);
    scheduleOAIImageWidgetVisibility(node);
    return result;
  };
  modelWidget.__oaiBridgePatched = true;
}

function patchOAIImageBananaModelWidget(node) {
  const bananaModelWidget = findWidget(node, IMAGE_FIELD.bananaModel);
  if (!bananaModelWidget || bananaModelWidget.__oaiBridgePatched) return;

  const originalCallback = bananaModelWidget.callback;
  bananaModelWidget.callback = function oaiBridgeBananaModelCallback(value, ...args) {
    const result = originalCallback?.apply(this, [value, ...args]);
    scheduleOAIImageWidgetVisibility(node);
    return result;
  };
  bananaModelWidget.__oaiBridgePatched = true;
}

function installOAIImageWidgetFilter(node) {
  node.__oaiBridgeCostKind = "image";
  patchOAIImageModelWidget(node);
  patchOAIImageBananaModelWidget(node);
  scheduleOAIImageWidgetVisibility(node);
  installOAICostBadge(node);
}

function isOAIImageNodeDefinition(nodeType, nodeData) {
  return nodeData?.name === IMAGE_NODE_ID || nodeData?.node_id === IMAGE_NODE_ID || nodeType?.comfyClass === IMAGE_NODE_ID;
}

function getSelectedVideoModel(node) {
  return findWidget(node, VIDEO_FIELD.model)?.value || DEFAULT_VIDEO_MODEL;
}

function updateOAIVideoWidgetVisibility(node) {
  if (!node?.widgets) return;
  const model = getSelectedVideoModel(node);
  const visible = new Set([
    VIDEO_FIELD.model,
    ...(VIDEO_MODEL_VISIBLE_WIDGETS[model] || VIDEO_MODEL_VISIBLE_WIDGETS[DEFAULT_VIDEO_MODEL]),
  ]);
  for (const widget of node.widgets) {
    const name = getWidgetName(widget);
    if (!VIDEO_WIDGET_NAMES.has(name)) continue;
    if (visible.has(name)) {
      showWidget(widget);
    } else {
      hideWidget(widget);
    }
  }

  refreshNodeLayout(node);
}

function scheduleOAIVideoWidgetVisibility(node) {
  updateOAIVideoWidgetVisibility(node);
  requestAnimationFrame?.(() => updateOAIVideoWidgetVisibility(node));
  setTimeout(() => updateOAIVideoWidgetVisibility(node), 0);
}

function patchOAIVideoModelWidget(node) {
  const modelWidget = findWidget(node, VIDEO_FIELD.model);
  if (!modelWidget || modelWidget.__oaiBridgePatched) return;

  const originalCallback = modelWidget.callback;
  modelWidget.callback = function oaiBridgeVideoModelCallback(value, ...args) {
    const result = originalCallback?.apply(this, [value, ...args]);
    scheduleOAIVideoWidgetVisibility(node);
    return result;
  };
  modelWidget.__oaiBridgePatched = true;
}

function installOAIVideoWidgetFilter(node) {
  node.__oaiBridgeCostKind = "video";
  patchOAIVideoModelWidget(node);
  scheduleOAIVideoWidgetVisibility(node);
  installOAICostBadge(node);
}

function isOAIVideoNodeDefinition(nodeType, nodeData) {
  return nodeData?.name === VIDEO_NODE_ID || nodeData?.node_id === VIDEO_NODE_ID || nodeType?.comfyClass === VIDEO_NODE_ID;
}

app.registerExtension?.({
  name: "oai.bridge.widget-filter",
  beforeRegisterNodeDef(nodeType, nodeData) {
    if (isOAINodeDefinition(nodeType, nodeData)) patchOAIInputConnectionTypes(nodeType);
    if (isOAIImageNodeDefinition(nodeType, nodeData)) {
      const originalOnNodeCreated = nodeType.prototype.onNodeCreated;
      nodeType.prototype.onNodeCreated = function oaiBridgeOnNodeCreated(...args) {
        const result = originalOnNodeCreated?.apply(this, args);
        installOAIImageWidgetFilter(this);
        return result;
      };

      const originalOnConfigure = nodeType.prototype.onConfigure;
      nodeType.prototype.onConfigure = function oaiBridgeOnConfigure(...args) {
        const result = originalOnConfigure?.apply(this, args);
        installOAIImageWidgetFilter(this);
        return result;
      };
      return;
    }

    if (isOAIVideoNodeDefinition(nodeType, nodeData)) {
      const originalOnNodeCreated = nodeType.prototype.onNodeCreated;
      nodeType.prototype.onNodeCreated = function oaiBridgeVideoOnNodeCreated(...args) {
        const result = originalOnNodeCreated?.apply(this, args);
        installOAIVideoWidgetFilter(this);
        return result;
      };

      const originalOnConfigure = nodeType.prototype.onConfigure;
      nodeType.prototype.onConfigure = function oaiBridgeVideoOnConfigure(...args) {
        const result = originalOnConfigure?.apply(this, args);
        installOAIVideoWidgetFilter(this);
        return result;
      };
    }
  },
});


const PREVIEW_RESTORE_NODE_TYPES = new Set([IMAGE_NODE_ID, VIDEO_NODE_ID, "SaveImage", "\u4fdd\u5b58\u56fe\u50cf"]);
const PREVIEW_PROPERTY = "__oaiBridgePreviewImages";
let previewRestoreInFlight = false;
const previewRestoreTimers = new Set();

function getHistoryItems(history) {
  if (Array.isArray(history)) return history;
  if (!history || typeof history !== "object") return [];
  return Object.values(history);
}

function getHistoryOutputs(item) {
  const outputs = item?.outputs;
  return outputs && typeof outputs === "object" ? outputs : null;
}

function hasImagesForAnyNode(outputs, nodes) {
  return nodes.some((node) => Boolean(getNodeOutputImages(outputs, node)));
}

async function findLatestHistoryOutputs(nodes = []) {
  try {
    const history = typeof comfyApi?.getHistory === "function" ? await comfyApi.getHistory(50) : await bridgeApi.get("/history");
    const items = getHistoryItems(history);
    let fallbackOutputs = null;
    for (const item of items) {
      const outputs = getHistoryOutputs(item);
      if (!outputs) continue;
      fallbackOutputs ||= outputs;
      if (!nodes.length || hasImagesForAnyNode(outputs, nodes)) return outputs;
    }
    return fallbackOutputs;
  } catch (error) {
    console.debug?.("OAI Bridge 恢复预览失败", error);
  }
  return null;
}

function getNodeTypeName(node) {
  return node?.constructor?.comfyClass || node?.type || node?.comfyClass || "";
}

function shouldRestoreNodePreview(node) {
  const typeName = getNodeTypeName(node);
  return PREVIEW_RESTORE_NODE_TYPES.has(typeName) || typeName.includes("SaveImage") || typeName.includes("\u4fdd\u5b58\u56fe\u50cf");
}

function isPreviewRestoreNodeDefinition(nodeType, nodeData) {
  const typeName = nodeData?.name || nodeData?.node_id || nodeType?.comfyClass || "";
  return PREVIEW_RESTORE_NODE_TYPES.has(typeName) || typeName.includes("SaveImage") || typeName.includes("\u4fdd\u5b58\u56fe\u50cf");
}

function getLinkSourceNode(graph, linkId) {
  const link = graph?.links?.[linkId];
  const sourceId = link?.origin_id ?? link?.originId;
  if (sourceId === undefined || sourceId === null) return null;
  return graph?._nodes_by_id?.[sourceId] || graph?._nodes?.find((candidate) => String(candidate.id) === String(sourceId)) || null;
}

function getUpstreamImageNodeIds(node, graph = getGraph()) {
  const upstreamIds = [];
  for (const input of node?.inputs || []) {
    if (input?.link === undefined || input?.link === null) continue;
    const sourceNode = getLinkSourceNode(graph, input.link);
    if (!sourceNode) continue;
    const sourceType = getNodeTypeName(sourceNode);
    if (sourceType === IMAGE_NODE_ID || sourceType.includes("Image") || sourceType.includes("\u56fe\u50cf")) {
      upstreamIds.push(String(sourceNode.id));
    }
  }
  return upstreamIds;
}

function getCandidateOutputIdsForNode(node, graph = getGraph()) {
  const ids = [String(node.id)];
  for (const upstreamId of getUpstreamImageNodeIds(node, graph)) {
    if (!ids.includes(upstreamId)) ids.push(upstreamId);
  }
  return ids;
}

function getNodeOutputImages(outputs, node) {
  for (const outputId of getCandidateOutputIdsForNode(node)) {
    const output = outputs?.[String(outputId)] || outputs?.[outputId];
    const images = output?.images || output?.gifs;
    if (Array.isArray(images) && images.length) return images;
  }
  return null;
}

function getPreviewImagesFromPayload(payload) {
  const images = payload?.images || payload?.gifs;
  return Array.isArray(images) && images.length ? images : null;
}

function rememberNodePreviewImages(node, images) {
  if (!node || !images?.length) return;
  node.properties ||= {};
  node.properties[PREVIEW_PROPERTY] = images;
}

function getStoredPreviewImages(node) {
  const images = node?.properties?.[PREVIEW_PROPERTY];
  return Array.isArray(images) && images.length ? images : null;
}

function getNodeOutputLocatorId(node) {
  return String(node?.id ?? "");
}

function writeNativePreviewOutput(node, images) {
  if (!node || !images?.length) return;
  const locatorId = getNodeOutputLocatorId(node);
  if (!locatorId) return;
  app.nodeOutputs ||= {};
  app.nodeOutputs[locatorId] = { ...(app.nodeOutputs[locatorId] || {}), images };
}

function applyNodePreviewImages(node, images) {
  if (!node || !images?.length) return false;
  writeNativePreviewOutput(node, images);
  node.images = null;
  node.imgs = null;
  node.animatedImages = null;
  delete node.__oaiBridgeRestoredImages;
  delete node.__oaiBridgePreviewImageObjects;
  node.onDrawBackground?.();
  node.setDirtyCanvas?.(true, true);
  return true;
}

function applyStoredNodePreview(node) {
  const images = getStoredPreviewImages(node);
  return images ? applyNodePreviewImages(node, images) : false;
}

function patchPreviewRestoreExecution(nodeType) {
  if (!nodeType?.prototype || nodeType.prototype.__oaiBridgePreviewExecutionPatched) return;
  const originalOnExecuted = nodeType.prototype.onExecuted;
  const originalOnConfigure = nodeType.prototype.onConfigure;

  nodeType.prototype.onExecuted = function oaiBridgePreviewOnExecuted(message, ...args) {
    const result = originalOnExecuted?.apply(this, [message, ...args]);
    const images = getPreviewImagesFromPayload(message);
    if (images) {
      rememberNodePreviewImages(this, images);
      writeNativePreviewOutput(this, images);
      app.graph?.setDirtyCanvas?.(true, true);
      app.canvas?.setDirty?.(true, true);
    }
    return result;
  };

  nodeType.prototype.onConfigure = function oaiBridgePreviewOnConfigure(...args) {
    const result = originalOnConfigure?.apply(this, args);
    applyStoredNodePreview(this);
    schedulePreviewRestore(300);
    return result;
  };

  nodeType.prototype.__oaiBridgePreviewExecutionPatched = true;
}

async function restoreNodePreviewsFromHistory() {
  if (previewRestoreInFlight) return;
  const graph = getGraph();
  const nodes = (graph?._nodes || []).filter(shouldRestoreNodePreview);
  if (!nodes.length) return;

  previewRestoreInFlight = true;
  try {
    let restored = false;
    for (const node of nodes) {
      restored = applyStoredNodePreview(node) || restored;
    }

    const missingNodes = nodes.filter((node) => !(Array.isArray(node.images) && node.images.length));
    if (missingNodes.length) {
      const outputs = await findLatestHistoryOutputs(missingNodes);
      if (outputs) {
        for (const node of missingNodes) {
          const images = getNodeOutputImages(outputs, node);
          if (images) {
            rememberNodePreviewImages(node, images);
            restored = applyNodePreviewImages(node, images) || restored;
          }
        }
      }
    }

    if (restored) {
      app.graph?.setDirtyCanvas?.(true, true);
      app.canvas?.setDirty?.(true, true);
    }
  } finally {
    previewRestoreInFlight = false;
  }
}

function schedulePreviewRestore(delay = 250) {
  const timer = setTimeout(() => {
    previewRestoreTimers.delete(timer);
    restoreNodePreviewsFromHistory();
  }, delay);
  previewRestoreTimers.add(timer);
}

function installPreviewRestoreHooks() {
  schedulePreviewRestore(500);
  schedulePreviewRestore(1500);
  comfyApi.addEventListener?.("graphChanged", () => schedulePreviewRestore(300));
  app?.api?.addEventListener?.("graphChanged", () => schedulePreviewRestore(300));
}

app.registerExtension?.({
  name: "oai.bridge.preview-restore",
  beforeRegisterNodeDef(nodeType, nodeData) {
    if (isPreviewRestoreNodeDefinition(nodeType, nodeData)) patchPreviewRestoreExecution(nodeType);
  },
  nodeCreated(node) {
    applyStoredNodePreview(node);
    schedulePreviewRestore(300);
    schedulePreviewRestore(1200);
  },
  loadedGraphNode(node) {
    applyStoredNodePreview(node);
    schedulePreviewRestore(300);
    schedulePreviewRestore(1200);
  },
  afterConfigureGraph() {
    schedulePreviewRestore(300);
    schedulePreviewRestore(1200);
    schedulePreviewRestore(2500);
  },
});
function injectStyle() {
  if (document.querySelector("link[data-oai-bridge-style]")) return;
  const link = document.createElement("link");
  link.rel = "stylesheet";
  link.href = new URL("oai_bridge_panel.css", import.meta.url).href;
  link.dataset.oaiBridgeStyle = "true";
  document.head.appendChild(link);
}

function row(label, input) {
  const wrap = document.createElement("label");
  wrap.className = "oai-bridge-row";
  const span = document.createElement("span");
  span.textContent = label;
  wrap.append(span, input);
  return wrap;
}

function button(text, onClick) {
  const el = document.createElement("button");
  el.type = "button";
  el.textContent = text;
  el.addEventListener("click", onClick);
  return el;
}

function sectionTitle(text) {
  const title = document.createElement("h3");
  title.className = "oai-bridge-section-title";
  title.textContent = text;
  return title;
}

function getGraph() {
  return app?.graph || app?.canvas?.graph;
}

function getLiteGraph() {
  return globalThis.LiteGraph || window.LiteGraph;
}

function chooseNodePosition(graph) {
  const canvas = app?.canvas;
  if (Array.isArray(canvas?.graph_mouse)) {
    return [canvas.graph_mouse[0], canvas.graph_mouse[1]];
  }
  const count = graph?._nodes?.length || 0;
  return [120 + count * 24, 120 + count * 24];
}

function addNodeToGraph(nodeInfo) {
  const graph = getGraph();
  if (!graph) throw new Error(TEXT.graphUnavailable);

  const LiteGraph = getLiteGraph();
  if (!LiteGraph?.createNode) throw new Error(TEXT.liteGraphUnavailable);

  const newNode = LiteGraph.createNode(nodeInfo.node_id);
  if (!newNode) throw new Error(TEXT.nodeUnavailable);

  newNode.pos = chooseNodePosition(graph);
  if (app.graph?.add) {
    app.graph.add(newNode);
  } else {
    graph.add(newNode);
  }
  graph.setDirtyCanvas?.(true, true);
  app.canvas?.setDirty?.(true, true);
  app.canvas?.centerOnNode?.(newNode);
  return newNode;
}

function renderNodeList(nodes, status) {
  const list = document.createElement("div");
  list.className = "oai-bridge-node-list node-list";

  if (!nodes.length) {
    const empty = document.createElement("p");
    empty.className = "oai-bridge-muted";
    empty.textContent = TEXT.noNodes;
    list.appendChild(empty);
    return list;
  }

  for (const node of nodes) {
    const card = document.createElement("button");
    card.type = "button";
    card.className = "oai-bridge-node-card";
    card.setAttribute("data-node-type", node.node_id || "");

    const header = document.createElement("div");
    header.className = "oai-bridge-node-card-header";

    const name = document.createElement("strong");
    name.textContent = node.display_name || node.node_id || TEXT.unnamedNode;

    const category = document.createElement("span");
    category.textContent = node.category || "OAI Bridge";

    const description = document.createElement("p");
    description.textContent = node.description || TEXT.noDescription;

    const io = document.createElement("p");
    io.className = "oai-bridge-node-io";
    io.textContent = `${TEXT.inputs}\uff1a${(node.inputs || []).join("\u3001") || TEXT.none}\uff1b${TEXT.outputs}\uff1a${(node.outputs || []).join("\u3001") || TEXT.none}`;

    card.addEventListener("click", () => {
      try {
        addNodeToGraph(node);
        status.textContent = `${TEXT.addedPrefix}${node.display_name || node.node_id}`;
        document.querySelector("[data-oai-bridge-dialog]")?.remove();
      } catch (error) {
        status.textContent = `${TEXT.addFailed}${error?.message || error}`;
      }
    });

    header.append(name, category);
    card.append(header, description, io);
    list.appendChild(card);
  }

  return list;
}

function openDialog(panel) {
  document.querySelector("[data-oai-bridge-dialog]")?.remove();

  const overlay = document.createElement("div");
  overlay.dataset.oaiBridgeDialog = "true";
  overlay.className = "oai-bridge-overlay";

  const dialog = document.createElement("section");
  dialog.className = "oai-bridge-dialog";

  const close = button(TEXT.close, () => overlay.remove());
  close.className = "oai-bridge-close";
  close.setAttribute("aria-label", TEXT.close);

  dialog.append(close, panel);
  overlay.appendChild(dialog);
  overlay.addEventListener("click", (event) => {
    if (event.target === overlay) overlay.remove();
  });
  document.addEventListener(
    "keydown",
    (event) => {
      if (event.key === "Escape") overlay.remove();
    },
    { once: true },
  );
  document.body.appendChild(overlay);
}

async function showPanel() {
  injectStyle();

  const panel = document.createElement("div");
  panel.className = "oai-bridge-panel";
  const title = document.createElement("h2");
  title.textContent = TEXT.panelTitle;
  panel.appendChild(title);

  const token = document.createElement("input");
  token.placeholder = TEXT.tokenPlaceholder;
  token.type = "password";
  const status = document.createElement("p");
  status.className = "oai-bridge-status";

  const tokenTools = document.createElement("div");
  tokenTools.className = "oai-bridge-token-tools";
  const tokenLink = document.createElement("a");
  tokenLink.href = "https://oaigc.cn";
  tokenLink.target = "_blank";
  tokenLink.rel = "noreferrer";
  tokenLink.textContent = TEXT.tokenLink;
  tokenTools.appendChild(tokenLink);

  const nodesWrap = document.createElement("div");
  nodesWrap.className = "oai-bridge-nodes-wrap";
  nodesWrap.append(sectionTitle(TEXT.projectNodes));
  const hint = document.createElement("p");
  hint.className = "oai-bridge-muted";
  hint.textContent = TEXT.nodeHint;
  nodesWrap.appendChild(hint);

  try {
    const data = await bridgeApi.get("/oai-bridge/config");
    token.placeholder = data.config?.has_token ? `${TEXT.tokenSaved}${data.config.token_masked}` : TEXT.tokenPlaceholder;
  } catch {
    status.textContent = TEXT.configReadFailed;
  }

  try {
    const data = await bridgeApi.get("/oai-bridge/nodes");
    nodesWrap.appendChild(renderNodeList(data.nodes || [], status));
  } catch {
    nodesWrap.appendChild(renderNodeList([], status));
    status.textContent = TEXT.nodesReadFailed;
  }

  panel.append(
    sectionTitle(TEXT.tokenSection),
    row(TEXT.tokenSection, token),
    tokenTools,
    button(TEXT.saveConfig, async () => {
      const body = {};
      if (token.value) body.token = token.value;
      const data = await bridgeApi.post("/oai-bridge/config", body);
      status.textContent = data.message || TEXT.configSaved;
    }),
    button(TEXT.testConnection, async () => {
      const data = await bridgeApi.post("/oai-bridge/test");
      status.textContent = data.message || TEXT.testDone;
    }),
    button(TEXT.refreshApps, async () => {
      const data = await bridgeApi.post("/oai-bridge/metadata/refresh");
      const meta = data.metadata || {};
      status.textContent = `${data.message || TEXT.refreshDone}\n${TEXT.updatedAt}${meta.updated_at || TEXT.none}\n${TEXT.appCount}${meta.apps?.length || 0}`;
    }),
    button(TEXT.cacheStatus, async () => {
      const data = await bridgeApi.get("/oai-bridge/metadata");
      const meta = data.metadata || {};
      status.textContent = `${TEXT.cacheSource}${meta.source || TEXT.unknown}\n${TEXT.updatedAt}${meta.updated_at || TEXT.none}\n${TEXT.appCount}${meta.apps?.length || 0}`;
    }),
    status,
    nodesWrap,
  );

  openDialog(panel);
}

function ensurePanelEntry() {
  injectStyle();
  if (document.querySelector("[data-oai-bridge-entry]")) return;
  if (!document.body) return;

  const entry = document.createElement("button");
  entry.type = "button";
  entry.dataset.oaiBridgeEntry = "true";
  entry.className = "oai-bridge-floating-entry";
  entry.textContent = TEXT.panelTitle;
  entry.title = TEXT.panelTitle;
  entry.addEventListener("click", showPanel);

  document.body.appendChild(entry);
}

function schedulePanelEntry() {
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", ensurePanelEntry, { once: true });
  } else {
    ensurePanelEntry();
  }
  setTimeout(ensurePanelEntry, 1000);
  setTimeout(ensurePanelEntry, 3000);
}

schedulePanelEntry();
installPreviewRestoreHooks();

