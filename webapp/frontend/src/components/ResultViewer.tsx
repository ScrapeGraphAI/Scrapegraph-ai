import { useState } from 'react'
import type { ScrapeResponse } from '../types'

interface Props {
  result: ScrapeResponse | null
  loading: boolean
}

export default function ResultViewer({ result, loading }: Props) {
  if (loading) {
    return (
      <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6">
        <h3 className="text-sm font-medium text-zinc-400 uppercase tracking-wider mb-4">Result</h3>
        <div className="animate-pulse space-y-3">
          <div className="h-4 bg-zinc-800 rounded w-3/4" />
          <div className="h-4 bg-zinc-800 rounded w-1/2" />
          <div className="h-4 bg-zinc-800 rounded w-5/6" />
        </div>
      </div>
    )
  }

  if (!result) {
    return (
      <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6">
        <h3 className="text-sm font-medium text-zinc-400 uppercase tracking-wider mb-4">Result</h3>
        <p className="text-zinc-600 text-sm">Configure your scraping job and click <span className="text-zinc-400">Run Scraper</span></p>
      </div>
    )
  }

  if (result.status === 'error') {
    return (
      <div className="bg-zinc-900 border border-red-800/50 rounded-xl p-6 space-y-3">
        <h3 className="text-sm font-medium text-red-400 uppercase tracking-wider">Error</h3>
        <pre className="text-sm text-red-300 whitespace-pre-wrap font-mono">{result.error}</pre>
      </div>
    )
  }

  const json = JSON.stringify(result.data, null, 2)
  const [showRaw, setShowRaw] = useState(false)

  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6 space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-medium text-emerald-400 uppercase tracking-wider">Result</h3>
        <button
          onClick={() => setShowRaw(!showRaw)}
          className="text-xs text-zinc-500 hover:text-zinc-300 transition-colors"
        >
          {showRaw ? 'Formatted' : 'Raw JSON'}
        </button>
      </div>
      {showRaw ? (
        <pre className="text-sm text-zinc-300 whitespace-pre-wrap font-mono bg-zinc-800/50 rounded-lg p-4 max-h-[70vh] overflow-auto">{json}</pre>
      ) : (
        <div className="max-h-[70vh] overflow-auto space-y-2">
          {renderData(result.data)}
        </div>
      )}
    </div>
  )
}

function renderData(data: unknown, depth = 0): React.ReactNode {
  if (data === null || data === undefined) return <span className="text-zinc-500">null</span>
  if (typeof data === 'string') return <span className="text-emerald-300">&quot;{data}&quot;</span>
  if (typeof data === 'number' || typeof data === 'boolean') return <span className="text-sky-300">{String(data)}</span>
  if (Array.isArray(data)) {
    return (
      <div className="space-y-1">
        {data.map((item, i) => (
          <div key={i} className="flex gap-2" style={{ paddingLeft: depth > 0 ? 12 : 0 }}>
            <span className="text-zinc-600 text-xs mt-1 shrink-0">{i}.</span>
            <div>{renderData(item, depth + 1)}</div>
          </div>
        ))}
      </div>
    )
  }
  if (typeof data === 'object') {
    return (
      <div className="space-y-2">
        {Object.entries(data as Record<string, unknown>).map(([key, val]) => (
          <div key={key} className="border-l-2 border-zinc-800 pl-3">
            <div className="text-xs text-zinc-500 font-mono mb-0.5">{key}</div>
            <div className="text-sm">{renderData(val, depth + 1)}</div>
          </div>
        ))}
      </div>
    )
  }
  return <span>{String(data)}</span>
}
