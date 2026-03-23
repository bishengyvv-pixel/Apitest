import { motion, useReducedMotion } from "motion/react";
import { useState } from "react";
import { Link, Outlet, useLocation } from "react-router";
import { Settings, MessageSquare, ChevronRight, ChevronLeft, Languages, Zap } from "lucide-react";
import { useLocale } from "../context/LocaleContext";

export function Layout() {
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const location = useLocation();
  const { locale, toggleLocale, t } = useLocale();
  const reduceMotion = useReducedMotion();

  const navItems = [
    { name: t("navTesting"), path: "/", icon: <MessageSquare className="h-5 w-5" /> },
    { name: t("navConnection"), path: "/presets", icon: <Settings className="h-5 w-5" /> },
  ];

  return (
    <div className="relative min-h-screen w-full overflow-hidden bg-slate-50 text-slate-800 font-sans">
      <motion.button
        type="button"
        onClick={toggleLocale}
        title={t("switchLanguage")}
        aria-label={t("switchLanguage")}
        className="absolute left-4 top-4 z-30 inline-flex items-center gap-2 rounded-2xl border border-white/70 bg-white/80 px-3 py-2 text-sm font-semibold tracking-[-0.02em] text-slate-700 shadow-lg backdrop-blur-xl md:left-6 md:top-6"
        initial={reduceMotion ? false : { opacity: 0, y: -14 }}
        animate={reduceMotion ? undefined : { opacity: 1, y: 0 }}
        transition={{ duration: 0.45, ease: "easeOut" }}
        whileHover={reduceMotion ? undefined : { y: -2, scale: 1.02 }}
        whileTap={reduceMotion ? undefined : { scale: 0.98 }}
      >
        <Languages className="h-4 w-4 text-blue-500" />
        <span>{locale === "en" ? "EN" : "ZH"}</span>
      </motion.button>

      <div className="pointer-events-none absolute inset-0 z-0 overflow-hidden">
        <motion.div
          animate={
            reduceMotion
              ? undefined
              : {
                  x: ["0%", "50%", "-20%", "0%"],
                  y: ["0%", "-30%", "20%", "0%"],
                }
          }
          transition={{ duration: 25, repeat: Infinity, ease: "linear" }}
          className="absolute -left-[10%] -top-[30%] h-[70vw] w-[70vw] rounded-full bg-blue-100/40 opacity-70 blur-3xl mix-blend-multiply"
        />
        <motion.div
          animate={
            reduceMotion
              ? undefined
              : {
                  x: ["0%", "-50%", "30%", "0%"],
                  y: ["0%", "40%", "-10%", "0%"],
                }
          }
          transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
          className="absolute right-[0%] top-[20%] h-[60vw] w-[60vw] rounded-full bg-amber-100/40 opacity-70 blur-3xl mix-blend-multiply"
        />
        <motion.div
          animate={
            reduceMotion
              ? undefined
              : {
                  x: ["0%", "18%", "-12%", "0%"],
                  y: ["0%", "14%", "-8%", "0%"],
                }
          }
          transition={{ duration: 18, repeat: Infinity, ease: "easeInOut" }}
          className="absolute left-[28%] top-[8%] h-[26vw] w-[26vw] rounded-full bg-cyan-100/30 opacity-60 blur-3xl"
        />
      </div>

      <div className="relative z-10 flex min-h-screen w-full overflow-hidden">
        <main className="relative flex h-screen flex-1 flex-col overflow-hidden">
          <motion.div
            className="flex-1 overflow-y-auto p-6 md:p-10 [scrollbar-width:none] [&::-webkit-scrollbar]:hidden"
            initial={reduceMotion ? false : { opacity: 0, y: 18 }}
            animate={reduceMotion ? undefined : { opacity: 1, y: 0 }}
            transition={{ duration: 0.55, ease: "easeOut" }}
          >
            <Outlet />
          </motion.div>
        </main>

        <motion.aside
          initial={{ width: 280 }}
          animate={{ width: isSidebarOpen ? 280 : 80 }}
          transition={{ type: "spring", stiffness: 300, damping: 30 }}
          className="relative z-20 flex h-screen flex-col border-l border-white/80 bg-white/60 shadow-[-10px_0_30px_-15px_rgba(0,0,0,0.05)] backdrop-blur-xl"
        >
          <div className="flex items-center justify-between border-b border-slate-200/50 p-4">
            <motion.div
              initial={reduceMotion ? false : { opacity: 0, x: 12 }}
              animate={{
                opacity: isSidebarOpen ? 1 : 0,
                width: isSidebarOpen ? "auto" : 0,
                x: reduceMotion ? 0 : isSidebarOpen ? 0 : 8,
              }}
              transition={{ duration: 0.35, ease: "easeOut" }}
              className="flex items-center gap-2 overflow-hidden whitespace-nowrap"
            >
              <motion.div
                className="flex h-8 w-8 items-center justify-center rounded-xl bg-gradient-to-tr from-blue-500 to-indigo-400 shadow-inner"
                animate={reduceMotion ? undefined : { rotate: [0, -7, 0, 7, 0] }}
                transition={{ duration: 8, repeat: Infinity, ease: "easeInOut" }}
              >
                <Zap className="h-4 w-4 text-white" />
              </motion.div>
              <span className="[font-family:var(--font-display)] text-[1.45rem] font-semibold tracking-[-0.05em] text-slate-800">
                {t("appName")}
              </span>
            </motion.div>

            <motion.button
              type="button"
              onClick={() => setIsSidebarOpen(!isSidebarOpen)}
              className="rounded-xl border border-white/50 bg-white/40 p-2 text-slate-500 shadow-sm transition-colors hover:bg-white/60"
              whileHover={reduceMotion ? undefined : { scale: 1.06 }}
              whileTap={reduceMotion ? undefined : { scale: 0.95 }}
            >
              {isSidebarOpen ? <ChevronRight className="h-4 w-4" /> : <ChevronLeft className="h-4 w-4" />}
            </motion.button>
          </div>

          <nav className="flex-1 space-y-2 overflow-y-auto px-3 py-6">
            {navItems.map((item, index) => {
              const isActive = location.pathname === item.path;

              return (
                <motion.div
                  key={item.path}
                  initial={reduceMotion ? false : { opacity: 0, x: 18 }}
                  animate={reduceMotion ? undefined : { opacity: 1, x: 0 }}
                  transition={{ duration: 0.35, delay: 0.06 * index, ease: "easeOut" }}
                >
                  <Link
                    to={item.path}
                    className={`group relative flex items-center gap-3 overflow-hidden rounded-2xl px-4 py-3 transition-all duration-300 ${
                      isActive
                        ? "border border-white bg-white/80 text-blue-600 shadow-sm"
                        : "text-slate-500 hover:bg-white/50 hover:text-slate-800"
                    }`}
                  >
                    {isActive ? (
                      <motion.div
                        layoutId="sidebar-active-indicator"
                        className="absolute inset-0 z-0 bg-linear-to-r from-blue-50/80 via-white/70 to-cyan-50/70"
                        transition={{ type: "spring", stiffness: 300, damping: 30 }}
                      />
                    ) : null}

                    <motion.div
                      className="relative z-10 flex items-center justify-center"
                      whileHover={reduceMotion ? undefined : { x: 2, scale: 1.08 }}
                      transition={{ type: "spring", stiffness: 260, damping: 20 }}
                    >
                      {item.icon}
                    </motion.div>

                    <motion.span
                      initial={false}
                      animate={{
                        opacity: isSidebarOpen ? 1 : 0,
                        width: isSidebarOpen ? "auto" : 0,
                        x: reduceMotion ? 0 : isSidebarOpen ? 0 : -4,
                      }}
                      transition={{ duration: 0.28, ease: "easeOut" }}
                      className="relative z-10 overflow-hidden whitespace-nowrap font-medium tracking-[-0.02em]"
                    >
                      {item.name}
                    </motion.span>

                    <motion.div
                      className="absolute inset-y-2 right-2 z-10 hidden w-1 rounded-full bg-blue-400/45 group-hover:block"
                      initial={false}
                      animate={isActive && !reduceMotion ? { opacity: [0.35, 0.8, 0.35] } : { opacity: isActive ? 0.55 : 0 }}
                      transition={{ duration: 2.2, repeat: Infinity, ease: "easeInOut" }}
                    />
                  </Link>
                </motion.div>
              );
            })}
          </nav>
        </motion.aside>
      </div>
    </div>
  );
}
