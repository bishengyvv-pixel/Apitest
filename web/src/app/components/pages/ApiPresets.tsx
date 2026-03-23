import { CheckCircle2, Globe, KeyRound, Loader2, Save, Server, Sparkles, UploadCloud } from "lucide-react";
import { useApi } from "../../context/ApiContext";

export function ApiPresets() {
  const {
    bootstrap,
    form,
    models,
    codexPresets,
    codexActive,
    loading,
    updateForm,
    applyPresetToForm,
    loadModels,
    saveCodexPreset,
    applyCodexPreset,
    applySavedPresetToCodex,
  } = useApi();

  return (
    <div className="max-w-6xl mx-auto w-full flex flex-col gap-8 pb-20">
      <div className="flex flex-col gap-3">
        <p className="text-sm uppercase tracking-[0.28em] text-slate-400">Connection & Presets</p>
        <h1 className="text-3xl font-bold text-slate-800 tracking-tight">Connection settings and Codex presets</h1>
        <p className="max-w-3xl text-slate-500">
          Phase 1 keeps the current Python Web backend and wires React into the local BFF. This page manages connection data, tests model connectivity, and writes presets back into Codex.
        </p>
      </div>

      <div className="grid gap-6 xl:grid-cols-[1.15fr_0.85fr]">
        <section className="rounded-3xl border border-white/80 bg-white/55 p-6 shadow-lg backdrop-blur-xl">
          <div className="flex items-center gap-2 text-slate-700">
            <Server className="h-4 w-4 text-blue-500" />
            <span className="text-sm font-semibold">Edit current connection</span>
          </div>

          <div className="mt-5 grid gap-4 md:grid-cols-2">
            <label className="flex flex-col gap-2 md:col-span-2">
              <span className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">
                preset name
              </span>
              <input
                value={form.presetName}
                onChange={(event) => updateForm("presetName", event.target.value)}
                placeholder="Example: company hk node"
                className="rounded-2xl border border-slate-200 bg-white/80 px-4 py-3 text-slate-700 shadow-sm outline-none transition focus:border-blue-400 focus:ring-2 focus:ring-blue-500/10"
              />
            </label>

            <label className="flex flex-col gap-2">
              <span className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">
                baseurl
              </span>
              <div className="relative">
                <Globe className="pointer-events-none absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
                <input
                  value={form.baseUrl}
                  onChange={(event) => updateForm("baseUrl", event.target.value)}
                  placeholder="https://api.openai.com/v1"
                  className="w-full rounded-2xl border border-slate-200 bg-white/80 py-3 pl-11 pr-4 text-slate-700 shadow-sm outline-none transition focus:border-blue-400 focus:ring-2 focus:ring-blue-500/10"
                />
              </div>
            </label>

            <label className="flex flex-col gap-2">
              <span className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">
                apikey
              </span>
              <div className="relative">
                <KeyRound className="pointer-events-none absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
                <input
                  type="password"
                  value={form.apiKey}
                  onChange={(event) => updateForm("apiKey", event.target.value)}
                  placeholder="sk-..."
                  className="w-full rounded-2xl border border-slate-200 bg-white/80 py-3 pl-11 pr-4 font-mono text-slate-700 shadow-sm outline-none transition focus:border-blue-400 focus:ring-2 focus:ring-blue-500/10"
                />
              </div>
            </label>

            <div className="rounded-2xl border border-slate-200 bg-slate-50/80 p-4 md:col-span-2">
              <div className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">Current state</div>
              <div className="mt-3 grid gap-2 text-sm text-slate-600 sm:grid-cols-2">
                <div>loaded models: {models.length}</div>
                <div>default image: {bootstrap?.defaultVisionImageUrl ? "ready" : "loading"}</div>
                <div>selected model: {form.model || "not selected"}</div>
                <div>active Codex item: {codexActive?.name || "not written"}</div>
              </div>
            </div>
          </div>

          <div className="mt-5 flex flex-wrap gap-3">
            <button
              onClick={() => void loadModels()}
              disabled={loading.models || loading.bootstrap}
              className="inline-flex items-center gap-2 rounded-2xl bg-slate-900 px-4 py-3 text-sm font-semibold text-white shadow-lg shadow-slate-900/15 transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {loading.models ? <Loader2 className="h-4 w-4 animate-spin" /> : <Sparkles className="h-4 w-4" />}
              Test connection and load models
            </button>
            <button
              onClick={() => void saveCodexPreset()}
              disabled={loading.codexSave}
              className="inline-flex items-center gap-2 rounded-2xl border border-slate-200 bg-white/80 px-4 py-3 text-sm font-semibold text-slate-700 shadow-sm transition hover:bg-white disabled:cursor-not-allowed disabled:opacity-60"
            >
              {loading.codexSave ? <Loader2 className="h-4 w-4 animate-spin" /> : <Save className="h-4 w-4" />}
              Save Codex preset
            </button>
            <button
              onClick={() => void applyCodexPreset()}
              disabled={loading.codexApply}
              className="inline-flex items-center gap-2 rounded-2xl bg-blue-600 px-4 py-3 text-sm font-semibold text-white shadow-lg shadow-blue-500/20 transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {loading.codexApply ? <Loader2 className="h-4 w-4 animate-spin" /> : <UploadCloud className="h-4 w-4" />}
              Apply to Codex
            </button>
          </div>
        </section>

        <section className="rounded-3xl border border-white/80 bg-white/55 p-6 shadow-lg backdrop-blur-xl">
          <div className="flex items-center gap-2 text-slate-700">
            <CheckCircle2 className="h-4 w-4 text-emerald-500" />
            <span className="text-sm font-semibold">Current active Codex config</span>
          </div>

          <div className="mt-5 rounded-3xl border border-slate-200 bg-white/80 p-5 shadow-sm">
            <div className="text-xl font-semibold text-slate-800">{codexActive?.name || "Not active"}</div>
            <div className="mt-2 text-sm text-slate-500">{codexActive?.baseUrl || "No config written yet"}</div>
            <div className="mt-4 space-y-2 text-xs leading-6 text-slate-500">
              <div>provider_id: {codexActive?.providerId || "-"}</div>
              <div>config.toml: {codexActive?.configPath || "-"}</div>
              <div>auth.json: {codexActive?.authPath || "-"}</div>
            </div>
          </div>

          <div className="mt-5 rounded-3xl border border-blue-100 bg-gradient-to-br from-blue-50 via-white to-cyan-50 p-5 text-sm leading-7 text-slate-600">
            {bootstrap?.subtitle || "Loading bootstrap info..."}
          </div>
        </section>
      </div>

      <section className="rounded-3xl border border-white/80 bg-white/55 p-6 shadow-lg backdrop-blur-xl">
        <div className="flex items-center justify-between gap-4">
          <div>
            <p className="text-sm uppercase tracking-[0.22em] text-slate-400">Saved Presets</p>
            <h2 className="mt-2 text-2xl font-semibold text-slate-800">Saved Codex presets</h2>
          </div>
          <div className="rounded-full border border-slate-200 bg-white/80 px-3 py-1 text-xs font-semibold text-slate-500">
            total {codexPresets.length}
          </div>
        </div>

        {codexPresets.length ? (
          <div className="mt-5 grid gap-4 md:grid-cols-2 xl:grid-cols-3">
            {codexPresets.map((preset) => {
              const isCurrent = preset.name === form.presetName;
              const isActive = preset.name === codexActive?.name;

              return (
                <article
                  key={preset.providerId || preset.name}
                  className={`rounded-3xl border p-5 shadow-sm transition ${
                    isCurrent
                      ? "border-blue-200 bg-blue-50/80"
                      : "border-slate-200 bg-white/85"
                  }`}
                >
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <div className="text-lg font-semibold text-slate-800">{preset.name}</div>
                      <div className="mt-1 break-all text-sm text-slate-500">{preset.baseUrl}</div>
                    </div>
                    {isActive ? (
                      <span className="rounded-full bg-emerald-100 px-2.5 py-1 text-xs font-semibold text-emerald-700">
                        active
                      </span>
                    ) : null}
                  </div>

                  <div className="mt-4 rounded-2xl bg-slate-50 px-4 py-3 text-xs leading-6 text-slate-500">
                    provider_id: {preset.providerId || "-"}
                    <br />
                    apikey: {preset.apiKey ? "saved" : "missing"}
                  </div>

                  <div className="mt-4 flex flex-wrap gap-2">
                    <button
                      onClick={() => applyPresetToForm(preset.name)}
                      className="rounded-2xl border border-slate-200 bg-white px-3 py-2 text-sm font-semibold text-slate-700 transition hover:bg-slate-50"
                    >
                      {isCurrent ? "Loaded" : "Load into form"}
                    </button>
                    <button
                      onClick={() => void applySavedPresetToCodex(preset.name)}
                      disabled={loading.codexApply}
                      className="rounded-2xl bg-slate-900 px-3 py-2 text-sm font-semibold text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-60"
                    >
                      Load and apply
                    </button>
                  </div>
                </article>
              );
            })}
          </div>
        ) : (
          <div className="mt-5 rounded-3xl border border-dashed border-slate-200 bg-white/70 px-6 py-10 text-center text-sm leading-7 text-slate-500">
            No Codex presets have been saved yet. Fill the form above, then save one.
          </div>
        )}
      </section>
    </div>
  );
}
