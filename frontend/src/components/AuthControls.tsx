"use client";

import { SignedIn, SignedOut, SignInButton, UserButton } from "@clerk/nextjs";

const hasClerk = !!process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY;

export default function AuthControls() {
  if (!hasClerk) {
    return <span className="text-xs text-black/40">dev mode</span>;
  }
  return (
    <>
      <SignedOut>
        <SignInButton mode="modal">
          <button className="text-sm font-semibold hover:text-teal-700">Sign in</button>
        </SignInButton>
      </SignedOut>
      <SignedIn>
        <UserButton afterSignOutUrl="/" />
      </SignedIn>
    </>
  );
}
