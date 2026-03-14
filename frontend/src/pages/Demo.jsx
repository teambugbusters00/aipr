import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import axios from 'axios'

function Demo() {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    runDemo()
  }, [])

  const runDemo = async () => {
    setLoading(true)
    setError('')
    
    try {
      const response = await axios.get('/api/demo')
      navigate('/result', { state: { result: response.data } })
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Demo failed')
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="container">
        <div className="card">
          <h2 className="card-header">Running Demo Review</h2>
          <div className="loading">
            <div className="spinner"></div>
          </div>
          <p style={{ textAlign: 'center', marginTop: '1rem' }}>
            Analyzing demo PR with Jira ticket PROJ-101...
          </p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="container">
        <div className="card">
          <h2 className="card-header">Demo Error</h2>
          <div className="error">{error}</div>
          <button onClick={runDemo} className="btn btn-primary">
            Try Again
          </button>
        </div>
      </div>
    )
  }

  return null
}

export default Demo
