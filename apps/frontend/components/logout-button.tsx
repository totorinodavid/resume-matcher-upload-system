"use client";

import { doLogout } from "@/app/actions";

export function LogoutButton() {
  return (
    <form action={doLogout}>
      <button type="submit" className="rounded-md border px-3 py-1">
        Logout
      </button>
    </form>
  );
}
