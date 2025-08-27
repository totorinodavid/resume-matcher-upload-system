export interface CreditPlan {
  id: 'small' | 'medium' | 'large';
  title: string;
  credits: number;
  priceLabel: string; // human readable e.g. "$5"
  price_id: string;   // Stripe Price ID
  benefits?: string[];
}

// TODO: Replace placeholder price IDs with your real Stripe price IDs.
export const CreditProducts: CreditPlan[] = [
  {
    id: 'small',
    title: 'Small',
    credits: 100,
    priceLabel: '$5',
    price_id: process.env.NEXT_PUBLIC_STRIPE_PRICE_SMALL || 'price_small_placeholder',
    benefits: ['Für Tests und kleine Läufe'],
  },
  {
    id: 'medium',
    title: 'Medium',
    credits: 500,
    priceLabel: '$20',
    price_id: process.env.NEXT_PUBLIC_STRIPE_PRICE_MEDIUM || 'price_medium_placeholder',
    benefits: ['Empfohlen für regelmäßige Nutzung'],
  },
  {
    id: 'large',
    title: 'Large',
    credits: 1500,
    priceLabel: '$50',
    price_id: process.env.NEXT_PUBLIC_STRIPE_PRICE_LARGE || 'price_large_placeholder',
    benefits: ['Für Teams und Power-User'],
  },
];

// named interface CreditPlan is already exported above
