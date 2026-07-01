import { AlertTriangle, Cpu } from 'lucide-react'

export default function ModelCheck({ modelStatus, backendStatus }) {
  if (backendStatus === 'loading') return null
  if (backendStatus === 'disconnected') {
    return (
      <div className="bg-red-900/50 border-b border-red-800">
        <div className="container mx-auto px-4 py-3 max-w-7xl flex items-center gap-3">
          <AlertTriangle className="w-5 h-5 text-red-400 shrink-0" />
          <p className="text-sm text-red-300">
            Backend server is not running. Start it with{' '}
            <code className="bg-red-950 px-2 py-0.5 rounded text-red-200">
              uvicorn main:app --reload
            </code>{' '}
            from the backend/ directory.
          </p>
        </div>
      </div>
    )
  }

  if (modelStatus === false) {
    return (
      <div className="bg-yellow-900/50 border-b border-yellow-800">
        <div className="container mx-auto px-4 py-3 max-w-7xl flex items-center gap-3">
          <Cpu className="w-5 h-5 text-yellow-400 shrink-0" />
          <div className="text-sm text-yellow-300">
            <strong>Local model missing.</strong> Download a GGUF model (e.g., Phi-3 Mini Instruct) and
            place it in the{' '}
            <code className="bg-yellow-950 px-2 py-0.5 rounded text-yellow-200">models/</code> directory.
            Processing invoices requires a local LLM.
          </div>
        </div>
      </div>
    )
  }

  return null
}
