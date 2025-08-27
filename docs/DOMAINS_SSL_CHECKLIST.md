# Domains & SSL Checklist

Vercel (Frontend)
- Add custom domain(s) (apex and www) to the project.
- Configure DNS (A/ALIAS or CNAME) as guided by Vercel.
- Separate preview deployments vs. production domain.
- Verify SSL/TLS status is Ready (automatic certificates).

Render (Backend)
- Confirm the Render service URL is HTTPS and presents a valid certificate.
- Optionally add a custom domain to Render for the API if needed.

Post-setup validation
- Open the frontend via the custom domain and ensure static + server routes work.
- Call the backend from frontend (through BFF) to confirm CORS/headers are correct.
