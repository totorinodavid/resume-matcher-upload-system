import { redirect } from 'next/navigation';

export default function LoginPage() {
  // Redirect to localized login page
  redirect('/en/login');
}
