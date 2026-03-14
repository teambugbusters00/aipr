"""
Verdict Agent - Generates final review verdict with evidence
"""

from typing import List, Optional

from src.types import (
    ReviewResult, Verdict, Requirement, RequirementStatus,
    CodeMapping, Risk, RiskLevel, GeneratedTest, JiraTicket, PRDiff
)
from src.config import get_config
from src.ai_client import get_ai_client, AIClient


class VerdictAgent:
    """Generates the final review verdict with evidence"""
    
    def __init__(self, ai_client: Optional[AIClient] = None):
        self.config = get_config()
        self.ai = ai_client or get_ai_client()
    
    def generate_verdict(
        self,
        jira_ticket: JiraTicket,
        pr_diff: PRDiff,
        requirements: List[Requirement],
        code_mappings: List[CodeMapping],
        risks: List[Risk],
        generated_tests: List[GeneratedTest],
    ) -> ReviewResult:
        """Generate final review result with verdict"""
        
        # Calculate overall verdict
        verdict = self._calculate_verdict(requirements, risks)
        
        # Generate summary and suggestions
        summary = self._generate_summary(
            jira_ticket, pr_diff, requirements, risks
        )
        
        suggestions = self._generate_suggestions(
            requirements, risks, code_mappings
        )
        
        return ReviewResult(
            jira_ticket=jira_ticket,
            pr_diff=pr_diff,
            requirements=requirements,
            code_mappings=code_mappings,
            risks=risks,
            generated_tests=generated_tests,
            verdict=verdict,
            summary=summary,
            suggestions=suggestions,
        )
    
    def _calculate_verdict(
        self, 
        requirements: List[Requirement], 
        risks: List[Risk]
    ) -> Verdict:
        """Calculate the overall verdict based on requirements and risks"""
        
        # Check for critical risks
        critical_risks = [r for r in risks if r.level == RiskLevel.CRITICAL]
        if critical_risks:
            return Verdict.FAIL
        
        # Check requirements
        passed = sum(1 for r in requirements if r.status == RequirementStatus.PASS)
        failed = sum(1 for r in requirements if r.status == RequirementStatus.FAIL)
        partial = sum(1 for r in requirements if r.status == RequirementStatus.PARTIAL)
        total = len(requirements)
        
        if total == 0:
            return Verdict.NEEDS_REVIEW
        
        pass_rate = passed / total
        
        # High risks automatically downgrades verdict
        high_risks = [r for r in risks if r.level == RiskLevel.HIGH]
        if high_risks:
            if pass_rate < 0.5:
                return Verdict.FAIL
            return Verdict.PARTIAL
        
        # Determine based on pass rate
        if pass_rate >= 0.8 and failed == 0:
            return Verdict.PASS
        elif pass_rate >= 0.5:
            return Verdict.PARTIAL
        else:
            return Verdict.FAIL
    
    def _generate_summary(
        self,
        jira_ticket: JiraTicket,
        pr_diff: PRDiff,
        requirements: List[Requirement],
        risks: List[Risk],
    ) -> str:
        """Generate a summary of the review"""
        
        # Try AI-generated summary first
        try:
            system_prompt = """You are a senior engineer providing a PR review summary.
Keep it concise and professional."""
            
            passed = sum(1 for r in requirements if r.status == RequirementStatus.PASS)
            failed = sum(1 for r in requirements if r.status == RequirementStatus.FAIL)
            
            prompt = f"""Generate a 2-3 sentence summary of this PR review:

Jira Ticket: {jira_ticket.key} - {jira_ticket.summary}
PR: #{pr_diff.pr_number} - {pr_diff.title}
Author: {pr_diff.author}

Requirements: {passed} passed, {failed} failed out of {len(requirements)} total
Risks: {len(risks)} detected ({sum(1 for r in risks if r.level == RiskLevel.CRITICAL)} critical)

Provide a concise summary."""
            
            return self.ai.complete(prompt, system_prompt)
            
        except Exception:
            # Fallback to template summary
            passed = sum(1 for r in requirements if r.status == RequirementStatus.PASS)
            failed = sum(1 for r in requirements if r.status == RequirementStatus.FAIL)
            
            return (
                f"PR #{pr_diff.pr_number} addresses {len(requirements)} requirements from "
                f"{jira_ticket.key}. {passed} requirements verified, {failed} missing. "
                f"{len(risks)} risks identified."
            )
    
    def _generate_suggestions(
        self,
        requirements: List[Requirement],
        risks: List[Risk],
        code_mappings: List[CodeMapping],
    ) -> List[str]:
        """Generate actionable suggestions based on the review"""
        
        suggestions = []
        
        # Suggestions for failed requirements
        failed_requirements = [r for r in requirements if r.status == RequirementStatus.FAIL]
        if failed_requirements:
            suggestions.append(
                f"Implement {len(failed_requirements)} missing requirements: "
                f"{', '.join(r.id for r in failed_requirements)}"
            )
        
        # Suggestions for risks
        critical_risks = [r for r in risks if r.level == RiskLevel.CRITICAL]
        high_risks = [r for r in risks if r.level == RiskLevel.HIGH]
        
        if critical_risks:
            suggestions.append(
                f"Address {len(critical_risks)} critical security issues before merging"
            )
        
        if high_risks:
            for risk in high_risks[:3]:  # Top 3
                if risk.suggestion:
                    suggestions.append(f"Risk: {risk.title} - {risk.suggestion}")
        
        # Suggestions for partial requirements
        partial_requirements = [r for r in requirements if r.status == RequirementStatus.PARTIAL]
        if partial_requirements:
            suggestions.append(
                f"Complete partial implementation for: "
                f"{', '.join(r.id for r in partial_requirements)}"
            )
        
        return suggestions[:5]  # Limit to 5 suggestions
    
    def format_dashboard(self, result: ReviewResult) -> str:
        """Format the review result as a dashboard"""
        
        lines = []
        lines.append("=" * 60)
        lines.append(f" AI PR Reviewer - Dashboard")
        lines.append("=" * 60)
        lines.append("")
        
        # Header
        lines.append(f"Jira Ticket: {result.jira_ticket.key}")
        lines.append(f"GitHub PR: #{result.pr_diff.pr_number}")
        lines.append("")
        lines.append("-" * 60)
        
        # Verdict
        verdict_emoji = {
            Verdict.PASS: "✅",
            Verdict.PARTIAL: "⚠️",
            Verdict.FAIL: "❌",
            Verdict.NEEDS_REVIEW: "🔍",
        }
        lines.append(f"Overall Verdict: {verdict_emoji.get(result.verdict, '')} {result.verdict.value}")
        lines.append("")
        
        # Requirements Summary
        lines.append("Requirement Analysis")
        for req in result.requirements:
            status_icon = {
                RequirementStatus.PASS: "✔",
                RequirementStatus.FAIL: "✘",
                RequirementStatus.PARTIAL: "◐",
                RequirementStatus.NOT_TESTABLE: "○",
            }
            lines.append(f"  {status_icon.get(req.status, '')} {req.id}: {req.text[:50]}...")
        
        lines.append("")
        
        # Risks
        if result.risks:
            lines.append("Detected Issues")
            for risk in result.risks:
                level_icon = {
                    RiskLevel.CRITICAL: "🔴",
                    RiskLevel.HIGH: "🟠",
                    RiskLevel.MEDIUM: "🟡",
                    RiskLevel.LOW: "🔵",
                    RiskLevel.INFO: "⚪",
                }
                lines.append(f"  {level_icon.get(risk.level, '')} {risk.title}")
                if risk.file_path:
                    lines.append(f"    → {risk.file_path}")
            lines.append("")
        
        # Suggestions
        if result.suggestions:
            lines.append("Suggested Fixes")
            for i, suggestion in enumerate(result.suggestions, 1):
                lines.append(f"  {i}. {suggestion}")
            lines.append("")
        
        lines.append("-" * 60)
        lines.append(f"Reviewed at: {result.reviewed_at.strftime('%Y-%m-%d %H:%M:%S')}")
        
        return "\n".join(lines)
