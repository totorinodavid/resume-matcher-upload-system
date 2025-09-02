# Back-compat wrapper to import the existing Stripe webhook route
from .api.router.webhooks import webhooks_router as router  # re-export for reference
