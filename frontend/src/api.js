const BASE_URL = import.meta.env.VITE_API_URL || ''

export async function uploadFile(file, onProgress) {
  const formData = new FormData()
  formData.append('file', file)
  const res = await fetch(`${BASE_URL}/upload`, { method: 'POST', body: formData })
  if (!res.ok) {
    const err = await res.json()
    throw new Error(err.detail || 'Upload failed')
  }
  return res.json()
}

export async function processInvoice(id) {
  const res = await fetch(`${BASE_URL}/process/${id}`, { method: 'POST' })
  if (!res.ok) {
    const err = await res.json()
    throw new Error(err.detail || 'Processing failed')
  }
  return res.json()
}

export async function getInvoices(params = {}) {
  const query = new URLSearchParams()
  if (params.query) query.set('query', params.query)
  if (params.limit) query.set('limit', params.limit)
  if (params.offset) query.set('offset', params.offset)
  const url = `${BASE_URL}/invoices${query.toString() ? '?' + query.toString() : ''}`
  const res = await fetch(url)
  if (!res.ok) throw new Error('Failed to fetch invoices')
  return res.json()
}

export async function getInvoice(id) {
  const res = await fetch(`${BASE_URL}/invoice/${id}`)
  if (!res.ok) throw new Error('Invoice not found')
  return res.json()
}

export async function deleteInvoice(id) {
  const res = await fetch(`${BASE_URL}/invoice/${id}`, { method: 'DELETE' })
  if (!res.ok) throw new Error('Failed to delete invoice')
  return res.json()
}

export async function getStats() {
  const res = await fetch(`${BASE_URL}/stats`)
  if (!res.ok) throw new Error('Failed to fetch stats')
  return res.json()
}

export async function healthCheck() {
  const res = await fetch(`${BASE_URL}/health`)
  if (!res.ok) throw new Error('Backend unreachable')
  return res.json()
}

export function getExportUrl(id, type) {
  return `${BASE_URL}/invoice/${id}/export/${type}`
}
