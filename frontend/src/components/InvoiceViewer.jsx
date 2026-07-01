import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism'
import {
  ArrowLeft, Download, FileJson, FileText as FileCsv, Trash2, Clock, Cpu, HardDrive, AlertCircle,
} from 'lucide-react'
import { getInvoice, deleteInvoice, getExportUrl } from '../api'

export default function InvoiceViewer() {
  const { id } = useParams()
  const [invoice, setInvoice] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [activeTab, setActiveTab] = useState('json')

  useEffect(() => {
    loadInvoice()
  }, [id])

  async function loadInvoice() {
    setLoading(true)
    setError(null)
    try {
      const data = await getInvoice(id)
      setInvoice(data)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  async function handleDelete() {
    if (!confirm('Delete this invoice?')) return
    try {
      await deleteInvoice(id)
      window.location.href = '/'
    } catch (e) {
      alert(e.message)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="animate-spin w-8 h-8 border-4 border-indigo-500 border-t-transparent rounded-full" />
      </div>
    )
  }

  if (error) {
    return (
      <div className="text-center py-20">
        <AlertCircle className="w-12 h-12 mx-auto mb-4 text-red-400" />
        <p className="text-red-300">{error}</p>
        <Link to="/" className="btn-secondary mt-4 inline-block">Back to Dashboard</Link>
      </div>
    )
  }

  let parsedJson = null
  try {
    parsedJson = JSON.parse(invoice.structured_json || '{}')
  } catch {
    parsedJson = { error: 'Invalid JSON', raw: invoice.structured_json }
  }

  const details = [
    { label: 'Status', value: invoice.status },
    { label: 'Filename', value: invoice.filename },
    { label: 'Created', value: new Date(invoice.created_at).toLocaleString() },
    { label: 'Processing Time', value: `${invoice.processing_time}s`, icon: Clock },
    { label: 'CPU Usage', value: `${invoice.cpu_usage}%`, icon: Cpu },
    { label: 'Memory', value: `${invoice.memory_usage} MB`, icon: HardDrive },
  ]

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Link to="/" className="p-2 hover:bg-gray-800 rounded-lg transition-colors">
            <ArrowLeft className="w-5 h-5 text-gray-500" />
          </Link>
          <div>
            <h1 className="text-xl font-bold">{invoice.vendor || 'Unnamed Invoice'}</h1>
            <p className="text-sm text-gray-500">
              {invoice.invoice_number && `#${invoice.invoice_number} · `}
              {invoice.invoice_date || ''}
              {invoice.grand_total && ` · Total: ${invoice.grand_total}`}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <a
            href={getExportUrl(id, 'json')}
            className="btn-secondary text-xs flex items-center gap-1.5"
            download
          >
            <FileJson className="w-3.5 h-3.5" /> JSON
          </a>
          <a
            href={getExportUrl(id, 'csv')}
            className="btn-secondary text-xs flex items-center gap-1.5"
            download
          >
            <FileCsv className="w-3.5 h-3.5" /> CSV
          </a>
          <a
            href={getExportUrl(id, 'ocr')}
            className="btn-secondary text-xs flex items-center gap-1.5"
            download
          >
            <Download className="w-3.5 h-3.5" /> OCR
          </a>
          <button onClick={handleDelete} className="btn-danger text-xs flex items-center gap-1.5">
            <Trash2 className="w-3.5 h-3.5" /> Delete
          </button>
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
        {details.map((d) => (
          <div key={d.label} className="card !p-4">
            <p className="text-xs text-gray-500 mb-1">{d.label}</p>
            <p className="text-sm font-medium text-gray-200">{String(d.value)}</p>
          </div>
        ))}
      </div>

      {invoice.status === 'error' && invoice.error_message && (
        <div className="bg-red-900/50 border border-red-800 rounded-xl p-4 flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-red-400 shrink-0 mt-0.5" />
          <p className="text-sm text-red-300">{invoice.error_message}</p>
        </div>
      )}

      <div className="card !p-0 overflow-hidden">
        <div className="flex border-b border-gray-800">
          <button
            onClick={() => setActiveTab('json')}
            className={`px-6 py-3 text-sm font-medium transition-colors ${
              activeTab === 'json'
                ? 'text-indigo-400 border-b-2 border-indigo-500 bg-indigo-500/5'
                : 'text-gray-500 hover:text-gray-300'
            }`}
          >
            Structured Data
          </button>
          <button
            onClick={() => setActiveTab('ocr')}
            className={`px-6 py-3 text-sm font-medium transition-colors ${
              activeTab === 'ocr'
                ? 'text-indigo-400 border-b-2 border-indigo-500 bg-indigo-500/5'
                : 'text-gray-500 hover:text-gray-300'
            }`}
          >
            Raw OCR Text
          </button>
        </div>

        <div className="p-4 max-h-[600px] overflow-auto">
          {activeTab === 'json' ? (
            <SyntaxHighlighter
              language="json"
              style={vscDarkPlus}
              customStyle={{
                background: 'transparent',
                padding: '0',
                margin: '0',
                fontSize: '0.85rem',
              }}
            >
              {JSON.stringify(parsedJson, null, 2)}
            </SyntaxHighlighter>
          ) : (
            <pre className="text-sm text-gray-300 whitespace-pre-wrap font-mono">
              {invoice.original_ocr || 'No OCR text available.'}
            </pre>
          )}
        </div>
      </div>
    </div>
  )
}
