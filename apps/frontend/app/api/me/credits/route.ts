import { NextRequest, NextResponse } from 'next/server';

export const dynamic = 'force-dynamic';
export const revalidate = 0;
export const fetchCache = 'force-no-store';

export async function GET(_req: NextRequest) {
  // Simple passthrough to backend via BFF so the frontend can refresh balance
  const res = await fetch(`${process.env.NEXT_PUBLIC_SITE_URL || ''}/api/bff/api/v1/me/credits`, { cache: 'no-store' }).catch(() => null);
  if (!res) return NextResponse.json({ error: 'unavailable' }, { status: 502 });
  const data = await res.json().catch(() => ({}));
  return NextResponse.json(data);
}
