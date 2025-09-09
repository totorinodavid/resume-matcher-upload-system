export default function HomePage() {
  return (
    <div style={{ padding: '0', fontFamily: 'Arial, sans-serif' }}>
      <div style={{background:'#f59e0b', color:'#000', textAlign:'center', fontWeight:700, padding:'10px 0'}}>
        LIVE TEST BANNER v3 — Backend
      </div>
      <div style={{ padding: '2rem' }}>
      <h1>🚀 Upload System Backend</h1>
      <p>Status: <span style={{ color: 'green', fontWeight: 'bold' }}>RUNNING</span></p>
      <p>Service: Resume Matcher Upload Backend</p>
      <p>Version: 1.0.0</p>
      <p>Deployment: SUCCESS</p>
      
      <h2>Available Endpoints:</h2>
      <ul>
        <li><a href="/api/health">/api/health</a> - Health Check</li>
        <li>/api/uploads - Upload Management</li>
        <li>/api/files - File Operations</li>
      </ul>
      </div>
    </div>
  )
}
