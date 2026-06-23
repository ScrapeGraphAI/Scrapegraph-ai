import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import type { LogEntry } from '../types'
import { fetchLogs } from '../lib/api'

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || 'http://127.0.0.1:8000'

const LEVEL_COLORS: Record<string, string> = {
  DEBUG: 'text-zinc-400',
  INFO: 'text-sky-400',
  WARNING: 'text-amber-400',
  ERROR: 'text-red-400',
  CRITICAL: 'text-red-500 font-bold',
}

const LEVEL_BG: Record<string, string> = {
  DEBUG: 'bg-zinc-800/30',
  INFO: 'bg-sky-500/10',
  WARNING: 'bg-amber-500/10',
  ERROR: 'bg-red-500/10',
  CRITICAL: 'bg-red-500/20',
}

const ALL_LEVELS = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'] as const

function relativeTime(iso: string): string {
  const diff = Date.now() - new Date(iso).getTime()
  const sec = Math.floor(diff / 1000)
  if (sec < 10) return 'just now'
  if (sec < 60) return `${sec}s ago`
  const min = Math.floor(sec / 60)
  if (min < 60) return `${min}m ago`
  const hr = Math.floor(min / 60)
  if (hr < 24) return `${hr}h ago`
  return `${Math.floor(hr / 24)}d ago`
}

function formatTime(ts: string) {
  return new Date(ts).toLocaleTimeString('tr-TR', { hour12: false })
}

function copyToClipboard(text: string) {
  navigator.clipboard.writeText(text)
}

export default function LogViewer() {
  const [open, setOpen] = useState(false)
  const [logs, setLogs] = useState<LogEntry[]>([])
  const [levelFilter, setLevelFilter] = useState<Set<string>>(new Set(['WARNING', 'ERROR', 'CRITICAL']))
  const [moduleFilter, setModuleFilter] = useState<Set<string>>(new Set())
  const [searchQuery, setSearchQuery] = useState('')
  const [autoRefresh, setAutoRefresh] = useState(true)
  const [fullscreen, setFullscreen] = useState(false)
  const [userScrolledUp, setUserScrolledUp] = useState(false)
  const containerRef = useRef<HTMLDivElement>(null)
  const bottomRef = useRef<HTMLDivElement>(null)

  const filtered = useMemo(() => {
    let result = logs
    if (levelFilter.size > 0) {
      result = result.filter(e => levelFilter.has(e.level))
    }
    if (moduleFilter.size > 0) {
      result = result.filter(e => moduleFilter.has(e.module))
    }
    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase()
      result = result.filter(e =>
        e.message.toLowerCase().includes(q) ||
        e.module.toLowerCase().includes(q) ||
        e.level.toLowerCase().includes(q)
      )
    }
    return result
  }, [logs, levelFilter, moduleFilter, searchQuery])

  const availableModules = useMemo(() => {
    const set = new Set<string>()
    for (const e of logs) set.add(e.module)
    return Array.from(set).sort()
  }, [logs])

  const levelCounts = useMemo(() => {
    const counts: Record<string, number> = { DEBUG: 0, INFO: 0, WARNING: 0, ERROR: 0, CRITICAL: 0 }
    for (const e of logs) counts[e.level] = (counts[e.level] || 0) + 1
    return counts
  }, [logs])

  const fetchAndSet = useCallback(async () => {
    try {
      const levels = levelFilter.size > 0 ? Array.from(levelFilter) : undefined
      const data = await fetchLogs({ level: levels, limit: 500 })
      setLogs(data.reverse())
    } catch { }
  }, [levelFilter])

  useEffect(() => {
    if (!open) return
    fetchAndSet()
    if (!autoRefresh) return
    const interval = setInterval(fetchAndSet, 3000)
    return () => clearInterval(interval)
  }, [open, fetchAndSet, autoRefresh])

  // Auto-scroll to bottom only when user hasn't manually scrolled up
  useEffect(() => {
    if (open && !userScrolledUp) {
      bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
    }
  }, [filtered, open, userScrolledUp])

  const handleScroll = useCallback(() => {
    const el = containerRef.current
    if (!el) return
    const isNearBottom = el.scrollHeight - el.scrollTop - el.clientHeight < 60
    if (isNearBottom !== !userScrolledUp) {
      setUserScrolledUp(!isNearBottom)
    }
  }, [userScrolledUp])

  const toggleLevel = (level: string) => {
    const next = new Set(levelFilter)
    if (next.has(level)) next.delete(level)
    else next.add(level)
    setLevelFilter(next)
  }

  const toggleModule = (mod: string) => {
    const next = new Set(moduleFilter)
    if (next.has(mod)) next.delete(mod)
    else next.add(mod)
    setModuleFilter(next)
  }

  const clearLogs = async () => {
    try {
      await fetch(`${BACKEND_URL}/api/logs`, { method: 'DELETE' })
      setLogs([])
    } catch { }
  }

  return (
    <>
      {/* Floating button */}
      <button
        onClick={() => setOpen(!open)}
        className={`fixed bottom-6 right-6 z-50 w-14 h-14 rounded-full shadow-lg transition-all flex items-center justify-center text-xl font-bold ${
          open
            ? 'bg-red-600 hover:bg-red-500'
            : 'bg-zinc-800 hover:bg-zinc-700 border border-zinc-700'
        }`}
        title={open ? 'Close debug panel' : 'Open debug panel'}
      >
        {open ? '✕' : '🐛'}
      </button>

      {/* Modal */}
      {open && (
        <div className={`fixed inset-0 z-40 flex items-end sm:items-center justify-center p-4 ${fullscreen ? 'p-0' : ''}`}>
          <div className="absolute inset-0 bg-black/60" onClick={() => setOpen(false)} />
          <div className={`relative bg-zinc-900 border border-zinc-800 shadow-2xl flex flex-col ${
            fullscreen
              ? 'w-full h-full rounded-none'
              : 'w-full max-w-5xl max-h-[85vh] rounded-2xl'
          }`}>
            {/* Header */}
            <div className="flex items-center justify-between px-5 py-3 border-b border-zinc-800 shrink-0">
              <div className="flex items-center gap-3">
                <h2 className="text-sm font-semibold text-zinc-300 uppercase tracking-wider">Debug Logs</h2>
                <span className="text-xs text-zinc-600">{filtered.length} entries</span>
              </div>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => setFullscreen(!fullscreen)}
                  className="text-xs text-zinc-600 hover:text-zinc-400 transition-colors px-2 py-1"
                  title="Toggle fullscreen"
                >
                  {fullscreen ? '⊡' : '⊞'}
                </button>
                <label className="flex items-center gap-1.5 text-xs text-zinc-500 cursor-pointer select-none">
                  <input
                    type="checkbox"
                    checked={autoRefresh}
                    onChange={e => setAutoRefresh(e.target.checked)}
                    className="rounded border-zinc-600 bg-zinc-800"
                  />
                  Auto
                </label>
                <button
                  onClick={fetchAndSet}
                  className="text-xs text-zinc-500 hover:text-zinc-300 transition-colors px-2 py-1"
                >
                  Refresh
                </button>
                <button
                  onClick={clearLogs}
                  className="text-xs text-zinc-600 hover:text-red-400 transition-colors px-2 py-1"
                  title="Clear all logs"
                >
                  Clear
                </button>
                <button
                  onClick={() => setOpen(false)}
                  className="text-xs text-zinc-600 hover:text-zinc-400 transition-colors px-2 py-1"
                >
                  Close
                </button>
              </div>
            </div>

            {/* Level summary bar */}
            <div className="flex gap-1 px-5 py-2 border-b border-zinc-800/50 shrink-0">
              {ALL_LEVELS.map(l => {
                const count = levelCounts[l]
                const active = levelFilter.has(l)
                return (
                  <button
                    key={l}
                    onClick={() => toggleLevel(l)}
                    className={`flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-medium transition-all ${
                      active
                        ? `${LEVEL_BG[l]} ${LEVEL_COLORS[l]}`
                        : 'text-zinc-700 hover:text-zinc-500'
                    }`}
                  >
                    <span className={`w-1.5 h-1.5 rounded-full ${
                      active
                        ? l === 'DEBUG' ? 'bg-zinc-400' : l === 'INFO' ? 'bg-sky-400' : l === 'WARNING' ? 'bg-amber-400' : 'bg-red-400'
                        : 'bg-zinc-700'
                    }`} />
                    {l}
                    <span className={`ml-0.5 text-2xs ${active ? 'opacity-60' : 'opacity-40'}`}>{count}</span>
                  </button>
                )
              })}
            </div>

            {/* Search + module filter row */}
            <div className="flex items-center gap-2 px-5 py-2 border-b border-zinc-800/50 shrink-0">
              <div className="relative flex-1">
                <svg className="absolute left-2.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-zinc-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
                <input
                  type="text"
                  value={searchQuery}
                  onChange={e => setSearchQuery(e.target.value)}
                  placeholder="Search messages, modules, levels..."
                  className="w-full bg-zinc-800 border border-zinc-700 rounded-lg pl-8 pr-3 py-1.5 text-xs focus:outline-none focus:ring-1 focus:ring-emerald-500 placeholder-zinc-600"
                />
                {searchQuery && (
                  <button
                    onClick={() => setSearchQuery('')}
                    className="absolute right-2 top-1/2 -translate-y-1/2 text-zinc-600 hover:text-zinc-400 text-xs"
                  >
                    ✕
                  </button>
                )}
              </div>
              {moduleFilter.size > 0 && (
                <button
                  onClick={() => setModuleFilter(new Set())}
                  className="text-xs text-zinc-600 hover:text-zinc-400 whitespace-nowrap"
                  title="Clear module filter"
                >
                  Clear filter
                </button>
              )}
            </div>

            {/* Module filter chips */}
            {availableModules.length > 0 && (
              <div className="flex items-center gap-1.5 px-5 py-2 border-b border-zinc-800/50 shrink-0 overflow-x-auto">
                <span className="text-2xs text-zinc-600 mr-0.5 shrink-0">Modules:</span>
                {availableModules.map(mod => {
                  const active = moduleFilter.has(mod)
                  return (
                    <button
                      key={mod}
                      onClick={() => toggleModule(mod)}
                      className={`shrink-0 px-2 py-0.5 rounded text-2xs font-medium transition-colors ${
                        active
                          ? 'bg-emerald-600/20 text-emerald-400 border border-emerald-600/30'
                          : 'text-zinc-500 hover:text-zinc-300 border border-transparent hover:border-zinc-700'
                      }`}
                    >
                      {mod}
                    </button>
                  )
                })}
              </div>
            )}

            {/* Log entries */}
            <div
              ref={containerRef}
              onScroll={handleScroll}
              className="flex-1 overflow-auto font-mono text-xs"
            >
              {logs.length === 0 && (
                <p className="text-zinc-600 text-center py-12 text-sm font-sans">No log entries yet</p>
              )}
              {logs.length > 0 && filtered.length === 0 && (
                <p className="text-zinc-600 text-center py-12 text-sm font-sans">No entries match the current filters</p>
              )}
              <div className="p-2 space-y-0.5">
                {filtered.map((entry, i) => (
                  <LogEntryRow
                    key={`${entry.ts}-${i}`}
                    entry={entry}
                  />
                ))}
                <div ref={bottomRef} />
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  )
}

function LogEntryRow({ entry }: { entry: LogEntry }) {
  const [copied, setCopied] = useState(false)

  const handleCopy = () => {
    const text = `[${entry.ts}] [${entry.level}] [${entry.module}] ${entry.message}${entry.traceback ? '\n' + entry.traceback : ''}`
    copyToClipboard(text)
    setCopied(true)
    setTimeout(() => setCopied(false), 1500)
  }

  const msg = entry.message
  const mod = entry.module
  const time = formatTime(entry.ts)
  const relative = relativeTime(entry.ts)

  return (
    <div
      className={`group flex gap-2 py-1 px-3 rounded-lg transition-colors hover:bg-zinc-800/60 ${LEVEL_BG[entry.level] || ''}`}
    >
      {/* Timestamp */}
      <span className="text-zinc-600 shrink-0 w-14 text-right" title={new Date(entry.ts).toLocaleString('tr-TR')}>
        {time}
      </span>
      <span className="text-2xs text-zinc-700 shrink-0 w-10 text-right" title={new Date(entry.ts).toLocaleString('tr-TR')}>
        {relative}
      </span>

      {/* Level */}
      <span className={`shrink-0 w-14 ${LEVEL_COLORS[entry.level] || ''}`}>
        {entry.level}
      </span>

      {/* Module */}
      <span className="text-zinc-500 shrink-0 w-24 truncate" title={mod}>
        {mod}
      </span>

      {/* Message + optional traceback */}
      <span className="text-zinc-300 break-words min-w-0 flex-1 leading-relaxed">
        {msg}
        {entry.traceback && (
          <details className="inline">
            <summary className="ml-1 text-2xs text-zinc-600 cursor-pointer hover:text-zinc-400 inline align-middle select-none">
              ⓘ
            </summary>
            <pre className="mt-1 text-red-300/70 whitespace-pre-wrap text-2xs leading-relaxed bg-zinc-800/50 rounded-lg p-3 overflow-x-auto">
              {entry.traceback}
            </pre>
          </details>
        )}
      </span>

      {/* Copy button */}
      <button
        onClick={handleCopy}
        className="shrink-0 opacity-0 group-hover:opacity-100 transition-opacity text-zinc-600 hover:text-zinc-300 px-1"
        title="Copy entry"
      >
        {copied ? (
          <svg className="w-3.5 h-3.5 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
          </svg>
        ) : (
          <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
          </svg>
        )}
      </button>
    </div>
  )
}
