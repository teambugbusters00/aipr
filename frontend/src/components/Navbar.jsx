import { Link } from 'react-router-dom'

function Navbar() {
  return (
    <nav className="navbar">
      <Link to="/" className="navbar-brand">AI PR Reviewer</Link>
      <div className="navbar-links">
        <Link to="/">Home</Link>
        <Link to="/review">Review</Link>
        <Link to="/demo">Demo</Link>
        <Link to="/history">History</Link>
        <Link to="/about">About</Link>
      </div>
    </nav>
  )
}

export default Navbar
