import { AlertCircle, Bot, Image as ImageIcon, Layers3, Loader2, RefreshCcw, Sparkles, Trash2 } from "lucide-react";
import { useApi } from "../../context/ApiContext";

export function ApiTesting() {
  const {
    bootstrap,
    form,
    models,
    codexActive,
    result,
    loading,
    errorMessage,
    updateForm,
    loadModels,
    sendDefaultRequest,
    clearResult,
    clearError,
  } = useApi();

  return (
    <div className="h-full flex flex-col max-w-6xl mx-auto w-full gap-6 pb-4">
      <div className="flex flex-col gap-3 shrink-0">
        <div className="flex items-start justify-between gap-4">
          <div>
            <p className="text-sm uppercase tracking-[0.28em] text-slate-400">Testing Console</p>
            <h1 className="text-3xl font-bold text-slate-800 tracking-tight">
              {bootstrap?.title || "AI API Web Tester"}
            </h1>
            <p className="text-slate-500 mt-2">
              {bootstrap?.subtitle || "Loading bootstrap data..."}
            </p>
          </div>
          <button
            onClick={clearResult}
            disabled={!result}
            className="inline-flex items-center gap-2 rounded-2xl border border-slate-200 bg-white/70 px-4 py-2.5 text-sm font-medium text-slate-600 shadow-sm transition hover:bg-white disabled:cursor-not-allowed disabled:opacity-50"
          >
            <Trash2 className="h-4 w-4" />
            Clear result
          </button>
        </div>

        <div className="grid gap-4 lg:grid-cols-[1.35fr_0.95fr]">
          <section className="rounded-3xl border border-white/80 bg-white/55 p-5 shadow-lg backdrop-blur-xl">
            <div className="flex items-center gap-2 text-slate-700">
              <Layers3 className="h-4 w-4 text-blue-500" />
              <span className="text-sm font-semibold">Current connection</span>
            </div>
            <div className="mt-4 grid gap-4 md:grid-cols-2">
              <label className="flex flex-col gap-2">
                <span className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">
                  baseurl
                </span>
                <input
                  value={form.baseUrl}
                  onChange={(event) => updateForm("baseUrl", event.target.value)}
                  placeholder="https://api.openai.com/v1"
                  className="rounded-2xl border border-slate-200 bg-white/80 px-4 py-3 text-slate-700 shadow-sm outline-none transition focus:border-blue-400 focus:ring-2 focus:ring-blue-500/10"
                />
              </label>
              <label className="flex flex-col gap-2">
                <span className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">
                  apikey
                </span>
                <input
                  type="password"
                  value={form.apiKey}
                  onChange={(event) => updateForm("apiKey", event.target.value)}
                  placeholder="sk-..."
                  className="rounded-2xl border border-slate-200 bg-white/80 px-4 py-3 font-mono text-slate-700 shadow-sm outline-none transition focus:border-blue-400 focus:ring-2 focus:ring-blue-500/10"
                />
              </label>
              <label className="flex flex-col gap-2">
                <span className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">
                  model
                </span>
                <select
                  value={form.model}
                  onChange={(event) => updateForm("model", event.target.value)}
                  className="rounded-2xl border border-slate-200 bg-white/80 px-4 py-3 text-slate-700 shadow-sm outline-none transition focus:border-blue-400 focus:ring-2 focus:ring-blue-500/10"
                >
                  <option value="">Auto select on request</option>
                  {models.map((item) => (
                    <option key={item.id} value={item.id}>
                      {item.id}
                    </option>
                  ))}
                </select>
              </label>
              <div className="flex flex-col justify-end gap-2">
                <button
                  onClick={() => void loadModels()}
                  disabled={loading.models || loading.bootstrap}
                  className="inline-flex items-center justify-center gap-2 rounded-2xl bg-slate-900 px-4 py-3 text-sm font-semibold text-white shadow-lg shadow-slate-900/15 transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-60"
                >
                  {loading.models ? <Loader2 className="h-4 w-4 animate-spin" /> : <RefreshCcw className="h-4 w-4" />}
                  Load model list
                </button>
                <p className="text-xs text-slate-400">
                  Phase 1 only connects the current backend flow. Free chat and custom image upload come next.
                </p>
              </div>
            </div>
          </section>

          <section className="rounded-3xl border border-white/80 bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 p-5 text-slate-100 shadow-lg">
            <p className="text-xs uppercase tracking-[0.24em] text-slate-400">Codex Active</p>
            <div className="mt-4 space-y-3">
              <div>
                <div className="text-lg font-semibold">{codexActive?.name || "Not active"}</div>
                <div className="text-sm text-slate-400">
                  {codexActive?.baseUrl || "Current form has not been written into Codex yet."}
                </div>
              </div>
              <div className="rounded-2xl border border-white/10 bg-white/5 p-4 text-sm text-slate-300">
                <div>config file: {codexActive?.configPath || "-"}</div>
                <div className="mt-1">auth file: {codexActive?.authPath || "-"}</div>
              </div>
            </div>
          </section>
        </div>
      </div>

      {errorMessage ? (
        <div className="flex items-start justify-between gap-3 rounded-2xl border border-amber-200 bg-amber-50 px-4 py-3 text-amber-800 shadow-sm">
          <div className="flex items-start gap-3">
            <AlertCircle className="mt-0.5 h-5 w-5 shrink-0" />
            <p className="whitespace-pre-wrap text-sm leading-6">{errorMessage}</p>
          </div>
          <button
            onClick={clearError}
            className="rounded-full px-2 py-1 text-xs font-semibold text-amber-700 transition hover:bg-amber-100"
          >
            Close
          </button>
        </div>
      ) : null}

      <div className="grid gap-6 xl:grid-cols-[1.05fr_0.95fr]">
        <div className="grid gap-6">
          <section className="rounded-3xl border border-white/80 bg-white/55 p-6 shadow-lg backdrop-blur-xl">
            <div className="flex items-start justify-between gap-4">
              <div>
                <p className="text-sm uppercase tracking-[0.22em] text-slate-400">Default Text</p>
                <h2 className="mt-2 text-2xl font-semibold text-slate-800">Verify the text endpoint</h2>
              </div>
              <button
                onClick={() => void sendDefaultRequest("text")}
                disabled={loading.text || loading.bootstrap}
                className="inline-flex items-center gap-2 rounded-2xl bg-blue-600 px-4 py-3 text-sm font-semibold text-white shadow-lg shadow-blue-500/20 transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-60"
              >
                {loading.text ? <Loader2 className="h-4 w-4 animate-spin" /> : <Sparkles className="h-4 w-4" />}
                Send default text
              </button>
            </div>
            <div className="mt-5 rounded-3xl border border-blue-100 bg-gradient-to-br from-blue-50 via-white to-cyan-50 p-5 text-sm leading-7 text-slate-700">
              {bootstrap?.defaultTextPrompt || "Loading default text prompt..."}
            </div>
          </section>

          <section className="rounded-3xl border border-white/80 bg-white/55 p-6 shadow-lg backdrop-blur-xl">
            <div className="flex items-start justify-between gap-4">
              <div>
                <p className="text-sm uppercase tracking-[0.22em] text-slate-400">Default Vision</p>
                <h2 className="mt-2 text-2xl font-semibold text-slate-800">Verify the multimodal endpoint</h2>
              </div>
              <button
                onClick={() => void sendDefaultRequest("vision")}
                disabled={loading.vision || loading.bootstrap}
                className="inline-flex items-center gap-2 rounded-2xl bg-slate-900 px-4 py-3 text-sm font-semibold text-white shadow-lg shadow-slate-900/15 transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-60"
              >
                {loading.vision ? <Loader2 className="h-4 w-4 animate-spin" /> : <ImageIcon className="h-4 w-4" />}
                Send default image
              </button>
            </div>
            <div className="mt-5 grid gap-5 lg:grid-cols-[240px_1fr]">
              <div className="overflow-hidden rounded-3xl border border-slate-200 bg-white shadow-sm">
                {bootstrap?.defaultVisionImageUrl ? (
                  <img
                    src={bootstrap.defaultVisionImageUrl}
                    alt="Default test image"
                    className="h-full min-h-[220px] w-full object-cover"
                  />
                ) : (
                  <div className="flex min-h-[220px] items-center justify-center bg-slate-100 text-sm text-slate-400">
                    Loading image...
                  </div>
                )}
              </div>
              <div className="rounded-3xl border border-slate-200 bg-white/80 p-5 text-sm leading-7 text-slate-700 shadow-sm">
                <div>{bootstrap?.defaultVisionPrompt || "Loading default vision prompt..."}</div>
                <div className="mt-4 rounded-2xl bg-slate-50 px-4 py-3 text-xs leading-6 text-slate-500">
                  This phase still uses the existing Python backend prompt and bundled image so we can validate the full React to BFF chain first.
                </div>
              </div>
            </div>
          </section>
        </div>

        <section className="rounded-3xl border border-white/80 bg-white/55 p-6 shadow-lg backdrop-blur-xl">
          <div className="flex items-start justify-between gap-4">
            <div>
              <p className="text-sm uppercase tracking-[0.22em] text-slate-400">Latest Result</p>
              <h2 className="mt-2 text-2xl font-semibold text-slate-800">Most recent response</h2>
            </div>
            <div className="rounded-full border border-slate-200 bg-white/70 px-3 py-1 text-xs font-semibold text-slate-500">
              {result ? (result.kind === "vision" ? "Vision" : "Text") : "Idle"}
            </div>
          </div>

          {result ? (
            <div className="mt-5 space-y-5">
              <div className="grid gap-3 sm:grid-cols-3">
                <ResultStat label="model" value={result.model || "-"} />
                <ResultStat label="elapsed" value={`${result.elapsedSeconds || 0}s`} />
                <ResultStat label="total tokens" value={String(result.usage.totalTokens || 0)} />
              </div>

              <div className="rounded-3xl border border-slate-200 bg-white/90 p-5 shadow-sm">
                <div className="flex items-center gap-2 text-sm font-semibold text-slate-600">
                  <Bot className="h-4 w-4 text-blue-500" />
                  Response
                </div>
                <div className="mt-3 whitespace-pre-wrap text-sm leading-7 text-slate-700">
                  {result.responseText || "The model did not return text content."}
                </div>
              </div>

              <div className="rounded-3xl border border-slate-200 bg-slate-950 p-4 text-xs leading-6 text-slate-200 shadow-sm">
                <div className="mb-2 font-semibold text-slate-400">Raw payload</div>
                <pre className="overflow-x-auto whitespace-pre-wrap break-all">
                  {JSON.stringify(result.raw, null, 2)}
                </pre>
              </div>
            </div>
          ) : (
            <div className="mt-5 flex min-h-[420px] flex-col items-center justify-center rounded-3xl border border-dashed border-slate-200 bg-white/50 px-8 text-center text-slate-400">
              <Bot className="h-12 w-12 opacity-60" />
              <p className="mt-4 text-base font-medium text-slate-500">
                Fill the connection info, then click the default text or default image action.
              </p>
              <p className="mt-2 text-sm leading-6">
                This first step proves the React page is now wired to the existing Python Web BFF before we expand backend features.
              </p>
            </div>
          )}
        </section>
      </div>
    </div>
  );
}

function ResultStat({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-2xl border border-slate-200 bg-white/80 p-4 shadow-sm">
      <div className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">{label}</div>
      <div className="mt-2 text-sm font-semibold text-slate-700">{value}</div>
    </div>
  );
}
