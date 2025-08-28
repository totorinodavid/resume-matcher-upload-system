import uvicorn
# All CORS, Auth (HTTPBearer + Clerk JWT), and Stripe webhook routing are configured in create_app().
from .base import create_app

app = create_app()

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
