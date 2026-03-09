import request from './request'

export interface Preset {
  id: string
  name: string
  prompt_text: string
  audio_path: string
  created_at: string
}

export interface PresetCreateRequest {
  name: string
  prompt_text: string
  audio_data: string
}

export const listPresets = () => {
  return request.get<any, { presets: Preset[] }>('/api/presets')
}

export const createPreset = (data: PresetCreateRequest) => {
  return request.post<any, Preset>('/api/presets', data)
}

export const deletePreset = (id: string) => {
  return request.delete(`/api/presets/${id}`)
}

export const getPresetAudio = (id: string) => {
  return request.get<any, { audio_data: string }>(`/api/presets/${id}/audio`)
}
