import { useLocation, Link } from 'react-router-dom'

function Result() {
  const location = useLocation()
  const result = location.state?.result

  if (!result) {
    return (
      <div className="container">
        <div className="card">
          <h2 className="card-header">No Results</h2>
          <p>No review result available. Please run a review first.</p>
          <Link to="/review" className="btn btn-primary">Start Review</Link>
        </div>
      </div>
    )
  }

  const getVerdictClass = (verdict) => {
    switch (verdict) {
      case 'approved':
        return 'approved'
      case 'changes_requested':
        return 'changes_requested'
      case 'rejected':
        return 'rejected'
      default:
        return ''
    }
  }

  return (
    <div className="container">
      <div className="card">
        <h2 className="card-header">Review Result</h2>
        
        <div className={`verdict ${getVerdictClass(result.verdict)}`}>
          Verdict: {result.verdict?.toUpperCase() || 'UNKNOWN'}
        </div>
        
        <div className="result-section">
          <h3>Summary</h3>
          <p>{result.summary}</p>
        </div>
        
        {result.passed_requirements && result.passed_requirements.length > 0 && (
          <div className="result-section">
            <h3>Passed Requirements ({result.passed_requirements.length})</h3>
            <ul className="requirements-list">
              {result.passed_requirements.map((req, index) => (
                <li key={index} className="requirement-item passed">
                  ✓ {req}
                </li>
              ))}
            </ul>
          </div>
        )}
        
        {result.failed_requirements && result.failed_requirements.length > 0 && (
          <div className="result-section">
            <h3>Failed Requirements ({result.failed_requirements.length})</h3>
            <ul className="requirements-list">
              {result.failed_requirements.map((req, index) => (
                <li key={index} className="requirement-item failed">
                  ✗ {req}
                </li>
              ))}
            </ul>
          </div>
        )}
        
        {result.risks && result.risks.length > 0 && (
          <div className="result-section">
            <h3>Risks Identified ({result.risks.length})</h3>
            <ul className="requirements-list">
              {result.risks.map((risk, index) => (
                <li key={index} className="requirement-item pending">
                  ⚠ {risk}
                </li>
              ))}
            </ul>
          </div>
        )}
        
        {result.file_reviews && result.file_reviews.length > 0 && (
          <div className="result-section">
            <h3>File Reviews</h3>
            {result.file_reviews.map((file, index) => (
              <div key={index} className="diff-file">
                <div className="diff-header">
                  {file.filename} ({file.additions} additions, {file.deletions} deletions)
                </div>
                <div className="diff-content">
                  {file.comments?.join('\n\n') || 'No specific comments'}
                </div>
              </div>
            ))}
          </div>
        )}
        
        <div style={{ marginTop: '2rem', display: 'flex', gap: '1rem' }}>
          <Link to="/review" className="btn btn-primary">New Review</Link>
          <Link to="/history" className="btn btn-secondary">View History</Link>
        </div>
      </div>
    </div>
  )
}

export default Result
