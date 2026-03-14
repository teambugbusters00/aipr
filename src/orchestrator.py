"""
Review Orchestrator - Coordinates all agents for PR review
"""

import json
from typing import Optional

from src.types import ReviewResult, JiraTicket, PRDiff
from src.agents.jira_agent import JiraAgent
from src.agents.github_agent import GitHubAgent
from src.analyzer import CodeAnalyzer
from src.test_generator import TestGenerator
from src.verdict_agent import VerdictAgent
from src.config import get_config
from src.ai_client import get_ai_client, AIClient


class ReviewOrchestrator:
    """
    Main orchestrator that coordinates all agents to perform a complete PR review.
    
    Flow:
    1. Jira Agent - Extract requirements from Jira ticket
    2. GitHub Agent - Fetch PR diff
    3. Code Analyzer - Map requirements to code, detect risks
    4. Test Generator - Generate tests for requirements
    5. Verdict Agent - Generate final verdict with evidence
    """
    
    def __init__(self, ai_client: Optional[AIClient] = None):
        self.config = get_config()
        self.ai = ai_client or get_ai_client()
        
        # Initialize all agents
        self.jira_agent = JiraAgent(ai_client=self.ai)
        self.github_agent = GitHubAgent(ai_client=self.ai)
        self.code_analyzer = CodeAnalyzer(ai_client=self.ai)
        self.test_generator = TestGenerator(ai_client=self.ai)
        self.verdict_agent = VerdictAgent(ai_client=self.ai)
    
    def review(self, jira_key: str, pr_number: int) -> ReviewResult:
        """
        Perform a complete PR review.
        
        Args:
            jira_key: Jira ticket key (e.g., "PROJ-101")
            pr_number: GitHub PR number
            
        Returns:
            ReviewResult with complete analysis
        """
        
        print(f"🔍 Starting review for {jira_key} / PR #{pr_number}")
        
        # Step 1: Fetch Jira ticket
        print("📋 Fetching Jira ticket...")
        jira_ticket = self.jira_agent.get_ticket(jira_key)
        
        # Step 2: Extract requirements
        print("📝 Extracting requirements...")
        requirements = self.jira_agent.extract_requirements(jira_ticket)
        
        # Step 3: Fetch PR diff
        print("📦 Fetching PR diff...")
        pr_diff = self.github_agent.get_pr_diff(pr_number)
        
        # Step 4: Map requirements to code
        print("🔗 Mapping requirements to code...")
        code_mappings = self.code_analyzer.map_requirements_to_code(
            requirements, pr_diff
        )
        
        # Step 5: Detect risks
        print("⚠️ Detecting risks...")
        risks = self.code_analyzer.detect_risks(pr_diff)
        
        # Step 6: Generate tests
        print("🧪 Generating tests...")
        generated_tests = self.test_generator.generate_tests(requirements, pr_diff)
        
        # Step 7: Generate verdict
        print("🎯 Generating verdict...")
        result = self.verdict_agent.generate_verdict(
            jira_ticket=jira_ticket,
            pr_diff=pr_diff,
            requirements=requirements,
            code_mappings=code_mappings,
            risks=risks,
            generated_tests=generated_tests,
        )
        
        print("✅ Review complete!")
        
        return result
    
    def review_with_data(
        self,
        jira_ticket: JiraTicket,
        pr_diff: PRDiff,
    ) -> ReviewResult:
        """
        Perform review with pre-fetched data.
        """
        
        # Extract requirements
        requirements = self.jira_agent.extract_requirements(jira_ticket)
        
        # Map requirements to code
        code_mappings = self.code_analyzer.map_requirements_to_code(
            requirements, pr_diff
        )
        
        # Detect risks
        risks = self.code_analyzer.detect_risks(pr_diff)
        
        # Generate tests
        generated_tests = self.test_generator.generate_tests(requirements, pr_diff)
        
        # Generate verdict
        result = self.verdict_agent.generate_verdict(
            jira_ticket=jira_ticket,
            pr_diff=pr_diff,
            requirements=requirements,
            code_mappings=code_mappings,
            risks=risks,
            generated_tests=generated_tests,
        )
        
        return result
    
    def export_result(self, result: ReviewResult, format: str = "json") -> str:
        """
        Export review result in specified format.
        
        Args:
            result: ReviewResult to export
            format: Output format (json, dashboard)
            
        Returns:
            Formatted string
        """
        
        if format == "json":
            return json.dumps(result.to_dict(), indent=2)
        
        elif format == "dashboard":
            return self.verdict_agent.format_dashboard(result)
        
        else:
            raise ValueError(f"Unknown format: {format}")
    
    def save_result(self, result: ReviewResult, filepath: str) -> None:
        """Save review result to file"""
        
        with open(filepath, 'w') as f:
            f.write(self.export_result(result))
    
    def print_dashboard(self, result: ReviewResult) -> None:
        """Print review result as dashboard"""
        
        print(self.verdict_agent.format_dashboard(result))
        
        # Print detailed requirement mapping
        print("\n📍 Requirement → Code Mapping:")
        print("-" * 40)
        for mapping in result.code_mappings:
            print(f"\n{mapping.requirement_id}: {mapping.file_path}:{mapping.line_number}")
            print(f"  {mapping.description}")
        
        # Print generated tests
        if result.generated_tests:
            print("\n🧪 Generated Tests:")
            print("-" * 40)
            for test in result.generated_tests:
                print(f"\n{test.name} ({test.framework})")
                print(f"```python")
                print(test.test_code)
                print(f"```")
