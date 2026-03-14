# AI PR Reviewer - Presentation Plan

## 1. Title Slide
- **Project Name**: AI PR Reviewer
- **Tagline**: Automated Pull Request Review System
- **Subtitle**: AI-Powered Code Review against Jira Requirements

---

## 2. Problem Statement
- Manual PR reviews are time-consuming
- Senior engineers spend hours reviewing code
- Inconsistent review quality
- Difficulty tracking ticket requirements vs implementation
- Need automated verification of acceptance criteria

---

## 3. Solution Overview
- Automated PR analysis using AI
- Integration with GitHub and Jira
- Compare PR changes against ticket requirements
- Generate comprehensive review reports
- Provide clear verdict (Approved/Changes Requested/Rejected)

---

## 4. Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         FRONTEND (React)                        │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐  │
│  │  Home   │ │ Review  │ │  Demo   │ │History  │ │ About   │  │
│  └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘  │
│       └───────────┴───────────┴───────────┴───────────┘        │
│                            │                                    │
│                     ┌──────┴──────┐                             │
│                     │  FastAPI    │                             │
│                     │  Backend    │                             │
│                     └──────┬──────┘                             │
└────────────────────────────┼────────────────────────────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
        ▼                    ▼                    ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│  GitHub API   │   │   Jira API    │   │  Claude/Groq  │
│   (PR Data)   │   │ (Ticket Data) │   │     (AI)      │
└───────────────┘   └───────────────┘   └───────────────┘
```

---

## 5. Technology Stack

### Frontend
- **Framework**: React 18 + Vite
- **Styling**: CSS3
- **Routing**: React Router
- **Port**: 3000 (dev) / served by backend (prod)

### Backend
- **Framework**: FastAPI (Python)
- **Server**: Uvicorn
- **Port**: 5000

### AI/ML
- **Provider**: Claude API / Groq API
- **Model**: Claude-3.5-Sonnet

### Integrations
- **GitHub**: PR diff retrieval, comments
- **Jira**: Ticket fetching, acceptance criteria

---

## 6. Component Breakdown

### Frontend Components

| Component | Description |
|-----------|-------------|
| `Navbar.jsx` | Navigation menu |
| `Home.jsx` | Dashboard with stats |
| `Review.jsx` | PR review submission form |
| `Demo.jsx` | Demo review (no auth needed) |
| `History.jsx` | Past review results |
| `Result.jsx` | Detailed review report |
| `About.jsx` | Project information |

### Backend Modules

| Module | Responsibility |
|--------|----------------|
| `app.py` | Main FastAPI application, routes |
| `orchestrator.py` | Coordinates review workflow |
| `analyzer.py` | Code diff analysis |
| `verdict_agent.py` | Generates approval verdict |
| `test_generator.py` | Suggests test cases |
| `dashboard.py` | Statistics dashboard |
| `ai_client.py` | AI API communication |
| `config.py` | Configuration management |
| `types.py` | Type definitions |

### Agent Modules

| Agent | Purpose |
|-------|---------|
| `github_agent.py` | GitHub API integration |
| `jira_agent.py` | Jira API integration |

---

## 7. Data Flow

```
User Input (PR URL + Ticket ID)
         │
         ▼
┌─────────────────────┐
│  Backend API        │
│  /api/review        │
└─────────┬───────────┘
          │
    ┌─────┴─────┬──────────────┐
    │           │              │
    ▼           ▼              ▼
┌────────┐ ┌────────┐    ┌──────────┐
│GitHub  │ │ Jira   │    │  Code    │
│Agent   │ │ Agent  │    │ Analyzer │
└───┬────┘ └───┬────┘    └────┬─────┘
    │          │              │
    │   ┌──────┴──────┐       │
    │   │   Merger    │       │
    │   └──────┬──────┘       │
    │          │              │
    ▼          ▼              ▼
┌─────────────────────────────────┐
│      AI Analysis Engine        │
│  (Requirements vs Code Match)   │
└─────────────┬───────────────────┘
              │
              ▼
┌─────────────────────────────────┐
│      Verdict Generator         │
│  (Approved/Changes/Rejected)   │
└─────────────┬───────────────────┘
              │
              ▼
┌─────────────────────────────────┐
│      Review Report              │
│  - Summary                      │
│  - Findings                     │
│  - Verdict                      │
└─────────────────────────────────┘
```

---

## 8. API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Home page |
| GET | `/review` | Review submission page |
| POST | `/review` | Submit PR for review |
| GET | `/demo` | Demo review page |
| POST | `/api/demo` | Run demo review |
| GET | `/history` | Review history |
| GET | `/result` | Review result details |
| GET | `/api/history` | Get all reviews |
| GET | `/health` | Health check |
| GET | `/about` | About page |

---

## 9. Key Features

### ✅ Core Features
1. **GitHub Integration**
   - Fetch PR diff
   - Get file changes
   - Retrieve PR metadata

2. **Jira Integration**
   - Fetch ticket details
   - Get acceptance criteria
   - Retrieve ticket status

3. **AI Analysis**
   - Requirements verification
   - Security scanning
   - Code quality check
   - Test coverage analysis
   - Risk identification

4. **Verdict System**
   - ✅ Approved: All requirements met
   - ⚠️ Changes Requested: Some issues found
   - ❌ Rejected: Critical problems

### 🎯 Demo Mode
- Pre-loaded sample ticket (PROJ-101)
- Password reset feature example
- No external credentials needed

---

## 10. Review Criteria

The AI analyzes PRs against:

| Category | Checks |
|----------|--------|
| **Requirements** | All acceptance criteria met? |
| **Security** | Vulnerabilities, exposed secrets |
| **Code Quality** | Best practices, readability |
| **Testing** | Unit tests, coverage |
| **Edge Cases** | Error handling, boundaries |
| **Performance** | Optimization opportunities |

---

## 11. Sample Output

### Review Report Structure:
```
{
  "verdict": "Changes Requested",
  "summary": "...",
  "findings": [
    {
      "category": "Security",
      "severity": "High",
      "message": "...",
      "file": "auth.py",
      "line": 42
    }
  ],
  "suggestions": [...],
  "test_suggestions": [...]
}
```

---

## 12. Use Cases

### Use Case 1: Full Integration
1. User provides GitHub PR URL + Jira Ticket ID
2. System fetches both data sources
3. AI analyzes code against requirements
4. Returns detailed report with verdict

### Use Case 2: Demo Mode
1. User clicks "Try Demo"
2. System uses sample PR + ticket
3. Returns demo review result
4. No authentication required

---

## 13. Project Structure

```
jirastmt/
├── app.py                 # Main Flask/FastAPI app
├── main.py               # Alternative entry point
├── config.yaml           # Configuration
├── requirements.txt      # Python dependencies
├── .env                  # Environment variables
│
├── frontend/             # React frontend
│   ├── src/
│   │   ├── App.jsx
│   │   ├── pages/
│   │   │   ├── Home.jsx
│   │   │   ├── Review.jsx
│   │   │   ├── Demo.jsx
│   │   │   ├── History.jsx
│   │   │   ├── Result.jsx
│   │   │   └── About.jsx
│   │   └── components/
│   │       └── Navbar.jsx
│   └── package.json
│
├── src/                  # Python backend modules
│   ├── ai_client.py
│   ├── analyzer.py
│   ├── config.py
│   ├── dashboard.py
│   ├── orchestrator.py
│   ├── test_generator.py
│   ├── types.py
│   ├── verdict_agent.py
│   └── agents/
│       ├── github_agent.py
│       └── jira_agent.py
│
└── templates/            # HTML templates (legacy)
```

---

## 14. Environment Setup

### Required Environment Variables:
```
GROQ_API_KEY=your_groq_api_key
GITHUB_TOKEN=your_github_personal_token
JIRA_API_KEY=your_jira_api_key
JIRA_EMAIL=your_email@company.com
JIRA_URL=https://your-domain.atlassian.net
```

---

## 15. Running the Application

### Development:
```bash
# Frontend (port 3000)
cd frontend && npm run dev

# Backend (port 5000)
python app.py
```

### Production:
```bash
# Build frontend
cd frontend && npm run build

# Run backend (serves both)
python app.py
```

---

## 16. Future Enhancements

| Feature | Description |
|---------|-------------|
| Database | Persistent storage for reviews |
| Auth | User login & authentication |
| Webhooks | Auto-trigger on PR events |
| Notifications | Slack/Teams integration |
| Custom Rules | User-defined review rules |
| Multi-language | Support for Java, JS, Go, etc. |

---

## 17. Summary Slide

- ✅ Automated PR review saves time
- ✅ AI-powered analysis is consistent
- ✅ Jira integration ensures requirement tracking
- ✅ Demo mode for easy testing
- ✅ Open source and extensible

---

## 18. Q&A
- Questions?
- Demo time!
- Thank you!

---

## Presentation Tips

1. **Keep slides clean** - Use bullet points, not paragraphs
2. **Use diagrams** - Architecture and data flow are key
3. **Live demo** - Show the demo mode in action
4. **Highlight AI** - Emphasize the value of AI analysis
5. **Show code examples** - Sample review output
6. **Focus on business value** - Time savings, consistency
