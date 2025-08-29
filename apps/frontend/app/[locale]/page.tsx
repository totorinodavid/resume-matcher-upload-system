import { auth } from "@/auth";
import Hero from '@/components/home/hero';

export default async function HomePage() {
  const session = await auth();
  return <Hero session={session} />;
}
