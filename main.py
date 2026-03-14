#!/usr/bin/env python3
"""
AI PR Reviewer - CLI Entry Point

A senior engineer PR review system that:
- Extracts requirements from Jira tickets
- Analyzes PR diffs
- Maps requirements to code with traceability
- Generates automated tests
- Detects security and performance risks
- Provides a verdict with evidence

Usage:
    python main.py --jira PROJ-101 --pr 245
    python main.py --jira PROJ-101 --pr 245 --output report.html
    python main.py --demo
"""

import argparse
import sys
import os
from pathlib import Path

# Load .env file if exists
from dotenv import load_dotenv
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)

# Fix Windows console encoding for emojis
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.orchestrator import ReviewOrchestrator
from src.dashboard import save_html_dashboard
from src.config import load_config


def main():
    parser = argparse.ArgumentParser(
        description="AI PR Reviewer - Senior Engineer PR Review System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --jira PROJ-101 --pr 245
  python main.py --jira PROJ-101 --pr 245 --output dashboard.html
  python main.py --demo
        """
    )
    
    parser.add_argument(
        "--jira", 
        type=str, 
        help="Jira ticket key (e.g., PROJ-101)"
    )
    
    parser.add_argument(
        "--pr", 
        type=int, 
        help="GitHub PR number (e.g., 245)"
    )
    
    parser.add_argument(
        "--output", 
        type=str, 
        default="review_result.html",
        help="Output file for HTML dashboard (default: review_result.html)"
    )
    
    parser.add_argument(
        "--format",
        type=str,
        choices=["json", "dashboard", "html"],
        default="html",
        help="Output format (default: html)"
    )
    
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Run with demo data (no API needed)"
    )
    
    parser.add_argument(
        "--config",
        type=str,
        default="config.yaml",
        help="Path to config file (default: config.yaml)"
    )
    
    args = parser.parse_args()
    
    # Load config
    try:
        config = load_config(args.config)
    except Exception as e:
        print(f"Warning: Could not load config: {e}")
    
    # Initialize orchestrator
    orchestrator = ReviewOrchestrator()
    
    # Run demo or actual review
    if args.demo or (not args.jira and not args.pr):
        print("🎮 Running in demo mode...")
        result = run_demo(orchestrator)
    else:
        if not args.jira or not args.pr:
            parser.error("--jira and --pr are required (or use --demo)")
        
        print(f"🔍 Starting review for {args.jira} / PR #{args.pr}")
        result = orchestrator.review(args.jira, args.pr)
    
    # Output results
    if args.format in ["html", "dashboard"]:
        save_html_dashboard(result, args.output)
        print(f"📊 Dashboard saved to: {args.output}")
    else:
        output = orchestrator.export_result(result, format="json")
        print(output)
    
    # Also print terminal dashboard
    print("\n" + "=" * 60)
    orchestrator.print_dashboard(result)
    
    return 0


def run_demo(orchestrator: ReviewOrchestrator):
    """Run a demo review with mock data"""
    
    from src.types import JiraTicket, PRDiff, DiffFile
    
    # Create demo Jira ticket
    jira_ticket = JiraTicket(
        key="PROJ-101",
        summary="Password Reset Feature Implementation",
        description="""## User Story
As a user, I want to reset my password via email so that I can recover my account.

## Acceptance Criteria
- Password reset link expires in 15 minutes
- Password must be at least 8 characters
- Password must contain at least one uppercase letter
- Password must contain at least one number
- Token should be securely hashed before storage
- User receives email with reset link
- After password reset, all other sessions are invalidated""",
        issue_type="Story",
        status="In Review",
        labels=["security", "authentication"],
    )
    
    # Create demo PR diff
    pr_diff = PRDiff(
        pr_number=245,
        title="Implement password reset feature",
        description="""## Changes Made
- Added password reset token generation with 15-minute expiry
- Added password validation (8+ chars, uppercase, number)
- Added session invalidation on password change""",
        author="developer",
        branch="feature/password-reset",
        base_branch="main",
        files_changed=[
            DiffFile(
                filename="auth/reset.py",
                status="modified",
                additions=45,
                deletions=10,
                patch="""+    def create_reset_link(self, user_id: str) -> str:
+        token = self.generate_token()
+        self.store_token(user_id, token)
+        expiry = datetime.now() + timedelta(minutes=15)
+        return f"https://example.com/reset?token={token}"
+
+    def store_token(self, user_id: str, token: str):
+        db.execute(
+            "INSERT INTO password_resets (user_id, token, created_at) VALUES (?, ?, ?)",
+            (user_id, token, datetime.now())
+        )
+
+    def validate_token(self, token: str) -> bool:
+        result = db.execute(
+            "SELECT created_at FROM password_resets WHERE token = ?",
+            (token,)
+        )
+        if not result:
+            return False
+        created_at = result[0]['created_at']
+        expiry = created_at + timedelta(minutes=15)
+        return datetime.now() < expiry
+
+    def invalidate_sessions(self, user_id: str):
+        db.execute("DELETE FROM sessions WHERE user_id = ?", (user_id,))
""",
            ),
            DiffFile(
                filename="auth/validators.py",
                status="modified",
                additions=20,
                deletions=0,
                patch="""+def validate_password(password: str) -> bool:
+    if len(password) < 8:
+        return False
+    if not any(c.isupper() for c in password):
+        return False
+    if not any(c.isdigit() for c in password):
+        return False
+    return True
""",
            ),
        ],
    )
    
    # Run review with demo data
    return orchestrator.review_with_data(jira_ticket, pr_diff)


if __name__ == "__main__":
    sys.exit(main())
