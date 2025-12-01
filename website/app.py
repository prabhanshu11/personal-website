'''Main FastHTML application for prabhanshu.space'''

import os
from fasthtml.common import *
from website import auth

# Configuration from environment variables
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 8000))
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# Shared styles for the application
GLOBAL_STYLES = Style('''
    /* Minimal CSS Reset */
    * { 
        box-sizing: border-box;
    }
    
    body {
        /* Standard HTML look: serif font, no background color specified (defaults to white) */
        font-family: serif; 
        line-height: 1.6;
        color: #000;
        background: white;
        /* "left aligned with no margin" - usually means no auto margin on container, 
           but body usually has some default margin in browser. 
           User said "no margin", so we'll remove body margin but keep some padding for readability?
           Or literally 0 margin? Let's go with 0 margin on body and simple padding. */
        margin: 0;
        padding: 1rem;
    }
    
    /* Remove container centering */
    .container {
        max-width: 100%;
        margin: 0;
    }
    
    header {
        margin-bottom: 2rem;
        border-bottom: 1px solid #ccc;
    }
    
    h1 { 
        font-size: 2em;
        font-weight: bold;
        margin-bottom: 0.5em;
    }
    
    .subtitle {
        color: #555;
        font-size: 1.2em;
    }
    
    section {
        margin-bottom: 2rem;
    }
    
    h2 {
        font-size: 1.5em;
        font-weight: bold;
        margin-bottom: 1rem;
        border-bottom: 1px solid #ccc;
    }
    
    p { 
        margin-bottom: 1rem;
        /* "left aligned" is default */
    }
    
    ul {
        margin-left: 2rem;
        margin-bottom: 1rem;
    }
    
    li {
        margin-bottom: 0.5rem;
    }
    
    footer {
        margin-top: 3rem;
        border-top: 1px solid #ccc;
        padding-top: 1rem;
        color: #777;
    }
    
    a { 
        color: #0000EE; /* Standard link blue */
        text-decoration: underline;
    }
    
    a:visited {
        color: #551A8B; /* Standard visited purple */
    }
    
    .btn {
        /* Simple button style if needed, or just link */
        margin-right: 1rem;
    }

    .links {
        margin-top: 1rem;
    }
    
    .emoji {
        margin-right: 0.5rem;
    }

    .skills-list li {
        margin-bottom: 0.1rem;
    }

    @media (min-width: 768px) {
        header, section {
            padding: 1.5rem;
        }
    }
''')

# Script for Mobile Zoom Reflow
# This forces the body width to match the visual viewport width when zooming,
# causing text to reflow (wrap) within the zoomed view.
ZOOM_REFLOW_SCRIPT = Script('''
    if (window.visualViewport) {
        window.visualViewport.addEventListener('resize', () => {
            // Only apply on mobile/touch devices where zooming is common
            if (window.innerWidth <= 768) {
                document.body.style.width = window.visualViewport.width + 'px';
            }
        });
    }
''')

# Initialize FastHTML app
app = FastHTML(
    secret_key=os.getenv("SECRET_KEY", "dev-secret-key-change-in-prod"),
    hdrs=(
        Meta(name="viewport", content="width=device-width, initial-scale=1.0, user-scalable=yes, maximum-scale=5.0"),
        Meta(name="description", content="Personal website of Prabhanshu - Software Developer and Python Enthusiast"),
        Meta(name="author", content="Prabhanshu"),
        Meta(charset="utf-8"),
        GLOBAL_STYLES,
        ZOOM_REFLOW_SCRIPT
    ),
)


# Helper function to create consistent layout
def create_layout(title: str, *content):
    """Create a consistent page layout"""
    return Html(
        Head(
            Title(f"{title} - Prabhanshu"),
            Meta(name="viewport", content="width=device-width, initial-scale=1"),
            GLOBAL_STYLES
        ),
        Body(
            Div(
                *content,
                cls="container"
            )
        ),
        lang="en"
    )


@app.get("/")
def home():
    return create_layout(
        "Home",
        Div(
            H1("Prabhanshu", cls="fade-in"),
            P("Data Scientist & AI Engineer", cls="subtitle fade-in"),
            Div(
                A("GitHub", href="https://github.com/prabhanshu11", cls="btn"),
                A("LinkedIn", href="https://linkedin.com/in/prabhanshu11", cls="btn"),
                A("Email", href="mailto:hello@prabhanshu.space", cls="btn"),
                cls="links fade-in"
            ),
            cls="hero"
        ),
        Div(
            H2("About Me"),
            P("""
            I am a Data Scientist and AI Engineer with a passion for building intelligent systems. 
            My expertise lies in developing scalable RAG pipelines, deploying Large Language Models (LLMs), 
            and creating data-driven applications including Databricks Apps.
            """),
            P("""
            I enjoy solving complex problems and turning data into actionable insights. 
            Whether it's optimizing machine learning models or architecting cloud-native solutions on Azure, 
            I am always eager to learn and innovate.
            """),
            cls="section fade-in"
        ),
        Div(
            H2("Skills"),
            Ul(
                Li("Python, SQL, PySpark"),
                Li("Machine Learning, Deep Learning, NLP"),
                Li("Generative AI, LLMs, RAG Pipelines"),
                Li("Databricks, Azure, Docker, Kubernetes"),
                Li("FastAPI, FastHTML, React"),
                cls="skills-list"
            ),
            cls="section fade-in"
        ),
        Div(
            H2("Newsletter"),
            P("Join my newsletter to get updates on thoughts on AI.", cls="text-justify"),
            Form(
                Input(type="email", name="email", placeholder="Enter your email", required=True, style="padding: 0.5rem; border-radius: 5px; border: 1px solid #ccc; width: 100%; margin-bottom: 1rem;"),
                Button("Subscribe", type="submit", cls="btn", style="width: 100%;"),
                action="/newsletter/subscribe",
                method="post",
                style="max-width: 400px;"
            ),
            cls="section fade-in"
        ),
        Div(
            A("My Zone", href="/myzone", style="font-size: 0.8rem; color: #888; text-decoration: none; float: right; margin-top: 1rem;"),
            style="overflow: hidden; padding-bottom: 2rem;" 
        )
    )


@app.get("/health")
def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy", 
        "service": "prabhanshu-website",
        "version": "0.1.0"
    }


@app.get("/about")
def about():
    """Detailed about page"""
    return create_layout(
        "About",
        Header(
            H1("About Me"),
            P(
                A("← Back to Home", href="/"),
                cls="subtitle"
            )
        ),
        Section(
            H2(Span("🚀", cls="emoji"), "My Journey"),
            P(
                "My journey began in engineering, where I developed a rigorous approach to problem-solving. "
                "This foundation serves me well in Data Science, where precision is paramount."
            ),
            P(
                "At ", Strong("Bread Financials"), ", I manage complex ETL pipelines and account reconciliations, "
                "ensuring data integrity for critical financial reports. Previously at ", Strong("TheMathCompany"), 
                ", I built NLP frameworks to analyze safety incidents, turning unstructured text into actionable safety insights."
            ),
            P(
                "I combine this deep data experience with modern web technologies to build tools that are powerful yet intuitive."
            )
        ),
        Section(
            H2(Span("💡", cls="emoji"), "Philosophy"),
            P(
                "I believe in writing clean, maintainable code and using the right tool for the job. "
                "Whether it's a complex RAG pipeline or a streamlined Databricks App, my goal is always "
                "to deliver robust solutions that drive real business value."
            )
        ),
        Footer(
            P(A("← Back to Home", href="/")),
            P(A("My Zone", href="/login", style="font-size: 0.8em; color: #ccc; text-decoration: none;"))
        )
    )


# Authentication Routes
app.get("/login")(auth.login_page)
app.get("/auth/github/login")(auth.github_login)
app.get("/auth/callback")(auth.github_callback)
app.get("/logout")(auth.logout)

@app.get("/myzone")
def my_zone(session):
    if not auth.check_auth(session):
        return RedirectResponse("/login", status_code=303)
    
    return create_layout(
        "My Zone",
        Header(
            H1("My Zone"),
            P("Welcome back, Prabhanshu!", cls="subtitle"),
            A("Logout", href="/logout", cls="btn", style="font-size: 0.8em;")
        ),
        Section(
            H2("Dashboard"),
            P("This is the private dashboard area."),
            # Placeholder for future dashboard widgets
            Div(
                P("More features coming soon..."),
                style="padding: 2rem; background: #f9f9f9; border-radius: 8px;"
            )
        ),
        Footer(
            P(A("← Back to Home", href="/"))
        )
    )


# Custom 404 handler
@app.exception_handler(404)
def not_found(request, exc):
    """Custom 404 page"""
    """Custom 404 page"""
    return HTMLResponse(
        to_xml(
            create_layout(
                "404 - Page Not Found",
                Header(
                    H1("404 - Page Not Found")
                ),
                Section(
                    P("Sorry, the page you're looking for doesn't exist."),
                    P(A("← Back to Home", href="/"))
                )
            )
        ),
        status_code=404
    )


if __name__ == "__main__":
    # Use uvicorn for production-ready server
    import uvicorn
    
    print(f"🚀 Starting FastHTML server on {HOST}:{PORT}")
    print(f"🔧 Debug mode: {DEBUG}")
    
    uvicorn.run(
        "website.app:app",
        host=HOST,
        port=PORT,
        reload=DEBUG,
        log_level="info" if not DEBUG else "debug"
    )