import React, { useState } from 'react'
import './CodeDisplay.css'

function CodeDisplay({ source }) {
  const [expanded, setExpanded] = useState(false)

  const truncateCode = (code, maxLines = 5) => {
    const lines = code.split('\n')
    if (lines.length > maxLines) {
      return {
        truncated: lines.slice(0, maxLines).join('\n'),
        isTruncated: true,
        totalLines: lines.length
      }
    }
    return {
      truncated: code,
      isTruncated: false,
      totalLines: lines.length
    }
  }

  const { truncated, isTruncated, totalLines } = truncateCode(source.content)

  return (
    <div className="code-display">
      <div className="code-header">
        <span className="file-name">{source.source}</span>
        <span className="file-type">{source.file_type}</span>
      </div>
      <pre className="code-block">
        <code>{expanded ? source.content : truncated}</code>
      </pre>
      {isTruncated && (
        <button
          className="expand-btn"
          onClick={() => setExpanded(!expanded)}
        >
          {expanded ? '▼ Collapse' : `▶ Show ${totalLines} lines`}
        </button>
      )}
    </div>
  )
}

export default CodeDisplay
