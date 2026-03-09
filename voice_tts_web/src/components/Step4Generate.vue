<template>
  <div class="step-container">
    <h3 class="step-title">生成语音</h3>

    <div class="summary">
      <p><strong>输入信息摘要：</strong></p>
      <p>✓ 参考音频：已上传</p>
      <p>✓ 参考音频文本：{{ promptTextPreview }}</p>
      <p>✓ 要合成的文本：{{ synthesisTextPreview }}</p>
    </div>

    <el-button
      type="primary"
      size="large"
      :loading="isGenerating"
      :disabled="isGenerating"
      @click="handleGenerate"
      class="generate-button"
    >
      {{ isGenerating ? '生成中...' : '生成语音' }}
    </el-button>

    <el-progress
      v-if="isGenerating"
      :percentage="progress"
      :stroke-width="20"
      :show-text="true"
      class="progress-bar"
    />

    <div v-if="generatedAudio || error" class="output-section">
      <h4>输出结果</h4>

      <div v-if="error" class="error-message">
        {{ error }}
      </div>

      <div v-if="generatedAudio" class="audio-result">
        <audio :src="generatedAudio" controls />
        <el-button
          type="success"
          @click="downloadAudio"
          style="margin-top: 12px"
        >
          下载音频
        </el-button>
      </div>
    </div>

    <div class="nav-buttons">
      <el-button size="large" @click="goPrev">上一步</el-button>
      <el-button size="large" @click="goRestart">重新开始</el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { ttsApi } from '../api/tts'
import type { AudioFile } from '../types'

interface Props {
  promptText: string
  synthesisText: string
  referenceAudio: AudioFile | null
}

interface Emits {
  (e: 'prev'): void
  (e: 'restart'): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const isGenerating = ref(false)
const progress = ref(0)
const generatedAudio = ref<string | null>(null)
const error = ref<string | null>(null)

const promptTextPreview = computed(() => {
  if (props.promptText.length <= 50) return props.promptText
  return props.promptText.slice(0, 50) + '...'
})

const synthesisTextPreview = computed(() => {
  if (props.synthesisText.length <= 100) return props.synthesisText
  return props.synthesisText.slice(0, 100) + '...'
})

async function handleGenerate() {
  if (!props.referenceAudio) {
    ElMessage.error('缺少参考音频')
    return
  }

  isGenerating.value = true
  progress.value = 0
  error.value = null
  generatedAudio.value = null

  const progressInterval = setInterval(() => {
    if (progress.value < 90) {
      progress.value += 5
    }
  }, 500)

  try {
    const audioChunks: string[] = []

    await ttsApi.generateVoiceStream(
      props.synthesisText,
      props.promptText,
      props.referenceAudio.file,
      (chunk) => {
        if (chunk.type === 'chunk' && chunk.data) {
          audioChunks.push(chunk.data)
          progress.value = Math.min(progress.value + 2, 95)
        } else if (chunk.type === 'final' && chunk.data) {
          progress.value = 100
          generatedAudio.value = `data:audio/wav;base64,${chunk.data}`
          ElMessage.success('语音生成成功！')
        }
      }
    )

  } catch (err: any) {
    error.value = err.message || '生成失败，请重试'
    ElMessage.error(error.value)
  } finally {
    clearInterval(progressInterval)
    isGenerating.value = false
  }
}

function downloadAudio() {
  if (!generatedAudio.value) return

  const link = document.createElement('a')
  link.href = generatedAudio.value
  link.download = `generated_audio_${Date.now()}.wav`
  link.click()
}

function goPrev() {
  emit('prev')
}

function goRestart() {
  emit('restart')
}
</script>

<style scoped>
/* ========================================
   Step Container - Anthropic Brand Styling
   ======================================== */

.step-container {
  max-width: 800px;
  margin: 0 auto;
  padding: var(--spacing-lg);
}

.step-title {
  font-family: var(--font-heading);
  font-size: 24px;
  font-weight: 600;
  margin-bottom: var(--spacing-lg);
  text-align: center;
  color: var(--color-dark);
  letter-spacing: -0.01em;
}

/* ========================================
   Summary Box
   ======================================== */

.summary {
  padding: var(--spacing-md);
  background-color: var(--bg-tertiary);
  border-radius: var(--radius-md);
  margin-bottom: var(--spacing-lg);
  border-left: 3px solid var(--color-accent-blue);
}

.summary p {
  font-family: var(--font-body);
  margin: 4px 0;
  color: var(--text-primary);
}

.summary strong {
  font-family: var(--font-heading);
  color: var(--color-accent-blue);
}

/* ========================================
   Generate Button
   ======================================== */

.generate-button {
  width: 100%;
  height: 56px;
  font-family: var(--font-heading);
  font-size: 18px;
  font-weight: 600;
  margin-bottom: var(--spacing-lg);
  border-radius: var(--radius-lg);
  letter-spacing: -0.01em;
}

/* ========================================
   Progress Bar
   ======================================== */

.progress-bar {
  margin-bottom: var(--spacing-lg);
}

/* ========================================
   Output Section
   ======================================== */

.output-section {
  padding: var(--spacing-lg);
  background-color: var(--bg-tertiary);
  border-radius: var(--radius-md);
  margin-bottom: var(--spacing-lg);
  border-left: 3px solid var(--color-accent-orange);
}

.output-section h4 {
  margin: 0 0 var(--spacing-md) 0;
  font-family: var(--font-heading);
  font-size: 18px;
  font-weight: 600;
  color: var(--color-dark);
}

/* ========================================
   Error Message
   ======================================== */

.error-message {
  padding: var(--spacing-md);
  background-color: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: var(--radius-sm);
  color: var(--color-danger);
  font-family: var(--font-body);
}

/* ========================================
   Audio Result
   ======================================== */

.audio-result {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.audio-result audio {
  width: 100%;
  max-width: 500px;
  border-radius: var(--radius-sm);
}

/* ========================================
   Navigation Buttons
   ======================================== */

.nav-buttons {
  display: flex;
  justify-content: center;
  gap: var(--spacing-md);
}

/* ========================================
   Element Plus Overrides
   ======================================== */

/* Progress bar */
:deep(.el-progress-bar__inner) {
  background: linear-gradient(90deg, var(--color-accent-orange), var(--color-accent-blue));
}

:deep(.el-progress__text) {
  font-family: var(--font-heading);
  font-weight: 600;
}

/* Button */
:deep(.el-button--success) {
  font-family: var(--font-heading);
  font-weight: 500;
}
</style>
