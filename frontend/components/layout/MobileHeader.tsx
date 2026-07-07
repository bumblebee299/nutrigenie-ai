"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Menu, Leaf } from "lucide-react";
import { useSidebar } from "./SidebarContext";

export function MobileHeader() {
  const pathname = usePathname();
  const { toggle } = useSidebar();

  // Do not render mobile header on landing page or auth screens
  if (pathname === "/" || pathname.startsWith("/auth/")) {
    return null;
  }

  return (
    <header className="flex md:hidden items-center justify-between h-14 px-4 bg-gray-900 border-b border-gray-800 sticky top-0 z-40">
      {/* Brand logo & Hamburger */}
      <div className="flex items-center gap-3">
        <button
          onClick={toggle}
          className="p-1.5 rounded-lg bg-gray-800 border border-gray-700 text-gray-400 hover:text-white transition-colors focus:outline-none"
          aria-label="Open navigation menu"
        >
          <Menu size={20} />
        </button>

        <Link href="/" className="flex items-center gap-2">
          <div className="w-7 h-7 rounded-lg bg-brand-600 flex items-center justify-center flex-shrink-0">
            <Leaf size={14} className="text-white" />
          </div>
          <span className="font-bold text-white text-sm">NutriGenie AI</span>
        </Link>
      </div>

      <div className="w-8 h-8" /> {/* Spacer to align brand logo nicely */}
    </header>
  );
}
