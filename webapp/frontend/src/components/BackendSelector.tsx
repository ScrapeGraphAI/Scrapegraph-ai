import type { BackendType } from '../types'

interface Props {
  value: {
    type: BackendType
    headless: boolean
    output_format: string
    cdp_url: string
  }
  onChange: (v: Props['value']) => void
}

export default function BackendSelector({ value, onChange }: Props) {
  const isCrawl4ai = value.type === 'crawl4ai'
  const isObscura = value.type === 'obscura'

  return (
    <div className="space-y-4">
      <h3 className="text-sm font-medium text-zinc-400 uppercase tracking-wider">Backend</h3>
      <div className="flex gap-2">
        {(['playwright', 'crawl4ai', 'obscura'] as const).map(t => (
          <button
            key={t}
            onClick={() => onChange({ ...value, type: t })}
            className={`flex-1 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
              value.type === t
                ? 'bg-emerald-600 text-white'
                : 'bg-zinc-800 text-zinc-400 hover:bg-zinc-700'
            }`}
          >
            {t === 'playwright' ? 'Playwright' : t === 'crawl4ai' ? 'Crawl4AI' : 'Obscura'}
          </button>
        ))}
      </div>
      <label className="flex items-center gap-2 text-sm">
        <input
          type="checkbox"
          checked={value.headless}
          onChange={e => onChange({ ...value, headless: e.target.checked })}
          className="rounded bg-zinc-800 border-zinc-600"
        />
        Headless mode
      </label>
      {isCrawl4ai && (
        <div>
          <label className="block text-xs text-zinc-500 mb-1">Output Format</label>
          <select
            value={value.output_format}
            onChange={e => onChange({ ...value, output_format: e.target.value })}
            className="w-full bg-zinc-800 border border-zinc-700 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500"
          >
            <option value="markdown">Markdown</option>
            <option value="html">HTML</option>
            <option value="text">Text</option>
          </select>
        </div>
      )}
      {isObscura && (
        <div>
          <label className="block text-xs text-zinc-500 mb-1">CDP URL</label>
          <input
            type="text"
            value={value.cdp_url}
            onChange={e => onChange({ ...value, cdp_url: e.target.value })}
            className="w-full bg-zinc-800 border border-zinc-700 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500 placeholder-zinc-600"
          />
        </div>
      )}
    </div>
  )
}
