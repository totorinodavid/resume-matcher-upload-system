import { auth } from "@/auth";

export default async function DebugAuthPage() {
  const session = await auth();
  return (
    <div className="p-6 space-y-4">
      <h1 className="text-xl font-semibold">Auth Debug</h1>
      <div className="rounded-md border border-zinc-800 bg-zinc-900 p-4 text-sm">
        <pre className="whitespace-pre-wrap text-xs">{JSON.stringify(session, null, 2)}</pre>
      </div>
    </div>
  );
}
