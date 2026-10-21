// Bridges the Clerk session token into the plain fetch-based API client without
// forcing every caller to be a Clerk-aware component. In dev mode (no Clerk) the
// getter stays null and requests go out unauthenticated (backend uses a dev user).

let tokenGetter: (() => Promise<string | null>) | null = null;

export function setTokenGetter(fn: () => Promise<string | null>) {
  tokenGetter = fn;
}

export async function getAuthToken(): Promise<string | null> {
  if (!tokenGetter) return null;
  try {
    return await tokenGetter();
  } catch {
    return null;
  }
}
