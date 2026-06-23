import { useState } from 'react'
import type { BackendType, ScrapeRequest, ScrapeResponse } from '../types'
import { scrape } from '../lib/api'
import ModelSelector from './ModelSelector'
import BackendSelector from './BackendSelector'
import ResultViewer from './ResultViewer'

export default function ScraperForm() {
  const [prompt, setPrompt] = useState('Extract the main heading and paragraph')
  const [source, setSource] = useState('https://example.com')
  const [llm, setLlm] = useState({ provider: 'ollama', model: '', api_key: '', model_tokens: 8192 })
  const [backend, setBackend] = useState<{
    type: BackendType
    headless: boolean
    output_format: string
    cdp_url: string
  }>({
    type: 'playwright',
    headless: true,
    output_format: 'markdown',
    cdp_url: 'ws://127.0.0.1:9222/devtools/browser',
  })
  const [result, setResult] = useState<ScrapeResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleScrape = async () => {
    setError('')
    setLoading(true)
    setResult(null)
    try {
      const body: ScrapeRequest = {
        prompt,
        source,
        llm: {
          provider: llm.provider,
          model: llm.model || (llm.provider === 'ollama' ? 'llama3.2' : 'gpt-4o'),
          api_key: llm.api_key || undefined,
          model_tokens: llm.model_tokens,
        },
        backend: {
          type: backend.type,
          headless: backend.headless,
        },
      }
      if (backend.type === 'crawl4ai') {
        body.backend.crawl4ai = { output_format: backend.output_format, headless: backend.headless, page_timeout: 30000 }
      }
      if (backend.type === 'obscura') {
        body.backend.obscura = { cdp_url: backend.cdp_url }
      }
      const res = await scrape(body)
      setResult(res)
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-8 space-y-8">
      <header className="text-center space-y-2">
        <h1 className="text-4xl font-bold tracking-tight">
          <span className="text-emerald-400">Scrape</span>GraphAI
        </h1>
        <p className="text-zinc-500">Enterprise-grade web scraping with LLM-powered extraction</p>
      </header>

      <div className="grid lg:grid-cols-2 gap-6">
        <div className="space-y-6">
          <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6 space-y-4">
            <div>
              <label className="block text-xs text-zinc-500 mb-1 uppercase tracking-wider">Prompt</label>
              <textarea
                value={prompt}
                onChange={e => setPrompt(e.target.value)}
                rows={3}
                className="w-full bg-zinc-800 border border-zinc-700 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500 placeholder-zinc-600 resize-none"
              />
            </div>
            <div>
              <label className="block text-xs text-zinc-500 mb-1 uppercase tracking-wider">Source URL</label>
              <input
                type="url"
                value={source}
                onChange={e => setSource(e.target.value)}
                placeholder="https://..."
                className="w-full bg-zinc-800 border border-zinc-700 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500 placeholder-zinc-600"
              />
            </div>
          </div>

          <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6">
            <ModelSelector value={llm} onChange={setLlm} />
          </div>

          <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6">
            <BackendSelector value={backend} onChange={setBackend} />
          </div>

          <button
            onClick={handleScrape}
            disabled={loading}
            className="w-full py-3 bg-emerald-600 hover:bg-emerald-500 disabled:bg-zinc-700 disabled:text-zinc-500 rounded-xl font-semibold text-base transition-colors"
          >
            {loading ? (
              <span className="flex items-center justify-center gap-2">
                <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                </svg>
                Scraping...
              </span>
            ) : (
              'Run Scraper'
            )}
          </button>

          {error && (
            <div className="bg-red-900/30 border border-red-800 rounded-xl p-4 text-sm text-red-300">
              {error}
            </div>
          )}
        </div>

        <div className="lg:sticky lg:top-8 h-fit">
          <ResultViewer result={result} loading={loading} />
        </div>
      </div>
    </div>
  )
}
