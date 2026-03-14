"""
Dashboard - HTML dashboard generator for PR reviews
"""

from typing import Optional
from src.types import ReviewResult, Verdict, RequirementStatus, RiskLevel


def generate_html_dashboard(result: ReviewResult) -> str:
    """Generate an HTML dashboard for the review result"""
    
    # Determine colors based on verdict
    verdict_colors = {
        Verdict.PASS: "#22c55e",
        Verdict.PARTIAL: "#eab308",
        Verdict.FAIL: "#ef4444",
        Verdict.NEEDS_REVIEW: "#6b7280",
    }
    
    verdict_color = verdict_colors.get(result.verdict, "#6b7280")
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI PR Reviewer - {result.jira_ticket.key} / PR #{result.pr_diff.pr_number}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: #f8fafc;
            color: #1e293b;
            line-height: 1.6;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        header {{
            background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
            color: white;
            padding: 30px;
            border-radius: 12px;
            margin-bottom: 30px;
        }}
        
        h1 {{
            font-size: 28px;
            margin-bottom: 10px;
        }}
        
        .meta {{
            display: flex;
            gap: 20px;
            flex-wrap: wrap;
            font-size: 14px;
            opacity: 0.9;
        }}
        
        .verdict-banner {{
            background: {verdict_color};
            color: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            margin-bottom: 30px;
        }}
        
        .verdict-banner h2 {{
            font-size: 32px;
            margin-bottom: 5px;
        }}
        
        .summary {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }}
        
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }}
        
        .card h3 {{
            font-size: 18px;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid #e2e8f0;
        }}
        
        .requirement {{
            display: flex;
            align-items: flex-start;
            padding: 12px;
            border-radius: 6px;
            margin-bottom: 10px;
            background: #f8fafc;
        }}
        
        .requirement.pass {{ border-left: 4px solid #22c55e; }}
        .requirement.fail {{ border-left: 4px solid #ef4444; }}
        .requirement.partial {{ border-left: 4px solid #eab308; }}
        
        .status-icon {{
            width: 24px;
            height: 24px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-right: 12px;
            font-size: 14px;
            flex-shrink: 0;
        }}
        
        .status-icon.pass {{ background: #dcfce7; color: #22c55e; }}
        .status-icon.fail {{ background: #fee2e2; color: #ef4444; }}
        .status-icon.partial {{ background: #fef9c3; color: #eab308; }}
        
        .req-text {{
            font-size: 14px;
        }}
        
        .req-id {{
            font-size: 12px;
            color: #64748b;
            margin-bottom: 4px;
        }}
        
        .risk {{
            padding: 12px;
            border-radius: 6px;
            margin-bottom: 10px;
        }}
        
        .risk.critical {{ background: #fef2f2; border-left: 4px solid #ef4444; }}
        .risk.high {{ background: #fff7ed; border-left: 4px solid #f97316; }}
        .risk.medium {{ background: #fefce8; border-left: 4px solid #eab308; }}
        .risk.low {{ background: #f0f9ff; border-left: 4px solid #3b82f6; }}
        
        .risk-title {{
            font-weight: 600;
            font-size: 14px;
            margin-bottom: 4px;
        }}
        
        .risk-description {{
            font-size: 13px;
            color: #64748b;
        }}
        
        .suggestion {{
            padding: 12px;
            background: #f8fafc;
            border-radius: 6px;
            margin-bottom: 10px;
            font-size: 14px;
        }}
        
        .mapping {{
            padding: 12px;
            background: #f8fafc;
            border-radius: 6px;
            margin-bottom: 10px;
            font-size: 13px;
        }}
        
        .mapping-file {{
            font-family: monospace;
            background: #e2e8f0;
            padding: 2px 6px;
            border-radius: 4px;
            font-size: 12px;
        }}
        
        .test-code {{
            background: #1e293b;
            color: #e2e8f0;
            padding: 15px;
            border-radius: 6px;
            font-family: monospace;
            font-size: 12px;
            overflow-x: auto;
            white-space: pre-wrap;
        }}
        
        .stats {{
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
            margin-bottom: 20px;
        }}
        
        .stat {{
            background: white;
            padding: 15px 20px;
            border-radius: 8px;
            text-align: center;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }}
        
        .stat-value {{
            font-size: 24px;
            font-weight: bold;
        }}
        
        .stat-label {{
            font-size: 12px;
            color: #64748b;
            text-transform: uppercase;
        }}
        
        .stat.pass .stat-value {{ color: #22c55e; }}
        .stat.fail .stat-value {{ color: #ef4444; }}
        .stat.risk .stat-value {{ color: #f97316; }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🤖 AI PR Reviewer</h1>
            <div class="meta">
                <span>📋 Jira: {result.jira_ticket.key}</span>
                <span>🔀 GitHub PR: #{result.pr_diff.pr_number}</span>
                <span>👤 Author: {result.pr_diff.author}</span>
                <span>🌿 {result.pr_diff.branch} → {result.pr_diff.base_branch}</span>
            </div>
        </header>
        
        <div class="verdict-banner">
            <h2>{result.verdict.value}</h2>
            <p>{result.summary}</p>
        </div>
        
        <div class="stats">
            <div class="stat pass">
                <div class="stat-value">{result.passed_requirements}</div>
                <div class="stat-label">Requirements Passed</div>
            </div>
            <div class="stat fail">
                <div class="stat-value">{result.failed_requirements}</div>
                <div class="stat-label">Requirements Failed</div>
            </div>
            <div class="stat risk">
                <div class="stat-value">{len(result.risks)}</div>
                <div class="stat-label">Risks Detected</div>
            </div>
            <div class="stat">
                <div class="stat-value">{len(result.pr_diff.files_changed)}</div>
                <div class="stat-label">Files Changed</div>
            </div>
        </div>
        
        <div class="grid">
            <div class="card">
                <h3>📋 Requirements Analysis</h3>
                {"".join([
                    f'''<div class="requirement {req.status.value}">
                        <div class="status-icon {req.status.value}">
                            {"✓" if req.status == RequirementStatus.PASS else "✗" if req.status == RequirementStatus.FAIL else "◐"}
                        </div>
                        <div>
                            <div class="req-id">{req.id} • {req.category} • {req.priority}</div>
                            <div class="req-text">{req.text}</div>
                        </div>
                    </div>'''
                    for req in result.requirements
                ])}
            </div>
            
            <div class="card">
                <h3>⚠️ Detected Risks</h3>
                {"" if result.risks else "<p>No risks detected</p>"}
                {"".join([
                    f'''<div class="risk {risk.level.value.lower()}">
                        <div class="risk-title">{risk.title}</div>
                        <div class="risk-description">{risk.description}</div>
                        {"<div class='mapping-file'>" + risk.file_path + "</div>" if risk.file_path else ""}
                    </div>'''
                    for risk in result.risks
                ])}
            </div>
        </div>
        
        <div class="grid">
            <div class="card">
                <h3>🔗 Requirement → Code Mapping</h3>
                {"" if result.code_mappings else "<p>No code mappings found</p>"}
                {"".join([
                    f'''<div class="mapping">
                        <div class="req-id">{mapping.requirement_id}</div>
                        <div><span class="mapping-file">{mapping.file_path}:{mapping.line_number}</span></div>
                        <div>{mapping.description}</div>
                    </div>'''
                    for mapping in result.code_mappings
                ])}
            </div>
            
            <div class="card">
                <h3>💡 Suggested Fixes</h3>
                {"" if not result.suggestions else "<p>No suggestions</p>"}
                {"" if result.suggestions else "<br>".join([
                    f"<div class='suggestion'>{i+1}. {s}</div>"
                    for i, s in enumerate(result.suggestions)
                ])}
            </div>
        </div>
        
        <div class="card">
            <h3>🧪 AI-Generated Tests</h3>
            {"" if not result.generated_tests else "<p>No tests generated</p>"}
            {"" if result.generated_tests else "<br>".join([
                f'''<div style="margin-bottom: 20px;">
                    <div class="req-id">{test.name} ({test.framework})</div>
                    <div class="test-code">{test.test_code[:500]}{"..." if len(test.test_code) > 500 else ""}</div>
                </div>'''
                for test in result.generated_tests
            ])}
        </div>
        
        <footer style="text-align: center; padding: 20px; color: #64748b; font-size: 12px;">
            Generated by AI PR Reviewer • {result.reviewed_at.strftime('%Y-%m-%d %H:%M:%S')}
        </footer>
    </div>
</body>
</html>"""
    
    return html


def save_html_dashboard(result: ReviewResult, filepath: str) -> None:
    """Save HTML dashboard to file"""
    html = generate_html_dashboard(result)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html)
