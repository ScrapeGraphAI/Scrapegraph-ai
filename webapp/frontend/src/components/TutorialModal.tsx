import { useEffect, useState } from 'react'

interface PageProps { setPage: (p: string) => void }

const STORAGE_KEY = 'scrapegraphai_tutorial_dismissed'

function Basics({ setPage }: PageProps) {
  return (
    <div className="space-y-5">
      <p className="text-zinc-400 text-sm leading-relaxed">
        ScrapeGraphAI is an <span className="text-emerald-400">LLM-powered web scraping</span> tool.
        Instead of writing complex selectors, you describe <em>what</em> you want in plain English.
      </p>

      <div className="bg-zinc-800/50 rounded-xl p-4 space-y-3">
        <h4 className="text-xs font-semibold text-zinc-300 uppercase tracking-wider">Quick Start</h4>
        <ol className="space-y-2 text-sm text-zinc-400">
          <li className="flex gap-2">
            <span className="text-emerald-500 font-bold shrink-0">1.</span>
            <span>Enter a <strong className="text-zinc-200">prompt</strong> describing what to extract</span>
          </li>
          <li className="flex gap-2">
            <span className="text-emerald-500 font-bold shrink-0">2.</span>
            <span>Paste the target <strong className="text-zinc-200">URL</strong></span>
          </li>
          <li className="flex gap-2">
            <span className="text-emerald-500 font-bold shrink-0">3.</span>
            <span>Pick an LLM <strong className="text-zinc-200">model</strong> (Ollama models are auto-detected)</span>
          </li>
          <li className="flex gap-2">
            <span className="text-emerald-500 font-bold shrink-0">4.</span>
            <span>Choose a <strong className="text-zinc-200">backend</strong> — see <button onClick={() => setPage('advanced')} className="text-emerald-400 underline underline-offset-2 hover:text-emerald-300">Advanced</button> for details</span>
          </li>
          <li className="flex gap-2">
            <span className="text-emerald-500 font-bold shrink-0">5.</span>
            <span>Click <strong className="text-zinc-200">Run Scraper</strong> and wait for the result</span>
          </li>
        </ol>
      </div>

      <div className="bg-zinc-800/30 border border-zinc-700/50 rounded-xl p-4">
        <h4 className="text-xs font-semibold text-zinc-300 uppercase tracking-wider mb-2">Example Prompt</h4>
        <code className="block text-sm text-emerald-300 bg-zinc-900 rounded-lg p-3 leading-relaxed">
          &quot;Extract all article titles and their publication dates from this blog page&quot;
        </code>
      </div>
    </div>
  )
}

function Advanced({ setPage }: PageProps) {
  return (
    <div className="space-y-5">
      {/* Backends */}
      <div>
        <h4 className="text-xs font-semibold text-zinc-300 uppercase tracking-wider mb-3">Backend Types</h4>
        <div className="space-y-3">
          <div className="bg-zinc-800/40 rounded-xl p-3 border-l-2 border-sky-500">
            <div className="flex items-center gap-2 mb-1">
              <span className="text-xs font-semibold text-sky-400">Playwright</span>
              <span className="text-2xs text-zinc-600 bg-zinc-800 px-1.5 py-0.5 rounded">default</span>
            </div>
            <p className="text-xs text-zinc-400 leading-relaxed">
              Full browser automation. Best for SPAs and JavaScript-heavy sites.
              Supports headless mode. Uses Chromium under the hood.
            </p>
          </div>
          <div className="bg-zinc-800/40 rounded-xl p-3 border-l-2 border-amber-500">
            <div className="flex items-center gap-2 mb-1">
              <span className="text-xs font-semibold text-amber-400">Crawl4AI</span>
              <span className="text-2xs text-zinc-600">experimental</span>
            </div>
            <p className="text-xs text-zinc-400 leading-relaxed">
              Specialized crawler optimized for AI-friendly output (Markdown, structured text).
              Supports custom output format and timeout configuration.
            </p>
          </div>
          <div className="bg-zinc-800/40 rounded-xl p-3 border-l-2 border-purple-500">
            <div className="flex items-center gap-2 mb-1">
              <span className="text-xs font-semibold text-purple-400">Obscura</span>
              <span className="text-2xs text-zinc-600">experimental</span>
            </div>
            <p className="text-xs text-zinc-400 leading-relaxed">
              CDP-based (Chrome DevTools Protocol) backend. Connects to an existing Chrome instance.
              Useful for authenticated sessions or when you need fine-grained browser control.
            </p>
          </div>
        </div>
      </div>

      {/* Models */}
      <div>
        <h4 className="text-xs font-semibold text-zinc-300 uppercase tracking-wider mb-3">Model Providers</h4>
        <div className="grid grid-cols-2 gap-2 text-xs">
          <div className="bg-zinc-800/30 rounded-lg p-2.5">
            <span className="text-zinc-200 font-medium">Ollama</span>
            <p className="text-zinc-500 mt-0.5">Local models, no API key needed. Auto-detected.</p>
          </div>
          <div className="bg-zinc-800/30 rounded-lg p-2.5">
            <span className="text-zinc-200 font-medium">OpenAI</span>
            <p className="text-zinc-500 mt-0.5">GPT-4o / GPT-4o-mini. Requires API key.</p>
          </div>
          <div className="bg-zinc-800/30 rounded-lg p-2.5">
            <span className="text-zinc-200 font-medium">Anthropic</span>
            <p className="text-zinc-500 mt-0.5">Claude 3.5 Sonnet / Haiku. Requires API key.</p>
          </div>
          <div className="bg-zinc-800/30 rounded-lg p-2.5">
            <span className="text-zinc-200 font-medium">DeepSeek</span>
            <p className="text-zinc-500 mt-0.5">DeepSeek-V3 / R1. API key required.</p>
          </div>
        </div>
        <p className="text-2xs text-zinc-600 mt-2">
          See <button onClick={() => setPage('pro-tips')} className="text-emerald-400 underline underline-offset-2 hover:text-emerald-300">Pro Tips</button> for model selection strategies.
        </p>
      </div>

      {/* Model Tokens */}
      <div className="bg-zinc-800/30 rounded-xl p-3">
        <h4 className="text-xs font-semibold text-zinc-300 uppercase tracking-wider mb-1">Model Tokens</h4>
        <p className="text-xs text-zinc-400 leading-relaxed">
          Controls the maximum context window. Higher values allow processing larger pages but use more VRAM.
          Typical ranges: 4096 (small), 8192 (default), 16384 (large pages), 32768+ (very large documents).
        </p>
      </div>
    </div>
  )
}

function Examples({ setPage }: PageProps) {
  return (
    <div className="space-y-4">
      <div className="bg-zinc-800/40 rounded-xl p-4 border-l-2 border-emerald-500">
        <h4 className="text-xs font-semibold text-emerald-400 mb-2">Extract Headings &amp; Paragraphs</h4>
        <p className="text-2xs text-zinc-500 mb-1.5">Prompt:</p>
        <code className="block text-xs text-zinc-200 bg-zinc-900 rounded-lg p-2.5 leading-relaxed">
          &quot;Extract the main heading and the first paragraph of the page content&quot;
        </code>
        <p className="text-2xs text-zinc-600 mt-2">
          Works on: <span className="text-zinc-400">example.com, most news sites, documentation pages</span>
        </p>
      </div>

      <div className="bg-zinc-800/40 rounded-xl p-4 border-l-2 border-sky-500">
        <h4 className="text-xs font-semibold text-sky-400 mb-2">Scrape Product Info</h4>
        <p className="text-2xs text-zinc-500 mb-1.5">Prompt:</p>
        <code className="block text-xs text-zinc-200 bg-zinc-900 rounded-lg p-2.5 leading-relaxed">
          &quot;Get the product name, price, description, and availability status from this product page&quot;
        </code>
        <p className="text-2xs text-zinc-600 mt-2">
          Tip: Use <button onClick={() => setPage('advanced')} className="text-emerald-400 underline underline-offset-2">Playwright backend</button> for JS-rendered e-commerce pages.
        </p>
      </div>

      <div className="bg-zinc-800/40 rounded-xl p-4 border-l-2 border-amber-500">
        <h4 className="text-xs font-semibold text-amber-400 mb-2">Extract Links</h4>
        <p className="text-2xs text-zinc-500 mb-1.5">Prompt:</p>
        <code className="block text-xs text-zinc-200 bg-zinc-900 rounded-lg p-2.5 leading-relaxed">
          &quot;Extract all links from this page as a JSON object with URL and anchor text&quot;
        </code>
      </div>

      <div className="bg-zinc-800/40 rounded-xl p-4 border-l-2 border-purple-500">
        <h4 className="text-xs font-semibold text-purple-400 mb-2">Structured Data Extraction</h4>
        <p className="text-2xs text-zinc-500 mb-1.5">Prompt:</p>
        <code className="block text-xs text-zinc-200 bg-zinc-900 rounded-lg p-2.5 leading-relaxed">
          &quot;Extract all job listings from this careers page. Return an array of objects with title, location, department, and apply_link&quot;
        </code>
        <p className="text-2xs text-zinc-600 mt-2">
          Pro Tip: Be explicit about the output structure in your prompt.
        </p>
      </div>
    </div>
  )
}

function ProTips({ setPage }: PageProps) {
  return (
    <div className="space-y-4">
      <div className="bg-zinc-800/30 rounded-xl p-3.5 border border-zinc-700/50">
        <div className="flex items-center gap-2 mb-1">
          <span className="text-emerald-400">⚡</span>
          <h4 className="text-xs font-semibold text-zinc-200">Craft Better Prompts</h4>
        </div>
        <p className="text-xs text-zinc-400 leading-relaxed">
          Be specific about format and structure. Instead of &quot;get page info&quot;, say
          &quot;extract the page title, meta description, and all h2 headings as a JSON array&quot;.
          The more structured your prompt, the better the output.
        </p>
      </div>

      <div className="bg-zinc-800/30 rounded-xl p-3.5 border border-zinc-700/50">
        <div className="flex items-center gap-2 mb-1">
          <span className="text-sky-400">🎯</span>
          <h4 className="text-xs font-semibold text-zinc-200">Model Selection Strategy</h4>
        </div>
        <ul className="text-xs text-zinc-400 space-y-1.5 list-disc list-inside">
          <li>Simple text extraction → lightweight models (llama3.2, qwen2.5:3b)</li>
          <li>Complex structured data → larger models (qwen3:4b, gemma3:4b)</li>
          <li>API-based models (GPT-4o, Claude) for the hardest tasks</li>
          <li>Run <code className="text-emerald-300 bg-zinc-900 px-1 rounded">ollama pull</code> in terminal to add more local models</li>
        </ul>
      </div>

      <div className="bg-zinc-800/30 rounded-xl p-3.5 border border-zinc-700/50">
        <div className="flex items-center gap-2 mb-1">
          <span className="text-amber-400">🔍</span>
          <h4 className="text-xs font-semibold text-zinc-200">Use the Debug Panel</h4>
        </div>
        <p className="text-xs text-zinc-400 leading-relaxed">
          Click the <span className="text-zinc-200">🐛 icon</span> (bottom-right) to open the log viewer.
          Filter by <strong className="text-zinc-300">ERROR</strong> and <strong className="text-zinc-300">WARNING</strong> levels to quickly diagnose issues.
          Enable <strong className="text-zinc-300">Auto-refresh</strong> to see logs in real-time during scraping.
        </p>
      </div>

      <div className="bg-zinc-800/30 rounded-xl p-3.5 border border-zinc-700/50">
        <div className="flex items-center gap-2 mb-1">
          <span className="text-purple-400">🌐</span>
          <h4 className="text-xs font-semibold text-zinc-200">Backend Selection Guide</h4>
        </div>
        <ul className="text-xs text-zinc-400 space-y-1.5 list-disc list-inside">
          <li><strong className="text-zinc-300">Playwright</strong> → general purpose, JS-heavy pages</li>
          <li><strong className="text-zinc-300">Crawl4AI</strong> → Markdown-friendly, faster for text sites</li>
          <li><strong className="text-zinc-300">Obscura</strong> → need control over browser (cookies, auth, CDP)</li>
          <li>Enable <strong className="text-zinc-300">Headless mode</strong> for automation; disable it to see what the browser is doing</li>
        </ul>
      </div>

      <div className="bg-zinc-800/30 rounded-xl p-3.5 border border-zinc-700/50">
        <div className="flex items-center gap-2 mb-1">
          <span className="text-emerald-400">🚀</span>
          <h4 className="text-xs font-semibold text-zinc-200">Token Budget Management</h4>
        </div>
        <p className="text-xs text-zinc-400 leading-relaxed">
          Set <button onClick={() => setPage('advanced')} className="text-emerald-400 underline underline-offset-2">Model Tokens</button> based on page size:
          4096 for short pages, 8192 (default) for most pages,
          16384+ for lengthy articles or documentation. Lower = faster + less VRAM.
        </p>
      </div>
    </div>
  )
}

const PAGES: Record<string, { title: string; component: React.FC<PageProps> }> = {
  basics: { title: 'Basics', component: Basics },
  advanced: { title: 'Advanced', component: Advanced },
  examples: { title: 'Examples', component: Examples },
  'pro-tips': { title: 'Pro Tips', component: ProTips },
}

export default function TutorialModal() {
  const [open, setOpen] = useState(false)
  const [dismissed, setDismissed] = useState(() => {
    try { return localStorage.getItem(STORAGE_KEY) === 'true' } catch { return false }
  })
  const [page, setPage] = useState('basics')
  const [dontShow, setDontShow] = useState(false)

  useEffect(() => {
    if (!dismissed) setOpen(true)
  }, [dismissed])

  const handleClose = () => {
    if (dontShow) {
      try { localStorage.setItem(STORAGE_KEY, 'true') } catch { }
      setDismissed(true)
    }
    setOpen(false)
  }

  const current = PAGES[page]

  return (
    <>
      {/* Floating help button */}
      <button
        onClick={() => { setOpen(true); setDontShow(false) }}
        className="fixed bottom-6 right-24 z-50 w-10 h-10 rounded-full shadow-lg bg-zinc-800 hover:bg-zinc-700 border border-zinc-700 transition-all flex items-center justify-center text-lg font-bold text-zinc-400 hover:text-zinc-200"
        title="Open tutorial"
      >
        ?
      </button>

      {open && (
        <div className="fixed inset-0 z-40 flex items-center justify-center p-4">
          <div className="absolute inset-0 bg-black/60" onClick={handleClose} />
          <div className="relative bg-zinc-900 border border-zinc-800 rounded-2xl shadow-2xl w-full max-w-2xl max-h-[85vh] flex flex-col">
            {/* Header */}
            <div className="flex items-center justify-between px-6 py-4 border-b border-zinc-800 shrink-0">
              <h2 className="text-sm font-semibold text-zinc-300 uppercase tracking-wider">Help &amp; Tutorial</h2>
              <button onClick={handleClose} className="text-xs text-zinc-600 hover:text-zinc-400 transition-colors">
                Close
              </button>
            </div>

            {/* Page tabs */}
            <div className="flex gap-1 px-6 py-3 border-b border-zinc-800 shrink-0 overflow-x-auto">
              {Object.entries(PAGES).map(([key, p]) => (
                <button
                  key={key}
                  onClick={() => setPage(key)}
                  className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors whitespace-nowrap ${
                    page === key
                      ? 'bg-emerald-600/20 text-emerald-400 border border-emerald-600/30'
                      : 'text-zinc-500 hover:text-zinc-300 hover:bg-zinc-800'
                  }`}
                >
                  {p.title}
                </button>
              ))}
            </div>

            {/* Content */}
            <div className="flex-1 overflow-y-auto px-6 py-5">
              {current && <current.component setPage={setPage} />}
            </div>

            {/* Footer */}
            <div className="flex items-center justify-between px-6 py-4 border-t border-zinc-800 shrink-0">
              <label className="flex items-center gap-2 text-xs text-zinc-500 cursor-pointer select-none">
                <input
                  type="checkbox"
                  checked={dontShow}
                  onChange={e => setDontShow(e.target.checked)}
                  className="rounded border-zinc-600 bg-zinc-800"
                />
                Don&apos;t show on startup
              </label>
              <button
                onClick={handleClose}
                className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 rounded-lg text-xs font-semibold text-white transition-colors"
              >
                Got it
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  )
}
