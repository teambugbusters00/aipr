import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import axios from 'axios'

function Home() {
  const [reviews, setReviews] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchHistory()
  }, [])

  const fetchHistory = async () => {
    try {
      const response = await axios.get('/api/history')
      setReviews(response.data.slice(0, 10))
    } catch (error) {
      console.error('Failed to fetch reviews:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="container">
      <div className="hero">
        <h1>AI PR Reviewer</h1>
        <p>Senior Engineer PR Review System - Automated code review with AI</p>
        <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center' }}>
          <Link to="/review" className="btn btn-primary">Start Review</Link>
          <Link to="/demo" className="btn btn-secondary">Try Demo</Link>
        </div>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-number">{reviews.length}</div>
          <div className="stat-label">Recent Reviews</div>
        </div>
        <div className="stat-card">
          <div className="stat-number">24/7</div>
          <div className="stat-label">Availability</div>
        </div>
        <div className="stat-card">
          <div className="stat-number">AI</div>
          <div className="stat-label">Powered Analysis</div>
        </div>
      </div>

      {loading ? (
        <div className="loading">
          <div className="spinner"></div>
        </div>
      ) : reviews.length > 0 ? (
        <div className="card">
          <h2 className="card-header">Recent Reviews</h2>
          <table className="history-table">
            <thead>
              <tr>
                <th>Jira Key</th>
                <th>PR Number</th>
                <th>Verdict</th>
                <th>Summary</th>
              </tr>
            </thead>
            <tbody>
              {reviews.map((review) => (
                <tr key={review.id}>
                  <td>{review.jira_key}</td>
                  <td>{review.pr_number}</td>
                  <td>
                    <span className={`verdict ${review.verdict}`} style={{ padding: '0.25rem 0.5rem', fontSize: '0.9rem' }}>
                      {review.verdict}
                    </span>
                  </td>
                  <td>{review.summary?.substring(0, 50)}...</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <div className="card">
          <p style={{ textAlign: 'center', color: '#666' }}>No reviews yet. Start by running a demo or review!</p>
        </div>
      )}
    </div>
  )
}

export default Home
