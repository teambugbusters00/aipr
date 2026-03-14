# AI PR Reviewer

A senior engineer PR review system that behaves like an experienced developer reviewing pull requests.

## Features

### Unique Feature 1: Requirement → Code Mapping
Maps every Jira requirement to actual code with traceability.

```
Requirement: Password reset link expires in 15 minutes

Evidence:
auth/reset.py line 84
expiry_time = now + timedelta(minutes=15)

Status: PASS
```

### Unique Feature 2: AI Test Generator
Automatically generates tests from Jira requirements.

```python
def test_password_length():
    assert len(password) >= 8
```

### Unique Feature 3: Risk Detection
Detects security, performance, and edge case risks.

```
Warning: Password reset token stored in plaintext.
```

## Architecture

```
Frontend Dashboard
        │
        ▼
Orchestrator Agent
        │
 ┌──────┼───────┐
 ▼      ▼       ▼
Jira   GitHub   Code Analyzer
Agent  Agent
        │
        ▼
Test Generator Agent
        │
        ▼
Verdict Agent
```

## Installation

```bash
pip install -r requirements.txt
```

## Configuration

Edit `config.yaml` with your settings:

```yaml
jira:
  domain: "your-domain.atlassian.net"
  email: "your-email@company.com"

github:
  owner: "your-org"
  repo: "your-repo"

ai:
  model: "gpt-4"
```

Set environment variables:
- `OPENAI_API_KEY` - For AI capabilities
- `JIRA_API_TOKEN` - For Jira integration
- `GITHUB_TOKEN` - For GitHub integration

### Using Local Transformer Models

Instead of OpenAI, you can use local transformer models:

```bash
# Install transformer dependencies
pip install transformers torch

# Set environment variables
set USE_TRANSFORMER_MODEL=1
set TRANSFORMER_MODEL_NAME=gpt2

# Run
python main.py --demo
```

Supported models:
- `gpt2` - Smallest, fastest
- `EleutherAI/gpt-neo-125M` - Better quality
- `Salesforce/codegen-350M-multi` - Code generation
- `microsoft/codebert-base` - Code understanding
- `bigcode/starcoder` - Code completion

### Using LLaMA.cpp (Recommended for local GGUF models)

Start the llama.cpp server:

```bash
# Install llama.cpp (macOS)
brew install llama.cpp

# Or download from: https://github.com/ggerganov/llama.cpp/releases

# Start server with a GGUF model
llama-server --hf-repo microsoft/Phi-3-mini-4k-instruct-gguf \
    --hf-file Phi-3-mini-4k-instruct-q4.gguf -c 4096
```

Then use the client:

```bash
# Set environment variables
set USE_LLAMACPP=1
set LLAMACPP_URL=http://localhost:8080

# Run
python main.py --demo
```

Alternative GGUF models:
- `TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF` - Tiny but capable
- `TheBloke/Mistral-7B-Instruct-v0.2-GGUF` - Better quality
- `TheBloke/CodeLlama-7B-Instruct-GGUF` - Code-specialized

## Usage

### Demo Mode (no API needed)
```bash
python main.py --demo
```

### With Jira + GitHub
```bash
python main.py --jira PROJ-101 --pr 245
```

### Output Options
```bash
# HTML dashboard
python main.py --jira PROJ-101 --pr 245 --output dashboard.html

# JSON output
python main.py --jira PROJ-101 --pr 245 --format json
```

## Dashboard

Open the generated HTML file in a browser to see:
- Overall verdict (PASS/PARTIAL/FAIL)
- Requirements analysis with pass/fail status
- Detected risks with severity levels
- Requirement → Code mappings
- AI-generated tests
- Suggested fixes

## Example Output

```
============================================================
 AI PR Reviewer - Dashboard
============================================================

Jira Ticket: PROJ-101
GitHub PR: #245

------------------------------------------------------------
Overall Verdict: PARTIAL

Requirement Analysis
✔ REQ-001: Password reset link expires in 15 minutes
✘ REQ-005: Token should be securely hashed before storage

Detected Issues
⚠ Token stored without hashing
  → auth/reset.py

Suggested Fixes
1. Add expiry timestamp logic
2. Hash tokens before storage
------------------------------------------------------------
```

## License

MIT
