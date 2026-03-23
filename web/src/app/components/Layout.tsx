import { motion } from "motion/react";
import { useState } from "react";
import { Link, Outlet, useLocation } from "react-router";
import { Settings, MessageSquare, ChevronRight, ChevronLeft, Zap } from "lucide-react";

export function Layout() {
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const location = useLocation();

  const navItems = [
    { name: "Testing", path: "/", icon: <MessageSquare className="w-5 h-5" /> },
    { name: "Connection", path: "/presets", icon: <Settings className="w-5 h-5" /> },
  ];

  return (
    <div className="relative min-h-screen w-full flex overflow-hidden bg-slate-50 text-slate-800 font-sans">
      <div className="absolute inset-0 z-0 overflow-hidden pointer-events-none">
        <motion.div
          animate={{
            x: ["0%", "50%", "-20%", "0%"],
            y: ["0%", "-30%", "20%", "0%"],
          }}
          transition={{ duration: 25, repeat: Infinity, ease: "linear" }}
          className="absolute -top-[30%] -left-[10%] w-[70vw] h-[70vw] rounded-full bg-blue-100/40 mix-blend-multiply filter blur-3xl opacity-70"
        />
        <motion.div
          animate={{
            x: ["0%", "-50%", "30%", "0%"],
            y: ["0%", "40%", "-10%", "0%"],
          }}
          transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
          className="absolute top-[20%] right-[0%] w-[60vw] h-[60vw] rounded-full bg-amber-100/40 mix-blend-multiply filter blur-3xl opacity-70"
        />
      </div>

      <main className="relative z-10 flex-1 flex flex-col h-screen overflow-hidden">
        <div className="flex-1 overflow-y-auto p-6 md:p-10 [scrollbar-width:none] [&::-webkit-scrollbar]:hidden">
          <Outlet />
        </div>
      </main>

      <motion.aside
        initial={{ width: 280 }}
        animate={{ width: isSidebarOpen ? 280 : 80 }}
        transition={{ type: "spring", stiffness: 300, damping: 30 }}
        className="relative z-20 h-screen bg-white/60 backdrop-blur-xl border-l border-white/80 shadow-[-10px_0_30px_-15px_rgba(0,0,0,0.05)] flex flex-col"
      >
        <div className="flex items-center justify-between p-4 border-b border-slate-200/50">
          <motion.div
            initial={false}
            animate={{ opacity: isSidebarOpen ? 1 : 0, width: isSidebarOpen ? "auto" : 0 }}
            className="flex items-center gap-2 overflow-hidden whitespace-nowrap"
          >
            <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-blue-500 to-indigo-400 flex items-center justify-center shadow-inner">
              <Zap className="w-4 h-4 text-white" />
            </div>
            <span className="font-semibold text-slate-800 tracking-wide">AI Tester</span>
          </motion.div>
          <button
            onClick={() => setIsSidebarOpen(!isSidebarOpen)}
            className="p-2 rounded-xl hover:bg-white/60 text-slate-500 transition-colors shadow-sm bg-white/40 border border-white/50"
          >
            {isSidebarOpen ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
          </button>
        </div>

        <nav className="flex-1 px-3 py-6 space-y-2 overflow-y-auto">
          {navItems.map((item) => {
            const isActive = location.pathname === item.path;
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`flex items-center gap-3 px-4 py-3 rounded-2xl transition-all duration-300 relative overflow-hidden group ${
                  isActive
                    ? "text-blue-600 bg-white/80 shadow-sm border border-white"
                    : "text-slate-500 hover:bg-white/50 hover:text-slate-800"
                }`}
              >
                {isActive && (
                  <motion.div
                    layoutId="sidebar-active-indicator"
                    className="absolute inset-0 bg-blue-50/50 z-0"
                    initial={false}
                    transition={{ type: "spring", stiffness: 300, damping: 30 }}
                  />
                )}
                <div className="relative z-10 flex items-center justify-center">{item.icon}</div>
                <motion.span
                  initial={false}
                  animate={{ opacity: isSidebarOpen ? 1 : 0, width: isSidebarOpen ? "auto" : 0 }}
                  className="relative z-10 font-medium whitespace-nowrap overflow-hidden"
                >
                  {item.name}
                </motion.span>
              </Link>
            );
          })}
        </nav>
      </motion.aside>
    </div>
  );
}
