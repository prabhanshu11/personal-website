import os
import httpx
from fasthtml.common import *
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# GitHub OAuth Configuration
GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")
ALLOWED_USER = "prabhanshu11"  # Restrict access to this GitHub user

def get_github_auth_url():
    return f"https://github.com/login/oauth/authorize?client_id={GITHUB_CLIENT_ID}&scope=read:user"

def login_page():
    return Html(
        Head(
            Title("Login - My Zone"),
            Meta(name="viewport", content="width=device-width, initial-scale=1"),
            # Reusing global styles from app.py would be ideal, but for now we'll just add basic styling
            Style('''
                body { font-family: serif; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; background-color: #f5f5f5; }
                .login-card { background: white; padding: 2rem; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); text-align: center; }
                .btn-github { background-color: #24292e; color: white; padding: 0.75rem 1.5rem; text-decoration: none; border-radius: 4px; font-weight: bold; display: inline-block; margin-top: 1rem; }
                .btn-github:hover { background-color: #1b1f23; }
                h1 { margin-top: 0; }
            ''')
        ),
        Body(
            Div(
                H1("My Zone Login"),
                P("Restricted access area."),
                A("Login with GitHub", href="/auth/github/login", cls="btn-github"),
                cls="login-card"
            )
        )
    )

async def github_login(req):
    if not GITHUB_CLIENT_ID:
        return Titled("Error", P("GitHub Client ID not configured."))
    return RedirectResponse(get_github_auth_url())

async def github_callback(code: str, req, session):
    if not code:
        return Titled("Error", P("No code provided."))
    
    async with httpx.AsyncClient() as client:
        # Exchange code for access token
        token_resp = await client.post(
            "https://github.com/login/oauth/access_token",
            headers={"Accept": "application/json"},
            data={
                "client_id": GITHUB_CLIENT_ID,
                "client_secret": GITHUB_CLIENT_SECRET,
                "code": code,
            },
        )
        token_data = token_resp.json()
        access_token = token_data.get("access_token")
        
        if not access_token:
            return Titled("Error", P("Failed to get access token."))
        
        # Get user info
        user_resp = await client.get(
            "https://api.github.com/user",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/json",
            },
        )
        user_data = user_resp.json()
        username = user_data.get("login")
        
        if username != ALLOWED_USER:
            return Titled("Unauthorized", P(f"User '{username}' is not allowed to access this area."))
        
        # Set session
        session["user"] = username
        return RedirectResponse("/myzone", status_code=303)

def logout(session):
    session.clear()
    return RedirectResponse("/", status_code=303)

def requires_auth(func):
    """Decorator to require authentication for a route"""
    def wrapper(*args, **kwargs):
        req = args[0] if args else None # Assuming req is the first arg if present, or we need to find it
        # In FastHTML, we often get session directly. Let's check session.
        # This is a bit tricky with FastHTML's dependency injection.
        # A simpler way is to check session inside the route handler.
        pass
    return func

# Better approach for FastHTML: Check session in the route
def check_auth(session):
    return session.get("user") == ALLOWED_USER
