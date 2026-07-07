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
import { useSidebar } from "./SidebarContext";

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
  const { isOpen, setIsOpen } = useSidebar();

  // Hide sidebar on landing page and auth screens
  if (pathname === "/" || pathname.startsWith("/auth/")) return null;

  return (
    <>
      {/* Overlay Backdrop on Mobile */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black/60 backdrop-blur-xs z-40 md:hidden"
          onClick={() => setIsOpen(false)}
        />
      )}

      {/* Sidebar Container */}
      <aside
        className={clsx(
          "fixed inset-y-0 left-0 z-50 w-64 bg-gray-900 border-r border-gray-800 py-6 px-3 flex flex-col transition-transform duration-300 ease-in-out",
          "md:static md:translate-x-0 md:flex md:w-20 lg:w-56",
          isOpen ? "translate-x-0" : "-translate-x-full"
        )}
      >
        {/* Logo */}
        <Link
          href="/"
          className="flex items-center gap-2 px-3 mb-8 justify-start md:justify-center lg:justify-start"
        >
          <div className="w-7 h-7 rounded-lg bg-brand-600 flex items-center justify-center flex-shrink-0">
            <Leaf size={14} className="text-white" />
          </div>
          <span className="font-bold text-white text-sm md:hidden lg:inline">
            NutriGenie AI
          </span>
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
                  "justify-start md:justify-center lg:justify-start",
                  active
                    ? "bg-brand-600/10 text-brand-400 border border-brand-800/50"
                    : "text-gray-400 hover:text-white hover:bg-gray-800"
                )}
              >
                <Icon size={16} className="flex-shrink-0" />
                <span className="md:hidden lg:inline">{label}</span>
              </Link>
            );
          })}
        </nav>

        <p className="text-xs text-gray-700 px-3 mt-4 text-left md:hidden lg:block">
          Powered by IBM Granite
        </p>
      </aside>
    </>
  );
}
