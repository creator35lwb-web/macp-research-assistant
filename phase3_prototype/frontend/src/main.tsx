import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'
import { registerWebMCPTools } from './webmcp.ts'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
)

// Register WebMCP tools after the app mounts
registerWebMCPTools().then((registered) => {
  if (registered) {
    console.log('[MACP] WebMCP tools active — agents can discover search_papers & analyze_paper')
  } else {
    console.log('[MACP] WebMCP not available. Tools accessible via window.macpTools in DevTools.')
  }
})
