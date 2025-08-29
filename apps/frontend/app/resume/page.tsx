import { redirect } from 'next/navigation';

export default function ResumePage() {
  // Redirect to localized resume page
  redirect('/en/resume');
}
