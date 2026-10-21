import { ClerkProvider } from "@clerk/nextjs";
import TokenBridge from "./TokenBridge";

const hasClerk = !!process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY;

export default function AuthProvider({ children }: { children: React.ReactNode }) {
  if (!hasClerk) return <>{children}</>;
  return (
    <ClerkProvider>
      <TokenBridge />
      {children}
    </ClerkProvider>
  );
}
