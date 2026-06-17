import React, { useState, useEffect } from 'react'
import ChatInterface from './components/ChatInterface'
import FileUploader from './components/FileUploader'
import './App.css'

function App() {
  const [activeTab, setActiveTab] = useState('chat')
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchStats()
  }, [])

  const fetchStats = async () => {
    try {
      const response = await fetch('/api/stats')
      const data = await response.json()
      setStats(data)
    } catch (error) {
      console.error('Error fetching stats:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleUploadSuccess = () => {
    fetchStats()
    setActiveTab('chat')
  }

  return (
    <div className="app-container">
      <header className="app-header">
        <div className="header-content">
          <h1>🤖 AAKIF's RAG Chatbot</h1>
          <p>Ask questions about your code with AI-powered answers</p>
        </div>
      </header>

      <div className="app-body">
        <div className="tab-buttons">
          <button
            className={`tab-btn ${activeTab === 'chat' ? 'active' : ''}`}
            onClick={() => setActiveTab('chat')}
          >
            💬 Chat
          </button>
          <button
            className={`tab-btn ${activeTab === 'upload' ? 'active' : ''}`}
            onClick={() => setActiveTab('upload')}
          >
            📤 Upload Code
          </button>
        </div>

        <div className="tab-content">
          {!loading && (
            <div className="status-bar">
              {stats?.status === 'empty' ? (
                <span className="status-empty">📝 No code indexed yet. Upload code to get started!</span>
              ) : (
                <span className="status-ready">✅ Ready to answer questions</span>
              )}
            </div>
          )}

          {activeTab === 'chat' && <ChatInterface />}
          {activeTab === 'upload' && <FileUploader onUploadSuccess={handleUploadSuccess} />}
        </div>
      </div>
    </div>
  )
}

export default App
