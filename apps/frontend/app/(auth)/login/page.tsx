import { signIn } from "@/auth";

async function loginWithGoogle() {
  "use server";
  await signIn("google");
}

export default function LoginPage() {
  return (
    <main className="mx-auto max-w-sm p-6">
      <h1 className="text-2xl font-semibold mb-4">Login</h1>
      <form action={loginWithGoogle}>
        <button type="submit" className="w-full rounded-md border px-4 py-2">
          Continue with Google
        </button>
      </form>
    </main>
  );
}
