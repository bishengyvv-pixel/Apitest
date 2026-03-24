import { createContext, useContext, useEffect, useState, type ReactNode } from "react";
import { toast } from "sonner";

export type ApiForm = {
  presetName: string;
  baseUrl: string;
  apiKey: string;
  model: string;
};

export type ApiModel = {
  id: string;
  object: string;
  ownedBy: string;
};

export type CodexPreset = {
  name: string;
  baseUrl: string;
  apiKey: string;
  providerId: string;
};

export type CodexActive = {
  name: string;
  providerId: string;
  baseUrl: string;
  apiKey: string;
  configPath: string;
  authPath: string;
};

export type BootstrapPayload = {
  title: string;
  subtitle: string;
  defaultTextPrompt: string;
  defaultVisionPrompt: string;
  defaultVisionImageUrl: string;
};

export type RequestResult = {
  kind: string;
  model: string;
  prompt: string;
  responseText: string;
  createdAt: string;
  elapsedSeconds: number;
  usage: {
    promptTokens: number;
    completionTokens: number;
    totalTokens: number;
  };
  raw: unknown;
  defaultVisionImageUrl?: string;
};

type LoadingState = {
  bootstrap: boolean;
  models: boolean;
  codexSave: boolean;
  codexApply: boolean;
  codexDelete: boolean;
  text: boolean;
  vision: boolean;
};

interface ApiContextType {
  bootstrap: BootstrapPayload | null;
  form: ApiForm;
  models: ApiModel[];
  codexPresets: CodexPreset[];
  codexActive: CodexActive | null;
  result: RequestResult | null;
  loading: LoadingState;
  errorMessage: string;
  updateForm: (field: keyof ApiForm, value: string) => void;
  applyPresetToForm: (presetName: string) => void;
  loadModels: () => Promise<void>;
  saveCodexPreset: () => Promise<void>;
  applyCodexPreset: () => Promise<void>;
  applySavedPresetToCodex: (presetName: string) => Promise<void>;
  deleteSavedPreset: (presetName: string) => Promise<void>;
  sendDefaultRequest: (kind: "text" | "vision") => Promise<void>;
  clearResult: () => void;
  clearError: () => void;
}

const ApiContext = createContext<ApiContextType | undefined>(undefined);

const defaultForm: ApiForm = {
  presetName: "",
  baseUrl: "",
  apiKey: "",
  model: "",
};

const defaultLoadingState: LoadingState = {
  bootstrap: true,
  models: false,
  codexSave: false,
  codexApply: false,
  codexDelete: false,
  text: false,
  vision: false,
};

export function ApiProvider({ children }: { children: ReactNode }) {
  const [bootstrap, setBootstrap] = useState<BootstrapPayload | null>(null);
  const [form, setForm] = useState<ApiForm>(defaultForm);
  const [models, setModels] = useState<ApiModel[]>([]);
  const [codexPresets, setCodexPresets] = useState<CodexPreset[]>([]);
  const [codexActive, setCodexActive] = useState<CodexActive | null>(null);
  const [result, setResult] = useState<RequestResult | null>(null);
  const [loading, setLoading] = useState<LoadingState>(defaultLoadingState);
  const [errorMessage, setErrorMessage] = useState("");

  useEffect(() => {
    const loadBootstrap = async () => {
      try {
        const payload = await fetchJson("/api/bootstrap", { method: "GET" });
        const nextBootstrap = normalizeBootstrapPayload(payload);
        const nextPresets = normalizePresetList(payload.codex_presets);
        const nextActive = normalizeCodexActive(payload.codex_active);

        setBootstrap(nextBootstrap);
        setCodexPresets(nextPresets);
        setCodexActive(nextActive);
        setForm((current) => ({
          ...current,
          presetName: current.presetName || nextActive?.name || "",
          baseUrl: current.baseUrl || nextActive?.baseUrl || "",
          apiKey: current.apiKey || nextActive?.apiKey || "",
        }));
      } catch (error) {
        const message = getErrorMessage(error);
        setErrorMessage(message);
        toast.error(message);
      } finally {
        setLoading((current) => ({ ...current, bootstrap: false }));
      }
    };

    void loadBootstrap();
  }, []);

  const updateForm = (field: keyof ApiForm, value: string) => {
    setForm((current) => ({ ...current, [field]: value }));
    if (errorMessage) {
      setErrorMessage("");
    }
  };

  const applyPresetToForm = (presetName: string) => {
    const preset = codexPresets.find((item) => item.name === presetName);
    if (!preset) {
      return;
    }

    setForm((current) => ({
      ...current,
      presetName: preset.name,
      baseUrl: preset.baseUrl,
      apiKey: preset.apiKey,
    }));
    setErrorMessage("");
    toast.success(`Preset loaded: ${preset.name}`);
  };

  const loadModels = async () => {
    if (!ensureConnectionReady(form, setErrorMessage)) {
      return;
    }

    setLoading((current) => ({ ...current, models: true }));
    try {
      const payload = await fetchJson("/api/models", {
        method: "POST",
        body: JSON.stringify(buildConnectionPayload(form)),
      });
      const nextModels = normalizeModelList(payload.models);
      setModels(nextModels);
      setForm((current) => ({
        ...current,
        model: resolveSelectedModel(current.model, nextModels, payload.selected_model),
      }));
      setErrorMessage("");
      toast.success(`Model list refreshed: ${nextModels.length}`);
    } catch (error) {
      const message = getErrorMessage(error);
      setErrorMessage(message);
      toast.error(message);
    } finally {
      setLoading((current) => ({ ...current, models: false }));
    }
  };

  const saveCodexPreset = async () => {
    if (!ensurePresetReady(form, setErrorMessage)) {
      return;
    }

    setLoading((current) => ({ ...current, codexSave: true }));
    try {
      const payload = await fetchJson("/api/codex-presets", {
        method: "POST",
        body: JSON.stringify(buildPresetPayload(form)),
      });
      setCodexPresets(normalizePresetList(payload.presets));
      if (payload.preset?.name) {
        setForm((current) => ({ ...current, presetName: String(payload.preset.name) }));
      }
      setErrorMessage("");
      toast.success(payload.message || "Preset saved.");
    } catch (error) {
      const message = getErrorMessage(error);
      setErrorMessage(message);
      toast.error(message);
    } finally {
      setLoading((current) => ({ ...current, codexSave: false }));
    }
  };

  const applyCodexPreset = async () => {
    if (!ensurePresetReady(form, setErrorMessage)) {
      return;
    }

    setLoading((current) => ({ ...current, codexApply: true }));
    try {
      const payload = await fetchJson("/api/codex-apply", {
        method: "POST",
        body: JSON.stringify(buildPresetPayload(form)),
      });
      setCodexPresets(normalizePresetList(payload.presets));
      setCodexActive(normalizeCodexActive(payload.active));
      setErrorMessage("");
      toast.success(payload.message || "Codex config updated.");
    } catch (error) {
      const message = getErrorMessage(error);
      setErrorMessage(message);
      toast.error(message);
    } finally {
      setLoading((current) => ({ ...current, codexApply: false }));
    }
  };

  const applySavedPresetToCodex = async (presetName: string) => {
    const preset = codexPresets.find((item) => item.name === presetName);
    if (!preset) {
      const message = "Preset not found.";
      setErrorMessage(message);
      toast.error(message);
      return;
    }

    setForm((current) => ({
      ...current,
      presetName: preset.name,
      baseUrl: preset.baseUrl,
      apiKey: preset.apiKey,
    }));

    setLoading((current) => ({ ...current, codexApply: true }));
    try {
      const payload = await fetchJson("/api/codex-apply", {
        method: "POST",
        body: JSON.stringify({
          name: preset.name,
          base_url: preset.baseUrl,
          api_key: preset.apiKey,
        }),
      });
      setCodexPresets(normalizePresetList(payload.presets));
      setCodexActive(normalizeCodexActive(payload.active));
      setErrorMessage("");
      toast.success(payload.message || "Codex config updated.");
    } catch (error) {
      const message = getErrorMessage(error);
      setErrorMessage(message);
      toast.error(message);
    } finally {
      setLoading((current) => ({ ...current, codexApply: false }));
    }
  };

  const deleteSavedPreset = async (presetName: string) => {
    const normalizedName = presetName.trim();
    if (!normalizedName) {
      return;
    }

    setLoading((current) => ({ ...current, codexDelete: true }));
    try {
      const payload = await fetchJson("/api/codex-presets", {
        method: "DELETE",
        body: JSON.stringify({ name: normalizedName }),
      });
      const nextPresets = normalizePresetList(payload.presets);
      setCodexPresets(nextPresets);
      setErrorMessage("");
      setForm((current) => {
        if (current.presetName !== normalizedName) {
          return current;
        }

        const fallbackPreset = nextPresets[0];
        return {
          ...current,
          presetName: fallbackPreset?.name || "",
          baseUrl: fallbackPreset?.baseUrl || "",
          apiKey: fallbackPreset?.apiKey || "",
        };
      });
      toast.success(payload.message || "Preset deleted.");
    } catch (error) {
      const message = getErrorMessage(error);
      setErrorMessage(message);
      toast.error(message);
    } finally {
      setLoading((current) => ({ ...current, codexDelete: false }));
    }
  };
  const sendDefaultRequest = async (kind: "text" | "vision") => {
    if (!ensureConnectionReady(form, setErrorMessage)) {
      return;
    }

    const loadingKey = kind === "vision" ? "vision" : "text";
    const route = kind === "vision" ? "/api/default-vision" : "/api/default-text";

    setLoading((current) => ({ ...current, [loadingKey]: true }));
    try {
      const payload = await fetchJson(route, {
        method: "POST",
        body: JSON.stringify({
          ...buildConnectionPayload(form),
          model: form.model.trim(),
        }),
      });
      const nextResult = normalizeResult(payload);
      setResult(nextResult);
      if (nextResult.model) {
        setForm((current) => ({ ...current, model: nextResult.model }));
      }
      setErrorMessage("");
      toast.success(kind === "vision" ? "Default vision request finished." : "Default text request finished.");
    } catch (error) {
      const message = getErrorMessage(error);
      setErrorMessage(message);
      toast.error(message);
    } finally {
      setLoading((current) => ({ ...current, [loadingKey]: false }));
    }
  };

  const clearResult = () => {
    setResult(null);
  };

  const clearError = () => {
    setErrorMessage("");
  };

  return (
    <ApiContext.Provider
      value={{
        bootstrap,
        form,
        models,
        codexPresets,
        codexActive,
        result,
        loading,
        errorMessage,
        updateForm,
        applyPresetToForm,
        loadModels,
        saveCodexPreset,
        applyCodexPreset,
        applySavedPresetToCodex,
        deleteSavedPreset,
        sendDefaultRequest,
        clearResult,
        clearError,
      }}
    >
      {children}
    </ApiContext.Provider>
  );
}

export function useApi() {
  const context = useContext(ApiContext);
  if (context === undefined) {
    throw new Error("useApi must be used within an ApiProvider");
  }
  return context;
}

function ensureConnectionReady(form: ApiForm, setErrorMessage: (message: string) => void) {
  if (!form.baseUrl.trim() || !form.apiKey.trim()) {
    const message = "Please fill baseurl and apikey first.";
    setErrorMessage(message);
    toast.error(message);
    return false;
  }
  return true;
}

function ensurePresetReady(form: ApiForm, setErrorMessage: (message: string) => void) {
  if (!form.presetName.trim() || !form.baseUrl.trim() || !form.apiKey.trim()) {
    const message = "Please fill preset name, baseurl, and apikey first.";
    setErrorMessage(message);
    toast.error(message);
    return false;
  }
  return true;
}

function buildConnectionPayload(form: ApiForm) {
  return {
    base_url: form.baseUrl.trim(),
    api_key: form.apiKey.trim(),
  };
}

function buildPresetPayload(form: ApiForm) {
  return {
    name: form.presetName.trim(),
    base_url: form.baseUrl.trim(),
    api_key: form.apiKey.trim(),
  };
}

function resolveSelectedModel(
  currentModel: string,
  models: ApiModel[],
  selectedModel: unknown,
) {
  const current = currentModel.trim();
  if (current && models.some((item) => item.id === current)) {
    return current;
  }

  const selected = toCleanText(selectedModel);
  if (selected) {
    return selected;
  }

  return models[0]?.id || "";
}

function normalizeBootstrapPayload(payload: any): BootstrapPayload {
  return {
    title: toCleanText(payload?.title),
    subtitle: toCleanText(payload?.subtitle),
    defaultTextPrompt: toCleanText(payload?.default_text_prompt),
    defaultVisionPrompt: toCleanText(payload?.default_vision_prompt),
    defaultVisionImageUrl: toCleanText(payload?.default_vision_image_url),
  };
}

function normalizeModelList(items: unknown): ApiModel[] {
  if (!Array.isArray(items)) {
    return [];
  }

  return items
    .map((item) => ({
      id: toCleanText((item as any)?.id),
      object: toCleanText((item as any)?.object),
      ownedBy: toCleanText((item as any)?.owned_by),
    }))
    .filter((item) => item.id);
}

function normalizePresetList(items: unknown): CodexPreset[] {
  if (!Array.isArray(items)) {
    return [];
  }

  return items
    .map((item) => ({
      name: toCleanText((item as any)?.name),
      baseUrl: toCleanText((item as any)?.base_url),
      apiKey: toCleanText((item as any)?.api_key),
      providerId: toCleanText((item as any)?.provider_id),
    }))
    .filter((item) => item.name);
}

function normalizeCodexActive(item: any): CodexActive | null {
  if (!item || typeof item !== "object") {
    return null;
  }

  const name = toCleanText(item.name);
  const providerId = toCleanText(item.provider_id);
  const baseUrl = toCleanText(item.base_url);
  const apiKey = toCleanText(item.api_key);
  const configPath = toCleanText(item.config_path);
  const authPath = toCleanText(item.auth_path);

  if (!name && !providerId && !baseUrl && !apiKey && !configPath && !authPath) {
    return null;
  }

  return {
    name,
    providerId,
    baseUrl,
    apiKey,
    configPath,
    authPath,
  };
}

function normalizeResult(payload: any): RequestResult {
  return {
    kind: toCleanText(payload?.kind),
    model: toCleanText(payload?.model),
    prompt: toCleanText(payload?.prompt),
    responseText: toCleanText(payload?.response_text),
    createdAt: toCleanText(payload?.created_at),
    elapsedSeconds: Number(payload?.elapsed_seconds) || 0,
    usage: {
      promptTokens: Number(payload?.usage?.prompt_tokens) || 0,
      completionTokens: Number(payload?.usage?.completion_tokens) || 0,
      totalTokens: Number(payload?.usage?.total_tokens) || 0,
    },
    raw: payload?.raw ?? payload,
    defaultVisionImageUrl: toCleanText(payload?.default_vision_image_url),
  };
}

async function fetchJson(url: string, options: RequestInit) {
  const response = await fetch(url, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  const rawText = await response.text();
  let payload: any = {};

  if (rawText.trim()) {
    try {
      payload = JSON.parse(rawText);
    } catch {
      if (!response.ok) {
        throw new Error(rawText.trim() || `Request failed with HTTP ${response.status}.`);
      }
      throw new Error(
        "Service returned a non-JSON response. Check whether baseurl points to a valid `/v1` API endpoint.",
      );
    }
  }

  if (!response.ok) {
    throw new Error(
      toCleanText(payload?.error) || rawText.trim() || `Request failed with HTTP ${response.status}.`,
    );
  }
  return payload;
}

function getErrorMessage(error: unknown) {
  if (error instanceof Error) {
    return error.message;
  }
  return String(error || "Unknown error");
}

function toCleanText(value: unknown) {
  if (value === null || value === undefined) {
    return "";
  }
  return String(value).trim();
}

