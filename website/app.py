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
    """Main homepage with profile information"""
    return create_layout(
        "Home",
        Header(
            H1("Prabhanshu"),
            P("Data Scientist & AI Engineer | Building robust, intelligent applications", 
              cls="subtitle")
        ),
        
        # Introduction Section
        Section(
            H2(Span("👋", cls="emoji"), "Introduction"),
            P(
                "I am a Data Scientist and Engineer dedicated to building robust, scalable systems. "
                "With a background in processing financial and industrial data at scale, I focus on "
                "creating applications that are not just experimental, but production-ready."
            ),
            P(
                "My expertise lies in architecting ", Strong("RAG pipelines"), ", optimizing data flows, "
                "and developing native ", Strong("Databricks Apps"), " that leverage your data infrastructure effectively."
            )
        ),
        
        # About Me Section
        Section(
            H2(Span("💼", cls="emoji"), "About Me"),
            P(
                "I bridge the gap between data science and software engineering. "
                "My experience ranges from handling critical financial datasets to building "
                "advanced NLP models for safety analysis. I am passionate about:"
            ),
            Ul(
                Li("Building Production-Grade AI Applications"),
                Li("Databricks App Development & Optimization"),
                Li("Large Scale Data Processing (PySpark, Azure)"),
                Li("Natural Language Processing & RAG"),
                Li("Robust ETL Pipelines")
            )
        ),
        
        # Skills Section
        Section(
            H2(Span("🛠️", cls="emoji"), "Skills & Technologies"),
            P("Python • RAG Pipelines • LLM Integration • Data Engineering • PySpark • Azure • Databricks Apps • FastHTML • Docker")
        ),
        
        # Projects Section
        Section(
            H2(Span("📁", cls="emoji"), "Projects"),
            P(
                "This section will showcase my projects. "
                "Stay tuned for updates!"
            ),
            P(
                A("View my GitHub", href="https://github.com/prabhanshu11", target="_blank"),
                " for my current work."
            )
        ),
        
        # Contact Section
        Section(
            H2(Span("📫", cls="emoji"), "Get in Touch"),
            P(
                "Feel free to reach out to me at: ",
                A("hello @prabhanshu.space", href="mailto:hello @prabhanshu.space")
            ),
            P(
                "GitHub: ",
                A(" @prabhanshu11", 
                  href="https://github.com/prabhanshu11",
                  target="_blank")
            )
        ),
        
        Footer(
            P(
                "© 2025 Prabhanshu. Built with ",
                A("FastHTML", href="https://fastht.ml", target="_blank"),
                " and deployed on VPS with ❤️"
            )
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