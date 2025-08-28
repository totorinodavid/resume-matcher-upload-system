import { NextRequest, NextResponse } from 'next/server';

// This route proxies the normalized credits balance from the BFF.
// It relies on per-request auth cookies, so disable static optimization/caching.
export const dynamic = 'force-dynamic';
export const revalidate = 0;
export const fetchCache = 'force-no-store';

export async function GET(req: NextRequest) {
	// Prefer absolute origin in server context; fall back to NEXT_PUBLIC_SITE_URL if provided
	const origin = req.nextUrl?.origin || process.env.NEXT_PUBLIC_SITE_URL || '';
	const url = `${origin}/api/bff/api/v1/me/credits`;
	const res = await fetch(url, { cache: 'no-store' }).catch(() => null);
	if (!res) {
		return NextResponse.json({ error: 'unavailable' }, { status: 502 });
	}
	const data = await res.json().catch(() => ({}));
	return NextResponse.json(data);
}

