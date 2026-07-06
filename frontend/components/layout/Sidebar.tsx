"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  MessageSquare,
  CalendarDays,
  Camera,
  Tag,
  ArrowLeftRight,
  BarChart2,
  User,
  Leaf,
} from "lucide-react";
import clsx from "clsx";

const NAV_ITEMS = [
  { href: "/chat", label: "AI Chat", icon: MessageSquare },
  { href: "/meal-plan", label: "Meal Planner", icon: CalendarDays },
  { href: "/image-analysis", label: "Image Analysis", icon: Camera },
  { href: "/label-reader", label: "Label Reader", icon: Tag },
  { href: "/food-swap", label: "Food Swap", icon: ArrowLeftRight },
  { href: "/dashboard", label: "Dashboard", icon: BarChart2 },
  { href: "/profile", label: "Profile", icon: User },
];

export function Sidebar() {
  const pathname = usePathname();

  if (pathname === "/") return null;

  return (
    <aside className="hidden md:flex flex-col w-56 min-h-screen bg-gray-900 border-r border-gray-800 py-6 px-3">
      {/* Logo */}
      <Link href="/" className="flex items-center gap-2 px-3 mb-8">
        <div className="w-7 h-7 rounded-lg bg-brand-600 flex items-center justify-center flex-shrink-0">
          <Leaf size={14} className="text-white" />
        </div>
        <span className="font-bold text-white text-sm">NutriGenie AI</span>
      </Link>

      {/* Navigation */}
      <nav className="flex flex-col gap-1 flex-1">
        {NAV_ITEMS.map(({ href, label, icon: Icon }) => {
          const active = pathname.startsWith(href);
          return (
            <Link
              key={href}
              href={href}
              className={clsx(
                "flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-colors",
                active
                  ? "bg-brand-600/10 text-brand-400 border border-brand-800/50"
                  : "text-gray-400 hover:text-white hover:bg-gray-800"
              )}
            >
              <Icon size={16} className="flex-shrink-0" />
              {label}
            </Link>
          );
        })}
      </nav>

      <p className="text-xs text-gray-700 px-3 mt-4">Powered by IBM Granite</p>
    </aside>
  );
}
