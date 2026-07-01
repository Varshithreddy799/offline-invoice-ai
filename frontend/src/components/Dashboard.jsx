import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { FileText, CheckCircle, XCircle, Clock, Search, Trash2, ExternalLink } from 'lucide-react'
import { getInvoices, getStats, deleteInvoice } from '../api'

export default function Dashboard() {
  const [stats, setStats] = useState(null)
  const [invoices, setInvoices] = useState([])
  const [searchQuery, setSearchQuery] = useState('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    loadData()
  }, [])

  async function loadData(query = '') {
    setLoading(true)
    setError(null)
    try {
      const [statsData, invoicesData] = await Promise.all([
        getStats(),
        getInvoices({ query, limit: 20 }),
      ])
      setStats(statsData)
      setInvoices(invoicesData)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  function handleSearch(e) {
    e.preventDefault()
    loadData(searchQuery)
  }

  async function handleDelete(id) {
    if (!confirm('Delete this invoice?')) return
    try {
      await deleteInvoice(id)
      loadData(searchQuery)
    } catch (e) {
      alert(e.message)
    }
  }

  const statCards = stats
    ? [
        { label: 'Total Invoices', value: stats.total, icon: FileText, color: 'text-blue-400', bg: 'bg-blue-500/10' },
        { label: 'Processed', value: stats.processed, icon: CheckCircle, color: 'text-green-400', bg: 'bg-green-500/10' },
        { label: 'Pending', value: stats.pending, icon: Clock, color: 'text-yellow-400', bg: 'bg-yellow-500/10' },
        { label: 'Failed', value: stats.failed, icon: XCircle, color: 'text-red-400', bg: 'bg-red-500/10' },
      ]
    : []

  if (loading && !stats) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="animate-spin w-8 h-8 border-4 border-indigo-500 border-t-transparent rounded-full" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Dashboard</h1>
        <Link to="/upload" className="btn-primary">
          + Upload Invoice
        </Link>
      </div>

      {error && (
        <div className="bg-red-900/50 border border-red-800 rounded-xl p-4 text-red-300 text-sm">
          {error}
        </div>
      )}

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {statCards.map((card) => {
          const Icon = card.icon
          return (
            <div key={card.label} className="card">
              <div className="flex items-center gap-3">
                <div className={`p-3 rounded-lg ${card.bg}`}>
                  <Icon className={`w-5 h-5 ${card.color}`} />
                </div>
                <div>
                  <p className="text-2xl font-bold text-white">{card.value}</p>
                  <p className="text-xs text-gray-500">{card.label}</p>
                </div>
              </div>
            </div>
          )
        })}
      </div>

      <div className="card">
        <form onSubmit={handleSearch} className="flex gap-3 mb-6">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
            <input
              type="text"
              className="input pl-10"
              placeholder="Search by vendor, invoice number, or date..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>
          <button type="submit" className="btn-primary">Search</button>
          {searchQuery && (
            <button
              type="button"
              className="btn-secondary"
              onClick={() => { setSearchQuery(''); loadData('') }}
            >
              Clear
            </button>
          )}
        </form>

        {invoices.length === 0 ? (
          <div className="text-center py-12 text-gray-500">
            <FileText className="w-12 h-12 mx-auto mb-3 opacity-50" />
            <p className="text-lg font-medium">No invoices yet</p>
            <p className="text-sm mt-1">Upload an invoice to get started.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-800 text-gray-500">
                  <th className="text-left py-3 px-2 font-medium">Vendor</th>
                  <th className="text-left py-3 px-2 font-medium">Invoice #</th>
                  <th className="text-left py-3 px-2 font-medium">Date</th>
                  <th className="text-right py-3 px-2 font-medium">Total</th>
                  <th className="text-center py-3 px-2 font-medium">Status</th>
                  <th className="text-right py-3 px-2 font-medium">Actions</th>
                </tr>
              </thead>
              <tbody>
                {invoices.map((inv) => (
                  <tr key={inv.id} className="border-b border-gray-800/50 hover:bg-gray-800/30 transition-colors">
                    <td className="py-3 px-2 text-gray-200">{inv.vendor || '-'}</td>
                    <td className="py-3 px-2 text-gray-400">{inv.invoice_number || '-'}</td>
                    <td className="py-3 px-2 text-gray-400">{inv.invoice_date || '-'}</td>
                    <td className="py-3 px-2 text-right text-gray-200">{inv.grand_total || '-'}</td>
                    <td className="py-3 px-2 text-center">
                      <span
                        className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium ${
                          inv.status === 'completed'
                            ? 'bg-green-500/10 text-green-400'
                            : inv.status === 'error'
                            ? 'bg-red-500/10 text-red-400'
                            : 'bg-yellow-500/10 text-yellow-400'
                        }`}
                      >
                        {inv.status === 'completed' && <CheckCircle className="w-3 h-3" />}
                        {inv.status === 'error' && <XCircle className="w-3 h-3" />}
                        {inv.status === 'pending' && <Clock className="w-3 h-3" />}
                        {inv.status}
                      </span>
                    </td>
                    <td className="py-3 px-2 text-right">
                      <div className="flex items-center justify-end gap-2">
                        <Link
                          to={`/invoice/${inv.id}`}
                          className="p-1.5 rounded-lg hover:bg-gray-700 text-gray-500 hover:text-gray-200 transition-colors"
                          title="View"
                        >
                          <ExternalLink className="w-4 h-4" />
                        </Link>
                        <button
                          onClick={() => handleDelete(inv.id)}
                          className="p-1.5 rounded-lg hover:bg-red-900/50 text-gray-500 hover:text-red-400 transition-colors"
                          title="Delete"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}
