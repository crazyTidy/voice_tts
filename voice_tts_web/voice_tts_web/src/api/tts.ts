import request from './request'

export interface TTSRequest {
  text: string
  prompt_text?: string
  prompt_speech_16k?: string
}

export interface TTSResponse {
  audio_data: string
  sample_rate: number
  message: string
}

export const generateSpeech = (data: TTSRequest) => {
  return request.post<any, TTSResponse>('/api/tts/generate', data)
}

export const generateSpeechStream = (formData: FormData) => {
  return request.post<any, TTSResponse>('/api/tts/generate/stream', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}
