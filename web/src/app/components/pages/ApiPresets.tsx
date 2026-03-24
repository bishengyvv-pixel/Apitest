import { CheckCircle2, Globe, KeyRound, Loader2, Save, Server, Shield, Sparkles, Trash2, UploadCloud } from "lucide-react";
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

const panelClass =
  "rounded-3xl border border-white/85 bg-[linear-gradient(180deg,rgba(255,255,255,0.95)_0%,rgba(255,255,255,0.88)_100%)] ring-1 ring-white/60 shadow-[0_18px_44px_-30px_rgba(15,23,42,0.14)] transition-shadow";

type RuntimeOption = {
  value: string;
  description: string;
  tone: "emerald" | "slate" | "blue" | "amber";
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
    deleteSavedPreset,
  } = useApi();
  const { t } = useLocale();
  const reduceMotion = useReducedMotion();

  const approvalPolicyOptions: RuntimeOption[] = [
    {
      value: "never",
      description: t("approvalPolicyNeverDescription"),
      tone: "emerald",
    },
    {
      value: "on-request",
      description: t("approvalPolicyOnRequestDescription"),
      tone: "slate",
    },
  ];

  const sandboxModeOptions: RuntimeOption[] = [
    {
      value: "workspace-write",
      description: t("sandboxModeWorkspaceDescription"),
      tone: "blue",
    },
    {
      value: "danger-full-access",
      description: t("sandboxModeDangerDescription"),
      tone: "amber",
    },
  ];

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
        <motion.section variants={pageReveal} className={`${panelClass} p-6`}>
          <div className="flex items-center gap-2 text-slate-700">
            <Server className="h-4 w-4 text-blue-500" />
            <span className="text-base font-semibold tracking-[-0.02em]">{t("editCurrentConnection")}</span>
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
                pattern="[A-Za-z0-9_-]+"
                title="Only English letters, numbers, underscore, and hyphen are allowed."
                className="rounded-2xl border border-slate-200 bg-white/80 px-4 py-3 text-slate-700 shadow-sm outline-none transition focus:border-blue-400 focus:ring-2 focus:ring-blue-500/10"
              />
              <span className="text-xs text-slate-400">Only English letters, numbers, `_`, `-`.</span>
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
              <div className="mt-3 grid gap-2 text-sm text-slate-600 sm:grid-cols-2 xl:grid-cols-3">
                <div>{t("loadedModels")}: {models.length}</div>
                <div>{t("defaultImage")}: {bootstrap?.defaultVisionImageUrl ? t("ready") : t("loading")}</div>
                <div>{t("selectedModel")}: {form.model || t("notSelected")}</div>
                <div>{t("activeCodexItem")}: {codexActive?.name || t("notWritten")}</div>
                <div>{t("approvalPolicy")}: {codexActive?.approvalPolicy || t("notSet")}</div>
                <div>{t("sandboxMode")}: {codexActive?.sandboxMode || t("notSet")}</div>
              </div>
            </div>
          </div>

          <div className="mt-5 flex flex-wrap gap-3">
            <motion.button
              onClick={() => void loadModels()}
              disabled={loading.models || loading.bootstrap}
              className="inline-flex items-center gap-2 rounded-2xl bg-slate-900 px-4 py-3 text-sm font-semibold text-white shadow-lg shadow-slate-900/15 transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-60"
              whileHover={reduceMotion ? undefined : { scale: 1.02 }}
              whileTap={reduceMotion ? undefined : { scale: 0.985 }}
            >
              {loading.models ? <Loader2 className="h-4 w-4 animate-spin" /> : <Sparkles className="h-4 w-4" />}
              {t("testConnectionAndLoadModels")}
            </motion.button>
            <motion.button
              onClick={() => void saveCodexPreset()}
              disabled={loading.codexSave}
              className="inline-flex items-center gap-2 rounded-2xl border border-slate-200 bg-white/80 px-4 py-3 text-sm font-semibold text-slate-700 shadow-sm transition hover:bg-white disabled:cursor-not-allowed disabled:opacity-60"
              whileHover={reduceMotion ? undefined : { scale: 1.02 }}
              whileTap={reduceMotion ? undefined : { scale: 0.985 }}
            >
              {loading.codexSave ? <Loader2 className="h-4 w-4 animate-spin" /> : <Save className="h-4 w-4" />}
              {t("saveCodexPreset")}
            </motion.button>
            <motion.button
              onClick={() => void applyCodexPreset()}
              disabled={loading.codexApply}
              className="inline-flex items-center gap-2 rounded-2xl bg-blue-600 px-4 py-3 text-sm font-semibold text-white shadow-lg shadow-blue-500/20 transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-60"
              whileHover={reduceMotion ? undefined : { scale: 1.02 }}
              whileTap={reduceMotion ? undefined : { scale: 0.985 }}
            >
              {loading.codexApply ? <Loader2 className="h-4 w-4 animate-spin" /> : <UploadCloud className="h-4 w-4" />}
              {t("applyToCodex")}
            </motion.button>
          </div>
        </motion.section>

        <motion.section variants={pageReveal} className={`${panelClass} p-6`}>
          <div className="flex items-center gap-2 text-slate-700">
            <CheckCircle2 className="h-4 w-4 text-emerald-500" />
            <span className="text-base font-semibold tracking-[-0.02em]">{t("currentActiveCodexConfig")}</span>
          </div>

          <div className="mt-5 rounded-3xl border border-slate-200 bg-white/80 p-5 shadow-sm">
            <div className="text-xl font-semibold text-slate-800">{codexActive?.name || t("notActive")}</div>
            <div className="mt-2 text-sm text-slate-500">{codexActive?.baseUrl || t("noConfigWrittenYet")}</div>
            <div className="mt-4 flex flex-wrap gap-2">
              <MetaPill label={t("approvalPolicy")} value={codexActive?.approvalPolicy || t("notSet")} tone={codexActive?.approvalPolicy === "never" ? "emerald" : "slate"} />
              <MetaPill label={t("sandboxMode")} value={codexActive?.sandboxMode || t("notSet")} tone={codexActive?.sandboxMode === "danger-full-access" ? "amber" : "blue"} />
            </div>
            <div className="mt-4 space-y-2 text-xs leading-6 text-slate-500">
              <div>provider_id: {codexActive?.providerId || "-"}</div>
              <div>config.toml: {codexActive?.configPath || "-"}</div>
              <div>auth.json: {codexActive?.authPath || "-"}</div>
            </div>
          </div>

          <div className="mt-5 rounded-3xl border border-blue-100 bg-gradient-to-br from-blue-50 via-white to-cyan-50 p-5 text-sm leading-7 text-slate-600">
            {t("apiWebTesterSubtitle")}
          </div>
        </motion.section>
      </div>

      <motion.section variants={pageReveal} className={`${panelClass} p-6`}>
        <div className="flex items-center gap-2 text-slate-700">
          <Shield className="h-4 w-4 text-slate-700" />
          <span className="text-base font-semibold tracking-[-0.02em]">{t("runtimeSettings")}</span>
        </div>

        <div className="mt-5 rounded-[28px] border border-slate-200/80 bg-[radial-gradient(circle_at_top_left,rgba(59,130,246,0.08),transparent_42%),linear-gradient(180deg,rgba(248,250,252,0.95)_0%,rgba(255,255,255,0.92)_100%)] p-5 shadow-sm">
          <div className="flex flex-col gap-4 xl:flex-row xl:items-start xl:justify-between">
            <div>
              <div className="flex flex-wrap gap-2">
                <MetaPill label={t("approvalPolicy")} value={form.approvalPolicy} tone={form.approvalPolicy === "never" ? "emerald" : "slate"} />
                <MetaPill label={t("sandboxMode")} value={form.sandboxMode} tone={form.sandboxMode === "danger-full-access" ? "amber" : "blue"} />
              </div>
              <p className="mt-4 max-w-3xl text-sm leading-7 text-slate-500">
                {t("runtimeSettingsDescription").split("应用").map((part, index, parts) => (
                  <span key={`${part}-${index}`}>
                    {part}
                    {index < parts.length - 1 ? <strong className="font-semibold text-slate-700">应用</strong> : null}
                  </span>
                ))}
              </p>
            </div>
          </div>

          <div className="mt-5 grid gap-4 xl:grid-cols-[1fr_1fr]">
            <RuntimeChoiceGroup
              label={t("approvalPolicy")}
              value={form.approvalPolicy}
              onSelect={(value) => updateForm("approvalPolicy", value)}
              options={approvalPolicyOptions}
              reduceMotion={reduceMotion}
            />
            <RuntimeChoiceGroup
              label={t("sandboxMode")}
              value={form.sandboxMode}
              onSelect={(value) => updateForm("sandboxMode", value)}
              options={sandboxModeOptions}
              reduceMotion={reduceMotion}
            />
          </div>
        </div>
      </motion.section>

      <motion.section variants={pageReveal} className={`${panelClass} p-6`}>
        <div className="flex items-center justify-between gap-4">
          <div>
            <p className="text-sm uppercase tracking-[0.22em] text-slate-400">{t("savedPresets")}</p>
            <h2 className="[font-family:var(--font-display)] mt-2 text-[1.75rem] font-semibold tracking-[-0.04em] text-slate-800 md:text-[2rem]">{t("savedCodexPresets")}</h2>
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
                  key={`${preset.name}-${preset.providerId || "no-provider"}`}
                  className={`flex h-full flex-col rounded-3xl border p-5 shadow-sm transition ${
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
                    <MetaPill label={t("approvalPolicy")} value={preset.approvalPolicy} tone={preset.approvalPolicy === "never" ? "emerald" : "slate"} />
                    <MetaPill label={t("sandboxMode")} value={preset.sandboxMode} tone={preset.sandboxMode === "danger-full-access" ? "amber" : "blue"} />
                  </div>

                  <div className="mt-4 flex flex-1 items-end justify-between gap-3">
                    <div className="flex flex-wrap gap-2">
                      <motion.button
                        onClick={() => applyPresetToForm(preset.name)}
                        className="rounded-2xl border border-slate-200 bg-white px-3 py-2 text-sm font-semibold text-slate-700 transition hover:bg-slate-50"
                        whileHover={reduceMotion ? undefined : { scale: 1.02 }}
                        whileTap={reduceMotion ? undefined : { scale: 0.985 }}
                      >
                        {isCurrent ? t("loaded") : t("loadIntoForm")}
                      </motion.button>
                      <motion.button
                        onClick={() => void applySavedPresetToCodex(preset.name)}
                        disabled={loading.codexApply}
                        className="rounded-2xl bg-slate-900 px-3 py-2 text-sm font-semibold text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-60"
                        whileHover={reduceMotion ? undefined : { scale: 1.02 }}
                        whileTap={reduceMotion ? undefined : { scale: 0.985 }}
                      >
                        {t("loadAndApply")}
                      </motion.button>
                    </div>

                    <motion.button
                      type="button"
                      title={t("deletePreset")}
                      aria-label={t("deletePreset")}
                      onClick={() => void deleteSavedPreset(preset.name)}
                      disabled={loading.codexDelete}
                      className="inline-flex h-10 w-10 shrink-0 items-center justify-center self-end rounded-2xl border border-transparent bg-transparent text-slate-400 transition hover:border-slate-200 hover:bg-white hover:text-slate-600 disabled:cursor-not-allowed disabled:opacity-60"
                      whileHover={reduceMotion ? undefined : { scale: 1.04 }}
                      whileTap={reduceMotion ? undefined : { scale: 0.96 }}
                    >
                      {loading.codexDelete ? <Loader2 className="h-4 w-4 animate-spin" /> : <Trash2 className="h-4 w-4" />}
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

function RuntimeChoiceGroup({
  label,
  value,
  onSelect,
  options,
  reduceMotion,
}: {
  label: string;
  value: string;
  onSelect: (value: string) => void;
  options: RuntimeOption[];
  reduceMotion: boolean;
}) {
  return (
    <div className="rounded-3xl border border-slate-200/80 bg-white/80 p-4 shadow-sm">
      <div className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">{label}</div>
      <div className="mt-3 space-y-3">
        {options.map((option) => {
          const isSelected = option.value === value;
          return (
            <motion.button
              key={option.value}
              type="button"
              onClick={() => onSelect(option.value)}
              className={buildRuntimeOptionClass(isSelected, option.tone)}
              whileHover={reduceMotion ? undefined : { scale: 1.01 }}
              whileTap={reduceMotion ? undefined : { scale: 0.985 }}
            >
              <div className="flex items-start justify-between gap-3">
                <div>
                  <div className="font-mono text-sm font-semibold text-slate-800">{option.value}</div>
                  <div className="mt-1 text-sm leading-6 text-slate-500">{option.description}</div>
                </div>
                <div
                  className={`mt-0.5 h-3 w-3 rounded-full border ${
                    isSelected ? "border-transparent bg-current" : "border-slate-300 bg-white"
                  } ${buildToneTextClass(option.tone)}`}
                />
              </div>
            </motion.button>
          );
        })}
      </div>
    </div>
  );
}

function MetaPill({
  label,
  value,
  tone = "slate",
}: {
  label: string;
  value: string;
  tone?: "emerald" | "slate" | "blue" | "amber";
}) {
  return (
    <div className={`rounded-full border px-3 py-1.5 text-xs shadow-sm ${buildTonePillClass(tone)}`}>
      <span className="font-semibold uppercase tracking-[0.18em]">{label}</span>
      <span className="mx-2 opacity-40">/</span>
      <span className="font-mono">{value}</span>
    </div>
  );
}

function buildRuntimeOptionClass(isSelected: boolean, tone: RuntimeOption["tone"]) {
  const baseClass = "w-full rounded-[24px] border px-4 py-4 text-left transition";
  const selectedClassMap = {
    emerald: "border-emerald-200 bg-emerald-50/80 shadow-[0_12px_24px_-18px_rgba(16,185,129,0.55)]",
    slate: "border-slate-300 bg-slate-100/90 shadow-[0_12px_24px_-18px_rgba(15,23,42,0.24)]",
    blue: "border-blue-200 bg-blue-50/80 shadow-[0_12px_24px_-18px_rgba(59,130,246,0.45)]",
    amber: "border-amber-200 bg-amber-50/85 shadow-[0_12px_24px_-18px_rgba(245,158,11,0.55)]",
  } as const;

  if (isSelected) {
    return `${baseClass} ${selectedClassMap[tone]}`;
  }

  return `${baseClass} border-slate-200 bg-white hover:border-slate-300 hover:bg-slate-50/80`;
}

function buildToneTextClass(tone: RuntimeOption["tone"]) {
  const textClassMap = {
    emerald: "text-emerald-500",
    slate: "text-slate-500",
    blue: "text-blue-500",
    amber: "text-amber-500",
  } as const;

  return textClassMap[tone];
}

function buildTonePillClass(tone: RuntimeOption["tone"]) {
  const pillClassMap = {
    emerald: "border-emerald-200 bg-emerald-50/80 text-emerald-700",
    slate: "border-slate-200 bg-slate-100/90 text-slate-600",
    blue: "border-blue-200 bg-blue-50/80 text-blue-700",
    amber: "border-amber-200 bg-amber-50/85 text-amber-700",
  } as const;

  return pillClassMap[tone];
}
