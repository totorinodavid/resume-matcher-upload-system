import { redirect } from 'next/navigation';

export default function MatchPage() {
  // Redirect to localized match page
  redirect('/en/match');
}
