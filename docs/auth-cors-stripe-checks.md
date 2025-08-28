Quick checks for Authorization header forwarding, CORS, and Stripe webhook bypass.

1) Missing token -> 401

PowerShell:
curl -Method POST -Uri "http://localhost:3000/api/bff/api/v1/match" -Body (@{ resume_id = 'r'; job_id = 'j' } | ConvertTo-Json) -ContentType 'application/json'

2) Forward existing Authorization header through BFF

curl -Method GET -Uri "http://localhost:3000/api/_proxy?path=/api/v1/health/ping" -Headers @{ Authorization = 'Bearer test' }

3) Backend direct CORS preflight (OPTIONS)

curl -Method OPTIONS -Uri "http://localhost:8000/api/v1/health/ping" -Headers @{ 'Origin' = 'https://my-app.vercel.app'; 'Access-Control-Request-Method' = 'GET'; 'Access-Control-Request-Headers' = 'authorization,content-type' }

4) Stripe webhook (no bearer; invalid signature expected)

curl -Method POST -Uri "http://localhost:8000/webhooks/stripe" -Headers @{ 'Stripe-Signature' = 't=0,v1=deadbeef' } -Body '{"type":"ping"}'
