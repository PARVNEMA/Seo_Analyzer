import { useState, useEffect, useRef } from 'react'
import './index.css'

interface PageResult {
  url: string;
  title: string | null;
  meta_description: string | null;
  headers: Record<string, string[]>;
  total_images: number;
  missing_alt_images: number;
  total_links: number;
  broken_links: number;
}

function App() {
  const [targetUrl, setTargetUrl] = useState('')
  const [jobId, setJobId] = useState<string | null>(null)
  const [status, setStatus] = useState<string>('idle')
  const [results, setResults] = useState<PageResult[]>([])
  
  const ws = useRef<WebSocket | null>(null)

  useEffect(() => {
    if (!jobId) return;

    // Connect to WebSocket
    ws.current = new WebSocket(`ws://localhost:8000/api/v1/ws/crawls/${jobId}`)
    
    ws.current.onopen = () => {
      console.log('Connected to WebSocket')
    }

    ws.current.onmessage = (event) => {
      const data = JSON.parse(event.data)
      setResults(prev => [...prev, data])
    }

    ws.current.onclose = () => {
      console.log('Disconnected from WebSocket')
      setStatus(prev => prev === 'stopped' ? 'stopped' : 'completed')
    }

    return () => {
      if (ws.current) {
        ws.current.close()
      }
    }
  }, [jobId])

  const startCrawl = async (type: 'crawl' | 'crawl-seo') => {
    if (!targetUrl) return;
    setStatus('starting')
    setResults([])
    setJobId(null)

    try {
      const response = await fetch(`http://localhost:8000/api/v1/crawler/${type}?target_url=${encodeURIComponent(targetUrl)}`, {
        method: 'POST'
      })
      const data = await response.json()
      setJobId(data.job_id)
      setStatus('running')
    } catch (err) {
      console.error(err)
      setStatus('failed')
    }
  }

  const stopCrawl = () => {
    if (ws.current && ws.current.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify({ action: 'stop' }))
      setStatus('stopped')
    }
  }

  return (
    <div className="container">
      <div className="glass-panel">
        <h1>AI SEO Analyzer</h1>
        <p>Enter a URL to crawl the entire website and perform deep SEO analysis.</p>
        
        <div className="form-group">
          <input 
            type="url" 
            placeholder="https://example.com" 
            value={targetUrl}
            onChange={(e) => setTargetUrl(e.target.value)}
          />
          <button onClick={() => startCrawl('crawl')} disabled={status === 'running'}>Crawl Map</button>
          <button className="secondary" onClick={() => startCrawl('crawl-seo')} disabled={status === 'running'}>Crawl + SEO</button>
          {status === 'running' && (
            <button className="danger" onClick={stopCrawl} style={{backgroundColor: '#ef4444', color: 'white'}}>Stop Crawl</button>
          )}
        </div>

        {status !== 'idle' && (
          <div style={{ marginTop: '2rem' }}>
            <h2>Status: {status.toUpperCase()}</h2>
            <p>Pages Crawled: {results.length}</p>
          </div>
        )}
      </div>

      {results.length > 0 && (
        <div className="grid">
          {results.map((res, i) => (
            <div key={i} className="glass-panel progress-item">
              <h3>{res.title || 'Untitled Page'}</h3>
              <a href={res.url} target="_blank" rel="noreferrer" style={{color: 'var(--primary-color)'}}>{res.url}</a>
              
              <div className="metric-grid">
                <div className="metric">
                  <div className="metric-val">{res.total_images}</div>
                  <div className="metric-label">Images</div>
                </div>
                <div className="metric">
                  <div className="metric-val" style={{color: res.missing_alt_images > 0 ? '#ef4444' : '#22c55e'}}>{res.missing_alt_images}</div>
                  <div className="metric-label">Missing Alt</div>
                </div>
                <div className="metric">
                  <div className="metric-val">{res.total_links}</div>
                  <div className="metric-label">Links</div>
                </div>
                <div className="metric">
                  <div className="metric-val" style={{color: res.meta_description ? '#22c55e' : '#ef4444'}}>
                    {res.meta_description ? 'Yes' : 'No'}
                  </div>
                  <div className="metric-label">Meta Desc</div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default App
