import { BrowserRouter, Routes, Route } from 'react-router-dom'
import './App.css'
import { Home } from './pages/Home'
import { SolutionDetailPage } from './pages/SolutionDetailPage'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/solution/:index" element={<SolutionDetailPage />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
