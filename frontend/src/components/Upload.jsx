import { useState, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { useDropzone } from 'react-dropzone'
import { Upload as UploadIcon, File, X, CheckCircle, Loader, AlertCircle } from 'lucide-react'
import { uploadFile, processInvoice } from '../api'

const ACCEPTED = {
  'image/jpeg': ['.jpg', '.jpeg'],
  'image/png': ['.png'],
  'application/pdf': ['.pdf'],
}

export default function Upload() {
  const navigate = useNavigate()
  const [files, setFiles] = useState([])
  const [processing, setProcessing] = useState(false)
  const [progress, setProgress] = useState({ stage: '', percent: 0 })
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  const onDrop = useCallback((accepted) => {
    setFiles((prev) => [...prev, ...accepted.map((f) => Object.assign(f, { id: Math.random().toString(36) }))])
    setError(null)
    setResult(null)
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: ACCEPTED,
    maxSize: 50 * 1024 * 1024,
  })

  function removeFile(id) {
    setFiles((prev) => prev.filter((f) => f.id !== id))
  }

  async function handleProcess() {
    if (files.length === 0) return
    setProcessing(true)
    setError(null)
    setResult(null)

    const file = files[0]

    try {
      setProgress({ stage: 'Uploading file...', percent: 20 })
      const uploadRes = await uploadFile(file)

      setProgress({ stage: 'Running OCR...', percent: 40 })
      setProgress({ stage: 'Extracting data with AI...', percent: 60 })

      const processRes = await processInvoice(uploadRes.invoice_id)

      setProgress({ stage: 'Complete!', percent: 100 })
      setResult(processRes)

      setTimeout(() => {
        navigate(`/invoice/${uploadRes.invoice_id}`)
      }, 1500)
    } catch (e) {
      setError(e.message || 'Processing failed')
      setProgress({ stage: '', percent: 0 })
    } finally {
      setProcessing(false)
    }
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Upload Invoice</h1>

      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-xl p-12 text-center cursor-pointer transition-all ${
          isDragActive
            ? 'border-indigo-500 bg-indigo-500/10'
            : 'border-gray-700 hover:border-gray-600 hover:bg-gray-900/50'
        }`}
      >
        <input {...getInputProps()} />
        <UploadIcon className="w-12 h-12 mx-auto mb-4 text-gray-500" />
        {isDragActive ? (
          <p className="text-lg text-indigo-400">Drop your files here...</p>
        ) : (
          <>
            <p className="text-lg text-gray-400">
              Drag & drop invoice images or PDFs here
            </p>
            <p className="text-sm text-gray-600 mt-2">
              Supports JPG, PNG, JPEG, PDF (max 50MB)
            </p>
          </>
        )}
      </div>

      {files.length > 0 && (
        <div className="card space-y-3">
          <h3 className="text-sm font-medium text-gray-400">Selected Files</h3>
          {files.map((f) => (
            <div key={f.id} className="flex items-center justify-between bg-gray-800/50 rounded-lg px-4 py-3">
              <div className="flex items-center gap-3">
                <File className="w-5 h-5 text-indigo-400" />
                <div>
                  <p className="text-sm text-gray-200">{f.name}</p>
                  <p className="text-xs text-gray-500">{(f.size / 1024).toFixed(1)} KB</p>
                </div>
              </div>
              {!processing && (
                <button onClick={() => removeFile(f.id)} className="p-1 hover:bg-gray-700 rounded">
                  <X className="w-4 h-4 text-gray-500" />
                </button>
              )}
            </div>
          ))}

          <button
            onClick={handleProcess}
            disabled={processing}
            className="btn-primary w-full mt-2"
          >
            {processing ? 'Processing...' : `Process ${files.length} file${files.length > 1 ? 's' : ''}`}
          </button>
        </div>
      )}

      {processing && (
        <div className="card space-y-3">
          <div className="flex items-center gap-3">
            <Loader className="w-5 h-5 text-indigo-400 animate-spin" />
            <span className="text-sm text-gray-300">{progress.stage}</span>
          </div>
          <div className="w-full bg-gray-800 rounded-full h-2 overflow-hidden">
            <div
              className="h-full bg-indigo-600 rounded-full transition-all duration-500 ease-out"
              style={{ width: `${progress.percent}%` }}
            />
          </div>
        </div>
      )}

      {error && (
        <div className="bg-red-900/50 border border-red-800 rounded-xl p-4 flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-red-400 shrink-0 mt-0.5" />
          <div>
            <p className="text-sm font-medium text-red-300">Processing Failed</p>
            <p className="text-sm text-red-400 mt-1">{error}</p>
          </div>
        </div>
      )}

      {result && (
        <div className="bg-green-900/50 border border-green-800 rounded-xl p-4 flex items-center gap-3">
          <CheckCircle className="w-5 h-5 text-green-400" />
          <div>
            <p className="text-sm font-medium text-green-300">Processing Complete</p>
            <p className="text-sm text-green-400 mt-1">
              Processed in {result.processing_time}s. Redirecting...
            </p>
          </div>
        </div>
      )}

      <div className="card text-sm text-gray-500">
        <h3 className="text-xs font-medium uppercase tracking-wider text-gray-600 mb-2">Supported Formats</h3>
        <ul className="space-y-1">
          <li>• Images: JPG, JPEG, PNG</li>
          <li>• Documents: PDF (multi-page supported)</li>
          <li>• Maximum file size: 50 MB</li>
        </ul>
        <h3 className="text-xs font-medium uppercase tracking-wider text-gray-600 mt-4 mb-2">Requirements</h3>
        <ul className="space-y-1">
          <li>• Tesseract OCR must be installed on your system</li>
          <li>• A GGUF model must be present in the models/ directory</li>
        </ul>
      </div>
    </div>
  )
}
