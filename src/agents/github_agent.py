"""
GitHub Agent - Fetches and analyzes PR diffs
"""

import os
from typing import List, Optional

from src.types import PRDiff, DiffFile
from src.config import get_config
from src.ai_client import get_ai_client, AIClient


class GitHubAgent:
    """Agent for interacting with GitHub and fetching PR diffs"""
    
    def __init__(self, ai_client: Optional[AIClient] = None):
        self.config = get_config()
        self.ai = ai_client or get_ai_client()
        self.github_client = None
        self._init_github_client()
    
    def _init_github_client(self):
        """Initialize GitHub client"""
        if not self.config.github.token:
            return
        
        try:
            import requests
            self.session = requests.Session()
            self.session.headers.update({
                "Authorization": f"token {self.config.github.token}",
                "Accept": "application/vnd.github.v3+json",
            })
        except ImportError:
            pass
    
    def get_pr_diff(self, pr_number: int) -> PRDiff:
        """Fetch PR diff by number"""
        
        if hasattr(self, 'session') and self.session:
            return self._fetch_pr_from_api(pr_number)
        
        return self._get_mock_pr(pr_number)
    
    def _fetch_pr_from_api(self, pr_number: int) -> PRDiff:
        """Fetch PR from GitHub API"""
        base_url = f"https://api.github.com/repos/{self.config.github.owner}/{self.config.github.repo}"
        
        # Get PR info
        pr_response = self.session.get(f"{base_url}/pulls/{pr_number}")
        pr_data = pr_response.json()
        
        # Get PR files
        files_response = self.session.get(f"{base_url}/pulls/{pr_number}/files")
        files_data = files_response.json()
        
        files = []
        for f in files_data:
            diff_file = DiffFile(
                filename=f.get('filename', ''),
                status=f.get('status', 'modified'),
                additions=f.get('additions', 0),
                deletions=f.get('deletions', 0),
                patch=f.get('patch', ''),
            )
            files.append(diff_file)
        
        return PRDiff(
            pr_number=pr_number,
            title=pr_data.get('title', ''),
            description=pr_data.get('body', ''),
            author=pr_data.get('user', {}).get('login', ''),
            branch=pr_data.get('head', {}).get('ref', ''),
            base_branch=pr_data.get('base', {}).get('ref', ''),
            files_changed=files,
        )
    
    def _get_mock_pr(self, pr_number: int) -> PRDiff:
        """Get mock PR for testing/demo"""
        
        # Mock diff files that match a password reset implementation
        files = [
            DiffFile(
                filename="auth/reset.py",
                status="modified",
                additions=45,
                deletions=10,
                patch="""--- a/auth/reset.py
+++ b/auth/reset.py
@@ -80,5 +80,30 @@ class PasswordReset:
     def generate_token(self):
         return secrets.token_urlsafe(32)
 
+    def create_reset_link(self, user_id: str) -> str:
+        token = self.generate_token()
+        # Store token (would need hashing in production)
+        self.store_token(user_id, token)
+        expiry = datetime.now() + timedelta(minutes=15)
+        return f"https://example.com/reset?token={token}"
+
+    def store_token(self, user_id: str, token: str):
+        # Store token in database
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
                patch="""+++ b/auth/validators.py
@@ -0,0 +1,20 @@
+def validate_password(password: str) -> bool:
+    if len(password) < 8:
+        return False
+    if not any(c.isupper() for c in password):
+        return False
+    if not any(c.isdigit() for c in password):
+        return False
+    return True
+
+def get_password_requirements() -> dict:
+    return {
+        "min_length": 8,
+        "require_uppercase": True,
+        "require_number": True,
+    }
""",
            ),
            DiffFile(
                filename="tests/test_password_reset.py",
                status="added",
                additions=30,
                deletions=0,
                patch="""+++ b/tests/test_password_reset.py
+import pytest
+
+def test_password_length():
+    password = "Test1234"
+    assert len(password) >= 8
+
+def test_password_uppercase():
+    password = "Test1234"
+    assert any(c.isupper() for c in password)
""",
            ),
        ]
        
        return PRDiff(
            pr_number=pr_number,
            title="Implement password reset feature",
            description="""## Changes Made
- Added password reset token generation with 15-minute expiry
- Added password validation (8+ chars, uppercase, number)
- Added session invalidation on password change

## Testing
- Unit tests added for password validation
- Manual testing of email flow""",
            author="developer",
            branch="feature/password-reset",
            base_branch="main",
            files_changed=files,
            commit_messages=[
                "Add password reset token generation",
                "Add password validation requirements",
                "Add session invalidation",
            ],
        )
    
    def summarize_diff(self, pr_diff: PRDiff) -> str:
        """Use AI to summarize the PR diff"""
        
        system_prompt = """You are a senior software engineer reviewing a PR diff.
Provide a concise summary of what changed and why."""
        
        files_summary = "\n".join([
            f"- {f.filename}: {f.additions} additions, {f.deletions} deletions"
            for f in pr_diff.files_changed
        ])
        
        prompt = f"""Summarize this PR:

Title: {pr_diff.title}
Description: {pr_diff.description}
Author: {pr_diff.author}
Branch: {pr_diff.branch} -> {pr_diff.base_branch}

Files Changed:
{files_summary}

Provide a 2-3 sentence summary of what this PR does."""
        
        return self.ai.complete(prompt, system_prompt)
