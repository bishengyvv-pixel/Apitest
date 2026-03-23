import { createContext, useContext, useEffect, useMemo, useState, type ReactNode } from "react";

type Locale = "en" | "zh-CN";

const LOCALE_STORAGE_KEY = "ai-tester-locale";

const translations = {
  en: {
    appName: "AI Tester",
    navTesting: "Testing",
    navConnection: "Connection",
    switchLanguage: "Switch to Chinese",
    connectionPresets: "Connection & Presets",
    connectionSettingsTitle: "Connection settings and Codex presets",
    connectionSettingsDescription:
      "Phase 1 keeps the current Python Web backend and wires React into the local BFF. This page manages connection data, tests model connectivity, and writes presets back into Codex.",
    editCurrentConnection: "Edit current connection",
    presetName: "preset name",
    presetNamePlaceholder: "Example: company hk node",
    baseUrl: "baseurl",
    apiKey: "apikey",
    currentState: "Current state",
    loadedModels: "loaded models",
    defaultImage: "default image",
    ready: "ready",
    loading: "loading",
    selectedModel: "selected model",
    notSelected: "not selected",
    activeCodexItem: "active Codex item",
    notWritten: "not written",
    testConnectionAndLoadModels: "Test connection and load models",
    saveCodexPreset: "Save Codex preset",
    applyToCodex: "Apply to Codex",
    currentActiveCodexConfig: "Current active Codex config",
    notActive: "Not active",
    noConfigWrittenYet: "No config written yet",
    savedPresets: "Saved Presets",
    savedCodexPresets: "Saved Codex presets",
    total: "total",
    active: "active",
    apiKeySaved: "saved",
    apiKeyMissing: "missing",
    loaded: "Loaded",
    loadIntoForm: "Load into form",
    loadAndApply: "Load and apply",
    noPresetsSavedYet: "No Codex presets have been saved yet. Fill the form above, then save one.",
    bootstrapLoading: "Loading bootstrap info...",
    testingConsole: "Testing Console",
    apiWebTester: "AI API Web Tester",
    loadingBootstrapData: "Loading bootstrap data...",
    clearResult: "Clear result",
    currentConnection: "Current connection",
    autoSelectOnRequest: "Auto select on request",
    loadModelList: "Load model list",
    phaseOneHint: "Phase 1 only connects the current backend flow. Free chat and custom image upload come next.",
    codexActive: "Codex Active",
    currentFormNotWritten: "Current form has not been written into Codex yet.",
    configFile: "config file",
    authFile: "auth file",
    close: "Close",
    defaultText: "Default Text",
    verifyTextEndpoint: "Verify the text endpoint",
    sendDefaultText: "Send default text",
    loadingDefaultTextPrompt: "Loading default text prompt...",
    defaultVision: "Default Vision",
    verifyVisionEndpoint: "Verify the multimodal endpoint",
    sendDefaultImage: "Send default image",
    defaultTestImage: "Default test image",
    loadingImage: "Loading image...",
    loadingDefaultVisionPrompt: "Loading default vision prompt...",
    visionHint:
      "This phase still uses the existing Python backend prompt and bundled image so we can validate the full React to BFF chain first.",
    latestResult: "Latest Result",
    mostRecentResponse: "Most recent response",
    idle: "Idle",
    vision: "Vision",
    text: "Text",
    model: "model",
    elapsed: "elapsed",
    totalTokens: "total tokens",
    response: "Response",
    noTextContent: "The model did not return text content.",
    rawPayload: "Raw payload",
    emptyStateTitle: "Fill the connection info, then click the default text or default image action.",
    emptyStateDescription:
      "This first step proves the React page is now wired to the existing Python Web BFF before we expand backend features.",
  },
  "zh-CN": {
    appName: "AI Tester",
    navTesting: "测试",
    navConnection: "连接",
    switchLanguage: "Switch to English",
    connectionPresets: "连接与预设",
    connectionSettingsTitle: "连接设置与 Codex 预设",
    connectionSettingsDescription:
      "第一阶段保留现有 Python Web 后端，并将 React 页面接入本地 BFF。这个页面用于管理连接信息、测试模型连通性，并将预设写回 Codex。",
    editCurrentConnection: "编辑当前连接",
    presetName: "预设名称",
    presetNamePlaceholder: "示例：company hk node",
    baseUrl: "接口地址",
    apiKey: "密钥",
    currentState: "当前状态",
    loadedModels: "已加载模型",
    defaultImage: "默认图片",
    ready: "已就绪",
    loading: "加载中",
    selectedModel: "已选模型",
    notSelected: "未选择",
    activeCodexItem: "当前 Codex 项",
    notWritten: "尚未写入",
    testConnectionAndLoadModels: "测试连接并加载模型",
    saveCodexPreset: "保存 Codex 预设",
    applyToCodex: "应用到 Codex",
    currentActiveCodexConfig: "当前生效的 Codex 配置",
    notActive: "未生效",
    noConfigWrittenYet: "尚未写入配置",
    savedPresets: "已保存预设",
    savedCodexPresets: "已保存的 Codex 预设",
    total: "总数",
    active: "生效中",
    apiKeySaved: "已保存",
    apiKeyMissing: "缺失",
    loaded: "已载入",
    loadIntoForm: "载入表单",
    loadAndApply: "载入并应用",
    noPresetsSavedYet: "还没有保存任何 Codex 预设。先填写上面的表单，再保存一个即可。",
    bootstrapLoading: "正在加载启动信息...",
    testingConsole: "测试控制台",
    apiWebTester: "AI API 网页测试器",
    loadingBootstrapData: "正在加载启动数据...",
    clearResult: "清空结果",
    currentConnection: "当前连接",
    autoSelectOnRequest: "请求时自动选择",
    loadModelList: "加载模型列表",
    phaseOneHint: "第一阶段只接通当前后端流程，自由聊天和自定义图片上传将在后续加入。",
    codexActive: "当前 Codex 配置",
    currentFormNotWritten: "当前表单内容尚未写入 Codex。",
    configFile: "配置文件",
    authFile: "认证文件",
    close: "关闭",
    defaultText: "默认文本",
    verifyTextEndpoint: "验证文本接口",
    sendDefaultText: "发送默认文本",
    loadingDefaultTextPrompt: "正在加载默认文本提示词...",
    defaultVision: "默认视觉",
    verifyVisionEndpoint: "验证多模态接口",
    sendDefaultImage: "发送默认图片",
    defaultTestImage: "默认测试图片",
    loadingImage: "正在加载图片...",
    loadingDefaultVisionPrompt: "正在加载默认视觉提示词...",
    visionHint: "这一阶段仍使用现有 Python 后端里的提示词和内置图片，先验证 React 到 BFF 的整条链路。",
    latestResult: "最近结果",
    mostRecentResponse: "最近一次响应",
    idle: "空闲",
    vision: "视觉",
    text: "文本",
    model: "模型",
    elapsed: "耗时",
    totalTokens: "总 token",
    response: "响应内容",
    noTextContent: "模型没有返回文本内容。",
    rawPayload: "原始载荷",
    emptyStateTitle: "先填写连接信息，再点击默认文本或默认图片操作。",
    emptyStateDescription: "这一步先证明 React 页面已经接通现有 Python Web BFF，后续再扩展更多后端能力。",
  },
} as const;

type TranslationKey = keyof typeof translations.en;

type LocaleContextValue = {
  locale: Locale;
  setLocale: (locale: Locale) => void;
  toggleLocale: () => void;
  t: (key: TranslationKey) => string;
};

const LocaleContext = createContext<LocaleContextValue | undefined>(undefined);

function resolveInitialLocale(): Locale {
  if (typeof window === "undefined") {
    return "en";
  }

  const storedLocale = window.localStorage.getItem(LOCALE_STORAGE_KEY);
  if (storedLocale === "en" || storedLocale === "zh-CN") {
    return storedLocale;
  }

  return window.navigator.language.toLowerCase().startsWith("zh") ? "zh-CN" : "en";
}

export function LocaleProvider({ children }: { children: ReactNode }) {
  const [locale, setLocale] = useState<Locale>(resolveInitialLocale);

  useEffect(() => {
    window.localStorage.setItem(LOCALE_STORAGE_KEY, locale);
  }, [locale]);

  const value = useMemo<LocaleContextValue>(() => {
    const t = (key: TranslationKey) => translations[locale][key] ?? translations.en[key];

    return {
      locale,
      setLocale,
      toggleLocale: () => setLocale((current) => (current === "en" ? "zh-CN" : "en")),
      t,
    };
  }, [locale]);

  return <LocaleContext.Provider value={value}>{children}</LocaleContext.Provider>;
}

export function useLocale() {
  const context = useContext(LocaleContext);
  if (context === undefined) {
    throw new Error("useLocale must be used within a LocaleProvider");
  }
  return context;
}
