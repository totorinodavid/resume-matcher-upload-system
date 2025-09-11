"use client";

import { useSession } from 'next-auth/react';
import Hero from '@/components/home/hero';

export default function HomePage() {
  const { data: session } = useSession();
  return <Hero session={session} />;
}
