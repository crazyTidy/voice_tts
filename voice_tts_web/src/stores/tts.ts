import { defineStore } from 'pinia'
import { ref, reactive, computed } from 'vue'
import type { AudioFile, VoicePreset, GenerationState } from '../types'

export const useTtsStore = defineStore('tts', () => {
  // 状态
  const state = reactive<GenerationState>({
    currentStep: 1,
    referenceAudio: null,
    promptText: '',
    synthesisText: '',
    generatedAudio: null,
    isGenerating: false,
    progress: 0,
    error: null
  })

  // 预设列表
  const presets = ref<VoicePreset[]>([])

  // 计算属性
  const canGoToStep2 = computed(() => state.referenceAudio !== null)
  const canGoToStep3 = computed(() => state.promptText.trim().length > 0)
  const canGoToStep4 = computed(() => {
    const text = state.synthesisText.trim()
    return text.length > 0 && text.length <= 500
  })

  // Actions
  function setStep(step: number) {
    state.currentStep = step
  }

  function setReferenceAudio(audio: AudioFile | null) {
    state.referenceAudio = audio
  }

  function setPromptText(text: string) {
    state.promptText = text
  }

  function setSynthesisText(text: string) {
    state.synthesisText = text
  }

  function setGeneratedAudio(audio: string | null) {
    state.generatedAudio = audio
  }

  function setGenerating(isGenerating: boolean) {
    state.isGenerating = isGenerating
  }

  function setProgress(progress: number) {
    state.progress = progress
  }

  function setError(error: string | null) {
    state.error = error
  }

  function reset() {
    state.currentStep = 1
    state.referenceAudio = null
    state.promptText = ''
    state.synthesisText = ''
    state.generatedAudio = null
    state.isGenerating = false
    state.progress = 0
    state.error = null
  }

  function loadPresets(presetsData: VoicePreset[]) {
    presets.value = presetsData
  }

  function addPreset(preset: VoicePreset) {
    presets.value.push(preset)
  }

  function deletePreset(id: string) {
    const index = presets.value.findIndex(p => p.id === id)
    if (index > -1) {
      presets.value.splice(index, 1)
    }
  }

  return {
    state,
    presets,
    canGoToStep2,
    canGoToStep3,
    canGoToStep4,
    setStep,
    setReferenceAudio,
    setPromptText,
    setSynthesisText,
    setGeneratedAudio,
    setGenerating,
    setProgress,
    setError,
    reset,
    loadPresets,
    addPreset,
    deletePreset
  }
})
