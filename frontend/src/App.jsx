import { Routes, Route } from 'react-router-dom'
import Navbar from './components/Navbar'
import Home from './pages/Home'
import Review from './pages/Review'
import Demo from './pages/Demo'
import History from './pages/History'
import About from './pages/About'
import Result from './pages/Result'

function App() {
  return (
    <div>
      <Navbar />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/review" element={<Review />} />
        <Route path="/demo" element={<Demo />} />
        <Route path="/history" element={<History />} />
        <Route path="/about" element={<About />} />
        <Route path="/result" element={<Result />} />
      </Routes>
    </div>
  )
}

export default App
