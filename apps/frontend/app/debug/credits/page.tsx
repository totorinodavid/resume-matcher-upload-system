"use client";
import Link from 'next/link';
import { useCreditsState } from '@/hooks/useCredits';

export default function CreditsDebugPage() {
	const { balance, loading, error, refresh } = useCreditsState();
	return (
		<div className="p-6 space-y-3">
			<h1 className="text-xl font-semibold">Credits Debug</h1>
			<div className="rounded-lg border border-zinc-800 bg-zinc-950 p-4">
				<div className="flex items-center justify-between">
					<div className="text-sm text-zinc-300">Aktuelles Guthaben</div>
					<div className="text-lg font-semibold text-white">{loading ? '…' : (balance ?? 0)}</div>
				</div>
				{error && <p className="text-xs text-red-400 mt-2">{error}</p>}
				<div className="mt-3 flex items-center gap-2">
					<button className="px-3 py-1.5 rounded bg-zinc-700 hover:bg-zinc-600 text-white text-xs" onClick={() => refresh()} disabled={loading}>Neu laden</button>
					<Link href="/billing" className="px-3 py-1.5 rounded bg-rose-700 hover:bg-rose-600 text-white text-xs">Zu Billing</Link>
				</div>
			</div>
			<p className="text-xs text-zinc-500">Melde dich an, kaufe ein Paket über Billing, und kehre hierher zurück—das Guthaben sollte steigen.</p>
		</div>
	);
}

