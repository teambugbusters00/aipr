import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import axios from 'axios'

function Review() {
  const navigate = useNavigate()
  const [formData, setFormData] = useState({
    jira_key: '',
    pr_number: ''
  })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      const response = await axios.post('/api/review', null, {
        params: {
          jira_key: formData.jira_key,
          pr_number: parseInt(formData.pr_number)
        }
      })
      navigate('/result', { state: { result: response.data } })
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Review failed')
    } finally {
      setLoading(false)
    }
  }

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    })
  }

  return (
    <div className="container">
      <div className="card">
        <h2 className="card-header">Submit PR Review</h2>
        
        {error && <div className="error">{error}</div>}
        
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label">Jira Key</label>
            <input
              type="text"
              name="jira_key"
              className="form-input"
              placeholder="e.g., PROJ-123"
              value={formData.jira_key}
              onChange={handleChange}
              required
            />
          </div>
          
          <div className="form-group">
            <label className="form-label">PR Number</label>
            <input
              type="number"
              name="pr_number"
              className="form-input"
              placeholder="e.g., 245"
              value={formData.pr_number}
              onChange={handleChange}
              required
            />
          </div>
          
          <button type="submit" className="btn btn-primary" disabled={loading}>
            {loading ? 'Submitting...' : 'Submit Review'}
          </button>
        </form>
      </div>
    </div>
  )
}

export default Review
