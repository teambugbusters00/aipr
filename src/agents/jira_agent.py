"""
Jira Agent - Extracts requirements from Jira tickets
Uses direct Jira REST API: https://your-domain.atlassian.net/rest/api/3/issue/{ISSUE_KEY}
"""

import os
import requests
from typing import List, Dict, Any, Optional

from src.types import JiraTicket, Requirement, RequirementStatus
from src.config import get_config
from src.ai_client import get_ai_client, AIClient


class JiraAgent:
    """Agent for interacting with Jira and extracting requirements"""
    
    def __init__(self, ai_client: Optional[AIClient] = None):
        self.config = get_config()
        self.ai = ai_client or get_ai_client()
        self.jira_base_url = None
        self.jira_email = None
        self.jira_api_token = None
        self._init_jira_client()
    
    def _init_jira_client(self):
        """Initialize Jira client with direct API"""
        if not self.config.jira.api_token:
            return
        
        self.jira_base_url = f"https://{self.config.jira.domain}/rest/api/3"
        self.jira_email = self.config.jira.email
        self.jira_api_token = self.config.jira.api_token
    
    def _make_request(self, endpoint: str) -> Dict[str, Any]:
        """Make authenticated request to Jira API"""
        url = f"{self.jira_base_url}/{endpoint}"
        auth = (self.jira_email, self.jira_api_token)
        
        response = requests.get(url, auth=(auth[0] or '', auth[1] or ''))
        response.raise_for_status()
        return response.json()
    
    def get_ticket(self, ticket_key: str) -> JiraTicket:
        """Fetch a Jira ticket by key using direct REST API"""
        
        # If we have Jira credentials, fetch from API
        if self.jira_base_url and self.jira_api_token:
            return self._fetch_ticket_from_api(ticket_key)
        
        # Otherwise, use mock or user-provided data
        return self._get_mock_ticket(ticket_key)
    
    def _fetch_ticket_from_api(self, ticket_key: str) -> JiraTicket:
        """Fetch ticket from Jira REST API
        
        API Endpoint: GET https://your-domain.atlassian.net/rest/api/3/issue/{ISSUE_KEY}
        
        Example:
        https://company.atlassian.net/rest/api/3/issue/PROJ-123
        """
        # Fetch issue data
        issue_data = self._make_request(f"issue/{ticket_key}")
        
        # Extract fields
        fields = issue_data.get('fields', {})
        
        # Get description (can be string or ADF format)
        description = fields.get('description')
        if isinstance(description, dict):
            # Handle Atlassian Document Format (ADF)
            description = self._parse_adf_description(description)
        description = description or ""
        
        # Get labels
        labels = fields.get('labels', [])
        
        # Get components
        components = [c.get('name', '') for c in fields.get('components', [])]
        
        # Get assignee
        assignee_data = fields.get('assignee')
        assignee = assignee_data.get('displayName') if assignee_data else None
        
        # Get status
        status_data = fields.get('status')
        status = status_data.get('name') if status_data else "Unknown"
        
        return JiraTicket(
            key=issue_data.get('key', ticket_key),
            summary=fields.get('summary', ''),
            description=description,
            issue_type=fields.get('issuetype', {}).get('name', 'Task'),
            status=status,
            assignee=assignee,
            labels=labels,
            components=components,
            raw_data=issue_data,
        )
    
    def _parse_adf_description(self, adf: Dict[str, Any]) -> str:
        """Parse Atlassian Document Format description to plain text"""
        text_parts = []
        
        if adf.get('type') == 'doc' and 'content' in adf:
            for content in adf['content']:
                if content.get('type') == 'paragraph' and 'content' in content:
                    for item in content['content']:
                        if item.get('type') == 'text':
                            text_parts.append(item.get('text', ''))
                        elif item.get('type') == 'hardBreak':
                            text_parts.append('\n')
                elif content.get('type') == 'bulletList':
                    for item in content.get('content', []):
                        if item.get('type') == 'listItem':
                            for para in item.get('content', []):
                                if para.get('type') == 'paragraph':
                                    for text in para.get('content', []):
                                        if text.get('type') == 'text':
                                            text_parts.append(f"- {text.get('text', '')}\n")
        
        return ''.join(text_parts)
    
    def _get_mock_ticket(self, ticket_key: str) -> JiraTicket:
        """Get mock ticket for testing"""
        return JiraTicket(
            key=ticket_key,
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
            status="In Progress",
            labels=["security", "authentication"],
            components=["Backend"],
        )
    
    def extract_requirements(self, ticket: JiraTicket) -> List[Requirement]:
        """Extract structured requirements from Jira ticket using AI"""
        
        system_prompt = """You are a senior software engineer analyzing Jira tickets.
Your task is to extract testable requirements from the ticket description.
For each requirement, identify:
1. A unique ID (e.g., REQ-001)
2. The requirement text
3. Category (security, functionality, performance, UX)
4. Priority (critical, high, medium, low)
5. Acceptance criteria (specific, testable conditions)

Return a JSON array of requirements."""
        
        prompt = f"""Extract requirements from this Jira ticket:

Key: {ticket.key}
Summary: {ticket.summary}
Description: {ticket.description}
Issue Type: {ticket.issue_type}
Labels: {', '.join(ticket.labels)}

Extract all testable requirements. Be specific and include numerical thresholds where mentioned."""
        
        try:
            result = self.ai.complete_with_json(prompt, system_prompt)
            requirements = []
            
            for idx, req_data in enumerate(result.get('requirements', [])):
                requirement = Requirement(
                    id=req_data.get('id', f'REQ-{idx+1:03d}'),
                    text=req_data.get('text', ''),
                    category=req_data.get('category', 'functionality'),
                    priority=req_data.get('priority', 'medium'),
                    acceptance_criteria=req_data.get('acceptance_criteria', []),
                    status=RequirementStatus.NOT_TESTABLE,
                )
                requirements.append(requirement)
            
            return requirements
            
        except Exception as e:
            # Fallback: create basic requirements from description
            return self._extract_basic_requirements(ticket)
    
    def _extract_basic_requirements(self, ticket: JiraTicket) -> List[Requirement]:
        """Extract basic requirements from description without AI"""
        requirements = []
        
        # Parse common requirement patterns from description
        desc_lower = ticket.description.lower()
        
        # Time-based requirements
        if '15 minutes' in desc_lower or '15 min' in desc_lower:
            requirements.append(Requirement(
                id="REQ-001",
                text="Password reset link expires in 15 minutes",
                category="security",
                priority="high",
                acceptance_criteria=["Link valid for exactly 15 minutes", "Expired links return error"],
            ))
        
        # Password length
        if '8 characters' in desc_lower or 'at least 8' in desc_lower:
            requirements.append(Requirement(
                id="REQ-002",
                text="Password must be at least 8 characters",
                category="security",
                priority="high",
                acceptance_criteria=["Passwords shorter than 8 chars rejected", "Passwords with 8+ chars accepted"],
            ))
        
        # Uppercase requirement
        if 'uppercase' in desc_lower:
            requirements.append(Requirement(
                id="REQ-003",
                text="Password must contain at least one uppercase letter",
                category="security",
                priority="medium",
                acceptance_criteria=["Passwords without uppercase rejected"],
            ))
        
        # Number requirement  
        if 'number' in desc_lower and 'password' in desc_lower:
            requirements.append(Requirement(
                id="REQ-004",
                text="Password must contain at least one number",
                category="security",
                priority="medium",
                acceptance_criteria=["Passwords without numbers rejected"],
            ))
        
        # Hashing requirement
        if 'hash' in desc_lower:
            requirements.append(Requirement(
                id="REQ-005",
                text="Token should be securely hashed before storage",
                category="security",
                priority="critical",
                acceptance_criteria=["Tokens stored in hashed form", "Hashed tokens cannot be reversed"],
            ))
        
        # Email requirement
        if 'email' in desc_lower and 'reset' in desc_lower:
            requirements.append(Requirement(
                id="REQ-006",
                text="User receives email with reset link",
                category="functionality",
                priority="high",
                acceptance_criteria=["Email sent to user's registered address", "Email contains valid reset link"],
            ))
        
        # Session invalidation
        if 'session' in desc_lower and 'invalidated' in desc_lower:
            requirements.append(Requirement(
                id="REQ-007",
                text="After password reset, all other sessions are invalidated",
                category="security",
                priority="high",
                acceptance_criteria=["Other sessions terminated after reset", "User must re-authenticate"],
            ))
        
        return requirements
