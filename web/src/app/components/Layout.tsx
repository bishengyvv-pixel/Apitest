import { motion, useReducedMotion } from "motion/react";
import { useState } from "react";
import { Link, Outlet, useLocation } from "react-router";
import { Settings, MessageSquare, ChevronRight, Languages, Zap } from "lucide-react";
import { useLocale } from "../context/LocaleContext";

export function Layout() {
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [navRipple, setNavRipple] = useState<{ key: number; path: string; x: number; y: number } | null>(null);
  const location = useLocation();
  const { locale, toggleLocale, t } = useLocale();
  const reduceMotion = useReducedMotion();

  const navItems = [
    { name: t("navTesting"), path: "/", icon: <MessageSquare className="h-5 w-5" /> },
    { name: t("navConnection"), path: "/presets", icon: <Settings className="h-5 w-5" /> },
  ];

  const triggerNavRipple = (path: string, element: HTMLElement, clientX?: number, clientY?: number) => {
    if (reduceMotion) {
      return;
    }

    const rect = element.getBoundingClientRect();
    const isKeyboardTrigger = clientX === undefined || clientY === undefined || (clientX === 0 && clientY === 0);

    setNavRipple({
      key: Date.now(),
      path,
      x: isKeyboardTrigger ? rect.width / 2 : clientX - rect.left,
      y: isKeyboardTrigger ? rect.height / 2 : clientY - rect.top,
    });
  };

  return (
    <div className="relative min-h-screen w-full overflow-hidden bg-slate-50 text-slate-800 font-sans">
      <div className="pointer-events-none absolute inset-0 z-0 overflow-hidden">
        <div className="absolute inset-0 bg-[linear-gradient(180deg,rgba(255,255,255,0.86)_0%,rgba(248,250,252,0.94)_52%,rgba(255,255,255,1)_100%)]" />
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_14%_16%,rgba(191,219,254,0.34),transparent_28%),radial-gradient(circle_at_86%_18%,rgba(207,250,254,0.26),transparent_24%),radial-gradient(circle_at_52%_82%,rgba(254,243,199,0.18),transparent_26%)]" />
        <div className="absolute inset-0 opacity-[0.45] [background-image:linear-gradient(rgba(255,255,255,0.36)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.3)_1px,transparent_1px)] [background-size:48px_48px]" />
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
          className="relative z-20 flex h-screen flex-col overflow-hidden border-l border-white/80 bg-white/86 shadow-[-10px_0_30px_-15px_rgba(0,0,0,0.05)]"
        >
          <div
            className={`grid grid-cols-[minmax(0,1fr)_auto] items-center overflow-hidden border-b border-slate-200/50 transition-[padding,gap] duration-300 ${
              isSidebarOpen ? "gap-3 p-4" : "gap-0 px-2 py-3"
            }`}
          >
            <div
              className={`flex min-w-0 items-center overflow-hidden transition-[gap] duration-300 ${
                isSidebarOpen ? "gap-2" : "gap-0"
              }`}
            >
              <motion.div
                className="flex h-8 w-8 shrink-0 items-center justify-center rounded-xl bg-gradient-to-tr from-blue-500 to-indigo-400 shadow-inner"
                animate={
                  reduceMotion
                    ? undefined
                    : {
                        rotate: isSidebarOpen ? [0, -7, 0, 7, 0] : 0,
                        opacity: isSidebarOpen ? 1 : 0,
                        scale: isSidebarOpen ? 1 : 0.82,
                        width: isSidebarOpen ? 32 : 0,
                        marginRight: isSidebarOpen ? 0 : -8,
                      }
                }
                transition={{ duration: 0.3, ease: "easeOut", rotate: { duration: 8, repeat: Infinity, ease: "easeInOut" } }}
              >
                <Zap className="h-4 w-4 text-white" />
              </motion.div>

              <motion.span
                initial={false}
                animate={{
                  opacity: isSidebarOpen ? 1 : 0,
                  maxWidth: isSidebarOpen ? 160 : 0,
                  x: reduceMotion ? 0 : isSidebarOpen ? 0 : 6,
                }}
                transition={{ duration: 0.28, ease: "easeOut" }}
                className="min-w-0 overflow-hidden whitespace-nowrap [font-family:var(--font-display)] text-[1.45rem] font-semibold tracking-[-0.05em] text-slate-800"
              >
                {t("appName")}
              </motion.span>
            </div>

            <div className={`flex items-center justify-end ${isSidebarOpen ? "gap-2" : "gap-1.5"}`}>
              <motion.button
                type="button"
                onClick={toggleLocale}
                title={t("switchLanguage")}
                aria-label={t("switchLanguage")}
                className={`inline-flex shrink-0 items-center justify-center rounded-xl border border-slate-200/70 bg-slate-50/90 font-semibold tracking-[-0.02em] text-slate-600 shadow-sm transition-colors hover:bg-white ${
                  isSidebarOpen ? "h-9 px-2.5 text-xs" : "h-7 w-7 text-[10px]"
                }`}
                whileHover={reduceMotion ? undefined : { scale: 1.04 }}
                whileTap={reduceMotion ? undefined : { scale: 0.95 }}
              >
                <Languages className={`${isSidebarOpen ? "h-3.5 w-3.5" : "h-3 w-3"}`} />
                <motion.span
                  initial={false}
                  animate={{
                    opacity: isSidebarOpen ? 1 : 0,
                    maxWidth: isSidebarOpen ? 32 : 0,
                    marginLeft: isSidebarOpen ? 6 : 0,
                  }}
                  transition={{ duration: 0.2, ease: "easeOut" }}
                  className="overflow-hidden whitespace-nowrap"
                >
                  {locale === "en" ? "EN" : "ZH"}
                </motion.span>
              </motion.button>

              <motion.button
                type="button"
                onClick={() => setIsSidebarOpen(!isSidebarOpen)}
                aria-label={isSidebarOpen ? t("collapseSidebar") : t("expandSidebar")}
                className={`flex shrink-0 items-center justify-center rounded-xl border border-slate-200/70 bg-slate-50/90 text-slate-500 shadow-sm transition-colors hover:bg-white ${
                  isSidebarOpen ? "h-9 w-9" : "h-7 w-7"
                }`}
                whileHover={reduceMotion ? undefined : { scale: 1.04 }}
                whileTap={reduceMotion ? undefined : { scale: 0.95 }}
              >
                <motion.div
                  initial={false}
                  animate={{ rotate: isSidebarOpen ? 0 : 180 }}
                  transition={{ duration: 0.24, ease: "easeOut" }}
                >
                  <ChevronRight className={`${isSidebarOpen ? "h-4 w-4" : "h-3.5 w-3.5"}`} />
                </motion.div>
              </motion.button>
            </div>
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
                    onClick={(event) =>
                      triggerNavRipple(item.path, event.currentTarget, event.clientX, event.clientY)
                    }
                    className={`group relative flex items-center gap-3 overflow-hidden rounded-2xl px-4 py-3 transition-all duration-300 ${
                      isActive
                        ? "border border-white bg-white/80 text-blue-600 shadow-sm"
                        : "text-slate-500 hover:bg-white/50 hover:text-slate-800"
                    }`}
                  >
                    {navRipple?.path === item.path ? (
                      <>
                        <motion.span
                          key={`ring-a-${navRipple.key}`}
                          className="pointer-events-none absolute z-0 rounded-full border border-blue-300/55"
                          style={{
                            left: navRipple.x,
                            top: navRipple.y,
                            width: 28,
                            height: 28,
                            x: "-50%",
                            y: "-50%",
                          }}
                          initial={{ scale: 0.4, opacity: 0.75 }}
                          animate={{ scale: 3.9, opacity: 0 }}
                          transition={{ duration: 0.72, ease: [0.2, 0.8, 0.2, 1] }}
                        />

                        <motion.span
                          key={`ring-b-${navRipple.key}`}
                          className="pointer-events-none absolute z-0 rounded-full border border-cyan-300/45"
                          style={{
                            left: navRipple.x,
                            top: navRipple.y,
                            width: 20,
                            height: 20,
                            x: "-50%",
                            y: "-50%",
                          }}
                          initial={{ scale: 0.35, opacity: 0.58 }}
                          animate={{ scale: 5.1, opacity: 0 }}
                          transition={{ duration: 0.92, delay: 0.05, ease: [0.2, 0.8, 0.2, 1] }}
                        />
                      </>
                    ) : null}

                    <motion.div
                      className="relative z-10 flex items-center justify-center"
                      whileHover={reduceMotion ? undefined : { scale: 1.05 }}
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
