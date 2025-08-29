import { signOut } from "@/auth";

export function LogoutButton() {
  async function doLogout() {
    "use server";
    await signOut();
  }
  return (
    <form action={doLogout}>
      <button type="submit" className="rounded-md border px-3 py-1">Logout</button>
    </form>
  );
}
