export type BackendType = 'playwright' | 'crawl4ai' | 'obscura'

export interface LLMConfig {
  provider: string
  model: string
  api_key?: string
  model_tokens: number
}

export interface Crawl4AIConfig {
  output_format: string
  headless: boolean
  page_timeout: number
}

export interface ObscuraConfig {
  cdp_url: string
  auto_start?: string
}

export interface BackendConfig {
  type: BackendType
  headless: boolean
  proxy?: Record<string, string>
  crawl4ai?: Crawl4AIConfig
  obscura?: ObscuraConfig
}

export interface ScrapeRequest {
  prompt: string
  source: string
  llm: LLMConfig
  backend: BackendConfig
}

export interface ScrapeResponse {
  status: 'success' | 'error'
  data: unknown
  error?: string
  execution_info?: Record<string, unknown>
}

export interface ModelInfo {
  ollama_models: string[]
  providers: string[]
}

export interface LogEntry {
  ts: string
  level: 'DEBUG' | 'INFO' | 'WARNING' | 'ERROR' | 'CRITICAL'
  module: string
  message: string
  traceback?: string
}
