"""
Configuration management for AI PR Reviewer
"""

import os
import yaml
from dataclasses import dataclass
from typing import Optional, Dict, Any


@dataclass
class JiraConfig:
    """Jira configuration"""
    domain: str
    email: str
    api_token: Optional[str] = None


@dataclass
class GitHubConfig:
    """GitHub configuration"""
    owner: str
    repo: str
    token: Optional[str] = None


@dataclass
class AIConfig:
    """AI model configuration"""
    model: str = "gpt-4"
    temperature: float = 0.3
    max_tokens: int = 4000


@dataclass
class AnalysisConfig:
    """Analysis settings"""
    max_diff_lines: int = 10000
    include_comments: bool = True
    detect_security_risks: bool = True
    detect_performance_issues: bool = True


@dataclass
class TestConfig:
    """Test generation settings"""
    framework: str = "pytest"
    output_dir: str = "generated_tests"
    auto_run: bool = False


@dataclass
class Config:
    """Main configuration"""
    jira: JiraConfig
    github: GitHubConfig
    ai: AIConfig
    analysis: AnalysisConfig
    tests: TestConfig


def load_config(config_path: str = "config.yaml") -> Config:
    """Load configuration from YAML file"""
    
    # Try to load from file
    config_data = {}
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            config_data = yaml.safe_load(f) or {}
    
    # Jira config
    jira_data = config_data.get('jira', {})
    jira = JiraConfig(
        domain=jira_data.get('domain', ''),
        email=jira_data.get('email', ''),
        api_token=os.environ.get('JIRA_API_TOKEN'),
    )
    
    # GitHub config
    github_data = config_data.get('github', {})
    github = GitHubConfig(
        owner=github_data.get('owner', ''),
        repo=github_data.get('repo', ''),
        token=os.environ.get('GITHUB_TOKEN'),
    )
    
    # AI config
    ai_data = config_data.get('ai', {})
    ai = AIConfig(
        model=ai_data.get('model', 'gpt-4'),
        temperature=ai_data.get('temperature', 0.3),
        max_tokens=ai_data.get('max_tokens', 4000),
    )
    
    # Analysis config
    analysis_data = config_data.get('analysis', {})
    analysis = AnalysisConfig(
        max_diff_lines=analysis_data.get('max_diff_lines', 10000),
        include_comments=analysis_data.get('include_comments', True),
        detect_security_risks=analysis_data.get('detect_security_risks', True),
        detect_performance_issues=analysis_data.get('detect_performance_issues', True),
    )
    
    # Test config
    test_data = config_data.get('tests', {})
    tests = TestConfig(
        framework=test_data.get('framework', 'pytest'),
        output_dir=test_data.get('output_dir', 'generated_tests'),
        auto_run=test_data.get('auto_run', False),
    )
    
    return Config(
        jira=jira,
        github=github,
        ai=ai,
        analysis=analysis,
        tests=tests,
    )


# Global config instance
_config: Optional[Config] = None


def get_config() -> Config:
    """Get global config instance"""
    global _config
    if _config is None:
        _config = load_config()
    return _config


def set_config(config: Config) -> None:
    """Set global config instance"""
    global _config
    _config = config
