import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8001'

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'multipart/form-data'
  }
})

// 请求拦截器
apiClient.interceptors.request.use(
  (config) => {
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    const message = error.response?.data?.detail || error.message || '请求失败'
    return Promise.reject(new Error(message))
  }
)

export interface VoicePreset {
  id: string
  name: string
  prompt_text: string
  audio_url: string
  created_at: string
}

export interface CreatePresetRequest {
  name: string
  prompt_text: string
  audio: File
}

export const presetApi = {
  /**
   * 获取所有预设
   */
  async getPresets(): Promise<VoicePreset[]> {
    const response = await apiClient.get<VoicePreset[]>('/api/presets')
    return response.data
  },

  /**
   * 获取单个预设
   */
  async getPreset(id: string): Promise<VoicePreset> {
    const response = await apiClient.get<VoicePreset>(`/api/presets/${id}`)
    return response.data
  },

  /**
   * 获取预设音频 URL
   */
  getPresetAudioUrl(id: string): string {
    return `${API_BASE_URL}/api/presets/${id}/audio`
  },

  /**
   * 创建预设 - 使用 FormData
   */
  async createPreset(data: CreatePresetRequest): Promise<VoicePreset> {
    const formData = new FormData()
    formData.append('name', data.name)
    formData.append('prompt_text', data.prompt_text)
    formData.append('audio', data.audio)

    const response = await apiClient.post<VoicePreset>('/api/presets', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })

    return response.data
  },

  /**
   * 更新预设
   */
  async updatePreset(id: string, data: Partial<VoicePreset>): Promise<VoicePreset> {
    const response = await apiClient.put<VoicePreset>(`/api/presets/${id}`, data)
    return response.data
  },

  /**
   * 删除预设
   */
  async deletePreset(id: string): Promise<void> {
    await apiClient.delete(`/api/presets/${id}`)
  }
}

export default presetApi
