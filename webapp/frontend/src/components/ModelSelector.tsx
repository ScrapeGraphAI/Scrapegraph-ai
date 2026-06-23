import { useEffect, useState } from 'react'
import type { ModelInfo } from '../types'
import { fetchModels } from '../lib/api'

interface Props {
  value: { provider: string; model: string; api_key: string; model_tokens: number }
  onChange: (v: Props['value']) => void
}

const KNOWN_PROVIDERS = [
  { id: 'ollama', label: 'Ollama', needsKey: false },
  { id: 'openai', label: 'OpenAI', needsKey: true },
  { id: 'deepseek', label: 'DeepSeek', needsKey: true },
  { id: 'anthropic', label: 'Anthropic', needsKey: true },
  { id: 'google_genai', label: 'Google GenAI', needsKey: true },
  { id: 'groq', label: 'Groq', needsKey: true },
  { id: 'mistralai', label: 'Mistral', needsKey: true },
  { id: 'xai', label: 'xAI', needsKey: true },
]

export default function ModelSelector({ value, onChange }: Props) {
  const [models, setModels] = useState<ModelInfo>({ ollama_models: [], providers: [] })

  useEffect(() => {
    fetchModels().then(setModels).catch(() => {})
  }, [])

  const providerInfo = KNOWN_PROVIDERS.find(p => p.id === value.provider)

  return (
    <div className="space-y-4">
      <h3 className="text-sm font-medium text-zinc-400 uppercase tracking-wider">Language Model</h3>
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-xs text-zinc-500 mb-1">Provider</label>
          <select
            value={value.provider}
            onChange={e => onChange({ ...value, provider: e.target.value, model: '', api_key: '' })}
            className="w-full bg-zinc-800 border border-zinc-700 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500"
          >
            {KNOWN_PROVIDERS.map(p => (
              <option key={p.id} value={p.id}>{p.label}</option>
            ))}
          </select>
        </div>
        <div>
          <label className="block text-xs text-zinc-500 mb-1">Model</label>
          {value.provider === 'ollama' && models.ollama_models.length > 0 ? (
            <select
              value={value.model}
              onChange={e => onChange({ ...value, model: e.target.value })}
              className="w-full bg-zinc-800 border border-zinc-700 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500"
            >
              <option value="">Select model...</option>
              {models.ollama_models.map(m => (
                <option key={m} value={m}>{m}</option>
              ))}
            </select>
          ) : (
            <input
              type="text"
              value={value.model}
              onChange={e => onChange({ ...value, model: e.target.value })}
              placeholder={value.provider === 'ollama' ? 'e.g. llama3.2 (ollama not running?)' : 'e.g. gpt-4o'}
              className="w-full bg-zinc-800 border border-zinc-700 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500 placeholder-zinc-600"
            />
          )}
        </div>
      </div>
      {providerInfo?.needsKey && (
        <div>
          <label className="block text-xs text-zinc-500 mb-1">API Key</label>
          <input
            type="password"
            value={value.api_key}
            onChange={e => onChange({ ...value, api_key: e.target.value })}
            placeholder={`${providerInfo.label} API key`}
            className="w-full bg-zinc-800 border border-zinc-700 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500 placeholder-zinc-600"
          />
        </div>
      )}
      <div>
        <label className="block text-xs text-zinc-500 mb-1">Model Tokens</label>
        <input
          type="number"
          value={value.model_tokens}
          onChange={e => onChange({ ...value, model_tokens: Number(e.target.value) })}
          className="w-full bg-zinc-800 border border-zinc-700 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500"
          min={1}
          max={128000}
        />
      </div>
    </div>
  )
}
