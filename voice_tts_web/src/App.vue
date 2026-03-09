<template>
  <div id="app">
    <header class="app-header">
      <h1 class="app-title">智能语音克隆演示系统</h1>
    </header>

    <main class="app-main">
      <StepIndicator :current-step="store.state.currentStep" />

      <div class="step-content">
        <!-- Step 1: Upload Audio -->
        <Step1AudioUpload
          v-if="store.state.currentStep === 1"
          @next="handleStep1Next"
          @load-preset="handleLoadPreset"
        />

        <!-- Step 2: Input Prompt Text -->
        <Step2PromptText
          v-if="store.state.currentStep === 2"
          :reference-audio="store.state.referenceAudio"
          :asr-enabled="asrEnabled"
          :initial-text="store.state.promptText"
          @prev="handleStep2Prev"
          @next="handleStep2Next"
        />

        <!-- Step 3: Input Synthesis Text -->
        <Step3SynthesisText
          v-if="store.state.currentStep === 3"
          :prompt-text="store.state.promptText"
          @prev="handleStep3Prev"
          @next="handleStep3Next"
        />

        <!-- Step 4: Generate -->
        <Step4Generate
          v-if="store.state.currentStep === 4"
          :prompt-text="store.state.promptText"
          :synthesis-text="store.state.synthesisText"
          :reference-audio="store.state.referenceAudio"
          @prev="handleStep4Prev"
          @restart="handleRestart"
        />
      </div>
    </main>

    <footer class="app-footer">
      <p>基于 Fun-CosyVoice3-0.5B-2512 API 实现</p>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useTtsStore } from './stores/tts'
import StepIndicator from './components/StepIndicator.vue'
import Step1AudioUpload from './components/Step1AudioUpload.vue'
import Step2PromptText from './components/Step2PromptText.vue'
import Step3SynthesisText from './components/Step3SynthesisText.vue'
import Step4Generate from './components/Step4Generate.vue'
import type { AudioFile } from './types'
import type { VoicePreset } from './api/preset'

const store = useTtsStore()

// TODO: 从环境变量或配置读取
const asrEnabled = false

// Step 1 handlers
function handleStep1Next(audio: AudioFile) {
  store.setReferenceAudio(audio)
  store.setStep(2)
}

// 处理预设加载：自动填充音频和文本，跳转到步骤3
async function handleLoadPreset(preset: VoicePreset) {
  // 获取音频文件
  const audioUrl = preset.audio_url.startsWith('http')
    ? preset.audio_url
    : `${import.meta.env.VITE_API_BASE_URL}${preset.audio_url}`

  try {
    const response = await fetch(audioUrl)
    const blob = await response.blob()
    const url = URL.createObjectURL(blob)
    const file = new File([blob], `preset_${preset.id}.wav`, { type: blob.type })

    // 设置音频和文本
    store.setReferenceAudio({ file, url })
    store.setPromptText(preset.prompt_text)

    // 跳转到步骤3
    store.setStep(3)
  } catch (error) {
    console.error('加载预设失败:', error)
  }
}

// Step 2 handlers
function handleStep2Prev() {
  store.setStep(1)
}

function handleStep2Next(text: string) {
  store.setPromptText(text)
  store.setStep(3)
}

// Step 3 handlers
function handleStep3Prev() {
  store.setStep(2)
}

function handleStep3Next(text: string) {
  store.setSynthesisText(text)
  store.setStep(4)
}

// Step 4 handlers
function handleStep4Prev() {
  store.setStep(3)
}

function handleRestart() {
  store.reset()
}
</script>

<style>
/* ========================================
   App Layout - Anthropic Brand Styling
   ======================================== */

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

#app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  /* Anthropic brand gradient - using Orange to Blue transition */
  background: linear-gradient(135deg, var(--color-accent-orange) 0%, var(--color-accent-blue) 100%);
}

/* ========================================
   Header
   ======================================== */
.app-header {
  padding: var(--spacing-xl) var(--spacing-lg);
  text-align: center;
}

.app-title {
  font-size: 32px;
  font-weight: 700;
  font-family: var(--font-heading);
  color: var(--color-light);
  text-shadow: 0 2px 8px rgba(20, 20, 19, 0.15);
  letter-spacing: -0.02em;
}

/* ========================================
   Main Content
   ======================================== */
.app-main {
  flex: 1;
  background-color: var(--bg-secondary);
  margin: 0 var(--spacing-lg) var(--spacing-lg);
  border-radius: var(--radius-xl);
  padding: var(--spacing-lg);
  box-shadow: var(--shadow-xl);
  max-width: 1200px;
  width: calc(100% - var(--spacing-2xl));
  align-self: center;
}

.step-content {
  min-height: 400px;
}

/* ========================================
   Footer
   ======================================== */
.app-footer {
  padding: var(--spacing-md);
  text-align: center;
  color: var(--color-light);
  font-size: 14px;
  font-family: var(--font-body);
  opacity: 0.9;
}

.app-footer p {
  margin: 0;
}

/* ========================================
   Responsive Design
   ======================================== */
@media (max-width: 768px) {
  .app-header {
    padding: var(--spacing-lg) var(--spacing-md);
  }

  .app-title {
    font-size: 24px;
  }

  .app-main {
    margin: 0 var(--spacing-md) var(--spacing-md);
    padding: var(--spacing-md);
    width: calc(100% - var(--spacing-lg));
  }
}

@media (max-width: 480px) {
  .app-title {
    font-size: 20px;
  }

  .app-main {
    border-radius: var(--radius-lg);
  }
}
</style>
