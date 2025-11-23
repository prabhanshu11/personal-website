'''Main FastHTML application for prabhanshu.space'''

import os
from fasthtml.common import *

# Configuration from environment variables
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 8000))
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# Shared styles for the application
GLOBAL_STYLES = Style('''
    * { 
        margin: 0; 
        padding: 0; 
        box-sizing: border-box;
        overflow-wrap: break-word;
        word-wrap: break-word;
    }
    
    body {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 
                     Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
        line-height: 1.6;
        color: #333;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
        padding: 2rem 1rem;
    }
    
    .container {
        max-width: 900px;
        margin: 0 auto;
    }
    
    header {
        background: white;
        padding: 2.5rem;
        margin-bottom: 2rem;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        text-align: center;
    }
    
    h1 { 
        color: #2c3e50;
        margin-bottom: 0.5rem;
        font-size: 2.5rem;
        font-weight: 700;
    }
    
    .subtitle {
        color: #7f8c8d;
        font-size: 1.2rem;
        font-weight: 400;
    }
    
    section {
        background: white;
        padding: 2rem;
        margin-bottom: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    h2 {
        color: #34495e;
        margin-bottom: 1rem;
        border-bottom: 3px solid #667eea;
        padding-bottom: 0.5rem;
        font-size: 1.8rem;
    }
    
    p { 
        margin-bottom: 1rem;
        text-align: justify;
        color: #555;
        hyphens: auto;
    }
    
    ul {
        margin-left: 2rem;
        margin-bottom: 1rem;
    }
    
    li {
        margin-bottom: 0.5rem;
        color: #555;
    }
    
    footer {
        text-align: center;
        color: white;
        margin-top: 3rem;
        padding: 1.5rem;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 12px;
    }
    
    a { 
        color: #667eea;
        text-decoration: none;
        font-weight: 500;
        transition: color 0.3s ease;
    }
    
    a:hover {
        color: #764ba2;
        text-decoration: underline;
    }
    
    .emoji {
        font-style: normal;
        margin-right: 0.5rem;
    }
    
    @media (max-width: 768px) {
        body {
            padding: 1rem 0.5rem;
        }
        
        h1 {
            font-size: 2rem;
        }
        
        h2 {
            font-size: 1.5rem;
        }
        
        header, section {
            padding: 1.5rem;
        }
    }
''')

# Initialize FastHTML app
app = FastHTML(
    hdrs=(
        Meta(name="viewport", content="width=device-width, initial-scale=1.0"),
        Meta(name="description", content="Personal website of Prabhanshu - Software Developer and Python Enthusiast"),
        Meta(name="author", content="Prabhanshu"),
        Meta(charset="utf-8"),
        GLOBAL_STYLES
    ),
)


# Helper function to create consistent layout
def create_layout(title: str, *content):
    """Create a consistent page layout"""
    return Html(
        Head(
            Title(f"{title} - Prabhanshu"),
            Meta(name="viewport", content="width=device-width, initial-scale=1"),
            Style(GLOBAL_STYLES)
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
        [
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
                H2("Newsletter"),
                P("Join my newsletter to get updates on my latest projects and thoughts on AI.", cls="text-justify"),
                Form(
                    Input(type="email", name="email", placeholder="Enter your email", required=True, style="padding: 0.5rem; border-radius: 5px; border: 1px solid #ccc; width: 100%; margin-bottom: 1rem;"),
                    Button("Subscribe", type="submit", cls="btn", style="width: 100%;"),
                    action="/newsletter/subscribe",
                    method="post",
                    style="max-width: 400px; margin: 0 auto;"
                ),
                cls="section fade-in"
            ),
            Div(
                H2("About Me"),
                P("""
                I am a Data Scientist and AI Engineer with a passion for building intelligent systems. 
                My expertise lies in developing scalable RAG pipelines, deploying Large Language Models (LLMs), 
                and creating data-driven applications using Databricks Apps.
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
            )
        ]
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
            P(A("← Back to Home", href="/"))
        )
    )


# Custom 404 handler
@app.exception_handler(404)
def not_found(request, exc):
    """Custom 404 page"""
    return create_layout(
        "404 - Page Not Found",
        Header(
            H1("404 - Page Not Found")
        ),
        Section(
            P("Sorry, the page you're looking for doesn't exist."),
            P(A("← Back to Home", href="/"))
        )
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