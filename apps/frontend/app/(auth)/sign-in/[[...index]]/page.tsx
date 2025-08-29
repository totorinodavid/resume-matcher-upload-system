import { redirect } from 'next/navigation';

export default function Page() {
  // Clerk has been removed. Redirect to NextAuth login.
  redirect('/login');
}
