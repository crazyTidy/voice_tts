import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 300000,
  headers: {
    'Content-Type': 'application/json'
  }
})

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    const message = error.response?.data?.detail || error.message || '请求失败'
    return Promise.reject(new Error(message))
  }
)

export interface StreamChunk {
  type: 'chunk' | 'final'
  data?: string
  audio_url?: string
}

export const ttsApi = {
  async generateVoiceStream(
    text: string,
    promptText: string,
    audioFile: File,
    onChunk: (chunk: StreamChunk) => void
  ): Promise<void> {
    const formData = new FormData()
    formData.append('text', text)
    formData.append('prompt_text', promptText)
    formData.append('prompt_audio', audioFile)

    const response = await fetch(`${API_BASE_URL}/api/tts/generate/stream`, {
      method: 'POST',
      body: formData
    })

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`)
    }

    const reader = response.body?.getReader()
    const decoder = new TextDecoder()

    if (!reader) throw new Error('无法读取响应流')

    let buffer = ''
    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n')
      buffer = lines.pop() || ''

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const data = JSON.parse(line.slice(6))
            onChunk(data)
          } catch (e) {
            console.error('JSON parse error:', e, 'line:', line)
          }
        }
      }
    }
  }
}

export default ttsApi
