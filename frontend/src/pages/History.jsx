import { useState, useEffect } from 'react'
import axios from 'axios'

function History() {
  const [reviews, setReviews] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchHistory()
  }, [])

  const fetchHistory = async () => {
    try {
      const response = await axios.get('/api/history')
      setReviews(response.data)
    } catch (error) {
      console.error('Failed to fetch history:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="container">
        <div className="loading">
          <div className="spinner"></div>
        </div>
      </div>
    )
  }

  return (
    <div className="container">
      <div className="card">
        <h2 className="card-header">Review History</h2>
        
        {reviews.length === 0 ? (
          <p style={{ textAlign: 'center', color: '#666' }}>No reviews yet</p>
        ) : (
          <table className="history-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Jira Key</th>
                <th>PR Number</th>
                <th>Verdict</th>
                <th>Passed</th>
                <th>Failed</th>
                <th>Risks</th>
              </tr>
            </thead>
            <tbody>
              {reviews.map((review) => (
                <tr key={review.id}>
                  <td>{review.id}</td>
                  <td>{review.jira_key}</td>
                  <td>{review.pr_number}</td>
                  <td>
                    <span className={`verdict ${review.verdict}`} style={{ padding: '0.25rem 0.5rem', fontSize: '0.9rem' }}>
                      {review.verdict}
                    </span>
                  </td>
                  <td>{review.passed?.length || 0}</td>
                  <td>{review.failed?.length || 0}</td>
                  <td>{review.risks || 0}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}

export default History
