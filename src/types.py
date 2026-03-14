"""
Type definitions for the AI PR Reviewer system
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, List, Dict, Any
from datetime import datetime


class Verdict(str, Enum):
    """Review verdict types"""
    PASS = "PASS"
    PARTIAL = "PARTIAL"
    FAIL = "FAIL"
    NEEDS_REVIEW = "NEEDS_REVIEW"


class RequirementStatus(str, Enum):
    """Status of a requirement in the PR"""
    PASS = "PASS"
    FAIL = "FAIL"
    PARTIAL = "PARTIAL"
    NOT_TESTABLE = "NOT_TESTABLE"


class RiskLevel(str, Enum):
    """Risk severity levels"""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"


class RiskType(str, Enum):
    """Types of risks that can be detected"""
    SECURITY = "SECURITY"
    PERFORMANCE = "PERFORMANCE"
    EDGE_CASE = "EDGE_CASE"
    CODE_QUALITY = "CODE_QUALITY"
    TESTING = "TESTING"


@dataclass
class JiraTicket:
    """Represents a Jira ticket"""
    key: str
    summary: str
    description: str
    issue_type: str
    status: str
    assignee: Optional[str] = None
    labels: List[str] = field(default_factory=list)
    components: List[str] = field(default_factory=list)
    raw_data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Requirement:
    """Represents a single requirement extracted from Jira"""
    id: str
    text: str
    category: str
    priority: str
    acceptance_criteria: List[str] = field(default_factory=list)
    status: RequirementStatus = RequirementStatus.NOT_TESTABLE
    evidence: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "text": self.text,
            "category": self.category,
            "priority": self.priority,
            "acceptance_criteria": self.acceptance_criteria,
            "status": self.status.value,
            "evidence": self.evidence,
        }


@dataclass
class CodeMapping:
    """Maps a requirement to specific code locations"""
    requirement_id: str
    file_path: str
    line_number: int
    code_snippet: str
    description: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "requirement_id": self.requirement_id,
            "file_path": self.file_path,
            "line_number": self.line_number,
            "code_snippet": self.code_snippet,
            "description": self.description,
        }


@dataclass
class DiffFile:
    """Represents a file changed in the PR"""
    filename: str
    status: str  # added, modified, deleted
    additions: int
    deletions: int
    patch: str
    old_content: Optional[str] = None
    new_content: Optional[str] = None


@dataclass
class PRDiff:
    """Represents the PR diff"""
    pr_number: int
    title: str
    description: str
    author: str
    branch: str
    base_branch: str
    files_changed: List[DiffFile] = field(default_factory=list)
    commit_messages: List[str] = field(default_factory=list)
    
    @property
    def total_additions(self) -> int:
        return sum(f.additions for f in self.files_changed)
    
    @property
    def total_deletions(self) -> int:
        return sum(f.deletions for f in self.files_changed)


@dataclass
class Risk:
    """Represents a detected risk"""
    type: RiskType
    level: RiskLevel
    title: str
    description: str
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    suggestion: Optional[str] = None
    cwe_id: Optional[str] = None  # Common Weakness Enumeration
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type.value,
            "level": self.level.value,
            "title": self.title,
            "description": self.description,
            "file_path": self.file_path,
            "line_number": self.line_number,
            "suggestion": self.suggestion,
            "cwe_id": self.cwe_id,
        }


@dataclass
class GeneratedTest:
    """Represents an AI-generated test"""
    name: str
    requirement_id: str
    test_code: str
    framework: str
    passed: Optional[bool] = None
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "requirement_id": self.requirement_id,
            "test_code": self.test_code,
            "framework": self.framework,
            "passed": self.passed,
            "error": self.error,
        }


@dataclass
class ReviewResult:
    """Final review result"""
    jira_ticket: JiraTicket
    pr_diff: PRDiff
    requirements: List[Requirement] = field(default_factory=list)
    code_mappings: List[CodeMapping] = field(default_factory=list)
    risks: List[Risk] = field(default_factory=list)
    generated_tests: List[GeneratedTest] = field(default_factory=list)
    verdict: Verdict = Verdict.NEEDS_REVIEW
    summary: str = ""
    suggestions: List[str] = field(default_factory=list)
    reviewed_at: datetime = field(default_factory=datetime.now)
    
    @property
    def passed_requirements(self) -> int:
        return sum(1 for r in self.requirements if r.status == RequirementStatus.PASS)
    
    @property
    def failed_requirements(self) -> int:
        return sum(1 for r in self.requirements if r.status == RequirementStatus.FAIL)
    
    @property
    def critical_risks(self) -> int:
        return sum(1 for r in self.risks if r.level == RiskLevel.CRITICAL)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "jira_ticket": {
                "key": self.jira_ticket.key,
                "summary": self.jira_ticket.summary,
                "description": self.jira_ticket.description,
            },
            "pr_diff": {
                "pr_number": self.pr_diff.pr_number,
                "title": self.pr_diff.title,
                "author": self.pr_diff.author,
                "files_changed": len(self.pr_diff.files_changed),
            },
            "requirements": [r.to_dict() for r in self.requirements],
            "code_mappings": [c.to_dict() for c in self.code_mappings],
            "risks": [r.to_dict() for r in self.risks],
            "generated_tests": [t.to_dict() for t in self.generated_tests],
            "verdict": self.verdict.value,
            "summary": self.summary,
            "suggestions": self.suggestions,
            "reviewed_at": self.reviewed_at.isoformat(),
            "stats": {
                "passed_requirements": self.passed_requirements,
                "failed_requirements": self.failed_requirements,
                "critical_risks": self.critical_risks,
                "total_risks": len(self.risks),
            },
        }
