export interface AudioFile {
  file: File
  url: string
  duration?: number
}

export interface VoicePreset {
  id: string
  name: string
  audio_path: string
  prompt_text: string
  created_at: string
}

export interface GenerationState {
  currentStep: number
  referenceAudio: AudioFile | null
  promptText: string
  synthesisText: string
  generatedAudio: string | null
  isGenerating: boolean
  progress: number
  error: string | null
}
