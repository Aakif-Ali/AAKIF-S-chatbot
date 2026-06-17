import React, { useState, useRef, useEffect } from 'react'
import axios from 'axios'
import CodeDisplay from './CodeDisplay'
import './ChatInterface.css'

function ChatInterface() {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const messagesEndRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSendMessage = async (e) => {
    e.preventDefault()
    
    if (!input.trim()) return

    const userMessage = input.trim()
    setInput('')
    setError(null)
    setLoading(true)

    // Add user message to chat
    setMessages(prev => [...prev, {
      id: Date.now(),
      type: 'user',
      content: userMessage
    }])

    try {
      const response = await axios.post('/api/query', {
        question: userMessage
      }, {
        timeout: 60000 // 60 second timeout
      })

      if (response.data.status === 'success') {
        setMessages(prev => [...prev, {
          id: Date.now() + 1,
          type: 'assistant',
          content: response.data.answer,
          sources: response.data.sources
        }])
      } else {
        setError(response.data.error || 'Failed to get response')
      }
    } catch (err) {
      console.error('Error:', err)
      if (err.response?.data?.error) {
        setError(err.response.data.error)
      } else {
        setError(err.message || 'Failed to connect to server')
      }
      setMessages(prev => [...prev, {
        id: Date.now() + 1,
        type: 'error',
        content: 'Failed to get response. Make sure the backend is running and code has been uploaded.'
      }])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="chat-interface">
      <div className="chat-messages">
        {messages.length === 0 && (
          <div className="empty-state">
            <div className="empty-icon">💬</div>
            <h2>Start a Conversation</h2>
            <p>Ask questions about your code. For example:</p>
            <ul>
              <li>"How do you handle authentication?"</li>
              <li>"Show me the database connection code"</li>
              <li>"What validation functions are available?"</li>
              <li>"How is error handling implemented?"</li>
            </ul>
          </div>
        )}

        {messages.map(message => (
          <div key={message.id} className={`message ${message.type}`}>
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
                      <h4>📚 Sources:</h4>
                      {message.sources.map((source, idx) => (
                        <CodeDisplay key={idx} source={source} />
                      ))}
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
        ))}

        {loading && (
          <div className="message assistant">
            <div className="message-content">
              <div className="loading-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
              <p>Thinking...</p>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      <form onSubmit={handleSendMessage} className="chat-input-form">
        <div className="input-wrapper">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask me about your code..."
            disabled={loading}
            className="chat-input"
          />
          <button
            type="submit"
            disabled={loading || !input.trim()}
            className="send-button"
          >
            {loading ? '⏳' : '➤'}
          </button>
        </div>
      </form>
    </div>
  )
}

export default ChatInterface
