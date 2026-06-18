import React, { useState, useRef, useEffect } from 'react'
import axios from 'axios'
import CodeDisplay from './CodeDisplay'
import './ChatInterface.css'

function ChatInterface() {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [sessionId, setSessionId] = useState(null)
  const [sessionLoading, setSessionLoading] = useState(true)
  const [modeInfo, setModeInfo] = useState(null)
  const messagesEndRef = useRef(null)

  // Initialize session on component mount
  useEffect(() => {
    initializeSession()
  }, [])

  const initializeSession = async () => {
    try {
      const response = await axios.post('/api/chat/start-session', {})
      setSessionId(response.data.session_id)
      console.log('Session started:', response.data.session_id)
    } catch (err) {
      console.error('Error starting session:', err)
      setError('Failed to start chat session')
    } finally {
      setSessionLoading(false)
    }
  }

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const detectMessageMode = async (message) => {
    try {
      const response = await axios.post('/api/mode/detect', {
        message: message
      })
      return response.data
    } catch (err) {
      console.error('Error detecting mode:', err)
      return { mode: 'general', confidence: 0 }
    }
  }

  const handleSendMessage = async (e) => {
    e.preventDefault()
    
    if (!input.trim() || !sessionId) return

    const userMessage = input.trim()
    setInput('')
    setError(null)
    setLoading(true)

    // Add user message to chat
    setMessages(prev => [...prev, {
      id: Date.now(),
      type: 'user',
      content: userMessage,
      timestamp: new Date().toLocaleTimeString()
    }])

    try {
      // Detect mode first
      const modeData = await detectMessageMode(userMessage)
      setModeInfo(modeData)

      // Send message with session context
      const response = await axios.post('/api/chat/message', {
        session_id: sessionId,
        message: userMessage
      }, {
        timeout: 60000 // 60 second timeout
      })

      if (response.data.status === 'success') {
        setMessages(prev => [...prev, {
          id: Date.now() + 1,
          type: 'assistant',
          content: response.data.answer,
          sources: response.data.sources,
          mode: response.data.mode,
          modeConfidence: response.data.mode_confidence,
          timestamp: new Date().toLocaleTimeString()
        }])
      } else {
        setError(response.data.error || 'Failed to get response')
        setMessages(prev => [...prev, {
          id: Date.now() + 1,
          type: 'error',
          content: response.data.error || 'Failed to get response',
          timestamp: new Date().toLocaleTimeString()
        }])
      }
    } catch (err) {
      console.error('Error:', err)
      const errorMessage = err.response?.data?.error || err.message || 'Failed to connect to server'
      setError(errorMessage)
      setMessages(prev => [...prev, {
        id: Date.now() + 1,
        type: 'error',
        content: errorMessage,
        timestamp: new Date().toLocaleTimeString()
      }])
    } finally {
      setLoading(false)
    }
  }

  const handleClearHistory = async () => {
    if (!sessionId) return
    
    try {
      await axios.post(`/api/chat/clear/${sessionId}`)
      setMessages([])
      setModeInfo(null)
      console.log('Chat history cleared')
    } catch (err) {
      console.error('Error clearing history:', err)
      setError('Failed to clear history')
    }
  }

  const handleNewSession = () => {
    setMessages([])
    setModeInfo(null)
    initializeSession()
  }

  if (sessionLoading) {
    return (
      <div className="chat-interface">
        <div className="chat-messages">
          <div className="empty-state">
            <div className="loading-spinner"></div>
            <p>Initializing chat session...</p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="chat-interface">
      {/* Chat Header with Mode Info */}
      <div className="chat-header">
        <div className="session-info">
          <span className="session-id">Session: {sessionId?.slice(0, 8)}...</span>
          {modeInfo && (
            <span className={`mode-badge ${modeInfo.mode}`}>
              {modeInfo.mode === 'coding' ? '💻 Coding Mode' : '💬 Chat Mode'}
              <span className="confidence">({(modeInfo.confidence * 100).toFixed(0)}%)</span>
            </span>
          )}
        </div>
        <div className="chat-actions">
          <button className="clear-btn" onClick={handleClearHistory} title="Clear history">
            🗑️
          </button>
          <button className="new-session-btn" onClick={handleNewSession} title="Start new session">
            ➕
          </button>
        </div>
      </div>

      {/* Messages */}
      <div className="chat-messages">
        {messages.length === 0 && (
          <div className="empty-state">
            <div className="empty-icon">💬</div>
            <h2>Welcome to AAKIF's Hybrid Chatbot</h2>
            <p>I can help you with:</p>
            <div className="feature-grid">
              <div className="feature">
                <div className="feature-icon">💻</div>
                <p><strong>Code Assistance</strong><br/>Debug, develop, and optimize code</p>
              </div>
              <div className="feature">
                <div className="feature-icon">💬</div>
                <p><strong>Personal Chat</strong><br/>General conversation and questions</p>
              </div>
              <div className="feature">
                <div className="feature-icon">📚</div>
                <p><strong>Memory</strong><br/>I remember our conversation</p>
              </div>
              <div className="feature">
                <div className="feature-icon">🌐</div>
                <p><strong>Multi-Language</strong><br/>All programming languages supported</p>
              </div>
            </div>
            <p className="example-text">Try asking:</p>
            <ul className="example-questions">
              <li>"Debug this code for me"</li>
              <li>"How do I implement authentication?"</li>
              <li>"What's the weather like?" (general chat)</li>
              <li>"Show me best practices for React"</li>
            </ul>
          </div>
        )}

        {messages.map(message => (
          <div key={message.id} className={`message ${message.type}`}>
            <div className="message-bubble">
              <div className="message-header">
                <span className="message-role">
                  {message.type === 'user' ? '👤 You' : '🤖 AAKIF'}
                </span>
                {message.mode && (
                  <span className={`inline-mode-badge ${message.mode}`}>
                    {message.mode === 'coding' ? '💻' : '💬'}
                  </span>
                )}
                <span className="message-time">{message.timestamp}</span>
              </div>
              
              <div className="message-content">
                {message.type === 'user' && (
                  <div className="message-text user-message">
                    {message.content}
                  </div>
                )}
                
                {message.type === 'assistant' && (
                  <>
                    <div className="message-text assistant-message">
                      {message.content}
                    </div>
                    {message.sources && message.sources.length > 0 && (
                      <div className="sources">
                        <h4>📚 Source Code:</h4>
                        <div className="sources-list">
                          {message.sources.map((source, idx) => (
                            <CodeDisplay key={idx} source={source} />
                          ))}
                        </div>
                      </div>
                    )}
                  </>
                )}
                
                {message.type === 'error' && (
                  <div className="message-text error-message">
                    ⚠️ {message.content}
                  </div>
                )}
              </div>
            </div>
          </div>
        ))}

        {loading && (
          <div className="message assistant">
            <div className="message-bubble">
              <div className="message-header">
                <span className="message-role">🤖 AAKIF</span>
              </div>
              <div className="message-content">
                <div className="loading-indicator">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
                <p className="thinking-text">Thinking...</p>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Form */}
      <form onSubmit={handleSendMessage} className="chat-input-form">
        {error && <div className="form-error">{error}</div>}
        <div className="input-wrapper">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask me anything... (coding questions, general chat, etc.)"
            disabled={loading}
            className="chat-input"
            autoFocus
          />
          <button
            type="submit"
            disabled={loading || !input.trim()}
            className="send-button"
            title="Send message"
          >
            {loading ? '⏳' : '➤'}
          </button>
        </div>
      </form>
    </div>
  )
}

export default ChatInterface
