import { AlertCircle, Bot, Image as ImageIcon, Layers3, Loader2, RefreshCcw, Sparkles, Trash2 } from "lucide-react";
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
  const { t } = useLocale();
  const reduceMotion = useReducedMotion();

  return (
    <motion.div
      className="h-full flex flex-col max-w-6xl mx-auto w-full gap-6 pb-4"
      initial={reduceMotion ? false : "hidden"}
      animate={reduceMotion ? undefined : "visible"}
      variants={pageReveal}
    >
      <motion.div className="flex flex-col gap-3 shrink-0" variants={pageReveal}>
        <div className="flex items-start justify-between gap-4">
          <div>
            <p className="text-sm uppercase tracking-[0.28em] text-slate-400">{t("testingConsole")}</p>
            <h1 className="[font-family:var(--font-display)] text-3xl font-bold tracking-[-0.05em] text-slate-800 md:text-[2.8rem]">
              {t("apiWebTester")}
            </h1>
            <p className="mt-2 text-[1.02rem] leading-8 tracking-[-0.015em] text-slate-500">
              {t("apiWebTesterSubtitle")}
            </p>
          </div>
          <motion.button
            onClick={clearResult}
            disabled={!result}
            className="inline-flex items-center gap-2 rounded-2xl border border-slate-200 bg-white/70 px-4 py-2.5 text-sm font-medium text-slate-600 shadow-sm transition hover:bg-white disabled:cursor-not-allowed disabled:opacity-50"
            whileHover={reduceMotion ? undefined : { scale: 1.02 }}
            whileTap={reduceMotion ? undefined : { scale: 0.985 }}
          >
            <Trash2 className="h-4 w-4" />
            {t("clearResult")}
          </motion.button>
        </div>

        <div className="grid gap-4 lg:grid-cols-[1.35fr_0.95fr]">
          <motion.section
            variants={pageReveal}
            className={`${panelClass} p-5`}
          >
            <div className="flex items-center gap-2 text-slate-700">
              <Layers3 className="h-4 w-4 text-blue-500" />
              <span className="text-base font-semibold tracking-[-0.02em]">{t("currentConnection")}</span>
            </div>
            <div className="mt-4 grid gap-4 md:grid-cols-2">
              <label className="flex flex-col gap-2">
                <span className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">
                  {t("baseUrl")}
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
                  {t("apiKey")}
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
                  {t("model")}
                </span>
                <select
                  value={form.model}
                  onChange={(event) => updateForm("model", event.target.value)}
                  className="rounded-2xl border border-slate-200 bg-white/80 px-4 py-3 text-slate-700 shadow-sm outline-none transition focus:border-blue-400 focus:ring-2 focus:ring-blue-500/10"
                >
                  <option value="">{t("autoSelectOnRequest")}</option>
                  {models.map((item) => (
                    <option key={item.id} value={item.id}>
                      {item.id}
                    </option>
                  ))}
                </select>
              </label>
              <div className="flex flex-col justify-end gap-2">
                <motion.button
                  onClick={() => void loadModels()}
                  disabled={loading.models || loading.bootstrap}
                  className="inline-flex items-center justify-center gap-2 rounded-2xl bg-slate-900 px-4 py-3 text-sm font-semibold text-white shadow-lg shadow-slate-900/15 transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-60"
                  whileHover={reduceMotion ? undefined : { scale: 1.02 }}
                  whileTap={reduceMotion ? undefined : { scale: 0.985 }}
                >
                  {loading.models ? <Loader2 className="h-4 w-4 animate-spin" /> : <RefreshCcw className="h-4 w-4" />}
                  {t("loadModelList")}
                </motion.button>
                <p className="text-xs text-slate-400">
                  {t("phaseOneHint")}
                </p>
              </div>
            </div>
          </motion.section>

          <motion.section
            variants={pageReveal}
            className="rounded-3xl border border-white/60 bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 p-5 text-slate-100 shadow-lg transition-shadow"
          >
            <p className="text-xs uppercase tracking-[0.24em] text-slate-400">{t("codexActive")}</p>
            <div className="mt-4 space-y-3">
              <div>
                <div className="text-lg font-semibold">{codexActive?.name || t("notActive")}</div>
                <div className="text-sm text-slate-400">
                  {codexActive?.baseUrl || t("currentFormNotWritten")}
                </div>
              </div>
              <div className="rounded-2xl border border-white/10 bg-white/5 p-4 text-sm text-slate-300">
                <div>{t("configFile")}: {codexActive?.configPath || "-"}</div>
                <div className="mt-1">{t("authFile")}: {codexActive?.authPath || "-"}</div>
              </div>
            </div>
          </motion.section>
        </div>
      </motion.div>

      {errorMessage ? (
        <motion.div
          variants={pageReveal}
          className="flex items-start justify-between gap-3 rounded-2xl border border-amber-200 bg-amber-50 px-4 py-3 text-amber-800 shadow-sm"
        >
          <div className="flex items-start gap-3">
            <AlertCircle className="mt-0.5 h-5 w-5 shrink-0" />
            <p className="whitespace-pre-wrap text-sm leading-6">{errorMessage}</p>
          </div>
          <motion.button
            onClick={clearError}
            className="rounded-full px-2 py-1 text-xs font-semibold text-amber-700 transition hover:bg-amber-100"
            whileHover={reduceMotion ? undefined : { scale: 1.02 }}
            whileTap={reduceMotion ? undefined : { scale: 0.98 }}
          >
            {t("close")}
          </motion.button>
        </motion.div>
      ) : null}

      <div className="grid items-start gap-6 xl:grid-cols-[1.05fr_0.95fr]">
        <div className="grid content-start gap-6 self-start">
          <motion.section
            variants={pageReveal}
            className={`${panelClass} p-6`}
          >
            <div className="flex items-start justify-between gap-4">
              <div>
                <p className="text-sm uppercase tracking-[0.22em] text-slate-400">{t("defaultText")}</p>
                <h2 className="[font-family:var(--font-display)] mt-2 text-[1.35rem] font-semibold tracking-[-0.04em] text-slate-800 md:text-[1.75rem]">{t("verifyTextEndpoint")}</h2>
              </div>
              <motion.button
                onClick={() => void sendDefaultRequest("text")}
                disabled={loading.text || loading.bootstrap}
                className="inline-flex items-center gap-2 rounded-2xl bg-blue-600 px-4 py-3 text-sm font-semibold text-white shadow-lg shadow-blue-500/20 transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-60"
                whileHover={reduceMotion ? undefined : { scale: 1.02 }}
                whileTap={reduceMotion ? undefined : { scale: 0.985 }}
              >
                {loading.text ? <Loader2 className="h-4 w-4 animate-spin" /> : <Sparkles className="h-4 w-4" />}
                {t("sendDefaultText")}
              </motion.button>
            </div>
            <div className="mt-5 rounded-3xl border border-blue-100 bg-gradient-to-br from-blue-50 via-white to-cyan-50 p-5 text-sm leading-7 text-slate-700">
              {bootstrap?.defaultTextPrompt || t("loadingDefaultTextPrompt")}
            </div>
          </motion.section>

          <motion.section
            variants={pageReveal}
            className={`${panelClass} p-6`}
          >
            <div className="flex items-start justify-between gap-4">
              <div>
                <p className="text-sm uppercase tracking-[0.22em] text-slate-400">{t("defaultVision")}</p>
                <h2 className="[font-family:var(--font-display)] mt-2 text-[1.35rem] font-semibold tracking-[-0.04em] text-slate-800 md:text-[1.75rem]">{t("verifyVisionEndpoint")}</h2>
              </div>
              <motion.button
                onClick={() => void sendDefaultRequest("vision")}
                disabled={loading.vision || loading.bootstrap}
                className="inline-flex items-center gap-2 rounded-2xl bg-slate-900 px-4 py-3 text-sm font-semibold text-white shadow-lg shadow-slate-900/15 transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-60"
                whileHover={reduceMotion ? undefined : { scale: 1.02 }}
                whileTap={reduceMotion ? undefined : { scale: 0.985 }}
              >
                {loading.vision ? <Loader2 className="h-4 w-4 animate-spin" /> : <ImageIcon className="h-4 w-4" />}
                {t("sendDefaultImage")}
              </motion.button>
            </div>
            <div className="mt-5 grid gap-5 lg:grid-cols-[240px_1fr]">
              <div className="overflow-hidden rounded-3xl border border-slate-200 bg-white shadow-sm">
                {bootstrap?.defaultVisionImageUrl ? (
                  <img
                    src={bootstrap.defaultVisionImageUrl}
                    alt={t("defaultTestImage")}
                    className="h-full min-h-[220px] w-full object-cover"
                  />
                ) : (
                  <div className="flex min-h-[220px] items-center justify-center bg-slate-100 text-sm text-slate-400">
                    {t("loadingImage")}
                  </div>
                )}
              </div>
              <div className="rounded-3xl border border-slate-200 bg-white/80 p-5 text-sm leading-7 text-slate-700 shadow-sm">
                <div>{bootstrap?.defaultVisionPrompt || t("loadingDefaultVisionPrompt")}</div>
                <div className="mt-4 rounded-2xl bg-slate-50 px-4 py-3 text-xs leading-6 text-slate-500">
                  {t("visionHint")}
                </div>
              </div>
            </div>
          </motion.section>
        </div>

        <motion.section
          variants={pageReveal}
          className={`${panelClass} self-start p-6`}
        >
          <div className="flex items-start justify-between gap-4">
            <div>
              <p className="text-sm uppercase tracking-[0.22em] text-slate-400">{t("latestResult")}</p>
              <h2 className="[font-family:var(--font-display)] mt-2 text-[1.35rem] font-semibold tracking-[-0.04em] text-slate-800 md:text-[1.75rem]">{t("mostRecentResponse")}</h2>
            </div>
            <div className="rounded-full border border-slate-200 bg-white/70 px-3 py-1 text-xs font-semibold text-slate-500">
              {result ? (result.kind === "vision" ? t("vision") : t("text")) : t("idle")}
            </div>
          </div>

          {result ? (
            <div className="mt-5 space-y-5">
              <div className="grid gap-3 sm:grid-cols-3">
                <ResultStat label={t("model")} value={result.model || "-"} />
                <ResultStat label={t("elapsed")} value={`${result.elapsedSeconds || 0}s`} />
                <ResultStat label={t("totalTokens")} value={String(result.usage.totalTokens || 0)} />
              </div>

              <div className="rounded-3xl border border-slate-200 bg-white/90 p-5 shadow-sm">
                <div className="flex items-center gap-2 text-sm font-semibold text-slate-600">
                  <Bot className="h-4 w-4 text-blue-500" />
                  {t("response")}
                </div>
                <div className="mt-3 whitespace-pre-wrap text-sm leading-7 text-slate-700">
                  {result.responseText || t("noTextContent")}
                </div>
              </div>

              <div className="rounded-3xl border border-slate-200 bg-slate-950 p-4 text-xs leading-6 text-slate-200 shadow-sm">
                <div className="mb-2 font-semibold text-slate-400">{t("rawPayload")}</div>
                <pre className="overflow-x-auto whitespace-pre-wrap break-all">
                  {JSON.stringify(result.raw, null, 2)}
                </pre>
              </div>
            </div>
          ) : (
            <div className="mt-5 flex min-h-[420px] flex-col items-center justify-center rounded-3xl border border-dashed border-slate-200 bg-white/50 px-8 text-center text-slate-400">
              <Bot className="h-12 w-12 opacity-60" />
              <p className="mt-4 text-base font-medium text-slate-500">
                {t("emptyStateTitle")}
              </p>
              <p className="mt-2 text-sm leading-6">
                {t("emptyStateDescription")}
              </p>
            </div>
          )}
        </motion.section>
      </div>
    </motion.div>
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
