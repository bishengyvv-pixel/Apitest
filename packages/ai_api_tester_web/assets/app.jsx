const { useEffect, useMemo, useState } = React;

function App() {
  const [bootstrap, setBootstrap] = useState(null);
  const [form, setForm] = useState({ base_url: "", api_key: "", model: "", preset_name: "" });
  const [models, setModels] = useState([]);
  const [codexPresets, setCodexPresets] = useState([]);
  const [codexActive, setCodexActive] = useState(null);
  const [codexStatus, setCodexStatus] = useState("");
  const [loading, setLoading] = useState({
    bootstrap: true,
    models: false,
    text: false,
    vision: false,
    codex_save: false,
    codex_apply: false,
  });
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    fetchJson("/api/bootstrap", { method: "GET" })
      .then((payload) => {
        setBootstrap(payload);
        setCodexPresets(payload.codex_presets || []);
        setCodexActive(payload.codex_active || null);
        setForm((current) => ({
          ...current,
          base_url: current.base_url || payload.codex_active?.base_url || "",
          api_key: current.api_key || payload.codex_active?.api_key || "",
          preset_name: current.preset_name || payload.codex_active?.name || "",
        }));
      })
      .catch((requestError) => {
        setError(getErrorMessage(requestError));
      })
      .finally(() => {
        setLoading((current) => ({ ...current, bootstrap: false }));
      });
  }, []);

  const canSubmit = useMemo(() => {
    return Boolean(form.base_url.trim() && form.api_key.trim());
  }, [form]);

  const canManageCodex = useMemo(() => {
    return Boolean(form.preset_name.trim() && form.base_url.trim() && form.api_key.trim());
  }, [form]);

  const updateField = (fieldName, value) => {
    setForm((current) => ({ ...current, [fieldName]: value }));
  };

  const applyPresetToForm = (presetName) => {
    const preset = codexPresets.find((item) => item.name === presetName);
    if (!preset) {
      return;
    }
    setForm((current) => ({
      ...current,
      base_url: preset.base_url || "",
      api_key: preset.api_key || "",
      preset_name: preset.name || "",
    }));
    setCodexStatus(`已载入预设：${preset.name}`);
  };

  const buildCodexPayload = () => {
    return {
      name: form.preset_name,
      base_url: form.base_url,
      api_key: form.api_key,
    };
  };

  const saveCodexPreset = async () => {
    setError("");
    setCodexStatus("");
    if (!canManageCodex) {
      setError("保存 Codex 预设前，请填写预设名称、baseurl 和 apikey。");
      return;
    }

    setLoading((current) => ({ ...current, codex_save: true }));
    try {
      const payload = await fetchJson("/api/codex-presets", {
        method: "POST",
        body: JSON.stringify(buildCodexPayload()),
      });
      setCodexPresets(payload.presets || []);
      if (payload.preset) {
        updateField("preset_name", payload.preset.name || "");
      }
      setCodexStatus(payload.message || "Codex 预设已保存。");
    } catch (requestError) {
      setError(getErrorMessage(requestError));
    } finally {
      setLoading((current) => ({ ...current, codex_save: false }));
    }
  };

  const applyCodexPreset = async () => {
    setError("");
    setCodexStatus("");
    if (!canManageCodex) {
      setError("应用到 Codex 前，请填写预设名称、baseurl 和 apikey。");
      return;
    }

    setLoading((current) => ({ ...current, codex_apply: true }));
    try {
      const payload = await fetchJson("/api/codex-apply", {
        method: "POST",
        body: JSON.stringify(buildCodexPayload()),
      });
      setCodexPresets(payload.presets || []);
      setCodexActive(payload.active || null);
      setCodexStatus(payload.message || "已写入 Codex 配置。");
    } catch (requestError) {
      setError(getErrorMessage(requestError));
    } finally {
      setLoading((current) => ({ ...current, codex_apply: false }));
    }
  };

  const loadModels = async () => {
    setError("");
    if (!canSubmit) {
      setError("请先填写 baseurl 和 apikey。\n模型列表虽然是可选项，但加载模型前仍需要连接信息。");
      return;
    }

    setLoading((current) => ({ ...current, models: true }));
    try {
      const payload = await fetchJson("/api/models", {
        method: "POST",
        body: JSON.stringify({ base_url: form.base_url, api_key: form.api_key }),
      });
      setModels(payload.models || []);
      if (!form.model && payload.selected_model) {
        updateField("model", payload.selected_model);
      }
    } catch (requestError) {
      setError(getErrorMessage(requestError));
    } finally {
      setLoading((current) => ({ ...current, models: false }));
    }
  };

  const sendDefaultRequest = async (kind) => {
    setError("");
    if (!canSubmit) {
      setError("baseurl 和 apikey 是必填项，请先填写后再发送默认请求。");
      return;
    }

    const route = kind === "vision" ? "/api/default-vision" : "/api/default-text";
    const loadingKey = kind === "vision" ? "vision" : "text";

    setLoading((current) => ({ ...current, [loadingKey]: true }));
    try {
      const payload = await fetchJson(route, {
        method: "POST",
        body: JSON.stringify({
          base_url: form.base_url,
          api_key: form.api_key,
          model: form.model,
        }),
      });
      setResult(payload);
      if (payload.model && !form.model) {
        updateField("model", payload.model);
      }
    } catch (requestError) {
      setError(getErrorMessage(requestError));
    } finally {
      setLoading((current) => ({ ...current, [loadingKey]: false }));
    }
  };

  return (
    <div className="app-shell">
      <section className="hero">
        <div className="hero-main">
          <span className="hero-kicker">React Web GUI / HTTP</span>
          <h1>{bootstrap?.title || "AI API Web 测试台"}</h1>
          <p>{bootstrap?.subtitle || "页面初始化中..."}</p>
          <div className="hero-checklist">
            <div className="check-item">
              <strong>1. 填连接信息</strong>
              <div className="muted">只需要 `baseurl` 和 `apikey`，不用再填 prompt 或图片路径。</div>
            </div>
            <div className="check-item">
              <strong>2. 保存 Codex 预设</strong>
              <div className="muted">你可以顺手给当前连接取一个名字，后续一键写回 Codex 配置。</div>
            </div>
            <div className="check-item">
              <strong>3. 默认文本</strong>
              <div className="muted">系统会发送内置文本测试，快速确认基础对话接口是否可用。</div>
            </div>
            <div className="check-item">
              <strong>4. 默认图片</strong>
              <div className="muted">系统会发送内置测试图片，帮助你验证多模态能力是否打通。</div>
            </div>
          </div>
        </div>
        <div className="hero-side">
          <h2 className="section-title">填写说明</h2>
          <p className="section-subtitle">这个界面刻意做成最小输入模式，避免让用户面对一堆不必要的参数。</p>
          <div className="guide-list">
            <div className="guide-card">
              <strong>`baseurl` 必填</strong>
              请输入你的 OpenAI 兼容接口根地址，例如 `https://api.openai.com/v1`。
            </div>
            <div className="guide-card">
              <strong>`apikey` 必填</strong>
              请输入当前接口对应的访问密钥。
            </div>
            <div className="guide-card">
              <strong>`Codex 预设名`</strong>
              给这组连接起一个容易记住的名字，保存后就能反复切换并应用到 `.codex/config.toml`。
            </div>
          </div>
        </div>
      </section>

      <section className="layout">
        <aside className="surface">
          <h2 className="section-title">连接信息</h2>
          <p className="section-subtitle">这里既是接口测试入口，也是 Codex 预设管理区。</p>

          <div className="form-grid">
            <div>
              <label className="field-label">
                <span>已存 Codex 预设</span>
                <span className="field-badge">可选</span>
              </label>
              <select className="select" value="" onChange={(event) => applyPresetToForm(event.target.value)}>
                <option value="">选择一个预设填入当前表单</option>
                {codexPresets.map((item) => (
                  <option key={item.provider_id || item.name} value={item.name}>
                    {item.name}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="field-label">
                <span>Codex 预设名</span>
                <span className="field-badge">必填</span>
              </label>
              <input
                className="input"
                value={form.preset_name}
                onChange={(event) => updateField("preset_name", event.target.value)}
                placeholder="例如：公司香港节点"
              />
            </div>

            <div>
              <label className="field-label">
                <span>baseurl</span>
                <span className="field-badge">必填</span>
              </label>
              <input
                className="input"
                value={form.base_url}
                onChange={(event) => updateField("base_url", event.target.value)}
                placeholder="https://api.openai.com/v1"
              />
            </div>

            <div>
              <label className="field-label">
                <span>apikey</span>
                <span className="field-badge">必填</span>
              </label>
              <input
                className="input"
                type="password"
                value={form.api_key}
                onChange={(event) => updateField("api_key", event.target.value)}
                placeholder="sk-..."
              />
            </div>

            <div>
              <label className="field-label">
                <span>模型列表</span>
                <span className="field-badge">可选</span>
              </label>
              <select
                className="select"
                value={form.model}
                onChange={(event) => updateField("model", event.target.value)}
              >
                <option value="">未选择，发送时自动决定</option>
                {models.map((item) => (
                  <option key={item.id} value={item.id}>
                    {item.id}
                  </option>
                ))}
              </select>
            </div>

            <div className="button-row">
              <button className="secondary-button" type="button" disabled={loading.models} onClick={loadModels}>
                {loading.models ? "模型加载中..." : "加载模型列表"}
              </button>
              <button className="secondary-button" type="button" disabled={loading.codex_save} onClick={saveCodexPreset}>
                {loading.codex_save ? "保存中..." : "保存 Codex 预设"}
              </button>
              <button className="primary-button" type="button" disabled={loading.codex_apply} onClick={applyCodexPreset}>
                {loading.codex_apply ? "写入中..." : "应用到 Codex"}
              </button>
            </div>

            {codexActive?.name ? (
              <div className="guide-card">
                <strong>当前 Codex 生效配置</strong>
                <div className="muted">名称：{codexActive.name || "-"}</div>
                <div className="muted">Base URL：{codexActive.base_url || "-"}</div>
                <div className="muted">配置文件：{codexActive.config_path || "-"}</div>
              </div>
            ) : null}

            {codexStatus ? (
              <div className="guide-card">
                <strong>操作结果</strong>
                <div className="muted">{codexStatus}</div>
              </div>
            ) : null}

            <div className="guide-card">
              <strong>当前引导逻辑</strong>
              先填好连接信息，测试可用后点“保存 Codex 预设”；确认无误再点“应用到 Codex”，就不用反复手动打开用户目录改配置了。
            </div>
          </div>
        </aside>

        <main className="action-stack">
          <section className="action-card">
            <div>
              <p className="hero-kicker">默认文本请求</p>
              <h3 className="action-title">一键验证基础对话接口</h3>
            </div>
            <div className="prompt-box">{bootstrap?.default_text_prompt || "正在读取默认文本..."}</div>
            <div className="button-row">
              <button className="primary-button" type="button" disabled={loading.text || loading.bootstrap} onClick={() => sendDefaultRequest("text")}>
                {loading.text ? "发送中..." : "发送默认文本"}
              </button>
            </div>
          </section>

          <section className="action-card">
            <div>
              <p className="hero-kicker">默认图片请求</p>
              <h3 className="action-title">一键验证多模态接口</h3>
            </div>
            <div className="image-box">
              {bootstrap?.default_vision_image_url ? (<img src={bootstrap.default_vision_image_url} alt="默认测试图片" />) : (<div className="prompt-box">默认测试图片加载中...</div>)}
              <div>
                <div className="prompt-box">{bootstrap?.default_vision_prompt || "正在读取默认图片请求..."}</div>
                <p className="helper-text">这张图片由系统内置，不需要用户再上传或手动选择。</p>
              </div>
            </div>
            <div className="button-row">
              <button className="primary-button" type="button" disabled={loading.vision || loading.bootstrap} onClick={() => sendDefaultRequest("vision")}>
                {loading.vision ? "发送中..." : "发送默认图片"}
              </button>
            </div>
          </section>

          <section className="result-grid">
            {error ? <div className="alert-box">{error}</div> : null}

            <div className="result-card">
              <div className="result-header">
                <div>
                  <h3 className="result-heading">最近一次响应</h3>
                  <div className="muted">无论点击默认文本还是默认图片，结果都会统一展示在这里。</div>
                </div>
                <span className="result-status">{result ? (result.kind === "vision" ? "图片响应" : "文本响应") : "等待操作"}</span>
              </div>

              {result ? (
                <>
                  <div className="result-meta">
                    <div className="meta-pill">
                      <span className="meta-label">实际模型</span>
                      <span className="meta-value">{result.model || "-"}</span>
                    </div>
                    <div className="meta-pill">
                      <span className="meta-label">响应耗时</span>
                      <span className="meta-value">{result.elapsed_seconds || 0}s</span>
                    </div>
                    <div className="meta-pill">
                      <span className="meta-label">总 Token</span>
                      <span className="meta-value">{result.usage?.total_tokens || 0}</span>
                    </div>
                  </div>

                  <div className="response-box">{result.response_text || "模型未返回文本内容。"}</div>
                  <div className="json-box">{JSON.stringify(result.raw || result, null, 2)}</div>
                </>
              ) : (
                <div className="empty-box">填写 `baseurl` 和 `apikey` 后，点击上方任意一个默认请求按钮，响应会出现在这里。</div>
              )}
            </div>
          </section>
        </main>
      </section>

      <div className="footer-note">
        当前页面通过本地 HTTP 服务运行；React 资源通过 CDN 加载，因此首次打开页面需要能够访问外网 CDN。
      </div>
    </div>
  );
}

async function fetchJson(url, options) {
  const response = await fetch(url, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  const payload = await response.json();
  if (!response.ok) {
    throw new Error(payload.error || "请求失败");
  }
  return payload;
}

function getErrorMessage(error) {
  if (!error) {
    return "未知错误";
  }
  return error.message || String(error);
}

ReactDOM.createRoot(document.getElementById("root")).render(<App />);
