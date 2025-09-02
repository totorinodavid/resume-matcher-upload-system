-- Insert Stripe price data into the database
INSERT INTO prices (stripe_price_id, credits_per_unit, price_in_cents, currency, active, name, description) 
VALUES 
  ('price_1S2v9EEPwuWwkzKTWctV6b8H', 100, 500, 'eur', true, 'Starter Pack', '10 resume analyses or 20 job matches'),
  ('price_1S2v9EEPwuWwkzKTozEzxD1f', 500, 2000, 'eur', true, 'Pro Pack', '50 resume analyses + improvements'), 
  ('price_1S2v9FEPwuWwkzKTygApOQqp', 1200, 3500, 'eur', true, 'Premium Pack', 'Everything included with 20% bonus')
ON CONFLICT (stripe_price_id) DO UPDATE SET
  credits_per_unit = EXCLUDED.credits_per_unit,
  price_in_cents = EXCLUDED.price_in_cents,
  currency = EXCLUDED.currency,
  active = EXCLUDED.active,
  name = EXCLUDED.name,
  description = EXCLUDED.description;
