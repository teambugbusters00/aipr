#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI PR Reviewer - Web Application
FastAPI-based web interface for the AI PR Reviewer with frontend
"""

import os
import sys
import json
from pathlib import Path
from datetime import timedelta
from typing import Optional

# Fix Windows console encoding
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import our modules
from src.orchestrator import ReviewOrchestrator
from src.dashboard import generate_html_dashboard
from src.types import ReviewResult, JiraTicket, PRDiff, DiffFile

app = FastAPI(
    title="AI PR Reviewer",
    description="Senior Engineer PR Review System",
    version="1.0.0"
)

# Setup templates
templates = Jinja2Templates(directory="templates")

# Serve React static files
app.mount("/static", StaticFiles(directory="frontend/dist/assets"), name="static")

# Initialize orchestrator
orchestrator = ReviewOrchestrator()

# Store recent reviews in memory
recent_reviews = []


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    """Main dashboard page - serve React app"""
    from pathlib import Path
    index_path = Path("frontend/dist/index.html")
    if index_path.exists():
        return HTMLResponse(index_path.read_text(encoding='utf-8'))
    return templates.TemplateResponse("index.html", {"request": request, "reviews": recent_reviews[:10]})


@app.get("/review", response_class=HTMLResponse)
def review_page(request: Request):
    """Review page - serve React app"""
    from pathlib import Path
    index_path = Path("frontend/dist/index.html")
    if index_path.exists():
        return HTMLResponse(index_path.read_text(encoding='utf-8'))
    return templates.TemplateResponse("review.html", {"request": request})


@app.post("/review", response_class=HTMLResponse)
def review_submit(request: Request, jira_key: str = Form(...), pr_number: str = Form(...)):
    """Review page - form submission"""
    jira_key = jira_key.strip()
    pr_number = pr_number.strip()
    
    if not jira_key or not pr_number:
        return templates.TemplateResponse("review.html", {"request": request, "error": "Please provide both Jira key and PR number"})
    
    try:
        pr_num = int(pr_number)
    except ValueError:
        return templates.TemplateResponse("review.html", {"request": request, "error": "PR number must be a number"})
    
    try:
        result = orchestrator.review(jira_key, pr_num)
        
        # Store in recent reviews
        review_data = {
            'id': len(recent_reviews) + 1,
            'jira_key': jira_key,
            'pr_number': pr_num,
            'verdict': result.verdict.value,
            'summary': result.summary,
            'passed': result.passed_requirements,
            'failed': result.failed_requirements,
            'risks': len(result.risks),
            'result': result,
        }
        recent_reviews.insert(0, review_data)
        if len(recent_reviews) > 50:
            recent_reviews.pop()
        
        return templates.TemplateResponse("result.html", {"request": request, "result": result})
        
    except Exception as e:
        return templates.TemplateResponse("review.html", {"request": request, "error": f"Review failed: {str(e)}"})


@app.get("/demo", response_class=HTMLResponse)
def demo(request: Request):
    """Run demo review - serve React app"""
    from pathlib import Path
    index_path = Path("frontend/dist/index.html")
    if index_path.exists():
        return HTMLResponse(index_path.read_text(encoding='utf-8'))
    return templates.TemplateResponse("result.html", {"request": request})


# API Endpoints
@app.post("/api/review")
def api_review(jira_key: str, pr_number: int):
    """API endpoint for running review"""
    try:
        result = orchestrator.review(jira_key, pr_number)
        return result.to_dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/demo")
def api_demo():
    """API endpoint for demo review"""
    jira_ticket = JiraTicket(
        key="PROJ-101",
        summary="Password Reset Feature",
        description="Password reset with 15 minute expiry",
        issue_type="Story",
        status="In Review",
    )
    
    pr_diff = PRDiff(
        pr_number=245,
        title="Password reset",
        description="Implementation",
        author="dev",
        branch="feature",
        base_branch="main",
    )
    
    result = orchestrator.review_with_data(jira_ticket, pr_diff)
    return result.to_dict()


@app.get("/history", response_class=HTMLResponse)
def history(request: Request):
    """Review history page - serve React app"""
    from pathlib import Path
    index_path = Path("frontend/dist/index.html")
    if index_path.exists():
        return HTMLResponse(index_path.read_text(encoding='utf-8'))
    return templates.TemplateResponse("history.html", {"request": request, "reviews": recent_reviews})


@app.get("/about", response_class=HTMLResponse)
def about(request: Request):
    """About page - serve React app"""
    from pathlib import Path
    index_path = Path("frontend/dist/index.html")
    if index_path.exists():
        return HTMLResponse(index_path.read_text(encoding='utf-8'))
    return templates.TemplateResponse("about.html", {"request": request})


@app.get("/health")
def health():
    """Health check"""
    return {"status": "ok", "message": "AI PR Reviewer API is running"}


@app.get("/api/history")
def api_history():
    """API endpoint for review history"""
    return recent_reviews


@app.get('/{full_path:path}')
async def serve_react_app(full_path: str):
    """Serve React app for all non-API routes"""
    # Don't interfere with API routes
    if full_path.startswith('api/'):
        raise HTTPException(status_code=404, detail="Not found")
    
    # Read the index.html from the dist folder
    from pathlib import Path
    index_path = Path("frontend/dist/index.html")
    if index_path.exists():
        return HTMLResponse(index_path.read_text(encoding='utf-8'))
    return HTMLResponse("<h1>React app not built</h1>", status_code=500)


if __name__ == "__main__":
    import uvicorn
    print("Starting AI PR Reviewer at http://localhost:5000")
    print("Routes: /, /review, /demo, /history, /about, /api/review, /api/demo")
    uvicorn.run(app, host="0.0.0.0", port=5000)
