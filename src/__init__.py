"""
AI PR Reviewer - Senior Engineer PR Review System

This package provides an AI-powered PR review system that:
- Extracts requirements from Jira tickets
- Analyzes PR diffs
- Maps requirements to code with traceability
- Generates automated tests
- Detects security and performance risks
- Provides a verdict with evidence
"""

__version__ = "1.0.0"
__author__ = "AI PR Reviewer Team"

from src.orchestrator import ReviewOrchestrator
from src.types import ReviewResult, Requirement, CodeMapping, Risk

__all__ = [
    "ReviewOrchestrator",
    "ReviewResult",
    "Requirement",
    "CodeMapping",
    "Risk",
]
