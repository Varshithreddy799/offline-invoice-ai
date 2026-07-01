import { Routes, Route } from 'react-router-dom'
import { useState, useEffect } from 'react'
import Navbar from './components/Navbar'
import Dashboard from './components/Dashboard'
import Upload from './components/Upload'
import InvoiceViewer from './components/InvoiceViewer'
import ModelCheck from './components/ModelCheck'
import { healthCheck } from './api'

export default function App() {
  const [backendStatus, setBackendStatus] = useState('loading')
  const [modelStatus, setModelStatus] = useState(null)

  useEffect(() => {
    healthCheck()
      .then((data) => {
        setBackendStatus('connected')
        setModelStatus(data.model_loaded)
      })
      .catch(() => {
        setBackendStatus('disconnected')
      })
  }, [])

  return (
    <div className="min-h-screen bg-gray-950 flex flex-col">
      <Navbar backendStatus={backendStatus} modelStatus={modelStatus} />
      <ModelCheck modelStatus={modelStatus} backendStatus={backendStatus} />
      <main className="flex-1 container mx-auto px-4 py-6 max-w-7xl">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/upload" element={<Upload />} />
          <Route path="/invoice/:id" element={<InvoiceViewer />} />
        </Routes>
      </main>
    </div>
  )
}
