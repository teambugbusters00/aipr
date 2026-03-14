"""
Code Analyzer - Analyzes code structure and maps requirements to code
"""

import re
from typing import List, Dict, Any, Optional, Tuple

from src.types import Requirement, CodeMapping, Risk, RiskLevel, RiskType, PRDiff, DiffFile, RequirementStatus
from src.config import get_config
from src.ai_client import get_ai_client, AIClient


class CodeAnalyzer:
    """Analyzes code and maps requirements to specific code locations"""
    
    def __init__(self, ai_client: Optional[AIClient] = None):
        self.config = get_config()
        self.ai = ai_client or get_ai_client()
    
    def map_requirements_to_code(
        self, 
        requirements: List[Requirement], 
        pr_diff: PRDiff
    ) -> List[CodeMapping]:
        """Map each requirement to code evidence in the PR diff"""
        
        mappings = []
        
        for requirement in requirements:
            requirement_mappings = self._map_single_requirement(requirement, pr_diff)
            mappings.extend(requirement_mappings)
            
            # Update requirement status based on findings
            if requirement_mappings:
                requirement.status = RequirementStatus.PASS
                requirement.evidence = [m.description for m in requirement_mappings]
            else:
                requirement.status = RequirementStatus.FAIL
                requirement.evidence = ["No code evidence found in PR"]
        
        return mappings
    
    def _map_single_requirement(
        self, 
        requirement: Requirement, 
        pr_diff: PRDiff
    ) -> List[CodeMapping]:
        """Map a single requirement to code using pattern matching and AI"""
        
        mappings = []
        req_text = requirement.text.lower()
        
        # Define patterns to search for based on requirement keywords
        search_patterns = self._get_search_patterns(requirement)
        
        for diff_file in pr_diff.files_changed:
            patch = diff_file.patch
            
            for pattern_name, pattern in search_patterns.items():
                matches = list(re.finditer(pattern, patch, re.IGNORECASE | re.MULTILINE))
                
                for match in matches:
                    # Extract context around the match
                    start = max(0, match.start() - 100)
                    end = min(len(patch), match.end() + 100)
                    context = patch[start:end]
                    
                    # Calculate line number (approximate)
                    line_number = patch[:match.start()].count('\n') + 1
                    
                    mapping = CodeMapping(
                        requirement_id=requirement.id,
                        file_path=diff_file.filename,
                        line_number=line_number,
                        code_snippet=context.strip(),
                        description=f"Found {pattern_name} in {diff_file.filename}",
                    )
                    mappings.append(mapping)
        
        # If no pattern matches, try AI-assisted mapping
        if not mappings:
            mappings = self._ai_map_requirement(requirement, pr_diff)
        
        return mappings
    
    def _get_search_patterns(self, requirement: Requirement) -> Dict[str, str]:
        """Get search patterns based on requirement keywords"""
        
        req_text = requirement.text.lower()
        patterns = {}
        
        # Time-based patterns (e.g., 15 minutes)
        if 'minute' in req_text or 'expir' in req_text:
            time_match = re.search(r'(\d+)\s*minute', req_text)
            if time_match:
                minutes = time_match.group(1)
                patterns['expiry_time'] = rf'(?:timedelta|minutes|expires?).*{minutes}'
                patterns['expiry_check'] = rf'(?:expiry|valid|now\s*<|datetime\.now\(\)).*{minutes}'
        
        # Password length patterns
        if '8' in req_text and ('character' in req_text or 'length' in req_text):
            patterns['length_check'] = r'len\([^)]+\)\s*[><=]+\s*\d+'
            patterns['min_length'] = r'min[_ ]?length["\']?\s*[:=]\s*\d+'
        
        # Uppercase patterns
        if 'uppercase' in req_text or 'upper' in req_text:
            patterns['uppercase'] = r'(?:isupper|upper|uppercase)'
        
        # Number/digit patterns
        if 'number' in req_text or 'digit' in req_text or 'numeric' in req_text:
            patterns['number'] = r'(?:isdigit|isnumeric|any\(.*isdigit)'
        
        # Hashing patterns
        if 'hash' in req_text:
            patterns['hashing'] = r'(?:hash|hashlib|bcrypt|argon2|pbkdf2)'
        
        # Email patterns
        if 'email' in req_text:
            patterns['email'] = r'(?:email|send.*mail|smtp)'
        
        # Session patterns
        if 'session' in req_text and ('invalidat' in req_text or 'terminat' in req_text):
            patterns['session_invalidation'] = r'(?:session).*(?:delete|invalidate|remove|clear)'
        
        return patterns
    
    def _ai_map_requirement(
        self, 
        requirement: Requirement, 
        pr_diff: PRDiff
    ) -> List[CodeMapping]:
        """Use AI to find code evidence for a requirement"""
        
        system_prompt = """You are a code analyzer. Given a requirement and a PR diff,
find specific code that implements or relates to that requirement.
Return a JSON array of findings with: file_path, line_number (approximate), code_snippet, description."""
        
        diff_text = self._format_diff_for_ai(pr_diff)
        
        prompt = f"""Find code that satisfies this requirement:

Requirement: {requirement.text}
ID: {requirement.id}

PR Diff:
{diff_text}

Look for code that implements the requirement. Be specific about file names and line numbers."""
        
        try:
            result = self.ai.complete_with_json(prompt, system_prompt)
            findings = result.get('findings', [])
            
            mappings = []
            for finding in findings:
                mapping = CodeMapping(
                    requirement_id=requirement.id,
                    file_path=finding.get('file_path', ''),
                    line_number=finding.get('line_number', 1),
                    code_snippet=finding.get('code_snippet', ''),
                    description=finding.get('description', ''),
                )
                mappings.append(mapping)
            
            return mappings
            
        except Exception:
            return []
    
    def _format_diff_for_ai(self, pr_diff: PRDiff) -> str:
        """Format PR diff for AI consumption"""
        
        lines = []
        for f in pr_diff.files_changed:
            lines.append(f"=== {f.filename} ({f.status}) ===")
            # Just show first 50 lines of patch to avoid token limits
            patch_lines = f.patch.split('\n')[:50]
            lines.extend(patch_lines)
            lines.append("")
        
        return '\n'.join(lines)
    
    def detect_risks(self, pr_diff: PRDiff) -> List[Risk]:
        """Detect security and performance risks in the PR diff"""
        
        risks = []
        
        # Pattern-based risk detection
        for diff_file in pr_diff.files_changed:
            file_risks = self._detect_file_risks(diff_file)
            risks.extend(file_risks)
        
        # AI-powered risk detection
        ai_risks = self._ai_detect_risks(pr_diff)
        risks.extend(ai_risks)
        
        return risks
    
    def _detect_file_risks(self, diff_file: DiffFile) -> List[Risk]:
        """Detect risks in a single file"""
        
        risks = []
        patch = diff_file.patch
        filename = diff_file.filename
        
        # Security risk: Plaintext password/token storage
        if re.search(r'password.*=.*["\'](?!hashed|hash|bcrypt)', patch, re.I):
            risks.append(Risk(
                type=RiskType.SECURITY,
                level=RiskLevel.HIGH,
                title="Potential plaintext password storage",
                description="Found potential plaintext password assignment. Use secure hashing.",
                file_path=filename,
                suggestion="Use bcrypt or Argon2 for password hashing",
                cwe_id="CWE-916",
            ))
        
        # Security risk: Token not hashed
        if re.search(r'token.*=.*["\']', patch, re.I) and not re.search(r'hash', patch, re.I):
            risks.append(Risk(
                type=RiskType.SECURITY,
                level=RiskLevel.HIGH,
                title="Token stored without hashing",
                description="Reset token stored in plaintext. Should be hashed before storage.",
                file_path=filename,
                suggestion="Hash tokens using hashlib before storing",
                cwe_id="CWE-916",
            ))
        
        # Security risk: SQL injection potential
        if re.search(r'execute.*\%s.*\+', patch, re.I):
            risks.append(Risk(
                type=RiskType.SECURITY,
                level=RiskLevel.CRITICAL,
                title="Potential SQL injection vulnerability",
                description="String concatenation in SQL query could lead to SQL injection.",
                file_path=filename,
                suggestion="Use parameterized queries exclusively",
                cwe_id="CWE-89",
            ))
        
        # Performance risk: N+1 query pattern
        if re.search(r'for .* in .*:\s*.*execute', patch, re.MULTILINE):
            risks.append(Risk(
                type=RiskType.PERFORMANCE,
                level=RiskLevel.MEDIUM,
                title="Potential N+1 query pattern",
                description="Loop with database queries could cause performance issues.",
                file_path=filename,
                suggestion="Use bulk operations or JOINs instead of loops",
            ))
        
        # Edge case: No validation
        if 'validate' not in patch.lower() and 'check' not in patch.lower():
            if diff_file.status == 'added':
                risks.append(Risk(
                    type=RiskType.EDGE_CASE,
                    level=RiskLevel.LOW,
                    title="Missing input validation",
                    description="New file added without obvious validation logic.",
                    file_path=filename,
                    suggestion="Add input validation",
                ))
        
        # Testing risk: No test coverage
        if not filename.startswith('test') and not filename.startswith('tests/'):
            if diff_file.status == 'added' and 'def ' in patch:
                # Check if corresponding test exists
                risks.append(Risk(
                    type=RiskType.TESTING,
                    level=RiskLevel.INFO,
                    title="New function without tests",
                    description=f"Added {filename} but no test file found.",
                    file_path=filename,
                    suggestion="Add unit tests for new functionality",
                ))
        
        return risks
    
    def _ai_detect_risks(self, pr_diff: PRDiff) -> List[Risk]:
        """Use AI to detect additional risks"""
        
        system_prompt = """You are a security expert reviewing code. Identify security, performance, 
and edge case risks in the code. Return a JSON array of risks with: type (SECURITY, PERFORMANCE, EDGE_CASE), 
level (CRITICAL, HIGH, MEDIUM, LOW), title, description, file_path, suggestion."""
        
        diff_text = self._format_diff_for_ai(pr_diff)
        
        prompt = f"""Analyze this PR for risks:

{diff_text}

Focus on:
1. Security vulnerabilities (SQL injection, XSS, auth issues)
2. Performance problems (N+1, inefficient algorithms)
3. Missing edge case handling
4. Error handling issues

Return only the risks found, formatted as JSON."""
        
        try:
            result = self.ai.complete_with_json(prompt, system_prompt)
            risks_data = result.get('risks', [])
            
            risks = []
            for risk_data in risks_data:
                risk = Risk(
                    type=RiskType(risk_data.get('type', 'CODE_QUALITY').upper()),
                    level=RiskLevel(risk_data.get('level', 'LOW').upper()),
                    title=risk_data.get('title', ''),
                    description=risk_data.get('description', ''),
                    file_path=risk_data.get('file_path'),
                    suggestion=risk_data.get('suggestion'),
                )
                risks.append(risk)
            
            return risks
            
        except Exception:
            return []
