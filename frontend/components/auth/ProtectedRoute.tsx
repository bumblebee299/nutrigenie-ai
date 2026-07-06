"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { isAuthenticated } from "@/services/authService";

interface ProtectedRouteProps {
  children: React.ReactNode;
}

export function ProtectedRoute({ children }: ProtectedRouteProps) {
  const router = useRouter();
  const [mounted, setMounted] = useState(false);
  const [authenticated, setAuthenticated] = useState(false);

  useEffect(() => {
    setMounted(true);

    const auth = isAuthenticated();
    setAuthenticated(auth);

    if (!auth) {
      router.replace("/auth/login");
    }
  }, [router]);

  // Don't render anything until after the component mounts.
  if (!mounted) {
    return null;
  }

  if (!authenticated) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-gray-400 animate-pulse">
          Redirecting...
        </div>
      </div>
    );
  }

  return <>{children}</>;
}