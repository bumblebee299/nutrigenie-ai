"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import {
  Leaf,
  Sparkles,
  MessageSquare,
  CalendarDays,
  Camera,
  Tag,
  ArrowLeftRight,
  BarChart2,
} from "lucide-react";

interface FloatingCardProps {
  children: React.ReactNode;
  delay?: number;
  duration?: number;
  x?: number;
  y?: number;
}

// Floating element wrapper
function FloatingCard({ children, delay = 0, duration = 6, x = 0, y = 0 }: FloatingCardProps) {
  return (
    <motion.div
      initial={{ y: 0, x: 0 }}
      animate={{
        y: [y, y - 20, y],
        x: [x, x + 10, x],
      }}
      transition={{
        duration,
        repeat: Infinity,
        repeatType: "reverse",
        ease: "easeInOut",
        delay,
      }}
      className="absolute pointer-events-auto"
    >
      {children}
    </motion.div>
  );
}


export default function HomePage() {
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.15,
        delayChildren: 0.2,
      },
    },
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 30 },
    visible: {
      opacity: 1,
      y: 0,
      transition: { type: "spring", stiffness: 80, damping: 15 },
    },
  };

  const features = [
    { icon: MessageSquare, title: "AI Chat", desc: "Watsonx.ai Q&A", color: "from-emerald-500/20 to-emerald-600/10 border-emerald-500/20 text-emerald-400" },
    { icon: CalendarDays, title: "Meal Planner", desc: "Personalised plans", color: "from-blue-500/20 to-blue-600/10 border-blue-500/20 text-blue-400" },
    { icon: Camera, title: "Image Analyser", desc: "Photo-to-calories", color: "from-purple-500/20 to-purple-600/10 border-purple-500/20 text-purple-400" },
    { icon: Tag, title: "Label Reader", desc: "Deconstruct nutrition", color: "from-amber-500/20 to-amber-600/10 border-amber-500/20 text-amber-400" },
    { icon: ArrowLeftRight, title: "Food Swap", desc: "Healthier swaps", color: "from-rose-500/20 to-rose-600/10 border-rose-500/20 text-rose-400" },
    { icon: BarChart2, title: "Tracker Dashboard", desc: "Track calories & water", color: "from-cyan-500/20 to-cyan-600/10 border-cyan-500/20 text-cyan-400" },
  ];

  return (
    <div className="relative min-h-screen bg-[#05070f] text-gray-100 overflow-hidden flex flex-col font-sans">
      {/* 1. Ambient shifting radial gradients */}
      <div className="absolute inset-0 pointer-events-none z-0">
        <div className="absolute top-[-20%] left-[-20%] w-[80vw] h-[80vw] rounded-full bg-gradient-to-tr from-emerald-900/20 to-transparent blur-[120px] animate-pulse duration-[10s]" />
        <div className="absolute bottom-[-25%] right-[-10%] w-[70vw] h-[70vw] rounded-full bg-gradient-to-bl from-brand-900/15 to-transparent blur-[140px]" />
        <div className="absolute top-[40%] right-[30%] w-[40vw] h-[40vw] rounded-full bg-cyan-900/10 blur-[100px]" />
      </div>

      {/* 2. Floating Food Glassmorphism Illustrations */}
      <div className="absolute inset-0 pointer-events-none z-10 hidden lg:block">
        {/* Avocado */}
        <FloatingCard delay={0} duration={7} x={120} y={150}>
          <div className="backdrop-blur-md bg-white/5 border border-white/10 rounded-2xl p-4 shadow-2xl flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-emerald-500/20 flex items-center justify-center">
              <span className="text-2xl">🥑</span>
            </div>
            <div>
              <p className="text-xs text-emerald-400 font-semibold uppercase tracking-wider">Superfood</p>
              <p className="text-sm font-bold text-white">Avocado</p>
            </div>
          </div>
        </FloatingCard>

        {/* Salmon */}
        <FloatingCard delay={1.5} duration={8} x={80} y={480}>
          <div className="backdrop-blur-md bg-white/5 border border-white/10 rounded-2xl p-4 shadow-2xl flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-rose-500/20 flex items-center justify-center">
              <span className="text-2xl">🥩</span>
            </div>
            <div>
              <p className="text-xs text-rose-400 font-semibold uppercase tracking-wider">Protein</p>
              <p className="text-sm font-bold text-white">Fresh Salmon</p>
            </div>
          </div>
        </FloatingCard>

        {/* Water / Hydration */}
        <FloatingCard delay={2.5} duration={6} x={900} y={120}>
          <div className="backdrop-blur-md bg-white/5 border border-white/10 rounded-2xl p-4 shadow-2xl flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-cyan-500/20 flex items-center justify-center">
              <span className="text-2xl">🥛</span>
            </div>
            <div>
              <p className="text-xs text-cyan-400 font-semibold uppercase tracking-wider">Hydration</p>
              <p className="text-sm font-bold text-white">+250ml water</p>
            </div>
          </div>
        </FloatingCard>

        {/* Apple */}
        <FloatingCard delay={0.8} duration={7.5} x={950} y={450}>
          <div className="backdrop-blur-md bg-white/5 border border-white/10 rounded-2xl p-4 shadow-2xl flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-red-500/20 flex items-center justify-center">
              <span className="text-2xl">🍎</span>
            </div>
            <div>
              <p className="text-xs text-red-400 font-semibold uppercase tracking-wider">Vitamins</p>
              <p className="text-sm font-bold text-white">Apple</p>
            </div>
          </div>
        </FloatingCard>
      </div>

      {/* 3. Header Navbar */}
      <header className="relative z-20 w-full px-6 py-5 max-w-7xl mx-auto flex justify-between items-center">
        <Link href="/" className="flex items-center gap-2">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-brand-600 to-emerald-500 flex items-center justify-center shadow-lg">
            <Leaf size={16} className="text-white" />
          </div>
          <span className="font-extrabold text-white text-lg tracking-tight">NutriGenie <span className="text-brand-400">AI</span></span>
        </Link>
        <div className="flex gap-4">
          <Link href="/auth/login" className="px-4 py-2 text-sm text-gray-300 hover:text-white transition-colors">
            Login
          </Link>
          <Link href="/auth/register" className="px-4 py-2 bg-white/5 border border-white/10 text-white rounded-lg text-sm hover:bg-white/10 transition-colors backdrop-blur-sm">
            Sign Up
          </Link>
        </div>
      </header>

      {/* 4. Main Hero Section */}
      <main className="relative z-20 flex-1 max-w-7xl mx-auto w-full px-6 flex flex-col items-center justify-center text-center py-12 lg:py-24">
        <motion.div
          variants={containerVariants}
          initial="hidden"
          animate="visible"
          className="max-w-3xl space-y-8"
        >
          {/* Badge */}
          <motion.div
            variants={itemVariants}
            className="inline-flex items-center gap-2 bg-emerald-500/10 border border-emerald-500/30 rounded-full px-4 py-1.5 text-xs font-semibold text-emerald-300"
          >
            <Sparkles size={12} className="animate-spin duration-1000" />
            <span>IBM Granite & Watsonx.ai Nutrition Engine</span>
          </motion.div>

          {/* Heading */}
          <motion.h1
            variants={itemVariants}
            className="text-5xl md:text-7xl font-extrabold tracking-tight leading-none text-white"
          >
            Your Intelligent <br />
            <span className="bg-gradient-to-r from-brand-400 via-emerald-400 to-teal-300 bg-clip-text text-transparent">
              Nutrition Assistant
            </span>
          </motion.h1>

          {/* Description */}
          <motion.p
            variants={itemVariants}
            className="text-lg md:text-xl text-gray-400 max-w-2xl mx-auto font-light leading-relaxed"
          >
            Enhance your wellness with personalised meal plans, dynamic hydration & weight logging, smart image analysis, and custom healthy food swap recommendations.
          </motion.p>

          {/* CTAs */}
          <motion.div
            variants={itemVariants}
            className="flex flex-col sm:flex-row gap-4 justify-center items-center pt-4"
          >
            <Link
              href="/dashboard"
              className="w-full sm:w-auto px-8 py-4 bg-gradient-to-r from-brand-600 to-emerald-600 hover:from-brand-500 hover:to-emerald-500 text-white font-semibold rounded-xl shadow-xl shadow-brand-900/25 hover:shadow-brand-900/40 hover:scale-[1.02] active:scale-[0.98] transition-all duration-200"
            >
              Get Started
            </Link>
            <Link
              href="/chat"
              className="w-full sm:w-auto px-8 py-4 bg-white/5 hover:bg-white/10 text-white font-semibold rounded-xl border border-white/10 hover:border-white/20 hover:scale-[1.02] active:scale-[0.98] transition-all duration-200 backdrop-blur-md"
            >
              Ask NutriGenie
            </Link>
          </motion.div>

          {/* Stats Bar */}
          <motion.div
            variants={itemVariants}
            className="grid grid-cols-3 gap-6 max-w-xl mx-auto pt-10 border-t border-white/5"
          >
            <div>
              <p className="text-2xl md:text-3xl font-extrabold text-white">99%</p>
              <p className="text-xs text-gray-500 uppercase tracking-wider mt-1">Accuracy</p>
            </div>
            <div>
              <p className="text-2xl md:text-3xl font-extrabold text-white">Instant</p>
              <p className="text-xs text-gray-500 uppercase tracking-wider mt-1">AI Swaps</p>
            </div>
            <div>
              <p className="text-2xl md:text-3xl font-extrabold text-white">100%</p>
              <p className="text-xs text-gray-500 uppercase tracking-wider mt-1">Secure</p>
            </div>
          </motion.div>
        </motion.div>

        {/* 5. Features Grid Section */}
        <section className="w-full max-w-6xl mt-24">
          <motion.div
            initial={{ opacity: 0, y: 40 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.8 }}
            className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
          >
            {features.map((feat, idx) => (
              <div
                key={idx}
                className={`relative group overflow-hidden bg-gradient-to-b ${feat.color} hover:bg-white/[0.06] border border-white/5 rounded-2xl p-6 text-left transition-all duration-300 hover:scale-[1.03] hover:shadow-2xl hover:border-white/15`}
              >
                <div className="w-12 h-12 rounded-xl bg-white/5 flex items-center justify-center mb-5 group-hover:scale-115 transition-transform duration-300 border border-white/10">
                  <feat.icon size={22} />
                </div>
                <h3 className="text-lg font-bold text-white mb-2">{feat.title}</h3>
                <p className="text-sm text-gray-400 leading-relaxed">{feat.desc}</p>
                <div className="absolute inset-0 border border-white/10 rounded-2xl opacity-0 group-hover:opacity-100 pointer-events-none transition-opacity duration-300" />
              </div>
            ))}
          </motion.div>
        </section>
      </main>

      {/* Footer */}
      <footer className="relative z-20 border-t border-white/5 py-8 mt-12 w-full text-center text-xs text-gray-500">
        <p>© {new Date().getFullYear()} NutriGenie AI. Powered by IBM watsonx.ai & Granite.</p>
      </footer>
    </div>
  );
}

