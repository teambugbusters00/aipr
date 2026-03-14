function About() {
  return (
    <div className="container">
      <div className="card">
        <h2 className="card-header">About AI PR Reviewer</h2>
        
        <div className="about-section">
          <h2>Overview</h2>
          <p>
            AI PR Reviewer is an automated code review system powered by AI. 
            It analyzes pull requests against Jira ticket requirements to provide 
            comprehensive feedback on code quality, security, and completeness.
          </p>
        </div>
        
        <div className="about-section">
          <h2>Features</h2>
          <ul style={{ marginLeft: '1.5rem', marginTop: '0.5rem' }}>
            <li>Automated PR analysis against Jira requirements</li>
            <li>Security vulnerability detection</li>
            <li>Code quality assessment</li>
            <li>Test coverage verification</li>
            <li>Risk identification</li>
            <li>Comprehensive review reports</li>
          </ul>
        </div>
        
        <div className="about-section">
          <h2>How It Works</h2>
          <p>
            The system connects to your Jira instance to fetch ticket details 
            and acceptance criteria, then analyzes the PR diff to verify that 
            all requirements are met. It provides a detailed verdict with 
            specific feedback on what's passing, failing, and what risks exist.
          </p>
        </div>
        
        <div className="about-section">
          <h2>Tech Stack</h2>
          <ul style={{ marginLeft: '1.5rem', marginTop: '0.5rem' }}>
            <li>Frontend: React</li>
            <li>Backend: FastAPI (Python)</li>
            <li>AI: Claude API</li>
            <li>Integration: GitHub, Jira</li>
          </ul>
        </div>
      </div>
    </div>
  )
}

export default About
