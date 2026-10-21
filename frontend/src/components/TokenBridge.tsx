"use client";

import { useAuth } from "@clerk/nextjs";
import { useEffect } from "react";
import { setTokenGetter } from "@/lib/auth-bridge";

// Rendered only inside ClerkProvider, so useAuth is always safe here.
export default function TokenBridge() {
  const { getToken } = useAuth();
  useEffect(() => {
    setTokenGetter(() => getToken());
  }, [getToken]);
  return null;
}
