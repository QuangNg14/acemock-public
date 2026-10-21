import { clerkMiddleware } from "@clerk/nextjs/server";
import { NextResponse } from "next/server";

const hasClerk = !!process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY;

// All app routes are public; backend enforces auth. Clerk middleware only runs
// when configured so the app works in dev mode without keys.
export default hasClerk ? clerkMiddleware() : () => NextResponse.next();

export const config = {
  matcher: ["/((?!_next|.*\\..*).*)"],
};
