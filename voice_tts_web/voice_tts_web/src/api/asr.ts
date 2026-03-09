import request from './request'

export interface ASRRequest {
  audio_data: string
}

export interface ASRResponse {
  text: string
  message: string
}

export const transcribeAudio = (data: ASRRequest) => {
  return request.post<any, ASRResponse>('/api/asr/transcribe', data)
}
