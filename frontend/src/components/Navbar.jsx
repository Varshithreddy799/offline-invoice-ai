import { Link, useLocation } from 'react-router-dom'
import { FileText, Upload, LayoutDashboard, Activity } from 'lucide-react'

export default function Navbar({ backendStatus, modelStatus }) {
  const location = useLocation()

  const navLinks = [
    { to: '/', label: 'Dashboard', icon: LayoutDashboard },
    { to: '/upload', label: 'Upload', icon: Upload },
  ]

  return (
    <nav className="bg-gray-900 border-b border-gray-800 sticky top-0 z-50">
      <div className="container mx-auto px-4 max-w-7xl">
        <div className="flex items-center justify-between h-16">
          <Link to="/" className="flex items-center gap-3 group">
            <div className="w-9 h-9 rounded-lg bg-indigo-600 flex items-center justify-center">
              <FileText className="w-5 h-5 text-white" />
            </div>
            <span className="text-lg font-semibold text-white hidden sm:block">
              Offline Invoice AI
            </span>
          </Link>

          <div className="flex items-center gap-1">
            {navLinks.map((link) => {
              const Icon = link.icon
              const isActive = location.pathname === link.to
              return (
                <Link
                  key={link.to}
                  to={link.to}
                  className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                    isActive
                      ? 'bg-indigo-600/20 text-indigo-400'
                      : 'text-gray-400 hover:text-gray-200 hover:bg-gray-800'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  <span className="hidden sm:inline">{link.label}</span>
                </Link>
              )
            })}

            <div className="ml-4 flex items-center gap-2 pl-4 border-l border-gray-800">
              <div
                className={`w-2 h-2 rounded-full ${
                  backendStatus === 'connected'
                    ? modelStatus
                      ? 'bg-green-500'
                      : 'bg-yellow-500'
                    : 'bg-red-500'
                }`}
                title={
                  backendStatus === 'connected'
                    ? modelStatus
                      ? 'Model loaded'
                      : 'Model missing'
                    : 'Backend disconnected'
                }
              />
              <span className="text-xs text-gray-500 hidden sm:inline">
                {backendStatus === 'connected'
                  ? modelStatus
                    ? 'AI Ready'
                    : 'No Model'
                  : 'Offline'}
              </span>
            </div>
          </div>
        </div>
      </div>
    </nav>
  )
}
