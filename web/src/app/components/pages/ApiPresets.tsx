import { CheckCircle2, Globe, KeyRound, Loader2, Save, Server, Sparkles, UploadCloud } from "lucide-react";
import { motion, useReducedMotion } from "motion/react";
import { useApi } from "../../context/ApiContext";
import { useLocale } from "../../context/LocaleContext";

const pageReveal = {
  hidden: { opacity: 0, y: 20, filter: "blur(10px)" },
  visible: {
    opacity: 1,
    y: 0,
    filter: "blur(0px)",
    transition: { duration: 0.45, ease: "easeOut" },
  },
};

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
  const { t } = useLocale();
  const reduceMotion = useReducedMotion();

  return (
    <motion.div
      className="max-w-6xl mx-auto w-full flex flex-col gap-8 pb-20"
      initial={reduceMotion ? false : "hidden"}
      animate={reduceMotion ? undefined : "visible"}
      variants={pageReveal}
    >
      <motion.div className="flex flex-col gap-3" variants={pageReveal}>
        <p className="text-sm uppercase tracking-[0.28em] text-slate-400">{t("connectionPresets")}</p>
        <h1 className="[font-family:var(--font-display)] text-3xl font-bold tracking-[-0.05em] text-slate-800 md:text-[2.8rem]">{t("connectionSettingsTitle")}</h1>
        <p className="max-w-3xl text-[1.02rem] leading-8 tracking-[-0.015em] text-slate-500">
          {t("connectionSettingsDescription")}
        </p>
      </motion.div>

      <div className="grid gap-6 xl:grid-cols-[1.15fr_0.85fr]">
        <motion.section
          variants={pageReveal}
          whileHover={reduceMotion ? undefined : { y: -4, boxShadow: "0 24px 60px -32px rgba(15, 23, 42, 0.22)" }}
          className="rounded-3xl border border-white/80 bg-white/55 p-6 shadow-lg backdrop-blur-xl transition-shadow"
        >
          <div className="flex items-center gap-2 text-slate-700">
            <Server className="h-4 w-4 text-blue-500" />
            <span className="text-sm font-semibold tracking-[-0.02em]">{t("editCurrentConnection")}</span>
          </div>

          <div className="mt-5 grid gap-4 md:grid-cols-2">
            <label className="flex flex-col gap-2 md:col-span-2">
              <span className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">
                {t("presetName")}
              </span>
              <input
                value={form.presetName}
                onChange={(event) => updateForm("presetName", event.target.value)}
                placeholder={t("presetNamePlaceholder")}
                className="rounded-2xl border border-slate-200 bg-white/80 px-4 py-3 text-slate-700 shadow-sm outline-none transition focus:border-blue-400 focus:ring-2 focus:ring-blue-500/10"
              />
            </label>

            <label className="flex flex-col gap-2">
              <span className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">
                {t("baseUrl")}
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
                {t("apiKey")}
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
              <div className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">{t("currentState")}</div>
              <div className="mt-3 grid gap-2 text-sm text-slate-600 sm:grid-cols-2">
                <div>{t("loadedModels")}: {models.length}</div>
                <div>{t("defaultImage")}: {bootstrap?.defaultVisionImageUrl ? t("ready") : t("loading")}</div>
                <div>{t("selectedModel")}: {form.model || t("notSelected")}</div>
                <div>{t("activeCodexItem")}: {codexActive?.name || t("notWritten")}</div>
              </div>
            </div>
          </div>

          <div className="mt-5 flex flex-wrap gap-3">
            <motion.button
              onClick={() => void loadModels()}
              disabled={loading.models || loading.bootstrap}
              className="inline-flex items-center gap-2 rounded-2xl bg-slate-900 px-4 py-3 text-sm font-semibold text-white shadow-lg shadow-slate-900/15 transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-60"
              whileHover={reduceMotion ? undefined : { y: -2, scale: 1.01 }}
              whileTap={reduceMotion ? undefined : { scale: 0.985 }}
            >
              {loading.models ? <Loader2 className="h-4 w-4 animate-spin" /> : <Sparkles className="h-4 w-4" />}
              {t("testConnectionAndLoadModels")}
            </motion.button>
            <motion.button
              onClick={() => void saveCodexPreset()}
              disabled={loading.codexSave}
              className="inline-flex items-center gap-2 rounded-2xl border border-slate-200 bg-white/80 px-4 py-3 text-sm font-semibold text-slate-700 shadow-sm transition hover:bg-white disabled:cursor-not-allowed disabled:opacity-60"
              whileHover={reduceMotion ? undefined : { y: -2, scale: 1.01 }}
              whileTap={reduceMotion ? undefined : { scale: 0.985 }}
            >
              {loading.codexSave ? <Loader2 className="h-4 w-4 animate-spin" /> : <Save className="h-4 w-4" />}
              {t("saveCodexPreset")}
            </motion.button>
            <motion.button
              onClick={() => void applyCodexPreset()}
              disabled={loading.codexApply}
              className="inline-flex items-center gap-2 rounded-2xl bg-blue-600 px-4 py-3 text-sm font-semibold text-white shadow-lg shadow-blue-500/20 transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-60"
              whileHover={reduceMotion ? undefined : { y: -2, scale: 1.01 }}
              whileTap={reduceMotion ? undefined : { scale: 0.985 }}
            >
              {loading.codexApply ? <Loader2 className="h-4 w-4 animate-spin" /> : <UploadCloud className="h-4 w-4" />}
              {t("applyToCodex")}
            </motion.button>
          </div>
        </motion.section>

        <motion.section
          variants={pageReveal}
          whileHover={reduceMotion ? undefined : { y: -4, boxShadow: "0 24px 60px -32px rgba(15, 23, 42, 0.22)" }}
          className="rounded-3xl border border-white/80 bg-white/55 p-6 shadow-lg backdrop-blur-xl transition-shadow"
        >
          <div className="flex items-center gap-2 text-slate-700">
            <CheckCircle2 className="h-4 w-4 text-emerald-500" />
            <span className="text-sm font-semibold tracking-[-0.02em]">{t("currentActiveCodexConfig")}</span>
          </div>

          <div className="mt-5 rounded-3xl border border-slate-200 bg-white/80 p-5 shadow-sm">
            <div className="text-xl font-semibold text-slate-800">{codexActive?.name || t("notActive")}</div>
            <div className="mt-2 text-sm text-slate-500">{codexActive?.baseUrl || t("noConfigWrittenYet")}</div>
            <div className="mt-4 space-y-2 text-xs leading-6 text-slate-500">
              <div>provider_id: {codexActive?.providerId || "-"}</div>
              <div>config.toml: {codexActive?.configPath || "-"}</div>
              <div>auth.json: {codexActive?.authPath || "-"}</div>
            </div>
          </div>

          <div className="mt-5 rounded-3xl border border-blue-100 bg-gradient-to-br from-blue-50 via-white to-cyan-50 p-5 text-sm leading-7 text-slate-600">
            {bootstrap?.subtitle || t("bootstrapLoading")}
          </div>
        </motion.section>
      </div>

      <motion.section
        variants={pageReveal}
        whileHover={reduceMotion ? undefined : { y: -4, boxShadow: "0 24px 60px -32px rgba(15, 23, 42, 0.22)" }}
        className="rounded-3xl border border-white/80 bg-white/55 p-6 shadow-lg backdrop-blur-xl transition-shadow"
      >
        <div className="flex items-center justify-between gap-4">
          <div>
            <p className="text-sm uppercase tracking-[0.22em] text-slate-400">{t("savedPresets")}</p>
            <h2 className="[font-family:var(--font-display)] mt-2 text-2xl font-semibold tracking-[-0.04em] text-slate-800">{t("savedCodexPresets")}</h2>
          </div>
          <div className="rounded-full border border-slate-200 bg-white/80 px-3 py-1 text-xs font-semibold text-slate-500">
            {t("total")} {codexPresets.length}
          </div>
        </div>

        {codexPresets.length ? (
          <div className="mt-5 grid gap-4 md:grid-cols-2 xl:grid-cols-3">
            {codexPresets.map((preset) => {
              const isCurrent = preset.name === form.presetName;
              const isActive = preset.name === codexActive?.name;

              return (
                <motion.article
                  key={preset.providerId || preset.name}
                  className={`rounded-3xl border p-5 shadow-sm transition ${
                    isCurrent
                      ? "border-blue-200 bg-blue-50/80"
                      : "border-slate-200 bg-white/85"
                  }`}
                  whileHover={reduceMotion ? undefined : { y: -4, scale: 1.01 }}
                  transition={{ type: "spring", stiffness: 240, damping: 20 }}
                >
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <div className="text-lg font-semibold text-slate-800">{preset.name}</div>
                      <div className="mt-1 break-all text-sm text-slate-500">{preset.baseUrl}</div>
                    </div>
                    {isActive ? (
                      <span className="rounded-full bg-emerald-100 px-2.5 py-1 text-xs font-semibold text-emerald-700">
                        {t("active")}
                      </span>
                    ) : null}
                  </div>

                  <div className="mt-4 rounded-2xl bg-slate-50 px-4 py-3 text-xs leading-6 text-slate-500">
                    provider_id: {preset.providerId || "-"}
                    <br />
                    apikey: {preset.apiKey ? t("apiKeySaved") : t("apiKeyMissing")}
                  </div>

                  <div className="mt-4 flex flex-wrap gap-2">
                    <motion.button
                      onClick={() => applyPresetToForm(preset.name)}
                      className="rounded-2xl border border-slate-200 bg-white px-3 py-2 text-sm font-semibold text-slate-700 transition hover:bg-slate-50"
                      whileHover={reduceMotion ? undefined : { y: -1 }}
                      whileTap={reduceMotion ? undefined : { scale: 0.985 }}
                    >
                      {isCurrent ? t("loaded") : t("loadIntoForm")}
                    </motion.button>
                    <motion.button
                      onClick={() => void applySavedPresetToCodex(preset.name)}
                      disabled={loading.codexApply}
                      className="rounded-2xl bg-slate-900 px-3 py-2 text-sm font-semibold text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-60"
                      whileHover={reduceMotion ? undefined : { y: -1 }}
                      whileTap={reduceMotion ? undefined : { scale: 0.985 }}
                    >
                      {t("loadAndApply")}
                    </motion.button>
                  </div>
                </motion.article>
              );
            })}
          </div>
        ) : (
          <div className="mt-5 rounded-3xl border border-dashed border-slate-200 bg-white/70 px-6 py-10 text-center text-sm leading-7 text-slate-500">
            {t("noPresetsSavedYet")}
          </div>
        )}
      </motion.section>
    </motion.div>
  );
}
