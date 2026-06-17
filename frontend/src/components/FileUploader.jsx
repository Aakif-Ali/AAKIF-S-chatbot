import React, { useState } from 'react'
import axios from 'axios'
import './FileUploader.css'

function FileUploader({ onUploadSuccess }) {
  const [uploadMethod, setUploadMethod] = useState('file')
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState(null)
  const [fileInput, setFileInput] = useState(null)
  const [textInput, setTextInput] = useState('')
  const [directoryPath, setDirectoryPath] = useState('')
  const [messageType, setMessageType] = useState('info')

  const handleFileUpload = async (e) => {
    const file = e.target.files[0]
    if (!file) return

    setLoading(true)
    setMessage(null)

    const formData = new FormData()
    formData.append('file', file)

    try {
      const response = await axios.post('/api/ingest/file', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })

      setMessageType('success')
      setMessage(`✅ Successfully uploaded ${file.name}!\nProcessed ${response.data.chunks_created} code chunks.`)
      setFileInput(null)
      setTimeout(onUploadSuccess, 1500)
    } catch (error) {
      setMessageType('error')
      setMessage(`❌ Error: ${error.response?.data?.error || error.message}`)
    } finally {
      setLoading(false)
    }
  }

  const handleTextSubmit = async () => {
    if (!textInput.trim()) {
      setMessageType('warning')
      setMessage('⚠️ Please enter some code')
      return
    }

    setLoading(true)
    setMessage(null)

    try {
      const response = await axios.post('/api/ingest/text', {
        code: textInput,
        language: 'unknown'
      })

      setMessageType('success')
      setMessage(`✅ Successfully ingested code!\nProcessed ${response.data.chunks_created} code chunks.`)
      setTextInput('')
      setTimeout(onUploadSuccess, 1500)
    } catch (error) {
      setMessageType('error')
      setMessage(`❌ Error: ${error.response?.data?.error || error.message}`)
    } finally {
      setLoading(false)
    }
  }

  const handleDirectorySubmit = async () => {
    if (!directoryPath.trim()) {
      setMessageType('warning')
      setMessage('⚠️ Please enter a directory path')
      return
    }

    setLoading(true)
    setMessage(null)

    try {
      const response = await axios.post('/api/ingest/directory', {
        directory_path: directoryPath
      })

      setMessageType('success')
      setMessage(
        `✅ Successfully ingested directory!\nDocuments: ${response.data.documents_processed}, Chunks: ${response.data.chunks_created}`
      )
      setDirectoryPath('')
      setTimeout(onUploadSuccess, 1500)
    } catch (error) {
      setMessageType('error')
      setMessage(`❌ Error: ${error.response?.data?.error || error.message}`)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="file-uploader">
      <div className="upload-tabs">
        <button
          className={`upload-tab ${uploadMethod === 'file' ? 'active' : ''}`}
          onClick={() => setUploadMethod('file')}
        >
          📄 File Upload
        </button>
        <button
          className={`upload-tab ${uploadMethod === 'text' ? 'active' : ''}`}
          onClick={() => setUploadMethod('text')}
        >
          ✏️ Paste Code
        </button>
        <button
          className={`upload-tab ${uploadMethod === 'directory' ? 'active' : ''}`}
          onClick={() => setUploadMethod('directory')}
        >
          📁 Directory
        </button>
      </div>

      {message && (
        <div className={`message-box ${messageType}`}>
          {message}
        </div>
      )}

      <div className="upload-content">
        {uploadMethod === 'file' && (
          <div className="upload-section">
            <h3>Upload Code File</h3>
            <div className="file-input-wrapper">
              <label htmlFor="file-input" className="file-label">
                <span className="upload-icon">📤</span>
                <span className="upload-text">
                  {fileInput ? fileInput.name : 'Click to select a file or drag & drop'}
                </span>
                <input
                  id="file-input"
                  type="file"
                  onChange={handleFileUpload}
                  disabled={loading}
                  className="file-input"
                />
              </label>
            </div>
            <p className="file-hint">Supported: Python, JavaScript, Java, Go, C++, and more</p>
          </div>
        )}

        {uploadMethod === 'text' && (
          <div className="upload-section">
            <h3>Paste Code</h3>
            <textarea
              value={textInput}
              onChange={(e) => setTextInput(e.target.value)}
              placeholder="Paste your code here..."
              className="code-textarea"
              disabled={loading}
            />
            <button
              onClick={handleTextSubmit}
              disabled={loading || !textInput.trim()}
              className="submit-btn"
            >
              {loading ? '⏳ Processing...' : '➤ Ingest Code'}
            </button>
          </div>
        )}

        {uploadMethod === 'directory' && (
          <div className="upload-section">
            <h3>Ingest Directory</h3>
            <input
              type="text"
              value={directoryPath}
              onChange={(e) => setDirectoryPath(e.target.value)}
              placeholder="Enter absolute path to directory (e.g., /home/user/myproject/src)"
              className="directory-input"
              disabled={loading}
            />
            <button
              onClick={handleDirectorySubmit}
              disabled={loading || !directoryPath.trim()}
              className="submit-btn"
            >
              {loading ? '⏳ Processing...' : '➤ Ingest Directory'}
            </button>
            <p className="file-hint">Will recursively process all supported code files in the directory</p>
          </div>
        )}
      </div>
    </div>
  )
}

export default FileUploader
